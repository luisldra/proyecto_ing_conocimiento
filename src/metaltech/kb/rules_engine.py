"""Motor de reglas: síntomas -> reglas -> modos de falla, con factores de certeza MYCIN.

Flujo (D-034, D-043):
  1. **Fusificación simple**: cada variable medida se convierte en síntomas con los umbrales de
     ``configs/assets.yaml``. Cada síntoma tiene un grado en [0, 1]; por defecto es nítido
     (1 si cruza el umbral, 0 si no). ``margen_suave`` > 0 agrega una rampa lineal bajo el
     umbral, para evitar saltos bruscos.
  2. **Encadenamiento hacia adelante**: una regla se dispara si todas sus premisas tienen grado
     > 0. FC de la premisa = mínimo de los grados; FC de la conclusión = ``fc`` * FC premisa.
  3. **Combinación MYCIN** de las conclusiones que apuntan al mismo modo de falla.
  4. **Traza**: cada regla disparada guarda sus premisas con el valor real y el umbral.

Uso rápido::

    from metaltech.kb.rules_engine import MotorReglas
    d = MotorReglas().diagnosticar("bomba_centrifuga", {"npsh_margen_ratio": 1.2, ...},
                                   texto_tecnico="la bomba está golpeando")
    print(d.a_texto())
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

from metaltech.kb.base import BaseConocimiento, cargar_base
from metaltech.kb.lexicon import Coincidencia, Lexico

FACTOR_TENDENCIA = 0.25  # D-004: cambio >= 25 % del límite de alerta respecto a la línea base


# ---------------------------------------------------------------------------------------
# Factores de certeza (MYCIN)
# ---------------------------------------------------------------------------------------
def combinar_fc(a: float, b: float) -> float:
    """Combina dos FC en [-1, 1] sobre la misma hipótesis (Shortliffe y Buchanan, 1975)."""
    if a >= 0 and b >= 0:
        return a + b * (1 - a)
    if a <= 0 and b <= 0:
        return a + b * (1 + a)
    divisor = 1 - min(abs(a), abs(b))
    return (a + b) / divisor if divisor else 0.0  # +1 y -1: contradicción total, sin conclusión


def combinar_fcs(valores: Iterable[float]) -> float:
    """Combinación incremental de varios FC (conmutativa y asociativa)."""
    total = 0.0
    for v in valores:
        total = combinar_fc(total, v)
    return total


# ---------------------------------------------------------------------------------------
# Estructuras de salida
# ---------------------------------------------------------------------------------------
@dataclass
class SintomaActivo:
    """Un síntoma evaluado (activo si ``grado`` > 0)."""

    id: str
    tipo: str  # medido | percibido
    grado: float
    variable: str | None = None
    valor: float | None = None  # valor evaluado (para "tendencia", el cambio vs. línea base)
    umbral: float | None = None
    operador: str | None = None  # >=, <=, rango
    descripcion: str = ""


@dataclass
class Premisa:
    """Premisa de una regla disparada, con el valor real que la sustenta."""

    sintoma: str
    grado: float
    tipo: str
    variable: str | None
    valor: float | None
    umbral: float | None
    operador: str | None
    descripcion: str


@dataclass
class ReglaDisparada:
    id: str
    modo: str
    fc_regla: float
    fc_premisa: float
    fc_conclusion: float
    premisas: list[Premisa]
    accion: str
    fuentes: list[str]


@dataclass
class ReglaParcial:
    """Regla con algunas premisas activas pero no todas (útil para explicar por qué no)."""

    id: str
    modo: str
    cumplidas: list[str]
    faltantes: list[str]


@dataclass
class Conclusion:
    """Modo de falla con el FC combinado de todas las reglas que lo apoyan."""

    modo: str
    nombre: str
    componente: str
    fc: float
    reglas: list[str]
    acciones: list[str]


@dataclass
class Diagnostico:
    activo: str
    sintomas: dict[str, SintomaActivo] = field(default_factory=dict)
    reglas_disparadas: list[ReglaDisparada] = field(default_factory=list)
    reglas_parciales: list[ReglaParcial] = field(default_factory=list)
    conclusiones: list[Conclusion] = field(default_factory=list)
    expresiones: list[Coincidencia] = field(default_factory=list)
    candidatos_lexico: dict[str, float] = field(default_factory=dict)
    datos_faltantes: list[str] = field(default_factory=list)
    variables_desconocidas: list[str] = field(default_factory=list)

    @property
    def principal(self) -> Conclusion | None:
        """Conclusión de mayor FC (None si ninguna regla se disparó)."""
        return self.conclusiones[0] if self.conclusiones else None

    def fc_de(self, modo: str) -> float:
        """FC combinado de un modo (0.0 si no se concluyó)."""
        return next((c.fc for c in self.conclusiones if c.modo == modo), 0.0)

    def a_dict(self) -> dict[str, Any]:
        """Versión serializable (para la API y la web)."""
        return asdict(self)

    def a_texto(self) -> str:
        """Explicación en español: conclusión, reglas disparadas y valores reales."""
        if not self.conclusiones:
            partes = [f"Sin diagnóstico para {self.activo}: ninguna regla se disparó."]
            if self.datos_faltantes:
                partes.append("Variables sin dato: " + ", ".join(self.datos_faltantes) + ".")
            return " ".join(partes)
        por_id = {r.id: r for r in self.reglas_disparadas}
        lineas = [f"Diagnóstico para {self.activo}:"]
        for i, c in enumerate(self.conclusiones, 1):
            lineas.append(f"{i}. {c.nombre} [{c.modo}] – FC {c.fc:.2f} (componente: {c.componente})")
            for rid in c.reglas:
                r = por_id[rid]
                lineas.append(
                    f"   {r.id} (FC regla {r.fc_regla:.2f} × premisas {r.fc_premisa:.2f} "
                    f"= {r.fc_conclusion:.2f}):"
                )
                for p in r.premisas:
                    lineas.append(f"     - {p.sintoma}: {_describir_premisa(p)}")
            if c.acciones:
                lineas.append(f"   Acción: {c.acciones[0]}")
        return "\n".join(lineas)


def _describir_premisa(p: Premisa) -> str:
    if p.tipo == "percibido":
        return "observación del técnico"
    if p.valor is None or p.umbral is None:
        return p.descripcion
    if p.operador == "rango":
        return f"{p.variable} = {p.valor:g} (dentro del rango normal, < {p.umbral:g})"
    return f"{p.variable} = {p.valor:g} ({p.operador} {p.umbral:g})"


# ---------------------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------------------
def _grado_rampa(valor: float, umbral: float, ancho: float, alta: bool) -> float:
    """1 si ``valor`` cruza ``umbral``; rampa lineal en los ``ancho`` previos; 0 si no."""
    if alta:
        if valor >= umbral:
            return 1.0
        return (valor - (umbral - ancho)) / ancho if ancho > 0 and valor > umbral - ancho else 0.0
    if valor <= umbral:
        return 1.0
    return ((umbral + ancho) - valor) / ancho if ancho > 0 and valor < umbral + ancho else 0.0


def _es_dato(x: Any) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))


class MotorReglas:
    """Evalúa síntomas y reglas de un tipo de activo.

    ``margen_suave``: fracción (0–1) de la distancia entre el borde del rango nominal y el
    umbral que se usa como rampa. 0 = nítido (comportamiento por defecto, D-034).
    """

    def __init__(
        self,
        base: BaseConocimiento | None = None,
        margen_suave: float = 0.0,
        lexico: Lexico | None = None,
    ) -> None:
        if not 0.0 <= margen_suave <= 1.0:
            raise ValueError("margen_suave debe estar entre 0 y 1")
        self.base = base or cargar_base()
        self.margen_suave = margen_suave
        self.lexico = lexico or Lexico(self.base)

    # -------------------------------------------------------------------------------
    def evaluar_sintomas(
        self,
        activo: str,
        variables: Mapping[str, float | None],
        linea_base: Mapping[str, float | None] | None = None,
        percibidos: Iterable[str] | Mapping[str, float] = (),
    ) -> dict[str, SintomaActivo]:
        """Síntomas activos (grado > 0) para un tipo de activo."""
        cfg = self._activo(activo)["variables"]
        linea_base = linea_base or {}
        pesos = dict(percibidos) if isinstance(percibidos, Mapping) else dict.fromkeys(percibidos, 1.0)
        activos: dict[str, SintomaActivo] = {}
        for sid, sd in self.base.sintomas.items():
            if sd["tipo"] == "percibido":
                grado = float(pesos.get(sid, 0.0))
                if grado > 0:
                    activos[sid] = SintomaActivo(sid, "percibido", min(grado, 1.0),
                                                 descripcion=sd["descripcion"])
                continue
            variable = sd["variable"]
            if variable not in cfg or not _es_dato(variables.get(variable)):
                continue
            sa = self._evaluar_medido(sid, sd, cfg[variable], float(variables[variable]),
                                      linea_base.get(variable))
            if sa is not None and sa.grado > 0:
                activos[sid] = sa
        return activos

    def inferir(self, activo: str, sintomas: Mapping[str, SintomaActivo]) -> Diagnostico:
        """Encadenamiento hacia adelante sobre síntomas ya evaluados."""
        self._activo(activo)
        diag = Diagnostico(activo=activo, sintomas=dict(sintomas))
        por_modo: dict[str, list[ReglaDisparada]] = {}
        for regla in self.base.reglas_de(activo):
            premisas = regla["si"]
            cumplidas = [s for s in premisas if s in sintomas]
            if len(cumplidas) == len(premisas):
                grados = [sintomas[s].grado for s in premisas]
                fc_premisa = min(grados)
                disparada = ReglaDisparada(
                    id=regla["id"], modo=regla["entonces"], fc_regla=regla["fc"],
                    fc_premisa=fc_premisa, fc_conclusion=regla["fc"] * fc_premisa,
                    premisas=[self._premisa(sintomas[s]) for s in premisas],
                    accion=regla["accion"], fuentes=list(regla["fuentes"]),
                )
                diag.reglas_disparadas.append(disparada)
                por_modo.setdefault(disparada.modo, []).append(disparada)
            elif cumplidas:
                diag.reglas_parciales.append(ReglaParcial(
                    regla["id"], regla["entonces"], cumplidas,
                    [s for s in premisas if s not in sintomas]))
        for modo, reglas in por_modo.items():
            reglas.sort(key=lambda r: (-r.fc_conclusion, r.id))
            diag.conclusiones.append(Conclusion(
                modo=modo, nombre=self.base.modos[modo]["nombre"],
                componente=self.base.componente_de_modo(modo, activo),
                fc=combinar_fcs(r.fc_conclusion for r in reglas),
                reglas=[r.id for r in reglas],
                acciones=list(dict.fromkeys(r.accion for r in reglas)),
            ))
        diag.conclusiones.sort(key=lambda c: (-c.fc, c.modo))
        diag.reglas_disparadas.sort(key=lambda r: (-r.fc_conclusion, r.id))
        return diag

    def diagnosticar(
        self,
        activo: str,
        variables: Mapping[str, float | None],
        linea_base: Mapping[str, float | None] | None = None,
        percibidos: Iterable[str] | Mapping[str, float] = (),
        texto_tecnico: str | None = None,
    ) -> Diagnostico:
        """Pipeline completo: observación del técnico + sensores -> diagnóstico con traza."""
        cfg = self._activo(activo)["variables"]
        coincidencias: list[Coincidencia] = []
        if isinstance(percibidos, Mapping):
            percibidos = dict(percibidos)
        else:
            percibidos = dict.fromkeys(percibidos, 1.0)
        if texto_tecnico:
            coincidencias = self.lexico.identificar(texto_tecnico, activo)
            for c in coincidencias:
                percibidos.setdefault(c.sintoma_percibido, 1.0)
        sintomas = self.evaluar_sintomas(activo, variables, linea_base, percibidos)
        diag = self.inferir(activo, sintomas)
        diag.expresiones = coincidencias
        for c in coincidencias:
            for modo, fc in c.candidatos.items():
                diag.candidatos_lexico[modo] = max(diag.candidatos_lexico.get(modo, 0.0), fc)
        diag.candidatos_lexico = dict(sorted(diag.candidatos_lexico.items(), key=lambda kv: -kv[1]))
        diag.datos_faltantes = [v for v in cfg if not _es_dato(variables.get(v))]
        diag.variables_desconocidas = [v for v in variables if v not in cfg]
        return diag

    # -------------------------------------------------------------------------------
    def _activo(self, activo: str) -> dict[str, Any]:
        try:
            return self.base.activos[activo]
        except KeyError:
            raise KeyError(
                f"activo desconocido: {activo!r}. Opciones: {sorted(self.base.activos)}"
            ) from None

    @staticmethod
    def _premisa(s: SintomaActivo) -> Premisa:
        return Premisa(s.id, s.grado, s.tipo, s.variable, s.valor, s.umbral, s.operador,
                       s.descripcion)

    def _ancho(self, umbral: float, borde: float) -> float:
        return self.margen_suave * abs(umbral - borde)

    def _evaluar_medido(
        self, sid: str, sd: dict[str, Any], var: dict[str, Any], valor: float, base: float | None
    ) -> SintomaActivo | None:
        nivel, variable = sd["nivel"], sd["variable"]
        alta = var["direccion"] == "alta"
        nom_lo, nom_hi = var["nominal"]
        s = SintomaActivo(sid, "medido", 0.0, variable, valor, descripcion=sd["descripcion"])

        if nivel in ("alerta", "critico"):
            umbral = var[nivel]
            borde = nom_hi if alta else nom_lo
            ancho = self._ancho(umbral, borde)
            if nivel == "critico" and "alerta" in var:
                ancho = min(ancho, abs(var["critico"] - var["alerta"]))
            s.umbral, s.operador = umbral, ">=" if alta else "<="
            s.grado = _grado_rampa(valor, umbral, ancho, alta)
        elif nivel == "alerta_baja":
            umbral = var["alerta_baja"]
            s.umbral, s.operador = umbral, "<="
            s.grado = _grado_rampa(valor, umbral, self._ancho(umbral, nom_lo), alta=False)
        elif nivel == "en_rango":
            # entre alerta_baja y alerta (variables de dos colas, p. ej. corriente)
            tope = var["alerta"]
            g_alta = _grado_rampa(valor, tope, self._ancho(tope, nom_hi), alta=True)
            g_baja = 0.0
            if "alerta_baja" in var:
                bajo = var["alerta_baja"]
                g_baja = _grado_rampa(valor, bajo, self._ancho(bajo, nom_lo), alta=False)
            s.umbral, s.operador = tope, "rango"
            s.grado = min(1.0 - g_alta, 1.0 - g_baja)
        elif nivel == "tendencia":
            if not _es_dato(base):
                return None  # sin línea base no hay tendencia (D-040)
            umbral = FACTOR_TENDENCIA * var["alerta"]
            s.valor, s.umbral, s.operador = valor - float(base), umbral, ">="
            s.grado = _grado_rampa(s.valor, umbral, self.margen_suave * umbral, alta=True)
        else:
            raise ValueError(f"nivel desconocido en el síntoma {sid}: {nivel}")
        s.grado = round(max(0.0, min(1.0, s.grado)), 6)
        return s


# ---------------------------------------------------------------------------------------
# Línea de comandos:  python -m metaltech.kb.rules_engine --activo ... --valores '{...}'
# ---------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Diagnóstico por reglas con factores de certeza.")
    ap.add_argument("--activo", required=True, help="tipo de activo, p. ej. bomba_centrifuga")
    ap.add_argument("--valores", default="{}", help="JSON con variable -> valor")
    ap.add_argument("--linea-base", default="{}", help="JSON con la línea base de las variables")
    ap.add_argument("--texto", default=None, help="observación del técnico en lenguaje natural")
    ap.add_argument("--json", action="store_true", help="imprime el diagnóstico como JSON")
    args = ap.parse_args(argv)
    diag = MotorReglas().diagnosticar(
        args.activo, json.loads(args.valores), json.loads(args.linea_base),
        texto_tecnico=args.texto)
    if args.json:
        print(json.dumps(diag.a_dict(), ensure_ascii=False, indent=2))
    else:
        print(diag.a_texto())
        if diag.expresiones:
            print("Expresiones reconocidas: " + ", ".join(c.expresion for c in diag.expresiones))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
