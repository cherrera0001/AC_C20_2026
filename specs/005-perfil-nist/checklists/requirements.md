# Checklist de requisitos: S05 — El perfil

Generado desde `specs/005-perfil-nist/spec.md`. No es la lista de verificación del código: es la
del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S04; sin ella, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y si la cita está firmada
- [ ] FR-003 seis secciones: Gobernar, Identificar, Proteger, Detectar, Responder, Recuperar, en ese orden
- [ ] FR-004 campos completos por sección: función, síntesis, riesgos citados, vacíos con motivo, falta, evidencias, estado, marcas, correcciones
- [ ] FR-005 asignación propuesta desde dominio, resultado y fundamento; movible y múltiple, con motivo; «no asignado» declarado
- [ ] FR-006 cero estados de cumplimiento; función vacía = «no consta» con motivo, nunca «sin hallazgos»
- [ ] FR-007 corrección de síntesis y reasignación con autor, fecha, valores y motivo; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y seis síntesis completas; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente de huellas: producto, entrega y evidencias; «evidencia alterada» y «riesgo no vigente»
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `03_hallazgos/`; los previos quedan intactos
- [ ] FR-012 ficha legible por sección, sin extractos de evidencia
- [ ] FR-013 entrega a S06: seis secciones con riesgos vigentes, vacíos con motivo y huellas
- [ ] FR-014 cita cambiada: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen cita inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 seis secciones; V vacíos con motivo; cada cita vigente aparece o queda «no asignada» declarada
- [ ] SC-002 100 % de las secciones citan la huella de la entrega y su estado de firma
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-004 alteración de un byte del JSON detectada
- [ ] SC-005 evidencia alterada: riesgo marcado y sección sin acreditarlo; «firmado con evidencia alterada»
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 «lo que falta» por sección y vacíos en una sola sección con conteo (manual: medir minutos)
- [ ] SC-009 la entrega contiene exactamente las seis secciones con los vigentes
- [ ] SC-010 huellas de los archivos previos de `03_hallazgos/` sin cambios
- [ ] SC-011 función sin material = «no consta» con motivo en el 100 % de los casos
- [ ] SC-012 recorrido de un tercero hasta la evidencia (manual)
- [ ] SC-013 firmado + cita cambiada = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Medir SC-008 y registrar los minutos en Notes
- [ ] Recorrido SC-012 de un tercero y registro del resultado en Notes
