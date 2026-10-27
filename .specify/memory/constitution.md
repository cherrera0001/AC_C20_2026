<!--
Informe de impacto de sincronización (borrador para revisión humana; retirar antes del commit)
- Versión: plantilla sin llenar → 1.0.0 (adopción inicial); 1.0.0 → 1.1.0 (2026-10-26):
  precedencia y tesis canónica en Gobernanza, objetivo CVSS v4.0 en Marcos. MINOR porque
  se amplía materialmente sin retirar principios.
- Principios añadidos: I–VIII (todos nuevos).
- Secciones añadidas: «Marcos, estados y evidencia» y «Flujo de trabajo y compuertas».
- Secciones eliminadas: ninguna.
- Plantillas dependientes (.specify/templates/*): no modificadas; leen esta constitución
  en tiempo de ejecución. La «Constitution Check» de plan-template.md debe evaluarse
  contra los principios I–VIII.
- TODO diferidos: ninguno.
-->

# Constitución de C4A — Herramienta de asistencia al auditor de cumplimiento

## Principios fundamentales

### I. La herramienta propone, el auditor firma

- La herramienta produce borradores. Ningún rol de la herramienta cierra un hallazgo,
  aprueba una evaluación ni emite un dictamen de cumplimiento.
- Un estado «cumple» sin evidencia citada MUST quedar en «pendiente de confirmar».
- Toda decisión final MUST registrar quién la revisó, cuándo y con qué justificación.

Fundamento: la responsabilidad profesional del dictamen es del auditor; la herramienta
acelera el trabajo manual, no lo sustituye.

### II. Separación de evidencia técnica, riesgo y dictamen (transversal)

- Se registran tres dimensiones independientes:
  - resultado técnico: `positivo`, `negativo`, `inconcluso`, `no-ejecutado`;
  - cumplimiento: `cumple`, `parcial`, `no-cumple`, `no-evaluado`, `no-aplica`;
  - aprobación: `borrador`, `revisado`, `firmado`.
- La severidad o el CVSS MUST NOT producir por sí solos una conclusión de cumplimiento.
- Un falso positivo descartado MUST NOT acreditar incumplimiento. Un riesgo aceptado
  MUST NOT registrarse como cumplimiento; la aceptación de riesgo se guarda aparte.
- «Sin hallazgos» MUST NOT implicar «cumple».
- Sin evidencia suficiente, el estado MUST ser `no-evaluado` o «pendiente de validación».
- `no-aplica` MUST llevar motivo aprobado.
- Toda conclusión exige criterio, aplicabilidad, evidencia y revisión humana registrada.

Fundamento: corrige la conclusión automática actual de
`platform/c4a/correlation.py::controls_matrix`, que deriva `no-cumple`/`parcial` de la
severidad sin considerar el estado del triaje ni una decisión firmada. Es requisito
transversal: aplica a todos los sprints, no es una funcionalidad aislada.

### III. Integridad verificable de la evidencia (transversal)

- Todo hash publicado MUST corresponder exactamente a los bytes persistidos que acredita.
- Se distinguen el hash del contenido original y el hash del artefacto guardado, y se
  declara qué bytes acredita cada uno. Evidencia que referencia un archivo del objetivo
  sin copiarlo MUST declararlo.
- La integridad MUST verificarse de forma independiente de la reproducción del detector.
- Un hash alterado MUST detectarse.
- Evidencia de otro activo o de otra corrida MUST NOT acreditar una evaluación.
- Los fixtures sintéticos MUST rotularse como tales; su resultado es una demostración de
  la herramienta, no una auditoría del objetivo.
- Tener hashes no implica cifrado; el cifrado de custodia requiere decisión explícita.

Fundamento: corrige `platform/c4a/evidence.py::from_command`, que hashea la salida antes
de añadir encabezados al archivo, de modo que `SHA256SUMS.txt` no verifica el archivo
persistido. Requisito transversal de todos los sprints.

### IV. Controles citados con marco, versión e identificador

- Todo control se cita con marco, versión e identificador. Marcos de referencia:
  - ISO/IEC 27001:2022;
  - NIST CSF 2.0, con sus seis funciones: Gobernar, Identificar, Proteger, Detectar,
    Responder y Recuperar;
  - CIS Controls v8.1, según la fuente oficial del CIS. Solo si la v8.1 no se puede
    obtener se usa la v8, y se declara.
- Se distingue un marco mencionado de un marco implementado: que un marco sea
  seleccionable no acredita cobertura.
- Si un identificador no consta en la fuente, queda «pendiente de confirmar». No se inventa.
- Una correspondencia CWE→control es una sugerencia explicada, nunca prueba de
  incumplimiento.
- Las obligaciones legales se registran con fuente oficial, fecha de consulta, artículo y
  fundamento de aplicabilidad; si falta alguno, «VALIDAR».
- Una vulnerabilidad de una VM no demuestra por sí sola el incumplimiento legal de una
  organización.

### V. Alcance y compuerta

- El ejercicio autorizado es un único activo, Metasploitable 2, en el laboratorio declarado.
- Ninguna prueba técnica se ejecuta sin `scope/autorizacion.md` firmada, completa y
  dentro de su ventana vigente. Una issue no autoriza una prueba.
- En spec, plan, tareas e issues MUST NOT escribirse direcciones IP, comandos, puertos,
  credenciales ni procedimientos de explotación: nombrar el tipo de evidencia alcanza.
- No se lee `.env`. No se publica evidencia cruda, secretos ni datos personales.

### VI. Proceso canónico y ciclo de construcción

- Las cuatro fases (Planificar, Recopilar, Analizar, Informar) son la definición canónica
  del proceso de auditoría. Sus carpetas (`scope/`, `01_plan/`, `02_evidencia/`,
  `03_hallazgos/`, `04_informe/`) son donde cae el resultado; no se abre un árbol paralelo.
- La herramienta se construye en diez sprints (S01–S10). Cada sprint es una épica y una
  funcionalidad de Spec Kit, en orden. La siguiente no se especifica hasta que la
  actual converja.
- Se reutiliza `platform/c4a` (Run, Evidence, Finding, identificadores deterministas,
  `report.py`, HTML, SARIF) en lugar de reescribirlo. Las pruebas existentes MUST seguir
  pasando.

### VII. Trazabilidad ágil sin duplicar

- El GitHub Project #7 y las issues de `cherrera0001/AC_C20_2026` reflejan specs y
  `tasks.md` ya escritos. No se duplica backlog ni se crea otro Project.
- Cada épica, historia y tarea se vincula a su issue existente, o a una nueva creada con
  los formularios de `.github/ISSUE_TEMPLATE/` y los campos de `docs/AGILE_PROJECT.md`.
- Las tallas son relativas, no horas. No se inventan responsables ni fechas.
- Una issue en Done exige el criterio demostrado y un vínculo a evidencia revisada; no
  equivale a un control cumplido.
- El informe final es trazable desde el requisito y el control hasta la prueba, la
  evidencia con hash, el hallazgo, la issue, la remediación y la reevaluación.

### VIII. Legibilidad

- El código y las specs se entienden sin haber estado en la sala. Castellano.
- Sin mencionar USACH. Si hace falta nombrar el sitio del curso: diplomadociberseguridad.com.

## Marcos, estados y evidencia

- Cobertura, si se calcula: controles aplicables evaluados / controles aplicables
  seleccionados, mostrando numerador, denominador y pendientes. No se extrapola al SGSI
  ni a la totalidad de controles de un marco.
- El CVSS conserva versión y vector; no se renombra la versión al exportar. La versión
  objetivo es CVSS v4.0 (`scope/alcance.md` §7); el puntaje v4.0 se calcula con
  `platform/c4a/cvss4.py` y sin el paquete opcional no se inventa.
- Un control que requiere políticas, personas o procesos no se acredita con una prueba
  de red: queda pendiente con solicitud documental.
- El texto importado no se interpreta como código en el HTML; no se exportan secretos.

## Flujo de trabajo y compuertas

- Ruta por sprint: specify → clarify → plan → checklist → tasks → analyze → implement →
  converge, repitiendo implement y converge hasta que converge informe convergencia.
- Las issues se abren después de `tasks.md`, no antes.
- Commit, push y escrituras en GitHub solo con aprobación explícita; sin `--force`.
- Los ítems abiertos del checklist se consultan antes de implementar.

## Gobernanza

- Esta constitución prevalece sobre los prompts locales y sobre `docs/AGILE_PROJECT.md`
  cuando choquen. La fuente del producto es `docs/PROMPT_SPEC_KIT.md` (tesis canónica:
  copiloto del auditor, ver `docs/DECISION_TESIS_CANONICA.md`); `docs/AUDIT_PROMPT.md` y
  `docs/CLAUDE_CODE_PROMPT.md` aportan el formato de salida de las cuatro fases, y su Fase 2
  de red queda suspendida.
- Las enmiendas se registran con versión semántica y fecha: MAJOR si se retira o
  redefine un principio; MINOR si se agrega un principio o sección o se amplía
  materialmente; PATCH si se aclara la redacción.
- Cada plan MUST pasar la verificación de constitución contra los principios I–VIII;
  `/speckit-analyze` trata un conflicto con un MUST como crítico.

**Version**: 1.1.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-26
