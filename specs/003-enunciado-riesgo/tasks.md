---
description: "Lista de tareas de S03 — El enunciado"
---

# Tasks: S03 — El enunciado

**Input**: documentos de diseño de `specs/003-enunciado-riesgo/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md),
[contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: se piden. Una prueba independiente por historia y pruebas de los criterios SC-001 a
SC-013 verificables por máquina. Las pruebas usan insumos **sintéticos, rotulados como tales**
(principio III); su resultado demuestra la herramienta, no audita el objetivo.

**Organization**: por historia (US1 a US4), en orden de prioridad. Ninguna tarea toca la red, lee
`.env` ni ejecuta pruebas contra el objetivo. Ninguna tarea escribe direcciones de red, puertos,
comandos contra el objetivo ni credenciales. Ninguna tarea escribe fuera de `03_hallazgos/` ni
modifica los archivos previos de esa carpeta.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: historia a la que pertenece (US1, US2, US3, US4)

## Path Conventions

- Código: `platform/c4a/` · Pruebas: `platform/tests/` · Producto: `03_hallazgos/enunciados_s03.*`
  y `03_hallazgos/enunciado-*.md` · Las pruebas se corren desde `platform/` con
  `python -m unittest discover -s tests`.

---

## Phase 1: Setup

**Purpose**: línea base y constantes.

- [X] T001 Correr la suite existente desde `platform/` y registrar la línea base (129 pruebas en
  verde el 2026-10-26) en Notes; si algo falla, detenerse y reportar
- [ ] T002 Extender `.gitattributes` con `03_hallazgos/enunciados_s03.* text eol=lf` y
  `03_hallazgos/enunciado-*.md text eol=lf`, con un comentario que cite el principio III

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: base común de las cuatro historias. Ninguna historia empieza antes.

- [ ] T003 Crear `platform/c4a/enunciado.py` con: `EnunciadoError(mensaje, codigo)` (como
  `RegistroError`); constantes `PRODUCTO = "S03 — El enunciado"`, `VERSION_ESQUEMA = "1"`,
  `APROBACION = ("borrador", "revisado")`, `CAMPOS_CORREGIBLES = ("condicion", "consecuencia",
  "criterio", "impacto")`, `EVENTOS = ("propuesta", "correccion", "descarte", "restablecimiento",
  "revision", "firma_anulada")`, `MARCAS` (`descartado`, `hecho no vigente`, `evidencia alterada`),
  rutas `03_hallazgos/enunciados_s03.json`, `.md`, `.firma.json` y prefijo de fichas
  `enunciado-`; mismo filtro de textos libres que S02 (FR-016) reutilizando `registro._PROHIBIDOS`
  y `alcance.limpiar`
- [ ] T004 En `platform/c4a/enunciado.py`, `cargar(raiz)` y `_escribir(raiz, contenido)`
  reutilizando `alcance.serializar`; el contenido canónico tiene exactamente las claves `producto`,
  `version_esquema`, `registro`, `enunciados`, `vacios`, `estado_aprobacion`, `historial`,
  `avisos` de `contracts/enunciados_s03.schema.json` (FR-011)
- [ ] T005 En `platform/c4a/enunciado.py`, contexto de origen `_contexto(raiz, previo)`: exige el
  registro de S02 (código 2 si falta), calcula `sha256` de `02_evidencia/registro_s02.json` y
  `entrega_sha256` como huella canónica de `registro.entregar(raiz)` (serialización determinista
  del dict de entrega), más `firmado` y `estado` (FR-002)
- [ ] T006 En `platform/c4a/enunciado.py`, identificadores con `util.short_id`: enunciado
  `short_id("R", hecho_id)` (patrón `^R-[0-9a-f]{10}$`), estable ante correcciones de texto
- [ ] T007 [P] Crear `platform/tests/enunciado_fixtures.py`: reutiliza `registro_fixtures` para
  dejar un registro de S02 **sintético rotulado** con H hechos (uno por resultado: positivo,
  negativo, inconcluso) y M «no consta», más variantes: sin `registro_s02.json`, con evidencia
  `sin_copia`, con un hecho marcado «alcance pendiente», y un registro firmado; expone `N_HECHOS`
  y `N_VACIOS` para SC-001

**Checkpoint**: base lista; las historias pueden empezar.

---

## Phase 3: User Story 1 - Abrir el enunciado sin registro firmado (Priority: P1) 🎯 MVP

**Goal**: el auditor obtiene un enunciado por cada hecho vigente de la entrega de S02, con campos
propuestos y cita de evidencias con huella, y los «no consta» listados como vacíos.

**Independent Test**: con una entrega con H hechos y M «no consta», el producto tiene exactamente
H enunciados y M vacíos, cada enunciado cita su hecho y al menos una evidencia con huella, y no
contiene estados de cumplimiento.

### Tests for User Story 1

- [ ] T008 [P] [US1] Escribir `platform/tests/test_enunciado_us1.py`: US1 escenarios 1 a 4; SC-001
  (H hechos y M «no consta» → exactamente H enunciados y M vacíos); FR-001 (sin
  `registro_s02.json` → código 2, nada escrito en `03_hallazgos/`); FR-002 (registro firmado →
  cita la huella de la entrega y `firmado: true`); FR-003 (hecho fuera/descartado → sin
  enunciado); FR-004 (campos completos: hecho, condición, consecuencia, criterio, impacto, falta,
  evidencias, estado, marcas); FR-005 (condición = afirmación del hecho; consecuencia según
  resultado; criterio cualitativo sin identificadores; impacto vacío); SC-002 (100 % citan hecho y
  evidencia con huella); SC-003 (cero cumplimientos, redes, comandos, puertos, credenciales);
  SC-007 (dos `abrir` → bytes idénticos); SC-010 (huellas de `README.md` y
  `matriz_cumplimiento.csv` de `03_hallazgos/` iguales antes y después)

### Implementation for User Story 1

- [ ] T009 [US1] En `platform/c4a/enunciado.py`, `abrir(raiz, fecha=None)`: deriva el contexto
  (T005), propone un enunciado por hecho vigente (T010-T012), conserva el historial previo y
  escribe el JSON y la vista; si el producto previo está firmado y los nuevos bytes difieren,
  rechaza con código 4 (FR-014)
- [ ] T010 [US1] En `platform/c4a/enunciado.py`, `_proponer(entrada, registro_firmado)`: condición
  desde la afirmación; consecuencia por resultado (positivo/negativo/inconcluso); criterio
  cualitativo (tipo de evidencia y resultado; sin identificadores de controles); impacto vacío;
  `falta` derivado de marcas y resultado: «alcance pendiente» → confirmar el alcance; `inconcluso`
  → evidencia adicional; `negativo` → reevaluar en una próxima revisión; evidencia `sin_copia` →
  verificar el original; registro no firmado → declararlo (FR-005)
- [ ] T011 [US1] En `platform/c4a/enunciado.py`, `_derivar(entrega, historial, registro_firmado)`:
  una propuesta por hecho (id estable T006), aplicando correcciones/descartes/restablecimientos del
  historial en orden; ordena por id; nada se borra (FR-007, FR-010)
- [ ] T012 [US1] En `platform/c4a/enunciado.py`, `vista(raiz)` y `_escribir_vista(raiz)`: título
  con estado, resumen (huella de la entrega de origen, firmado o no, conteos de enunciados y
  vacíos), sección «Enunciados (N)» con todos los campos, sección «Vacíos heredados del registro
  (M)» con la nota de que no son riesgos enunciados, historial y huella del JSON leída del
  archivo; sin extractos de evidencia (FR-012 parcial, FR-006)

**Checkpoint**: US1 se prueba sola; MVP.

---

## Phase 4: User Story 2 - La herramienta propone y el auditor corrige (Priority: P2)

**Goal**: el auditor corrige campos con motivo, descarta y restablece, revisa y firma; ningún
cambio llega a «firmado» sin la acción explícita del auditor; firmar exige criterio e impacto
completos.

**Independent Test**: una corrección queda en el historial con autor, fecha, valores y motivo y
deja el enunciado «revisado»; firmar desde «revisado» con campos completos escribe la firma;
ningún otro camino llega a «firmado».

### Tests for User Story 2

- [ ] T013 [P] [US2] Escribir `platform/tests/test_enunciado_us2.py`: US2 escenarios 1 a 5; FR-007
  (corregir los cuatro campos; campo no corregible, sin motivo o sin autor → código 1 y sin
  escritura; descartar y restablecer con motivo; nada desaparece); FR-008 (firmar desde
  «borrador», sin firmante o sin motivo → código 1; firmar con impacto vacío → código 1
  informando los enunciados incompletos; firma válida con conteos; corrección posterior elimina la
  firma y agrega `firma_anulada`); SC-006 (ningún camino a «firmado» sin `firmar`; 100 % de
  cambios con autor, fecha y motivo)

### Implementation for User Story 2

- [ ] T014 [US2] En `platform/c4a/enunciado.py`, `corregir(raiz, enunciado, campo, valor, motivo,
  autor, fecha=None)`: campo en `CAMPOS_CORREGIBLES`; motivo y autor obligatorios; valor filtrado;
  entrada inexistente → código 1; evento con campo, anterior y nuevo; el enunciado y el producto
  pasan a «revisado» (FR-007)
- [ ] T015 [US2] En `platform/c4a/enunciado.py`, `descartar(raiz, enunciado, motivo, autor,
  fecha=None)` y `restablecer(raiz, enunciado, motivo, autor, fecha=None)` (solo sobre un
  descartado), con marca `descartado` persistente y eventos (FR-007)
- [ ] T016 [US2] En `platform/c4a/enunciado.py`, `_guardar(raiz, contenido, evento)`: único punto
  de escritura de las acciones del auditor; agrega el evento, anula una firma previa y recompone
  los enunciados; `_cargar_vigente(raiz)` exige que el registro de origen no haya cambiado (código
  4) (FR-015, análisis I1 de S02)
- [ ] T017 [US2] En `platform/c4a/enunciado.py`, `revisar(raiz, autor, motivo, fecha=None)` y
  `firmar(raiz, firmante, motivo, fecha=None)`: firmar exige «revisado», firmante, justificación y
  criterio/impacto no vacíos en cada enunciado vigente; escribe `enunciados_s03.firma.json` con
  `archivo`, `sha256` de los bytes ya guardados, `firmante`, `fecha`, `motivo`, conteos y
  `NOTA_FIRMA` (FR-008, principio I)

**Checkpoint**: US1 y US2 funcionan juntas.

---

## Phase 5: User Story 3 - Un hecho negativo o inconcluso no es un cumplimiento (Priority: P3)

**Goal**: los hechos negativos e inconclusos enuncian riesgo acotado, con nota fija de
no-cumplimiento y «lo que falta» derivado; ningún archivo contiene estados de cumplimiento.

**Independent Test**: con hechos negativos e inconclusos, sus enunciados llevan la nota fija, la
`falta` deriva del resultado y una búsqueda no encuentra estados de cumplimiento.

### Tests for User Story 3

- [ ] T018 [P] [US3] Escribir `platform/tests/test_enunciado_us3.py`: US3 escenarios 1 a 4; FR-006
  (negativo → nota fija de no-cumplimiento y reevaluación en `falta`; inconcluso → evidencia
  adicional en `falta`; cero estados de cumplimiento en JSON, vista y fichas); SC-011 (100 % de
  negativos con nota)

### Implementation for User Story 3

- [ ] T019 [US3] En `platform/c4a/enunciado.py`, nota fija en la consecuencia del negativo («esto
  no acredita cumplimiento ni descarta su reaparición») y en la vista la frase de que un riesgo
  acotado no es una evaluación de controles (FR-006)
- [ ] T020 [US3] En `platform/c4a/enunciado.py`, `falta` del inconcluso incluye «evidencia
  adicional para decidir» y la vista mantiene la sección única de vacíos con conteo (SC-008 parte
  automática)

**Checkpoint**: US1 a US3 funcionan.

---

## Phase 6: User Story 4 - Verificar la consistencia con el registro y entregar a S04 (Priority: P3)

**Goal**: `verificar` recalcula producto, entrega y evidencias; `entregar` da a S04 exactamente
los vigentes.

**Independent Test**: alterar un byte de una evidencia y otro del JSON se detecta; un hecho que ya
no está en la entrega se informa «hecho no vigente»; la entrega contiene exactamente los
vigentes.

### Tests for User Story 4

- [ ] T021 [P] [US4] Escribir `platform/tests/test_enunciado_us4.py`: US4 escenarios 1 a 4; SC-004
  (alterar un byte del JSON → `verificar` informa alteración y código 3); SC-005 (alterar un byte
  de una copia → enunciado «evidencia alterada», fuera de la entrega; firmado → «firmado con
  evidencia alterada»); FR-009 (hecho que sale de la entrega → «hecho no vigente»); SC-009 (la
  entrega contiene exactamente los vigentes: sin descartados, no vigentes ni alterados; al
  restablecer el único hecho de un dominio, vuelve); SC-013 (firmado + registro cambiado → `abrir`
  y las acciones terminan en código 4 sin escribir)

### Implementation for User Story 4

- [ ] T022 [US4] En `platform/c4a/enunciado.py`, `verificar(raiz)`: recalcula la huella del JSON
  contra la firma; recalcula `entrega_sha256` actual y compara con la registrada; recalcula la
  huella de cada evidencia citada sobre su copia (o su original si es referencia sin copia y sigue
  accesible); devuelve `huella_ok`, `entrega_ok`, `evidencias_alteradas[]`, `hechos_no_vigentes[]`,
  `estado` y `estado_informado` (FR-009)
- [ ] T023 [US4] En `platform/c4a/enunciado.py`, `_cargar_vigente` además exige que la huella de
  `registro_s02.json` y la entrega sigan iguales (código 4) (FR-015)
- [ ] T024 [US4] En `platform/c4a/enunciado.py`, `entregar(raiz) -> dict` para S04: enunciados
  vigentes (no descartados, con hecho en la entrega vigente y sin evidencia alterada), cada uno con
  activo, dominio, condición, consecuencia, criterio, impacto, falta, hecho y evidencias con
  huellas; más `vacios` y `firmado` según `estado_efectivo` (FR-013)
- [ ] T025 [US4] En `platform/c4a/enunciado.py`, `estado_efectivo(raiz) -> str`: `borrador`,
  `revisado` o `firmado` (huella del JSON contra la firma, principio III)

**Checkpoint**: las cuatro historias funcionan.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Escribir `platform/tests/test_enunciado_cli.py`: invoca `c4a.cli.main` sobre un
  fixture sintético y comprueba los códigos de salida 0, 1, 2 y 4 de `contracts/cli-enunciado.md`
- [ ] T027 [P] Agregar a `platform/tests/test_enunciado_us1.py` la prueba de las fichas: una
  `enunciado-<id>.md` por enunciado, sin extractos de evidencia y con los mismos campos que el
  JSON (FR-012)
- [ ] T028 Correr la suite completa desde `platform/`; si una prueba que antes pasaba falla,
  detenerse y reportar
- [ ] T029 Generar el producto real con `enunciado abrir` sobre la raíz del repositorio y registrar
  en Notes el conteo de enunciados y vacíos; comprobar SC-003 (búsqueda limpia) y SC-010 (huellas
  de los archivos previos sin cambios). No se corrige ni firma nada: eso es del auditor
- [ ] T030 [P] Documentar el subcomando `enunciado` en `platform/README.md` (uso, archivos que
  produce, que firmar no abre la compuerta y que un negativo no acredita cumplimiento)
- [ ] T031 [P] Registrar en `specs/003-enunciado-riesgo/quickstart.md` el resultado de la
  validación de punta a punta
- [ ] T032 Acción humana: el auditor mide SC-008 y un tercero hace el recorrido de SC-009; ambos
  resultados se registran en `specs/003-enunciado-riesgo/checklists/enunciado.md` → Notes
- [ ] T033 Acción humana: el auditor corrige criterio e impacto de los enunciados reales cuando
  existan hechos, revisa y firma con `enunciado firmar --motivo`. La herramienta no lo hace por él

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (T001–T002) → Foundational (T003–T007) → US1 (T008–T012) → US2 (T013–T017) → US3
  (T018–T020) → US4 (T021–T025) → Polish (T026–T033).
- US3 puede ir en paralelo con US2 (misma base, archivos de prueba distintos).
- US4 depende de US2 (`_guardar`, `estado_efectivo`) y US1 (`_derivar`).
- T032 y T033 son humanas y van al final; T033 depende de T029.

### Within Each User Story

- La prueba de la historia se escribe primero y falla; luego la implementación.
- Las tareas de implementación de una historia tocan `platform/c4a/enunciado.py`, así que van en
  serie.

### Parallel Opportunities

- T002 en paralelo con T001.
- T007 en paralelo con T003–T006 (otro archivo).
- T008, T013, T018 y T021 en paralelo entre sí (archivos de prueba distintos), una vez lista la
  fase 2.
- T026, T027, T030 y T031 en paralelo.

## Cobertura

| Requisito | Tareas | Verificación |
|---|---|---|
| FR-001 | T005, T009 | T008 |
| FR-002 | T005, T009 | T008 |
| FR-003 | T011 | T008 (SC-001) |
| FR-004 | T010, T011 | T008 |
| FR-005 | T010 | T008 |
| FR-006 | T010, T019 | T018 (SC-011), T008 (SC-003) |
| FR-007 | T011, T014, T015 | T013 |
| FR-008 | T016, T017 | T013 (SC-006) |
| FR-009 | T022 | T021 (SC-004, SC-005) |
| FR-010 | T004, T011 | T008 (SC-007) |
| FR-011 | T004, T009 | T008 (SC-010) |
| FR-012 | T009 | T027 |
| FR-013 | T024 | T021 (SC-009) |
| FR-014 | T005, T009 | T021 (SC-013) |
| FR-015 | T016, T023 | T021 (SC-013) |
| FR-016 | T003 | T008 (SC-003) |
| SC-001 | T011 | T008 |
| SC-002 | T010 | T008 |
| SC-003 | T003, T012 | T008, T029 |
| SC-004 | T022 | T021 |
| SC-005 | T022, T024 | T021 |
| SC-006 | T014–T017 | T013 |
| SC-007 | T004, T011 | T008 |
| SC-008 | T012, T020 | T008 (automática), T032 (manual) |
| SC-009 | T024 | T021 |
| SC-010 | T004, T009 | T008, T029 |
| SC-011 | T019 | T018 |
| SC-012 | T012 (evidencia y huella por enunciado) | T032 (manual) |
| SC-013 | T009, T016, T023 | T021 |

## Notes

- Línea base (T001, 2026-10-26): `python -m unittest discover -s tests` → 129 pruebas, OK.
