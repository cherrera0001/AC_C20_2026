# Prompt para Claude Code CLI — Backlog ágil C4A desde Markdown

> Ejecuta Claude Code desde la raíz de este repositorio. En PowerShell se puede invocar con `claude -p (Get-Content -Raw .\PROMPT_BACKLOG_CLAUDE_CODE.md)` o abrir Claude Code y pegar el contenido completo de este archivo.

## Instrucción

Actúa como analista de producto ágil y mantenedor de GitHub Projects para C4A. Tu tarea es derivar, depurar y registrar en GitHub las épicas, historias de usuario, tareas y bugs que estén justificadas por los documentos Markdown de este repositorio. Trabaja en español, con trazabilidad a las fuentes.

## Fuentes y precedencia

1. Lee primero y trata como **contrato original del proyecto** estos tres documentos:
   - `scope/alcance.md`: propósito, límites, reglas de enganche y entregables.
   - `docs/AUDIT_PROMPT.md`: flujo Planificar → Recopilar → Analizar → Informar, entradas, salidas y restricciones.
   - `docs/historia_usuario.md`: épica inicial, criterios de aceptación, DoD y desglose original.
2. Lee `docs/LINEA_ORIGEN.md` para comprender la procedencia y jerarquía documental.
3. Lee los demás Markdown pertinentes, incluidos `README.md`, `docs/CLAUDE_CODE_PROMPT.md`, `docs/AGILE_PROJECT.md`, `platform/README.md`, `platform/ROADMAP.md`, `01_plan/`, `02_evidencia/`, `03_hallazgos/`, `04_informe/`, `scope/autorizacion.md`, `evidence/README.md` y otros documentos Markdown existentes. Usa estos documentos posteriores para conocer implementación, estado reportado, discrepancias y trabajo pendiente; no alteran el contrato de los tres archivos base.
4. No infieras hechos desde documentos que no hayas leído. No inventes alcance, requisitos normativos, activos, resultados, esfuerzo, responsables, sprints ni fechas.

## Límites

- Este encargo autoriza organizar el backlog en GitHub; **no autoriza pruebas contra redes u objetivos**. No ejecutes escaneos, explotación, solicitudes a objetivos auditados ni comandos de red de auditoría.
- La fase de auditoría de red permanece bloqueada hasta que `scope/autorizacion.md` contenga autorización escrita, rango, ventana y firma vigentes. Una issue o un Project no son autorización.
- No publiques secretos, datos personales, evidencia cruda ni contenido sensible en títulos, cuerpos, comentarios o adjuntos de issues. Cita rutas Markdown no sensibles y resume lo imprescindible.
- No modifiques el código, los tres documentos base ni la configuración local de Git. No hagas commit, push, merge, cierre o reapertura de issues.
- Solo crea o actualiza issues y elementos/campos del Project después de comprobar acceso y deduplicar. Si la cuenta no tiene permisos, no cambies la cuenta activa ni sus credenciales; detente y explica cómo el usuario puede autenticarse.

## Verificación remota previa

Antes de cualquier cambio remoto:

