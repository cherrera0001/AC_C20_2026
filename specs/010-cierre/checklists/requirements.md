# Checklist de requisitos: S10 — El cierre

Generado desde `specs/010-cierre/spec.md`. No es la lista de verificación del código: es la del
producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S09; ausente = código 2; sin firmar = código 5; nada escrito en ambos
- [ ] FR-002 el producto cita la huella de la entrega y el estado de firma de la cadena S01–S08
- [ ] FR-003 mismas secciones del borrador firmado + tabla de recorrido + registro en blanco; nada de material que no conste en S01–S09
- [ ] FR-004 tabla con una entrada por afirmación: afirmación, sección, ficha, huella esperada y estado del enlace
- [ ] FR-005 huellas recalculadas antes del recorrido; byte alterado marcado; «no-verifica»/«ilegible» resuelto antes de firmar
- [ ] FR-006 cero estados de cumplimiento generados; conclusiones del auditor como su texto firmado, identificado como tal
- [ ] FR-007 corrección de redacción y agrupación con autor, fecha, valores y motivo; contradicción con el borrador rechazada; nada se borra
- [ ] FR-008 firma solo desde «revisado», con firmante, justificación y recorrido sin enlaces sin resolver; cualquier escritura posterior la anula; no publica nada
- [ ] FR-009 verificación independiente: huellas del producto, de S09, de cada enlace y de cada evidencia citada
- [ ] FR-010 determinismo byte a byte con los mismos insumos
- [ ] FR-011 solo archivos nuevos en `04_informe/`; los previos quedan intactos; legible por un tercero sin la herramienta
- [ ] FR-012 informe legible `informe-cierre.md` con la tabla de recorrido como anexo, sin extractos crudos
- [ ] FR-013 registro del recorrido listo para el checklist humano: conteos, identidad, fecha y observaciones; la herramienta no simula el recorrido
- [ ] FR-014 borrador cambiado: `abrir` señala; firmado-no-escribe (código 4)
- [ ] FR-015 acciones del auditor exigen borrador inmutable (código 4)
- [ ] FR-016 textos libres filtrados (cumplimiento, puertos, comandos, credenciales; red remitida; datos personales enmascarados)

## De éxito (automáticas salvo indicación)

- [ ] SC-001 100 % de las secciones del borrador y de las afirmaciones cubiertas por la tabla
- [ ] SC-002 100 % de los enlaces llegan a ficha legible y huella; el tercero recorre una muestra sin ayuda
- [ ] SC-003 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales y datos personales sin enmascarar
- [ ] SC-004 alteración de un byte del JSON, de la tabla o de una evidencia citada detectada
- [ ] SC-005 100 % de «no-verifica»/«ilegible» resueltos antes de la firma
- [ ] SC-006 nada firma solo; 100 % de cambios con autor, fecha y motivo
- [ ] SC-007 dos aperturas, bytes idénticos
- [ ] SC-008 huellas de los archivos previos de `04_informe/` sin cambios
- [ ] SC-009 ausente = código 2; sin firmar = código 5; ninguno escribe
- [ ] SC-010 registro del recorrido completo: conteos por estado, identidad y fecha; discrepancia del tercero anotada
- [ ] SC-011 firmado + borrador cambiado = código 4 sin escritura
- [ ] SC-012 el tercero declara entender el informe sin haber estado en la sala (manual)

## Humanas (las marca el auditor, no el agente)

- [ ] Recorrido SC-002/SC-010/SC-012: tercero ajeno recorre el informe hasta la evidencia y registra conteos, identidad y fecha en Notes
- [ ] Confirmar que la publicación o entrega al cliente quedó en decisión del dueño, no ejecutada por la herramienta
