"""Contrasta el simulador con AI4I 2020 y SKAB (D-052).

Descarga los CSV públicos a ``data/external/`` (no se versionan) y escribe
``reports/tables/contraste_datasets.csv``. Requiere el dataset generado.

Uso: ``python scripts/contrastar_datasets.py``
"""

from __future__ import annotations

import urllib.request

import pandas as pd

from metaltech.kb.base import RAIZ

EXTERNOS = RAIZ / "data" / "external"
SKAB = "https://raw.githubusercontent.com/waico/SKAB/master/data"
FUENTES = {
    "ai4i2020.csv": "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv",
    "anomaly-free.csv": f"{SKAB}/anomaly-free/anomaly-free.csv",
    "valve1_0.csv": f"{SKAB}/valve1/0.csv",
    "valve1_5.csv": f"{SKAB}/valve1/5.csv",
    "valve2_0.csv": f"{SKAB}/valve2/0.csv",
    "other_1.csv": f"{SKAB}/other/1.csv",
    "other_9.csv": f"{SKAB}/other/9.csv",
}
CANALES = {"vib_rms_mm_s": "Accelerometer1RMS", "corriente_pct": "Current", "caudal_pct": "Volume Flow RateRMS"}


def descargar() -> None:
    EXTERNOS.mkdir(parents=True, exist_ok=True)
    for nombre, url in FUENTES.items():
        destino = EXTERNOS / nombre
        if not destino.exists():
            peticion = urllib.request.Request(url, headers={"User-Agent": "metaltech-proyecto-universitario"})
            with urllib.request.urlopen(peticion, timeout=90) as r:
                destino.write_bytes(r.read())


def _skab(nombre: str) -> pd.DataFrame:
    return pd.read_csv(EXTERNOS / nombre, sep=";", index_col="datetime", parse_dates=True)


def contrastar() -> pd.DataFrame:
    filas: list[dict] = []
    ai4i = pd.read_csv(EXTERNOS / "ai4i2020.csv")
    falla = ai4i.loc[ai4i["TWF"] == 1, "Tool wear [min]"]
    cnc = pd.read_parquet(RAIZ / "data" / "synthetic" / "centro_cnc.parquet")
    sim = cnc.loc[(cnc["estado"] == "falla") & (cnc["modo_activo"] == "desgaste_herramienta"), "desgaste_herramienta_min"]
    for nombre, fn in (("minimo", "min"), ("mediana", "median"), ("maximo", "max")):
        filas.append({"medida": f"desgaste de herramienta al fallar, {nombre} (min)", "referencia": "AI4I 2020",
                      "publico": round(float(getattr(falla, fn)()), 1), "simulador": round(float(getattr(sim, fn)()), 1)})

    libre = _skab("anomaly-free.csv").resample("10min").mean().dropna()
    bomba = pd.read_parquet(RAIZ / "data" / "synthetic" / "bomba_centrifuga.parquet")
    sana = bomba[(bomba["estado"] == "sano") & (bomba["confusor"] == "ninguno")]
    cv_sim = sana.groupby("unidad", observed=True)[list(CANALES)].agg(lambda s: 100 * s.std() / s.mean()).mean()
    for variable, canal in CANALES.items():
        filas.append({"medida": f"variación en sano a 10 min, CV % ({variable})", "referencia": f"SKAB {canal}",
                      "publico": round(float(100 * libre[canal].std() / libre[canal].mean()), 2),
                      "simulador": round(float(cv_sim[variable]), 2)})

    movidos, total = 0, 0
    for nombre in ("valve1_0.csv", "valve1_5.csv", "valve2_0.csv", "other_1.csv", "other_9.csv"):
        df = _skab(nombre)
        sano, anomalo = df[df["anomaly"] == 0], df[df["anomaly"] == 1]
        for canal in CANALES.values():
            total += 1
            movidos += abs(anomalo[canal].mean() - sano[canal].mean()) >= sano[canal].std()
    filas.append({"medida": "canales que se mueven al menos 1 desviación en anomalía (%)", "referencia": "SKAB, 5 experimentos",
                  "publico": round(100 * movidos / total, 1), "simulador": "80 (por diseño, sin contar la primera variable)"})
    return pd.DataFrame(filas)


def main() -> int:
    descargar()
    tabla = contrastar()
    salida = RAIZ / "reports" / "tables" / "contraste_datasets.csv"
    tabla.to_csv(salida, index=False)
    print(tabla.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
