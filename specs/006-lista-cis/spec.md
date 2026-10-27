# Feature Specification: S06 — La lista

**Feature Branch**: `006-lista-cis` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S06, La lista». Sexta épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S06 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, listaba los CIS Controls que aplican, partiendo
por el inventario. La herramienta deja **la lista**.

**Épica**: S06 de S01–S10. **Recibe**: la entrega de S05 (`perfil.entregar`): la lectura del
activo por las seis funciones del NIST CSF 2.0, con sus riesgos citados y sus vacíos. **Produce**:
la lista. **Entrega a S07 (El encargo)**: los CIS Controls v8.1 seleccionados como aplicables al
activo, cada uno con su justificación de aplicabilidad anclada en los hechos del inventario y del
perfil, con su estado de confirmación, para que S07 deje el mismo trabajo escrito para que una
herramienta lo repita.

**Lugar en el proceso de auditoría**: S06 corresponde a la fase Analizar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`03_hallazgos/`. La herramienta propone la aplicabilidad de cada control; el auditor la corrige y
firma. Una lista no dictamina: seleccionar un control como aplicable no dice que esté cumplido ni
incumplido.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S05 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S06 necesita un «mínimo de referencia» cuando falta el perfil de S05? → A: No. La lista se
  ancla en los hechos y riesgos citados; sin perfil no hay anclaje. Si falta la entrega de S05,
  `lista abrir` se detiene con el código 2 y no escribe nada.
- Q: ¿«Partiendo por el inventario» significa el archivo `02_evidencia/inventario.json`? → A: No.
  El inventario que manda es el del registro de S02: los hechos vigentes sobre el activo y sus
  dominios. El archivo previo corresponde a otra corrida y no acredita esta auditoría (principio
  III, como en S02).
- Q: ¿Un control seleccionado queda marcado como «aplica» para siempre? → A: No. La selección se
  justifica con los hechos vigentes; si el registro cambia y el anclaje cae, la fila se revisa.
  El auditor puede descartar un control con motivo (por ejemplo, no aplica a este activo); el
  descarte se guarda como decisión de aplicabilidad, no como estado de cumplimiento.
- Q: ¿Un control que requiere políticas, personas o procesos entra a la lista? → A: entra como
  pendiente, con la nota de solicitud documental; su aplicabilidad no se confirma con una prueba
  de red (sección «Marcos, estados y evidencia» de la constitución).
- Q: ¿Un identificador CIS que la herramienta no puede verificar? → A: queda «pendiente de
  confirmar», con la fuente que el auditor declare. No se inventa (principio IV); la versión es
  CIS Controls v8.1, y solo si no se obtiene se usa la v8, declarada.
- Evaluación de coherencia (2026-10-26): la lista hereda las marcas del perfil y de las citas; un
  riesgo con evidencia alterada no ancla aplicabilidad hasta que el auditor corrija.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir la lista sin perfil (Priority: P1) 🎯 MVP

El auditor abre la lista a partir de la entrega de S05. El perfil no existe: la herramienta se
detiene y lo informa, sin escribir nada. Si existe, la herramienta propone los CIS Controls
aplicables partiendo por el inventario: los hechos vigentes sobre el activo alimentan la
selección, cada control propuesto lleva su justificación de aplicabilidad anclada en hechos
concretos, su identificador en CIS Controls v8.1 y, si no consta verificable, «pendiente de
confirmar».

**Why this priority**: es el producto mínimo viable de S06. Partiendo por el inventario —no por
la memoria del auditor— deja la lista de controles que una corrida repetible debe verificar, que
es la entrada del encargo de S07.

**Independent Test**: con una entrega de S05 con hechos del activo en varios dominios, se
comprueba que cada control propuesto cita al menos un hecho del inventario o del perfil como
anclaje, que ningún control se propone sin justificación y que ningún archivo contiene estados de
cumplimiento.

**Acceptance Scenarios**:

1. **Given** una entrega con hechos del activo en varios dominios, **When** el auditor abre la
   lista, **Then** cada control propuesto lleva identificador (o «pendiente de confirmar»),
   justificación de aplicabilidad con al menos un hecho anclado y su referencia al perfil.
