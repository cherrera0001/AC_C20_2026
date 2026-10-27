# Feature Specification: S05 — El perfil

**Feature Branch**: `005-perfil-nist` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S05, El perfil». Quinta épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S05 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, leía el mismo activo con las seis funciones del
NIST CSF 2.0 (Gobernar, Identificar, Proteger, Detectar, Responder, Recuperar). La herramienta
deja **el perfil**.

**Épica**: S05 de S01–S10. **Recibe**: la entrega de S04 (`cita.entregar`): los riesgos citados
en un marco, con sus hechos de origen, sus evidencias con huella y el estado de sus
identificadores. **Produce**: el perfil. **Entrega a S06 (La lista)**: la lectura del mismo
activo organizada por las seis funciones del NIST CSF 2.0, cada función con sus riesgos citados,
sus vacíos y lo que falta, para que S06 liste los CIS Controls que aplican partiendo por el
inventario.

**Lugar en el proceso de auditoría**: S05 corresponde a la fase Analizar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`03_hallazgos/`. La herramienta propone la organización por funciones; el auditor la corrige y
firma. Un perfil no dictamina: ordena lo ya registrado y citado, no evalúa controles.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S04 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S05 necesita un «mínimo de referencia» cuando falta la cita de S04? → A: No. Sin riesgos
  citados no hay materia prima para perfilar. Si falta la entrega de S04, `perfil abrir` se
  detiene con el código 2 y no escribe nada (mismo criterio que S03 y S04).
- Q: ¿Un riesgo citado solo en CIS (sin función NIST evidente) entra al perfil? → A: Sí, la
  herramienta propone una función a partir del dominio y el fundamento de la cita; el auditor
  puede moverlo a otra función o asignarle una segunda función, con motivo. Un riesgo puede
  informar más de una función.
- Q: ¿Una función sin ningún riesgo queda «cumple»? → A: No. Queda declarada como vacío
  («no consta» para esa función), con su conteo. «Sin riesgos en la función» MUST NOT presentarse
  como cumplimiento (principio II).
- Q: ¿El perfil cita los vacíos heredados? → A: Sí, agrupados por función cuando se puede
  derivar su función, y en una sección común cuando no; cada uno con su origen (compuerta
  cerrada, solicitud documental, alcance pendiente).
- Q: ¿El perfil introduce material nuevo sobre el activo? → A: No. Solo organiza lo registrado
  (S02), enunciado (S03) y citado (S04); no recolecta ni infiere hechos nuevos.
- Evaluación de coherencia (2026-10-26): el perfil hereda las marcas de las citas (evidencia
  alterada, riesgo no vigente, identificador pendiente); una cita marcada no acredita su función
  hasta que el auditor corrija.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el perfil sin cita (Priority: P1) 🎯 MVP

El auditor abre el perfil a partir de la entrega de S04. La cita no existe: la herramienta se
detiene y lo informa, sin escribir nada. Si existe, la herramienta propone una sección por cada
una de las seis funciones del NIST CSF 2.0 —Gobernar, Identificar, Proteger, Detectar, Responder,
Recuperar— con los riesgos citados que propone asignar a cada una, sus vacíos y lo que falta,
citando siempre la huella de la entrega de la que deriva.

**Why this priority**: es el producto mínimo viable de S05. Aun sin añadir material nuevo, deja
la lectura del activo por las seis funciones, que es la forma en que la gerencia y los marcos
entienden el resultado; es la entrada de S06.

**Independent Test**: con una entrega de S04 con C citas vigentes y V vacíos heredados, se
comprueba que el perfil tiene seis secciones, que entre todas citan exactamente las C citas (o
las informan como no asignadas), que los V vacíos quedan listados y que ningún archivo contiene
estados de cumplimiento.

**Acceptance Scenarios**:

1. **Given** una entrega con C citas vigentes y V vacíos heredados, **When** el auditor abre el
   perfil, **Then** hay seis secciones —una por función del NIST CSF 2.0— cada una con sus
   riesgos citados propuestos, sus vacíos y lo que falta, y los V vacíos quedan listados.
2. **Given** que la entrega de S04 no existe, **When** el auditor abre el perfil, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `03_hallazgos/`.
3. **Given** una cita firmada, **When** se abre el perfil, **Then** el producto cita la huella de
   la entrega firmada de la que deriva y declara que la cita está firmada.
