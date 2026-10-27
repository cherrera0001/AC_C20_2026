# Checklist de requisitos: S06 — La lista

Generado desde `specs/006-lista-cis/spec.md`. No es la lista de verificación del código: es la
del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S05; sin ella, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y si el perfil está firmado
- [ ] FR-003 propuesta partiendo por el inventario: hechos vigentes del registro organizados por el perfil; cada control cita un ancla o declara «a mano»
- [ ] FR-004 campos completos por fila: identificador CIS, justificación, anclajes, estados de aplicabilidad y de confirmación, evidencias, estado, marcas, correcciones
- [ ] FR-005 identificadores con marco, versión e identificador; v8 solo si la v8.1 no se obtiene, declarada; nada inventado
- [ ] FR-006 cero estados de cumplimiento; seleccionar no es prueba ni cobertura
- [ ] FR-007 corrección de justificación con autor, fecha, valores y motivo; descarte y recuperación; altas a mano con fuente; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y justificaciones completas; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente de huellas: producto, entrega y evidencias ancla; «evidencia alterada» y «ancla no vigente»
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `03_hallazgos/`; los previos quedan intactos
- [ ] FR-012 ficha legible por fila, sin extractos de evidencia
- [ ] FR-013 entrega a S07: exactamente los seleccionados, con estado de confirmación y huellas
- [ ] FR-014 perfil cambiado: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen perfil inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 100 % de los controles propuestos citan un hecho ancla o declaran «a mano»
- [ ] SC-002 100 % de las filas citan la huella de la entrega y su estado de firma
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-004 alteración de un byte del JSON detectada
- [ ] SC-005 evidencia ancla alterada: fila marcada y fuera de la entrega; «firmado con evidencia alterada»
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 pendientes por fila y en una sola sección con conteo (manual: medir minutos)
- [ ] SC-009 la entrega contiene exactamente los seleccionados
- [ ] SC-010 huellas de los archivos previos de `03_hallazgos/` sin cambios
- [ ] SC-011 controles documentales «pendiente-documental» con nota en el 100 % de los casos
- [ ] SC-012 recorrido de un tercero hasta los anclas y la evidencia (manual)
- [ ] SC-013 firmado + perfil cambiado = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Medir SC-008 y registrar los minutos en Notes
- [ ] Recorrido SC-012 de un tercero y registro del resultado en Notes
