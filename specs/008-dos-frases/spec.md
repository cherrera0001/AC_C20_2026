# Feature Specification: S08 — Las dos frases

**Feature Branch**: `008-dos-frases` (directorio de funcionalidad; no se creó rama git)

**Created**: 2026-10-26

**Status**: Draft

**Input**: Descripción del usuario: «S08, Las dos frases». Octava épica del ciclo de construcción
(S01–S10) de la herramienta C4A que asiste al auditor de cumplimiento. Según la fila S08 de
`docs/PROMPT_SPEC_KIT.md`, el auditor, a mano, decía el mismo resultado para la gerencia y para
quien corrige. La herramienta deja **las dos frases**.

**Épica**: S08 de S01–S10. **Recibe**: la entrega de S07 (`encargo.entregar`): el mismo trabajo
escrito como datos repetibles, que consolida hechos, riesgos, citas, perfil y lista con sus
huellas. **Produce**: las dos frases. **Entrega a S09 (El borrador)**: el mismo resultado dicho
en dos registros —la frase para la gerencia y la frase para quien corrige— para que S09 arme el
borrador del informe de cierre con un solo contenido.

**Lugar en el proceso de auditoría**: S08 corresponde a la fase Informar del proceso canónico
(Planificar → Recopilar → Analizar → Informar, `docs/AUDIT_PROMPT.md`); su resultado cae en
`04_informe/`. La herramienta propone ambas redacciones; el auditor las corrige y las firma. Una
frase no dictamina: comunica lo registrado y citado, sin convertirlo en cumplimiento.

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta
que el anterior converja, y S07 aún no está implementada (esta misma jornada se escriben las
specs S04–S10, por orden del dueño: «construye la herramienta», 2026-10-26). La desviación queda
registrada aquí y en `tasks.md`.

## Clarifications

### Session 2026-10-26

- Q: ¿S08 necesita un «mínimo de referencia» cuando falta el encargo de S07? → A: No. Las frases
  deben decir el mismo resultado que el trabajo consolidado; sin el encargo no hay contenido
  fiable. Si falta la entrega de S07, `frases abrir` se detiene con el código 2 y no escribe
  nada.
- Q: ¿Las dos frases pueden decir cosas distintas? → A: No. Dicen el mismo resultado en dos
  registros: la de gerencia en lenguaje de negocio, sin jerga técnica ni datos sensibles; la de
  quien corrige con la referencia a fichas, huellas y lo que falta. Si difieren en un hecho, la
  verificación lo marca como inconsistencia.
- Q: ¿La frase de gerencia lleva identificadores de controles o marcos? → A: puede nombrar el
  marco (por ejemplo, que la lectura se organizó con las seis funciones del NIST CSF 2.0), pero
  no identificadores de controles ni estados de cumplimiento: la gerencia recibe el resultado, no
  el expediente.
- Q: ¿Un dato que no consta entra en las frases? → A: sí, igual en ambas: se declara como vacío
  pendiente con su causa en términos generales (por ejemplo, «quedaron verificaciones pendientes
  de autorización»), sin técnicismos innecesarios en la frase de gerencia.
- Q: ¿Las frases tienen extensión fija? → A: la de gerencia cabe en un párrafo; la de quien
  corrige puede estructurarse en apartados, uno por dominio o función, siempre derivados del
  encargo. El límite es la fidelidad al resultado, no un número de palabras.
- Evaluación de coherencia (2026-10-26): ambas frases heredan las marcas del encargo; un paso con
  «origen alterado» no alimenta ninguna de las dos hasta que el auditor corrija.

## User Scenarios & Testing *(mandatory)*

En todas las historias el actor es el auditor. La herramienta es el medio: propone, no firma.

### User Story 1 - Abrir las frases sin encargo (Priority: P1) 🎯 MVP

El auditor abre las dos frases a partir de la entrega de S07. El encargo no existe: la
herramienta se detiene y lo informa, sin escribir nada. Si existe, la herramienta propone las dos
frases: la de gerencia y la de quien corrige, cada una derivada de los mismos datos del encargo,
con la huella de la entrega de la que derivan y sin estados de cumplimiento.

