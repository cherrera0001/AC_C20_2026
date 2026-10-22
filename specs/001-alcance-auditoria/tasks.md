---

description: "Lista de tareas de S01 — El alcance"
---

# Tasks: S01 — El alcance

**Input**: documentos de diseño de `specs/001-alcance-auditoria/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: se piden. La instrucción del dueño exige una forma de verificar cada criterio de aceptación
y las pruebas de SC-001 a SC-008. Las pruebas usan insumos **sintéticos, rotulados como tales**
(principio III); su resultado demuestra la herramienta, no audita el objetivo.

**Organization**: por historia (US1 a US4), en orden de dependencia. Ninguna tarea toca la red ni lee
`.env`. Ninguna tarea escribe direcciones de red, puertos, comandos contra el objetivo ni credenciales.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: historia a la que pertenece (US1, US2, US3, US4)

## Path Conventions

- Código: `platform/c4a/` · Pruebas: `platform/tests/` · Producto: `scope/` · Las pruebas se corren
  desde `platform/` con `python -m unittest discover -s tests`.

---

## Phase 1: Setup

**Purpose**: línea base y preparación de insumos.

- [X] T001 Correr la suite existente desde `platform/` y registrar la línea base (24 pruebas en verde el 2026-10-21) en `specs/001-alcance-auditoria/tasks.md` → sección Notes; si algo falla, detenerse y reportar
- [X] T002 Completar `scope/autorizacion.md` **solo** con datos que ya constan en el repositorio (decisión 7 del dueño, 2026-10-21): organización auditada según `docs/PROMPT_SPEC_KIT.md`, activo incluido por tipo y rol según `scope/alcance.md` §4, exclusiones según `scope/alcance.md` §5, y una nota de la decisión con fecha. Firmante, facultad, origen del auditor, ventana, contacto de emergencia y firma quedan «por completar»; el encabezado sigue en «NO FIRMADA — COMPUERTA CERRADA»

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: base común de las cuatro historias. Ninguna historia empieza antes.

- [X] T003 Crear `platform/c4a/alcance.py` con: vocabulario `TIPOS = ("activo","parte","marco","obligacion","dominio","exclusion","regla","compuerta")`, `DECISIONES = ("incluido","excluido","pendiente de confirmar")`, `APROBACION = ("borrador","revisado")` (más «firmado» derivado), rutas `scope/alcance_s01.json`, `scope/alcance_s01.md` y `scope/alcance_s01.firma.json`, y el constructor de fila con todos los campos de `data-model.md` (id = `short_id("A", tipo, clave)`, patrón `^A-[0-9a-f]{10}$`)
- [X] T004 En `platform/c4a/alcance.py`, serialización determinista del contenido canónico (`sort_keys`, sangría 2, UTF-8, `ensure_ascii=False`, salto de línea final, sin hora de generación) y lectura (`cargar`) (FR-018, research D3)
- [X] T005 En `platform/c4a/alcance.py`, filtro de direcciones de red: todo valor tomado de un insumo que contenga una dirección IPv4 o un rango se reemplaza por la remisión a `scope/autorizacion.md` (FR-004, research D9)
- [X] T006 En `platform/c4a/alcance.py`, lector de markdown dirigido: secciones `## N. Título` con su texto y su huella SHA-256, tablas `| Campo | Valor |`, listas con viñeta y numeradas; detección de valores «por completar» (`_(…)_`, «completar») (research D5)
- [X] T007 [P] Crear `platform/tests/alcance_fixtures.py` con un constructor de repositorio temporal que escribe un `scope/alcance.md` y un `scope/autorizacion.md` **sintéticos rotulados** («FIXTURE SINTÉTICO — no es el ejercicio»), con variantes: completo, sin exclusiones de activos, sin documento de alcance, dos activos, ventana vencida, autorización firmada

**Checkpoint**: base lista; las historias pueden empezar.

---

## Phase 3: User Story 1 - Proponer el alcance con insumos incompletos (Priority: P1) 🎯 MVP

