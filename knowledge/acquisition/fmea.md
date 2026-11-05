# FMEA – Metal Tech

> Versión legible de [fmea.yaml](fmea.yaml), que es la fuente máquina-legible; ambas tienen el mismo contenido. Autor: agente Investigador, Fase 1 (2026-10-29). Las decisiones D-NNN están en [decisiones.md](decisiones.md).

## Escalas (D-035)

| Valor | Severidad (S) | Ocurrencia (O) | Detección (D) |
|---|---|---|---|
| 1–2 | Sin efecto o efecto menor en calidad | Remota (una vez en varios años por unidad) | Casi segura: un sensor continuo dispara antes de la falla |
| 3–4 | Pérdida leve de rendimiento; paro corto | Baja (una vez al año) | Alta: firma clara en una variable monitoreada |
| 5–6 | Paro no planificado de una máquina o scrap de lote | Moderada (varias veces al año) | Moderada: requiere combinar varias variables o tendencia |
| 7–8 | Paro de línea, daño a componentes mayores | Alta (mensual) | Baja: firma débil o tardía; depende de inspección |
| 9–10 | Riesgo de seguridad o daño catastrófico, sin aviso | Muy alta (semanal o más) | Casi imposible con los sensores disponibles |

NPR = S × O × D. Los valores S/O/D son juicio documentado del agente a partir de las fuentes citadas, no datos de campo de Metal Tech; confianza media-baja (ver D-035).

## Motor eléctrico de inducción (`motor_electrico`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| rodamientos | `falla_lubricacion_rodamiento` | `temp_rodamiento_alta`, `vibracion_hf_alta` | falta de grasa, exceso de grasa, grasa incompatible o degradada | relubricar segun plan, corregir cantidad e intervalo, vigilar tendencia 24h | 7 | 6 | 5 | **210** | D-008, D-010, D-033 |
| rodamientos | `desgaste_rodamiento` | `vibracion_impulsiva`, `vibracion_hf_alta`, `vibracion_hf_critica`, `temp_rodamiento_alta` | fatiga, contaminacion lubricante, sobrecarga por desalineacion, corrientes por rodamiento variador | analisis envolvente, planificar cambio rodamiento, aislar rodamiento o escobilla a tierra | 8 | 6 | 4 | **192** | D-010, D-036 |
| estator devanado | `degradacion_aislamiento` | `temp_devanado_alta`, `desbalance_corriente_alto`, `corriente_alta`, `olor_quemado_percibido` | sobrecarga sostenida, perdida de fase, ventilacion obstruida, humedad contaminacion, picos dv dt variador | prueba megohmetro e indice polarizacion, prueba surge, reducir carga, rebobinado o reemplazo | 9 | 4 | 5 | **180** | D-005, D-006, D-032 |
| variador | `falla_variador` | `disparos_intermitentes`, `disparos_frecuentes`, `distorsion_armonica_alta`, `tension_bus_dc_alta`, `temp_variador_alta` | rampas muy cortas, datos de motor erroneos, cable largo sin reactancia, regeneracion sin resistencia de frenado, condensadores bus envejecidos, ventilador del variador | leer registro de fallas, ajustar rampas y parametros, reactancia o filtro, resistencia de frenado, mantenimiento ventiladores | 6 | 5 | 6 | **180** | D-030 |
| contactor | `falla_contactor` | `desbalance_corriente_critico`, `temp_devanado_alta` | contactos picados, bobina debil, bornes flojos, fin de vida electrica | inspeccion termografica tablero, cambio de contactos o contactor, reapriete bornes | 7 | 4 | 5 | **140** | D-006, D-031 |
| eje acople | `desalineacion_eje` | `vibracion_alerta`, `vibracion_creciente`, `vibracion_2x_elevada`, `vibracion_axial_alta` | montaje incorrecto, pata coja, dilatacion termica, asentamiento de base | alineacion laser, corregir pata coja, reapriete anclajes | 6 | 6 | 3 | **108** | D-003, D-004, D-011 |
| ventilacion | `sobrecalentamiento_ventilacion` | `temp_devanado_alta`, `corriente_en_rango` | rejillas aletas sucias, ventilador danado, temperatura ambiente alta, operacion a baja velocidad con variador | limpiar carcasa y rejillas, verificar ventilador, ventilacion forzada si baja velocidad | 7 | 5 | 3 | **105** | D-005, D-033 |
| carga accionada | `sobrecarga_mecanica` | `sobrecorriente`, `corriente_alta`, `temp_devanado_alta` | atasco de la maquina accionada, freno arrastrando, proceso fuera de diseno | verificar carga, comparar con corriente de placa y fs, ajustar proteccion | 7 | 5 | 3 | **105** | D-005, D-007 |
| rotor | `desbalanceo_rotor` | `vibracion_alerta`, `vibracion_creciente`, `vibracion_1x_dominante` | acumulacion de suciedad, perdida de masa ventilador, barras de rotor danadas | limpieza, balanceo en sitio | 6 | 4 | 3 | **72** | D-003, D-011 |

