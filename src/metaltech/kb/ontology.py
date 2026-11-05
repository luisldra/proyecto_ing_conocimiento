"""Ontología OWL de Metal Tech: generación desde los YAML, consultas y validación.

La ontología **no se edita a mano**: ``construir()`` la genera desde ``configs/`` y
``knowledge/`` (fuente única de verdad, AGENTS.md §7) y ``guardar()`` escribe
``knowledge/ontology/metaltech.owl``, que se puede abrir en Protégé.

Esquema (docs/PLAN.md, Fase 2):

* Clases: ``Activo`` (subclases por tipo), ``Componente``, ``Sensor``, ``Variable``,
  ``Sintoma`` (``SintomaMedido`` / ``SintomaPercibido``), ``ModoFalla``, ``Causa``, ``Accion``,
  ``Regla``, ``ExpresionColoquial``, ``Tecnico``, ``Turno``, ``Alerta`` y ``FilaFMEA``
  (agregada para conservar las relaciones de la FMEA por tipo de activo).
* Propiedades de objeto: ``tieneComponente``, ``monitoreadoPor``, ``mide``, ``manifiesta``,
  ``causadoPor``, ``mitigadoPor``, ``refiereA``, ``sustentadaPor`` y auxiliares.
* Propiedades de datos: ``severidad``, ``umbral`` (con ``umbralAlerta``, ``umbralCritico`` y
  ``umbralAlertaBaja``), ``fcRegla`` y otras.
* Las clases de nivel superior son disjuntas, de modo que un razonador detecta individuos
  mal clasificados.

Uso::

    python -m metaltech.kb.ontology                 # genera el .owl y valida su estructura
    python -m metaltech.kb.ontology --hermit        # además valida con HermiT (requiere Java)
    python -m metaltech.kb.ontology --modo cavitacion --activo bomba_centrifuga
"""

from __future__ import annotations

import argparse
import re
import shutil
import types
from pathlib import Path
from typing import Any

import owlready2
from owlready2 import (
    AllDisjoint,
    DataProperty,
    FunctionalProperty,
    ObjectProperty,
    Thing,
    World,
    sync_reasoner_hermit,
)

from metaltech.kb.base import RAIZ, BaseConocimiento, cargar_base

IRI = "http://metaltech.example.org/ontologia/metaltech.owl"
RUTA_OWL = RAIZ / "knowledge" / "ontology" / "metaltech.owl"
CLASES_SUPERIORES = [
    "Activo", "Componente", "Sensor", "Variable", "Sintoma", "ModoFalla", "Causa", "Accion",
    "Regla", "ExpresionColoquial", "Tecnico", "Turno", "Alerta", "FilaFMEA",
]


def buscar_java() -> str | None:
    """Ruta del ejecutable de Java: el del PATH o el JDK local de ``.tools/jdk17``."""
    local = RAIZ / ".tools" / "jdk17" / "bin" / ("java.exe" if shutil.which("cmd") else "java")
    return shutil.which("java") or (str(local) if local.exists() else None)


def _nombre(prefijo: str, ident: str) -> str:
    return f"{prefijo}_{re.sub(r'[^A-Za-z0-9_]', '_', ident)}"


def _legible(slug: str) -> str:
    return slug.replace("_", " ")


def _camel(slug: str) -> str:
    return "".join(p.capitalize() for p in slug.split("_"))