**Goal**: el auditor obtiene un borrador con todo lo que consta, con su fuente, y cada vacío como fila
pendiente, sin valores inventados.

**Independent Test**: con un documento de alcance sintético con vacíos conocidos, el borrador tiene
exactamente esas filas pendientes y ningún valor ausente de los insumos.

### Tests for User Story 1

- [X] T008 [P] [US1] Escribir `platform/tests/test_alcance_us1.py`: US1 escenarios 1 a 4; SC-001 (N vacíos conocidos → N pendientes, cero valores ajenos a los insumos); SC-002 (100 % de filas con fuente o «sin fuente» y con estado de aprobación); SC-003 parte automática (una sola sección «Pendientes» en la vista y su conteo igual a las filas pendientes, FR-019); SC-005 (cero direcciones de red, puertos, comandos y credenciales en `alcance_s01.json` y `alcance_s01.md`); SC-010/FR-015 (ninguna fila ni campo contiene `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`); SC-008 parte automática (cada fuente citada existe como archivo y sección); FR-009 (huellas de los dos insumos iguales antes y después); FR-017 (solo se crean archivos `scope/alcance_s01.*`)

### Implementation for User Story 1

- [X] T009 [US1] En `platform/c4a/alcance.py`, derivar la fila `activo` desde `scope/alcance.md` §4 y contrastarla con `scope/autorizacion.md` §2: un único activo nombrado por tipo y rol; cero o más de uno → «pendiente de confirmar» con la observación «el ejercicio admite un solo activo» (FR-003, US1 escenarios 3 y 4)
- [X] T010 [US1] En `platform/c4a/alcance.py`, derivar filas `marco`: ISO/IEC 27001:2022 (versión declarada, «implementado parcialmente», cobertura = controles del Anexo A presentes en `platform/c4a/knowledge/controls_iso27001.json`); NIST CSF 2.0 y CIS Controls v8.1 desde la constitución, «mencionado», decisión «pendiente de confirmar» si no están declarados en el alcance; marco sin versión → versión «pendiente de confirmar»; versión distinta de la de referencia → se conserva y se anota la diferencia (FR-005, research D7, Edge Cases)
- [X] T011 [US1] En `platform/c4a/alcance.py`, derivar filas `obligacion` desde `scope/alcance.md` §3 (Ley 21.663, Ley 21.719, Ley 21.459) con `marca_legal = "VALIDAR"` si falta fuente oficial, fecha de consulta, artículo o fundamento (FR-006, principio IV); el estado anotado se guarda como `antecedente` con su fecha, no como vigencia; la aplicabilidad de la Ley 21.663 se anota dependiente de la clasificación OIV (§9) (FR-006, research D8)
- [X] T012 [US1] En `platform/c4a/alcance.py`, derivar filas `dominio` (§4, técnicos y de control), `exclusion` (§5) y `regla` (§6): sin motivo en el mismo ítem → decisión «pendiente de confirmar» con `declarado` = lo que dice el insumo; dominios que requieren políticas, personas o procesos llevan la observación «no se acredita con una prueba técnica»; el requisito de almacenamiento cifrado queda «pendiente de confirmar» con la observación «tener huellas no equivale a cifrado»; el detalle de red se representa con una fila `regla` que remite a `scope/autorizacion.md` (FR-007, research D6, Edge Cases)
- [X] T013 [US1] En `platform/c4a/alcance.py`, derivar desde `scope/autorizacion.md` la fila `parte` (organización auditada) y las filas `compuerta` (firma según el encabezado `ESTADO:` y la sección de firma; completitud con la lista `campos_faltantes`; ventana con `inicio` y `fin`), sin copiar valores de red; un insumo inexistente se informa en `avisos` y deja sus filas en «pendiente de confirmar» (FR-002, FR-008, US1 escenario 2)
- [X] T014 [US1] En `platform/c4a/alcance.py`, `proponer(raiz)`: registrar `insumos` (archivo, existe, sha256), ordenar filas, escribir `scope/alcance_s01.json` y la vista `scope/alcance_s01.md` (tabla por tipo con fuente y estado de aprobación, sección única «Pendientes (N)» con las filas «pendiente de confirmar» y «VALIDAR», huella del JSON guardado leída del archivo persistido) (FR-001, FR-010, FR-017, FR-019)
- [X] T015 [US1] En `platform/c4a/cli.py`, agregar el subcomando `alcance` con `proponer [--raiz] [--fecha-referencia]` según `specs/001-alcance-auditoria/contracts/cli-alcance.md`

