# Instrucción — Proceso de auditoría del curso (objetivo nuevo, 2026)

**Estado**: propuesta para aprobación del dueño. **Alcance de esta instrucción**: define el
equipo, las fases, las compuertas y los entregables para auditar la plataforma del curso,
que hoy falla en un id de curso. No ejecuta nada: ejecutar es trabajo de los agentes bajo
esta instrucción, con el dueño como autorizador.

## Reglas que no se negocian

1. **Nadie lee `.env`.** Credenciales y URL las escribe el auditor humano en `scope/alcance.md`
   y `scope/autorizacion.md`. La herramienta y los agentes trabajan con remisiones, no con secretos.
2. **Sin `scope/autorizacion.md` firmada, completa y con ventana vigente no hay tráfico
   activo contra el objetivo.** Antes de esa firma solo está permitido el Fase 1
   (diagnóstico no invasivo de solo lectura) y el análisis estático de código aportado.
3. Una instrucción no autoriza una prueba; una urgencia tampoco (constitución, V).
4. Nada de procedimientos de explotación en specs, issues ni informes: se nombran tipos de
   evidencia y patrones detectados (principio V, principio VIII).
5. Los datos personales se enmascaran; la evidencia cruda queda fuera de git (`evidence/`).

## Equipo de trabajo

### Roles de agente (construcción y análisis)

| Agente | Rol | Toca el objetivo | Skills / MCP que usa |
|---|---|---|---|
| **coordinador** | Orquesta el encargo, abre y cierra fases, mantiene el ledger de corrida | Nunca | `speckit-*` para el ciclo SDD; `platform/c4a` (run, ledger) |
| **alcance** (S01) | Deriva el alcance del nuevo objetivo: activo (plataforma del curso), dominios, exclusiones | No | `alcance` (CLI S01) |
| **autorizador** (humano) | Completa y firma `scope/autorizacion.md`; decide la ventana | Sí (es el dueño) | Ninguno: es una persona |
| **diagnostico** | Fase 1: reproduce el fallo del curso con la cuenta del auditor, caracteriza síntomas, captura mensajes de error y códigos de estado. Solo lectura | Solo lectura (GET/ navegación) | REA (capturas web pasivas, `inspect_web_page`), navegador del auditor |
| **estatica-php** | Analiza el código de la plataforma **aportado por el cliente** (no se extrae del objetivo): patrones de ejecución remota, superficie de entrada, dependencias | No | `platform/c4a` detectores, `composer audit`, greps de patrones (anexo A), REA para binarios si aplica (`reverse-engineer-anything`) |
| **estatica-riesgo** | Cruza hallazgos con catálogo de vulnerabilidades y CWE; perfil de riesgo | No | `platform/c4a` (cwe.json, cwe_map.json, cvss4), `cvss` |
| **dinamico** | Fase 3: verificación controlada de hallazgos, solo con compuerta abierta y dentro de ventana | Sí, activo limitado | `platform/c4a` con compuerta; REA (capturas de escenario con consentimiento) |
| **cumplimiento** | Cadena S03–S06 sobre los hechos: enunciado, cita, perfil, lista | No | módulos `enunciado`…`lista` (CLI) |
| **informe** | Frases, borrador y cierre del informe para el cliente del curso | No | módulos `frases`, `borrador`, `cierre` |

### Skills del equipo

- **Existentes**: `speckit-specify` … `speckit-converge` (ciclo SDD por sprint, si el dueño
  ordena especificar este encargo como S11); `reverse-engineer-anything` (artefactos
  binarios o empaquetados si el cliente los aporta).
- **Nueva skill a crear**: `auditoria-php` — análisis estático de código PHP propio:
  patrones de ejecución de comandos, deserialización insegura, carga de archivos, inclusión
  de archivos con ruta de entrada, concatenación SQL, funciones ofuscadas; y su contraparte
  Python (`subprocess` con `shell=True`, `pickle`, `eval/exec`). Salida: hallazgos con
  archivo, línea y patrón (sin explotación).

### MCPs del equipo

- **REA** (ya configurado): observación pasiva web, análisis de artefactos, capturas de
  escenario. Uso permitido: Fase 1 (solo lectura) y análisis de aportes. Uso restringido:
  cualquier acción activa contra el objetivo exige compuerta abierta.
