# Checklist de requisitos: S07 — El encargo

Generado desde `specs/007-encargo/spec.md`. No es la lista de verificación del código: es la del
producto. Criterio de aceptación y verificación por requisito.

## Funcionales

- [ ] FR-001 abrir exige la entrega de S06 y la cadena S01–S05; si falta alguna, código 2 y nada escrito
- [ ] FR-002 el encargo cita las huellas de todas las entregas y declara cuáles están firmadas
- [ ] FR-003 pasos repetibles de S01–S06, cada uno con entradas, salida esperada y huella de su entrega de origen
- [ ] FR-004 vacíos heredados escritos como condiciones con motivo; nada rellenado ni presentado como verificado
- [ ] FR-005 cero comandos, direcciones de red, puertos, credenciales y procedimientos de explotación; filtro igual que S02
- [ ] FR-006 cero estados de cumplimiento; el encargo no es una evaluación hecha
- [ ] FR-007 sin firma de aprobación; autoría registrada; huella de integridad al guardar; correcciones con autor, fecha, valores y motivo; nada se borra
- [ ] FR-008 verificación independiente: huella de integridad y de cada entrega citada; «origen alterado» por paso
- [ ] FR-009 determinismo byte a byte con los mismos insumos
- [ ] FR-010 solo archivos nuevos en `01_plan/`; los previos quedan intactos; legible por herramienta ajena y tercero
- [ ] FR-011 ficha legible por paso, sin extractos de evidencia
- [ ] FR-012 entrega a S08: pasos, condiciones, exclusiones con motivo, huellas y estados de firma
- [ ] FR-013 entrega de origen cambiada: `abrir` señala y no escribe hasta la decisión del auditor
- [ ] FR-014 el encargo no abre la compuerta, no transporta la autorización ni exime de verificarla
- [ ] FR-015 la entrega declara pasos repetibles y condicionados, con conteos

## De éxito (automáticas salvo indicación)

- [ ] SC-001 cobertura del 100 % de los dominios del alcance y de los sprints S01–S06, cada paso con huella de origen
- [ ] SC-002 búsqueda limpia: cero cumplimientos, redes, comandos, puertos, credenciales
- [ ] SC-003 alteración de un byte del JSON o de cualquier ficha detectada
- [ ] SC-004 100 % de correcciones, altas a mano y exclusiones con autor, fecha y motivo
- [ ] SC-005 dos aperturas, bytes idénticos
- [ ] SC-006 repetición del trabajo por una herramienta ajena sin ayuda humana (manual)
- [ ] SC-007 100 % de los vacíos heredados como condiciones con motivo; conteo coincide con S03
- [ ] SC-008 huellas de los archivos previos de `01_plan/` sin cambios
- [ ] SC-009 con una entrega de origen cambiada, `abrir` informa y no escribe
- [ ] SC-010 el resumen declara repetibles y condicionados, y el conteo coincide con las condiciones
- [ ] SC-011 la corrida que repite verifica la compuerta por sí misma (manual)

## Humanas (las marca el auditor, no el agente)

- [ ] Ejecutar SC-006 con una herramienta ajena y registrar el resultado en Notes
- [ ] Verificar SC-011 en el checklist humano de la corrida que repite
