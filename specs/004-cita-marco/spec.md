# Feature Specification: S04 — La cita

**Feature Branch**: `004-cita-marco` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S04, La cita». Cuarta épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S04 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, ubicaba ese riesgo en un marco, con nombre y
versión. La herramienta deja **la cita**.

**Épica**: S04 de S01–S10. **Recibe**: la entrega de S03 (`enunciado.entregar`): los riesgos
enunciados vigentes, cada uno con su hecho de origen, su evidencia con huella y sus campos de
criterio, impacto y lo que falta, más la lista de vacíos heredados y el estado de firma del
enunciado. **Produce**: la cita. **Entrega a S05 (El perfil)**: los riesgos citados en un marco,
cada uno con marco, versión e identificador de control (o «pendiente de confirmar»), junto con
sus hechos y evidencias con huella, para que S05 lea el mismo activo con las seis funciones del
NIST CSF 2.0.

**Lugar en el proceso de auditoría**: S04 corresponde a la fase Analizar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`03_hallazgos/`. La herramienta propone la correspondencia riesgo ↔ control; el auditor la
corrige y la firma. Una cita no dictamina: ubicar un riesgo en un control no concluye
cumplimiento, y la correspondencia es una sugerencia explicada, nunca prueba (principio IV).

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S03 aún no está implementada (spec y tareas listas, código pendiente).
El dueño ordenó «construye la herramienta» (2026-10-26); esta spec se escribe con esa orden
expresa y con la implementación de S03 aún abierta. La desviación queda registrada aquí y en
`tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S04 necesita un «mínimo de referencia» como S02 cuando falta el producto anterior? → A: No.
  S02 podía derivar el alcance de `scope/alcance.md`; S04 no puede citar riesgos que no existen.
  Si falta la entrega de S03, `cita abrir` se detiene con el código 2 y no escribe nada (mismo
  criterio que S03 con el registro de S02).
- Q: ¿Qué marcos puede proponer la herramienta? → A: solo los de la constitución (IV): ISO/IEC
  27001:2022, NIST CSF 2.0 y CIS Controls v8.1 (la v8 solo si la v8.1 no se obtiene, y se
  declara). Un marco mencionado no acredita cobertura.
- Q: ¿Un identificador de control que la herramienta no puede verificar? → A: queda «pendiente
  de confirmar», registrando la fuente que el auditor declare si la aporta. No se inventa
  (principio IV). El estado del identificador (confirmado / pendiente) viaja con la cita.
- Q: ¿Una cita propone un único control por riesgo? → A: propone una correspondencia principal;
  el auditor puede añadir correspondencias adicionales con motivo. Cada correspondencia lleva su
  fundamento.
- Q: ¿El auditor puede citar un marco fuera de los tres de la constitución? → A: la herramienta
  no lo propone; si el auditor lo escribe, se registra como su aporte, con fuente declarada y
  estado «pendiente de confirmar».
- Evaluación de coherencia (2026-10-26): la cita hereda las marcas del enunciado (descartado,
  evidencia alterada, hecho no vigente); un riesgo marcado no genera cita vigente y sus marcas se
  informan. Los vacíos heredados de S03 viajan como contexto, sin cita.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir la cita sin enunciado (Priority: P1) 🎯 MVP

El auditor abre la cita a partir de la entrega de S03. El enunciado no existe: la herramienta se
detiene y lo informa, sin escribir nada. Si existe, la herramienta propone una cita por cada
riesgo vigente: el marco y el control como sugerencia explicada, el identificador solo si consta
en su base (si no, «pendiente de confirmar»), citando siempre el riesgo de origen y la huella de
la entrega de la que deriva; los vacíos heredados se listan sin cita.

**Why this priority**: es el producto mínimo viable de S04. Sin escribir un dictamen, ubica cada
riesgo en un marco con nombre y versión y deja explícito qué identificadores faltan por
confirmar, que es la materia prima del perfil de S05.

**Independent Test**: con una entrega de S03 con R riesgos vigentes y V vacíos heredados, se
comprueba que hay exactamente R citas y V vacíos listados, que cada cita cita su riesgo y la
huella de la entrega, y que ningún archivo contiene estados de cumplimiento.

**Acceptance Scenarios**:

1. **Given** una entrega con R riesgos vigentes y V vacíos heredados, **When** el auditor abre la
   cita, **Then** hay exactamente R citas propuestas, cada una con marco, versión, control
   sugerido con su fundamento e identificador confirmado o «pendiente de confirmar», y los V
   vacíos quedan listados sin cita.
2. **Given** que la entrega de S03 no existe, **When** el auditor abre la cita, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `03_hallazgos/`.
3. **Given** un enunciado firmado, **When** se abre la cita, **Then** el producto cita la huella
   de la entrega firmada de la que deriva y declara que el enunciado está firmado.
4. **Given** una entrega donde un riesgo fue descartado o tiene evidencia alterada, **When** se
   abre la cita, **Then** ese riesgo no genera cita vigente y su marca se informa.

---

### User Story 2 - La herramienta propone la correspondencia y el auditor corrige (Priority: P2)

El auditor corrige el marco, la versión, el identificador o el fundamento de una cita, con
motivo; la corrección queda en el historial con autor, fecha, valor anterior y valor nuevo. Puede
añadir una correspondencia adicional, descartar una cita y restablecerla. Revisa el producto y lo
firma; cualquier escritura posterior anula la firma. Firmar exige que cada cita vigente tenga
marco y versión completos.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. Sin esta historia, la cita sería una conclusión automática del propio motor
que propone.

**Independent Test**: con una cita propuesta, se comprueba que corregir el identificador con
motivo queda en el historial y deja la cita «revisada»; que añadir una correspondencia adicional
registra su fundamento; que descartar y restablecer funcionan con motivo; que firmar desde
«revisado» con firmante y justificación escribe la firma con la huella de los bytes guardados; y
que ningún camino llega a «firmado» sin la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** una cita propuesta, **When** el auditor corrige el identificador de control con un
   motivo, **Then** el cambio queda registrado con autor, fecha, valor anterior, valor nuevo y
   motivo, y la cita pasa a «revisada».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y la cita no se
   modifica.
3. **Given** un producto revisado cuyas citas vigentes tienen marco y versión, **When** el
   auditor firma con su nombre y una justificación, **Then** el producto queda «firmado» con la
   huella de sus bytes guardados; cualquier cambio posterior anula la firma.
4. **Given** una cita vigente sin marco, **When** se intenta firmar, **Then** la firma se rechaza
   informando qué citas faltan por completar.
5. **Given** una cita descartada, **When** el auditor la restablece con motivo, **Then** vuelve a
   la entrega y la historia conserva el descarte y el restablecimiento.

---

### User Story 3 - Un identificador no consta y la fila se conserva (Priority: P3)

El marco y la versión constan, pero el identificador del control no se puede verificar contra la
guía ni contra la norma abierta. La cita se conserva con el identificador en «pendiente de
confirmar», con la fuente que el auditor declare si la aporta. La fila no se borra, no se
rellena con un identificador inventado y viaja a S05 marcada como pendiente.

**Why this priority**: protege el principio IV: un control se cita con marco, versión e
identificador, y lo que no consta queda pendiente, no inventado. Es la diferencia entre una cita
verificable y una que solo parece completa.

**Independent Test**: con riesgos cuyo control sugerido no tiene identificador verificable, se
comprueba que sus citas quedan «pendiente de confirmar», que el conteo de pendientes aparece en
una sola sección y que ningún archivo generado afirma el cumplimiento del control citado.

**Acceptance Scenarios**:

1. **Given** un riesgo cuyo control sugerido no tiene identificador verificable, **When** se
   abre la cita, **Then** el identificador queda «pendiente de confirmar» y la cita sigue
   vigente con su fundamento.
2. **Given** una cita «pendiente de confirmar», **When** el auditor aporta la fuente del
   identificador, **Then** la fuente queda registrada con autor y fecha, y el identificador sigue
   «pendiente de confirmar» hasta su verificación.
3. **Given** cualquier cita, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta la cita como
   prueba de incumplimiento.
4. **Given** un producto con P citas «pendiente de confirmar», **When** se resume, **Then** el
   resumen dice cuántas citas hay y cuántas pendientes, en una sola sección con su conteo.

---

### User Story 4 - Verificar la consistencia con el enunciado y entregar a S05 (Priority: P3)

El auditor verifica el producto: la huella de los bytes guardados sigue correspondiendo a la
firma, la huella de la entrega de S03 sigue siendo la registrada, y cada evidencia citada sigue
coincidiendo con su copia guardada. Si el enunciado cambió después de firmar, la herramienta no
actualiza sola. La entrega a S05 contiene exactamente las citas vigentes, con sus marcas de
identificador.

**Why this priority**: es el contrato con S03 y el principio III: una cita solo acredita si su
riesgo de origen y sus evidencias siguen en pie. Es también la entrada del perfil de S05.

**Independent Test**: con un producto firmado, se altera un byte de una evidencia copiada y otro
del JSON de la cita, y se comprueba que `verificar` lo detecta; se cambia el enunciado de origen
y se comprueba que `abrir` informa y, estando firmado, no escribe; se comprueba que `entregar`
devuelve solo las citas vigentes.

**Acceptance Scenarios**:

1. **Given** una cita que cita una evidencia cuya copia ya no corresponde a la huella
   registrada, **When** se verifica, **Then** la cita se informa con «evidencia alterada» y deja
   de entrar en la entrega a S05.
2. **Given** un producto firmado cuyo enunciado de origen cambió, **When** se abre de nuevo,
   **Then** la herramienta informa el cambio y no escribe (código 4).
3. **Given** un riesgo que ya no está en la entrega del enunciado, **When** se verifica, **Then**
   la cita se informa con «riesgo no vigente».
4. **Given** un producto con citas vigentes, descartadas y con inconsistencias, **When** se
   entrega a S05, **Then** la entrega contiene exactamente las vigentes, con marco, versión,
   identificador (o su pendiente), fundamento y las huellas de sus evidencias.

---

## Edge Cases

- El enunciado de S03 no existe: `abrir` termina en código 2 sin escribir.
- La entrega tiene cero riesgos: el producto tiene cero citas y lista los vacíos heredados; la
  vista lo dice así, sin «sin hallazgos».
- El mismo riesgo aparece una sola vez en la entrega (garantía de S03, FR-003); si una entrega
  externa la rompiera, `abrir` toma el primero y anota el aviso.
- Un identificador propuesto por la herramienta deja de constar en su base: la cita pasa a
  «pendiente de confirmar» al verificar, con el cambio anotado en el historial.
- El auditor corrige con un marco fuera de los tres de la constitución: se registra como su
  aporte, con fuente declarada y estado «pendiente de confirmar».
- El enunciado cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4
  («el enunciado de origen cambió»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- La evidencia citada es una referencia sin copia (heredada de S02): la cita lo declara y el
  fundamento no la usa como prueba.
- El JSON de la cita se altera un byte después de firmar: `verificar` lo detecta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir la cita a partir de la entrega vigente de S03
  (`enunciado.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar si el enunciado está firmado.
