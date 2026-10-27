# Feature Specification: S10 — El cierre

**Feature Branch**: `010-cierre` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S10, El cierre». Décima y última épica del ciclo de
construcción (S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila
S10 de `docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, dejaba un informe que un tercero recorre
hasta la evidencia. La herramienta deja **el cierre**.

**Épica**: S10 de S01–S10. **Recibe**: la entrega de S09 (`borrador.entregar`): el informe de
cierre en borrador, con todas sus secciones derivadas de las entregas S01–S08 y citando sus
huellas. **Produce**: el cierre: el informe final que un tercero recorre hasta la evidencia, con
el registro de ese recorrido. **Entrega**: es la última épica; su producto es el informe de
cierre para el cliente (Comercial Andes Sur SpA), que el dueño entrega cuando decide.

**Lugar en el proceso de auditoría**: S10 corresponde a la fase Informar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`04_informe/`. La herramienta propone el informe de cierre y la tabla de recorrido; el auditor
las corrige y firma. Un cierre no dictamina: deja el trabajo verificable; las conclusiones que el
auditor formule van como su texto firmado, nunca generadas como dictamen por la herramienta.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S09 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S10 necesita un «mínimo de referencia» cuando falta el borrador de S09? → A: No. El cierre
  es el último eslabón; sin borrador no hay qué cerrar. Si falta la entrega de S09, `cierre
  abrir` se detiene con el código 2 y no escribe nada.
- Q: ¿El cierre exige el borrador firmado? → A: Sí. Abrir un cierre sobre un borrador no firmado
  se informa y se rechaza: el informe final firma sobre el borrador aprobado por el auditor. El
  código de salida en ese caso es el 5 («el producto anterior no está firmado»), distinto del 2
  («falta el producto anterior»).
- Q: ¿Quién es el tercero que recorre? → A: una persona que no estuvo en la sala: otro auditor,
  el cliente o un revisor. La herramienta prepara la tabla de recorrido (afirmación → sección →
  ficha → huella); el recorrido mismo lo hace el tercero y su resultado se registra en el
  checklist humano, no lo simula la herramienta.
- Q: ¿Un enlace del recorrido que no verifica impide cerrar? → A: Sí. El cierre con enlaces rotos
  queda «pendiente» y se informa; el auditor decide corregir o declarar. No se maquilla: un
  informe que un tercero no puede recorrer no es un cierre (principio III).
- Q: ¿El cierre publica o entrega el informe al cliente? → A: No. Publicar, entregar o subir el
  informe a GitHub son decisiones del dueño (la constitución reserva commit, push y escrituras en
  GitHub a su aprobación expresa). El cierre deja el informe listo y firmado en `04_informe/`.
- Evaluación de coherencia (2026-10-26): el cierre recalcula todas las huellas que el borrador
  cita; si alguna dejó de corresponder, el recorrido lo marca antes de que el tercero empiece.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el cierre sin borrador (Priority: P1) 🎯 MVP

El auditor abre el cierre a partir de la entrega de S09. El borrador no existe: la herramienta se
detiene y lo informa, sin escribir nada (código 2). Si existe pero no está firmado, se informa y
no se escribe (código 5). Si está firmado, la herramienta propone el informe de cierre: el
contenido del borrador con la tabla de recorrido —cada afirmación con su sección, su ficha y su
huella— y el registro del recorrido en blanco para el tercero.

**Why this priority**: es el producto mínimo viable de S10. Sin redactar nada nuevo, convierte el
borrador firmado en el informe que un tercero puede recorrer; cierra la cadena S01–S10.

**Independent Test**: con la entrega de S09 firmada, se comprueba que el informe de cierre
contiene todas las secciones del borrador, que la tabla de recorrido cubre cada afirmación del
informe, que cada enlace lleva a una ficha y a una huella, y que ningún archivo contiene estados
de cumplimiento.

**Acceptance Scenarios**:

1. **Given** un borrador firmado, **When** el auditor abre el cierre, **Then** el informe de
   cierre contiene todas las secciones del borrador y la tabla de recorrido con un enlace por
   afirmación: sección, ficha y huella.
2. **Given** que la entrega de S09 no existe, **When** el auditor abre el cierre, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `04_informe/`.
3. **Given** un borrador que no está firmado, **When** el auditor abre el cierre, **Then** la
   herramienta informa que el producto anterior no está firmado y no escribe (código 5).
4. **Given** una sección del borrador con «no consta», **When** se abre el cierre, **Then** el
   informe la conserva con su motivo y el recorrido lo declara.

---

### User Story 2 - La herramienta propone la tabla de recorrido y el auditor corrige (Priority: P2)

El auditor corrige la redacción del informe o la agrupación de la tabla de recorrido, con motivo;
cada cambio queda en el historial con autor, fecha, valor anterior y valor nuevo. Revisa el
producto y lo firma; cualquier escritura posterior anula la firma. Firmar exige que el recorrido
esté completo: ningún enlace roto sin resolver.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. El cierre es la última palabra del auditor en el trabajo; sin esta historia,
el recorrido sería un índice automático que nadie responde.

**Independent Test**: con un informe de cierre propuesto, se comprueba que corregir una entrada de
la tabla con motivo queda en el historial; que una corrección que contradice el borrador firmado
se rechaza; que firmar desde «revisado» con firmante y justificación escribe la firma con la
huella de los bytes guardados; y que ningún camino llega a «firmado» sin la acción explícita del
auditor.

**Acceptance Scenarios**:

1. **Given** una entrada de la tabla de recorrido, **When** el auditor corrige su descripción con
   un motivo sin contradecir el borrador, **Then** el cambio queda registrado con autor, fecha,
   valor anterior, valor nuevo y motivo, y el producto pasa a «revisado».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y el informe no se
   modifica.
3. **Given** una corrección que contradice el borrador firmado, **When** se intenta registrar,
   **Then** se rechaza informando la contradicción y la huella que la decide.
4. **Given** un recorrido completo sin enlaces rotos, **When** el auditor firma con su nombre y
   una justificación, **Then** el producto queda «firmado» con la huella de sus bytes guardados;
   cualquier cambio posterior anula la firma.
5. **Given** un enlace roto sin resolver, **When** se intenta firmar, **Then** la firma se rechaza
   informando qué enlaces faltan por resolver.

---

### User Story 3 - Un enlace que no verifica se conserva como pendiente (Priority: P3)

Una huella citada no verifica, una ficha no se lee o una afirmación no llega hasta su evidencia.
El recorrido lo marca, la entrada se conserva como pendiente con su causa y el informe no se
presenta como cerrado hasta que el auditor corrija o declare. Ningún pendiente se maquilla como
verificado.

**Why this priority**: protege el sentido de la épica: «un informe que un tercero recorre hasta la
evidencia». Un recorrido con eslabones rotos no es un recorrido; declararlo es decisión del
auditor, no omisión de la herramienta (principios II y III).

**Independent Test**: con un informe al que se le rompe un enlace (huella alterada, ficha
ilegible), se comprueba que el recorrido lo marca con su causa, que el conteo de pendientes
aparece en una sola sección y que firmar queda bloqueado mientras haya pendientes sin resolver.

**Acceptance Scenarios**:

1. **Given** una huella que ya no corresponde a sus bytes, **When** se recorre el informe, **Then**
   la entrada se marca «no verifica» con la referencia exacta del enlace.
2. **Given** una ficha ilegible para el tercero, **When** se recorre el informe, **Then** la
   entrada se marca «ficha ilegible» y la causa queda registrada.
3. **Given** cualquier entrada, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta un pendiente como
   verificado.
4. **Given** un informe con K pendientes resueltos por el auditor (corregidos o declarados), **When**
   se resume, **Then** el resumen dice cuántos enlaces verificaron, cuántos se corrigieron y
   cuántos quedaron declarados, en una sola sección con su conteo.

---

### User Story 4 - El tercero recorre el informe hasta la evidencia (Priority: P3)

Una persona que no estuvo en la sala recorre el informe de cierre: parte del resumen, sigue cada
afirmación hasta su sección, su ficha y su evidencia, y verifica las huellas por sí misma. El
resultado de ese recorrido —cuántos enlaces verificaron, cuántos no y qué hizo el tercero— se
registra en el checklist humano. El informe se entiende sin haber estado en la sala.

**Why this priority**: es la entrega de la épica y el criterio de éxito de todo el ciclo S01–S10:
la trazabilidad completa, de la afirmación del informe a la evidencia con huella, demostrada por
alguien ajeno. Es también lo que el cliente recibe.

**Independent Test**: con el informe firmado, el tercero recorre una muestra de afirmaciones de
cada sección hasta sus evidencias y verifica sus huellas sin ayuda; se comprueba que cada enlace
del recorrido existió y que el registro del checklist humano queda escrito con los conteos.

**Acceptance Scenarios**:

1. **Given** el informe firmado, **When** el tercero recorre las afirmaciones del resumen, **Then**
   cada una lo lleva a su sección del desarrollo sin atajos ni enlaces muertos.
2. **Given** una afirmación del desarrollo, **When** el tercero sigue su enlace, **Then** llega a
   la ficha del riesgo citado, a su hecho y a su evidencia, y la huella verifica.
3. **Given** el recorrido terminado, **When** el tercero registra su resultado, **Then** el
   checklist humano queda con los conteos (enlaces recorridos, verificados, pendientes) y su
   identidad y fecha.
4. **Given** un informe recorrido sin ayuda, **When** se evalúa la lectura, **Then** el tercero
   declara haberlo entendido sin haber estado en la sala; el resultado se registra.

---

## Edge Cases

- El borrador de S09 no existe: `abrir` termina en código 2 sin escribir.
- El borrador existe pero no está firmado: `abrir` termina en código 5 sin escribir.
- El borrador cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4
  («el borrador de origen cambió»), sin escribir.
- Una huella del borrador dejó de corresponder desde que se firmó: el recorrido la marca «no
  verifica» antes de que el tercero empiece; el auditor corrige o declara.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- El informe contiene datos personales: se enmascaran o se rechazan; la herramienta no publica
  datos personales ni secretos.
- El tercero no verifica un enlace que la herramienta marcó como sano: el registro del checklist
  humano prevalece y la discrepancia queda anotada para el auditor.
- El JSON del cierre se altera un byte después de firmar: `verificar` lo detecta.
- El dueño aprueba publicar el informe: es una decisión fuera de la herramienta (constitución,
  «Flujo de trabajo y compuertas»); el cierre la deja lista, no la ejecuta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el cierre a partir de la entrega vigente de S09
  (`borrador.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada (código 2).
  Si el borrador no está firmado, MUST informarlo y no escribir nada (código 5).
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar el estado de firma de la cadena S01–S08.
- **FR-003**: El informe de cierre MUST contener las mismas secciones del borrador firmado, la
  tabla de recorrido y el registro del recorrido del tercero en blanco. El producto MUST NOT
  contener material que no conste en las entregas S01–S09.
- **FR-004**: La tabla de recorrido MUST tener una entrada por afirmación del informe: afirmación,
  sección, ficha de origen, huella esperada y estado del enlace (`verifica`, `no-verifica`,
  `ilegible`, `pendiente`, `declarado`).
- **FR-005**: Antes de registrar el recorrido del tercero, la herramienta MUST recalcular cada
  huella de la tabla contra sus bytes. MUST detectar la alteración de un byte y MUST marcar el
  enlace antes del recorrido. Un enlace «no-verifica» o «ilegible» MUST resolverse —corregir o
  declarar con motivo— antes de firmar.
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles generadas por la
  herramienta. Las conclusiones que el auditor formule MUST quedar como su texto firmado,
  identificado como tal.
- **FR-007**: El auditor MUST poder corregir la redacción del informe y la agrupación de la tabla,
  cada cambio con autor, fecha, valor anterior, valor nuevo y motivo obligatorio, dejando el
  producto en «revisado». Una corrección que contradiga el borrador firmado MUST rechazarse
  informando la contradicción. Ningún dato se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que no queden enlaces sin resolver, y MUST rechazar
  firmar desde «borrador» o sin firmante o sin justificación. Firmar el cierre MUST NOT abrir la
  compuerta ni publicar nada.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S09 contra la registrada; la huella de cada enlace
  de la tabla contra sus bytes; y la huella de cada evidencia citada. MUST detectar la alteración
  de un byte.
- **FR-010**: Con las mismas entregas y las mismas correcciones, la herramienta MUST producir el
  mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `04_informe/`, sin crear un
  árbol paralelo ni sobrescribir los productos previos de esa carpeta (incluidos los del ciclo
  S01–S09 y los de la corrida previa de la plataforma), y ser legible por un tercero sin la
  herramienta.
- **FR-012**: Debe escribirse el informe legible `04_informe/informe-cierre.md` con el mismo
  contenido del JSON, la tabla de recorrido como anexo, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST dejar el registro del recorrido del tercero listo para el
  checklist humano: conteos por estado, identidad y fecha del tercero y observaciones. El
  recorrido MUST NOT ser simulado por la herramienta: lo ejecuta el tercero.
- **FR-014**: Si el borrador de origen cambió (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor MUST exigir que el borrador de origen no haya cambiado
  desde `abrir`; si cambió, se rechazan con código 4 sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija; los datos personales se enmascaran.

### Key Entities

- **Cierre**: producto de S10. Referencia la entrega del borrador de la que deriva (huella y
  estados de firma de la cadena S01–S09). Agrupa el informe, la tabla de recorrido, el registro
  del tercero, el estado de aprobación, el historial y la firma.
- **Tabla de recorrido**: una entrada por afirmación del informe, con su sección, su ficha, su
  huella esperada y el estado del enlace.
- **Registro del recorrido**: resultado del tercero: conteos por estado, identidad, fecha y
  observaciones; se completa en el checklist humano.
- **Enlace resuelto**: un enlace que verificó, o que el auditor corrigió o declaró con motivo.
- **Corrección**: autor, fecha, entrada afectada, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con el borrador firmado de prueba, el informe de cierre contiene el 100 % de sus
  secciones y la tabla de recorrido cubre el 100 % de las afirmaciones.
- **SC-002**: El 100 % de los enlaces de la tabla llegan a una ficha legible y a una huella; el
  tercero recorre una muestra de cada sección hasta la evidencia sin ayuda.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos, credenciales y datos personales sin enmascarar.
- **SC-004**: La alteración de un solo byte del JSON del producto, de la tabla o de una evidencia
  citada se detecta en el 100 % de los casos.
- **SC-005**: El 100 % de los enlaces «no-verifica» o «ilegible» se resuelven antes de la firma:
  corregidos o declarados con motivo (FR-005).
- **SC-006**: Ningún cierre llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: Abrir y corregir el cierre solo crean archivos nuevos en `04_informe/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-009**: Con el borrador ausente, `abrir` termina en código 2; con el borrador sin firmar,
  en código 5; ninguno escribe (FR-001).
- **SC-010**: El registro del recorrido del tercero queda completo: conteos por estado, identidad
  y fecha; si el tercero no verificó un enlace sano, la discrepancia queda anotada.
- **SC-011**: Con el producto firmado y el borrador cambiado, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).
- **SC-012**: El informe se entiende sin haber estado en la sala: el tercero lo declara y el
  resultado se registra en el checklist humano (principio VIII).

## Assumptions

- **Origen de la descripción**: como en S02–S09, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S10 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S09 y de la constitución (principios I, II, III, IV y VIII).
- El cliente del informe es Comercial Andes Sur SpA, como declara `docs/PROMPT_SPEC_KIT.md`.
- Hay un solo rol humano en la construcción, el auditor; el tercero del recorrido es un rol de
  verificación, no de construcción. La revisión por segundo par (#33) queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S10 no recolecta material nuevo, no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la
  entrega de S09 (y a través de ella la cadena S01–S08) y escribe en `04_informe/`.
- Publicar, entregar al cliente o subir el informe a GitHub son decisiones del dueño, fuera de
  esta funcionalidad; el cierre las deja listas, no las ejecuta.
- **Dependencias**: la entrega de S09 (`borrador.entregar`, FR-013 de S09) y la cadena S01–S08;
  `alcance.serializar`, `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: la entrega física o publicación del informe; la reauditoría o
  reevaluación posterior al cierre; cualquier escritura fuera de `04_informe/`; emitir un
  dictamen de cumplimiento (el informe presenta trabajo verificable; las conclusiones firmadas
  son texto del auditor, identificado como tal).