## Bomba centrífuga (`bomba_centrifuga`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| sello mecanico | `desgaste_sello_mecanico` | `fuga_sello` | operacion en seco, vibracion excesiva, abrasivos, plan de lavado inadecuado | cambio de sello, revisar plan de lavado, corregir vibracion y alineacion | 7 | 6 | 5 | **210** | D-015 |
| impulsor | `cavitacion` | `margen_npsh_bajo`, `margen_npsh_insuficiente`, `vibracion_hf_alta`, `caudal_inestable`, `presion_descarga_baja`, `golpeteo_percibido` | nivel bajo en succion, filtro succion obstruido, temperatura liquido alta, operacion lejos del bep | restablecer npsha, limpiar filtro succion, reducir caudal, inspeccionar erosion impulsor | 8 | 5 | 4 | **160** | D-012, D-013 |
| rodamientos | `desgaste_rodamiento` | `vibracion_impulsiva`, `vibracion_hf_alta`, `temp_rodamiento_alta` | fatiga, contaminacion del aceite, sobrecarga axial por operacion fuera bep | analisis envolvente, cambio de rodamientos, revisar lubricante | 8 | 5 | 4 | **160** | D-009, D-010 |
| carcasa succion | `obstruccion_bomba` | `caudal_bajo`, `corriente_baja`, `presion_descarga_baja` | objetos extranos, incrustaciones, canastilla sucia, valvula parcialmente cerrada | limpiar canastilla e impulsor, verificar valvulas | 6 | 5 | 4 | **120** | D-014 |
| eje acople | `desalineacion_eje` | `vibracion_creciente`, `vibracion_2x_elevada`, `vibracion_axial_alta` | esfuerzos de tuberia, montaje, dilatacion termica | alineacion laser, revisar soportes de tuberia | 6 | 5 | 3 | **90** | D-004, D-011 |
| impulsor | `desbalanceo_rotor` | `vibracion_alerta`, `vibracion_1x_dominante` | erosion por cavitacion, incrustaciones en impulsor | balanceo del impulsor, reemplazo del impulsor | 5 | 3 | 3 | **45** | D-003, D-011 |