# ---------------------------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------------------------
def _definir_esquema(onto: Any, tipos: list[str]) -> dict[str, Any]:
    """Crea clases y propiedades en ``onto`` y devuelve ``{nombre: clase_o_propiedad}``."""
    e: dict[str, Any] = {}
    with onto:
        for nombre in CLASES_SUPERIORES:
            e[nombre] = types.new_class(nombre, (Thing,))
        e["SintomaMedido"] = types.new_class("SintomaMedido", (e["Sintoma"],))
        e["SintomaPercibido"] = types.new_class("SintomaPercibido", (e["Sintoma"],))
        for tipo in tipos:
            e[f"tipo:{tipo}"] = types.new_class(_camel(tipo), (e["Activo"],))

        AllDisjoint([e[n] for n in CLASES_SUPERIORES])
        AllDisjoint([e["SintomaMedido"], e["SintomaPercibido"]])
        AllDisjoint([e[f"tipo:{t}"] for t in tipos])

        def obj(nombre: str, dominio: Any, rango: Any, funcional: bool = False) -> Any:
            bases = (ObjectProperty, FunctionalProperty) if funcional else (ObjectProperty,)
            p = types.new_class(nombre, bases)
            p.domain, p.range = dominio, rango
            e[nombre] = p
            return p

        obj("tieneComponente", [e["Activo"]], [e["Componente"]])
        obj("monitoreadoPor", [e["Activo"]], [e["Sensor"]])
        obj("mide", [e["Sensor"]], [e["Variable"]], funcional=True)
        obj("manifiesta", [e["ModoFalla"]], [e["Sintoma"]])
        obj("causadoPor", [e["ModoFalla"]], [e["Causa"]])
        obj("mitigadoPor", [e["ModoFalla"]], [e["Accion"]])
        obj("afectaComponente", [e["ModoFalla"]], [e["Componente"]])
        obj("refiereA", [e["ExpresionColoquial"]], [e["Sintoma"]])
        obj("sugiereModo", [e["ExpresionColoquial"]], [e["ModoFalla"]])
        obj("concluye", [e["Regla"]], [e["ModoFalla"]], funcional=True)
        obj("tienePremisa", [e["Regla"]], [e["Sintoma"]])
        obj("sobreVariable", [e["SintomaMedido"]], [e["Variable"]])
        obj("sustentadaPor", [e["Alerta"]], [e["Regla"] | e["Variable"]])
        obj("modoDeFila", [e["FilaFMEA"]], [e["ModoFalla"]], funcional=True)
        obj("componenteDeFila", [e["FilaFMEA"]], [e["Componente"]], funcional=True)
        obj("sintomaDeFila", [e["FilaFMEA"]], [e["Sintoma"]])
        obj("causaDeFila", [e["FilaFMEA"]], [e["Causa"]])
        obj("accionDeFila", [e["FilaFMEA"]], [e["Accion"]])

        def dato(nombre: str, tipo: type, dominio: Any = None, funcional: bool = True,
                 padre: Any = None) -> Any:
            bases = (padre or DataProperty,) + ((FunctionalProperty,) if funcional else ())
            p = types.new_class(nombre, bases)
            p.domain = [dominio or Thing]
            p.range = [tipo]
            e[nombre] = p
            return p

        dato("identificador", str)
        dato("nombre", str)
        dato("descripcion", str)
        dato("tipoActivo", str, funcional=False)
        dato("severidad", int)
        dato("ocurrencia", int, e["FilaFMEA"])
        dato("deteccion", int, e["FilaFMEA"])
        dato("npr", int, e["FilaFMEA"])
        # `umbral` agrupa los tres niveles; NO puede ser funcional: una variable tiene varios
        # umbrales (alerta, crítico...) y HermiT los vería como valores en conflicto (ERR-011).
        base_umbral = dato("umbral", float, e["Variable"], funcional=False)
        dato("umbralAlerta", float, e["Variable"], padre=base_umbral)
        dato("umbralCritico", float, e["Variable"], padre=base_umbral)
        dato("umbralAlertaBaja", float, e["Variable"], padre=base_umbral)
        dato("nominalMin", float, e["Variable"])
        dato("nominalMax", float, e["Variable"])
        dato("unidadMedida", str, e["Variable"])
        dato("direccion", str, e["Variable"])
        dato("variableId", str, e["Sintoma"])
        dato("nivel", str, e["Sintoma"])
        dato("fcRegla", float, e["Regla"])
        dato("accionRecomendada", str, e["Regla"])
        dato("fuente", str, funcional=False)
        dato("formaDegradacion", str, e["ModoFalla"])
        dato("expresionTexto", str, e["ExpresionColoquial"])
        dato("rol", str, e["Tecnico"])
    return e