4. **Given** una entrega donde una cita fue descartada o tiene evidencia alterada, **When** se
   abre el perfil, **Then** esa cita no se asigna a función alguna como vigente y su marca se
   informa.

---

### User Story 2 - La herramienta propone la función y el auditor corrige (Priority: P2)

El auditor corrige la síntesis de una función, mueve un riesgo citado a otra función o le asigna
una función adicional, con motivo; la corrección queda en el historial con autor, fecha, valor
anterior y valor nuevo. Revisa el producto y lo firma; cualquier escritura posterior anula la
firma. Firmar exige que las seis secciones tengan su síntesis completada por el auditor.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. La asignación riesgo ↔ función es juicio del auditor; la herramienta solo
acelera el ordenamiento.

**Independent Test**: con un perfil propuesto, se comprueba que mover un riesgo citado a otra
función con motivo queda en el historial; que una síntesis corregida deja la sección «revisada»;
que firmar desde «revisado» con firmante y justificación escribe la firma con la huella de los
bytes guardados; y que ningún camino llega a «firmado» sin la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** un riesgo citado asignado a Proteger, **When** el auditor lo mueve a Detectar con un
   motivo, **Then** el cambio queda registrado con autor, fecha, valor anterior, valor nuevo y
   motivo, y la sección afectada pasa a «revisada».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y el perfil no se
   modifica.
3. **Given** un producto revisado cuyas seis secciones tienen síntesis completas, **When** el
   auditor firma con su nombre y una justificación, **Then** el producto queda «firmado» con la
   huella de sus bytes guardados; cualquier cambio posterior anula la firma.
4. **Given** una sección con la síntesis vacía, **When** se intenta firmar, **Then** la firma se
   rechaza informando qué secciones faltan por completar.
5. **Given** un riesgo citado que el auditor considera fuera de toda función, **When** lo deja sin
   asignar con motivo, **Then** queda listado como «no asignado» y la historia conserva la
   decisión.

---

### User Story 3 - Una función sin material no es un cumplimiento (Priority: P3)

Una función del perfil no tiene riesgos citados: no hubo hechos en ese dominio o la evidencia no
consta. La sección queda con su vacío declarado («no consta» para esa función), con el motivo
heredado (compuerta cerrada, solicitud documental, alcance pendiente). No se rellena, no se
borra y no se presenta como «sin hallazgos» ni «cumple».

**Why this priority**: protege la diferencia entre «no hay riesgos observados en la función» y «la
función está gobernada». Esa diferencia es la que el dictamen humano, no la herramienta, debe
decidir (principio II).

**Independent Test**: con hechos y vacíos heredados de causas distintas, se comprueba que cada
función sin material lleva su vacío con motivo, que el conteo de vacíos aparece en una sola
sección y que una búsqueda sobre los archivos generados no encuentra estados de cumplimiento ni
la frase «sin hallazgos».

**Acceptance Scenarios**:

1. **Given** una función sin riesgos citados por compuerta cerrada, **When** se abre el perfil,
   **Then** la sección declara «no consta» con el motivo «compuerta cerrada» heredado del
   registro.
2. **Given** una función que requiere políticas, personas o procesos, **When** se abre el perfil,
   **Then** la sección declara «no consta» con la nota de solicitud documental.
3. **Given** cualquier sección, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta una función vacía
   como «sin hallazgos».
4. **Given** un producto con F funciones sin material, **When** se resume, **Then** el resumen
   dice cuántas funciones tienen material y cuántas quedan «no consta», en una sola sección con
   su conteo.

---

### User Story 4 - Verificar la consistencia con la cita y entregar a S06 (Priority: P3)

El auditor verifica el producto: la huella de los bytes guardados sigue correspondiendo a la
firma, la huella de la entrega de S04 sigue siendo la registrada, y cada evidencia citada sigue
coincidiendo con su copia guardada. Si la cita cambió después de firmar, la herramienta no
actualiza sola. La entrega a S06 contiene exactamente las seis secciones con sus riesgos citados
vigentes y sus vacíos.

**Why this priority**: es el contrato con S04 y el principio III: un perfil solo acredita si las
citas y evidencias de las que se alimenta siguen en pie. Es también la entrada de la lista CIS
de S06.

