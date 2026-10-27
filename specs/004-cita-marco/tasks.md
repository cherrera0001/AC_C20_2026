---

description: "Lista de tareas de S04 — La cita"
---

# Tasks: S04 — La cita

**Input**: documentos de diseño de `specs/004-cita-marco/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: se piden. La spec define una prueba independiente por historia y los criterios SC-001 a SC-013.
Las pruebas usan insumos **sintéticos, rotulados como tales** (principio III); demuestran la herramienta, no
auditan el objetivo.

**Organization**: por historia (US1 a US4), en orden de prioridad.

**Desviación declarada**: S04 avanza mientras S03 no converge (plan, sección «Desviación de compuerta
declarada»). Las tareas dependen de la API pública de `platform/c4a/enunciado.py` (`entregar`,
`estado_efectivo`), no de su implementación interna.

**Archivos de otra sesión**: no se modifican `platform/c4a/cita.py`, `platform/tests/test_cita.py`,
`platform/tests/cita_fixtures.py` ni ningún archivo de S03. Los archivos nuevos de esta épica llevan nombres
propios (`test_cita_us*.py`, `cita_s04_fixtures.py`) para no chocar con ellos.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: historia a la que pertenece (US1, US2, US3, US4)

## Path Conventions

- Código: `platform/c4a/` · Pruebas: `platform/tests/` · Producto: `03_hallazgos/citas_s04.*`,
  `03_hallazgos/cita-<id>.md`
- Las pruebas se corren desde `platform/` con `python -m unittest discover -s tests -p "test_*.py"`.

---

## Phase 1: Setup

**Purpose**: decisiones previas y fines de línea.

- [X] T001 Correr la suite completa desde `platform/` y registrar la línea base en `specs/004-cita-marco/tasks.md` → Notes (número de pruebas y resultado). Si algo falla, detenerse y reportar
- [X] T002 Reconciliar `platform/c4a/cita.py` existente (escrito por otra sesión, 30 KB, sin plan ni tareas). Leerlo y compararlo con FR-001 a FR-016 y con `contracts/cli-cita.md`. Decidir **adoptar** solo si cubre al menos FR-001, FR-003, FR-004, FR-005 y FR-014, y su API coincide con `data-model.md`; decidir **reescribir** en otro caso. Registrar la decisión y su motivo en Notes. No modificar `cita.py` en este paso
- [X] T003 [P] Extender `.gitattributes` con `03_hallazgos/citas_s04.* text eol=lf` y `03_hallazgos/cita-*.md text eol=lf`, con un comentario que cite el principio III, como la regla de `scope/**` y de `02_evidencia/registro_s02.*`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: base común de las cuatro historias. Ninguna historia empieza antes.

- [ ] T004 Crear o ajustar `platform/c4a/cita.py` según la decisión de T002, con `CitaError(mensaje, codigo=1)`; constantes `PRODUCTO = "S04 — La cita"`, `VERSION_ESQUEMA = "1"`, `MARCOS = ("ISO-27001:2022", "NIST-CSF:2.0", "CIS-v8.1", "aporte del auditor")`, `ESTADOS_IDENTIFICADOR = ("confirmado", "pendiente-confirmar")`, `APROBACION = ("borrador", "revisado")`, `CAMPOS_CORREGIBLES = ("marco", "control", "fundamento", "motivo")`, `MARCAS = ("descartado", "riesgo no vigente", "evidencia alterada")`; rutas `03_hallazgos/citas_s04.json`, `.firma.json`, `.md` y `03_hallazgos/cita-<id>.md`; `ARCHIVO_ENTREGA = "03_hallazgos/enunciados_s03.json"` (data-model → Archivos)
- [ ] T005 En `platform/c4a/cita.py`, `cargar(raiz)` y `_guardar(raiz, contenido, evento)`: reutilizan `alcance.serializar` (claves ordenadas, sangría 2, UTF-8, salto final) y escritura binaria; el contenido canónico tiene exactamente las claves `producto`, `version_esquema`, `entrega`, `citas`, `vacios`, `estado_aprobacion`, `historial`, `avisos` de `contracts/citas_s04.schema.json` (`additionalProperties: false`). `_guardar` es el único punto de escritura de las acciones del auditor y anula la firma previa (`firma_anulada`)
- [ ] T006 En `platform/c4a/cita.py`, identificadores con `util.short_id`: cita `short_id("C", riesgo_id)` con patrón `^C-[0-9a-f]{10}$`; el id se fija en la primera apertura y no cambia al corregir (data-model → `citas[]`, research D3)
- [ ] T007 En `platform/c4a/cita.py`, `_contexto(raiz)`: exige la entrega de S03 (`03_hallazgos/enunciados_s03.json` y `enunciado.entregar(raiz)` disponibles). Si falta, `CitaError` código 2 sin escribir (FR-001). Calcula `entrega_sha256` sobre `alcance.serializar(entrega)` y registra `entrega.sha256` con la huella del JSON de S03
- [ ] T008 [P] Crear `platform/tests/cita_s04_fixtures.py`: entrega de S03 **sintética rotulada** («FIXTURE SINTÉTICO — no es el ejercicio»): R riesgos vigentes (al menos uno con dominio técnico y uno con dominio de políticas), V vacíos heredados, un riesgo descartado, un riesgo con evidencia alterada, un riesgo que ya no está en la entrega; expone `R_FIXTURE` y `V_FIXTURE`; usa `registro_fixtures` y `enunciado_fixtures` solo si su API pública lo permite, sin modificarlos
- [ ] T009 En `platform/c4a/cita.py`, `_derivar(riesgos, historial, catalogos)`: una cita por riesgo vigente de la entrega; aplica el historial en orden; no borra nada; ordena por riesgo (FR-003, FR-015)
- [ ] T010 En `platform/c4a/cita.py`, `vista(raiz)` y `escribir_vista(raiz)` para `03_hallazgos/citas_s04.md` y las fichas `cita-<id>.md`: en castellano; sin extractos de evidencia; sin estados de cumplimiento; cabecera con la huella de la entrega (FR-002, FR-011, FR-012, FR-016, principio VIII)

**Checkpoint**: base lista; las historias pueden empezar.

---

## Phase 3: User Story 1 - Abrir la cita sin enunciado (Priority: P1) 🎯 MVP

**Goal**: el auditor obtiene una cita por cada riesgo vigente de la entrega de S03, con la huella de esa
entrega, sin escribir nada si falta la entrega.

**Independent Test**: con una entrega con R riesgos vigentes y V vacíos heredados, el producto tiene
exactamente R citas, V vacíos y cita la huella de la entrega.

### Tests for User Story 1

- [ ] T011 [P] [US1] Escribir `platform/tests/test_cita_us1.py`: escenarios 1 a 4 de US1; SC-001 (R riesgos y V vacíos → R citas y V vacíos); FR-001 (sin entrega de S03 → código 2 y ningún archivo nuevo); FR-002 (el producto cita la huella de la entrega de S03 y `firmado` cuando corresponde); FR-003 (un riesgo descartado o con evidencia alterada no genera cita vigente); SC-007 (dos aperturas → bytes idénticos); SC-010 (solo se crean archivos nuevos en `03_hallazgos/`; huellas de `enunciados_s03.*` y de `README.md` y `matriz_cumplimiento.csv` iguales antes y después)

### Implementation for User Story 1

- [ ] T012 [US1] En `platform/c4a/cita.py`, `abrir(raiz, fecha=None)`: deriva las citas con T009, conserva el historial previo, escribe `citas_s04.json` y la vista con T010; `fecha` solo se usa en eventos del historial, nunca en la propuesta (`contracts/cli-cita.md`)
- [ ] T013 [US1] En `platform/c4a/cita.py`, avisos de `abrir`: riesgo duplicado en la entrega (se toma el primero y se avisa); entrega de S03 sobre un registro no firmado (aviso, no bloqueo)
- [ ] T014 [US1] En `platform/c4a/cli.py`, subcomando `cita` con la acción `abrir [--fecha] [--raiz]` según `contracts/cli-cita.md`; stdout y stderr con `errors="replace"` como en `registro`

**Checkpoint**: US1 se prueba sola; MVP.

---

## Phase 4: User Story 2 - La herramienta propone la correspondencia y el auditor corrige (Priority: P2)

**Goal**: la herramienta propone un marco, un identificador y un fundamento explicados; el auditor corrige,
añade correspondencias con motivo, descarta, restablece, revisa y firma; cualquier cambio anula la firma.

**Independent Test**: con una cita propuesta, corregir el identificador con motivo deja el cambio en el
historial, el identificador de la cita no cambia y nada llega a «firmado» sin la acción del auditor.

### Tests for User Story 2

- [ ] T015 [P] [US2] Escribir `platform/tests/test_cita_us2.py`: escenarios 1 a 5 de US2; SC-002 (100 % de citas con riesgo, huella y fundamento); SC-011 (fundamento no vacío en toda propuesta); FR-005 (identificador solo si consta en el catálogo; si no, `pendiente-confirmar`); FR-006 (ninguna propuesta contiene `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`); FR-007 (corregir marco, control, fundamento y motivo con autor, fecha y motivo; sin motivo o campo no corregible → código 1 y archivo sin cambios); FR-008 (firmar solo desde «revisado»; cualquier escritura posterior elimina la firma con `firma_anulada`); SC-006 (ningún camino llega a «firmado» sin `firmar`); SC-007 (mismas entradas y correcciones → bytes idénticos)

### Implementation for User Story 2

- [ ] T016 [US2] En `platform/c4a/cita.py`, `_proponer(riesgo, catalogos)` según `data-model.md` → «Propuesta (FR-005)»: candidatos por términos del dominio, criterio e impacto contra `terminos` de cada control del catálogo; elección por mayor número de términos, empate por orden del catálogo; sin candidato → `control: null`, `identificador.estado: "pendiente-confirmar"`, `fundamento` con el texto «ningún control del catálogo coincide con los términos del riesgo»
- [ ] T017 [US2] En `platform/c4a/cita.py`, `corregir(raiz, cita, campo, valor, motivo, autor, fecha=None)` con `campo` en `marco|control|fundamento|motivo`; valor de `marco` restringido a `MARCOS`; valor de `control` debe existir en el catálogo del marco, o el estado queda `pendiente-confirmar`; motivo y autor obligatorios, filtrados con `alcance.limpiar` y el filtro de textos de S02 (FR-016); la cita pasa a «revisado»
- [ ] T018 [US2] En `platform/c4a/cita.py`, `agregar(raiz, cita, marco, control, fundamento, motivo, autor, fecha=None)`: correspondencia adicional del auditor; si el marco está fuera de `MARCOS` se registra como `aporte del auditor` con `identificador.estado: "pendiente-confirmar"` y `fuente` declarada (spec, clarificaciones)
- [ ] T019 [US2] En `platform/c4a/cita.py`, `descartar(raiz, cita, motivo, autor, fecha=None)` y `restablecer(raiz, cita, motivo, autor, fecha=None)` (solo sobre una descartada): marcan con la marca `descartado`, no borran; motivo y autor obligatorios (FR-007)
- [ ] T020 [US2] En `platform/c4a/cita.py`, `revisar(raiz, autor, motivo, fecha=None)` y `firmar(raiz, firmante, motivo, fecha=None)`: `firmar` exige producto «revisado», firmante y justificación; rechaza con código 1 una cita vigente sin marco (spec US2 escenario 4); escribe `citas_s04.firma.json` con `archivo`, `sha256` (huella de los bytes ya guardados), `firmante`, `fecha`, `motivo`, `citas_al_firmar`, `pendientes_al_firmar` y la nota de `data-model.md` → Firma
- [ ] T021 [US2] En `platform/c4a/cli.py`, acciones `cita corregir`, `agregar`, `descartar`, `restablecer`, `revisar` y `firmar` con argumentos y códigos de salida 0, 1, 2, 3 y 4 de `contracts/cli-cita.md`

**Checkpoint**: US1 y US2 funcionan juntas.

---

## Phase 5: User Story 3 - Un identificador no consta y la fila se conserva (Priority: P3)

**Goal**: «no consta» nunca se lee como «cumple»: un identificador sin base verificable queda
`pendiente-confirmar`, con su fila conservada y la fuente que el auditor declare, si la aporta.

**Independent Test**: con riesgos cuyo control sugerido no tiene identificador verificable, cada cita queda
`pendiente-confirmar`, ninguno de los archivos contiene estados de cumplimiento y el resumen cuenta los pendientes.

### Tests for User Story 3

- [ ] T022 [P] [US3] Escribir `platform/tests/test_cita_us3.py`: escenarios 1 a 4 de US3; FR-005 (sin base → `pendiente-confirmar`, `control: null`); SC-003 (búsqueda sobre todos los archivos generados: cero `cumple`, `parcial`, `no-cumple`, `no-evaluado`, `no-aplica`); SC-008 (todos los pendientes en una sola sección con su conteo); un aporte de fuente declarada cambia el estado solo con `motivo` y `autor`; el resumen nunca dice «sin hallazgos» ni «cumple»

### Implementation for User Story 3

- [ ] T023 [US3] En `platform/c4a/cita.py`, el aporte de fuente declarada por el auditor se registra con `corregir` sobre `control` y `fuente`; el estado pasa a `confirmado` solo si el auditor aporta fuente y el control está en el catálogo; si no, sigue `pendiente-confirmar` (FR-005, principio IV)
- [ ] T024 [US3] En `platform/c4a/cita.py`, resumen de la vista: conteo «N citas pendientes de confirmar» siempre visible; texto fijo: «una correspondencia es una sugerencia explicada, no un dictamen de cumplimiento» (FR-006, principio II)

**Checkpoint**: US1 a US3 funcionan.

---

## Phase 6: User Story 4 - Verificar la consistencia con el enunciado y entregar a S05 (Priority: P3)

**Goal**: `verificar` recalcula el producto, la entrega de S03 y las evidencias; `entregar` da a S05 exactamente
las citas vigentes.

**Independent Test**: alterar un byte de una evidencia copiada o del JSON se detecta; un riesgo que sale de la
entrega deja su cita sin vigencia; la entrega a S05 contiene solo las vigentes.

### Tests for User Story 4

- [ ] T025 [P] [US4] Escribir `platform/tests/test_cita_us4.py`: escenarios 1 a 4 de US4; SC-004 (alterar un byte del JSON → `verificar` lo detecta, código 3); SC-005 (alterar un byte de una evidencia copiada → cita «evidencia alterada»); SC-009 (entrega a S05 = citas vigentes exactas); SC-013 (producto firmado y entrega de S03 cambiada → `abrir` rechaza con código 4 y no escribe); FR-013 (citas vigentes con estado del identificador y huellas; vacíos heredados; indicador de firma); FR-015 (las acciones del auditor exigen que la entrega no haya cambiado)

### Implementation for User Story 4

- [ ] T026 [US4] En `platform/c4a/cita.py`, `verificar(raiz)`: recalcula la huella del JSON contra la firma, la de la entrega de S03 contra `entrega.entrega_sha256`, y las evidencias citadas con `registro._evidencias_alteradas` (misma forma de datos: `id`, `tipo`, `ubicacion_original`, `copia`, `sha256_original`, `sha256_guardado`); informa `riesgos_no_vigentes` y `estado_informado` según `data-model.md` → Verificación
- [ ] T027 [US4] En `platform/c4a/cita.py`, `abrir` sobre entrega cambiada (FR-014): si la huella de la entrega difiere de la registrada, lo señala en `avisos`; si el producto está firmado, rechaza con `CitaError` código 4 sin escribir (SC-013)
- [ ] T028 [US4] En `platform/c4a/cita.py`, `_cargar_vigente(raiz)`: toda acción del auditor (corregir, agregar, descartar, restablecer, revisar, firmar) exige que la entrega de S03 no haya cambiado; si cambió, código 4 sin escribir (FR-015)
- [ ] T029 [US4] En `platform/c4a/cita.py`, `entregar(raiz) -> dict` para S05: citas vigentes (no descartadas, riesgo vigente, sin evidencia alterada) con `id`, `riesgo`, `marco`, `control`, `identificador`, `fundamento`, `evidencias` con huellas y `marcas`; vacíos heredados; `firmado` según `estado_efectivo` (FR-013)
- [ ] T030 [US4] En `platform/c4a/cita.py`, `estado_efectivo(raiz) -> str` (`borrador`, `revisado`, `firmado`) y `cargar(raiz)`, con la API pública de `contracts/cli-cita.md`
- [ ] T031 [US4] En `platform/c4a/cli.py`, acciones `cita verificar`, `cita entregar [--json]` y código 4 de `abrir`, según `contracts/cli-cita.md`

**Checkpoint**: las cuatro historias funcionan.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T032 [P] Escribir `platform/tests/test_cita_cli.py`: invoca `c4a.cli.main` sobre un fixture sintético y comprueba los códigos de salida 0, 1, 2, 3 y 4 de `contracts/cli-cita.md`
- [ ] T033 [P] Agregar a `platform/tests/test_cita_us1.py` la prueba SC-003 de búsqueda limpia sobre archivos generados con insumos que contienen direcciones de red de documentación, una línea con forma de comando y una con forma de credencial: cero direcciones, comandos, puertos, credenciales y estados de cumplimiento
- [ ] T034 Correr la suite completa desde `platform/` (existente y nueva); si una prueba que antes pasaba falla, detenerse y reportar
- [ ] T035 Generar el producto real con `cita abrir` sobre la raíz del repositorio: `03_hallazgos/citas_s04.json`, `.md` y fichas; comprobar SC-003 y SC-010; registrar en Notes el conteo de citas, de `pendiente-confirmar` y de marcos
- [ ] T036 [P] Documentar el subcomando `cita` en `platform/README.md` (uso, archivos que produce, que firmar no abre la compuerta, que una correspondencia es sugerencia y no dictamen)
- [ ] T037 [P] Registrar en `specs/004-cita-marco/quickstart.md` el resultado de la validación de punta a punta (pasos 1 a 6 con fixtures sintéticos; paso 7 con el producto real)
- [ ] T038 Acción humana: el auditor mide SC-008 (minutos para identificar todos los pendientes en `03_hallazgos/citas_s04.md`) y un tercero hace el recorrido de SC-012; ambos resultados se registran en `specs/004-cita-marco/checklists/` → Notes
- [ ] T039 Acción humana: el auditor corrige las correspondencias reales, aporta fuentes donde las tenga, revisa y firma la cita con `cita firmar --motivo` (FR-008). La herramienta no lo hace por él

---

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T010) → US1 (T011–T014) → US2 (T015–T021) → US3 (T022–T024) → US4 (T025–T031) → Polish (T032–T039).
- T002 bloquea T004: la decisión sobre `cita.py` precede a cualquier cambio.
- US3 depende de US2 (`corregir` sobre `control` y `fuente`); US4 depende de US2 (`_cargar_vigente`, `estado_efectivo`).
- T038 y T039 son humanas y van al final; T039 depende de T035.

### Within Each User Story

- La prueba de la historia se escribe primero y falla; luego la implementación; luego el subcomando.
- Todas las tareas de implementación tocan `platform/c4a/cita.py`, así que dentro de una historia van en serie.

### Parallel Opportunities

- T003 en paralelo con T001–T002.
- T008 en paralelo con T004–T007 (otro archivo).
- T011, T015, T022 y T025 en paralelo entre sí (archivos de prueba distintos), una vez lista la fase 2.
- T032, T033, T036 y T037 en paralelo.

## Implementation Strategy

### MVP First (User Story 1 Only)

Fases 1 y 2, luego US1. Validar con `test_cita_us1.py` y con el producto real (T035 adelantado) cuando
exista la entrega de S03.

### Incremental Delivery

US1 (abrir) → US2 (corregir, firmar) → US3 (identificadores pendientes) → US4 (verificar y entregar a S05).
La suite completa se corre al cerrar cada historia.

## Cobertura

| Requisito | Tareas | Verificación |
|---|---|---|
| FR-001 | T007, T012 | T011 |
| FR-002 | T007, T010 | T011 |
| FR-003 | T009 | T011 |
| FR-004 | T004, T006, T009 | T015 |
| FR-005 | T016, T023 | T015, T022 |
| FR-006 | T016, T024 | T015, T022 |
| FR-007 | T017, T019 | T015 |
| FR-008 | T020 | T015 |
| FR-009 | T026 | T025 |
| FR-010 | T005, T009 | T011, T015 |
| FR-011 | T010 | T033 |
| FR-012 | T010 | T035 |
| FR-013 | T029 | T025 |
| FR-014 | T027 | T025 |
| FR-015 | T028 | T025 |
| FR-016 | T017 | T033 |
| SC-001 | T012 | T011 |
| SC-002 | T016 | T015 |
| SC-003 | T024 | T022, T033 |
| SC-004 | T026 | T025 |
| SC-005 | T026 | T025 |
| SC-006 | T020 | T015 |
| SC-007 | T005, T012 | T011, T015 |
| SC-008 | T024 | T022 (automática), T038 (manual) |
| SC-009 | T029 | T025 |
| SC-010 | T012 | T011 |
| SC-011 | T016 | T015 |
| SC-012 | T010 | T038 (manual) |
| SC-013 | T027 | T025 |

## Notes

- Línea base (T001, 2026-10-26): `python -m unittest discover -s tests -p "test_*.py"` desde `platform/` → 230 pruebas, OK. Ninguna falla antes de tocar S04.
- Decisión sobre `platform/c4a/cita.py` (T002, 2026-10-26): **REESCRIBIR**. Motivo: el criterio fijado en T002 exige adoptar solo si la API coincide con `data-model.md`, y no coincide. Diferencias: (a) el marco es fijo `ISO/IEC 27001` con `version` separada, en vez de `marco` con valores de `MARCOS`; (b) solo carga el catálogo ISO, no NIST CSF 2.0 ni CIS v8.1 (FR-005); (c) nombres distintos del contrato: `estado_identificador` en vez de `identificador.estado`, `correspondencias` en vez de `correspondencias_adicionales`, `anadir_correspondencia` en vez de `agregar`, sin `fuente`; (d) `CAMPOS_CORREGIBLES` no coincide con `contracts/cli-cita.md`. Cubre bien la lógica de FR-001, FR-003, FR-004, FR-005 y FR-014 y sirve de referencia; no se conserva el archivo sin revisión. `cita.py` de la otra sesión no se modifica en T002; la reescritura empieza en T004.
- Desviación de orden: S04 avanza con S03 sin converger (plan y spec).
- Las tareas humanas (T038, T039) no las marca el agente.
