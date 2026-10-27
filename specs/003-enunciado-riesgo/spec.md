# Feature Specification: S03 — El enunciado

**Feature Branch**: `003-enunciado-riesgo` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S03, El enunciado». Tercera épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S03 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, enunciaba el riesgo con criterio, impacto y lo que
falta. La herramienta deja **el enunciado**.

**Épica**: S03 de S01–S10. **Recibe**: la entrega de S02 (`registro entregar`: los hechos vigentes,
cada uno con sus evidencias y huellas, y las entradas «no consta» vigentes). **Produce**: el
enunciado. **Entrega a S04 (La cita)**: los riesgos enunciados, cada uno con su hecho de origen, su
evidencia con huella y sus campos de criterio, impacto y lo que falta, para que S04 ubique el
riesgo en un marco con nombre y versión.

**Lugar en el proceso de auditoría**: S03 corresponde a la fase Analizar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`03_hallazgos/`. La herramienta propone los enunciados; el auditor los corrige y los firma. Un
enunciado no dictamina: interpreta hechos ya registrados, no evalúa controles.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S02 aún tiene acciones humanas pendientes (T038, T039). El dueño ordenó
«construye la herramienta» (2026-10-26); esta spec se escribe con esa orden expresa y con las
acciones humanas aún abiertas. La desviación queda registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S03 necesita un «mínimo de referencia» como S02 cuando falta el producto anterior? → A: No.
  S02 podía derivar el alcance de `scope/alcance.md` sin escribir en `scope/`; S03 no puede
  enunciar riesgos sin hechos. Si falta el registro de S02, `enunciado abrir` se detiene con el
  código 2 y no escribe nada.
- Q: ¿Un hecho con resultado «negativo» (se buscó y no se observó la condición) produce un riesgo? →
  A: Produce un enunciado acotado: declara lo observado y lleva la nota fija de que no acredita
  cumplimiento ni descarta la reaparición de la condición (principio II).
- Q: ¿La herramienta propone criterio e impacto? → A: Propone textos genéricos claramente
  marcables como borrador; la cita del marco (control, versión, identificador) es trabajo de S04 y
  S03 no inventa identificadores (principio IV). Firmar exige que criterio e impacto de cada
  enunciado vigente estén completados por el auditor.
- Q: ¿Qué identidad tiene un enunciado? → A: Un enunciado por hecho vigente, identificador derivado
  del identificador del hecho (`R-…` sobre `H-…`); corrigiendo el texto el identificador no cambia.
- Evaluación de coherencia (2026-10-26): un «no consta» del registro no genera enunciado; se lista
  como vacío heredado. Lo que falta por enunciado se deriva de las marcas y del resultado técnico.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el enunciado sin registro firmado (Priority: P1) 🎯 MVP

El auditor abre el enunciado a partir del registro de S02. El registro existe solo en borrador, o
no existe. Si existe, la herramienta propone un enunciado de riesgo por cada hecho vigente, cada
uno citando su hecho de origen y la huella de sus evidencias, con los campos de criterio, impacto
y lo que falta; los «no consta» del registro quedan listados como vacíos heredados, no como
riesgos. Si el registro no existe, la herramienta se detiene y lo informa.

**Why this priority**: es el producto mínimo viable de S03. Sin escribir una sola conclusión,
convierte los hechos registrados en riesgos redactados y deja explícito lo que falta, que es la
entrada de S04. Hoy es el caso real: el registro está en borrador con cero hechos.

**Independent Test**: con una entrega de S02 con H hechos vigentes y M «no consta», se comprueba
que hay exactamente H enunciados y M vacíos listados, que cada enunciado cita su hecho y al menos
una evidencia con huella, y que ningún archivo contiene estados de cumplimiento.

**Acceptance Scenarios**:

1. **Given** una entrega con H hechos vigentes (resultados positivo, negativo e inconcluso) y M
   «no consta», **When** el auditor abre el enunciado, **Then** hay exactamente H enunciados, cada
   uno con condición, consecuencia, criterio, impacto y lo que falta propuestos, y los M «no
   consta» quedan listados como vacíos heredados, sin enunciado.
2. **Given** que el registro de S02 no existe, **When** el auditor abre el enunciado, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `03_hallazgos/`.
3. **Given** un registro firmado, **When** se abre el enunciado, **Then** el producto cita la
   huella de la entrega firmada de la que deriva y declara que el registro está firmado.
