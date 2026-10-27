# Feature Specification: S07 — El encargo

**Feature Branch**: `007-encargo` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S07, El encargo». Séptima épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S07 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, dejaba el mismo trabajo escrito para que una
herramienta lo repita, sin firmar. La herramienta deja **el encargo**.

**Épica**: S07 de S01–S10. **Recibe**: la entrega de S06 (`lista.entregar`): los CIS Controls
seleccionados con sus justificaciones, anclajes y estados. **Produce**: el encargo. **Entrega a
S08 (Las dos frases)**: el mismo trabajo —activo, alcance, hechos a verificar, riesgos a
enunciar, citas a hacer, perfil a elaborar y lista a generar— escrito como datos que una
herramienta puede repetir, para que S08 diga el mismo resultado para la gerencia y para quien
corrige.

**Lugar en el proceso de auditoría**: el encargo consolida el trabajo de las fases Recopilar y
Analizar en una especificación repetible de la corrida; cae en `01_plan/`, la carpeta de la fase
Planificar. Es el plan de la corrida que se repite: la herramienta que lo ejecute vuelve a
Planificar → Recopilar → Analizar con estos datos. La compuerta sigue siendo
`scope/autorizacion.md`: el encargo no la abre ni la sustituye.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S06 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S07 necesita un «mínimo de referencia» cuando falta la lista de S06? → A: No. El encargo
  consolida el trabajo analizado; sin la lista no está completo. Si falta la entrega de S06,
  `encargo abrir` se detiene con el código 2 y no escribe nada.
- Q: ¿El encargo lleva firma del auditor? → A: No, por diseño de la guía («sin firmar»). El
  encargo no es un dictamen: es el trabajo escrito para repetir. Lleva autoría registrada (quién
  lo escribió y cuándo) y huella de integridad, pero no firma de aprobación; firmarlo lo
  convertiría en un resultado, y el resultado de cada corrida se firma en sus propios sprints.
- Q: ¿El encargo contiene comandos, direcciones o pasos para entrar a un servicio? → A: No.
  Nombra el tipo de evidencia y el dominio; nunca un comando, una dirección de red, un puerto,
  una credencial ni un procedimiento de explotación (principio V, igual que en spec, plan,
  tareas e issues).
- Q: ¿El encargo autoriza una corrida? → A: No. La autorización de cada corrida es
  `scope/autorizacion.md` firmada y con ventana vigente en esa corrida. El encargo MUST NOT
  transportar la autorización ni abrir la compuerta; la herramienta que repite verifica la
  compuerta por sí misma.
- Q: ¿Qué pasa con los pasos cuyo dato no consta en las entregas? → A: se escriben como
  condiciones de la repetición («verificar cuando conste evidencia de…»), con el motivo heredado.
  El encargo no rellena lo que no consta: lo deja escrito para la próxima corrida.
- Evaluación de coherencia (2026-10-26): el encargo deriva todo su contenido de las entregas
  S01–S06 con sus huellas; no inventa pasos ni resultados.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir el encargo sin lista (Priority: P1) 🎯 MVP

El auditor abre el encargo a partir de la entrega de S06. La lista no existe: la herramienta se
detiene y lo informa, sin escribir nada. Si existe, la herramienta propone el encargo: el mismo
trabajo de S01–S06 escrito como datos repetibles —activo y alcance con sus huellas, hechos a
verificar por dominio con el tipo de evidencia esperada, riesgos a enunciar, citas a hacer,
perfil a elaborar, lista a generar— todo derivado de las entregas vigentes y citando sus huellas.

**Why this priority**: es el producto mínimo viable de S07. Sin añadir material nuevo, deja el
trabajo en forma que una herramienta lo repita; es la entrada de S08, que dice el mismo
resultado en dos registros.

**Independent Test**: con las entregas S01–S06 vigentes, se comprueba que el encargo cubre cada
dominio del alcance, que cada paso cita la entrega y la huella de la que deriva, que no contiene
comandos, direcciones de red, puertos ni credenciales, y que ningún archivo contiene estados de
cumplimiento.

**Acceptance Scenarios**:

1. **Given** las entregas S01–S06 vigentes, **When** el auditor abre el encargo, **Then** el
   encargo propone los pasos repetibles de cada sprint —alcance, registro, enunciado, cita,
   perfil, lista— con sus entradas, salidas esperadas y las huellas de las entregas de las que
   deriva.