- **FR-003**: Por cada riesgo vigente de la entrega MUST existir exactamente una cita. Los
  riesgos descartados, con evidencia alterada o con hecho no vigente no generan cita vigente: se
  informan con su marca. Los vacíos heredados MUST NOT generar cita: se listan como contexto.
- **FR-004**: Cada cita MUST tener: identificador, riesgo de origen (id y condición), marco,
  versión, identificador de control (o «pendiente de confirmar»), fundamento de la
  correspondencia, correspondencias adicionales (opcionales), estado del identificador
  (`confirmado`, `pendiente-confirmar`), evidencias citadas (tipo, ubicación, huellas), estado de
  aprobación (`borrador`, `revisado`, `firmado`), marcas y su historial de cambios.
- **FR-005**: La herramienta MUST proponer la correspondencia como sugerencia explicada a partir
  del dominio, el criterio y el impacto del riesgo. El identificador del control MUST proponerse
  solo si consta en su base (guía o norma abierta); si no consta, MUST quedar «pendiente de
  confirmar». La herramienta MUST NOT inventar identificadores (principio IV).
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. La cita MUST NOT
  presentarse como prueba de incumplimiento, y un marco mencionado MUST NOT acreditar cobertura.
- **FR-007**: El auditor MUST poder corregir el marco, la versión, el identificador y el
  fundamento de cualquier cita, añadir correspondencias adicionales, y descartarla y
  restablecerla. Cada corrección, descarte o restablecimiento registra autor, fecha, valor
  anterior, valor nuevo y motivo obligatorio, y deja la cita en «revisado». Ninguna cita se
  borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que marco y versión de cada cita vigente estén
  completos, y MUST rechazar firmar desde «borrador» o sin firmante o sin justificación. Firmar
  la cita MUST NOT abrir la compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S03 contra la registrada; y la huella de cada
  evidencia citada contra su copia guardada (o su original cuando es referencia sin copia). MUST
  detectar la alteración de un byte y MUST informar «evidencia alterada» y «riesgo no vigente»
  por cita.