## Compresor de tornillo (`compresor_tornillo`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| red distribucion | `fuga_aire_red` | `carga_compresor_alta`, `presion_descarga_baja` | racores y mangueras, purgadores abiertos, herramientas y acoples desgastados | deteccion ultrasonica de fugas, prueba de aislamiento, programa de fugas | 5 | 8 | 5 | **200** | D-017, D-019 |
| rodamientos | `desgaste_rodamiento` | `vibracion_impulsiva`, `vibracion_hf_alta` | fatiga, dilucion o degradacion del aceite | analisis envolvente, analisis de aceite, overhaul del elemento | 9 | 3 | 5 | **135** | D-010 |
| valvula admision | `falla_valvula_admision` | `presion_descarga_baja`, `corriente_baja` | solenoide de control, barniz en el piston, filtro de aire obstruido | revisar apertura en carga, limpiar o reparar valvula, cambiar filtro de aire | 6 | 4 | 4 | **96** | D-017 |
| separador aceite | `obstruccion_separador` | `dp_separador_alto`, `presion_descarga_baja` | fin de vida del elemento, aceite degradado o barnizado | cambiar elemento separador, cambiar aceite | 6 | 5 | 3 | **90** | D-017, D-018 |
| enfriador aceite | `sobrecalentamiento_compresor` | `temp_descarga_alta`, `temp_descarga_critica`, `corriente_en_rango`, `calor_percibido` | enfriador sucio, nivel de aceite bajo, aceite degradado, valvula termostatica, ventilacion de sala deficiente | limpiar enfriador, reponer o cambiar aceite, verificar termostatica, mejorar ventilacion | 8 | 5 | 2 | **80** | D-016 |
| elemento tornillo | `desalineacion_eje` | `vibracion_alerta`, `vibracion_2x_elevada`, `vibracion_axial_alta` | montaje del acople, desgaste del acople | alineacion, cambio de elemento elastico | 6 | 3 | 3 | **54** | D-011 |

## Prensa hidráulica (`prensa_hidraulica`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| cilindro principal | `fuga_interna_cilindro` | `caida_presion_retencion`, `tiempo_ciclo_alto`, `temp_aceite_alta` | sello de piston desgastado, rayado de camisa, contaminacion | prueba de bypass fin de carrera, aislar valvulas, reemplazo de sellos | 7 | 5 | 6 | **210** | D-022 |
| valvula direccional proporcional | `valvula_hidraulica_pegada` | `presion_sistema_alta`, `tiempo_ciclo_alto`, `aceite_contaminado`, `prensa_dura_percibida` | barniz, particulas en carrete, bobina debil, aceite frio | verificar respuesta bobina vs posicion, limpiar o reemplazar valvula, filtrar aceite, calentar aceite antes de producir | 8 | 4 | 6 | **192** | D-021, D-023 |
| sellos | `fuga_hidraulica_externa` | `nivel_tanque_bajo`, `presion_sistema_baja` | manguera danada, racor flojo, sello de vastago desgastado, temperatura excesiva | bloqueo y aislamiento de energia, reemplazo de manguera o sello, reponer aceite filtrado | 8 | 6 | 3 | **144** | D-020, D-022 |
| tanque filtros | `contaminacion_aceite_hidraulico` | `aceite_contaminado` | filtro saturado o bypass, respiradero sin filtro, ingreso por sellos, aceite nuevo sin filtrar | cambio de filtros, filtrado en rinon, conteo de particulas iso4406 | 6 | 6 | 4 | **144** | D-021 |
| enfriador | `sobrecalentamiento_aceite_hidraulico` | `temp_aceite_alta`, `temp_aceite_critica` | enfriador sucio o sin agua, valvula de alivio descargando, fugas internas | limpiar enfriador, ajustar alivio, buscar fugas internas | 6 | 5 | 2 | **60** | D-020 |

## Banda transportadora (`banda_transportadora`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| rodillos portantes | `falla_rodillo` | `vibracion_impulsiva`, `corriente_alta`, `cascabeleo_percibido` | rodamiento del rodillo danado, rodillo trabado por material, sellos del rodillo | inspeccion termografica o acustica, reemplazo de rodillos | 5 | 7 | 6 | **210** | D-024, D-026 |
| banda empalme | `desalineacion_banda` | `desvio_banda`, `corriente_alta`, `banda_corrida_percibida` | tambores o rodillos fuera de escuadra, empalme no escuadrado, rodillo trabado, carga descentrada, acumulacion de material | alinear tambores y rodillos, rehacer empalme, rodillos autoalineantes, centrar carga | 6 | 7 | 3 | **126** | D-024 |
| banda empalme | `rotura_banda` | `velocidad_banda_nula`, `corriente_baja` | empalme deteriorado, objeto atrapado, sobretension, desgaste de bordes por corrimiento | paro y bloqueo, reemplazar o reempalmar, inspeccion periodica de empalmes | 9 | 2 | 7 | **126** | D-025 |
| rodamientos | `desgaste_rodamiento` | `vibracion_impulsiva`, `temp_rodamiento_alta` | fatiga, contaminacion | analisis envolvente, cambio de rodamiento del tambor | 7 | 4 | 4 | **112** | D-010 |
| tambor motriz | `deslizamiento_banda` | `deslizamiento_alto` | tension insuficiente, recubrimiento de tambor gastado, agua o material entre banda y tambor, sobrecarga | ajustar tension, recubrir tambor, limpiar | 5 | 5 | 4 | **100** | D-025 |
| motorreductor | `sobrecarga_mecanica` | `sobrecorriente`, `corriente_alta` | atasco de material, sobrecarga de piezas | despejar atasco, verificar carga | 7 | 4 | 3 | **84** | D-007 |