**Why this priority**: es el producto mínimo viable de S08. Sin escribir el informe entero, deja
el mismo resultado en los dos registros que el informe de cierre necesita; es la entrada de S09.

**Independent Test**: con una entrega de S07 con hechos, riesgos, vacíos y condiciones, se
comprueba que ambas frases existen, que tratan los mismos temas con los mismos conteos, que
ninguna contiene estados de cumplimiento y que cada una cita la huella de la entrega.

**Acceptance Scenarios**:

1. **Given** una entrega con H hechos, R riesgos y V vacíos, **When** el auditor abre las frases,
   **Then** la frase de gerencia y la de quien corrige mencionan los mismos temas con conteos
   consistentes (R riesgos, V vacíos) y ninguna contiene estados de cumplimiento.
2. **Given** que la entrega de S07 no existe, **When** el auditor abre las frases, **Then** la
   herramienta informa que falta el producto anterior y no escribe nada en `04_informe/`.
3. **Given** un encargo cuyas entregas de origen están firmadas, **When** se abren las frases,
   **Then** el producto cita la huella de la entrega de S07 y declara el estado de firma de las
   entregas del encargo.
4. **Given** una entrega con pasos condicionados, **When** se abren las frases, **Then** ambas
   declaran los vacíos pendientes con la misma causa, en el registro propio de cada audiencia.

---

### User Story 2 - La herramienta propone las dos frases y el auditor corrige (Priority: P2)

El auditor corrige la redacción de cualquiera de las dos frases, con motivo; la corrección queda
en el historial con autor, fecha, valor anterior y valor nuevo. Puede ajustar el nivel de detalle
de cada registro siempre que el contenido factual se mantenga. Revisa el producto y lo firma;
cualquier escritura posterior anula la firma. Firmar exige que las dos frases estén completas.

**Why this priority**: es la separación central de la constitución (I): la herramienta propone y
el auditor decide. Las frases son la voz del auditor ante la gerencia y ante quien corrige; sin
esta historia serían un resumen automático.

**Independent Test**: con las frases propuestas, se comprueba que corregir la frase de gerencia
con motivo queda en el historial; que una corrección que alteraría los hechos se rechaza si rompe
la consistencia con la otra frase; que firmar desde «revisado» con firmante y justificación
escribe la firma con la huella de los bytes guardados; y que ningún camino llega a «firmado» sin
la acción explícita del auditor.

**Acceptance Scenarios**:

1. **Given** la frase de gerencia propuesta, **When** el auditor corrige su redacción con un
   motivo sin cambiar los hechos, **Then** el cambio queda registrado con autor, fecha, valor
   anterior, valor nuevo y motivo, y la frase pasa a «revisado».
2. **Given** un intento de corregir sin motivo o con un texto que contiene un estado de
   cumplimiento, **When** se intenta registrar, **Then** el cambio se rechaza y las frases no se
   modifican.
3. **Given** una corrección que cambiaría un conteo de la frase de gerencia sin tocar la de quien
   corrige, **When** se intenta registrar, **Then** se rechaza informando la inconsistencia entre
   registros.
4. **Given** un producto revisado con las dos frases completas, **When** el auditor firma con su
   nombre y una justificación, **Then** el producto queda «firmado» con la huella de sus bytes
   guardados; cualquier cambio posterior anula la firma.
5. **Given** una frase vacía, **When** se intenta firmar, **Then** la firma se rechaza informando
   qué frase falta.

---

### User Story 3 - Un dato no consta y ambas frases lo dicen igual (Priority: P3)

Una parte del trabajo quedó condicionada: faltan verificaciones porque la autorización no estuvo
vigente, o porque requieren documentos que no se aportaron. Las dos frases lo declaran, cada una
en su registro, con la misma causa y sin presentar el vacío como resultado favorable. La gerencia
y quien corrige escuchan lo mismo.