# ---------------------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------------------
def construir(base: BaseConocimiento | None = None) -> Ontologia:
    """Genera la ontología en un ``World`` propio (no toca el estado global de owlready2)."""
    base = base or cargar_base()
    world = World()
    onto = world.get_ontology(IRI)
    tipos = list(base.activos)
    e = _definir_esquema(onto, tipos)
    ind: dict[str, dict[str, Any]] = {n: {} for n in CLASES_SUPERIORES}

    def crear(clase: Any, tope: str, prefijo: str, ident: str, nombre: str | None = None) -> Any:
        i = clase(_nombre(prefijo, ident))
        i.identificador = ident
        if nombre:
            i.nombre = nombre
        ind[tope][ident] = i
        return i

    with onto:
        # --- personal y turnos (ficticios, anonimizados) ---
        for turno in base.planta.get("turnos", []):
            crear(e["Turno"], "Turno", "turno", turno, turno)
        for rol, cantidad in base.planta.get("tecnicos", {}).items():
            letra = "T" if rol == "electromecanico" else "I"
            for k in range(1, cantidad + 1):
                t = crear(e["Tecnico"], "Tecnico", "tecnico", f"{letra}{k:02d}", f"{letra}{k:02d}")
                t.rol = rol

        # --- activos: componentes, variables, unidades y sensores ---
        for tipo, cfg in base.activos.items():
            comps = []
            for comp in cfg["componentes"]:
                c = crear(e["Componente"], "Componente", "comp", f"{tipo}__{comp}", _legible(comp))
                c.tipoActivo = [tipo]
                comps.append(c)
            variables = {}
            for var, v in cfg["variables"].items():
                x = crear(e["Variable"], "Variable", "var", f"{tipo}__{var}", var)
                x.tipoActivo = [tipo]
                x.unidadMedida, x.direccion = str(v["unidad"]), v["direccion"]
                x.nominalMin, x.nominalMax = float(v["nominal"][0]), float(v["nominal"][1])
                x.umbralAlerta, x.umbralCritico = float(v["alerta"]), float(v["critico"])
                if "alerta_baja" in v:
                    x.umbralAlertaBaja = float(v["alerta_baja"])
                x.fuente = list(v.get("fuentes", []))
                variables[var] = x
            for k in range(1, int(cfg.get("unidades", 1)) + 1):
                u = crear(e[f"tipo:{tipo}"], "Activo", "unidad", f"{tipo}_{k}", f"{_legible(tipo)} {k}")
                u.tipoActivo = [tipo]
                u.tieneComponente = list(comps)
                sensores = []
                for var, x in variables.items():
                    s = crear(e["Sensor"], "Sensor", "sensor", f"{tipo}_{k}__{var}", var)
                    s.mide = x
                    sensores.append(s)
                u.monitoreadoPor = sensores

        # --- síntomas ---
        for sid, sd in base.sintomas.items():
            clase = e["SintomaMedido"] if sd["tipo"] == "medido" else e["SintomaPercibido"]
            s = crear(clase, "Sintoma", "sintoma", sid, sid)
            s.descripcion = sd["descripcion"]
            s.variableId = sd["variable"]
            if sd["tipo"] == "medido":
                s.nivel = sd["nivel"]
                s.sobreVariable = [
                    v for k, v in ind["Variable"].items() if k.endswith(f"__{sd['variable']}")
                ]

        # --- modos, causas, acciones y filas de la FMEA ---
        for mid, m in base.modos.items():
            x = crear(e["ModoFalla"], "ModoFalla", "modo", mid, m["nombre"])
            x.tipoActivo = list(m["activos"])
            x.formaDegradacion = m["degradacion"]["forma"]
            x.fuente = list(m.get("fuentes", []))
        causas_de: dict[str, list[Any]] = {m: [] for m in base.modos}
        acciones_de: dict[str, list[Any]] = {m: [] for m in base.modos}
        sintomas_de: dict[str, list[Any]] = {
            m: [ind["Sintoma"][s] for s in d["sintomas"]] for m, d in base.modos.items()
        }
        comps_de: dict[str, list[Any]] = {m: [] for m in base.modos}
        severidad: dict[str, int] = {}

        def unico(lista: list[Any], item: Any) -> None:
            if item not in lista:
                lista.append(item)

        for tipo, filas in base.fmea.items():
            for fila in filas:
                mid = fila["modo_falla"]
                f = crear(e["FilaFMEA"], "FilaFMEA", "fmea", f"{tipo}__{mid}",
                          f"{_legible(mid)} en {_legible(tipo)}")
                f.tipoActivo = [tipo]
                f.severidad, f.ocurrencia = fila["severidad"], fila["ocurrencia"]
                f.deteccion, f.npr = fila["deteccion"], fila["npr"]
                f.fuente = list(fila["fuentes"])
                f.modoDeFila = ind["ModoFalla"][mid]
                comp = ind["Componente"][f"{tipo}__{fila['componente']}"]
                f.componenteDeFila = comp
                unico(comps_de[mid], comp)
                f.sintomaDeFila = [ind["Sintoma"][s] for s in fila["sintomas"]]
                for s in f.sintomaDeFila:
                    unico(sintomas_de[mid], s)
                f.causaDeFila, f.accionDeFila = [], []
                for slug in fila["causas"]:
                    c = ind["Causa"].get(slug) or crear(e["Causa"], "Causa", "causa", slug,
                                                         _legible(slug))
                    f.causaDeFila.append(c)
                    unico(causas_de[mid], c)
                for slug in fila["acciones"]:
                    a = ind["Accion"].get(slug) or crear(e["Accion"], "Accion", "accion", slug,
                                                          _legible(slug))
                    f.accionDeFila.append(a)
                    unico(acciones_de[mid], a)
                severidad[mid] = max(severidad.get(mid, 0), fila["severidad"])
        for mid, x in ind["ModoFalla"].items():
            x.manifiesta = sintomas_de[mid]
            x.causadoPor = causas_de[mid]
            x.mitigadoPor = acciones_de[mid]
            x.afectaComponente = comps_de[mid]
            x.severidad = severidad[mid]

        # --- reglas ---
        for r in base.reglas:
            x = crear(e["Regla"], "Regla", "regla", r["id"], r["id"])
            x.concluye = ind["ModoFalla"][r["entonces"]]
            x.tienePremisa = [ind["Sintoma"][s] for s in r["si"]]
            x.fcRegla = float(r["fc"])
            x.accionRecomendada = r["accion"]
            x.tipoActivo = [r["activo"]]
            x.fuente = list(r["fuentes"])

        # --- léxico ---
        for exp in base.lexico:
            x = crear(e["ExpresionColoquial"], "ExpresionColoquial", "exp", exp["id"],
                      exp["expresion"])
            x.expresionTexto = exp["expresion"]
            x.tipoActivo = list(exp["activos"])
            x.refiereA = [ind["Sintoma"][exp["sintoma_percibido"]]] + [
                ind["Sintoma"][s] for s in exp["sintomas_formales"]
                if s != exp["sintoma_percibido"]
            ]
            x.sugiereModo = [ind["ModoFalla"][c["id"]] for c in exp["modos_falla_candidatos"]]
    return Ontologia(world, onto)


