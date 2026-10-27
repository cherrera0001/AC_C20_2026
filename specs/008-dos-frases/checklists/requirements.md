# Checklist de requisitos: S08 — Las dos frases

Generado desde `specs/008-dos-frases/spec.md`. No es la lista de verificación del código: es la
del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S07; sin ella, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y el estado de firma de las entregas del encargo
- [ ] FR-003 exactamente dos frases; mismos datos, mismos riesgos, mismos vacíos con la misma causa y conteos consistentes
- [ ] FR-004 gerencia en lenguaje de negocio sin jerga ni identificadores de controles; técnica remite a fichas y huellas sin copiar extractos
- [ ] FR-005 vacíos declarados en ambas frases con la misma causa; nunca presentados como favorables
- [ ] FR-006 cero estados de cumplimiento; «sin riesgos enunciados» ≠ «sin hallazgos»
- [ ] FR-007 corrección de redacción con autor, fecha, valores y motivo; inconsistencia entre frases rechazada con detalle; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y ambas frases completas; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente: huella del producto, de la entrega y consistencia entre frases por dimensión
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `04_informe/`; los previos quedan intactos
- [ ] FR-012 ficha legible por frase (`frase-gerencia.md`, `frase-tecnica.md`)
- [ ] FR-013 entrega a S09: ambas frases con conteos verificados, huella y estado de firma
- [ ] FR-014 encargo cambiado: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen encargo inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 R riesgos y V vacíos: ambas frases tratan los mismos temas y sus conteos coinciden
- [ ] SC-002 el producto cita la huella de S07 y el estado de firma de las entregas del encargo
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales; gerencia sin identificadores de controles
- [ ] SC-004 alteración de un byte del JSON detectada
- [ ] SC-005 conteos o causas que difieren detectados en el 100 % de los casos, con dimensión informada
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 100 % de los vacíos declarados en ambas frases con la misma causa
- [ ] SC-009 la entrega a S09 contiene ambas frases sin inconsistencias abiertas
- [ ] SC-010 huellas de los archivos previos de `04_informe/` sin cambios
- [ ] SC-011 lectura de cada audiencia sin ayuda y sin haber estado en la sala (manual)
- [ ] SC-012 firmado + encargo cambiado = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Lectura SC-011: un lector de gerencia y un lector técnico, cada uno con su frase, y registro del resultado en Notes