**Why this priority**: protege la diferencia entre «comunicar poco» y «maquillar el vacío». Si la
frase de gerencia omitiera lo que la de quien corrige declara, las dos frases dejarían de decir
el mismo resultado (principio II).

**Independent Test**: con vacíos de distinta causa en la entrega, se comprueba que ambas frases
los declaran, que las causas coinciden entre registros y que ninguna presenta un vacío como
logro o como cumplimiento.

**Acceptance Scenarios**:

1. **Given** un vacío por compuerta cerrada, **When** se abren las frases, **Then** la de
   gerencia declara que quedaron verificaciones pendientes de autorización y la de quien corrige
   nombra el dominio y la condición, con la misma causa.
2. **Given** un vacío por solicitud documental, **When** se abren las frases, **Then** ambas lo
   declaran como pendiente de documentación, en el registro propio de cada audiencia.
3. **Given** cualquiera de las dos frases, **When** se generan los archivos, **Then** ninguno
   contiene `cumple`, `parcial`, `no-cumple`, `no-evaluado` ni `no-aplica`, ni presenta un vacío
   como resultado favorable.
4. **Given** un producto con V vacíos, **When** se resume, **Then** el resumen dice cuántos vacíos
   declara cada frase y los conteos coinciden, en una sola sección.

---

### User Story 4 - Verificar que las dos frases dicen lo mismo y entregar a S09 (Priority: P3)

El auditor verifica el producto: la huella de los bytes guardados sigue correspondiendo a la
firma, la huella de la entrega de S07 sigue siendo la registrada y las dos frases siguen
diciendo el mismo resultado —mismos conteos, mismas causas de vacío, mismos riesgos tratados—.
Si el encargo cambió después de firmar, la herramienta no actualiza sola. La entrega a S09
contiene las dos frases con sus conteos verificados.

**Why this priority**: es el contrato con S07 y la garantía de la épica: «el mismo resultado para
la gerencia y para quien corrige». Es también la entrada del borrador de S09.

**Independent Test**: con un producto firmado, se altera un byte del JSON y se comprueba que
`verificar` lo detecta; se cambia el encargo de origen y se comprueba que `abrir` informa y,
estando firmado, no escribe; se comprueba que `entregar` devuelve las dos frases y su
consistencia.

**Acceptance Scenarios**:

1. **Given** dos frases cuyos conteos difieren, **When** se verifica, **Then** la inconsistencia
   se informa por dimensión (riesgos, vacíos, dominios) y el producto no se entrega a S09 hasta
   que el auditor corrija.
2. **Given** un producto firmado cuyo encargo de origen cambió, **When** se abre de nuevo, **Then**
   la herramienta informa el cambio y no escribe (código 4).
3. **Given** una frase que cita un paso marcado «origen alterado» en el encargo, **When** se
   verifica, **Then** se informa y la frase queda marcada para corrección del auditor.
4. **Given** un producto consistente, **When** se entrega a S09, **Then** la entrega contiene la
   frase de gerencia y la de quien corrige, los conteos verificados, la huella de la entrega de
   S07 y el estado de firma.

---

## Edge Cases

- El encargo de S07 no existe: `abrir` termina en código 2 sin escribir.
- La entrega tiene cero riesgos: las frases lo declaran («no se enunciaron riesgos sobre lo
  verificado») y recogen los vacíos; ninguna dice «sin hallazgos» ni «todo en orden».
- El encargo cambia entre `abrir` y una acción del auditor: la acción se rechaza con código 4
  («el encargo de origen cambió»), sin escribir.
- Un texto libre del auditor contiene una dirección de red: se reemplaza con la remisión fija
  (`limpiar`); si contiene un estado de cumplimiento, un puerto, una forma de comando o de
  credencial, se rechaza.
- La frase de gerencia crece con jerga técnica: la verificación de consistencia no la prohíbe
  (es estilo), pero rechaza cualquier dato que la frase de quien corrige no respalde.
