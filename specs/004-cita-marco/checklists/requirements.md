# Checklist de requisitos: S04 — La cita

Generado desde `specs/004-cita-marco/spec.md`. No es la lista de verificación del código: es la
del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S03; sin ella, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y si el enunciado está firmado
- [ ] FR-003 una cita por riesgo vigente; marcados sin cita vigente; vacíos heredados sin cita
- [ ] FR-004 campos completos: identificador, riesgo de origen, marco, versión, identificador de control, fundamento, adicionales, estado del identificador, evidencias, estado, marcas, correcciones
- [ ] FR-005 correspondencia propuesta con fundamento; identificador solo si consta; si no, «pendiente de confirmar»
- [ ] FR-006 cero estados de cumplimiento; la cita no es prueba; marco mencionado ≠ cobertura
- [ ] FR-007 corrección de marco/versión/identificador/fundamento con autor, fecha, valores y motivo; descarte y restablecimiento; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y marco/versión completos; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente de huellas: producto, entrega y evidencias; «evidencia alterada» y «riesgo no vigente»
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `03_hallazgos/`; los previos quedan intactos
- [ ] FR-012 ficha legible por cita, sin extractos de evidencia
- [ ] FR-013 entrega a S05: exactamente las vigentes, con campos, estado del identificador y huellas
- [ ] FR-014 enunciado cambiado: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen enunciado inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 R riesgos → R citas; V vacíos → V listados
- [ ] SC-002 100 % de las citas citan riesgo, huella de la entrega y evidencia con huella
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-004 alteración de un byte del JSON detectada
- [ ] SC-005 evidencia alterada: cita marcada y fuera de la entrega; «firmado con evidencia alterada»
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 pendientes por cita y en una sola sección con conteo (manual: medir minutos)
- [ ] SC-009 la entrega contiene exactamente las vigentes
- [ ] SC-010 huellas de los archivos previos de `03_hallazgos/` sin cambios
- [ ] SC-011 100 % de correspondencias con fundamento; no verificables quedan pendientes
- [ ] SC-012 recorrido de un tercero hasta la evidencia (manual)
- [ ] SC-013 firmado + enunciado cambiado = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Medir SC-008 y registrar los minutos en Notes
- [ ] Recorrido SC-012 de un tercero y registro del resultado en Notes