# ---------------------------------------------------------------------------------------
# Consultas y validación
# ---------------------------------------------------------------------------------------
class Ontologia:
    """Envoltura con las consultas de dominio sobre la ontología (en memoria o cargada)."""

    def __init__(self, world: World, onto: Any) -> None:
        self.world, self.onto = world, onto
        self._ix: dict[str, dict[str, Any]] = {n: {} for n in CLASES_SUPERIORES}
        for i in onto.individuals():
            ident = i.identificador
            for cls in type(i).mro():
                if cls.__name__ in self._ix:
                    self._ix[cls.__name__][ident] = i
                    break

    # --- E/S --------------------------------------------------------------------------
    def guardar(self, ruta: Path | str = RUTA_OWL) -> Path:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self.onto.save(file=str(ruta), format="rdfxml")
        return ruta

    @classmethod
    def cargar(cls, ruta: Path | str = RUTA_OWL) -> Ontologia:
        world = World()
        # fileobj evita los URI file:/// con espacios que owlready2 no resuelve en Windows
        with open(ruta, "rb") as f:
            onto = world.get_ontology(IRI).load(fileobj=f)
        return cls(world, onto)

    # --- conteos ------------------------------------------------------------------------
    def conteos(self) -> dict[str, int]:
        return {n: len(d) for n, d in self._ix.items()}

    # --- consultas ----------------------------------------------------------------------
    def _modo(self, modo: str) -> Any:
        try:
            return self._ix["ModoFalla"][modo]
        except KeyError:
            raise KeyError(f"modo de falla desconocido: {modo!r}") from None

    def _filas(self, modo: str, activo: str | None) -> list[Any]:
        m = self._modo(modo)
        filas = [f for f in self._ix["FilaFMEA"].values() if f.modoDeFila is m]
        return [f for f in filas if activo is None or activo in f.tipoActivo]

    @staticmethod
    def _ids(items: Any) -> list[str]:
        return sorted(i.identificador for i in items)

    def modos(self, activo: str | None = None) -> list[str]:
        """Modos de falla (opcionalmente solo los de un tipo de activo)."""
        return sorted(
            m for m, x in self._ix["ModoFalla"].items() if activo is None or activo in x.tipoActivo
        )

    def sintomas_de_modo(self, modo: str, activo: str | None = None) -> list[str]:
        """Síntomas que manifiesta un modo de falla."""
        if activo is None:
            return self._ids(self._modo(modo).manifiesta)
        return self._ids({s for f in self._filas(modo, activo) for s in f.sintomaDeFila})

    def causas_de_modo(self, modo: str, activo: str | None = None) -> list[str]:
        if activo is None:
            return self._ids(self._modo(modo).causadoPor)
        return self._ids({c for f in self._filas(modo, activo) for c in f.causaDeFila})

    def acciones_de_modo(self, modo: str, activo: str | None = None) -> list[str]:
        """Acciones recomendadas para una falla ("acciones para una falla")."""
        if activo is None:
            return self._ids(self._modo(modo).mitigadoPor)
        return self._ids({a for f in self._filas(modo, activo) for a in f.accionDeFila})

    def componentes_de_modo(self, modo: str, activo: str | None = None) -> list[str]:
        if activo is None:
            return self._ids(self._modo(modo).afectaComponente)
        return self._ids({f.componenteDeFila for f in self._filas(modo, activo)})

    def reglas_de_modo(self, modo: str, activo: str | None = None) -> list[str]:
        m = self._modo(modo)
        return sorted(
            r for r, x in self._ix["Regla"].items()
            if x.concluye is m and (activo is None or activo in x.tipoActivo)
        )

    def modos_de_sintoma(self, sintoma: str) -> list[str]:
        """Modos que manifiestan un síntoma (diagnóstico diferencial)."""
        s = self._ix["Sintoma"][sintoma]
        return sorted(m for m, x in self._ix["ModoFalla"].items() if s in x.manifiesta)

    def expresiones_de_sintoma(self, sintoma: str) -> list[str]:
        s = self._ix["Sintoma"][sintoma]
        return sorted(x.expresionTexto for x in self._ix["ExpresionColoquial"].values()
                      if s in x.refiereA)

    def expresiones_de_modo(self, modo: str) -> list[str]:
        m = self._modo(modo)
        return sorted(x.expresionTexto for x in self._ix["ExpresionColoquial"].values()
                      if m in x.sugiereModo)

    def componentes_de_activo(self, tipo: str) -> list[str]:
        unidad = next(u for u in self._ix["Activo"].values() if tipo in u.tipoActivo)
        return sorted(c.nombre for c in unidad.tieneComponente)

    def unidades(self, tipo: str | None = None) -> list[str]:
        return sorted(u for u, x in self._ix["Activo"].items() if tipo is None or tipo in x.tipoActivo)

    def sensores_de_unidad(self, unidad: str) -> dict[str, str]:
        """Variable medida por cada sensor de una unidad: ``{sensor: variable}``."""
        u = self._ix["Activo"][unidad]
        return {s.identificador: s.mide.nombre for s in u.monitoreadoPor}

    def detalle_modo(self, modo: str, activo: str | None = None) -> dict[str, Any]:
        """Ficha de un modo de falla (para ``GET /kb/failure/{id}``)."""
        m = self._modo(modo)
        filas = self._filas(modo, activo)
        return {
            "id": modo,
            "nombre": m.nombre,
            "activos": sorted(m.tipoActivo),
            "forma_degradacion": m.formaDegradacion,
            "severidad": m.severidad,
            "sintomas": self.sintomas_de_modo(modo, activo),
            "causas": self.causas_de_modo(modo, activo),
            "acciones": self.acciones_de_modo(modo, activo),
            "componentes": self.componentes_de_modo(modo, activo),
            "reglas": self.reglas_de_modo(modo, activo),
            "expresiones": self.expresiones_de_modo(modo),
            "fmea": [
                {"activo": f.tipoActivo[0], "severidad": f.severidad, "ocurrencia": f.ocurrencia,
                 "deteccion": f.deteccion, "npr": f.npr}
                for f in sorted(filas, key=lambda f: f.identificador)
            ],
        }

    def grafo(self, activo: str | None = None) -> dict[str, list[dict[str, str]]]:
        """Nodos y aristas para visualizar (``GET /kb/ontology/graph``, pyvis).

        Con ``activo`` se limita a los modos, reglas y síntomas de ese tipo de activo.
        """
        modos = self.modos(activo)
        nodos: dict[str, dict[str, str]] = {}
        aristas: list[dict[str, str]] = []

        def nodo(clase: str, ident: str, etiqueta: str | None = None) -> str:
            nid = f"{clase}:{ident}"
            nodos.setdefault(nid, {"id": nid, "tipo": clase, "etiqueta": etiqueta or ident})
            return nid

        def arista(a: str, rel: str, b: str) -> None:
            aristas.append({"origen": a, "relacion": rel, "destino": b})

        for modo in modos:
            m = nodo("ModoFalla", modo, self._modo(modo).nombre)
            for s in self.sintomas_de_modo(modo, activo):
                arista(m, "manifiesta", nodo("Sintoma", s))
            for c in self.causas_de_modo(modo, activo):
                arista(m, "causadoPor", nodo("Causa", c, _legible(c)))
            for a in self.acciones_de_modo(modo, activo):
                arista(m, "mitigadoPor", nodo("Accion", a, _legible(a)))
            for r in self.reglas_de_modo(modo, activo):
                rn = nodo("Regla", r)
                arista(rn, "concluye", m)
                for p in self._ix["Regla"][r].tienePremisa:
                    arista(rn, "tienePremisa", nodo("Sintoma", p.identificador))
            for ex in self._ix["ExpresionColoquial"].values():
                if self._modo(modo) in ex.sugiereModo and (activo is None or activo in ex.tipoActivo):
                    en = nodo("ExpresionColoquial", ex.identificador, ex.expresionTexto)
                    arista(en, "sugiereModo", m)
                    for s in ex.refiereA:
                        if f"Sintoma:{s.identificador}" in nodos:
                            arista(en, "refiereA", f"Sintoma:{s.identificador}")
        return {"nodos": list(nodos.values()), "aristas": aristas}

    # --- validación ---------------------------------------------------------------------
    def validar_estructura(self, base: BaseConocimiento | None = None) -> list[str]:
        """Comprobaciones propias (no requieren Java). Devuelve los problemas encontrados."""
        base = base or cargar_base()
        p: list[str] = []
        esperado = {
            "ModoFalla": len(base.modos), "Regla": len(base.reglas),
            "Sintoma": len(base.sintomas), "ExpresionColoquial": len(base.lexico),
            "FilaFMEA": sum(len(v) for v in base.fmea.values()),
            "Activo": sum(int(c.get("unidades", 1)) for c in base.activos.values()),
        }
        for clase, n in esperado.items():
            if len(self._ix[clase]) != n:
                p.append(f"{clase}: {len(self._ix[clase])} individuos, se esperaban {n}")
        for mid, m in self._ix["ModoFalla"].items():
            for rel in ("manifiesta", "causadoPor", "mitigadoPor", "afectaComponente"):
                if not getattr(m, rel):
                    p.append(f"modo {mid} sin {rel}")
            if not self.reglas_de_modo(mid):
                p.append(f"modo {mid} sin reglas")
        for rid, r in self._ix["Regla"].items():
            if r.concluye is None or not r.tienePremisa or not r.fuente:
                p.append(f"regla {rid} incompleta (conclusión, premisas o fuente)")
        for sid, s in self._ix["Sintoma"].items():
            if isinstance(s, self.onto["SintomaMedido"]) and not s.sobreVariable:
                p.append(f"síntoma medido {sid} sin variable")
        for uid, u in self._ix["Activo"].items():
            if not u.tieneComponente or not u.monitoreadoPor:
                p.append(f"unidad {uid} sin componentes o sin sensores")
        for fid, f in self._ix["FilaFMEA"].items():
            if f.severidad * f.ocurrencia * f.deteccion != f.npr:
                p.append(f"fila {fid}: NPR incoherente")
        return p

    def validar_con_hermit(self, java: str | None = None, debug: int = 0) -> None:
        """Valida la consistencia lógica con HermiT.

        Lanza ``OwlReadyInconsistentOntologyError`` si la ontología es inconsistente y
        ``RuntimeError`` si hay clases insatisfacibles o no se encuentra Java (ERR-008).
        """
        java = java or buscar_java()
        if not java:
            raise RuntimeError("Java no encontrado; ejecute scripts/instalar_jdk.py (ERR-008)")
        owlready2.JAVA_EXE = java
        with self.onto:
            sync_reasoner_hermit(self.world, debug=debug)
        malas = list(self.world.inconsistent_classes())
        if malas:
            raise RuntimeError(f"clases insatisfacibles: {malas}")


