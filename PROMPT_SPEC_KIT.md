# Prompt — construir la herramienta con Spec Kit (SDD)

Pégalo en el agente, con el directorio de trabajo en `C:\Users\herre\OneDrive\Documentos\AC_C20_2026`. Una habilidad por mensaje. Lees el resultado y esperas. No adelantes el paso siguiente.

Metodología única: [Spec Kit](https://github.com/github/spec-kit), desarrollo dirigido por especificación, tal como está en https://github.github.io/spec-kit/quickstart.html. Las habilidades se invocan en el chat del agente, no en la terminal. La terminal solo instala e inicializa.

## Qué se construye

Una herramienta que acelera el trabajo manual del auditor de cumplimiento. El auditor, a mano, recorre normas, controles y estándares y, además, verifica el hecho técnico. La herramienta propone. El auditor corrige y firma. Ningún rol de la herramienta cierra un hallazgo.

El ejercicio autorizado es la máquina Metasploitable 2, en VirtualBox, adaptador puente, en la LAN de laboratorio ya aislada. El cliente del informe de cierre es Comercial Andes Sur SpA. La máquina sigue siendo esa. No hay otra organización.

Las guías que describen ese trabajo manual están en `F:\Code\Auditoría a la Ciberseguridad\guias\`, de `S00.docx` a `S10.docx` si `S00` existe, y si no, de `S01.docx` a `S10.docx`. Léelas. El hilo que manda, si una guía se contradice, es este:

| Guía | El auditor hacía a mano | La herramienta deja |
|---|---|---|
| S01 | Decidir qué entra y qué no | El alcance |
| S02 | Anotar lo que se puede afirmar y lo que no consta | El registro |
| S03 | Enunciar el riesgo con criterio, impacto y lo que falta | El enunciado |
| S04 | Ubicar ese riesgo en un marco, con nombre y versión | La cita |
| S05 | Leer el mismo activo con las seis funciones del NIST CSF 2.0 (Gobernar, Identificar, Proteger, Detectar, Responder, Recuperar) | El perfil |
| S06 | Listar los CIS Controls que aplican, partiendo por el inventario | La lista |
| S07 | Dejar el mismo trabajo escrito para que una herramienta lo repita, sin firmar | El encargo |
| S08 | Decir el mismo resultado para la gerencia y para quien corrige | Las dos frases |
| S09 | Armar el borrador del informe de cierre | El borrador |
| S10 | Dejar un informe que un tercero recorre hasta la evidencia | El cierre |

Ese hilo es la necesidad. No la reemplaces por las cuatro carpetas `01_plan`, `02_evidencia`, `03_hallazgos` y `04_informe`. Esas carpetas son el lugar donde cae el resultado. `AUDIT_PROMPT.md`, `AGILE_PROJECT.md` y `historia_usuario.md` se leen. Si chocan con este hilo, manda este hilo y la guía.

## Antes de la primera habilidad

Si no existe `.specify/`, detente. En la terminal, desde esta raíz, sigue la guía oficial de Spec Kit para un repositorio que ya tiene código (https://github.github.io/spec-kit/). No inventes banderas de `specify init`. Cuando `.specify/` exista, paras y muestras qué creó. Recién ahí empieza el chat.

No leas `.env`. No copies credenciales, evidencia cruda de `evidence/` ni la contraseña de la consola de la máquina. No escribas direcciones IP, banderas de escáner, ni un procedimiento de explotación, en la spec, en el plan, en las tareas ni en una issue. Nombrar el tipo de evidencia alcanza. La compuerta sigue siendo `scope/autorizacion.md`: sin firma y sin ventana vigente no se toca la red. Una issue no autoriza una prueba.

## Constitución, una sola vez

```
/speckit-constitution
```

Principios que le pasas, en este idioma:

- La herramienta propone borradores. El auditor firma. Un estado «cumple» sin evidencia citada queda en pendiente de confirmar.
- Un control se cita con marco, versión e identificador. Si el identificador no está en la guía ni en la norma abierta, queda pendiente de confirmar. No se inventa.
- El alcance de este ejercicio es Metasploitable 2. Fuera de `scope/autorizacion.md` no hay prueba técnica.
- Cada producto de la tabla de arriba es una funcionalidad. La siguiente no se especifica hasta que la actual converja.
- El código y las specs se pueden leer sin haber estado en la sala. Castellano. Sin USACH. El sitio del curso, si hace falta nombrarlo, es diplomadociberseguridad.com.

## Una épica, un ciclo

Cada fila de la tabla es una épica y una sola funcionalidad de Spec Kit. El orden es el de la tabla. `S00` no es épica: es contexto de encuadre, se cita y no se implementa.

Para la épica en curso, y solo para esa, corre la ruta completa. Una habilidad por mensaje. Si el resultado no se sostiene, corriges el artefacto y repites esa habilidad. No sigues con la siguiente.

1. `/speckit-specify` — el qué y el porqué. Sin stack. La descripción sale de la guía de esa fila: qué recibe del producto anterior, qué produce, qué le deja a la siguiente. Dentro de la spec van las historias de usuario, en la forma que ya trae la plantilla de Spec Kit: quién, qué quiere, para qué, y el escenario comprobable. El quién es el auditor. La herramienta es el medio, no el que firma. Como mínimo, tres historias: una en la que falta el producto de la guía anterior y se usa el mínimo de referencia; una en la que la herramienta propone y el auditor corrige; una en la que un dato no consta y la fila se conserva.
2. `/speckit-clarify` — lo que la guía no fija. No inventes la respuesta. Si la guía dice pendiente de confirmar, la spec lo deja así.
3. `/speckit-plan` — aquí sí el cómo. Encaja el producto en las carpetas que ya existen (`scope/`, `01_plan/`, `02_evidencia/`, `03_hallazgos/`, `04_informe/`). No abras un árbol paralelo.
4. `/speckit-checklist` — la calidad de la spec. El revisor marca. No marques ítems para poder implementar.
5. `/speckit-tasks` — `tasks.md`, en orden de dependencia.
6. `/speckit-analyze` — solo lee. Si hay conflicto entre `spec.md`, `plan.md` y `tasks.md`, se corrige el origen y se vuelve a analizar.
7. `/speckit-implement` — ejecuta `tasks.md`. Si el checklist tiene ítems abiertos, pregunta antes de seguir.
8. `/speckit-converge` — compara el código con la spec, el plan y las tareas. Si faltan tareas, las agrega.
9. Repite implementar y converger hasta que converge diga `Converged`.

Recién entonces abres la épica siguiente. La funcionalidad activa es la que dice `.specify/feature.json`. No cambies de épica con un checkout.

## Issues, después de las tareas, no antes

Spec Kit no se sustituye por el tablero. El tablero refleja la épica que ya tiene spec y `tasks.md`.

Usa los formularios que ya están:

- `.github/ISSUE_TEMPLATE/04-epica.yml` — una issue por épica, cuando `spec.md` ya existe. El cuerpo apunta a la carpeta de esa funcionalidad bajo `.specify/` o `specs/`, la que haya creado Spec Kit. Tipo de trabajo: Épica.
- `.github/ISSUE_TEMPLATE/01-historia-usuario.yml` — una issue por historia escrita en la spec. Tipo de trabajo: Historia de usuario. Enlázala a la épica.
- `.github/ISSUE_TEMPLATE/02-tarea.yml` — una issue por tarea de `tasks.md`, con el mismo orden y la misma dependencia. Tipo de trabajo: Tarea. Enlázala a la historia que la contiene.

Campos, como los define `AGILE_PROJECT.md`: Status, Prioridad, Talla, Fase C4A, Tipo de trabajo, Sprint. La talla es relativa. Si no alcanza para estimarla, queda `Por definir`. No conviertas la talla en horas. No inventes responsables ni fechas. Project: [C4A — Gestión Ágil 2026](https://github.com/users/cherrera0001/projects/7), repositorio `cherrera0001/AC_C20_2026`.

El bucle de la issue es el de la tarea: se abre al quedar escrita en `tasks.md`, pasa a In Progress cuando `/speckit-implement` la toma, y se cierra solo si el criterio de aceptación se cumple y `/speckit-converge` no la reabre. Una tarea que converge agrega de nuevo queda abierta.

No hagas push, commit ni publiques una issue sin que esta ejecución lo pida. No uses `--force`.

## Qué no entra en ninguna spec

- Comandos, puertos, credenciales de la consola, ni un paso para entrar a un servicio.
- Una red solo-host como requisito. La red del ejercicio es el adaptador puente.
- Nombres de archivo inventados para el entregable del estudiante. El producto es el de la tabla (el alcance, el registro, el enunciado, la cita, el perfil, la lista, el encargo, las dos frases, el borrador, el cierre).
- Una URL que no esté ya en este repositorio.
- La Actividad de Cierre de la unidad como si fuera la épica S06. S06 es la lista CIS. El informe del cliente es S09 y S10.

## Cierre de cada épica, en cinco líneas

Antes de pasar a la guía siguiente, responde:

1. Frase de salida, copiada de la portada de esa guía.
2. Producto que quedó en la spec, con el nombre de la tabla.
3. Si la spec, el plan o una issue contienen un comando, una IP o un procedimiento de ataque.
4. Si converge dijo `Converged`.
5. Números de la issue épica, de las historias y de las tareas.

Si la línea 3 no está limpia, o la 4 no es `Converged`, no abras la épica siguiente.