- El JSON de las frases se altera un byte después de firmar: `verificar` lo detecta.
- Una frase menciona un marco con nombre y versión: se permite; lo que MUST NOT aparecer es un
  estado de cumplimiento o un identificador de control presentado como conclusión.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La herramienta MUST abrir las dos frases a partir de la entrega vigente de S07
  (`encargo.entregar`). Si la entrega no existe, MUST informarlo y no escribir nada.
- **FR-002**: El producto MUST citar la versión de la entrega de la que deriva (su huella) y
  declarar el estado de firma de las entregas del encargo.
- **FR-003**: El producto MUST tener exactamente dos frases: la frase de gerencia y la frase de
  quien corrige. Ambas MUST derivarse de los mismos datos del encargo y MUST decir el mismo
  resultado: mismos riesgos tratados, mismos vacíos con la misma causa y conteos consistentes.
- **FR-004**: La frase de gerencia MUST estar en lenguaje de negocio, sin jerga técnica ni datos
  sensibles, y MUST NOT presentar identificadores de controles ni estados de cumplimiento. La
  frase de quien corrige MUST referir a las fichas y huellas de las que deriva, sin copiar
  extractos de la evidencia.
- **FR-005**: Los vacíos MUST declararse en ambas frases con la misma causa, en el registro
  propio de cada audiencia, y MUST NOT presentarse como resultado favorable.
- **FR-006**: El producto MUST NOT contener estados de cumplimiento (`cumple`, `parcial`,
  `no-cumple`, `no-evaluado`, `no-aplica`) ni conclusiones sobre controles. «Sin riesgos
  enunciados» MUST NOT presentarse como «sin hallazgos» ni como «todo en orden».
- **FR-007**: El auditor MUST poder corregir la redacción de cualquiera de las dos frases. Cada
  corrección registra autor, fecha, valor anterior, valor nuevo y motivo obligatorio, y deja la
  frase en «revisado». Una corrección que rompa la consistencia entre frases MUST rechazarse con
  el detalle de la inconsistencia. Ninguna frase se borra.
- **FR-008**: Solo una acción explícita del auditor MUST dejar el producto en «firmado». La firma
  registra firmante, fecha, justificación y huella de los bytes guardados; cualquier escritura
  posterior la anula. Firmar MUST exigir que las dos frases estén completas, y MUST rechazar
  firmar desde «borrador» o sin firmante o sin justificación. Firmar las frases MUST NOT abrir la
  compuerta.
- **FR-009**: Una verificación independiente MUST recalcular: la huella del producto guardado
  contra la firma; la huella de la entrega de S07 contra la registrada; y la consistencia entre
  las dos frases (conteos, causas de vacío, riesgos tratados). MUST detectar la alteración de un
  byte y MUST informar la inconsistencia por dimensión.
- **FR-010**: Con la misma entrega de S07 y las mismas correcciones, la herramienta MUST producir
  el mismo producto, byte a byte.
- **FR-011**: El producto MUST guardarse en archivos nuevos dentro de `04_informe/`, sin crear un
  árbol paralelo ni sobrescribir los productos previos de esa carpeta (`informe_tecnico.md`,
  `resumen_ejecutivo.md`, `plan_remediacion.md` y los demás), y ser legible por un tercero sin la
  herramienta.
- **FR-012**: Debe escribirse una ficha legible por frase (`04_informe/frase-gerencia.md` y
  `04_informe/frase-tecnica.md`) con el mismo contenido del JSON.
- **FR-013**: La herramienta MUST entregar a S09 las dos frases con los conteos verificados, la
  huella de la entrega de S07 y el estado de firma.
- **FR-014**: Si el encargo de origen cambió (huella de la entrega distinta de la registrada),
  `abrir` MUST señalarlo; si el producto está firmado, MUST rechazar la escritura con código 4.
- **FR-015**: Las acciones del auditor MUST exigir que el encargo de origen no haya cambiado desde
  `abrir`; si cambió, se rechazan con código 4 sin escribir.
- **FR-016**: Los textos libres del auditor MUST pasar por el mismo filtro de S02: sin estados
  de cumplimiento, puertos, formas de comando ni de credencial; las direcciones de red se
  reemplazan con la remisión fija.

