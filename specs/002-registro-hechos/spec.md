# Feature Specification: S02 — El registro

**Feature Branch**: `002-registro-hechos` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-21

**Status**: Draft

**Input**: Descripción del usuario: «S02, El registro». Segunda épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S02 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, anotaba lo que se puede afirmar y lo que no consta. La
herramienta deja **el registro**.

**Épica**: S02 de S01–S10. **Recibe**: el alcance de S01 (`scope/alcance_s01.json`), firmado o
explícitamente en borrador; si falta, el mínimo de referencia es `scope/alcance.md` y
`scope/autorizacion.md`. **Produce**: el registro. **Entrega a S03 (El enunciado)**: los hechos que se
pueden afirmar, cada uno con su evidencia y su huella, y la lista explícita de lo que no consta, para
que S03 enuncie el riesgo con criterio, impacto y lo que falta.

**Lugar en el proceso de auditoría**: S02 corresponde a la fase Recopilar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`02_evidencia/`. La herramienta propone las entradas del registro; el auditor las corrige y las firma.
Un registro no dictamina: anota hechos y vacíos, no cumplimientos.

## Clarifications

### Session 2026-10-21

- Q: Con la compuerta cerrada, ¿qué evidencia documental puede entrar al registro? → A: La que el
  auditor aporta declarando su origen (de la organización, del ejercicio o del repositorio), obtenida
  sin tocar el objetivo.
- Q: Si una entrada cita varias evidencias que no coinciden, ¿qué resultado técnico queda? → A: Una
  entrada puede citar varias evidencias; si sus resultados discrepan, la herramienta propone
  «inconcluso» hasta que el auditor decida con motivo.
- Q: ¿Qué hace que dos entradas sean la misma? → A: Activo + dominio + afirmación. El identificador se
  deriva del contenido; un dominio puede tener varios hechos distintos, el mismo hecho no se repite.
- Q: ¿Se puede firmar el registro con entradas «no consta»? → A: Sí. La firma guarda cuántas entradas
  no constan y la vista lo muestra.
- Q: ¿Se mantiene SC-008 (menos de 10 minutos)? → A: Sí, verificable: prueba automática de una sola
  sección con su conteo; el auditor mide y registra los minutos.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el registro sin alcance firmado (Priority: P1)

El auditor abre el registro de hechos. El alcance de S01 existe solo en borrador, o no existe. La
herramienta usa lo que hay como mínimo de referencia: crea una entrada «no consta» por cada activo y
dominio del alcance que todavía no tiene evidencia, marca todo el registro como «basado en un alcance
no firmado» y no rellena ningún hecho.

**Why this priority**: es el producto mínimo viable de S02. Aun sin evidencias, deja escrito qué hay
que afirmar y qué falta, que es la entrada de S03. Hoy es el caso real: el alcance está en borrador y
la compuerta técnica está cerrada.

**Independent Test**: con un alcance en borrador y ninguna evidencia, se comprueba que el registro
tiene una entrada «no consta» por cada activo y dominio dentro o pendiente del alcance, que declara
que el alcance no está firmado y que no contiene ningún hecho afirmado.

**Acceptance Scenarios**:

1. **Given** un alcance en borrador con un activo y N dominios dentro o pendientes, **When** el
   auditor abre el registro, **Then** el registro tiene una entrada «no consta» por el activo y por
   cada uno de los N dominios, y declara que se basa en un alcance no firmado.
2. **Given** que el alcance de S01 no existe, **When** el auditor abre el registro, **Then** la
   herramienta informa que falta el producto anterior, usa `scope/alcance.md` como mínimo de
   referencia y deja todas las entradas en «no consta», sin hechos afirmados.
3. **Given** un alcance firmado, **When** el auditor abre el registro, **Then** el registro cita la
   huella del alcance firmado del que deriva.
4. **Given** un dominio del alcance marcado «fuera», **When** se abre el registro, **Then** ese
   dominio no genera entradas.

---