**Checkpoint**: US1 se prueba sola; MVP.

---

## Phase 4: User Story 2 - El auditor corrige y firma la propuesta (Priority: P2)

**Goal**: cada corrección queda registrada; solo el auditor firma; cualquier cambio anula la firma.

**Independent Test**: sobre un borrador sintético, una corrección y una firma producen el historial y
los estados esperados; la alteración de un byte se detecta.

### Tests for User Story 2

- [X] T016 [P] [US2] Escribir `platform/tests/test_alcance_us2.py`: US2 escenarios 1 a 5; corrección sin motivo rechazada sin modificar el archivo; firmar desde «borrador» rechazado; SC-006 (alterar un byte de `alcance_s01.json` → `verificar` lo detecta, en cada posición probada); SC-007 (ningún camino llega a «firmado» sin `firmar`; 100 % de correcciones con autor, fecha y motivo); SC-009/FR-018 (dos `proponer` con los mismos insumos y correcciones → bytes idénticos); firmar sin nombre rechazado; FR-013 (insumo cambiado → fila corregida conserva el valor y marca `insumo_cambio`; alcance firmado con insumos cambiados → aviso, código 4, sin escribir)

### Implementation for User Story 2

- [X] T017 [US2] En `platform/c4a/alcance.py`, `corregir(raiz, fila, campo, valor, motivo, autor, fecha=None)`: campos `decision|valor|motivo|version`; `motivo` y `autor` obligatorios y no vacíos; evento `correccion` con anterior y nuevo; fila y alcance → «revisado»; si existía firma, se elimina `alcance_s01.firma.json` y se agrega el evento `firma_anulada` (FR-011, FR-012)
- [X] T018 [US2] En `platform/c4a/alcance.py`, `revisar(raiz, autor, motivo, fecha=None)`: evento `revision`, alcance → «revisado», sin cambiar filas
- [X] T019 [US2] En `platform/c4a/alcance.py`, `firmar(raiz, firmante, fecha=None)`: exige «revisado»; escribe `alcance_s01.firma.json` con `archivo`, `sha256` = `util.sha256_file` del JSON ya persistido, `firmante`, `fecha`, `pendientes_al_firmar` y la nota «Firmar el alcance no abre la compuerta de autorización»; `verificar(raiz)` y `estado_efectivo(raiz)` recalculan la huella sin regenerar (FR-012, FR-014, principio III)
- [X] T020 [US2] En `platform/c4a/alcance.py`, al `proponer` sobre un alcance existente: reaplicar las correcciones del historial; si la `huella_fuente` de una fila corregida cambió, conservar la corrección y marcar `insumo_cambio`; si el alcance está firmado y algún insumo cambió, avisar y no escribir (código 4) (FR-013, FR-018, Edge Cases)
- [X] T021 [US2] En `platform/c4a/cli.py`, subcomandos `alcance corregir`, `alcance revisar`, `alcance firmar` y `alcance verificar`, con los códigos de salida de `specs/001-alcance-auditoria/contracts/cli-alcance.md`

**Checkpoint**: US1 y US2 funcionan juntas.

---

## Phase 5: User Story 3 - Un dato no consta y la fila se conserva (Priority: P3)

**Goal**: la compuerta se informa cerrada con su motivo; nada la abre; la autorización no se toca.