2. **Given** que la entrega de S05 no existe, **When** el auditor abre la lista, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `03_hallazgos/`.
3. **Given** un perfil firmado, **When** se abre la lista, **Then** el producto cita la huella de
   la entrega firmada de la que deriva y declara que el perfil está firmado.
4. **Given** una entrega con una función «no consta», **When** se abre la lista, **Then** ningún
   control se propone apoyado solo en esa función y el vacío se declara.

---

### User Story 2 - La herramienta propone la aplicabilidad y el auditor corrige (Priority: P2)

El auditor corrige la justificación de un control, descarta uno que no aplica al activo o
recupera uno descartado, con motivo; cada cambio queda en el historial con autor, fecha, valor
anterior y valor nuevo. Puede añadir un control a mano, con su justificación y su fuente. Revisa
el producto y lo firma; cualquier escritura posterior anula la firma. Firmar exige que cada
control seleccionado tenga justificación completa.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. La aplicabilidad de un control al activo es juicio del auditor; la
herramienta solo acelera el listado partiendo por el inventario.

**Independent Test**: con una lista propuesta, se comprueba que descartar un control con motivo
queda en el historial; que añadir uno a mano exige justificación y fuente; que firmar desde
«revisado» con firmante y justificación escribe la firma con la huella de los bytes guardados; y
que ningún camino llega a «firmado» sin la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** un control propuesto, **When** el auditor lo descarta con el motivo «no aplica a
   este activo», **Then** el cambio queda registrado con autor, fecha, valor anterior, valor
   nuevo y motivo, y el control deja de estar seleccionado sin borrarse.
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y la lista no se
   modifica.
3. **Given** un producto revisado cuyos controles seleccionados tienen justificación, **When** el
   auditor firma con su nombre y una justificación, **Then** el producto queda «firmado» con la
   huella de sus bytes guardados; cualquier cambio posterior anula la firma.
4. **Given** un control seleccionado sin justificación, **When** se intenta firmar, **Then** la
   firma se rechaza informando qué controles faltan por completar.
5. **Given** un control descartado, **When** el auditor lo recupera con motivo, **Then** vuelve a
   la selección y la historia conserva el descarte y la recuperación.

---

### User Story 3 - Un control que requiere solicitud documental queda pendiente (Priority: P3)

Un control seleccionable solo se puede confirmar con políticas, personas o procesos: la prueba de
red no alcanza. La fila se conserva como pendiente, con la nota de solicitud documental y el
hecho del inventario que la motiva. No se confirma, no se borra y no se presenta como cubierta.

**Why this priority**: protege la sección «Marcos, estados y evidencia» de la constitución: un
control que requiere políticas, personas o procesos no se acredita con una prueba de red. La
diferencia entre «aplica, pendiente documental» y «aplica, confirmado» es trabajo del auditor,
no de la herramienta.

**Independent Test**: con hechos que motivan controles de ambos tipos, se comprueba que los
controles documentales quedan «pendiente» con su nota, que el conteo de pendientes aparece en una
sola sección y que ningún archivo presenta un pendiente como cumplido.

**Acceptance Scenarios**:

1. **Given** un control cuya confirmación exige políticas, personas o procesos, **When** se abre
   la lista, **Then** queda «pendiente» con la nota de solicitud documental y el hecho que lo
   motiva.
2. **Given** un control «pendiente», **When** el auditor aporta la evidencia documental
   correspondiente (en el registro de S02), **Then** la fila deja de depender de la solicitud y
   el estado se actualiza con el cambio anotado en el historial.
3. **Given** cualquier fila, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta un control
   pendiente como cubierto.
4. **Given** un producto con P controles «pendiente», **When** se resume, **Then** el resumen
   dice cuántos controles están seleccionados y cuántos pendientes, en una sola sección con su
   conteo.

---

### User Story 4 - Verificar la consistencia con el perfil y entregar a S07 (Priority: P3)

El auditor verifica el producto: la huella de los bytes guardados sigue correspondiendo a la
firma, la huella de la entrega de S05 sigue siendo la registrada y cada hecho ancla sigue
coincidiendo con su evidencia guardada. Si el perfil cambió después de firmar, la herramienta no
actualiza sola. La entrega a S07 contiene exactamente los controles seleccionados con sus
justificaciones y sus estados.

**Why this priority**: es el contrato con S05 y el principio III: una lista solo acredita si los
hechos que anclan sus controles siguen en pie. Es también la entrada del encargo de S07.

