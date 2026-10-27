# Feature Specification: S09 — El borrador

**Feature Branch**: `009-borrador-informe` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S09, El borrador». Novena épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S09 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, armaba el borrador del informe de cierre. La
herramienta deja **el borrador**.

**Épica**: S09 de S01–S10. **Recibe**: la entrega de S08 (`frases.entregar`): el mismo resultado
dicho para la gerencia y para quien corrige, con conteos verificados y la huella del encargo que
consolida todo el trabajo. **Produce**: el borrador. **Entrega a S10 (El cierre)**: el informe de
cierre en borrador, con todas sus secciones derivadas de las entregas S01–S08 y citando sus
huellas, para que S10 deje un informe que un tercero recorre hasta la evidencia.

**Lugar en el proceso de auditoría**: S09 corresponde a la fase Informar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`04_informe/`. La herramienta propone el borrador ensamblando las entregas; el auditor lo corrige
y lo firma. Un borrador no dictamina: presenta el trabajo hecho, no un cumplimiento.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S08 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S09 necesita un «mínimo de referencia» cuando faltan las frases de S08? → A: No. El
  borrador se alimenta de las dos frases; sin ellas, armarlo sería escribir otro informe, no el
  de este trabajo. Si falta la entrega de S08, `borrador abrir` se detiene con el código 2 y no
  escribe nada.
- Q: ¿El borrador sobrescribe los informes previos de `04_informe/`? → A: No. Los archivos
  actuales de la carpeta (`informe_tecnico.md`, `resumen_ejecutivo.md`, `plan_remediacion.md`,
  entre otros) pertenecen a la corrida previa de la plataforma y quedan intactos; el borrador es
  archivos nuevos (igual que S03 protegió `03_hallazgos/`).
- Q: ¿El borrador incluye el plan de remediación? → A: incluye una sección de acciones sugeridas
  para quien corrige, derivadas de las frases y de lo que falta; es propuesta de la herramienta
  que el auditor corrige, sin plazos inventados ni responsables inventados (la constitución
  prohíbe inventar responsables y fechas en el trabajo ágil; el borrador hereda esa regla).
- Q: ¿Qué secciones tiene el borrador? → A: las que el trabajo sostiene: encabezado con cliente
  (Comercial Andes Sur SpA) y alcance; la frase de gerencia como resumen; el desarrollo con los
  riesgos citados, el perfil por funciones y la lista CIS; la frase de quien corrige con las
  acciones sugeridas; los vacíos declarados; y el anexo de trazabilidad con las huellas. Ninguna
  sección se rellena con material que no conste en las entregas.
- Q: ¿Una sección sin material se omite? → A: No. Se conserva con su «no consta» y su motivo,
  igual que en los sprints anteriores.
- Evaluación de coherencia (2026-10-26): cada sección del borrador cita la huella de la entrega
  de la que deriva; si esa entrega cambia, `abrir` lo señala y, estando firmado, no escribe.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el borrador sin las frases (Priority: P1) 🎯 MVP

El auditor abre el borrador a partir de la entrega de S08. Las frases no existen: la herramienta
se detiene y lo informa, sin escribir nada. Si existen, la herramienta propone el borrador
completo: encabezado con cliente y alcance, la frase de gerencia, el desarrollo con riesgos
citados, perfil y lista, la frase de quien corrige con acciones sugeridas, los vacíos declarados
y el anexo de trazabilidad, cada parte con la huella de la entrega de la que deriva.

**Why this priority**: es el producto mínimo viable de S09. Ensambla el informe de cierre sin
redactar nada nuevo: todo sale de las entregas S01–S08; es la entrada del cierre de S10.

**Independent Test**: con una entrega de S08 cuyo encargo consolida hechos, riesgos y vacíos, se
comprueba que el borrador tiene todas las secciones, que cada una cita la huella de su entrega,
que ninguna contiene estados de cumplimiento y que los archivos previos de `04_informe/` quedan
con huella idéntica.

**Acceptance Scenarios**:

1. **Given** una entrega con R riesgos y V vacíos, **When** el auditor abre el borrador, **Then**
   el borrador tiene todas sus secciones, el desarrollo trata los R riesgos citados, los vacíos
   se declaran en su sección y cada sección cita la huella de la entrega de la que deriva.
2. **Given** que la entrega de S08 no existe, **When** el auditor abre el borrador, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `04_informe/`.
3. **Given** las frases firmadas y las entregas del encargo firmadas, **When** se abre el
   borrador, **Then** el producto declara el estado de firma de las entregas de las que deriva.
4. **Given** los archivos previos de `04_informe/`, **When** se abre y corrige el borrador,
   **Then** esos archivos quedan con huella idéntica.

---

### User Story 2 - La herramienta propone el borrador y el auditor corrige (Priority: P2)

El auditor corrige la redacción de cualquier sección, reordena el desarrollo o ajusta las
acciones sugeridas para quien corrige, con motivo; cada cambio queda en el historial con autor,
fecha, valor anterior y valor nuevo. Revisa el producto y lo firma; cualquier escritura posterior
anula la firma. Firmar exige que todas las secciones estén completas y consistentes con las
entregas.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. El borrador es el informe del auditor ante el cliente; sin esta historia sería
un compilado automático.

**Independent Test**: con un borrador propuesto, se comprueba que corregir una sección con motivo
queda en el historial; que una corrección que contradice su entrega de origen se rechaza; que
firmar desde «revisado» con firmante y justificación escribe la firma con la huella de los bytes
guardados; y que ningún camino llega a «firmado» sin la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** una sección propuesta, **When** el auditor corrige su redacción con un motivo sin
   contradecir su entrega de origen, **Then** el cambio queda registrado con autor, fecha, valor
   anterior, valor nuevo y motivo, y la sección pasa a «revisada».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y el borrador no se
   modifica.
3. **Given** una corrección que contradice la entrega de origen de la sección, **When** se
   intenta registrar, **Then** se rechaza informando la contradicción y la huella que la decide.
4. **Given** un producto revisado con todas las secciones completas, **When** el auditor firma con
   su nombre y una justificación, **Then** el producto queda «firmado» con la huella de sus bytes
   guardados; cualquier cambio posterior anula la firma.
5. **Given** una acción sugerida con responsable o plazo, **When** se intenta registrar, **Then**
   se rechaza: las acciones se proponen sin responsables ni fechas inventados.

---

### User Story 3 - Una sección sin material se conserva con su «no consta» (Priority: P3)

Una parte del trabajo quedó vacía: una función del perfil sin material, una lista sin controles
confirmados, un dominio sin verificar. La sección correspondiente del borrador se conserva con su
«no consta» y su motivo, visible para el cliente, y no se omite ni se maquilla. El anexo de
trazabilidad la incluye con su conteo.

**Why this priority**: protege la diferencia entre «informar incompleto» y «informar limpio». Un
borrador que omite las secciones vacías presenta un trabajo que no se hizo como si no existiera
(principio II).

**Independent Test**: con entregas que tienen secciones vacías de distinta causa, se comprueba
que el borrador las conserva con motivo, que el conteo de vacíos coincide con el de S08 y que
ninguna sección vacía se presenta como favorable.

**Acceptance Scenarios**:

1. **Given** una función del perfil «no consta», **When** se abre el borrador, **Then** la
   sección del desarrollo correspondiente declara el vacío con su motivo.
2. **Given** un dominio sin verificar por compuerta cerrada, **When** se abre el borrador, **Then**
   la sección de vacíos lo declara con su causa, igual que las frases de S08.
3. **Given** cualquier sección, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta un vacío como
   resultado favorable.
4. **Given** un producto con V vacíos, **When** se resume, **Then** el resumen dice cuántas
   secciones tienen material y cuántas quedan «no consta», en una sola sección con su conteo.

---

### User Story 4 - Verificar el borrador y entregarlo a S10 (Priority: P3)