4. **Given** una entrega donde un hecho fue descartado o quedó fuera del alcance vigente, **When**
   se abre el enunciado, **Then** ese hecho no genera enunciado.

---

### User Story 2 - La herramienta propone y el auditor corrige (Priority: P2)

El auditor corrige la condición, la consecuencia, el criterio o el impacto de un enunciado, con
motivo; la corrección queda en el historial con autor, fecha, valor anterior y valor nuevo. Puede
descartar un enunciado y restablecerlo. Revisa el producto y lo firma; cualquier escritura
posterior anula la firma. Firmar exige que criterio e impacto estén completados.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. Sin esta historia, el enunciado sería una conclusión automática.

**Independent Test**: con un enunciado propuesto, se comprueba que corregir un campo con motivo
queda en el historial y deja el enunciado «revisado»; que descartar y restablecer funcionan con
motivo; que firmar desde «revisado» con firmante y justificación escribe la firma con la huella de
los bytes guardados; y que ningún camino llega a «firmado» sin la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** un enunciado propuesto, **When** el auditor corrige el impacto con un motivo, **Then**
   el cambio queda registrado con autor, fecha, valor anterior, valor nuevo y motivo, y el
   enunciado pasa a «revisado».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y el enunciado no se
   modifica.
3. **Given** un producto revisado cuyos enunciados vigentes tienen criterio e impacto completos,
   **When** el auditor firma con su nombre y una justificación, **Then** el producto queda
   «firmado» con la huella de sus bytes guardados; cualquier cambio posterior anula la firma.
4. **Given** un enunciado vigente con el impacto vacío, **When** se intenta firmar, **Then** la
   firma se rechaza informando qué enunciados faltan por completar.
5. **Given** un enunciado descartado, **When** el auditor lo restablece con motivo, **Then** vuelve
   a la entrega y la historia conserva el descarte y el restablecimiento.

---

### User Story 3 - Un hecho negativo o inconcluso no es un cumplimiento (Priority: P3)

Un hecho «negativo» (se buscó la condición y la evidencia muestra que no está) o «inconcluso»
produce un enunciado acotado: declara lo observado, lleva la nota fija de que no acredita
cumplimiento y señala lo que falta para decidir. Ningún archivo del producto contiene estados de
cumplimiento ni presenta la ausencia de riesgos enunciados como «sin hallazgos» ni «cumple».

**Why this priority**: protege la diferencia entre «no se observó la condición» y «el control
cumple». Esa diferencia es la que el dictamen humano, no la herramienta, debe decidir (principio
II).

**Independent Test**: con hechos negativos e inconclusos en la entrega, se comprueba que sus
enunciados llevan la nota de no-cumplimiento, que «lo que falta» deriva del resultado técnico y
que una búsqueda sobre los archivos generados no encuentra estados de cumplimiento.

**Acceptance Scenarios**:

1. **Given** un hecho negativo, **When** se abre el enunciado, **Then** el enunciado declara que la
   condición no se observó y lleva la nota fija de que eso no acredita cumplimiento ni descarta su
   reaparición.
2. **Given** un hecho inconcluso, **When** se abre el enunciado, **Then** «lo que falta» incluye la
   necesidad de evidencia adicional para decidir.
