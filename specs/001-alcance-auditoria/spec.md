# Feature Specification: S01 — El alcance

**Feature Branch**: `001-alcance-auditoria` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-19

**Status**: Draft

**Input**: Descripción del usuario: «S01 — El alcance. Primera épica del ciclo de construcción
(sprint S01 de S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Qué hacía el
auditor a mano: decidir qué entra y qué no en la auditoría. Qué deja la herramienta: el alcance.»
El texto completo del encargo (insumos, producto, entrega a S02, historias mínimas, requisitos
transversales y exclusiones) está en el mensaje que invocó `/speckit-specify` y se resume en las
secciones siguientes.

**Épica**: S01 de S01–S10. **Recibe**: ningún producto de sprint anterior; mínimo de referencia
`scope/alcance.md` y `scope/autorizacion.md`. **Produce**: el alcance. **Entrega a S02 (El registro)**:
el alcance firmado, o explícitamente en borrador, que delimita qué hechos se pueden registrar y sobre
qué activo.

**Lugar en el proceso de auditoría**: S01 corresponde a la fase Planificar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `AUDIT_PROMPT.md`). El alcance es la entrada de la
Fase 1 (`01_plan/`): sin alcance no hay plan, y sin plan y autorización firmada y vigente no hay
Fase 2. La herramienta propone el alcance; el auditor lo corrige y lo firma.

## Clarifications

### Session 2026-10-21

- Q: ¿Cómo se firma el alcance? (FR-012) → A: Opción A. Se registra firmante, fecha y huella
  SHA-256 de los bytes guardados del alcance, reutilizando el mecanismo de huellas de `platform/c4a`.
  Sin claves GPG ni firma electrónica avanzada. Cualquier cambio posterior anula la firma y devuelve
  el alcance a «revisado» (principio III; verifica SC-006 y SC-007).
- Q: ¿Se puede firmar el alcance con la compuerta de autorización cerrada? → A: Sí, son
  independientes. Firmar el alcance fija qué se audita; no abre la compuerta ni autoriza pruebas.
