"""Revisión de la web demostrativa con Playwright (Fase 8).

Levanta la API y la web en puertos propios, recorre cada página y sus opciones con un
navegador real, guarda capturas y un informe con excepciones, errores de consola y avisos.

Uso: ``python scripts/revisar_web.py --salida <carpeta>`` (requiere ``pip install playwright``
y ``python -m playwright install chromium``).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
PUERTO_API, PUERTO_WEB = 8765, 8599
ESPERA_MS = 120_000


# ---------------------------------------------------------------------------------------
# Servidores
# ---------------------------------------------------------------------------------------
def levantar(argumentos: list[str], url: str, entorno: dict[str, str], bitacora: Path) -> subprocess.Popen:
    proceso = subprocess.Popen([sys.executable, *argumentos], cwd=RAIZ, env=entorno,
                               stdout=bitacora.open("w"), stderr=subprocess.STDOUT)
    fin = time.time() + 180
    while time.time() < fin:
        try:
            with urllib.request.urlopen(url, timeout=3):
                return proceso
        except OSError:
            time.sleep(1)
    proceso.kill()
    raise RuntimeError(f"no respondió {url}; ver {bitacora}")


# ---------------------------------------------------------------------------------------
# Ayudas para Streamlit
# ---------------------------------------------------------------------------------------
class Revisor:
    def __init__(self, page: Page, salida: Path) -> None:
        self.page, self.salida = page, salida
        self.pasos: list[dict[str, Any]] = []
        self.consola: list[str] = []
        page.on("console", lambda m: self.consola.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: self.consola.append(f"pageerror: {e}"))

    def esperar(self) -> None:
        """Espera a que Streamlit termine de ejecutar: el indicador debe estar ausente varias veces seguidas."""
        indicador = self.page.locator('[data-testid="stStatusWidget"]')
        quietas, fin = 0, time.time() + ESPERA_MS / 1000
        while quietas < 4 and time.time() < fin:
            self.page.wait_for_timeout(250)
            quietas = quietas + 1 if not indicador.is_visible() else 0
        self.page.wait_for_timeout(300)

    def paso(self, pagina: str, accion: str, captura: bool = False) -> dict[str, Any]:
        """Registra el estado tras una acción: excepciones, errores, avisos y consola."""
        self.esperar()
        excepciones = self.page.locator('[data-testid="stException"]').all_inner_texts()
        errores = self.page.locator('[data-testid="stAlertContentError"]').all_inner_texts()
        avisos = self.page.locator('[data-testid="stAlertContentWarning"]').all_inner_texts()
        nuevo = {"pagina": pagina, "accion": accion, "ok": not excepciones and not errores,
                 "excepciones": [e[:400] for e in excepciones], "errores": errores, "avisos": avisos,
                 "consola": self.consola[:]}
        self.consola.clear()
        if captura:
            nombre = f"{len(self.pasos):03d}_{pagina}_{accion}".replace(" ", "_").replace("/", "-")[:90] + ".png"
            # Streamlit desplaza el contenido dentro de stMain: se agranda la ventana a su altura real.
            alto = self.page.evaluate("document.querySelector('[data-testid=\"stMain\"]').scrollHeight")
            self.page.set_viewport_size({"width": 1440, "height": min(int(alto) + 40, 9000)})
            self.page.wait_for_timeout(1200)
            self.page.screenshot(path=str(self.salida / nombre), full_page=True)
            self.page.set_viewport_size({"width": 1440, "height": 1000})
            self.page.wait_for_timeout(300)
            nuevo["captura"] = nombre
        self.pasos.append(nuevo)
        estado = "OK " if nuevo["ok"] else "ERR"
        print(f"[{estado}] {pagina}: {accion}" + (f" · avisos: {len(avisos)}" if avisos else ""), flush=True)
        return nuevo

    def ir(self, titulo: str) -> None:
        self.page.locator('[data-testid="stSidebarNav"]').get_by_text(titulo, exact=True).click()
        self.esperar()

    def _caja(self, etiqueta: str):
        return self.page.locator('[data-testid="stSelectbox"]').filter(has_text=etiqueta).first

    def _cerrar(self) -> None:
        lista = self.page.get_by_role("listbox")
        if lista.is_visible():
            self.page.keyboard.press("Escape")
            try:
                lista.wait_for(state="hidden", timeout=3000)
            except Exception:  # si Escape no cierra, un clic fuera de la lista sí
                self.page.locator('[data-testid="stHeader"]').click(position={"x": 5, "y": 5})
                lista.wait_for(state="hidden", timeout=5000)

    def _abrir(self, etiqueta: str) -> None:
        # En Streamlit 1.67 la lista es un ComboBox de react-aria: se abre con el botón "Open".
        # Si Streamlit redibuja la lista justo al hacer clic, el clic se pierde: se reintenta.
        for intento in range(4):
            self._cerrar()
            self.esperar()
            self._caja(etiqueta).get_by_role("button", name="Open").click()
            try:
                self.page.get_by_role("listbox").wait_for(timeout=5_000)
                return
            except Exception:
                if intento == 3:
                    raise

    def opciones(self, etiqueta: str) -> list[str]:
        self._abrir(etiqueta)
        textos = self.page.get_by_role("option").all_inner_texts()
        self._cerrar()
        return [t.strip() for t in textos]

    def elegir(self, etiqueta: str, opcion: str) -> None:
        self._abrir(etiqueta)
        self.page.get_by_role("option", name=opcion, exact=True).first.click()
        self.esperar()

    def radio(self, texto: str) -> None:
        self.page.locator('[data-testid="stRadio"]').get_by_text(texto, exact=True).click()
        self.esperar()

    def deslizar(self, etiqueta: str, pasos: int) -> None:
        # En Streamlit 1.67 el deslizador es un input type="range" (react-aria), sin role="slider".
        control = self.page.locator('[data-testid="stSlider"]').filter(has_text=etiqueta).locator('input[type="range"]').first
        control.focus()
        for _ in range(abs(pasos)):
            control.press("ArrowRight" if pasos > 0 else "ArrowLeft")
        self.esperar()

    def pestana(self, nombre: str) -> None:
        self.page.get_by_role("tab", name=nombre).click()
        self.esperar()

    def boton(self, nombre: str) -> None:
        self.page.get_by_role("button", name=nombre).click()
        self.esperar()

    def texto(self) -> str:
        return self.page.locator('[data-testid="stMain"]').inner_text()


# ---------------------------------------------------------------------------------------
# Recorrido
# ---------------------------------------------------------------------------------------
def revisar(r: Revisor) -> dict[str, Any]:
    hallazgos: dict[str, Any] = {}
    r.page.goto(f"http://127.0.0.1:{PUERTO_WEB}/")
    r.page.get_by_role("heading", name="Mantenimiento predictivo explicable en Metal Tech").wait_for()
    r.paso("Inicio", "carga", captura=True)
    hallazgos["conexion"] = next((linea for linea in r.texto().splitlines() if linea.startswith("Conexión")), "")

    r.ir("Planta")
    r.paso("Planta", "carga", captura=True)
    r.deslizar("Instante", 48)
    r.paso("Planta", "mover instante 48 h")
    r.radio("Reservadas (nunca vistas)")
    r.paso("Planta", "unidades reservadas", captura=True)

    r.ir("Simulador")
    r.paso("Simulador", "carga")
    activos = r.opciones("Activo")
    hallazgos["simulador"] = []
    for i, activo in enumerate(activos):
        r.elegir("Activo", activo)
        modos = r.opciones("Falla a simular")
        r.elegir("Falla a simular", modos[1])
        r.boton("Diagnosticar")
        texto = r.texto()
        resultado = "identificó" if "El sistema híbrido identificó" in texto else "difiere" if "Se simuló" in texto else "sin resultado"
        hallazgos["simulador"].append({"activo": activo, "falla": modos[1], "resultado": resultado})
        r.paso("Simulador", f"{activo} - {modos[1]}", captura=i < 2)
    r.elegir("Activo", activos[1])
    r.elegir("Falla a simular", "Operación normal")
    r.boton("Diagnosticar")
    r.paso("Simulador", "operación normal", captura=True)
    expresiones = r.opciones("Observación del técnico")
    r.elegir("Falla a simular", r.opciones("Falla a simular")[1])
    r.elegir("Observación del técnico", expresiones[1])
    r.deslizar("Severidad", 4)
    r.deslizar("Avance", -6)
    r.boton("Diagnosticar")
    r.paso("Simulador", f"con observación '{expresiones[1]}', severidad y avance", captura=True)
    r.elegir("Observación del técnico", "Escribir otra…")
    r.page.locator('[data-testid="stTextInput"] input').fill("huele a quemado y zumba raro")
    r.page.keyboard.press("Enter")
    r.boton("Diagnosticar")
    r.paso("Simulador", "texto libre del técnico")

    r.ir("Explicación")
    r.paso("Explicación", "carga", captura=True)
    for activo in r.opciones("Activo"):
        r.elegir("Activo", activo)
        alertas = r.opciones("Alerta")
        r.elegir("Alerta", alertas[-1])
        r.paso("Explicación", f"{activo} - última alerta")
    r.page.get_by_text("Ver como tabla").first.click()
    r.paso("Explicación", "ver como tabla", captura=True)

    r.ir("Base de conocimiento")
    for seccion in ("Reglas", "FMEA", "Léxico de técnicos", "Ontología", "Decisiones"):
        r.radio(seccion)
        r.paso("Base de conocimiento", f"todos - {seccion}", captura=seccion in ("Reglas", "Ontología"))
    r.elegir("Activo", r.opciones("Activo")[2])
    r.radio("Reglas")
    r.elegir("Modo de falla", r.opciones("Modo de falla")[1])
    r.paso("Base de conocimiento", "reglas filtradas por modo")
    r.radio("Ontología")
    r.page.wait_for_timeout(4000)  # la red de pyvis se estabiliza
    marco = r.page.locator("iframe").count()
    hallazgos["ontologia_iframes"] = marco
    r.paso("Base de conocimiento", "grafo de la ontología", captura=True)

    r.ir("Modelos y comparación")
    for metrica in r.opciones("Métrica"):
        r.elegir("Métrica", metrica)
        r.paso("Modelos y comparación", f"métrica {metrica}", captura=metrica.startswith("F1"))
    r.radio("Máquinas nunca vistas")
    r.paso("Modelos y comparación", "por activo, máquinas nunca vistas", captura=True)

    r.ir("Equidad e impacto")
    for grupo in r.opciones("Agrupar por"):
        r.elegir("Agrupar por", grupo)
        for medida in r.opciones("Medida"):
            r.elegir("Medida", medida)
            r.paso("Equidad e impacto", f"{grupo} - {medida}", captura=grupo == "Turno")
    for ratio in ("3", "5", "9"):
        r.radio(ratio)
        r.paso("Equidad e impacto", f"costo r={ratio}", captura=ratio == "5")

    r.ir("Datos")
    for activo in r.opciones("Activo"):
        r.elegir("Activo", activo)
        sensores = r.opciones("Sensor")
        r.elegir("Sensor", sensores[-1])
        r.paso("Datos", f"{activo} - {sensores[-1]}", captura=activo.startswith("bomba"))
    r.elegir("Unidad", r.opciones("Unidad")[-1])
    r.deslizar("Días a mostrar", 20)
    r.paso("Datos", "unidad reservada y más días", captura=True)

    r.ir("Bitácora y errores")
    for pestana in ("Bitácora (MEMORIA)", "Errores (ERRORES)", "Plan"):
        r.pestana(pestana)
        r.paso("Bitácora", pestana, captura=pestana.startswith("Bitácora"))
    return hallazgos


def main() -> int:
    ap = argparse.ArgumentParser(description="Revisión de la web con Playwright.")
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--ver", action="store_true", help="muestra el navegador")
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8", "METALTECH_API": f"http://127.0.0.1:{PUERTO_API}"}
    api = levantar(["-m", "uvicorn", "metaltech.api.main:app", "--port", str(PUERTO_API)],
                   f"http://127.0.0.1:{PUERTO_API}/health", entorno, args.salida / "api.log")
    web = levantar(["-m", "streamlit", "run", "src/metaltech/dashboard/app.py", "--server.port", str(PUERTO_WEB),
                    "--server.headless", "true"], f"http://127.0.0.1:{PUERTO_WEB}/_stcore/health", entorno,
                   args.salida / "web.log")
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=not args.ver)
            pagina = navegador.new_page(viewport={"width": 1440, "height": 1000})
            pagina.set_default_timeout(ESPERA_MS)
            revisor = Revisor(pagina, args.salida)
            try:
                hallazgos = revisar(revisor)
            except Exception as e:  # deja constancia del punto exacto donde falló
                pagina.screenshot(path=str(args.salida / "fallo.png"), full_page=True)
                hallazgos = {"fallo": f"{type(e).__name__}: {e}"[:1500]}
            navegador.close()
    finally:
        for proceso in (web, api):
            proceso.kill()
    pasos = revisor.pasos
    informe = {"pasos": len(pasos), "con_error": sum(not p["ok"] for p in pasos),
               "con_aviso": sum(bool(p["avisos"]) for p in pasos),
               "consola": sorted({c for p in pasos for c in p["consola"]}), "hallazgos": hallazgos, "detalle": pasos}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in informe.items() if k != "detalle"}, indent=2, ensure_ascii=False))
    return 0 if informe["con_error"] == 0 and "fallo" not in hallazgos else 1


if __name__ == "__main__":
    raise SystemExit(main())