### User Story 2 - La herramienta propone un hecho y el auditor lo corrige (Priority: P2)

El auditor aporta una pieza de evidencia (por ejemplo, un documento del ejercicio o la salida de una
prueba autorizada) y la asocia a un activo y un dominio. La herramienta propone la entrada: qué se
puede afirmar, el tipo de evidencia, la huella de los bytes guardados, cuándo y quién la recolectó, y
el resultado técnico. El auditor corrige la redacción o el resultado, con motivo, y la entrada queda
«revisada». Solo cuando el auditor firma el registro las entradas quedan «firmadas».

**Why this priority**: es la separación central de la constitución: la herramienta propone y el
auditor decide. Sin esta historia, el registro sería una afirmación automática.

**Independent Test**: con una evidencia sintética dentro del alcance, se comprueba que la entrada
propuesta trae tipo, huella, fecha, responsable y resultado técnico; que una corrección queda en el
historial con autor, fecha, valor anterior, valor nuevo y motivo; y que nada llega a «firmado» sin la
acción del auditor.

**Acceptance Scenarios**:

1. **Given** una evidencia sobre el activo del alcance y un dominio dentro, **When** el auditor la
   aporta, **Then** la herramienta propone una entrada con lo que se puede afirmar, el tipo de
   evidencia, la huella de los bytes guardados, la fecha y el responsable de la recolección, y el
   resultado técnico, en estado «borrador».
2. **Given** una entrada propuesta, **When** el auditor cambia el resultado técnico de «positivo» a
   «inconcluso» con un motivo, **Then** el cambio queda registrado con autor, fecha, valor anterior,
   valor nuevo y motivo, y la entrada pasa a «revisada».
3. **Given** un intento de corregir sin motivo, **When** se intenta registrar, **Then** el cambio se
   rechaza y el registro no se modifica.
4. **Given** un registro revisado, **When** el auditor lo firma con su nombre y una justificación,
   **Then** el registro queda «firmado» con la huella de sus bytes guardados; cualquier cambio
   posterior anula la firma.
5. **Given** una entrada «no consta» y una evidencia nueva para ese mismo activo y dominio, **When**
   el auditor la aporta, **Then** la entrada pasa a tener un hecho propuesto y la historia de que
   antes no constaba se conserva.

---

### User Story 3 - Un dato no consta y la fila se conserva (Priority: P3)

Un dominio del alcance no tiene evidencia porque la prueba técnica no se pudo ejecutar: la compuerta
de autorización está cerrada. La herramienta conserva la entrada «no consta», con resultado técnico
«no-ejecutado» y el motivo («compuerta cerrada»). No la borra, no la rellena y no la presenta como
«sin hallazgos».

**Why this priority**: protege la diferencia entre «no se observó nada» y «no se miró». Esa diferencia
es la que S03 necesita para enunciar lo que falta.

**Independent Test**: con la compuerta cerrada y un dominio técnico sin evidencia, se comprueba que la
entrada existe, que está «no consta» con resultado «no-ejecutado» y motivo, y que en ningún lugar se
lee como ausencia de hallazgos.

**Acceptance Scenarios**:

1. **Given** la compuerta cerrada y un dominio técnico sin evidencia, **When** se genera el registro,
   **Then** la entrada queda «no consta» con resultado «no-ejecutado» y motivo «compuerta cerrada».
2. **Given** un dominio que requiere políticas, personas o procesos, **When** se genera el registro,
   **Then** la entrada queda «no consta» con la nota de que requiere solicitud documental, no una
   prueba técnica.
3. **Given** cualquier entrada «no consta», **When** se vuelve a generar el registro, **Then** la
   entrada se conserva hasta que una evidencia admisible o una decisión del auditor la cambie.
4. **Given** un registro sin ningún hecho positivo, **When** se resume, **Then** el resumen dice
   cuántas entradas no constan; no dice «sin hallazgos».

---

### User Story 4 - Rechazar evidencia que no acredita esta auditoría (Priority: P3)