1. Confirma la raíz del repositorio y revisa el estado de Git de forma solo lectura; no incluyas ni alteres cambios locales.
2. Comprueba `gh auth status` sin mostrar tokens. Confirma acceso a `cherrera0001/AC_C20_2026` y al GitHub Project `C4A — Gestión Ágil 2026` (#7, propietario `cherrera0001`) usando `gh repo view`, `gh project view` y las consultas de issues/campos pertinentes.
3. La URL conocida del Project es `https://github.com/users/cherrera0001/projects/7`. Puede ser privado; un 404 en una sesión web no demuestra que haya desaparecido. Confía solo en una consulta autenticada con permisos adecuados.
4. Lista issues **abiertas y cerradas** del repositorio y los elementos ya presentes en el Project. Compara títulos, contenido, relaciones, estado y criterios; no crees duplicados. Si una issue equivalente ya existe, conserva su número y estado. No edites ni cierres una existente salvo que sea estrictamente necesario para vincularla al Project y no se alteren sus datos.
5. Revisa los campos reales y opciones actuales del Project antes de intentar establecer valores. Si repo, cuenta, Project o permisos no coinciden, no adivines, no crees otro Project y no cambies visibilidad: detente con un informe de bloqueo.

## Clasificación del estado del trabajo

Para cada tema documentado determina uno de estos estados y justifícalo con rutas Markdown:

- **Pendiente:** el trabajo no se reporta como terminado y tiene un resultado verificable.
- **Hecho por verificar:** un Markdown lo declara hecho, pero los criterios o evidencia disponible no bastan para confirmarlo.
- **Reportado como hecho:** existe un reporte/documentación que lo declara terminado; no lo reabras automáticamente ni lo trates como verificado por la sola declaración.
- **Bloqueado/condicional:** requiere autorización, información externa o decisión humana pendiente.
- **No aplica/ya cubierto:** existe un artefacto/funcionalidad suficiente; no generes otra issue para repetirlo.

No conviertas tareas históricas ya realizadas —por ejemplo, redactar el alcance que ya existe o funcionalidades de roadmap marcadas completadas— en trabajo nuevo. Cuando un artefacto tenga inconsistencias, crea una issue de **validación/corrección** acotada y documenta la discrepancia, sin afirmar cuál versión es correcta antes de verificarla.

## Estructura de backlog a derivar

Usa esta estructura como punto de partida, no como lista ciega. Confirma cada elemento contra todos los Markdown y el backlog remoto, elimina duplicados y añade solo tareas adicionales sustentadas por fuentes. Si el análisis demuestra que un elemento ya está resuelto, no lo crees.

### Épica A — Flujo de auditoría C4A de cuatro fases

Objetivo: ofrecer el flujo Planificar → Recopilar → Analizar → Informar con criterios de aceptación, evidencia y entregables trazables, según `docs/AUDIT_PROMPT.md` y `docs/historia_usuario.md`.

Historias candidatas:
- **A1. Planificación y compuerta de autorización:** validar alcance, plan, criterios y compuerta antes de pruebas; separar auditoría estática local de las pruebas de red.
- **A2. Recopilación reproducible:** producir inventario y conservar evidencia/hash de forma segura para las actividades autorizadas. No implica ejecutar pruebas de red ahora.
- **A3. Análisis verificable y mapeo normativo:** enlazar hecho, evidencia, severidad, control/requisito y decisión humana sin inventar CVE ni declarar cumplimiento sin base.
- **A4. Informes y revisión humana:** cumplir los entregables y DoD de la historia original, incluyendo revisión y coherencia entre informe, matriz y registro de evidencia.
- **A5. Resolver discrepancias documentadas:** crea solo las issues necesarias tras verificar el contenido actual. Revisa especialmente las inconsistencias descritas en Markdown entre el registro de evidencia y los informes, entre controles `no-evaluado` y declaraciones de cumplimiento, y entre la exigencia CVSS v4 de los documentos base y referencias posteriores a CVSS v3.1. Formula como validación/decisión técnica, no presupongas la solución.

### Épica B — Evolución pendiente de la plataforma C4A

Usa `platform/ROADMAP.md` y `platform/README.md`; no recrees trabajo indicado como completado. Evalúa crear historias para los hitos que los Markdown señalen explícitamente pendientes, como:
- **B1. M2 — comparar corridas y detectar cambios.**
- **B2. M3 — ampliar catálogos/perfiles normativos**, exigiendo fuentes, versión y validación humana.
- **B3. M4 — empaquetar la CLI**, con instalación, pruebas y documentación.
- **B4. M5 — ampliar detectores**; divide IaC, SAST ligero y permisos de nube en historias separadas si los criterios y el tamaño lo justifican.

Cada historia debe tener una tarea o tareas técnicas comprobables, a menos que la historia misma sea suficientemente pequeña para que su DoD equivalga a una sola entrega. No inventes una arquitectura más allá de lo que dicen los documentos.

### Épica C — Fase de red sujeta a autorización

Mantén separadas la preparación documental y cualquier actividad técnica:
- **C1. Completar/revisar autorización**: datos de representante autorizado, activos/rango, ventana, origen, contacto de emergencia, firma y vigencia; depende de la persona autorizante y no se completa automáticamente.
- **C2. Preparar integración de pruebas de red con compuerta estricta**, solo si la hoja de ruta o los Markdown justifican ese trabajo; define pruebas no disruptivas dentro del rango firmado y mecanismo de parada.
- **C3. Ejecutar/validar pruebas de red** solo como trabajo futuro **bloqueado** hasta autorización vigente. No la marques como iniciada, no asignes un sprint y no ejecutes ninguna prueba.

No incluyas en el backlog DoS, persistencia, exfiltración, acceso fuera del rango, ni otra actividad prohibida por el alcance.

### Épica D — Gestión ágil, calidad y trazabilidad del backlog

Comprueba si el Project ya tiene campos y procesos descritos en `docs/AGILE_PROJECT.md`. Crea issues solo para brechas todavía pendientes y verificables (por ejemplo, automatización Auto-add únicamente si los Markdown indican que no está activa y se puede comprobar). No crees issues para volver a crear formularios, etiquetas, campos o Project ya existentes.

## Modelo de tickets

- **Épica:** objetivo amplio, valor esperado, alcance/exclusiones, criterios de salida y enlaces a historias hijas.
- **Historia de usuario:** formato `Como [rol], quiero [capacidad], para [beneficio]`; incluye criterios de aceptación comprobables, dependencias, límites y Definition of Done aplicable.
- **Tarea:** entregable concreto, una persona podría verificarlo, referencia a la historia padre y criterios de aceptación propios. No dupliques una historia como tarea.
- **Bug/discrepancia:** comportamiento/afirmación observado, evidencia documental, resultado esperado y verificación requerida. No clasifiques como bug un asunto normativo aún no validado.

Para cada ticket incluye:
1. Título con prefijo `[ÉPICA]`, `[HU]`, `[TAREA]` o `[BUG]`.
2. Tipo, fase C4A, estado de trabajo, prioridad propuesta y talla.
3. Contexto/valor, alcance y exclusiones.
4. Criterios de aceptación en formato verificable (Gherkin cuando ayude).
5. Dependencias y relación padre-hijo, usando números de issue después de crear/reusar tickets.
6. Sección `Fuentes Markdown` con ruta y encabezado o sección que fundamenta el ticket.
7. DoD cuando aplique y notas de autorización/seguridad.

## Priorización y talla

- Usa las opciones existentes del Project: `P0 - Urgente`, `P1 - Alta`, `P2 - Media`, `P3 - Baja`; no asignes P0/P1 por intuición. Justifica la prioridad en el cuerpo del issue. Si no hay evidencia suficiente, usa P2 solo si está justificado como prioridad provisional; de lo contrario deja el campo sin asignar y anota `Por definir`.
- Talla relativa del Project: `XS`, `S`, `M`, `L`, `XL`, `XXL`, `Por definir`; guía numérica orientativa `XS=1`, `S=2`, `M=3`, `L=5`, `XL=8`, `XXL=13`. No equivale a horas.
- Estima cada historia/tarea por alcance, incertidumbre, integración y dependencias. Si la fuente no permite estimar responsablemente, asigna `Por definir` y crea/propón una tarea de refinamiento solo si agrega valor.
- Si una historia supera XXL, divídela en resultados verticales comprobables. Una épica no se estima como si fuera una historia.
- No asignes personas, sprints ni fechas sin instrucción/dato explícito. No inventes capacidad o velocidad del equipo.

## Creación y vinculación en GitHub

Una vez que el inventario y la deduplicación estén completos:

1. Presenta internamente un resumen del conjunto a crear/reutilizar y comprueba que cada ticket tiene fuentes Markdown y criterios verificables. Como esta instrucción autoriza explícitamente la creación del backlog derivado, crea las issues no duplicadas si la autenticación y el destino fueron confirmados.
2. Usa `gh issue create` en `cherrera0001/AC_C20_2026`, etiquetas apropiadas (reutiliza `epic`, `user-story`, `task`, `bug` si existen; crea una etiqueta faltante solo si es necesaria y está permitido). No agregues etiquetas inexistentes sin comprobarlas.
3. Añade cada issue nueva y toda issue existente pertinente que no esté ya en el tablero al Project #7 usando la CLI/API de GitHub disponible. Consulta `gh project --help`, las opciones de `item-add` y los campos antes de usarlos. Si la versión instalada de `gh` no permite editar campos de elementos, usa la API GraphQL autenticada de GitHub solo después de comprobar la operación y los identificadores vigentes; verifica cada cambio de vuelta. Establece `Status=Todo` para trabajo nuevo cuando el campo admita ese valor; no cambies el estado de tickets existentes.
4. Rellena `Tipo de trabajo`, `Fase C4A`, `Prioridad` y `Talla` con las opciones reales del Project. `Sprint` y `Assignees` deben quedar vacíos salvo que estén especificados en los Markdown o por el usuario. No inventes valores si el Project difiere del documento: informa la discrepancia y detente antes de cambiar la configuración.
5. Enlaza jerarquía y bloqueos entre épicas, historias y tareas con las relaciones nativas de GitHub si la cuenta/CLI las soportan. Si no, incluye referencias `#número` y dependencias explícitas en los cuerpos; no afirmes que se creó una relación nativa.
6. Si alguna operación remota falla, no repitas a ciegas ni dejes tickets duplicados. Reconsulta el estado y continúa solo cuando sea seguro.
7. No actives auto-add sin comprobar el workflow existente. No cambies visibilidad, configuración del repositorio, ramas ni archivos.

## Validación y respuesta final

Al terminar, vuelve a consultar issues y Project para verificar cada creación, número, URL, relación y campo. Informa:

- Épicas, historias, tareas y bugs creados, con número/URL y estructura padre-hijo.
- Issues existentes reutilizadas y duplicados evitados.
- Tickets bloqueados/condicionales y su razón, especialmente la fase de red.
- Temas marcados hechos por verificar/reportados como hechos que no se reabrieron.
- Tallas, prioridades y valores que quedaron `Por definir`; no transformes tally en horas.
- Errores de permisos o discrepancias que impidieron completar la operación.
- Confirma expresamente que no ejecutaste pruebas de red ni cambiaste archivos, commits o ramas locales.
