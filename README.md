# Laboratorio C4A — Auditoría de Ciberseguridad de Cumplimiento

Repositorio de trabajo de la **Auditoría de Ciberseguridad de Cumplimiento (C4A)**:
una auditoría híbrida que combina validación técnica ofensiva (*ethical hacking*)
con auditoría normativa (ISO/IEC 27001:2022, Ley 21.663 y Ley 21.719), descrita en
[`docs/AUDIT_PROMPT.md`](docs/AUDIT_PROMPT.md).

En este repositorio conviven dos cosas, y no se confunden:

1. **El proceso de auditoría**, canónico, en cuatro fases:
   Planificar → Recopilar → Analizar → Informar.
2. **La herramienta que asiste al auditor**, que se construye aparte con
   desarrollo dirigido por especificación (SDD, Spec Kit) en diez sprints
   (S01–S10). La herramienta **propone borradores; el auditor corrige y firma**.
   Ningún rol de la herramienta cierra un hallazgo ni emite un dictamen.

El ejercicio autorizado es un único activo de laboratorio, Metasploitable 2,
según [`scope/alcance.md`](scope/alcance.md). El cliente del informe de cierre
es Comercial Andes Sur SpA.

---

## Estado actual

| Componente | Estado |
|---|---|
| Proceso de 4 fases | Definido y con entregables de ejecución en `01_plan/` a `04_informe/` |
| Plataforma `platform/c4a` | Operativa: auditoría estática de repositorio, SCA con CVE reales, SARIF, mapa HTML, triaje humano, reproducción por hash |
| Spec Kit (SDD) | Inicializado en `.specify/`; constitución 1.0.0 con principios I–VIII |
| Sprint S01 «El alcance» | Implementado: spec, plan, tareas, checklists, contratos y módulo `alcance` con CLI. Quedan **2 acciones humanas**: medir SC-003/SC-008 y firmar el alcance |
| Sprint S02 «El registro» | Especificado y planificado: spec (con clarificaciones), plan, research, data-model, contracts, quickstart, checklists y 39 tareas; tablero creado como épica #46 con historias #47–#50. Implementación **no** iniciada |
| Sprints S03–S10 | No iniciados |
| Compuerta de autorización | **Cerrada.** `scope/autorizacion.md` está sin firmar y sin ventana vigente: no se ejecuta ningún comando contra el objetivo |
| Equipo técnico de red | **Nuevo (2026-10-28).** Agentes en `.claude/agents/`, skills `net-*` en `.agents/skills/` y MCP en `.mcp.json`, todos gobernados por la compuerta |
| Tablero | [C4A — Gestión Ágil 2026](https://github.com/users/cherrera0001/projects/7), repo `cherrera0001/AC_C20_2026` |

---

## Documentación (`docs/`)

Toda la documentación de gobierno, historia y prompts del proyecto vive en
`docs/`. En la raíz solo queda este `README.md`.

| Documento | Para qué |
|---|---|
| [`docs/LINEA_ORIGEN.md`](docs/LINEA_ORIGEN.md) | Origen confirmado del proyecto: el contrato son `scope/alcance.md`, `docs/AUDIT_PROMPT.md` y `docs/historia_usuario.md` |
| [`docs/AUDIT_PROMPT.md`](docs/AUDIT_PROMPT.md) | Rol del auditor, reglas, las 4 fases con entrada/salida y estructura de salida |
| [`docs/historia_usuario.md`](docs/historia_usuario.md) | Épica original, criterios de aceptación (Gherkin) y desglose inicial |
| [`docs/AGILE_PROJECT.md`](docs/AGILE_PROJECT.md) | Método ágil: campos del Project, tallas relativas, DoR/DoD y métricas |
| [`docs/PROMPT_SPEC_KIT.md`](docs/PROMPT_SPEC_KIT.md) | Cómo se construye la herramienta con Spec Kit: ciclo por épica S01–S10 y reglas del tablero |
| [`docs/LINEAMIENTO_C4A.md`](docs/LINEAMIENTO_C4A.md) | Revisión del repositorio y propuesta de MVP |
| [`docs/INSTRUCCION_UNICA_C4A.md`](docs/INSTRUCCION_UNICA_C4A.md) | Instrucción única de encargo para el agente |
| [`docs/VERIFICACION_C4A.md`](docs/VERIFICACION_C4A.md) | Evidencia de verificación del lineamiento |
| [`docs/CLAUDE_CODE_PROMPT.md`](docs/CLAUDE_CODE_PROMPT.md) | Prompt consolidado para Claude Code (auditoría, GitHub y gestión ágil) |
| [`docs/ESTACION_LOCAL.md`](docs/ESTACION_LOCAL.md) | Estación local del auditor y su instrumental |
| [`docs/PROMPT_BACKLOG_CLAUDE_CODE.md`](docs/PROMPT_BACKLOG_CLAUDE_CODE.md) | Prompt para levantar el backlog desde los documentos |

Orden de autoridad cuando dos documentos chocan:
`.specify/memory/constitution.md` → `docs/LINEA_ORIGEN.md` →
`docs/PROMPT_SPEC_KIT.md` → `docs/AGILE_PROJECT.md` → spec, plan y tareas de
la épica activa.

---

## Estructura del repositorio

```text
AC_C20_2026/
├── README.md                  ← único .md en la raíz
├── docs/                      ← documentación de gobierno, historia y prompts
├── scope/                     ← contrato de ejecución (rutas canónicas)
│   ├── alcance.md             ← qué se audita, criterios y fuera de alcance
│   ├── autorizacion.md        ← autorización escrita (compuerta, sin firmar)
│   ├── alcance_s01.md/.json   ← producto de S01 (borrador; aún sin firmar)
├── 01_plan/                   ← Fase 1: plan
├── 02_evidencia/              ← Fase 2: inventario estructurado
├── 03_hallazgos/              ← Fase 3: fichas y matriz de cumplimiento
├── 04_informe/                ← Fase 4: entregables finales
├── evidence/                  ← salidas crudas con hash (el crudo no entra a git)
├── platform/                  ← la herramienta (paquete Python `c4a`)
├── .specify/                  ← Spec Kit: constitución, plantillas, scripts
├── specs/                     ← especificaciones por sprint
│   ├── 001-alcance-auditoria/ ← S01: spec, plan, research, data-model,
│   │                            quickstart, contracts, checklists, tasks
│   └── 002-registro-hechos/   ← S02: idem (spec con clarificaciones)
├── .agents/skills/            ← habilidades del agente: speckit-* y net-*
├── .claude/agents/            ← agentes técnicos de red (guardián, diagnóstico,
│                                custodio, redactor); gobernados por la compuerta
├── .mcp.json                  ← MCP sin credenciales: filesystem acotado a
│                                evidence/, docs/ y scope/, más fetch
├── .github/ISSUE_TEMPLATE/    ← formularios de épica, historia, tarea y bug
└── triage/                    ← decisiones humanas de triaje persistidas
```

**Por qué no todo está en `docs/`:** Spec Kit exige `specs/` y `.specify/` en
su sitio, la constitución fija `scope/` y las carpetas de las 4 fases como
rutas canónicas donde cae el resultado, y `platform/` es un paquete de código
con su propio `README.md`. Moverlos rompería el framework, el código que lee
`scope/` y la trazabilidad de la auditoría. Cada sprint S01–S10, además, es
una épica de Spec Kit: no se abre un árbol paralelo.

---

## El proceso de auditoría (4 fases)

Cada fase consume el producto de la anterior; ninguna se salta
(`docs/AUDIT_PROMPT.md`).

| Fase | Entrada | Salida |
|---|---|---|
| 1. Planificar | Alcance y autorización | `01_plan/plan.md` |
| 2. Recopilar | Plan aprobado | `02_evidencia/inventario.json` + crudos en `evidence/` |
| 3. Analizar | Inventario y evidencia | `03_hallazgos/<id>.md` + `03_hallazgos/matriz_cumplimiento.csv` |
| 4. Informar | Hallazgos encuadrados | `04_informe/` (informe técnico, resumen ejecutivo, plan de remediación) |

Se separan tres dimensiones que nunca se mezclan (principio II de la
constitución): **resultado técnico** (positivo/negativo/inconcluso/
no-ejecutado), **cumplimiento** (cumple/parcial/no-cumple/no-evaluado/
no-aplica) y **aprobación** (borrador/revisado/firmado). Un CVSS alto no
produce por sí solo un «no-cumple», y «sin hallazgos» no significa «cumple».

---

## La herramienta (SDD con Spec Kit)

La herramienta deja de hacer a mano el recorrido norma → control → hecho
técnico. Cada sprint es **una épica y una funcionalidad**, en este orden:

| Sprint | El auditor hacía a mano | La herramienta deja |
|---|---|---|
| S01 | Decidir qué entra y qué no | El alcance |
| S02 | Anotar lo que se puede afirmar y lo que no consta | El registro |
| S03 | Enunciar el riesgo con criterio, impacto y lo que falta | El enunciado |
| S04 | Ubicar ese riesgo en un marco, con nombre y versión | La cita |
| S05 | Leer el activo con las 6 funciones del NIST CSF 2.0 | El perfil |
| S06 | Listar los CIS Controls que aplican | La lista |
| S07 | Dejar el trabajo escrito para repetirlo, sin firmar | El encargo |
| S08 | Decir el resultado a gerencia y a quien corrige | Las dos frases |
| S09 | Armar el borrador del informe de cierre | El borrador |
| S10 | Dejar un informe recorrible hasta la evidencia | El cierre |

Ruta obligada por sprint (constitución, «Flujo de trabajo y compuertas»):

```text
specify → clarify → plan → checklist → tasks → analyze → implement → converge
```

Las issues del Project se abren **después** de `tasks.md`, nunca antes, y
reflejan la épica que ya tiene spec y tareas: épica
(`.github/ISSUE_TEMPLATE/04-epica.yml`), una historia por historia de la spec
(`01-historia-usuario.yml`) y una tarea por tarea de `tasks.md`
(`02-tarea.yml`). Talla relativa (no horas); sin responsables ni fechas
inventadas.

### S01 «El alcance» — dónde va

- Spec y artefactos: `specs/001-alcance-auditoria/` (`spec.md` con
  clarificaciones 2026-10-21, `plan.md`, `research.md`, `data-model.md`,
  `quickstart.md`, `contracts/`, `checklists/`, `tasks.md`).
- Decisiones clave: la firma es registro de **firmante + fecha + huella
  SHA-256** de los bytes guardados (sin GPG ni firma electrónica avanzada);
  firmar el alcance **no** abre la compuerta; las filas que no constan quedan
  «pendiente de confirmar» y no se borran ni se rellenan.
- Implementación: `platform/c4a/alcance.py` + CLI (`alcance proponer |
  compuerta | corregir | revisar | firmar | verificar | consultar`)
  y producto en `scope/alcance_s01.md` / `scope/alcance_s01.json`.
- Pendiente humano: medir SC-003 y SC-008 y firmar el alcance
  (tareas T032 y T033). Sin eso, S01 no converge.
- Tablero: S01 se integró bajo la épica existente #1 como épica #41, con
  historias US1 #42, US2 #43, US3 #44 y US4 #45 (tareas como checklist dentro
  de cada historia, sin issues de tarea sueltas).

