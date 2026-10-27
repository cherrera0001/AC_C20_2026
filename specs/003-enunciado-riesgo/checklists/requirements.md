# Checklist de requisitos: S03 — El enunciado

Generado desde `specs/003-enunciado-riesgo/spec.md`. No es la lista de verificación del código: es
la del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige el registro de S02; sin él, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y si el registro está firmado
- [ ] FR-003 un enunciado por hecho vigente; «no consta» sin enunciado (vacíos heredados)
- [ ] FR-004 campos completos: identificador, hecho de origen, condición, consecuencia, criterio, impacto, falta, evidencias, estado, marcas, correcciones
- [ ] FR-005 propuestas: condición desde la afirmación; consecuencia por resultado; criterio cualitativo; impacto vacío; falta derivada
- [ ] FR-006 cero estados de cumplimiento; negativo con nota fija
- [ ] FR-007 corrección de condición/consecuencia/criterio/impacto con autor, fecha, valores y motivo; descarte y restablecimiento; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y criterio/impacto completos; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente de huellas: producto, entrega y evidencias; «evidencia alterada» y «hecho no vigente»
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `03_hallazgos/`; los previos quedan intactos
- [ ] FR-012 ficha legible por enunciado, sin extractos de evidencia
- [ ] FR-013 entrega a S04: exactamente los vigentes, con campos y huellas
- [ ] FR-014 registro cambiado: `abrir` firma-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen registro inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 H hechos → H enunciados; M «no consta» → M vacíos
- [ ] SC-002 100 % de enunciados citan hecho y evidencia con huella
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-004 alteración de un byte del JSON detectada
- [ ] SC-005 evidencia alterada: enunciado marcado y fuera de la entrega; «firmado con evidencia alterada»
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 «lo que falta» por enunciado y vacíos en una sola sección con conteo (manual: medir minutos)
- [ ] SC-009 la entrega contiene exactamente los vigentes
- [ ] SC-010 huellas de los archivos previos de `03_hallazgos/` sin cambios
- [ ] SC-011 todo negativo con nota de no-cumplimiento
- [ ] SC-012 recorrido de un tercero hasta la evidencia (manual)
- [ ] SC-013 firmado + registro cambiado = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Medir SC-008 y registrar los minutos en Notes
- [ ] Recorrido SC-009 de un tercero y registro del resultado en Notes