**Independent Test**: con un producto firmado, se altera un byte de una evidencia copiada y otro
del JSON del perfil, y se comprueba que `verificar` lo detecta; se cambia la cita de origen y se
comprueba que `abrir` informa y, estando firmado, no escribe; se comprueba que `entregar`
devuelve las seis secciones completas.

**Acceptance Scenarios**:

1. **Given** una sección que cita una evidencia cuya copia ya no corresponde a la huella
   registrada, **When** se verifica, **Then** el riesgo citado se informa con «evidencia
   alterada» y deja de acreditar su función.
2. **Given** un producto firmado cuya cita de origen cambió, **When** se abre de nuevo, **Then**
   la herramienta informa el cambio y no escribe (código 4).
3. **Given** un riesgo citado que ya no está en la entrega de S04, **When** se verifica, **Then**
   se informa «riesgo no vigente» y la sección queda marcada.
4. **Given** un producto con secciones completas, **When** se entrega a S06, **Then** la entrega
   contiene las seis funciones con sus riesgos citados vigentes (con marco, versión e
   identificador o su pendiente), sus vacíos con motivo y las huellas de sus evidencias.

---

## Edge Cases

- La cita de S04 no existe: `abrir` termina en código 2 sin escribir.
- La entrega tiene cero citas: el perfil tiene seis secciones «no consta» y lista los vacíos; la
  vista lo dice así, sin «sin hallazgos».
- Un riesgo citado en un marco sin correspondencia NIST clara: la herramienta propone función a
  partir del dominio y el fundamento de la cita; el auditor decide con motivo; puede quedar «no
  asignado», declarado.