**Independent Test**: con autorizaciones sintéticas sin ventana, no firmadas o vencidas, la compuerta
es «cerrada» con el motivo correcto y el documento no cambia.

### Tests for User Story 3

- [X] T022 [P] [US3] Escribir `platform/tests/test_alcance_us3.py`: US3 escenarios 1 a 4; SC-004 (cada combinación no favorable de firma, completitud y ventana → «cerrada» con su motivo; ninguna combinación es abierta salvo la totalmente favorable de un fixture sintético); fecha ilegible tratada como «no informada»; la huella de `scope/autorizacion.md` no cambia

### Implementation for User Story 3

- [X] T023 [US3] En `platform/c4a/alcance.py`, `evaluar_compuerta(raiz, fecha_referencia)`: atributos `firma` (`firmada|no firmada`), `completitud` (`completa|incompleta`), `ventana` (`vigente|vencida|no informada`), `resultado` (`abierta|cerrada`) y `motivos`; solo lectura; se muestra en la vista `scope/alcance_s01.md` y no entra en el contenido firmado (FR-008, FR-009, research D4)
- [X] T024 [US3] En `platform/c4a/cli.py`, subcomando `alcance compuerta [--fecha-referencia]`

**Checkpoint**: US1 a US3 funcionan.

---

## Phase 6: User Story 4 - Entregar el alcance a S02 (Priority: P3)

**Goal**: S02 pregunta si algo está dentro, fuera o pendiente, con la fila que lo decide.

**Independent Test**: con un alcance sintético con filas dentro, fuera y pendientes, cada consulta
responde lo esperado y cita la fila.

### Tests for User Story 4

- [X] T025 [P] [US4] Escribir `platform/tests/test_alcance_us4.py`: US4 escenarios 1 a 4; un activo distinto del declarado → «fuera» y `evidencia_admisible` falso; un dominio pendiente → «pendiente», nunca «dentro»; un alcance en borrador → `firmado: false` explícito

### Implementation for User Story 4

- [X] T026 [US4] En `platform/c4a/alcance.py`, `consultar(raiz, tipo, valor)` (respuesta `dentro|fuera|pendiente`, fila con id y fuente, motivo, `firmado`) y `evidencia_admisible(raiz, activo)`; lo que no figura en el alcance responde «fuera» (FR-016)
- [X] T027 [US4] En `platform/c4a/cli.py`, subcomando `alcance consultar --tipo --valor`

**Checkpoint**: las cuatro historias funcionan.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T028 Correr la suite completa desde `platform/` (existente y nueva); si una prueba que antes pasaba falla, detenerse y reportar
- [X] T029 Generar el producto real con `proponer` sobre la raíz del repositorio: `scope/alcance_s01.json` y `scope/alcance_s01.md`; comprobar que no contienen direcciones de red, puertos, comandos ni credenciales (SC-005) y que los dos insumos no cambiaron (FR-009)
- [X] T030 [P] Documentar el subcomando `alcance` en `platform/README.md` (uso, archivos que produce, que firmar no abre la compuerta)
- [X] T031 [P] Registrar en `specs/001-alcance-auditoria/quickstart.md` el resultado de la validación de punta a punta (pasos 1 a 5)
- [ ] T032 Acción humana: el auditor mide SC-003 (minutos para identificar los pendientes en `scope/alcance_s01.md`) y SC-008 (recorre filas hasta su sección de origen) y lo registra en `specs/001-alcance-auditoria/checklists/alcance.md` → Notes
- [ ] T033 Acción humana: el auditor corrige las filas pendientes que pueda resolver y firma el alcance con `alcance firmar` (FR-012). La herramienta no lo hace por él

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (T001–T002) → Foundational (T003–T007) → US1 (T008–T015) → US2 (T016–T021) → US3 (T022–T024) → US4 (T025–T027) → Polish (T028–T033).
- US3 depende solo de la fase 2 y de T013; puede ir en paralelo con US2.
- US4 depende de US1 (filas) y de US2 (`estado_efectivo`).
- T032 y T033 son humanas y van al final; T033 depende de T029.