3. **Given** cualquier enunciado, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`.
4. **Given** un producto sin ningún hecho positivo, **When** se resume, **Then** el resumen dice
   cuántos riesgos se enuncian y cuántos vacíos hereda; no dice «sin hallazgos».

---

### User Story 4 - Verificar la consistencia con el registro y entregar a S04 (Priority: P3)

El auditor verifica el producto: la huella de los bytes guardados sigue correspondiendo a la firma,
cada evidencia citada sigue coincidiendo con su copia guardada y cada hecho de origen sigue
vigente en el registro. Si el registro cambió después de firmar, la herramienta no actualiza sola.
La entrega a S04 contiene exactamente los enunciados vigentes.

**Why this priority**: es el contrato con S02 y el principio III: un enunciado solo acredita si su
evidencia y su hecho de origen siguen en pie. Es también la entrada de S04.

**Independent Test**: con un producto firmado, se altera un byte de una evidencia copiada y otro
del JSON del enunciado, y se comprueba que `verificar` lo detecta; se cambia el registro y se
comprueba que `abrir` informa y, estando firmado, no escribe; se comprueba que `entregar` devuelve
solo los vigentes.

**Acceptance Scenarios**:

1. **Given** un enunciado que cita una evidencia cuya copia ya no corresponde a la huella
   registrada, **When** se verifica, **Then** el enunciado se informa con «evidencia alterada» y
   deja de entrar en la entrega a S04.
2. **Given** un producto firmado cuyo registro de origen cambió, **When** se abre de nuevo, **Then**
   la herramienta informa el cambio y no escribe (código 4).
3. **Given** un hecho que ya no está en la entrega del registro (porque el registro cambió), **When**
   se verifica, **Then** el enunciado se informa con «hecho no vigente».
4. **Given** un producto con enunciados vigentes, descartados y con inconsistencias, **When** se
   entrega a S04, **Then** la entrega contiene exactamente los vigentes, con sus campos y las
   huellas de sus evidencias.

---

## Edge Cases

- El registro de S02 no existe: `abrir` termina en código 2 sin escribir.
- La entrega de S02 tiene cero hechos: el producto tiene cero enunciados y lista los vacíos; la
  vista lo dice así, sin «sin hallazgos».
- El mismo hecho aparece una sola vez en la entrega (garantía de S02, FR-020); si una entrega
  externa la rompiera, `abrir` toma el primero y anota el aviso.
- Una corrección de texto no cambia el identificador del enunciado (deriva del hecho, no del
  texto).
- El auditor descarta el único enunciado de un dominio: la entrega a S04 no contiene ese dominio y
  el historial conserva el descarte.
- El registro cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4
  («el registro de origen cambió»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- La evidencia citada es una referencia sin copia (`sin_copia` de S02): el enunciado lo declara y
  «lo que falta» incluye verificar el original.
- El JSON del enunciado se altera un byte después de firmar: `verificar` lo detecta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el enunciado a partir de la entrega vigente de S02
  (`registro.entregar`). Si el registro no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar si el registro está firmado.
- **FR-003**: Por cada hecho vigente de la entrega MUST existir exactamente un enunciado. Los hechos
  fuera del alcance vigente, descartados o con evidencia alterada no generan enunciado. Las
  entradas «no consta» MUST NOT generar enunciado: se listan como vacíos heredados.
- **FR-004**: Cada enunciado MUST tener: identificador, activo, dominio, hecho de origen (id,
  afirmación, resultado), condición, consecuencia, criterio, impacto, «lo que falta» (lista),
  evidencias citadas (tipo, ubicación, huellas), estado de aprobación (`borrador`, `revisado`,
  `firmado`), marcas y su historial de cambios.
- **FR-005**: La herramienta MUST proponer: la condición a partir de la afirmación del hecho; la
  consecuencia según el resultado técnico (positivo, negativo, inconcluso); el criterio como texto
  cualitativo sin identificadores de controles (la cita del marco es de S04); el impacto vacío para
  el auditor; y «lo que falta» derivado de las marcas y del resultado (alcance pendiente, evidencia
  adicional, registro no firmado, evidencia sin copia, reevaluación de un negativo).
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. Un hecho negativo MUST
  enunciarse con la nota fija de que no acredita cumplimiento ni descarta la reaparición de la
  condición.
- **FR-007**: El auditor MUST poder corregir la condición, la consecuencia, el criterio y el
  impacto de cualquier enunciado, y descartarlo y restablecer un descartado. Cada corrección,
  descarte o restablecimiento registra autor, fecha, valor anterior, valor nuevo y motivo
  obligatorio, y deja el enunciado en «revisado». Ningún enunciado se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que criterio e impacto de cada enunciado vigente estén
  completos, y MUST rechazar firmar desde «borrador» o sin firmante o sin justificación. Firmar el
  enunciado MUST NOT abrir la compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado contra
  la firma; la huella de la entrega de S02 contra la registrada; y la huella de cada evidencia
  citada contra su copia guardada (o su original cuando es referencia sin copia). MUST detectar la
  alteración de un byte y MUST informar «evidencia alterada» y «hecho no vigente» por enunciado.
- **FR-010**: Con la misma entrega de S02 y las mismas correcciones, la herramienta MUST producir
  el mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `03_hallazgos/`, sin crear un
  árbol paralelo ni sobrescribir los productos previos de esa carpeta (`README.md`,
  `matriz_cumplimiento.csv`), y ser legible por un tercero sin la herramienta.
- **FR-012**: Por cada enunciado MUST escribirse una ficha legible `03_hallazgos/enunciado-<id>.md`
  con el mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST entregar a S04 los enunciados vigentes: los no descartados, cuyo
  hecho sigue en la entrega y sin evidencia alterada; cada uno con sus campos y las huellas de sus
  evidencias, más la lista de vacíos heredados e indicar si el producto está firmado.
- **FR-014**: Si el registro de origen cambió (huella de `registro_s02.json` o de la entrega
  distinta de la registrada), `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la
  escritura con código 4.