El auditor verifica el borrador: la huella de los bytes guardados sigue correspondiendo a la
firma, la huella de la entrega de S08 sigue siendo la registrada, cada sección sigue coincidiendo
con su entrega de origen y las huellas citadas verifican. Si las frases cambiaron después de
firmar, la herramienta no actualiza sola. La entrega a S10 contiene el borrador completo, listo
para el recorrido del tercero.

**Why this priority**: es el contrato con S08 y el principio III: un borrador solo se puede
cerrar si todo lo que cita sigue en pie. Es también la entrada del cierre de S10.

**Independent Test**: con un producto firmado, se altera un byte del JSON y de una evidencia
citada en el anexo, y se comprueba que `verificar` lo detecta; se cambian las frases de origen y
se comprueba que `abrir` informa y, estando firmado, no escribe; se comprueba que `entregar`
devuelve el borrador completo con sus huellas.

**Acceptance Scenarios**:

1. **Given** una sección cuya entrega de origen ya no corresponde a la huella registrada, **When**
   se verifica, **Then** la sección se informa con «origen alterado» y queda marcada para el
   auditor.
2. **Given** un producto firmado cuyas frases de origen cambiaron, **When** se abre de nuevo,
   **Then** la herramienta informa el cambio y no escribe (código 4).
3. **Given** una huella del anexo que no verifica, **When** se verifica, **Then** el anexo lo
   informa con la referencia exacta del enlace roto.
4. **Given** un borrador consistente, **When** se entrega a S10, **Then** la entrega contiene
   todas las secciones, las huellas de las entregas S01–S08, el estado de firma y los conteos
   verificados.

---

## Edge Cases

- Las frases de S08 no existen: `abrir` termina en código 2 sin escribir.
- La entrega tiene cero riesgos: el desarrollo lo declara y las secciones de riesgos citados
  quedan «no consta»; ninguna dice «sin hallazgos».