El auditor intenta aportar una evidencia que pertenece a otro activo, a otra corrida sobre otro
objetivo, a un dominio fuera del alcance, o que se tomó sin autorización vigente. La herramienta no
la acepta como evidencia de esta auditoría y dice por qué.

**Why this priority**: es el contrato con S01 y el principio III: evidencia de otro activo o de otra
corrida no acredita una evaluación. Hoy hay en el repositorio corridas del análisis estático sobre otro
objetivo que no deben entrar al registro de Metasploitable 2.

**Independent Test**: con evidencias sintéticas de otro activo, de un dominio fuera y de una fecha
fuera de la ventana, se comprueba que ninguna entra como hecho y que cada rechazo queda anotado con su
motivo.

**Acceptance Scenarios**:

1. **Given** una evidencia sobre un activo que el alcance responde «fuera», **When** se aporta,
   **Then** se rechaza con el motivo y la fila del alcance que lo decide.
2. **Given** una evidencia de una corrida sobre otro objetivo, **When** se aporta, **Then** se rechaza
   con el motivo «otro objetivo».
3. **Given** una evidencia técnica recolectada sin autorización firmada y vigente en su fecha, **When**
   se aporta, **Then** se rechaza con el motivo «sin autorización vigente»; la evidencia documental no
   necesita la compuerta abierta.
4. **Given** una evidencia cuyo archivo ya no corresponde a la huella registrada, **When** se verifica
   el registro, **Then** la entrada se informa «evidencia alterada» y deja de acreditar el hecho.

---

### Edge Cases

- El archivo de evidencia no existe o no se puede leer: no se crea la entrada; se informa el motivo.
- La misma evidencia se aporta dos veces para el mismo hecho: la entrada es una sola (identidad
  derivada del contenido); no se duplica.
- La evidencia referencia un archivo del objetivo sin copiarlo: la entrada lo declara y distingue la
  huella del contenido original de la huella de lo guardado.
- La evidencia contiene datos personales o secretos: el registro no copia el contenido; cita el tipo,
  la ubicación y la huella. Lo que se muestre como extracto va enmascarado.
- La evidencia contiene direcciones de red o comandos: el registro no los copia; nombra el tipo de
  evidencia.
- El alcance cambia o se vuelve a firmar después de abrir el registro: el registro advierte que se
  basó en otra versión del alcance y señala las entradas afectadas; no se actualiza solo.
- Un dominio pasa a «fuera» en el alcance después de registrar hechos: las entradas se conservan con
  la advertencia «dominio fuera del alcance vigente» y dejan de entregarse a S03.
- Un hecho «negativo» (se miró y no se observó la condición) se registra como tal; no equivale a
  «cumple».
- Una entrada con resultado «positivo» sin evidencia citada no se acepta: queda «no consta».
- El auditor quiere descartar una entrada: se marca descartada con motivo; no se borra.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el registro a partir del alcance de S01. Si el alcance no
  existe, MUST informarlo y usar `scope/alcance.md` y `scope/autorizacion.md` como mínimo de referencia.
- **FR-002**: El registro MUST citar la versión del alcance de la que deriva (su huella) y declarar si
  ese alcance está firmado.
- **FR-003**: Por cada activo y cada dominio que el alcance responde «dentro» o «pendiente», el
  registro MUST tener al menos una entrada; sin evidencia, la entrada queda «no consta». Lo que el
  alcance responde «fuera» MUST NOT generar entradas.
- **FR-004**: Cada entrada MUST tener: activo, dominio, lo que se afirma (o «no consta»), resultado
  técnico (`positivo`, `negativo`, `inconcluso`, `no-ejecutado`), evidencias citadas, motivo,
  responsable y estado de aprobación (`borrador`, `revisado`, `firmado`).
- **FR-005**: Cada evidencia citada MUST registrar su tipo (documental o técnica), origen declarado,
  ubicación, fecha de recolección, responsable y huella SHA-256 de los bytes guardados. Una evidencia
  documental sin origen declarado MUST rechazarse. Si referencia un archivo del
  objetivo sin copiarlo, MUST declararlo y distinguir la huella del contenido original de la huella de
  lo guardado.