### S02 «El registro» — dónde va

- Spec y artefactos: `specs/002-registro-hechos/` (`spec.md`, `plan.md`,
  `research.md`, `data-model.md`, `quickstart.md`, `contracts/`,
  `checklists/`, `tasks.md` con 39 tareas).
- Diseñado para no depender de la firma de S01: abre el registro con el
  alcance firmado o en borrador, y registra «no consta» por activo y dominio
  si el alcance aún no existe (FR-001). Es trabajo documental: ninguna tarea
  toca la red ni escribe en `scope/` ni en `02_evidencia/inventario.json`.
- Reutiliza de S01 `alcance.py` sin cambios (`cargar`, `consultar`,
  `evaluar_compuerta`); la implementación del módulo `registro` **no** ha
  comenzado.
- Tablero: épica #46 con historias US1 #47, US2 #48, US3 #49 y US4 #50.

---

## Plataforma `platform/c4a`

Herramienta ejecutable en Python (solo librería estándar, 3.10+) que audita un
repositorio y produce evidencia verificable, hallazgos, correlación
CWE/CVSS/controles e informes reproducibles. Detalle completo en
[`platform/README.md`](platform/README.md).

```bash
cd platform
python -m c4a catalog                     # detectores y normativas
python -m c4a run --config config/audit.example.json
python -m c4a alcance proponer --raiz ..  # borrador del alcance (S01)
python -m c4a alcance compuerta --raiz .. # estado de la autorización
```

