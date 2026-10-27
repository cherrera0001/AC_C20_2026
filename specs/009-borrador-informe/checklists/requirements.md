# Checklist de requisitos: S09 — El borrador

Generado desde `specs/009-borrador-informe/spec.md`. No es la lista de verificación del código:
es la del producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S08; sin ella, código 2 y nada escrito
- [ ] FR-002 el producto cita la huella de la entrega y el estado de firma de S01–S08
- [ ] FR-003 secciones completas: encabezado, resumen, desarrollo, acciones, vacíos, anexo de trazabilidad
- [ ] FR-004 cada sección deriva de su entrega y cita su huella; nada de material que no conste en S01–S08
- [ ] FR-005 secciones sin material conservadas con «no consta» y motivo; nunca omitidas ni favorables
- [ ] FR-006 cero estados de cumplimiento; acciones sin responsables ni fechas inventados
- [ ] FR-007 corrección de secciones con autor, fecha, valores y motivo; contradicción con su origen rechazada con la huella que la decide; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y secciones completas; cualquier escritura posterior la anula
- [ ] FR-009 verificación independiente: huellas del producto, de S08, de las entregas intermedias y de cada evidencia del anexo; «origen alterado» por sección y enlace
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `04_informe/`; los previos quedan intactos
- [ ] FR-012 informe legible `borrador-informe-cierre.md` con el mismo contenido del JSON, sin extractos crudos
- [ ] FR-013 entrega a S10: borrador completo con huellas de S01–S08, estados de firma y conteos verificados
- [ ] FR-014 frases cambiadas: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen frases inmutables (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 R riesgos tratados en el desarrollo y V vacíos declarados, con todas las secciones de FR-003
- [ ] SC-002 100 % de las secciones citan la huella de su origen; estados de firma declarados
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-004 alteración de un byte del JSON o de una evidencia del anexo detectada
- [ ] SC-005 100 % de las secciones sin material conservan su «no consta» con motivo
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 huellas de los archivos previos de `04_informe/` sin cambios
- [ ] SC-009 la entrega a S10 contiene el borrador completo sin inconsistencias abiertas
- [ ] SC-010 contradicción con el origen rechazada en el 100 % de los casos, con la huella que la decide
- [ ] SC-011 el anexo verifica: cada huella citada corresponde a sus bytes; enlace roto con referencia exacta
- [ ] SC-012 firmado + frases cambiadas = código 4 sin escritura

## Humanas (las marca el auditor, no el agente)

- [ ] Registrar en Notes la revisión del borrador contra las entregas de origen (muestreo de secciones)