- **FR-010**: Con la misma entrega de S03 y las mismas correcciones, la herramienta MUST producir
  el mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `03_hallazgos/`, sin crear
  un árbol paralelo ni sobrescribir los productos previos de esa carpeta (`README.md`,
  `matriz_cumplimiento.csv`, `enunciado-*.md`), y ser legible por un tercero sin la herramienta.
- **FR-012**: Por cada cita MUST escribirse una ficha legible `03_hallazgos/cita-<id>.md` con el
  mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST entregar a S05 las citas vigentes: las no descartadas, cuyo
  riesgo sigue en la entrega y sin evidencia alterada; cada una con sus campos, el estado de su
  identificador y las huellas de sus evidencias, más la lista de vacíos heredados e indicar si el
  producto está firmado.
- **FR-014**: Si el enunciado de origen cambió (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor (corregir, descartar, restablecer, revisar) MUST exigir
  que el enunciado de origen no haya cambiado desde `abrir`; si cambió, se rechazan con código 4
  sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija.

### Key Entities

- **Cita**: producto de S04. Referencia la entrega del enunciado de la que deriva (huella y
  estado de firma). Agrupa las citas de riesgo, los vacíos heredados, el estado de aprobación, el
  historial y la firma.
- **Cita de riesgo**: una por riesgo vigente. Identificador derivado del riesgo. Tiene riesgo de
  origen, marco, versión, identificador de control (o pendiente), fundamento, correspondencias
  adicionales, estado de aprobación, marcas (descartada, riesgo no vigente, evidencia alterada) y
  correcciones.
- **Correspondencia**: vínculo riesgo ↔ control con su fundamento explicado; es una sugerencia,
  nunca prueba de incumplimiento.
- **Vacío heredado**: vacío heredado de S03, listado como contexto; no genera cita.
- **Corrección**: autor, fecha, cita afectada, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con R riesgos vigentes y V vacíos heredados, el producto
  tiene exactamente R citas y lista V vacíos heredados.
- **SC-002**: El 100 % de las citas citan su riesgo de origen, la huella de la entrega de S03 y
  al menos una evidencia con tipo, ubicación y huella.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-004**: La alteración de un solo byte del JSON del producto se detecta en el 100 % de los
  casos (`verificar`).
- **SC-005**: La alteración de un solo byte de una evidencia citada deja su cita «evidencia
  alterada» y fuera de la entrega a S05; con firma válida, el estado informado es «firmado con
  evidencia alterada».
- **SC-006**: Ninguna cita llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones, descartes y restablecimientos registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: El auditor identifica todos los identificadores pendientes en menos de 10 minutos:
  por cita en su campo y los pendientes en una sola sección con conteo. Verificación automática:
  existe la sección y su conteo coincide; verificación manual: el auditor mide y registra el
  tiempo.
- **SC-009**: La entrega a S05 contiene exactamente las citas vigentes de FR-013 y ninguna
  descartada, con riesgo no vigente o con evidencia alterada.
- **SC-010**: Abrir y corregir la cita solo crean archivos nuevos en `03_hallazgos/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-011**: El 100 % de las correspondencias propuestas tienen fundamento no vacío, y los
  identificadores no verificables quedan «pendiente de confirmar».
- **SC-012**: Un tercero recorre una cita hasta su riesgo, su hecho y su evidencia y comprueba su
  huella sin ayuda; el resultado se registra en el checklist humano.
- **SC-013**: Con el producto firmado y el enunciado cambiado, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: como en S02 y S03, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S04 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S03 y de la constitución (principios I, II, III y IV).
- Hay un solo rol humano, el auditor, que corrige y firma, como en S01–S03. La revisión por
  segundo par (#33) queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S04 no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la entrega de S03 y escribe en
  `03_hallazgos/`.
- Los marcos citables son los de la constitución (IV): ISO/IEC 27001:2022, NIST CSF 2.0 y CIS
  Controls v8.1. La base de identificadores de la herramienta se alimenta solo de fuentes abiertas
  y de la guía; lo que no consta queda «pendiente de confirmar».
- La cita es sugerencia explicada: la correspondencia CWE↔control de la plataforma existente
  (`platform/c4a/correlation.py`) no se usa como prueba ni como propuesta automática; el
  historial de ese módulo motiva el principio IV.
- **Dependencias**: la entrega de S03 (`enunciado.entregar`, FR-013 de S03) y su modelo de
  riesgo; `alcance.serializar`, `alcance.limpiar` y `util.short_id` ya usados en sprints
  anteriores.
- **Fuera de esta funcionalidad**: leer el activo con las seis funciones NIST (S05), la lista CIS
  (S06), el encargo (S07), las dos frases (S08), el borrador (S09) y el cierre (S10); calcular
  cobertura de un marco (si se calculara, numerador, denominador y pendientes, sin extrapolar al
  SGSI); emitir cualquier dictamen de cumplimiento.