- **FR-015**: Las acciones del auditor (corregir, descartar, restablecer, revisar) MUST exigir que
  el registro de origen no haya cambiado desde `abrir`; si cambió, se rechazan con código 4 sin
  escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados de
  cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se reemplazan
  con la remisión fija.

### Key Entities

- **Enunciado**: producto de S03. Referencia la entrega del registro de la que deriva (huella y
  estado de firma). Agrupa los enunciados de riesgo, los vacíos heredados, el estado de aprobación,
  el historial y la firma.
- **Enunciado de riesgo**: uno por hecho vigente. Identificador derivado del hecho. Tiene activo,
  dominio, hecho de origen, condición, consecuencia, criterio, impacto, «lo que falta», evidencias
  citadas, estado de aprobación, marcas (descartado, hecho no vigente, evidencia alterada) y
  correcciones.
- **Vacío heredado**: entrada «no consta» vigente del registro, listada como contexto de lo que
  falta; no es un riesgo enunciado.
- **Corrección**: autor, fecha, enunciado afectado, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con H hechos vigentes y M «no consta», el producto tiene
  exactamente H enunciados y lista M vacíos heredados.
- **SC-002**: El 100 % de los enunciados citan su hecho de origen y al menos una evidencia con
  tipo, ubicación y huella.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-004**: La alteración de un solo byte del JSON del producto se detecta en el 100 % de los
  casos (`verificar`).
- **SC-005**: La alteración de un solo byte de una evidencia citada deja su enunciado «evidencia
  alterada» y fuera de la entrega a S04; con firma válida, el estado informado es «firmado con
  evidencia alterada».
- **SC-006**: Ningún enunciado llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones, descartes y restablecimientos registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: El auditor identifica todo lo que falta en menos de 10 minutos: por enunciado en su
  campo y los vacíos en una sola sección con conteo. Verificación automática: existe la sección y
  su conteo coincide; verificación manual: el auditor mide y registra el tiempo.
- **SC-009**: La entrega a S04 contiene exactamente los enunciados vigentes de FR-013 y ninguno
  descartado, con hecho no vigente o con evidencia alterada.
- **SC-010**: Abrir y corregir el enunciado solo crean archivos nuevos en `03_hallazgos/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-011**: Todo enunciado de hecho negativo lleva la nota fija de no-cumplimiento (FR-006).
- **SC-012**: Un tercero recorre un enunciado hasta la evidencia de su hecho y comprueba su huella
  sin ayuda; el resultado se registra en el checklist humano.
- **SC-013**: Con el producto firmado y el registro cambiado, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: la descripción sale de la fila S03 de `docs/PROMPT_SPEC_KIT.md`, de
  la entrega de S02 y de la constitución (principios I, II, III y IV).
- Hay un solo rol humano, el auditor, que corrige y firma, como en S01 y S02. La revisión por
  segundo par (#33) queda fuera.
- La firma sigue el mecanismo de S01 y S02: firmante, fecha, justificación y huella SHA-256 de los
  bytes guardados.
- S03 no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la entrega de S02 y escribe en
  `03_hallazgos/`.
- La cita del marco (control, versión, identificador) es de S04: S03 propone criterio cualitativo y
  no inventa identificadores (principio IV).
- Los hechos negativos e inconclusos enuncian riesgo acotado: la conclusión de cumplimiento es del
  auditor, nunca de la herramienta (principio II).
- Las corridas existentes del análisis estático no alimentan S03: solo la entrega vigente del
  registro de S02 (principio III).
- **Dependencias**: la entrega de S02 (`registro.entregar`, FR-019 de S02) y su modelo de evidencia;
  `alcance.serializar`, `alcance.limpiar` y `util.short_id` ya usados en S01 y S02.
- **Fuera de esta funcionalidad**: citar controles con marco y versión (S04), perfiles NIST (S05),
  lista CIS (S06), el encargo (S07), las dos frases (S08), el borrador (S09) y el cierre (S10);
  calcular CVSS (la plataforma ya lo hace; un enunciado puede citar la severidad como dato del
  hecho cuando la evidencia la trae, sin recalcularla aquí).