- La cita cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4 («la
  cita de origen cambió»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- La evidencia citada es una referencia sin copia (heredada de S02): la sección lo declara y lo
  que falta incluye verificar el original.
- El JSON del perfil se altera un byte después de firmar: `verificar` lo detecta.
- Un vacío heredado no tiene función derivable: queda en la sección común de vacíos con su motivo
  original.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el perfil a partir de la entrega vigente de S04
  (`cita.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar si la cita está firmada.
- **FR-003**: El perfil MUST tener exactamente seis secciones, una por función del NIST CSF 2.0:
  Gobernar, Identificar, Proteger, Detectar, Responder y Recuperar, en ese orden.
- **FR-004**: Cada sección MUST tener: función, síntesis, riesgos citados asignados (cada uno con
  su cita, marco, versión e identificador o su pendiente), vacíos con su motivo, «lo que falta»
  (lista), evidencias citadas (tipo, ubicación, huellas), estado de aprobación (`borrador`,
  `revisado`, `firmado`), marcas y su historial de cambios.
- **FR-005**: La herramienta MUST proponer la asignación riesgo ↔ función a partir del dominio, el
  resultado técnico del hecho de origen y el fundamento de la cita. El auditor MUST poder mover un
  riesgo a otra función, asignarle funciones adicionales o dejarlo «no asignado», siempre con
  motivo. Un riesgo puede informar más de una función.
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. Una función sin
  material MUST declararse «no consta» con su motivo, nunca «sin hallazgos» ni «cumple».
- **FR-007**: El auditor MUST poder corregir la síntesis de cualquier sección y reasignar sus
  riesgos citados. Cada corrección o reasignación registra autor, fecha, valor anterior, valor
  nuevo y motivo obligatorio, y deja la sección en «revisado». Ningún dato se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que la síntesis de las seis secciones esté completada
  por el auditor, y MUST rechazar firmar desde «borrador» o sin firmante o sin justificación.
  Firmar el perfil MUST NOT abrir la compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S04 contra la registrada; y la huella de cada
  evidencia citada contra su copia guardada (o su original cuando es referencia sin copia). MUST
  detectar la alteración de un byte y MUST informar «evidencia alterada» y «riesgo no vigente»
  por sección.
- **FR-010**: Con la misma entrega de S04 y las mismas correcciones, la herramienta MUST producir
  el mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `03_hallazgos/`, sin crear
  un árbol paralelo ni sobrescribir los productos previos de esa carpeta (`README.md`,
  `matriz_cumplimiento.csv`, `enunciado-*.md`, `cita-*.md`), y ser legible por un tercero sin la
  herramienta.
- **FR-012**: Por cada sección MUST escribirse una ficha legible `03_hallazgos/perfil-<funcion>.md`
  con el mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST entregar a S06 las seis secciones con sus riesgos citados
  vigentes (los no descartados, cuyo riesgo sigue en la entrega y sin evidencia alterada), sus
  vacíos con motivo y las huellas de sus evidencias, e indicar si el producto está firmado.
- **FR-014**: Si la cita de origen cambió (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor MUST exigir que la cita de origen no haya cambiado desde
  `abrir`; si cambió, se rechazan con código 4 sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija.

### Key Entities

- **Perfil**: producto de S05. Referencia la entrega de la cita de la que deriva (huella y
  estado de firma). Agrupa las seis secciones, los vacíos, los riesgos «no asignados», el estado
  de aprobación, el historial y la firma.
- **Sección de función**: una por función del NIST CSF 2.0. Tiene función, síntesis, riesgos
  citados asignados, vacíos con motivo, «lo que falta», evidencias citadas, estado de aprobación,
  marcas y correcciones.
- **Asignación**: vínculo riesgo citado ↔ función, propuesto por la herramienta y decidido por el
  auditor; puede ser múltiple y puede quedar «no asignado», declarado.
- **Vacío**: ausencia de material para una función, con el motivo heredado (compuerta cerrada,
  solicitud documental, alcance pendiente); no es un cumplimiento.
- **Corrección**: autor, fecha, sección afectada, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con C citas vigentes y V vacíos heredados, el perfil tiene
  seis secciones, lista los V vacíos con motivo y cada cita vigente aparece en al menos una
  sección o queda «no asignada» declarada.
- **SC-002**: El 100 % de las secciones citan la huella de la entrega de S04 y declaran si está
  firmada.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-004**: La alteración de un solo byte del JSON del producto se detecta en el 100 % de los
  casos (`verificar`).
- **SC-005**: La alteración de un solo byte de una evidencia citada deja su riesgo «evidencia
  alterada» y la sección deja de acreditarlo; con firma válida, el estado informado es «firmado
  con evidencia alterada».
- **SC-006**: Ninguna sección llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones y reasignaciones registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: El auditor identifica todo lo que falta en menos de 10 minutos: por sección en su
  campo y los vacíos en una sola sección con conteo. Verificación automática: existe la sección y
  su conteo coincide; verificación manual: el auditor mide y registra el tiempo.
- **SC-009**: La entrega a S06 contiene exactamente las seis secciones con los riesgos citados
  vigentes de FR-013 y ninguno descartado, con riesgo no vigente o con evidencia alterada.
- **SC-010**: Abrir y corregir el perfil solo crean archivos nuevos en `03_hallazgos/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-011**: Una función sin material lleva «no consta» con su motivo en el 100 % de los casos
  (FR-006).
- **SC-012**: Un tercero recorre una sección hasta sus riesgos citados, sus hechos y sus
  evidencias y comprueba una huella sin ayuda; el resultado se registra en el checklist humano.
- **SC-013**: Con el producto firmado y la cita cambiada, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: como en S02–S04, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S05 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S04 y de la constitución (principios I, II, III y IV).
- Las seis funciones son las del NIST CSF 2.0, con sus nombres en castellano de la constitución
  (IV): Gobernar, Identificar, Proteger, Detectar, Responder y Recuperar.
- Hay un solo rol humano, el auditor, que corrige y firma, como en los sprints anteriores. La
  revisión por segundo par (#33) queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S05 no recolecta material nuevo, no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la
  entrega de S04 y escribe en `03_hallazgos/`.
- El perfil es una lectura organizada: no introduce hechos, riesgos ni controles que no consten
  en las entregas anteriores.
- **Dependencias**: la entrega de S04 (`cita.entregar`, FR-013 de S04) y su modelo; el registro de
  S02 para los motivos de los vacíos; `alcance.serializar`, `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: la lista CIS (S06), el encargo (S07), las dos frases (S08), el
  borrador (S09) y el cierre (S10); evaluar controles NIST por categorías y subcategorías (el
  perfil trabaja a nivel función, que es la granularidad de la fila S05); emitir cualquier
  dictamen de cumplimiento.