**Independent Test**: con un producto firmado, se altera un byte de una evidencia ancla y otro del
JSON de la lista, y se comprueba que `verificar` lo detecta; se cambia el perfil de origen y se
comprueba que `abrir` informa y, estando firmado, no escribe; se comprueba que `entregar`
devuelve solo los seleccionados.

**Acceptance Scenarios**:

1. **Given** una justificación anclada en un hecho cuya evidencia ya no corresponde a su huella,
   **When** se verifica, **Then** el control se informa con «evidencia alterada» y queda fuera de
   la entrega a S07 hasta que el auditor corrija.
2. **Given** un producto firmado cuyo perfil de origen cambió, **When** se abre de nuevo, **Then**
   la herramienta informa el cambio y no escribe (código 4).
3. **Given** un hecho ancla que ya no está en la entrega del perfil, **When** se verifica, **Then**
   el control se informa con «ancla no vigente».
4. **Given** un producto con controles seleccionados, descartados y pendientes, **When** se
   entrega a S07, **Then** la entrega contiene exactamente los seleccionados, con justificación,
   estado (confirmado / pendiente-confirmar / pendiente-documental) y las huellas de sus anclas.

---

## Edge Cases

- El perfil de S05 no existe: `abrir` termina en código 2 sin escribir.
- La entrega tiene cero hechos del activo: la lista se propone solo desde el alcance y lo declara;
  si no hay anclaje posible, se informa y el auditor decide a mano, con justificación.
- El mismo control se propone desde dos funciones del perfil: la fila es una sola, con ambos
  anclajes.
- Un identificador CIS no verificable: queda «pendiente de confirmar» con la fuente declarada; no
  se inventa.