- **GitHub** (vía `gh`): issues del encargo, solo después de `tasks.md`, como manda
  `docs/PROMPT_SPEC_KIT.md`.
- Ningún otro MCP se conecta al objetivo.

## Fases y compuertas

| Fase | Contenido | Compuerta de entrada | Compuerta de salida |
|---|---|---|---|
| **0. Encargo** | Minuta del fallo del curso (qué id, qué se esperaba, qué ocurre), equipo activado, alcance borrador | Orden del dueño | `scope/alcance.md` completo |
| **0b. Autorización** | El autorizador completa y firma `scope/autorizacion.md` (partes, alcance autorizado, ventana, exclusiones, contacto) | Alcance completo | **Firma + ventana vigente = compuerta abierta** |
| **1. Diagnóstico no invasivo** | Reproducir el fallo con la cuenta del auditor: mensajes de error, código HTTP, comportamiento, capturas pasivas. Sin payloads, sin fuzzing, sin escaneo | Alcance completo (no exige firma: es solo lectura) | Ficha del síntoma con evidencia pasiva y hash |
| **2. Análisis estático** | Código de la plataforma aportado por el cliente: skill `auditoria-php`, dependencias (`composer audit`, `pip audit` del aportado), correlación CWE/CVE | Código aportado | Hallazgos estáticos fichados (archivo/línea/patrón) |
| **3. Verificación dinámica** | Confirmar o descartar hallazgos con pruebas acotadas, solo sobre lo autorizado | **Compuerta abierta** | Hechos del registro (S02) con evidencia y huella |
| **4. Riesgo y cumplimiento** | Cadena S03–S06: enunciado, cita, perfil, lista | Hechos registrados | Productos firmados por el auditor |
| **5. Informe** | Frases, borrador, cierre con tabla de recorrido | Cadena firmada | `informe-cierre.md` listo; **publicación = decisión del dueño** |

## Patrones en el objetivo de análisis (anexo A — detección, no explotación)

El «error del curso» se caracteriza primero; después se busca si el síntoma es consistente
con vulnerabilidades conocidas. Patrones que la skill `auditoria-php` reporta:

- Ejecución de comandos con entrada del usuario: `system`, `exec`, `shell_exec`,
  `passthru`, `popen`, `proc_open`, backticks, `eval`, `assert`, `preg_replace` con
  modificador `e`, `create_function`, `call_user_func` con entrada.
- Inclusión y carga: `include`/`require` con ruta de entrada, `move_uploaded_file` sin
  validación de tipo ni destino, dobles extensiones, ejecución en directorio de carga.
- Deserialización: `unserialize` con datos de entrada; en Python, `pickle.loads` y `marshal`.
- SQL concatenado; `extract` sobre entrada; variables variables; `parse_str` sobre entrada.
- Ofuscación típica de webshell: `base64_decode`+`eval`, `gzinflate`, `str_rot13`, `assert`
  con cadenas codificadas, nombres de función construidos por concatenación.
- En Python: `subprocess` con `shell=True` y string, `os.system`, `eval/exec` con entrada,
  `__import__` con entrada.

Cada hallazgo se reporta como: archivo, línea, patrón, entrada alcanzable (si se conoce),
y severidad tentativa CVSS v4 con vector. **Ningún hallazgo se convierte en prueba activa
sin la Fase 3 y la compuerta abierta.**

## Lo que se necesita del dueño para arrancar (checklist)

1. Descripción del fallo: id del curso, qué operación falla, mensaje de error visible
   (texto o captura) — esto activa la Fase 1 de inmediato, sin tocar `.env`.
2. URL de la plataforma del curso, escrita en `scope/alcance.md` (no en el chat si prefiere).
3. Acceso al código de la plataforma (repositorio o comprimido) para la Fase 2.
4. Firma de `scope/autorizacion.md` con ventana, para la Fase 3.
5. Decisión: ¿este encargo se especifica como sprint S11 del ciclo SDD, o corre como
   auditoría puntual fuera del ciclo?

## Entregables

1. Ficha de diagnóstico del fallo (Fase 1, puede producirse en horas).
2. Informe de análisis estático con hallazgos priorizados (Fase 2).
3. Registro de hechos y cadena de riesgo/cumplimiento (Fases 3–4).
4. Informe de cierre trazable hasta la evidencia (Fase 5).