- Las frases cambian entre `abrir` y una acción del auditor: la acción se rechaza con código 4
  («las frases de origen cambiaron»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- El anexo cita una evidencia que es referencia sin copia: lo declara y remite al original.
- El auditor quiere añadir una sección nueva a mano: se registra como su aporte con motivo y
  pasa por el mismo filtro; la sección no puede contradecir las entregas.
- El JSON del borrador se altera un byte después de firmar: `verificar` lo detecta.
- Una entrega intermedia cambia aunque S08 siga igual: `abrir` lo señala (el encargo declara sus
  huellas) y no escribe hasta la decisión del auditor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el borrador a partir de la entrega vigente de S08
  (`frases.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar el estado de firma de las entregas S01–S08.
- **FR-003**: El borrador MUST tener estas secciones: encabezado (cliente, alcance con su huella),
  resumen para la gerencia (la frase de gerencia), desarrollo (riesgos citados, perfil por
  funciones, lista CIS), acciones sugeridas para quien corrige (la frase de quien corrige), vacíos
  declarados y anexo de trazabilidad (huellas de las entregas y de las evidencias citadas).
- **FR-004**: Cada sección MUST derivarse de la entrega que la sostiene y MUST citar su huella.
  El producto MUST NOT contener material que no conste en las entregas S01–S08.
- **FR-005**: Las secciones sin material MUST conservarse con su «no consta» y su motivo. El
  producto MUST NOT omitirlas ni presentarlas como favorables.
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles, y las acciones
  sugeridas MUST NOT incluir responsables ni fechas inventados.
- **FR-007**: El auditor MUST poder corregir la redacción de cualquier sección, reordenar el
  desarrollo y ajustar las acciones sugeridas, y añadir secciones a mano. Cada corrección registra
  autor, fecha, valor anterior, valor nuevo y motivo obligatorio, y deja la sección en «revisado».
  Una corrección que contradiga su entrega de origen MUST rechazarse informando la contradicción.
  Ninguna sección se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que todas las secciones estén completas, y MUST rechazar
  firmar desde «borrador» o sin firmante o sin justificación. Firmar el borrador MUST NOT abrir la
  compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S08 contra la registrada; la huella de cada
  entrega intermedia declarada en el encargo; y la huella de cada evidencia citada en el anexo.
  MUST detectar la alteración de un byte y MUST informar «origen alterado» por sección y por
  enlace del anexo.
- **FR-010**: Con las mismas entregas y las mismas correcciones, la herramienta MUST producir el
  mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `04_informe/`, sin crear un
  árbol paralelo ni sobrescribir los productos previos de esa carpeta (`informe_tecnico.md`,
  `resumen_ejecutivo.md`, `plan_remediacion.md`, `matriz_normativas.md`, `mapa.html`, `mapa_cve_cwe_cvss.md`,
  `hallazgos.sarif.json`, `registro_*.md`, `PLANTILLA_CIERRE_C4A.md` y `README.md`), y ser legible
  por un tercero sin la herramienta.
- **FR-012**: Debe escribirse el informe legible `04_informe/borrador-informe-cierre.md` con el
  mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-013**: La herramienta MUST entregar a S10 el borrador completo: secciones, huellas de las
  entregas S01–S08, estado de firma de cada una y conteos verificados.
- **FR-014**: Si las frases de origen cambiaron (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor MUST exigir que las frases de origen no hayan cambiado
  desde `abrir`; si cambiaron, se rechazan con código 4 sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija.

### Key Entities

- **Borrador**: producto de S09. Referencia la entrega de las frases de la que deriva (huella y
  estados de firma de la cadena S01–S08). Agrupa las secciones, el estado de aprobación, el
  historial y la firma.
- **Sección**: una parte del informe (encabezado, resumen, desarrollo, acciones, vacíos, anexo).
  Tiene contenido derivado de su entrega de origen, con su huella, estado de aprobación, marcas y
  correcciones.
- **Acción sugerida**: propuesta para quien corrige, derivada de lo que falta; sin responsable ni
  fecha inventados.
- **Anexo de trazabilidad**: enlaces con huellas desde cada sección hasta su entrega y su
  evidencia, verificables de forma independiente.
- **Corrección**: autor, fecha, sección afectada, campo, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con R riesgos y V vacíos, el borrador tiene todas las
  secciones de FR-003, el desarrollo trata los R riesgos citados y los V vacíos se declaran.
- **SC-002**: El 100 % de las secciones citan la huella de su entrega de origen y el producto
  declara el estado de firma de S01–S08.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-004**: La alteración de un solo byte del JSON del producto o de una evidencia citada en el
  anexo se detecta en el 100 % de los casos (`verificar`).
- **SC-005**: El 100 % de las secciones sin material conservan su «no consta» con motivo (FR-005).
- **SC-006**: Ninguna sección llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: Abrir y corregir el borrador solo crean archivos nuevos en `04_informe/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-009**: La entrega a S10 contiene el borrador completo con las huellas de S01–S08 y los
  conteos verificados, sin inconsistencias abiertas.
- **SC-010**: Una corrección que contradice su entrega de origen se rechaza en el 100 % de los
  casos, con la huella que la decide.
- **SC-011**: El anexo de trazabilidad verifica de forma independiente: cada huella citada
  corresponde a sus bytes, y un enlace roto se informa con su referencia exacta.
- **SC-012**: Con el producto firmado y las frases cambiadas, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: como en S02–S08, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S09 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S08 y de la constitución (principios I, II, III y IV).
- El cliente del informe es Comercial Andes Sur SpA, como declara `docs/PROMPT_SPEC_KIT.md`.
- Hay un solo rol humano, el auditor, que corrige y firma. La revisión por segundo par (#33)
  queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S09 no recolecta material nuevo, no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la
  entrega de S08 (y a través de ella la cadena S01–S07) y escribe en `04_informe/`.
- El borrador es el insumo del cierre: la publicación o entrega al cliente es trabajo del cierre
  (S10) y de la decisión del dueño, no de esta épica.
- **Dependencias**: la entrega de S08 (`frases.entregar`, FR-013 de S08) y la cadena S01–S07 que
  el encargo consolida; `alcance.serializar`, `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: el recorrido del tercero y el informe final (S10); publicar o
  entregar el informe; medir cumplimiento; cualquier escritura fuera de `04_informe/`.
