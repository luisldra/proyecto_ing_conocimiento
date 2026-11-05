"""Descarga un JDK 17 portable (Eclipse Temurin) en .tools/jdk17 para el razonador HermiT.

Uso:  python scripts/instalar_jdk.py
No modifica el sistema: todo queda dentro de .tools/ (ignorado por git). Verifica el SHA-256
que publica la API de Adoptium antes de extraer. Solo Windows x64 (ver ERR-008 para otros SO).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / ".tools" / "jdk17"
API = ("https://api.adoptium.net/v3/assets/latest/17/hotspot"
       "?architecture=x64&image_type=jdk&os=windows&vendor=eclipse")


def _pedido(url: str) -> urllib.request.Request:
    # La API y GitHub rechazan el User-Agent por defecto de urllib (HTTP 403).
    return urllib.request.Request(url, headers={"User-Agent": "metaltech-setup/1.0"})


def main() -> int:
    java = DESTINO / "bin" / "java.exe"
    if java.exists():
        print(f"JDK ya instalado en {DESTINO}")
        return 0
    with urllib.request.urlopen(_pedido(API), timeout=60) as r:
        paquete = json.load(r)[0]["binary"]["package"]
    descarga = RAIZ / ".tools" / "descarga"
    descarga.mkdir(parents=True, exist_ok=True)
    zip_path = descarga / paquete["name"]
    if not zip_path.exists():
        print(f"Descargando {paquete['name']} ({paquete['size'] / 1e6:.0f} MB)...")
        with urllib.request.urlopen(_pedido(paquete["link"]), timeout=900) as r,                 open(zip_path, "wb") as f:
            shutil.copyfileobj(r, f)
    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if sha != paquete["checksum"]:
        zip_path.unlink()
        print(f"SHA-256 no coincide: {sha} != {paquete['checksum']}", file=sys.stderr)
        return 1
    print("SHA-256 verificado. Extrayendo...")
    tmp = descarga / "extraido"
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tmp)
    carpeta = next(p for p in tmp.iterdir() if p.is_dir())
    shutil.rmtree(DESTINO, ignore_errors=True)
    shutil.move(str(carpeta), str(DESTINO))
    shutil.rmtree(descarga, ignore_errors=True)
    print(f"JDK instalado en {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