### Key Entities

- **Dos frases**: producto de S08. Referencia la entrega del encargo de la que deriva (huella y
  estados de firma). Agrupa la frase de gerencia, la frase de quien corrige, el estado de
  aprobación, el historial y la firma.
- **Frase de gerencia**: el mismo resultado en lenguaje de negocio: qué se revisó, qué riesgos se
  enunciaron, qué queda pendiente y por qué. Sin jerga técnica, sin identificadores de controles,
  sin estados de cumplimiento.
- **Frase de quien corrige**: el mismo resultado en registro técnico: riesgos con remisión a sus
  fichas y huellas, vacíos con su causa y condición, y lo que falta para verificar.
- **Consistencia**: igualdad de contenido factual entre las dos frases: riesgos tratados, vacíos
  con causa y conteos.
- **Corrección**: autor, fecha, frase afectada, valor anterior, valor nuevo y motivo.
- **Firma**: firmante, fecha, justificación, huella del producto guardado y conteos al firmar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con una entrega de prueba con R riesgos y V vacíos, ambas frases existen, tratan
  los mismos temas y sus conteos coinciden.
- **SC-002**: El producto cita la huella de la entrega de S07 y declara el estado de firma de las
  entregas del encargo.
- **SC-003**: Una búsqueda sobre los archivos generados encuentra cero estados de cumplimiento,
  direcciones de red, comandos, puertos y credenciales; la frase de gerencia contiene cero
  identificadores de controles.
- **SC-004**: La alteración de un solo byte del JSON del producto se detecta en el 100 % de los
  casos (`verificar`).
- **SC-005**: Dos frases con conteos o causas que difieren se detectan en el 100 % de los casos,
  con la dimensión informada.
- **SC-006**: Ninguna frase llega a «firmado» sin la acción explícita del auditor, y el 100 % de
  las correcciones registra autor, fecha y motivo.
- **SC-007**: Dos aperturas con la misma entrega producen archivos idénticos byte a byte.
- **SC-008**: El 100 % de los vacíos se declaran en ambas frases con la misma causa (FR-005).
- **SC-009**: La entrega a S09 contiene las dos frases con conteos verificados y ninguna
  inconsistencia abierta.
- **SC-010**: Abrir y corregir las frases solo crean archivos nuevos en `04_informe/`; los
  archivos previos de esa carpeta quedan con huella idéntica.
- **SC-011**: Un lector de cada audiencia entiende su frase sin ayuda y sin haber estado en la
  sala; el resultado se registra en el checklist humano.
- **SC-012**: Con el producto firmado y el encargo cambiado, `abrir` y las acciones del auditor
  terminan en código 4 sin escribir (FR-014, FR-015).

## Assumptions

- **Origen de la descripción**: como en S02–S07, no se usaron las guías del curso (decisión del
  usuario: autoestudio). La descripción sale de la fila S08 de `docs/PROMPT_SPEC_KIT.md`, de la
  entrega de S07 y de la constitución (principios I, II, III y IV).
- Hay un solo rol humano, el auditor, que corrige y firma. La revisión por segundo par (#33)
  queda fuera.
- La firma sigue el mecanismo de los sprints anteriores: firmante, fecha, justificación y huella
  SHA-256 de los bytes guardados.
- S08 no recolecta material nuevo, no ejecuta pruebas, no toca la red ni lee `.env`; solo lee la
  entrega de S07 y escribe en `04_informe/`.
- Las frases no sustituyen al informe: lo resumen en dos registros. El detalle sigue en las
  fichas de S02–S06, a las que la frase de quien corrige remite.
- **Dependencias**: la entrega de S07 (`encargo.entregar`, FR-012 de S07) y su modelo; el filtro
  `alcance.limpiar` y `util.short_id`.
- **Fuera de esta funcionalidad**: armar el borrador del informe (S09) y el cierre (S10);
  proponer acciones de remediación (quien corrige las deriva de las fichas, no de esta épica);
  emitir cualquier dictamen de cumplimiento.
