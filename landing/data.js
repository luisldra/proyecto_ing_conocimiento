// Generado por scripts/generar_datos_landing.py; no editar a mano.
window.DATOS = {
 "conocimiento": {
  "reglas": 55,
  "modos": 31,
  "sintomas": 68,
  "fmea": 41,
  "expresiones": 10,
  "decisiones": 75,
  "referencias": 126,
  "activos": 6,
  "unidades": 32,
  "normas": [
   "ISO 20816-3 (vibración)",
   "ISO 10816-7 vía Europump (bombas)",
   "ISO 17359 y 13374 (monitoreo de condición)",
   "IEC 60034-1 y NEMA MG-1 (motores)",
   "ANSI/HI 9.6.1 (NPSH, cavitación)",
   "IEEE 519 (armónicos)",
   "ISO 4406 (limpieza de aceite)"
  ],
  "datasets": [
   "AI4I 2020",
   "CWRU Bearing",
   "NASA IMS",
   "NASA C-MAPSS",
   "MIMII",
   "SKAB",
   "UCI sistemas hidráulicos"
  ],
  "regla_ejemplo": {
   "id": "R13",
   "si": [
    "margen_npsh_bajo",
    "vibracion_hf_alta",
    "caudal_inestable"
   ],
   "entonces": "Cavitación por NPSH disponible insuficiente",
   "fc": 0.85,
   "accion": "Revisar NPSH disponible: nivel del depósito, válvula y filtro de succión, temperatura del líquido; evitar operar lejos del BEP."
  },
  "expresion_ejemplo": {
   "texto": "la bomba está golpeando",
   "sintoma": "golpeteo_percibido",
   "candidatos": [
    "Cavitación por NPSH disponible insuficiente",
    "Obstrucción de succión/impulsor (filtro, canastilla, incrustaciones)",
    "Desgaste/defecto localizado de rodamiento (pista o elemento rodante)"
   ]
  }
 },
 "resultados": {
  "semillas": 5,
  "f1_test": [
   {
    "sistema": "M0",
    "media": 0.6059,
    "inf": 0.6059,
    "sup": 0.6059
   },
   {
    "sistema": "M1",
    "media": 0.9141,
    "inf": 0.9087,
    "sup": 0.9194
   },
   {
    "sistema": "M2",
    "media": 0.9126,
    "inf": 0.9086,
    "sup": 0.9166
   },
   {
    "sistema": "M3",
    "media": 0.917,
    "inf": 0.9114,
    "sup": 0.9227
   }
  ],
  "f1_no_vista": [
   {
    "sistema": "M0",
    "media": 0.6564,
    "inf": 0.6564,
    "sup": 0.6564
   },
   {
    "sistema": "M1",
    "media": 0.9321,
    "inf": 0.9274,
    "sup": 0.9368
   },
   {
    "sistema": "M2",
    "media": 0.9342,
    "inf": 0.9263,
    "sup": 0.942
   },
   {
    "sistema": "M3",
    "media": 0.9399,
    "inf": 0.9341,
    "sup": 0.9457
   }
  ],
  "fa_confusor_no_vista": [
   {
    "sistema": "M0",
    "media": 0.1732,
    "inf": 0.1732,
    "sup": 0.1732
   },
   {
    "sistema": "M1",
    "media": 0.042,
    "inf": 0.0298,
    "sup": 0.0541
   },
   {
    "sistema": "M2",
    "media": 0.0349,
    "inf": 0.0258,
    "sup": 0.044
   },
   {
    "sistema": "M3",
    "media": 0.0307,
    "inf": 0.0198,
    "sup": 0.0417
   }
  ],
  "m3_m1_f1_no_vista": {
   "media": 0.0078,
   "inf": 0.0033,
   "sup": 0.0124,
   "a_mayor_pct": 86.7
  },
  "m3_m1_fa_no_vista": {
   "media": -0.0112,
   "inf": -0.0137,
   "sup": -0.0088,
   "a_mayor_pct": 10.0
  },
  "m2_m1_f1_no_vista": {
   "media": 0.0021,
   "inf": -0.0068,
   "sup": 0.011,
   "a_mayor_pct": 50.0
  },
  "impacto": {
   "M0": {
    "detectadas_pct": 68.1,
    "eventos_fa": 9.57,
    "costo_r5": 28.42
   },
   "M1": {
    "detectadas_pct": 99.2,
    "eventos_fa": 8.8,
    "costo_r5": 13.36
   },
   "M2": {
    "detectadas_pct": 98.6,
    "eventos_fa": 5.15,
    "costo_r5": 13.28
   },
   "M3": {
    "detectadas_pct": 98.8,
    "eventos_fa": 4.73,
    "costo_r5": 13.15
   }
  },
  "ahorro_m3_vs_m0_pct": {
   "3": 38.02,
   "5": 53.75,
   "9": 68.63
  },
  "xai": {
   "top3_firma": 0.746,
   "top3_azar": 0.33,
   "top3_reglas": 0.675,
   "fidelidad": 0.983,
   "fidelidad_azar": 0.3
  },
  "panel": {
   "comprensibilidad": {
    "modelo": 2.7,
    "hibrida": 3.85
   },
   "confianza": {
    "modelo": 2.12,
    "hibrida": 3.3
   },
   "utilidad": {
    "modelo": 1.67,
    "hibrida": 3.75
   }
  },
  "panel_preferencia": {
   "hibrida": 60,
   "pares": 60
  },
  "equidad": {
   "brecha_turno_m3_pts": 2.2,
   "fa_obs_incorrecta": {
    "M0": 2.08,
    "M3": 0.32
   },
   "fa_sin_obs": {
    "M0": 1.05,
    "M3": 0.28
   }
  },
  "latencia_ms": {
   "sin_explicacion": 21.24,
   "con_explicacion": 79.24
  }
 },
 "ejemplo": {
  "texto": "Alerta de degradación térmica del aislamiento del devanado (puntaje 87%). El modelo se apoyó sobre todo en temp_devanado_c (47%), desbalance_corriente_pct (18%), corriente_pct (15%). La respalda la regla R07: temp_devanado_c = 130.05 (>= 130); desbalance_corriente_pct = 7.06 (>= 5). Acción sugerida: Medir resistencia de aislamiento (megóhmetro) e índice de polarización; revisar la tensión de alimentación por fase.",
  "variables": [
   {
    "variable": "temp_devanado_c",
    "peso": 0.4679483473300934,
    "en_reglas": true
   },
   {
    "variable": "desbalance_corriente_pct",
    "peso": 0.18322446942329407,
    "en_reglas": true
   },
   {
    "variable": "corriente_pct",
    "peso": 0.14838585257530212,
    "en_reglas": false
   }
  ],
  "unidad": "motor_electrico_01",
  "reglas": [
   "R07"
  ]
 },
 "datos": {
  "meses": 36,
  "filas": 5049216,
  "episodios": 1075,
  "observaciones": 2118
 },
 "prototipo": {
  "endpoints": 11,
  "paginas": 8
 },
 "repositorio": "https://github.com/luisldra/proyecto_ing_conocimiento"
};