2. **Given** que la entrega de S06 no existe, **When** el auditor abre el encargo, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `01_plan/`.
3. **Given** una entrega con vacíos heredados, **When** se abre el encargo, **Then** cada vacío se
   escribe como condición de la repetición con su motivo (compuerta cerrada, solicitud
   documental, alcance pendiente).
4. **Given** cualquier paso propuesto, **When** se inspecciona su contenido, **Then** nombra el
   tipo de evidencia y el dominio, y no contiene comandos, direcciones de red, puertos ni
   credenciales.

---

### User Story 2 - La herramienta propone el encargo y el auditor corrige (Priority: P2)

El auditor corrige la redacción de un paso, añade una condición o marca un paso como no repetible
por ahora, con motivo; cada cambio queda en el historial con autor, fecha, valor anterior y valor
nuevo. El encargo no se firma: la autoría queda registrada y su huella de integridad se calcula
al guardar. Cualquier escritura posterior deja el encargo «revisado» y la huella anterior queda en
el historial.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. El encargo es el trabajo escrito del auditor para una herramienta; sin esta
historia sería una exportación opaca.

**Independent Test**: con un encargo propuesto, se comprueba que corregir un paso con motivo
queda en el historial; que un paso marcado «no repetible» queda excluido de la repetición con su
motivo; que guardar calcula la huella de integridad; y que ningún cambio se pierde sin autor,
fecha y motivo.

**Acceptance Scenarios**:

1. **Given** un paso propuesto, **When** el auditor corrige su descripción con un motivo, **Then**
   el cambio queda registrado con autor, fecha, valor anterior, valor nuevo y motivo, y el paso
   pasa a «revisado».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y el encargo no se
   modifica.
3. **Given** un paso que hoy no se puede repetir, **When** el auditor lo marca «no repetible» con
   motivo, **Then** queda excluido de la repetición y la historia conserva la decisión.
4. **Given** un texto libre con una dirección de red, **When** se intenta registrar, **Then** se
   reemplaza con la remisión fija; si contiene un comando, un puerto o una credencial, se rechaza.
5. **Given** un encargo guardado, **When** se altera un byte de sus archivos, **Then** `verificar`
   lo detecta comparando con la huella de integridad registrada.

---

### User Story 3 - Un dato no consta y la condición se conserva (Priority: P3)

Un dominio quedó sin verificar porque la compuerta estaba cerrada. En el encargo, ese paso no se
borra ni se rellena: se escribe como condición de la repetición («verificar este dominio cuando la
autorización esté firmada y vigente»), con el motivo heredado del registro. Quien repite encuentra
el paso, entiende por qué faltó y sabe qué falta.

**Why this priority**: protege la diferencia entre «el trabajo no incluía ese paso» y «el paso
quedó pendiente de condición». El encargo es honesto con lo que no consta; de lo contrario, la
repetición silenciaría los vacíos (principio II).

**Independent Test**: con vacíos de distinta causa en las entregas, se comprueba que cada uno
aparece como condición con su motivo, que el conteo de condiciones aparece en una sola sección y
que ningún archivo presenta un paso condicionado como hecho.

**Acceptance Scenarios**:

1. **Given** un dominio «no consta» por compuerta cerrada, **When** se abre el encargo, **Then**
   el paso de ese dominio se escribe como condición con el motivo «compuerta cerrada» heredado.
2. **Given** un dominio que requiere solicitud documental, **When** se abre el encargo, **Then**
   el paso lo declara y pide la evidencia documental, no una prueba técnica.
