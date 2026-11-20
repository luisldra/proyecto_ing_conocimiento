// Landing de Metal Tech: rellena el contenido y dibuja los gráficos en SVG a partir de data.js.
(function () {
  "use strict";
  const D = window.DATOS;
  if (!D) {
    document.body.insertAdjacentHTML("afterbegin",
      "<p style='padding:16px;background:#fde;'>Falta data.js: ejecute python scripts/generar_datos_landing.py</p>");
    return;
  }
  const R = D.resultados, C = D.conocimiento;
  const SISTEMAS = ["M0", "M1", "M2", "M3"];
  const NOMBRE = { M0: "M0 · solo reglas", M1: "M1 · solo modelo", M2: "M2 · modelo + conocimiento", M3: "M3 · fusión" };
  const CORTO = { M0: "Reglas", M1: "Modelo", M2: "Modelo + conocimiento", M3: "Fusión" };
  const DESCRIPCION = {
    M0: "El sistema experto: reglas con factores de certeza sobre síntomas y lo que reporta el técnico.",
    M1: "Deep Learning sobre la ventana de sensores, una arquitectura por tipo de activo.",
    M2: "El mismo modelo, con certezas de las reglas como entradas adicionales.",
    M3: "Combina la probabilidad del modelo y la certeza de las reglas.",
  };
  const color = (s) => getComputedStyle(document.documentElement).getPropertyValue("--" + s.toLowerCase()).trim();
  const pct = (x, d = 0) => (100 * x).toLocaleString("es-CO", { maximumFractionDigits: d, minimumFractionDigits: d }) + " %";
  const num = (x, d = 2) => x.toLocaleString("es-CO", { maximumFractionDigits: d, minimumFractionDigits: d });
  const $ = (id) => document.getElementById(id);
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const por = (lista) => Object.fromEntries(lista.map((x) => [x.sistema, x]));

  // --- Enlaces --------------------------------------------------------------------------------
  const enlaces = { repositorio: D.repositorio, web: D.repositorio + "#comandos",
                    documento: D.repositorio + "/blob/main/docs/documento_APA/documento_apa.pdf",
                    poster: D.repositorio + "/blob/main/docs/poster/poster.pdf" };
  document.querySelectorAll("[data-enlace]").forEach((a) => { a.href = enlaces[a.dataset.enlace]; a.target = "_blank"; a.rel = "noopener"; });

  // --- Cifras de portada ------------------------------------------------------------------------
  const f1 = por(R.f1_no_vista);
  const reduccion = 1 - R.impacto.M3.eventos_fa / R.impacto.M1.eventos_fa;
  const campos = {
    f1M3: num(f1.M3.media, 3),
    reduccionEventos: pct(reduccion),
    detectadasM3: num(R.impacto.M3.detectadas_pct, 1) + " %",
    latencia: Math.round(R.latencia_ms.con_explicacion) + " ms",
  };
  document.querySelectorAll("[data-campo]").forEach((el) => { el.textContent = campos[el.dataset.campo]; });

  // --- Conocimiento -----------------------------------------------------------------------------
  const contadores = [
    [C.decisiones, "decisiones justificadas"], [C.referencias, "referencias APA 7"], [C.reglas, "reglas con certeza"],
    [C.modos, "modos de falla"], [C.sintomas, "síntomas"], [C.fmea, "filas FMEA"], [C.unidades, "máquinas simuladas"],
  ];
  $("contadores").innerHTML = contadores.map(([v, t]) =>
    `<div class="contador"><span class="contador__valor">${v}</span><span class="contador__texto">${t}</span></div>`).join("");
  $("normas").innerHTML = C.normas.map((n) => `<li>${esc(n)}</li>`).join("");
  $("datasets").innerHTML = C.datasets.map((n) => `<li>${esc(n)}</li>`).join("");
  const r = C.regla_ejemplo;
  $("regla").innerHTML = `<b>${esc(r.id)}</b> · SI ${r.si.map((s) => esc(s)).join(" <b>∧</b> ")}<br>ENTONCES ${esc(r.entonces)} <b>(FC ${num(r.fc)})</b>`;
  $("regla-accion").textContent = "Acción: " + r.accion;
  const e = C.expresion_ejemplo;
  $("expresion").innerHTML = `«${esc(e.texto)}» → <span class="chip">${esc(e.sintoma)}</span><br>Sugiere: `
    + e.candidatos.map((c) => `<span class="chip">${esc(c)}</span>`).join("");
  $("leyenda-sistemas").innerHTML = SISTEMAS.map((s) =>
    `<li><span class="muestra" style="background:${color(s)}"></span><span><strong>${NOMBRE[s]}.</strong> ${DESCRIPCION[s]}</span></li>`).join("");

  // --- Gráficos SVG -----------------------------------------------------------------------------
  const NS = "http://www.w3.org/2000/svg";
  function svg(ancho, alto) {
    const s = document.createElementNS(NS, "svg");
    s.setAttribute("viewBox", `0 0 ${ancho} ${alto}`);
    s.setAttribute("role", "img");
    return s;
  }
  function el(nombre, atributos, padre, texto) {
    const n = document.createElementNS(NS, nombre);
    for (const [k, v] of Object.entries(atributos)) n.setAttribute(k, v);
    if (texto !== undefined) n.textContent = texto;
    padre.appendChild(n);
    return n;
  }
  function tabla(filas, columnas) {
    return `<table><thead><tr>${columnas.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>`
      + filas.map((f) => `<tr>${f.map((v) => `<td>${v}</td>`).join("")}</tr>`).join("") + "</tbody></table>";
  }

  // Puntos con intervalo (F1), con etiqueta directa del valor.
  (function graficoF1() {
    const A = 520, H = 300, m = { i: 46, d: 16, a: 24, b: 44 };
    const s = svg(A, H);
    s.setAttribute("aria-label", "F1 macro por sistema en máquinas nunca vistas, con intervalo del 95 %");
    const yMin = 0.5, yMax = 1.0;
    const y = (v) => m.a + (H - m.a - m.b) * (1 - (v - yMin) / (yMax - yMin));
    const x = (i) => m.i + ((A - m.i - m.d) / SISTEMAS.length) * (i + 0.5);
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0].forEach((t) => {
      el("line", { x1: m.i, x2: A - m.d, y1: y(t), y2: y(t), class: "rejilla" }, s);
      el("text", { x: m.i - 8, y: y(t) + 4, "text-anchor": "end" }, s, num(t, 1));
    });
    SISTEMAS.forEach((k, i) => {
      const d = f1[k], g = el("g", { class: "marca-dato" }, s);
      el("title", {}, g, `${NOMBRE[k]}: ${num(d.media, 3)} [${num(d.inf, 3)}, ${num(d.sup, 3)}]`);
      el("line", { x1: x(i), x2: x(i), y1: y(d.inf), y2: y(d.sup), stroke: color(k), "stroke-width": 2 }, g);
      el("circle", { cx: x(i), cy: y(d.media), r: 7, fill: color(k), stroke: "var(--superficie)", "stroke-width": 2 }, g);
      el("text", { x: x(i), y: y(d.media) - 14, "text-anchor": "middle", class: "etiqueta-valor" }, g, num(d.media, 3));
      el("text", { x: x(i), y: H - m.b + 22, "text-anchor": "middle" }, s, CORTO[k]);
    });
    $("grafico-f1").appendChild(s);
    $("tabla-f1").innerHTML = tabla(SISTEMAS.map((k) => [NOMBRE[k], num(f1[k].media, 3), num(f1[k].inf, 3), num(f1[k].sup, 3)]),
      ["Sistema", "Media", "IC 95 % inf.", "IC 95 % sup."]);
  })();

  // Barras con base en cero (eventos de falsa alarma), con etiqueta directa.
  function barras(contenedor, datos, formato, etiqueta) {
    const A = 520, H = 300, m = { i: 16, d: 16, a: 28, b: 44 };
    const s = svg(A, H);
    s.setAttribute("aria-label", etiqueta);
    const max = Math.max(...datos.map((d) => d.valor)) * 1.15;
    const ancho = (A - m.i - m.d) / datos.length;
    const y = (v) => m.a + (H - m.a - m.b) * (1 - v / max);
    el("line", { x1: m.i, x2: A - m.d, y1: y(0), y2: y(0), class: "eje" }, s);
    datos.forEach((d, i) => {
      const x0 = m.i + ancho * i + ancho * 0.18, w = ancho * 0.64, g = el("g", { class: "marca-dato" }, s);
      el("title", {}, g, `${d.nombre}: ${formato(d.valor)}`);
      const alto = y(0) - y(d.valor), r = Math.min(4, alto);
      el("path", { d: `M${x0},${y(0)} V${y(d.valor) + r} Q${x0},${y(d.valor)} ${x0 + r},${y(d.valor)} H${x0 + w - r} Q${x0 + w},${y(d.valor)} ${x0 + w},${y(d.valor) + r} V${y(0)} Z`, fill: d.color }, g);
      el("text", { x: x0 + w / 2, y: y(d.valor) - 8, "text-anchor": "middle", class: "etiqueta-valor" }, g, formato(d.valor));
      el("text", { x: x0 + w / 2, y: H - m.b + 22, "text-anchor": "middle" }, s, d.corto);
    });
    contenedor.appendChild(s);
  }
  barras($("grafico-eventos"), SISTEMAS.map((k) => ({ nombre: NOMBRE[k], corto: CORTO[k], valor: R.impacto[k].eventos_fa, color: color(k) })),
    (v) => num(v, 1), "Eventos de falsa alarma por unidad y año, por sistema");
  $("tabla-eventos").innerHTML = tabla(SISTEMAS.map((k) => [NOMBRE[k], num(R.impacto[k].eventos_fa, 1), num(R.impacto[k].detectadas_pct, 1) + " %"]),
    ["Sistema", "Eventos de falsa alarma / unidad-año", "Fallas detectadas"]);

  // --- Resultados en texto ---------------------------------------------------------------------
  const dF1 = R.m3_m1_f1_no_vista, dFA = R.m3_m1_fa_no_vista, dM2 = R.m2_m1_f1_no_vista;
  $("resumen-resultados").textContent = `Con ${R.semillas} semillas y en máquinas que el modelo nunca vio, combinar el modelo con las reglas `
    + `(M3) mejora al modelo solo en F1 por poco pero de forma consistente (${dF1.media >= 0 ? "+" : ""}${num(dF1.media, 3)}, intervalo `
    + `${num(dF1.inf, 3)} a ${num(dF1.sup, 3)}) y, sobre todo, reduce las falsas alarmas.`;
  const hallazgos = [
    ["Menos falsas alarmas", `La fusión tiene ${pct(reduccion)} menos eventos de falsa alarma que el modelo solo y `
      + `${num(-100 * dFA.media, 1)} puntos menos de falsa alarma ante eventos que imitan fallas.`],
    ["El modelo supera a las reglas", `F1 de ${num(f1.M1.media, 3)} del modelo frente a ${num(f1.M0.media, 3)} de las reglas solas; las reglas detectan `
      + `${num(R.impacto.M0.detectadas_pct, 0)} % de las fallas y la fusión ${num(R.impacto.M3.detectadas_pct, 1)} %.`],
    ["Cómo integrar importa", `Usar el conocimiento como entrada del modelo (M2) no se distingue de M1 (${dM2.media >= 0 ? "+" : ""}${num(dM2.media, 3)}); `
      + "combinarlo a la salida (M3) sí aporta."],
    ["Costo simulado", `Ahorro de la fusión frente a las reglas de ${num(R.ahorro_m3_vs_m0_pct[3], 0)} %, ${num(R.ahorro_m3_vs_m0_pct[5], 0)} % y `
      + `${num(R.ahorro_m3_vs_m0_pct[9], 0)} % según cuánto cueste una falla no detectada.`],
  ];
  $("hallazgos").innerHTML = hallazgos.map(([t, p]) => `<li><strong>${t}</strong>${esc(p)}</li>`).join("");

  // --- Explicación ------------------------------------------------------------------------------
  $("ejemplo-texto").textContent = D.ejemplo.texto;
  barras($("grafico-sensores"), D.ejemplo.variables.map((v) => ({ nombre: v.variable, corto: v.variable, valor: v.peso,
    color: v.en_reglas ? color("M3") : color("M1") })), (v) => pct(v), "Peso de los tres sensores más importantes en la alerta de ejemplo");
  $("grafico-sensores").insertAdjacentHTML("beforeend",
    `<p class="nota"><span class="muestra" style="display:inline-block;background:${color("M3")}"></span> también aparece en la regla que respalda la alerta · `
    + `<span class="muestra" style="display:inline-block;background:${color("M1")}"></span> solo en el modelo</p>`);
  const X = R.xai, P = R.panel;
  $("metricas-xai").innerHTML = [
    [pct(X.top3_firma), `de los 3 sensores con más peso son los que la falla mueve de verdad (azar: ${pct(X.top3_azar)})`],
    [pct(X.top3_reglas), "coinciden con los sensores de las reglas disparadas"],
    [num(X.fidelidad), `caída de confianza al anular esos sensores (azar: ${num(X.fidelidad_azar)})`],
    [`${num(P.utilidad.hibrida)} / 5`, `utilidad de la explicación híbrida para el panel (modelo solo: ${num(P.utilidad.modelo)})`],
  ].map(([v, t]) => `<div class="contador"><span class="contador__valor">${v}</span><span class="contador__texto">${t}</span></div>`).join("");

  // --- Equidad ----------------------------------------------------------------------------------
  const Q = R.equidad;
  $("equidad").innerHTML = [
    `<strong>El sesgo del turno no pasa al sistema.</strong> De noche los técnicos aciertan menos, pero la brecha de acierto por turno de la fusión es de ${num(Q.brecha_turno_m3_pts, 1)} puntos, como la del modelo solo.`,
    `<strong>La fusión amortigua el error humano.</strong> Con observaciones incorrectas, las reglas solas suben su falsa alarma a ${num(Q.fa_obs_incorrecta.M0, 2)} % (sin observación: ${num(Q.fa_sin_obs.M0, 2)} %); la fusión apenas cambia (${num(Q.fa_obs_incorrecta.M3, 2)} % frente a ${num(Q.fa_sin_obs.M3, 2)} %).`,
    "<strong>Evaluación por agentes.</strong> Sin técnicos disponibles, las explicaciones las juzgó un panel de agentes; es exploratorio y está declarado.",
  ].map((t) => `<li>${t}</li>`).join("");
})();