### Within Each User Story

- La prueba de la historia se escribe primero y falla; luego la implementación; luego el subcomando.
- Todas las tareas de implementación tocan `platform/c4a/alcance.py`, así que dentro de una historia van en serie.

### Parallel Opportunities

- T007 en paralelo con T003–T006 (otro archivo).
- T008, T016, T022 y T025 en paralelo entre sí (archivos de prueba distintos), una vez lista la fase 2.
- T030 y T031 en paralelo.

## Parallel Example: pruebas

```text
T008 platform/tests/test_alcance_us1.py
T016 platform/tests/test_alcance_us2.py
T022 platform/tests/test_alcance_us3.py
T025 platform/tests/test_alcance_us4.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

Fases 1 y 2, luego US1. Validar con `test_alcance_us1.py` y con el borrador real (T029 adelantado).

### Incremental Delivery

US1 (borrador) → US2 (corrección y firma) → US3 (compuerta) → US4 (consulta para S02). Cada historia
suma sin romper la anterior; la suite completa se corre al cerrar cada una.

## Cobertura

| Requisito | Tareas | Verificación |
|---|---|---|
| FR-001 | T014 | T008, T029 |
| FR-002 | T013 | T008 (US1 esc. 2) |
| FR-003 | T009 | T008 (US1 esc. 3 y 4) |
| FR-004 | T005 | T008 (SC-005), T029 |
| FR-005 | T010 | T008 |
| FR-006 | T011 | T008 |
| FR-007 | T012 | T008 |
| FR-008 | T013, T023 | T022 |
| FR-009 | T023 | T008, T022, T029 |
| FR-010 | T003, T014 | T008 (SC-002) |
| FR-011 | T017 | T016 |
| FR-012 | T017, T019 | T016 |
| FR-013 | T020 | T016 |
| FR-014 | T019 | T016 (SC-006) |
| FR-015 | T003, T014 | T008 (SC-010) |
| FR-016 | T026 | T025 |
| FR-017 | T014 | T008 |
| FR-018 | T004, T020 | T016 (SC-009) |
| FR-019 | T014 | T008 (SC-003) |
| SC-001 | T009–T013 | T008 |
| SC-002 | T014 | T008 |
| SC-003 | T014 | T008 (automática), T032 (manual) |
| SC-004 | T023 | T022 |
| SC-005 | T005 | T008, T029 |
| SC-006 | T019 | T016 |
| SC-007 | T017, T019 | T016 |
| SC-008 | T014 (fuente por fila) | T008 (fuentes existen), T032 (manual) |
| SC-009 | T004, T020 | T016 |
| SC-010 | T003, T014 | T008 |

## Reconciliación con el Project #7 (solo lectura, 2026-10-21)

Leído con `gh issue list` y `gh project item-list 7`. No hay ninguna issue de épica, historia ni tarea
del ciclo S01–S10. Las issues #1 a #40 son el backlog del motor de cuatro fases y de la plataforma.
**Acción propuesta, pendiente de la aprobación del dueño. No se escribió nada en GitHub.**

| Issue existente | Relación con S01 | Acción propuesta |
|---|---|---|
| — | Épica S01 | Crear `[ÉPICA] S01 — El alcance` (04-epica.yml) |
| — | US1–US4 | Crear 4 historias (01-historia-usuario.yml), hijas de la épica S01 |
| — | T001–T033 | Crear tareas (02-tarea.yml) hijas de su historia; las de fase 1, 2 y 7 cuelgan de la épica |
| #1 Épica de cuatro fases | S01 es la fase Planificar del mismo flujo | Sin cambios; enlazar la épica S01 como «relacionada» |
| #19 HU Planificación y compuerta | Consume el alcance de S01; no lo produce | Sin cambios; anotar «depende de la épica S01» |
| #20 Tarea `01_plan/plan.md` | Fase 1, posterior al alcance | Sin cambios; no se duplica |
| #21 Tarea compuerta de fases | Usará `evaluar_compuerta` de T023 | Sin cambios; anotar la relación con T023 |
| #34 HU Completar la autorización | T002 completa solo lo que consta; la firma sigue en #34 | Sin cambios; enlazar T002 como «relacionada» |
| #36 Tarea compuerta verificable | T023 cubre firma, completitud y ventana; rango y origen siguen en #36 | Sin cambios; anotar el solapamiento parcial con T023 |
| #33 Revisión por segundo par | Fuera de S01 (aclaración Q3) | Sin cambios |
| #2–#18, #22–#32, #35, #37–#40 | Otras fases o plataforma | Sin cambios |

Duplicados detectados: ninguno. Huérfanas: ninguna dentro de S01. Desorden: #19, #20 y #21 (fase
Planificar) se abrieron antes de que existiera el producto que consumen (el alcance); se ordenan
detrás de la épica S01 sin editarlas.

**Tablero creado (2026-10-21, aprobación expresa del dueño en la compuerta H)**: por decisión del
dueño, S01 se integró bajo la épica existente #1 y las tareas viajan como checklist dentro de cada
historia (sin issues de tarea sueltas). Épica S01: #41 (sub-issue de #1). Historias: US1 #42, US2 #43,
US3 #44, US4 #45 (sub-issues de #41). Campos: Status «In Progress», Fase C4A «Planificar», Sprint
«S01», prioridad y talla según la tabla anterior. Ninguna issue existente se editó.

## Notes

- Línea base (T001, 2026-10-21): `python -m unittest discover -s tests` → 24 pruebas, OK.
- Tras implementar (T028, 2026-10-21): 72 pruebas (24 existentes + 48 de S01), OK. Ninguna prueba
  que pasaba antes falló.
- T029 (2026-10-21): `scope/alcance_s01.json` y `scope/alcance_s01.md` generados: 31 filas, 22
  pendientes, estado «borrador», compuerta «cerrada». Búsqueda de direcciones de red, puertos,
  comandos, credenciales y estados de cumplimiento: cero coincidencias. Huellas de
  `scope/alcance.md` y `scope/autorizacion.md` iguales antes y después.
- Las tareas humanas (T032, T033) no las marca el agente.
- Commit después de cada historia, solo con aprobación del dueño.

---

## Phase 8: Convergence

- [X] T034 Agregar `platform/tests/test_alcance_cli.py` que invoque `c4a.cli.main` sobre un fixture sintético y compruebe los códigos de salida 0, 1, 2, 3 y 4 per contracts/cli-alcance.md (partial)
- [X] T035 Filtrar con `limpiar` el autor de correcciones y revisiones y el nombre del firmante en `platform/c4a/alcance.py`, y probarlo en `platform/tests/test_alcance_us2.py` per FR-004 (partial)
- [X] T036 Agregar a `platform/tests/test_alcance_us1.py` el caso de un marco declarado con una versión distinta de la de referencia (se conserva y se anota la diferencia) per Spec Edge Cases / T010 (partial)
- [X] T037 Documentar en `specs/001-alcance-auditoria/data-model.md` el valor de ventana «no vigente (aún no comienza)» como extensión de FR-008, que cierra la compuerta, y probarlo en `platform/tests/test_alcance_us3.py` per FR-008 (unrequested)

Resultado de la fase 8 (2026-10-21): 76 pruebas OK (24 existentes + 52 de S01).

---

## Phase 9: Convergence

- [X] T038 CRITICAL: exigir y registrar la justificación de la firma (`--motivo` obligatorio en `alcance firmar`; campo `motivo` en `scope/alcance_s01.firma.json` y en la vista), corregir en origen `specs/001-alcance-auditoria/spec.md` FR-012, `contracts/cli-alcance.md` y `data-model.md`, y probarlo en `platform/tests/test_alcance_us2.py` y `platform/tests/test_alcance_cli.py` per Constitution I (partial)