## Centro de mecanizado CNC (`centro_cnc`)

| Componente | Modo de falla | Síntomas medibles | Causas | Acciones | S | O | D | NPR | Fuentes |
|---|---|---|---|---|---|---|---|---|---|
| herramienta | `rotura_herramienta` | `carga_husillo_caida_subita`, `impacto_vibracion` | desgaste no detectado, chatter, inclusion dura en material, evacuacion de viruta deficiente | paro de avance, inspeccion con palpador, revisar pieza | 7 | 5 | 4 | **140** | D-028 |
| herramienta | `desgaste_herramienta` | `desgaste_herramienta_alto`, `desgaste_herramienta_limite`, `carga_husillo_alta` | vida util alcanzada, parametros de corte agresivos, refrigerante insuficiente | cambio de herramienta, revisar parametros de corte | 5 | 9 | 3 | **135** | D-027, D-036 |
| husillo | `colision_husillo` | `impacto_vibracion`, `carga_husillo_critica` | error de programa, offset de herramienta erroneo, sujecion de pieza | paro inmediato, verificar runout y rodamientos, simulacion de programa | 10 | 2 | 6 | **120** | D-028 |
| husillo | `vibracion_chatter` | `carga_husillo_inestable`, `vibracion_hf_alta`, `vibracion_alerta` | profundidad de corte excesiva, voladizo largo, velocidad en zona inestable | ajustar rpm a lobulo estable, reducir profundidad, acortar voladizo | 5 | 6 | 4 | **120** | D-029 |
| rodamientos husillo | `desgaste_rodamiento` | `vibracion_impulsiva`, `vibracion_hf_alta`, `temp_husillo_alta` | fatiga, colisiones previas, contaminacion por refrigerante | analisis envolvente, reconstruccion del husillo | 8 | 3 | 5 | **120** | D-010 |
| rodamientos husillo | `sobrecalentamiento_husillo` | `temp_husillo_alta`, `vibracion_hf_alta` | falla del enfriador, lubricacion aceite aire deficiente, precarga excesiva | revisar enfriador, revisar lubricacion, ciclo de calentamiento | 7 | 3 | 3 | **63** | D-010, D-029 |

## Prioridades (NPR más alto)

| # | Activo | Modo de falla | NPR |
|---|---|---|---|
| 1 | prensa_hidraulica | `fuga_interna_cilindro` | 210 |
| 2 | motor_electrico | `falla_lubricacion_rodamiento` | 210 |
| 3 | bomba_centrifuga | `desgaste_sello_mecanico` | 210 |
| 4 | banda_transportadora | `falla_rodillo` | 210 |
| 5 | compresor_tornillo | `fuga_aire_red` | 200 |
| 6 | prensa_hidraulica | `valvula_hidraulica_pegada` | 192 |
| 7 | motor_electrico | `desgaste_rodamiento` | 192 |
| 8 | motor_electrico | `falla_variador` | 180 |

Los modos con NPR alto y detección D ≥ 5 (fuga interna, sello mecánico, falla de rodillo, lubricación) son donde el modelo DL debería aportar más que las reglas.