- El perfil cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4 («el
  perfil de origen cambió»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- Un control descartado por «no aplica a este activo» reaparece propuesto en una apertura nueva:
  queda descartado con su motivo; la historia no se pierde.
- El JSON de la lista se altera un byte después de firmar: `verificar` lo detecta.
- Un control añadido a mano sin fuente: se rechaza hasta que el auditor la complete.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir la lista a partir de la entrega vigente de S05
  (`perfil.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar si el perfil está firmado.
- **FR-003**: La herramienta MUST proponer los CIS Controls aplicables partiendo por el inventario:
  los hechos vigentes del registro de S02, organizados por el perfil de S05. Cada control
  propuesto MUST citar al menos un hecho ancla (o declarar que se añade a mano).
- **FR-004**: Cada fila MUST tener: identificador del control en CIS Controls v8.1 (o «pendiente
  de confirmar»), justificación de aplicabilidad, anclajes (hechos y sección del perfil), estado
  de aplicabilidad (`propuesto`, `seleccionado`, `descartado`), estado de confirmación
  (`confirmado`, `pendiente-confirmar`, `pendiente-documental`), evidencias citadas (tipo,
  ubicación, huellas), estado de aprobación (`borrador`, `revisado`, `firmado`), marcas y su
  historial de cambios.
- **FR-005**: Los identificadores MUST citarse con marco, versión e identificador; solo si la
  v8.1 no se obtiene se usa la v8, y se declara. La herramienta MUST NOT inventar identificadores
  (principio IV).
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. Seleccionar un
  control MUST NOT presentarse como prueba de incumplimiento ni de cobertura.
- **FR-007**: El auditor MUST poder corregir la justificación de cualquier fila, descartarla y
  recuperarla, y añadir controles a mano con justificación y fuente. Cada corrección, descarte o
  recuperación registra autor, fecha, valor anterior, valor nuevo y motivo obligatorio, y deja la
  fila en «revisado». Ninguna fila se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que cada control seleccionado tenga justificación
  completa, y MUST rechazar firmar desde «borrador» o sin firmante o sin justificación. Firmar la
  lista MUST NOT abrir la compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S05 contra la registrada; y la huella de cada
  evidencia ancla contra su copia guardada. MUST detectar la alteración de un byte y MUST
  informar «evidencia alterada» y «ancla no vigente» por fila.
- **FR-010**: Con la misma entrega de S05 y las mismas correcciones, la herramienta MUST producir
  el mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `03_hallazgos/`, sin crear
  un árbol paralelo ni sobrescribir los productos previos de esa carpeta (`README.md`,
  `matriz_cumplimiento.csv`, `enunciado-*.md`, `cita-*.md`, `perfil-*.md`), y ser legible por un
  tercero sin la herramienta.
- **FR-012**: Por cada fila MUST escribirse una ficha legible `03_hallazgos/lista-<id>.md` con el
  mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST entregar a S07 los controles seleccionados: los no descartados,
  cuyos anclajes siguen vigentes y sin evidencia alterada; cada uno con identificador (o su
  pendiente), justificación, estado de confirmación y las huellas de sus evidencias, e indicar si
  el producto está firmado.
- **FR-014**: Si el perfil de origen cambió (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor MUST exigir que el perfil de origen no haya cambiado desde
  `abrir`; si cambió, se rechazan con código 4 sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija.

### Key Entities

- **Lista**: producto de S06. Referencia la entrega del perfil de la que deriva (huella y estado
  de firma). Agrupa las filas de control, los conteos, el estado de aprobación, el historial y la
  firma.
- **Fila de control**: un CIS Controls v8.1 ante el activo. Tiene identificador (o pendiente),
  justificación de aplicabilidad, anclajes en hechos y en sección del perfil, estados de
  aplicabilidad y de confirmación, evidencias citadas, estado de aprobación, marcas y
  correcciones.
- **Ancla**: hecho del inventario (registro de S02) o sección del perfil (S05) que justifica la
  aplicabilidad de un control.
- **Corrección**: autor, fecha, fila afectada, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con hechos en varios dominios, el 100 % de los controles
  propuestos citan al menos un hecho ancla o declaran que se añaden a mano.
- **SC-002**: El 100 % de las filas citan la huella de la entrega de S05 y declaran si está
  firmada.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-004**: La alteración de un solo byte del JSON del producto se detecta en el 100 % de los
  casos (`verificar`).
- **SC-005**: La alteración de un solo byte de una evidencia ancla deja su fila «evidencia
  alterada» y fuera de la entrega a S07; con firma válida, el estado informado es «firmado con
  evidencia alterada».
- **SC-006**: Ninguna fila llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones, descartes y recuperaciones registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: El auditor identifica todo lo pendiente en menos de 10 minutos: por fila en su
  campo y los pendientes en una sola sección con conteo. Verificación automática: existe la
  sección y su conteo coincide; verificación manual: el auditor mide y registra el tiempo.
- **SC-009**: La entrega a S07 contiene exactamente los controles seleccionados de FR-013 y
  ninguno descartado, con ancla no vigente o con evidencia alterada.
- **SC-010**: Abrir y corregir la lista solo crean archivos nuevos en `03_hallazgos/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-011**: El 100 % de los controles que requieren políticas, personas o procesos quedan
  «pendiente-documental» con su nota (FR-013 de la sección «Marcos, estados y evidencia»).
- **SC-012**: Un tercero recorre una fila hasta sus anclas, sus hechos y sus evidencias y
  comprueba una huella sin ayuda; el resultado se registra en el checklist humano.
- **SC-013**: Con el producto firmado y el perfil cambiado, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: como en S02–S05, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S06 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S05 y de la constitución (principios I, II, III y IV).
- La fuente del marco es la oficial del CIS (constitución, IV): CIS Controls v8.1; la v8 solo si
  la v8.1 no se obtiene, y se declara.
- Hay un solo rol humano, el auditor, que corrige y firma, como en los sprints anteriores. La
  revisión por segundo par (#33) queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S06 no recolecta material nuevo, no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la
  entrega de S05 (y a través de ella el registro) y escribe en `03_hallazgos/`.
- El «inventario» es el conjunto de hechos vigentes sobre el activo en el registro de S02, no el
  archivo previo `02_evidencia/inventario.json`, que corresponde a otra corrida.
- **Dependencias**: la entrega de S05 (`perfil.entregar`, FR-013 de S05); la entrega de S02 para
  los hechos ancla; `alcance.serializar`, `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: el encargo (S07), las dos frases (S08), el borrador (S09) y el
  cierre (S10); medir cobertura del marco CIS (si se calculara, numerador, denominador y
  pendientes, sin extrapolar); ejecutar verificación alguna sobre el objetivo.