Pruebas:

```powershell
$env:PYTHONPATH = "platform"
python -m unittest discover -s platform/tests -p "test_*.py"
```

En Windows se usa `python` (o `py -3`) y las configs `*.windows.json`.

---

## Compuerta de seguridad

**No se toca el objetivo sin `scope/autorizacion.md` firmada, completa y con
ventana vigente** (Ley 21.459). Hoy el documento registra la decisión del
dueño (2026-10-21) de autorizar el ejercicio de laboratorio, pero firmante,
facultad, origen del auditor, ventana, contacto de emergencia y firma siguen
«por completar»: la compuerta está **cerrada** y solo se permite análisis
documental y construcción local. Ninguna issue, prompt o instrucción de este
repositorio autoriza una prueba.

Además: no se publica evidencia cruda, secretos, credenciales ni datos
personales. `.env` y las claves están excluidos por `.gitignore`; en specs,
planes, tareas e issues no se escriben direcciones IP, comandos, puertos ni
procedimientos de explotación — nombrar el tipo de evidencia alcanza.

---

## Equipo técnico de red (agentes, skills y MCP)

Desde el 2026-10-28 la estación del auditor tiene un equipo técnico con roles
acotados, todos gobernados por la misma compuerta:

| Rol | Archivo | Qué hace |
|---|---|---|
| Guardián del alcance | `.claude/agents/guardian-alcance.md` | Decide si una actividad de red está permitida leyendo `scope/alcance.md` y `scope/autorizacion.md`; responde ABIERTA o CERRADA con motivo. No ejecuta pruebas |
| Diagnóstico de red | `.claude/agents/diagnostico-red.md` | Mide y explica fallos de conectividad de la estación (DNS, latencia, pérdida, MTU, IPv4/IPv6, rutas) y analiza capturas pcap. Solo lee y mide; no modifica nada |
| Custodio de evidencia | `.claude/agents/custodio-evidencia.md` | Registra salidas y capturas en `evidence/` con comando, fecha, zona horaria, ejecutor y SHA-256 de los bytes guardados, y mantiene `evidence/MANIFEST.md` |
| Redactor de hallazgos | `.claude/agents/redactor-hallazgos.md` | Convierte evidencia registrada en borradores de fichas para `03_hallazgos/`, separando resultado técnico, cumplimiento y aprobación. Nunca firma |