- **FR-006**: Una entrada con un hecho afirmado (resultado distinto de `no-ejecutado`) MUST citar al
  menos una evidencia admisible. Sin evidencia, MUST quedar «no consta». Una entrada puede citar varias
  evidencias; si sus resultados discrepan, la herramienta MUST proponer «inconcluso» y dejar la
  decisión al auditor.
- **FR-020**: La identidad de una entrada MUST ser activo + dominio + afirmación, con identificador
  derivado del contenido. Aportar de nuevo el mismo hecho agrega la evidencia a la entrada existente;
  no crea otra.
- **FR-007**: La herramienta MUST rechazar como evidencia de esta auditoría la que pertenece a un
  activo o dominio que el alcance responde «fuera», a una corrida sobre otro objetivo, o la evidencia
  técnica recolectada sin autorización firmada, completa y con ventana vigente en su fecha. Cada
  rechazo MUST quedar anotado con su motivo.
- **FR-008**: Una verificación independiente MUST recalcular la huella de cada evidencia citada y del
  registro guardado, y detectar cualquier alteración. Una evidencia alterada MUST dejar de acreditar su
  hecho.
- **FR-009**: Con la compuerta de autorización cerrada, las entradas de dominios técnicos sin
  evidencia MUST quedar con resultado `no-ejecutado` y motivo «compuerta cerrada». La herramienta MUST
  NOT abrir la compuerta ni ejecutar pruebas.
- **FR-010**: Los dominios que requieren políticas, personas o procesos MUST quedar «no consta» con la
  nota de solicitud documental cuando no tengan evidencia documental.