def generar(ruta: Path | str = RUTA_OWL) -> Ontologia:
    """Construye la ontología desde los YAML y la guarda en ``ruta``."""
    onto = construir()
    onto.guardar(ruta)
    return onto


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Genera, valida y consulta la ontología de Metal Tech.")
    ap.add_argument("--salida", default=str(RUTA_OWL), help="ruta del .owl a generar")
    ap.add_argument("--hermit", action="store_true", help="valida también con HermiT (Java)")
    ap.add_argument("--modo", help="muestra la ficha de un modo de falla")
    ap.add_argument("--activo", help="filtra la ficha por tipo de activo")
    args = ap.parse_args(argv)

    onto = generar(args.salida)
    print(f"Ontología escrita en {args.salida}")
    print("Individuos por clase:", onto.conteos())
    problemas = onto.validar_estructura()
    for pr in problemas:
        print(f"[FALLA] {pr}")
    print("Validación estructural:", "OK" if not problemas else f"{len(problemas)} problemas")
    if args.hermit:
        onto.validar_con_hermit(debug=0)
        print("HermiT: ontología consistente, sin clases insatisfacibles.")
    if args.modo:
        import json

        print(json.dumps(onto.detalle_modo(args.modo, args.activo), ensure_ascii=False, indent=2))
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