Las skills de red en `.agents/skills/` (`net-compuerta`, `net-diagnostico`,
`net-pcap-analisis`) documentan el procedimiento de cada rol. El MCP de
`.mcp.json` conecta dos servidores **sin credenciales**: `evidencia`
(filesystem acotado a `evidence/`, `docs/` y `scope/`) y `fetch` (contenido
web). El diagnóstico de la estación local no es evidencia C4A: al expediente
solo entra lo que el custodio registra de un activo en alcance con la
compuerta abierta.

---

## Gestión ágil y versionado

- **Project**: [C4A — Gestión Ágil 2026](https://github.com/users/cherrera0001/projects/7)
  (privado), fuente de verdad de estado y asignaciones; el método está en
  [`docs/AGILE_PROJECT.md`](docs/AGILE_PROJECT.md).
- **Campos**: Status, Assignees, Prioridad, Talla (`XS`–`XXL` o
  `Por definir`), Fase C4A, Tipo de trabajo, Sprint.
- **Git**: rama principal `main`, remoto
  `https://github.com/cherrera0001/AC_C20_2026.git`. Commit, push y escrituras
  en GitHub solo con aprobación explícita del dueño; sin `--force`.
- **Estación del auditor**: las pruebas técnicas se ejecutan desde Ubuntu en
  WSL (ver [`docs/ESTACION_LOCAL.md`](docs/ESTACION_LOCAL.md)).

---

## Qué sigue

1. El auditor mide SC-003/SC-008 y firma el alcance S01 (`alcance firmar`).
2. `/speckit-converge` declara la convergencia de S01 y se reconcilia su
   tablero contra `tasks.md`.
3. Se implementa S02 «El registro» con `/speckit-implement`, siguiendo
   `specs/002-registro-hechos/tasks.md` (39 tareas; reutiliza `alcance.py`
   sin cambios y no toca la red).

Lo que no conste queda siempre declarado: `pendiente de confirmar` o
`VALIDAR`. Nunca se rellena con un valor inventado.