- Q: ¿S01 trabaja con un solo rol humano? → A: Sí, el auditor corrige y firma. La revisión por un
  segundo par (#33) queda fuera de S01.
- Q: ¿El producto es un archivo nuevo dentro de `scope/`? → A: Sí. El alcance se guarda en archivos
  nuevos de `scope/`; `scope/alcance.md` y `scope/autorizacion.md` son insumos de solo lectura para la
  herramienta.
- Q: ¿Se mantiene SC-003 (menos de 10 minutos)? → A: Se mantiene y se hace verificable: el borrador
  agrupa los pendientes en una sola sección con su conteo (verificación automática); los minutos los
  mide el auditor y se registran como verificación manual.
- Decisión del dueño: la spec se conserva y se enriquece con los documentos de alcance y el análisis
  del proceso de auditoría de cumplimiento (cuatro fases; la herramienta propone, el auditor firma);
  no se reescribe desde cero.
- Decisión del dueño: plan, investigación, modelo de datos, guía rápida y contratos se completan con
  lo que consta en el repositorio; lo que no consta queda «pendiente de confirmar» o «VALIDAR».
- Decisión del dueño: `checklists/requirements.md` queda aprobado por el dueño (2026-10-21). No
  sustituye al checklist humano de `/speckit-checklist`, que es otro artefacto.
- Decisión del dueño: el checklist de `/speckit-checklist` se construye y completa marcando cada ítem
  solo con evidencia citada del repositorio; lo no evidenciable queda abierto y declarado.
- Decisión del dueño: `tasks.md` se construye en orden de dependencia y se reconcilia con el Project
  #7 y las issues existentes en solo lectura. Ninguna escritura en GitHub sin aprobación expresa.
- Decisión del dueño: el dueño autoriza el ejercicio de laboratorio (Metasploitable 2). En
  `scope/autorizacion.md` se completa solo lo que ya consta en el repositorio; firmante, facultad,
  origen del auditor, ventana y contacto de emergencia quedan «por completar». La compuerta técnica
  sigue cerrada hasta que el documento esté firmado y con ventana vigente (principio V). Esta decisión
  habilita todo el ciclo SDD, no comandos de red.
- Decisión del dueño: se crea `.specify/extensions.yml` con estructura válida y sin hooks que apunten
  a comandos inexistentes.
- Q: ¿Se puede firmar el alcance con pendientes? (compuerta F, CHK033) → A: Sí. El registro de firma
  guarda cuántos pendientes había y la vista lo muestra.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Proponer el alcance con insumos incompletos (Priority: P1)

El auditor pide a la herramienta un borrador de alcance. No hay producto de un sprint anterior, y el
documento de alcance del repositorio está incompleto. La herramienta usa el mínimo de referencia
(lo declarado en el documento de alcance y el estado de la autorización), arma el borrador con todo
lo que consta, señala cada vacío como fila «pendiente de confirmar» y no inventa ningún valor.

**Why this priority**: sin un alcance no hay nada que registrar, enunciar ni citar en los sprints
siguientes. Es el producto mínimo viable de S01: aun incompleto, le dice al auditor qué falta.

**Independent Test**: se entrega a la herramienta un documento de alcance con campos vacíos o
ausentes y se comprueba que el borrador contiene todo lo declarado, con su fuente, y una fila
pendiente por cada vacío, sin valores que no estén en los insumos.

**Acceptance Scenarios**:

1. **Given** un documento de alcance que declara el activo, los marcos y los dominios, pero no las
   exclusiones de activos, **When** el auditor pide el borrador, **Then** el borrador incluye el
   activo, los marcos y los dominios con la fuente de cada uno, y una fila «pendiente de confirmar»
   para las exclusiones de activos.
2. **Given** que el documento de alcance no existe, **When** el auditor pide el borrador, **Then** la
   herramienta informa que falta el insumo, entrega un borrador con la estructura mínima y todas sus
   filas en «pendiente de confirmar», y no rellena ningún valor.
3. **Given** un documento de alcance que declara más de un activo o ninguno, **When** el auditor pide
   el borrador, **Then** la fila del activo queda «pendiente de confirmar» con la observación de que el
   ejercicio admite un solo activo.
4. **Given** un documento de alcance que identifica el activo con su dirección de red, **When** se
   genera el borrador, **Then** el activo aparece nombrado por tipo y rol, y la dirección no se copia.

---

### User Story 2 - El auditor corrige y firma la propuesta (Priority: P2)

El auditor revisa el borrador y cambia un dominio de incluido a excluido, indicando el motivo. La
herramienta registra el cambio con autor, fecha, valor anterior, valor nuevo y motivo, y deja el
alcance en estado «revisado». Solo cuando el auditor lo firma el alcance queda «firmado».

**Why this priority**: es la separación central de la constitución: la herramienta propone y el
auditor decide. Sin esta historia, el alcance sería una conclusión automática.

**Independent Test**: sobre un borrador generado, se registra una corrección y luego una firma, y se
comprueba el historial, los cambios de estado y que nada pasa a «firmado» sin la acción del auditor.

**Acceptance Scenarios**:

1. **Given** un borrador con el dominio «cifrado en tránsito» incluido, **When** el auditor lo cambia
   a excluido con un motivo, **Then** el cambio queda registrado con autor, fecha, valor anterior,
   valor nuevo y motivo, y el estado del alcance pasa a «revisado».
2. **Given** un intento de cambiar un dominio sin motivo, **When** se intenta registrar, **Then** el
   cambio se rechaza y el borrador no se modifica.
3. **Given** un alcance «revisado», **When** el auditor lo firma, **Then** el estado pasa a «firmado»
   con el nombre del firmante, la fecha y la huella del contenido firmado.
4. **Given** un alcance «firmado», **When** se modifica cualquier fila, **Then** la firma deja de
   aplicar, el estado vuelve a «revisado» y se exige una nueva firma.
5. **Given** que la herramienta vuelve a proponer el borrador después de una corrección, **When** los
   insumos no cambiaron, **Then** las correcciones del auditor se conservan y no se pierden.

---

### User Story 3 - Un dato no consta y la fila se conserva (Priority: P3)

La ventana temporal de la autorización no está informada. La herramienta conserva la fila de la
ventana como «pendiente de confirmar» e informa la compuerta como cerrada. No borra la fila, no la
rellena y no abre la compuerta.

**Why this priority**: protege la compuerta de seguridad y la trazabilidad de lo que falta. Se apoya
en el borrador de la historia 1.

**Independent Test**: con una autorización sin ventana informada, se comprueba que la fila existe,
está pendiente, y que la compuerta se informa cerrada con el motivo.

**Acceptance Scenarios**:

1. **Given** una autorización sin ventana informada, **When** se genera el borrador, **Then** la fila
   de la ventana existe como «pendiente de confirmar» y la compuerta se informa «cerrada» con motivo
   «ventana no informada».
2. **Given** una autorización marcada como no firmada, **When** se genera el borrador, **Then** la
   compuerta se informa «cerrada» con motivo «no firmada», aunque el alcance mismo esté firmado.
3. **Given** una autorización firmada y completa cuya ventana ya terminó, **When** se genera el
   borrador, **Then** la compuerta se informa «cerrada» con motivo «ventana vencida».
4. **Given** cualquier estado de la autorización, **When** la herramienta trabaja, **Then** el
   documento de autorización no se modifica.

---

### User Story 4 - Entregar el alcance a S02 (Priority: P3)

Al preparar el registro de hechos del sprint siguiente, el auditor consulta si un activo o un dominio
está dentro del alcance. La herramienta responde «dentro», «fuera» o «pendiente», citando la fila del
alcance que lo decide.

**Why this priority**: es el contrato con S02. Sin él, un hecho fuera del alcance podría registrarse
como evidencia de esta auditoría.

**Independent Test**: con un alcance que tiene filas dentro, fuera y pendientes, se consulta cada
caso y se comprueba la respuesta y la fila citada.

**Acceptance Scenarios**:

1. **Given** un dominio excluido, **When** se consulta, **Then** la respuesta es «fuera», con la fila y
   el motivo de la exclusión.
2. **Given** un activo distinto del declarado, **When** se consulta, **Then** la respuesta es «fuera»,
   y un hecho sobre ese activo no se acepta como evidencia de esta auditoría.
3. **Given** un dominio en «pendiente de confirmar», **When** se consulta, **Then** la respuesta es
   «pendiente», no «dentro».
4. **Given** un alcance en borrador, **When** se consulta, **Then** la respuesta indica explícitamente
   que el alcance no está firmado.

---

### Edge Cases

- El documento de alcance cita un marco sin versión: el marco aparece con versión «pendiente de
  confirmar»; no se completa con la versión de referencia sin decisión del auditor.
- El documento de alcance cita un marco con una versión distinta de la de referencia de la
  constitución (por ejemplo, otra versión de CIS Controls): se conserva lo declarado y se señala la
  diferencia para que el auditor decida.
- Un marco está mencionado pero la herramienta no tiene su catálogo, o solo tiene un subconjunto: el
  estado lo dice («mencionado» o «implementado parcialmente», con la cobertura declarada); ser
  seleccionable no acredita cobertura.
- Una ley figura como aplicable sin fuente oficial, fecha de consulta o fundamento de aplicabilidad: la
  fila queda en «VALIDAR».
- Una ley figura con un estado de vigencia anotado como antecedente histórico: se conserva como
  antecedente con su fecha, no como vigencia verificada.
- El documento de alcance pide un tratamiento de evidencia (por ejemplo, almacenamiento cifrado) que
  el sistema no garantiza: se conserva como requisito declarado y queda «pendiente de confirmar»;
  tener huellas de integridad no equivale a cifrado.
- El documento de alcance incluye dominios de control que requieren políticas, personas o procesos:
  se conservan como incluidos, con la nota de que no se acreditan con una prueba técnica.
- El archivo del alcance guardado se altera después de firmado: la verificación de integridad lo
  detecta y el alcance deja de considerarse firmado.
- Los insumos cambian después de una firma: la herramienta advierte que el alcance firmado se basó en
  otra versión de los insumos y no lo actualiza sola.
- El alcance contiene datos personales del firmante o de contactos: solo se registra lo que ya consta
  en el repositorio, y nada de eso se publica fuera de él.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST generar un borrador de alcance a partir del documento de alcance y
  del documento de autorización del repositorio, sin requerir ningún producto de un sprint anterior.
- **FR-002**: La herramienta MUST informar cada insumo faltante o incompleto y representar cada dato
  ausente como una fila «pendiente de confirmar». MUST NOT eliminar esas filas ni rellenarlas con
  valores que no estén en los insumos.
- **FR-003**: El borrador MUST declarar un único activo, nombrado por tipo y rol tal como los dice
  el insumo (por ejemplo, tipo «host» y rol «objetivo del laboratorio»). Si los insumos declaran cero o
  más de un activo, la fila queda «pendiente de confirmar».
- **FR-004**: El borrador MUST NOT contener direcciones de red, comandos, puertos, credenciales ni
  procedimientos de explotación. Para el detalle de red, remite al documento de autorización.
- **FR-005**: El borrador MUST listar cada marco con nombre, versión y estado en la herramienta
  («mencionado», «implementado parcialmente» con la cobertura declarada, o «implementado»). Los
  marcos de referencia son ISO/IEC 27001:2022, NIST CSF 2.0 con sus seis funciones y CIS Controls
  v8.1.
- **FR-006**: Las leyes MUST registrarse solo como obligación candidata, con fuente oficial, fecha de
  consulta, artículo y fundamento de aplicabilidad (principio IV). Si falta alguno, la fila queda en
  «VALIDAR».
- **FR-007**: Cada dominio y cada exclusión MUST figurar como incluido o excluido con su motivo. Si el
  insumo no da el motivo en el mismo ítem, la fila queda «pendiente de confirmar» y conserva lo
  declarado (incluido o excluido) para que el auditor lo confirme. El título de una sección no es un
  motivo.
- **FR-008**: El borrador MUST informar la compuerta de autorización con tres atributos: firma
  (firmada / no firmada), completitud (completa / incompleta) y ventana (vigente / vencida / no
  informada). Si cualquiera de los tres no es favorable o no consta, la compuerta se informa «cerrada»
  con su motivo. Una fecha de la ventana que no se puede leer se trata como «no informada».
- **FR-009**: La herramienta MUST NOT abrir la compuerta ni modificar el documento de autorización ni
  el documento de alcance de origen.
- **FR-010**: Cada fila MUST indicar su fuente (archivo del repositorio y sección) o declarar que no
  tiene fuente, y llevar un estado de aprobación: «borrador», «revisado» o «firmado».
- **FR-011**: El auditor MUST poder corregir cualquier fila. Cada corrección registra autor, fecha,
  valor anterior, valor nuevo y motivo obligatorio, y deja el alcance en «revisado».
- **FR-012**: Solo una acción explícita del auditor MUST dejar el alcance en «firmado». La firma
  registra nombre del firmante, fecha, justificación (principio I) y huella SHA-256 de los bytes
  guardados del alcance; no usa
  claves ni firma electrónica avanzada. Cualquier cambio posterior invalida la firma y devuelve el
  estado a «revisado». Firmar el alcance MUST NOT abrir la compuerta de autorización. Firmar un alcance
  en «borrador» MUST rechazarse: la firma exige al menos una corrección o una revisión registrada.
  Firmar sin nombre del firmante o sin justificación MUST rechazarse.
- **FR-013**: Al volver a generar el borrador, la herramienta MUST conservar las correcciones del
  auditor. Si los insumos cambiaron, MUST señalar las filas afectadas en lugar de sobrescribirlas.
- **FR-014**: La huella de integridad publicada del alcance guardado MUST corresponder exactamente a
  los bytes guardados. Una verificación independiente MUST detectar cualquier alteración.
- **FR-015**: El alcance MUST NOT contener estados de cumplimiento ni conclusiones sobre controles:
  delimita qué se audita, no dictamina.
- **FR-016**: La herramienta MUST responder si un activo o dominio está «dentro», «fuera» o
  «pendiente», citando la fila que lo decide e indicando si el alcance está firmado. Un hecho sobre
  algo «fuera» no se acepta como evidencia de esta auditoría.
- **FR-017**: El alcance MUST guardarse en archivos nuevos dentro de `scope/`, sin crear un árbol de
  carpetas paralelo ni sobrescribir `scope/alcance.md` ni `scope/autorizacion.md`, y ser legible por un
  tercero sin la herramienta.
- **FR-019**: El borrador MUST agrupar todas las filas «pendiente de confirmar» y «VALIDAR» en una
  sola sección, con su conteo, de modo que el auditor las identifique sin abrir otros archivos.
- **FR-018**: Con los mismos insumos y las mismas correcciones, la herramienta MUST producir el mismo
  borrador.

### Key Entities

- **Alcance**: producto de S01. Agrupa el activo, los marcos, las obligaciones candidatas, los
  dominios, el estado de la compuerta, las filas pendientes, el estado de aprobación, el historial de
  correcciones y la firma. Referencia la versión de los insumos de la que se derivó.
- **Fila de alcance**: una afirmación del alcance. Tiene tipo (activo, parte, marco, obligación,
  dominio, exclusión, regla, compuerta), valor, decisión (incluido, excluido o pendiente de confirmar), motivo, fuente y
  estado de aprobación.
- **Activo**: el único objeto auditado, nombrado por tipo y rol, sin direcciones de red.
- **Marco de referencia**: nombre, versión, estado en la herramienta y cobertura declarada.
- **Obligación candidata**: norma legal con fuente oficial, fecha de consulta, fundamento de
  aplicabilidad y marca «VALIDAR» cuando falta alguno.
- **Estado de compuerta**: firma, completitud y ventana de la autorización, más el resultado
  (abierta o cerrada) y su motivo. Es de solo lectura para la herramienta.
- **Corrección**: autor, fecha, fila afectada, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación y huella del contenido firmado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con un documento de alcance de prueba que tiene N vacíos conocidos, el borrador muestra
  exactamente N filas pendientes y cero valores ausentes de los insumos. Cuenta como vacío: un campo
  «por completar», un dato ausente, un dominio o una exclusión sin motivo, un marco sin versión o no
  declarado, o una obligación sin fuente oficial, fecha de consulta, artículo o fundamento. Una fila
  pendiente es una «pendiente de confirmar» o una «VALIDAR».
- **SC-002**: El 100 % de las filas del borrador tienen fuente (o la declaración de que no la tienen) y
  estado de aprobación.
- **SC-003**: El auditor obtiene el borrador e identifica todos los pendientes en menos de 10 minutos,
  sin abrir otros archivos. Verificación automática: existe una sola sección de pendientes y su conteo
  coincide con las filas pendientes. Verificación manual: el auditor mide y registra el tiempo.
- **SC-004**: En el 100 % de los casos de prueba donde la firma, la completitud o la ventana no son
  favorables o no constan, la compuerta se informa «cerrada» con su motivo; en ningún caso la
  herramienta la abre.
- **SC-005**: Una búsqueda sobre el alcance generado encuentra cero direcciones de red, comandos,
  puertos y credenciales.
- **SC-006**: La alteración de un solo byte del alcance guardado se detecta en el 100 % de los casos.
- **SC-007**: Ningún alcance llega a «firmado» sin la acción explícita del auditor, y el 100 % de las
  correcciones registra autor, fecha y motivo.
- **SC-008**: Un tercero que no estuvo en la sala toma una fila de cada tipo presente en el alcance y
  la recorre hasta la sección citada de su archivo de origen sin ayuda; el resultado (filas recorridas
  y cuántas llegaron) se registra en el checklist humano. Verificación automática: el 100 % de las
  fuentes citadas existen como archivo y sección.
- **SC-009**: Dos propuestas con los mismos insumos y las mismas correcciones producen archivos
  idénticos byte a byte (FR-018).
- **SC-010**: El alcance generado contiene cero estados de cumplimiento («cumple», «parcial»,
  «no-cumple», «no-evaluado», «no-aplica») (FR-015).

## Assumptions

- **Origen de la descripción**: no se usaron las guías del curso. Por decisión del usuario quedan como
  referencia de autoestudio; la descripción se tomó de la fila S01 de `PROMPT_SPEC_KIT.md`, de
  `scope/alcance.md` y de `scope/autorizacion.md`.
- **Contrato de origen confirmado** (`LINEA_ORIGEN.md`): `scope/alcance.md`, `AUDIT_PROMPT.md` e
  `historia_usuario.md` son el contrato; no vuelven a «VALIDAR».
- Hay un solo rol humano, el auditor, que corrige y firma (aclarado 2026-10-21). La revisión por un
  segundo par (#33) queda fuera de S01.
- La firma del alcance es un registro de firmante, fecha y huella SHA-256 de los bytes guardados
  (aclarado 2026-10-21), no una firma electrónica avanzada.
- El alcance puede firmarse con la compuerta cerrada (aclarado 2026-10-21). Firmar el alcance no abre
  la compuerta ni autoriza pruebas.
- El producto del alcance son archivos nuevos dentro de `scope/` (aclarado 2026-10-21). La
  herramienta lee `scope/alcance.md` y `scope/autorizacion.md` y no los sobrescribe. Completar
  `scope/autorizacion.md` con datos que constan en el repositorio es una acción del dueño, no de la
  herramienta.
- Se puede firmar un alcance que aún tiene pendientes; el registro de firma guarda cuántos había
  (`research.md` D10; confirmado por el dueño el 2026-10-21 en la compuerta F).
- La autorización del dueño (2026-10-21) cubre el ejercicio de laboratorio; mientras
  `scope/autorizacion.md` no tenga firmante, facultad, ventana vigente y firma, la compuerta técnica
  se informa cerrada.
- Las leyes que hoy menciona el repositorio (Ley 21.663, Ley 21.719 y Ley 21.459 como delimitación
  de lo legalmente permitido) entran como obligaciones candidatas en «VALIDAR». Este sprint no hace
  validación jurídica.
- El cliente del informe de cierre (Comercial Andes Sur SpA, según `PROMPT_SPEC_KIT.md`) solo se
  registra como organización auditada si consta en la autorización. Si consta sin la firma de un
  representante con facultad, la fila conserva el valor y la compuerta sigue cerrada.
- La versión de CIS Controls v8.1 se tomó de la página oficial del CIS; su número de safeguards no
  está fijado y queda pendiente para S06.
- **Dependencias**: el documento de alcance y el de autorización existentes; el modelo de evidencia
  e integridad de `platform/c4a`, que debe cumplir el principio III de la constitución.
- **Fuera de esta funcionalidad**: ejecutar pruebas, registrar hechos (S02), enunciar riesgos (S03) y
  mapear controles (S04–S06).
