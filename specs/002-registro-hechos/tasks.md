---

description: "Lista de tareas de S02 — El registro"
---

# Tasks: S02 — El registro

**Input**: documentos de diseño de `specs/002-registro-hechos/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: se piden. La spec define una prueba independiente por historia y los criterios SC-001 a
SC-013; como en S01, cada criterio verificable por máquina tiene su prueba. Las pruebas usan insumos
**sintéticos, rotulados como tales** (principio III); su resultado demuestra la herramienta, no audita
el objetivo.

**Organization**: por historia (US1 a US4), en orden de prioridad. Ninguna tarea toca la red, lee
`.env` ni ejecuta pruebas contra el objetivo. Ninguna tarea escribe direcciones de red, puertos,
comandos contra el objetivo ni credenciales. Ninguna tarea escribe en `scope/` ni en
`02_evidencia/inventario.json`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: historia a la que pertenece (US1, US2, US3, US4)

## Path Conventions

- Código: `platform/c4a/` · Pruebas: `platform/tests/` · Producto: `02_evidencia/registro_s02.*` ·
  Copias de evidencia: `evidence/registro_s02/` (fuera de git) · Las pruebas se corren desde
  `platform/` con `python -m unittest discover -s tests`.

---

## Phase 1: Setup

**Purpose**: línea base y fines de línea.

- [X] T001 Correr la suite existente desde `platform/` y registrar la línea base (78 pruebas en verde el 2026-10-22) en `specs/002-registro-hechos/tasks.md` → sección Notes; si algo falla, detenerse y reportar
- [X] T002 [P] Extender `.gitattributes` con `02_evidencia/registro_s02.* text eol=lf` y un comentario que cite el principio III, como la regla existente de `scope/**` (plan → Pendientes declarados, research D8)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: base común de las cuatro historias. Ninguna historia empieza antes.

- [X] T003 Crear `platform/c4a/registro.py` con: `RegistroError(mensaje, codigo)` (como `AlcanceError`); constantes `PRODUCTO = "S02 — El registro"`, `VERSION_ESQUEMA = "1"`, `RESULTADOS = ("positivo","negativo","inconcluso","no-ejecutado")`, `RESULTADOS_EVIDENCIA = ("positivo","negativo","inconcluso")`, `TIPOS_EVIDENCIA = ("documental","tecnica")`, `APROBACION = ("borrador","revisado")` («firmado» se deriva de una firma válida), `CAMPOS_CORREGIBLES = ("afirmacion","resultado","motivo")`, `EVENTOS = ("aporte","rechazo","correccion","descarte","restablecimiento","revision","firma_anulada")`, `MARCAS` (`descartada`, `superada por H-…`, `fuera del alcance vigente`, `alcance pendiente`, `evidencia alterada`) y `MOTIVOS_NO_CONSTA = ("compuerta cerrada","requiere solicitud documental","sin evidencia")`; rutas `02_evidencia/registro_s02.json`, `.md`, `.firma.json` y `evidence/registro_s02/` (data-model → Archivos)
- [X] T004 En `platform/c4a/registro.py`, `cargar(raiz)` y `_guardar(raiz, contenido)` reutilizando `alcance.serializar` (`sort_keys`, sangría 2, UTF-8, salto final, sin hora de generación) y escritura binaria para que los bytes sean exactos; el contenido canónico tiene exactamente las claves `producto`, `version_esquema`, `alcance`, `entradas`, `rechazos`, `estado_aprobacion`, `historial`, `avisos` de `contracts/registro_s02.schema.json` (FR-018)
- [X] T005 En `platform/c4a/registro.py`, identificadores con `util.short_id`: entrada hecho `short_id("H", activo, fila_dominio, afirmacion_normalizada)` (minúsculas, espacios colapsados; patrón `^[HN]-[0-9a-f]{10}$`), entrada «no consta» `short_id("N", activo, fila_dominio)`, evidencia `short_id("E", sha256_original, tipo)` (patrón `^E-[0-9a-f]{10}$`); el id de un hecho se fija en su primer aporte y una corrección de la afirmación no lo cambia (FR-020, research D4)
- [X] T006 En `platform/c4a/registro.py`, motor de derivación `_derivar(raiz, historial)`: parte de las entradas «no consta» del alcance vigente y reaplica el historial en orden (aporte → crea o amplía el hecho; correccion; descarte; restablecimiento; revision); calcula las marcas `superada por H-…` y `alcance pendiente`; ordena las entradas por activo, dominio y clase; nada se borra (FR-013, FR-015, FR-018, research D1)
- [X] T007 [P] Crear `platform/tests/registro_fixtures.py`: reutiliza `alcance_fixtures.construir` y `alcance.proponer` para dejar un `scope/alcance_s01.json` **sintético rotulado** («FIXTURE SINTÉTICO — no es el ejercicio»); variantes: alcance en borrador con un activo y N dominios conocidos (dentro y pendientes, uno «fuera», uno que requiere políticas, personas o procesos), sin `alcance_s01.json`, alcance firmado, autorización firmada y vigente; crea archivos de evidencia sintéticos (texto rotulado) y un `.c4a/runs.jsonl` sintético con una corrida cuyo `target` es otra ruta de repositorio y otra cuyo `target` es el activo; expone `N_DOMINIOS_FIXTURE` para SC-001

**Checkpoint**: base lista; las historias pueden empezar.

---

## Phase 3: User Story 1 - Abrir el registro sin alcance firmado (Priority: P1) 🎯 MVP

**Goal**: el auditor obtiene un registro con una entrada «no consta» por activo y dominio dentro o
pendiente, que declara si el alcance está firmado, sin ningún hecho afirmado.

**Independent Test**: con un alcance en borrador y ninguna evidencia, el registro tiene N + 1 entradas
«no consta», declara el alcance no firmado y no contiene hechos.

### Tests for User Story 1

- [X] T008 [P] [US1] Escribir `platform/tests/test_registro_us1.py`: US1 escenarios 1 a 4; SC-001 (N dominios dentro o pendientes y ninguna evidencia → exactamente N + 1 «no consta» y cero hechos); FR-002 (`alcance.sha256` y `alcance.firmado` presentes; firmado → cita la huella del alcance firmado); FR-001 (sin `alcance_s01.json` → aviso «falta el producto anterior», `minimo_de_referencia: true`, todo «no consta», `scope/` sin cambios, y `aportar` rechazado con código 2); FR-003 (dominio «fuera» → sin entradas); SC-012 (solo se crean `02_evidencia/registro_s02.json` y `.md`; huellas de `02_evidencia/inventario.json` y de cada archivo de `scope/` iguales antes y después); FR-016/SC-008 parte automática (una sola sección «No consta (N)» en la vista y N igual a las entradas «no consta»); FR-011 (ningún campo contiene `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`); SC-007 (dos `abrir` seguidos → bytes idénticos)

### Implementation for User Story 1

- [X] T009 [US1] En `platform/c4a/registro.py`, entradas «no consta» desde el alcance: una por la fila `activo` (`dominio = {"fila": null, "valor": "(el activo como un todo)"}`) y una por cada fila `dominio` que `alcance.consultar` responde «dentro» o «pendiente» (`dominio = {"fila": "A-…", "valor": <valor de la fila>}`); resultado `no-ejecutado`, afirmación «no consta», motivo «sin evidencia» por ahora, `estado_aprobacion: "borrador"`, `evidencias: []`; lo «fuera» no genera entradas (FR-003, FR-004)
- [X] T010 [US1] En `platform/c4a/registro.py`, mínimo de referencia: si falta `scope/alcance_s01.json`, derivar las filas en memoria con `alcance.derivar(raiz)` **sin escribir en `scope/`**, clasificar esas filas en memoria con la misma regla que `alcance.consultar` (pendiente → «pendiente»; `excluido` → «fuera»; resto → «dentro»), registrar `alcance = {archivo, sha256: null, firmado: false, minimo_de_referencia: true, …}` y el aviso «falta el producto anterior (S01); se usa scope/alcance.md como mínimo de referencia» (FR-001, US1 escenario 2)
- [X] T011 [US1] En `platform/c4a/registro.py`, `abrir(raiz, fecha_referencia=None)`: registra `alcance = {archivo: "scope/alcance_s01.json", sha256: util.sha256_file(...), firmado: alcance.estado_efectivo(raiz) == "firmado", minimo_de_referencia: false, autorizacion_sha256, compuerta, compuerta_fecha}` (la compuerta, de `alcance.evaluar_compuerta(raiz, fecha_referencia)`, se evalúa una vez y se guarda; derivar usa el valor guardado, no la fecha del día), deriva con T006, conserva el historial previo si el registro ya existe y escribe `02_evidencia/registro_s02.json` (FR-002, FR-015)
- [X] T012 [US1] En `platform/c4a/registro.py`, `vista(raiz)` y `escribir_vista(raiz)` para `02_evidencia/registro_s02.md`, en castellano: resumen (alcance de origen y su huella, «alcance no firmado» cuando corresponde, estado efectivo, conteos de hechos, «no consta» y rechazos, nunca «sin hallazgos» ni «cumple»), sección única «No consta (N)» con activo, dominio, resultado y motivo, sección «Hechos» con evidencias (id, tipo, ubicación, huella) y marcas, sección «Rechazos (N)», historial y la huella del JSON leída del archivo persistido; sin extractos de evidencia (FR-011, FR-012, FR-016, principio VIII)
- [X] T013 [US1] En `platform/c4a/cli.py`, subcomando `registro` con la acción `abrir [--raiz]` según `specs/002-registro-hechos/contracts/cli-registro.md`; stdout y stderr con `errors="replace"` como en `alcance`

**Checkpoint**: US1 se prueba sola; MVP.

---

## Phase 4: User Story 2 - La herramienta propone un hecho y el auditor lo corrige (Priority: P2)

**Goal**: el auditor aporta una evidencia y obtiene un hecho propuesto en «borrador»; corrige,
descarta, restablece, revisa y firma; cualquier cambio anula la firma.

**Independent Test**: con una evidencia documental sintética dentro del alcance, la entrada propuesta
trae tipo, huellas, fecha, responsable y resultado; una corrección queda en el historial; nada llega a
«firmado» sin la acción del auditor.

### Tests for User Story 2

- [X] T014 [P] [US2] Escribir `platform/tests/test_registro_us2.py`: US2 escenarios 1 a 5; SC-002 (100 % de hechos con al menos una evidencia con tipo, ubicación, fecha, responsable y huella); FR-005 (documental sin `--origen` → rechazo; con `--sin-copia` → `copia: null`, `sha256_guardado: null`, `sin_copia: true`; con copia → `sha256_guardado` = huella del archivo en `evidence/registro_s02/` y `sha256_original` = huella del origen); FR-006 (varias evidencias con resultados distintos → «inconcluso»); SC-011 (mismo hecho aportado dos veces → una entrada con dos evidencias; misma evidencia dos veces → no se duplica); FR-013 (corregir `afirmacion`, `resultado` y `motivo`; campo no corregible, sin motivo o sin autor → rechazo y archivo sin cambios; descartar y restablecer con motivo; ninguna entrada desaparece); FR-014 (firmar desde «borrador», sin firmante o sin justificación → rechazo; firma con `no_consta_al_firmar`; cualquier aporte, corrección, descarte o restablecimiento posterior elimina la firma y agrega `firma_anulada`); SC-004 parte registro (alterar un byte de `registro_s02.json` en varias posiciones → `verificar` lo detecta); I1 (un rechazo o un `revisar` posteriores a la firma también la anulan con `firma_anulada`, y `verificar` no informa alteración); FR-014 (un aporte sobre un registro «revisado» lo devuelve a «borrador»); SC-006 (ningún camino llega a «firmado» sin `firmar`; 100 % de correcciones, descartes y restablecimientos con autor, fecha y motivo); SC-007 (mismo alcance, evidencias y correcciones → bytes idénticos)

### Implementation for User Story 2

- [X] T015 [US2] En `platform/c4a/registro.py`, `aportar(raiz, activo, dominio, afirmacion, resultado, evidencia, tipo, fecha_recoleccion, autor, origen=None, corrida=None, sin_copia=False, fecha=None)`: sin `scope/alcance_s01.json` → `RegistroError` código 2 «falta el alcance de S01» sin escribir (US1 escenario 2: sin hechos); archivo inexistente o ilegible → `RegistroError` código 2 sin escribir; `dominio` acepta el id `A-…` de la fila, un texto que `alcance.consultar` resuelva o `activo` para la entrada del activo; crear `_admisible(...)` con el chequeo de documental sin origen → rechazo «origen no declarado» como **último** paso (T026 inserta los anteriores delante); un aporte sobre un registro «revisado» lo devuelve a «borrador» (FR-014); si es admisible, copia el archivo a `evidence/registro_s02/<E-id>.<ext>` (salvo `sin_copia`) y calcula `sha256_guardado` sobre la copia ya escrita y `sha256_original` sobre el origen; `ubicacion_original` es la ruta relativa al repositorio si está dentro, si no solo el nombre del archivo; afirmación, origen y autor pasan por `alcance.limpiar`; agrega el evento `aporte` (FR-005, FR-006, FR-012, FR-020, research D2, D7)
- [X] T016 [US2] En `platform/c4a/registro.py`, al derivar un hecho: resultado = el de sus evidencias si coinciden, «inconcluso» si discrepan, salvo corrección posterior del auditor; la entrada «no consta» del mismo activo y dominio pasa a `superada por H-…` solo mientras exista un hecho vigente (no descartado) para ese activo y dominio; si se descarta, la «no consta» vuelve a valer; nunca se borra (FR-006, US2 escenario 5, research D5)
- [X] T017 [US2] En `platform/c4a/registro.py`, `corregir(raiz, entrada, campo, valor, motivo, autor, fecha=None)` con `campo` en `afirmacion|resultado|motivo` (el resultado corregido solo admite `positivo|negativo|inconcluso|no-ejecutado`), `descartar(raiz, entrada, motivo, autor, fecha=None)` y `restablecer(raiz, entrada, motivo, autor, fecha=None)` (solo sobre una descartada): motivo y autor obligatorios y no vacíos, filtrados con `limpiar`; entrada inexistente → código 1; eventos con anterior y nuevo; la entrada pasa a «revisado» (FR-013)
- [X] T018 [US2] En `platform/c4a/registro.py`, `_anular_firma`, llamada desde el único punto de escritura `_guardar`: toda escritura posterior a una firma (aporte, rechazo, corrección, descarte, restablecimiento o revisión) elimina `registro_s02.firma.json` y agrega el evento `firma_anulada` con autor, fecha y motivo (FR-014, como `alcance._anular_firma`)
- [X] T019 [US2] En `platform/c4a/registro.py`, `revisar(raiz, autor, motivo, fecha=None)` (evento `revision`, registro → «revisado») y `firmar(raiz, firmante, motivo, fecha=None)`: exige «revisado», firmante y justificación; escribe `02_evidencia/registro_s02.firma.json` con `archivo`, `sha256` = `util.sha256_file` del JSON ya persistido, `firmante`, `fecha`, `motivo`, `no_consta_al_firmar` y la nota «Firmar el registro no abre la compuerta de autorización» (FR-014, principio I)
- [X] T020 [US2] En `platform/c4a/registro.py`, `verificar(raiz)` y `estado_efectivo(raiz)`: recalculan la huella de `registro_s02.json` contra la firma sin regenerar; `estado_efectivo` devuelve `borrador`, `revisado` o `firmado` (FR-008 parte registro, principio III)
- [X] T021 [US2] En `platform/c4a/cli.py`, acciones `registro aportar`, `corregir`, `descartar`, `restablecer`, `revisar`, `firmar` y `verificar` con los argumentos y códigos de salida 0, 1, 2 y 3 de `specs/002-registro-hechos/contracts/cli-registro.md`; agregar al contrato el valor `activo` de `--dominio`

**Checkpoint**: US1 y US2 funcionan juntas.

---

## Phase 5: User Story 3 - Un dato no consta y la fila se conserva (Priority: P3)

**Goal**: «no se miró» nunca se lee como «no se observó nada»: cada «no consta» lleva su motivo y se
conserva.

**Independent Test**: con la compuerta cerrada y un dominio técnico sin evidencia, la entrada está «no
consta», `no-ejecutado`, con motivo «compuerta cerrada», y nada dice «sin hallazgos».

### Tests for User Story 3

- [X] T022 [P] [US3] Escribir `platform/tests/test_registro_us3.py`: US3 escenarios 1 a 4; FR-009 (compuerta cerrada y dominio técnico sin evidencia → `no-ejecutado` y «compuerta cerrada»; la huella de `scope/autorizacion.md` no cambia y ninguna función de `registro` abre la compuerta); FR-010 (dominio con la observación de políticas, personas o procesos → «requiere solicitud documental»); las «no consta» se conservan al regenerar; un registro sin hechos positivos resume «N entradas no constan» y en ningún archivo aparece «sin hallazgos»; firmar con «no consta» está permitido y la firma guarda el conteo

### Implementation for User Story 3

- [X] T023 [US3] En `platform/c4a/registro.py`, motivo de cada «no consta» según research D5: «requiere solicitud documental» si la fila de dominio del alcance trae la observación «no se acredita con una prueba técnica» (políticas, personas o procesos); «compuerta cerrada» si el dominio es técnico (la `clave` de la fila empieza por `tecnico:`, como la deriva `alcance._derivar_dominios`) y la compuerta guardada en `alcance.compuerta` no es «abierta»; «sin evidencia» en otro caso; la compuerta se lee en solo lectura (FR-009, FR-010)
- [X] T024 [US3] En `platform/c4a/registro.py`, resumen de la vista: conteo «N entradas no constan» siempre visible; texto fijo que aclara que «no consta» no equivale a «sin hallazgos» ni a «cumple» (FR-011, US3 escenario 4)

**Checkpoint**: US1 a US3 funcionan.

---

## Phase 6: User Story 4 - Rechazar evidencia que no acredita esta auditoría (Priority: P3)

**Goal**: la evidencia de otro activo, de un dominio fuera, de otra corrida o tomada sin autorización
no entra como hecho; cada rechazo queda anotado; una evidencia alterada deja de acreditar.

**Independent Test**: con evidencias sintéticas de cada causa, ninguna entra como hecho y cada rechazo
tiene su motivo; alterar un byte de una copia hace que la entrada se informe «evidencia alterada».

### Tests for User Story 4

- [X] T025 [P] [US4] Escribir `platform/tests/test_registro_us4.py`: US4 escenarios 1 a 4; SC-003 (las cinco causas: otro activo, dominio fuera, corrida sobre otro objetivo, técnica sin autorización vigente en su fecha de recolección, documental sin origen → 100 % rechazadas, cada una con su motivo y, si aplica, la fila del alcance); la evidencia documental se acepta con la compuerta cerrada; la técnica se acepta con una autorización sintética firmada y vigente en su fecha; SC-013 (activo o dominio «pendiente» → aceptada con la marca «alcance pendiente», que viaja en la entrega); SC-004 parte evidencia (alterar un byte de una copia → `verificar` informa la entrada «evidencia alterada» y código 3; registro firmado → «firmado con evidencia alterada»); FR-015 (alcance cambiado con un dominio que pasa a «fuera» → la entrada se conserva con «fuera del alcance vigente»; registro firmado y alcance cambiado → aviso, código 4, sin escribir; lo mismo si cambia `scope/autorizacion.md` o el estado de la compuerta; dos `abrir` en fechas distintas con los mismos insumos → bytes idénticos, FR-018); SC-010 (la entrega contiene exactamente las vigentes y ninguna descartada, superada, fuera del alcance vigente ni con evidencia alterada; si se descarta el único hecho de un dominio, su «no consta» vuelve a la entrega)

### Implementation for User Story 4

- [X] T026 [US4] En `platform/c4a/registro.py`, admisibilidad en el orden de research D3, y el primer motivo que falle es el rechazo: activo «fuera» según `alcance.consultar("activo", …)` → «otro activo» con la fila o «no figura en el alcance»; dominio «fuera» → «dominio fuera del alcance» con la fila; `--corrida` cuyo `target` en `.c4a/runs.jsonl` no es el activo, o que no figura → «otro objetivo» (leer el archivo solo si existe; `Ledger.__init__` crea la carpeta, así que no se instancia sin él); técnica con `alcance.evaluar_compuerta(raiz, fecha_recoleccion)` distinta de «abierta» → «sin autorización vigente»; documental sin origen → «origen no declarado»; el rechazo se guarda como evento `rechazo` (evidencia por tipo, ubicación y huella; activo; dominio; motivo; regla; fila; autor; fecha) y la acción termina en 0 informando el motivo (FR-007, FR-016)
- [X] T027 [US4] En `platform/c4a/registro.py`, marca «alcance pendiente» para los aportes sobre un activo o dominio que el alcance responde «pendiente» (FR-021, research D10)
- [X] T028 [US4] En `platform/c4a/registro.py`, cambio del alcance: si la huella de `scope/alcance_s01.json`, la de `scope/autorizacion.md` o el estado de la compuerta difieren de los registrados, `abrir` agrega un aviso con las entradas afectadas y marca «fuera del alcance vigente» las que ahora responden «fuera»; si el registro está firmado, avisa y no escribe (`RegistroError` código 4) (FR-015, research D6)
- [X] T029 [US4] En `platform/c4a/registro.py`, en `verificar`, recalcular la huella de cada copia en `evidence/registro_s02/` (y del original cuando `sin_copia`, si sigue accesible): las que no coinciden dejan su entrada «evidencia alterada», calculada al verificar y no persistida en el JSON firmado; si el registro está firmado, el estado informado es «firmado con evidencia alterada» (FR-008)
- [X] T030 [US4] En `platform/c4a/registro.py`, `entregar(raiz) -> dict` para S03: entradas vigentes de FR-019 (hechos no descartados, dentro del alcance vigente y sin evidencia alterada; «no consta» no superadas), cada una con activo, dominio, resultado, marcas, evidencias con huellas, y `firmado` según `estado_efectivo` (FR-019, research D9)
- [X] T031 [US4] En `platform/c4a/cli.py`, acción `registro entregar [--json]` y el código 4 de `abrir`, según `specs/002-registro-hechos/contracts/cli-registro.md`

**Checkpoint**: las cuatro historias funcionan.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T032 [P] Escribir `platform/tests/test_registro_cli.py`: invoca `c4a.cli.main` sobre un fixture sintético y comprueba los códigos de salida 0, 1, 2, 3 y 4 de `contracts/cli-registro.md` (lección de la convergencia de S01)
- [X] T033 [P] Agregar a `platform/tests/test_registro_us1.py` la prueba SC-005: búsqueda sobre `registro_s02.json` y `.md` generados con evidencias sintéticas que contienen direcciones de red de documentación, una línea con forma de comando y una con forma de credencial → cero direcciones de red, comandos, puertos, credenciales y estados de cumplimiento en el registro (FR-012)
- [X] T034 Correr la suite completa desde `platform/` (existente y nueva); si una prueba que antes pasaba falla, detenerse y reportar
- [X] T035 Generar el producto real con `registro abrir` sobre la raíz del repositorio: `02_evidencia/registro_s02.json` y `.md`; comprobar que no contienen direcciones de red, puertos, comandos ni credenciales (SC-005), que `02_evidencia/inventario.json` y `scope/` no cambiaron (SC-012) y registrar en Notes el conteo de entradas «no consta» y sus motivos. No se aporta evidencia del ejercicio: eso es del auditor
- [X] T036 [P] Documentar el subcomando `registro` en `platform/README.md` (uso, archivos que produce, dónde quedan las copias, que firmar no abre la compuerta y que «no consta» no es «sin hallazgos»)
- [X] T037 [P] Registrar en `specs/002-registro-hechos/quickstart.md` el resultado de la validación de punta a punta (pasos 1 a 5, con fixtures sintéticos para los pasos 3 a 5)
- [ ] T038 Acción humana: el auditor mide SC-008 (minutos para identificar todo lo que no consta en `02_evidencia/registro_s02.md`) y un tercero hace el recorrido de SC-009; ambos resultados se registran en `specs/002-registro-hechos/checklists/registro.md` → Notes
- [ ] T039 Acción humana: el auditor aporta la evidencia documental que tenga, con origen declarado, corrige, revisa y firma el registro con `registro firmar --motivo` (FR-014). La herramienta no lo hace por él

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (T001–T002) → Foundational (T003–T007) → US1 (T008–T013) → US2 (T014–T021) → US3 (T022–T024) → US4 (T025–T031) → Polish (T032–T039).
- US3 depende de US1 (entradas «no consta» y vista); puede ir en paralelo con US2.
- US4 depende de US2 (`aportar`, `verificar`, `estado_efectivo`).
- T038 y T039 son humanas y van al final; T039 depende de T035.

### Within Each User Story

- La prueba de la historia se escribe primero y falla; luego la implementación; luego el subcomando.
- Todas las tareas de implementación tocan `platform/c4a/registro.py`, así que dentro de una historia van en serie.

### Parallel Opportunities

- T002 en paralelo con T001.
- T007 en paralelo con T003–T006 (otro archivo).
- T008, T014, T022 y T025 en paralelo entre sí (archivos de prueba distintos), una vez lista la fase 2.
- T032, T033, T036 y T037 en paralelo.

## Parallel Example: pruebas

```text
T008 platform/tests/test_registro_us1.py
T014 platform/tests/test_registro_us2.py
T022 platform/tests/test_registro_us3.py
T025 platform/tests/test_registro_us4.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

Fases 1 y 2, luego US1. Validar con `test_registro_us1.py` y con el registro real (T035 adelantado):
hoy es el caso real, alcance en borrador y compuerta cerrada.

### Incremental Delivery

US1 (abrir) → US2 (aportar, corregir y firmar) → US3 (motivos de «no consta») → US4 (rechazos,
alteración y entrega a S03). Cada historia suma sin romper la anterior; la suite completa se corre al
cerrar cada una.

## Cobertura

| Requisito | Tareas | Verificación |
|---|---|---|
| FR-001 | T010, T011 | T008 |
| FR-002 | T011 | T008 |
| FR-003 | T009 | T008 (SC-001) |
| FR-004 | T003, T009 | T008, T014 |
| FR-005 | T015 | T014 |
| FR-006 | T015, T016 | T014 |
| FR-007 | T015, T026 | T025 (SC-003) |
| FR-008 | T020, T029 | T014, T025 (SC-004) |
| FR-009 | T023 | T022 |
| FR-010 | T023 | T022 |
| FR-011 | T012, T024 | T008, T022 |
| FR-012 | T012, T015 | T033 (SC-005), T035 |
| FR-013 | T006, T017 | T014 |
| FR-014 | T018, T019 | T014, T022 |
| FR-015 | T006, T011, T028 | T025 |
| FR-016 | T012, T026 | T008 |
| FR-017 | T003, T015 | T008 (SC-012), T035 |
| FR-018 | T004, T006 | T008, T014 (SC-007) |
| FR-019 | T030 | T025 (SC-010) |
| FR-020 | T005, T015 | T014 (SC-011) |
| FR-021 | T027 | T025 (SC-013) |
| SC-001 | T009 | T008 |
| SC-002 | T015 | T014 |
| SC-003 | T026 | T025 |
| SC-004 | T020, T029 | T014, T025 |
| SC-005 | T012, T015 | T033, T035 |
| SC-006 | T017, T019 | T014 |
| SC-007 | T004, T006 | T008, T014 |
| SC-008 | T012 | T008 (automática), T038 (manual) |
| SC-009 | T012 (evidencia y huella por entrada) | T038 (manual) |
| SC-010 | T030 | T025 |
| SC-011 | T005, T015 | T014 |
| SC-012 | T010, T011 | T008, T035 |
| SC-013 | T027 | T025 |

## Reconciliación con el Project #7 (solo lectura, 2026-10-22)

Leído con `gh issue list --state all`. No hay ninguna issue de la épica S02 ni de sus historias. Las
issues #41 a #45 son S01. **Acción propuesta, pendiente de la aprobación del dueño. No se escribió
nada en GitHub.**

| Issue existente | Relación con S02 | Acción propuesta |
|---|---|---|
| — | Épica S02 | Crear `[ÉPICA] S02 — El registro`, sub-issue de #1, como S01 |
| — | US1–US4 | Crear 4 historias, sub-issues de la épica S02, con sus tareas como checklist (forma acordada en S01) |
| #22 HU Recopilación reproducible con evidencia hasheada | S02 cubre el registro con huella sobre los bytes guardados; la custodia cifrada no | Sin cambios; enlazar la épica S02 como «relacionada» |
| #23 Cifrado y cadena de custodia | Fuera de S02 (Assumptions) | Sin cambios |
| #30 Coherencia del registro de evidencia con `evidence/README.md` | Solapamiento parcial: S02 copia a `evidence/registro_s02/` | Sin cambios; anotar la relación con T015 |
| #24 Análisis verificable | Consume la entrega de S02 (S03 en adelante) | Sin cambios |
| #45 S01 US4 — Entregar el alcance a S02 | S02 consume `consultar` y `evaluar_compuerta` | Sin cambios; anotar «la consume la épica S02» |
| #33 Revisión por segundo par | Fuera de S02 (Assumptions) | Sin cambios |

Duplicados detectados: ninguno. Huérfanas: ninguna.

**Tablero creado (2026-10-22, aprobación expresa del dueño)**: épica S02 #46 (sub-issue de #1) e
historias US1 #47, US2 #48, US3 #49, US4 #50 (sub-issues de #46), con sus tareas como checklist.
Campos: Sprint «S02», Fase C4A «Recopilar», épica «In Progress» e historias «Todo». Se comentó la
relación en #22, #30 y #45. En la misma sesión: rutas de `docs/` corregidas en 44 issues, talla «Por
definir» en #5 y #8, y #40 cerrada como completada.

## Notes

- Línea base (T001, 2026-10-22): `python -m unittest discover -s tests` → 78 pruebas, OK.
- Tras implementar (T034, 2026-10-22): 124 pruebas (78 existentes + 46 de S02), OK. Ninguna prueba
  que pasaba antes falló.
- T035 (2026-10-22): `02_evidencia/registro_s02.json` y `.md` generados: 8 entradas «no consta» (el
  activo y 7 dominios), 0 hechos, 0 rechazos, estado «borrador», alcance no firmado, compuerta
  «cerrada». Motivos: 5 «compuerta cerrada», 1 «requiere solicitud documental», 2 «sin evidencia».
  Cero direcciones de red, puertos, comandos, credenciales y estados de cumplimiento. `scope/` y
  `02_evidencia/inventario.json` sin cambios.
- Implementación con el visto bueno del dueño a las decisiones (a)–(i) («continuar», 2026-10-22).
- Las tareas humanas (T038, T039) no las marca el agente.
- Las cinco decisiones propuestas por el agente en `spec.md` → Clarifications las aprueba el dueño
  antes de `/speckit-implement`.
- Commit después de cada historia, solo con aprobación del dueño.
- `/speckit-analyze` (2026-10-22): 0 críticos, 2 altos (I1 anulación de firma, I2 compuerta y
  determinismo), 4 medios (U1–U4) y 3 bajos (I3–I5). Corregidos en origen con aprobación del dueño:
  spec (FR-014, FR-015, FR-019, Clarifications f–i), data-model, research D6, esquema, plan y estas
  tareas (T010, T011, T014, T015, T016, T018, T023, T025, T028).

---

## Phase 8: Convergence

- [X] T040 Excluir de `no_consta_vigentes` en `platform/c4a/registro.py` las entradas «no consta» marcadas `descartada`, para que no se entreguen a S03 ni cuenten en la vista ni en `no_consta_al_firmar`, y probarlo en `platform/tests/test_registro_us4.py` (SC-010) per FR-019 (partial)
- [X] T041 En `registro.corregir` de `platform/c4a/registro.py`, rechazar con código 1 que una entrada sin evidencias citadas quede con resultado distinto de `no-ejecutado` o con una afirmación distinta de «no consta», y probarlo en `platform/tests/test_registro_us2.py` per FR-006 (partial)
- [X] T042 En `registro.aportar` de `platform/c4a/registro.py`, cuando la copia `evidence/registro_s02/<E-id>` ya existe, comprobar que su huella coincide con `sha256_original` antes de reutilizarla; si no coincide, rechazar con código 3 sin escribir, y probarlo en `platform/tests/test_registro_us4.py` per Constitution III / FR-008 (partial)
- [X] T043 Rechazar con código 1, en `aportar`, `corregir`, `descartar`, `restablecer`, `revisar` y `firmar` de `platform/c4a/registro.py`, los textos libres (afirmación, origen, motivo, valor) que contengan un estado de cumplimiento (`cumple`, `parcial`, `no-cumple`, `no-evaluado`, `no-aplica`), un número de puerto, una forma de comando o una forma de credencial, y probarlo en `platform/tests/test_registro_us1.py` (SC-005) per FR-011 / FR-012 (partial)
- [X] T044 Incluir el cambio de estado de firma del alcance de S01 entre los cambios que `abrir` advierte en `platform/c4a/registro.py`, y probarlo en `platform/tests/test_registro_us4.py` per Spec Edge Cases (alcance que se vuelve a firmar) / FR-015 (partial)

Resultado de la fase 8 (2026-10-22): 129 pruebas OK (78 existentes + 51 de S02). El registro real no cambió.