3. **Given** cualquier paso, **When** se generan los archivos, **Then** ninguno contiene
   `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta una condición
   como verificación hecha.
4. **Given** un encargo con K condiciones, **When** se resume, **Then** el resumen dice cuántos
   pasos son repetibles de inmediato y cuántos quedan condicionados, en una sola sección con su
   conteo.

---

### User Story 4 - Verificar el encargo y entregarlo a S08 (Priority: P3)

El auditor verifica el encargo: la huella de integridad corresponde a los bytes guardados, cada
paso cita la entrega y la huella de la que deriva, y esas entregas siguen vigentes. Si alguna
entrega de origen cambió, la herramienta lo señala y no actualiza sola. La entrega a S08 contiene
el encargo completo, con sus pasos, condiciones y huellas.

**Why this priority**: es el contrato con S01–S06 y el principio III: un encargo solo se puede
repetir si deriva de entregas que siguen en pie. Es también la entrada de las dos frases de S08.

**Independent Test**: con un encargo guardado, se altera un byte de un archivo y se comprueba que
`verificar` lo detecta; se cambia una entrega de origen y se comprueba que `abrir` informa; se
comprueba que `entregar` devuelve el encargo completo con sus huellas.

**Acceptance Scenarios**:

1. **Given** un paso que deriva de una entrega cuya huella ya no corresponde, **When** se
   verifica, **Then** el paso se informa con «origen alterado» y queda marcado para revisión del
   auditor.
2. **Given** un encargo cuya entrega de origen cambió, **When** se abre de nuevo, **Then** la
   herramienta informa el cambio y no escribe hasta que el auditor decida.
3. **Given** un paso marcado «no repetible», **When** se entrega a S08, **Then** la entrega lo
   conserva con su motivo; la exclusión es de la repetición, no del registro.
4. **Given** un encargo completo, **When** una herramienta ajena lo lee, **Then** puede repetir
   el trabajo descrito sin haber estado en la sala, nombrando tipos de evidencia y dominios, sin
   ejecutar nada que exija autorización por sí misma.

---

## Edge Cases

- La lista de S06 no existe: `abrir` termina en código 2 sin escribir.
- Alguna entrega intermedia (S02–S05) no existe aunque S06 sí: `abrir` informa el faltante y no
  escribe; el encargo exige la cadena completa.
- Un paso cuyo origen tiene evidencia alterada: queda marcado «origen alterado» y no se entrega
  como repetible hasta que el auditor corrija.
- El auditor escribe un paso nuevo a mano: se registra como su aporte, con motivo, y pasa por el
  mismo filtro (sin comandos, direcciones de red, puertos ni credenciales).
- Una condición heredada se resuelve en una corrida posterior: el encargo de esa corrida lo
  registra; la historia conserva que fue condición.
- El encargo no contiene la autorización ni la transporta: repetir exige compuerta vigente en la
  corrida que repite.
- El JSON del encargo se altera un byte después de guardar: `verificar` lo detecta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir el encargo a partir de la entrega vigente de S06
  (`lista.entregar`) y de la cadena completa de entregas S01–S05 que S06 cita. Si falta alguna,
  MUST informarlo y no escribir nada.
- **FR-002**: El encargo MUST citar las huellas de todas las entregas de las que deriva y declarar
  cuáles están firmadas.
- **FR-003**: El encargo MUST describir el mismo trabajo de S01–S06 como pasos repetibles: alcance
  a fijar, hechos a verificar por dominio (con el tipo de evidencia esperada), riesgos a
   enunciar, citas a hacer, perfil a elaborar y lista a generar. Cada paso MUST declarar sus
  entradas, su salida esperada y la huella de la entrega de la que deriva.
- **FR-004**: Los vacíos heredados MUST escribirse como condiciones de la repetición, con el
  motivo heredado. El encargo MUST NOT rellenar lo que no consta ni presentarlo como verificado.
- **FR-005**: El encargo MUST NOT contener comandos, direcciones de red, puertos, credenciales ni
  procedimientos de explotación: nombra el tipo de evidencia y el dominio (principio V). Todo
  texto libre del auditor MUST pasar el mismo filtro de S02, con las direcciones de red
  reemplazadas por la remisión fija.
- **FR-006**: El encargo MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles, y MUST NOT
  presentarse como una evaluación hecha.
- **FR-007**: El encargo MUST NOT llevar firma de aprobación: es trabajo escrito para repetir, no
  un dictamen. MUST registrar autoría (autor y fecha de cada aportación) y huella SHA-256 de
  integridad al guardar. El auditor MUST poder corregir pasos, añadir pasos a mano y marcar pasos
  como «no repetible», cada uno con autor, fecha, valor anterior, valor nuevo y motivo
  obligatorio. Ningún paso se borra.
- **FR-008**: Una verificación independiente MUST recalcular la huella de integridad del encargo
  guardado y la de cada entrega citada contra las registradas. MUST detectar la alteración de un
  byte y MUST informar «origen alterado» por paso.
- **FR-009**: Con las mismas entregas y las mismas correcciones, la herramienta MUST producir el
  mismo encargo, byte a byte.
- **FR-010**: El encargo MUST guardarse en archivos nuevos dentro de `01_plan/`, sin crear un
  árbol paralelo ni sobrescribir los productos previos de esa carpeta, y ser legible por una
  herramienta ajena y por un tercero sin la herramienta.
- **FR-011**: Por cada paso MUST escribirse una ficha legible `01_plan/encargo-<id>.md` con el
  mismo contenido del JSON, sin extractos de la evidencia cruda.
- **FR-012**: La herramienta MUST entregar a S08 el encargo completo: pasos, condiciones,
  exclusiones con motivo, huellas de las entregas de origen y estado de firma de cada una.
- **FR-013**: Si alguna entrega de origen cambió (huella distinta de la registrada), `abrir` MUST
  señalarlo y MUST NOT escribir hasta que el auditor decida.
- **FR-014**: El encargo MUST NOT abrir la compuerta, transportar la autorización ni eximir a la
  corrida que repite de verificar `scope/autorizacion.md` firmada y con ventana vigente.
- **FR-015**: La entrega a S08 MUST indicar qué pasos son repetibles de inmediato y cuáles quedan
  condicionados, con sus conteos.

### Key Entities

- **Encargo**: producto de S07. Consolida el trabajo de S01–S06 como pasos repetibles. Referencia
  todas las entregas de las que deriva (huellas y estados de firma). Agrupa los pasos, las
  condiciones, las exclusiones, la autoría, el historial y la huella de integridad. No lleva
  firma de aprobación.
- **Paso**: una unidad repetible del trabajo (fijar alcance, verificar un dominio, enunciar,
  citar, perfilar, listar). Tiene identificador, descripción, entradas, salida esperada, entrega
  de origen con su huella, repetibilidad y condiciones.
- **Condición**: vacío heredado escrito como requisito de la repetición, con su motivo.
- **Aportación**: corrección o paso a mano del auditor, con autor, fecha, valores y motivo.
- **Huella de integridad**: SHA-256 de los bytes guardados del encargo, verificable de forma
  independiente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con las entregas S01–S06 de prueba, el encargo cubre el 100 % de los dominios del
  alcance y el 100 % de los sprints S01–S06, cada paso con la huella de su entrega de origen.
- **SC-002**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales.
- **SC-003**: La alteración de un solo byte del JSON o de cualquier ficha se detecta en el 100 %
  de los casos (`verificar`).
- **SC-004**: El 100 % de las correcciones, pasos a mano y exclusiones registra autor, fecha y
  motivo.
- **SC-005**: Dos aperturas con las mismas entregas producen archivos idénticos byte a byte.
- **SC-006**: Una herramienta ajena lee el encargo y repite el trabajo descrito sin ayuda humana
  y sin haber estado en la sala; el resultado de la repetición se registra en el checklist
  humano.
- **SC-007**: El 100 % de los vacíos heredados aparecen como condiciones con su motivo, y su
  conteo coincide con el de la entrega de S03.
- **SC-008**: Abrir y corregir el encargo solo crean archivos nuevos en `01_plan/`; los archivos
  previos de esa carpeta quedan con huella idéntica.
- **SC-009**: Con una entrega de origen cambiada, `abrir` informa y no escribe hasta la decisión
  del auditor (FR-013).
- **SC-010**: El encargo declara en su resumen cuántos pasos son repetibles de inmediato y
  cuántos quedan condicionados, y el conteo coincide con las condiciones (FR-015).
- **SC-011**: Una corrida que repite usando el encargo verifica la compuerta por sí misma: sin
  `scope/autorizacion.md` vigente no ejecuta pasos técnicos (verificación manual en el
  checklist humano).

## Assumptions

- **Origen de la descripción**: como en S02–S06, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S07 de `docs/PROMPT_SPEC_KIT.md`, de las
  entregas S01–S06 y de la constitución (principios I, II, III, IV y V).
- El encargo no lleva firma por diseño de la guía; la trazabilidad la dan la autoría registrada,
  el historial y la huella de integridad. Esto rompe la convención de los sprints anteriores de
  manera deliberada y declarada.
- Hay un solo rol humano, el auditor. La revisión por segundo par (#33) queda fuera.
- S07 no ejecuta pruebas, no toca la red ni lee `.env`; solo lee las entregas S01–S06 y escribe
  en `01_plan/`.
- El encargo es agnóstico de la herramienta que repite: cualquier herramienta que entienda los
  datos y respete la compuerta puede usarlo.
- **Dependencias**: la cadena completa de entregas S01–S06 y sus modelos; `alcance.serializar`,
  `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: ejecutar la repetición (la corrida que repite es uso del
  encargo, no parte de S07), las dos frases (S08), el borrador (S09) y el cierre (S10); medir
  cumplimiento de los controles listados; cualquier escritura fuera de `01_plan/`.