- **FR-011**: El registro MUST NOT contener estados de cumplimiento (`cumple`, `parcial`, `no-cumple`,
  `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. «Sin hechos positivos» MUST NOT
  presentarse como «sin hallazgos» ni como «cumple».
- **FR-012**: El registro MUST NOT copiar contenido crudo de la evidencia, direcciones de red,
  comandos, puertos, credenciales ni datos personales. Nombra el tipo de evidencia y su ubicación.
- **FR-013**: El auditor MUST poder corregir cualquier entrada y descartarla. Cada corrección o
  descarte registra autor, fecha, valor anterior, valor nuevo y motivo obligatorio, y deja la entrada
  en «revisado». Ninguna entrada se borra.
- **FR-014**: Solo una acción explícita del auditor MUST dejar el registro en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier cambio posterior
  la anula. Firmar el registro MUST NOT abrir la compuerta. Se puede firmar con entradas «no consta»;
  el registro de firma guarda cuántas había.
- **FR-015**: Al regenerar, la herramienta MUST conservar las entradas, evidencias y correcciones
  previas. Si el alcance cambió, MUST señalar las entradas afectadas en lugar de sobrescribirlas.
- **FR-016**: El registro MUST agrupar en una sola sección las entradas «no consta», con su conteo, y
  en otra los rechazos, con su motivo.
- **FR-017**: El registro MUST guardarse en archivos nuevos dentro de `02_evidencia/`, sin crear un
  árbol paralelo ni sobrescribir `02_evidencia/inventario.json`, y ser legible por un tercero sin la
  herramienta.
- **FR-018**: Con el mismo alcance, las mismas evidencias y las mismas correcciones, la herramienta
  MUST producir el mismo registro.
- **FR-019**: La herramienta MUST entregar a S03 las entradas con hecho afirmado y las «no consta»,
  cada una con su activo, dominio, evidencia y huella, e indicar si el registro está firmado.

### Key Entities

- **Registro**: producto de S02. Referencia el alcance del que deriva (huella y estado de firma).
  Agrupa las entradas, las evidencias citadas, los rechazos, el estado de aprobación, el historial y
  la firma.
- **Entrada**: un hecho afirmable o un vacío, identificada por activo + dominio + afirmación. Tiene
  activo, dominio, afirmación (o «no consta»),
  resultado técnico, evidencias citadas, motivo, responsable, estado de aprobación y marcas (descartada,
  afectada por cambio de alcance).
- **Evidencia citada**: tipo (documental o técnica), origen declarado, ubicación, fecha y responsable de la recolección,
  huella de lo guardado, huella del contenido original cuando difiere, y si es una referencia sin copia.
- **Rechazo**: evidencia que se intentó aportar y no acredita esta auditoría, con su motivo y la regla
  o fila del alcance que lo decide.
- **Corrección**: autor, fecha, entrada afectada, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación y huella del registro guardado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con un alcance de prueba que tiene un activo y N dominios dentro o pendientes y ninguna
  evidencia, el registro tiene exactamente N + 1 entradas «no consta» y cero hechos afirmados.
- **SC-002**: El 100 % de las entradas con hecho afirmado citan al menos una evidencia con tipo,
  ubicación, fecha, responsable y huella.
- **SC-003**: El 100 % de las evidencias de prueba de otro activo, de otra corrida, de un dominio fuera
  o técnicas sin autorización vigente se rechazan, cada una con su motivo.
- **SC-004**: La alteración de un solo byte de una evidencia citada o del registro guardado se detecta
  en el 100 % de los casos.
- **SC-005**: Una búsqueda sobre el registro generado encuentra cero direcciones de red, comandos,
  puertos, credenciales y estados de cumplimiento.
- **SC-006**: Ninguna entrada llega a «firmado» sin la acción explícita del auditor, y el 100 % de las
  correcciones y descartes registra autor, fecha y motivo.
- **SC-007**: Dos generaciones con las mismas entradas producen archivos idénticos byte a byte.
- **SC-008**: El auditor identifica todo lo que no consta en menos de 10 minutos, desde una sola
  sección con su conteo, sin abrir otros archivos. Verificación automática: existe una sola sección
  «no consta» y su conteo coincide con las entradas. Verificación manual: el auditor mide y registra el
  tiempo.
- **SC-009**: Un tercero que no estuvo en la sala recorre una entrada de cada dominio hasta su
  evidencia y comprueba su huella sin ayuda.

## Assumptions

- **Origen de la descripción**: como en S01, no se usaron las guías del curso (decisión del usuario:
  autoestudio). La descripción sale de la fila S02 de `docs/PROMPT_SPEC_KIT.md`, del producto de S01 y
  de la constitución (principios II y III).
- Hay un solo rol humano, el auditor, que corrige y firma, como en S01. La revisión por segundo par
  (#33) queda fuera.
- La firma del registro sigue el mecanismo de S01: firmante, fecha, justificación y huella SHA-256 de
  los bytes guardados.
- Mientras `scope/autorizacion.md` no esté firmada y vigente, solo se registra evidencia documental
  aportada con origen declarado y obtenida sin tocar el objetivo (aclarado 2026-10-21); los dominios
  técnicos quedan `no-ejecutado`. S02 no ejecuta pruebas ni las dispara.
- Las corridas existentes del análisis estático en `evidence/` y `02_evidencia/inventario.json`
  corresponden a otro objetivo (un repositorio), no a Metasploitable 2; no acreditan esta auditoría.
- La evidencia cruda sigue fuera de git (`evidence/` está ignorado); el registro solo cita ubicación y
  huella. El cifrado de custodia no es parte de S02 (#23).
- El defecto conocido de `platform/c4a/evidence.py::from_command` (la huella no corresponde al archivo
  guardado, principio III) no se replica: el registro calcula la huella sobre los bytes guardados.
- **Dependencias**: el alcance de S01 y su consulta (dentro/fuera/pendiente); la compuerta de
  autorización en solo lectura; el modelo de evidencia de `platform/c4a`.
- **Fuera de esta funcionalidad**: ejecutar pruebas, enunciar riesgos (S03), citar controles (S04),
  perfiles NIST (S05), lista CIS (S06) y cualquier dictamen de cumplimiento.
