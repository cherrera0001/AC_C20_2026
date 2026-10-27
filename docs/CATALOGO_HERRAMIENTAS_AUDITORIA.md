# Catálogo de herramientas del proceso C4A — cumplimiento + ethical hacking

**Versión**: 1.0.0 (2026-10-27). **Pregunta de investigación**: *¿Qué herramientas deben
formar parte del proceso de auditoría a la ciberseguridad que integra auditor de
cumplimiento y ethical hacking?* **Fuentes del juicio**: el estado real de este
repositorio (`platform/c4a/`, `scope/`, `specs/001–010`, `.agents/skills/`,
`~/.kimi-code/mcp.json`), los documentos de gobierno (`docs/PROMPT_SPEC_KIT.md`,
`docs/AUDIT_PROMPT.md`, `docs/AGILE_PROJECT.md`, `docs/ESTACION_LOCAL.md`,
`scope/alcance.md` §3 y §6) y las fuentes oficiales que esos documentos citan (FIRST para
CVSS, CIS para Controls v8.1, NIST CSF 2.0, ISO/IEC 27001:2022 y las leyes chilenas
21.663 / 21.719 / 21.459 ya verificadas en `docs/LINEA_ORIGEN.md` §1).

**Criterio de selección**: entra una herramienta solo si (a) sirve a una de las cuatro
fases canónicas (Planificar → Recopilar → Analizar → Informar, principio VI), (b) deja
su producto en una ruta canónica del repo y (c) preserva la trazabilidad (evidencia con
hash, identificadores deterministas, ledger). Si duplica capacidades existentes, si su
uso es explotación activa sin autorización, o si no aporta evidencia verificable, queda
fuera.

## Respuesta corta

El proceso C4A híbrido se instrumenta con **cuatro clases de herramientas, todas ya
presentes o referenciadas en este repo**: (1) **orquestación y productos SDD** —Spec Kit
(skills `speckit-*`) y el CLI `platform/c4a`, que producen el alcance, el registro y la
cadena S03–S10; (2) **adquisición de evidencia verificable** —scripts locales de
diagnóstico web autenticado + MCP Playwright y REA para observación pasiva, con la
cadena de custodia de `evidence.py`; (3) **análisis** — detectores estáticos propios
(incluido `php-shell` para php2shell/python2shell), SCA con CVE reales (`sca.py` vía
OSV.dev, `osv-scanner`/`trivy` locales o `composer audit`/`pip audit` de manifiestos
aportados), cálculo CVSS v3.1/v4.0 y bases de conocimiento CWE/ISO/CIS/NIST; y
(4) **cierre** — triaje humano persistente, reproducción por hash, informes
`report.py`/`htmlmap.py`/`sarif.py` y gestión ágil en GitHub Project #7 sin duplicar
backlog. La línea ofensiva activa (escaneo de red, verificación de explotabilidad) no se
omite por descuido: **queda tras la compuerta** de `scope/autorizacion.md` (principio V;
`docs/AUDIT_PROMPT.md` tiene su Fase 2 explícitamente suspendida) y se detalla abajo en
«queda fuera y por qué».

## Tabla de familias

Compuerta: **SR** = solo lectura, no exige autorización · **CE** = requiere código
aportado/local · **AU** = requiere `scope/autorizacion.md` firmada y ventana vigente.

| Familia | Fase C4A | Rol que la usa | Ya existe en el repo (ruta) | Falta | Riesgo si se omite | Compuerta |
|---|---|---|---|---|---|---|
| Alcance y autorización | Planificar | autorizador, coordinador | `platform/c4a/alcance.py` + CLI; `scope/alcance.md`, `scope/autorizacion.md` (plantilla); spec `specs/001-alcance-auditoria/` | Firma humana del alcance S01 (T032/T033) y de la autorización | Sin compuerta trazada, cualquier prueba posterior es indefendible legalmente (Ley 21.459) | SR |
| Orquestación SDD (Spec Kit) | Transversal | coordinador | `.agents/skills/speckit-*` (11 skills); `specs/001–010`; `.specify/` | Nada para el ciclo S01–S10; decisión S11 pendiente | El equipo construye sin especificación; se pierde la reproducibilidad del ciclo | SR |
| Inventario de activos | Recopilar | analista-estatico | `platform/c4a/inventory.py` (lenguajes, dependencias, contenedores, IaC, CI/CD) | Inventario de red activo (suspendido con la Fase 2 de red) | No se sabe qué se audita; se audita el papel, no el sistema | SR (código) / AU (red) |
| Evidencia con integridad | Recopilar | custodio-evidencia | `platform/c4a/evidence.py`, `ledger.py`, `reproduction.py`; convención `evidence/<run>/` + `MANIFEST.json` + `SHA256SUMS.txt`; skill `evidencia-integridad` (nueva) | Verificador independiente periódico de `SHA256SUMS.txt` en frío | Un hash que no verifica los bytes persistidos tumba toda la cadena de custodia (principio III) | SR |
| Reconocimiento pasivo web | Recopilar | diagnostico-web | MCP **Playwright** (headless) + MCP **REA** (inspección web pasiva); `platform/tools/diagnostico_curso.py`, `platform/tools/recon_curso.py` | Nada para Fase 1: reproduce el fallo, caracteriza alcance del síntoma | Se confunde síntoma con causa; no hay línea base del comportamiento observado | SR |
| Análisis estático de código (php2shell/python2shell) | Analizar | analista-estatico | `platform/c4a/detectors/php_shell.py` (+ 7 detectores más); skill `auditoria-php` | Código de la plataforma aportado por el cliente | El vector pedido por el encargo (php2shell, webshell, deserialización) queda sin revisar | CE |
| SCA de dependencias (CVE reales) | Analizar | analista-riesgo | `platform/c4a/sca.py` (API OSV.dev opt-in; `osv-scanner`/`trivy` locales); `composer audit`/`pip audit` citados en skill | Ejecución contra los manifiestos aportados cuando lleguen | Vulnerabilidades conocidas con parche disponible pasan inadvertidas | CE |
| Mapeo CWE/CVE/CVSS | Analizar | analista-riesgo | `platform/c4a/knowledge/` (cwe.json, cwe_map.json, controls_iso27001.json, controls_cis.json, normativas.json); `cvss.py` (v3.1), `cvss4.py` (v4.0, sin inventar si falta el paquete opcional) | Nada estructural | Severidad por opinión; informe impugnable | SR |
| Correlación a controles y obligaciones | Analizar | correlacion-cumplimiento | `platform/c4a/correlation.py`, `cita.py`, `perfil.py`, `lista.py`; skill `correlacion-cumplimiento` (nueva) | Medición humana de cobertura SC pendiente | Hallazgos técnicos sin encuadre: ruido para gerencia; brecha normativa sin prueba: opinión | SR |
| Triaje humano | Analizar | auditor-firma | `platform/c4a/triage.py` + `triage/` + `registro_triaje.md` | Decisiones sobre los hallazgos reales del nuevo encargo | Falsos positivos se convierten en «no-cumple» o se ocultan riesgos aceptados (principio II) | SR (decisión humana) |
| Reproducción | Analizar | custodio-evidencia, verificador-dinamico | `platform/c4a/reproduction.py` (`reproduce` por ciclo, `verify` por hallazgo; `result_hash` por contenido) | Nada estructural | «Reproducible» sin prueba: una segunda corrida puede no coincidir | SR / AU según la prueba |
| Navegación autenticada de diagnóstico | Recopilar | diagnostico-web | Scripts `platform/tools/` sobre Playwright; venv `~/.venv-c4a-audit` | Credenciales ya están en `.env` (la herramienta nunca las lee; los scripts sí, en runtime y enmascarando) | Sin sesión autenticada no se distingue «curso roto» de «sin permiso» | SR |
| Reverse engineering de artefactos aportados | Analizar | analista-estatico | MCP **REA** (`reverse-engineer-anything`, usuario); `platform/c4a/inventory.py` para empaquetados | Artefactos binarios aportados por el cliente | Componentes cerrados quedan como caja negra en el informe | CE |
| Informe dual (gerencia / técnico) | Informar | redactor-informe | `platform/c4a/report.py`, `frases.py`, `borrador.py`, `cierre.py`, `htmlmap.py`, `sarif.py`; `04_informe/` ya poblado | Firma del auditor y recorrido del tercero (S10) | Informe sin trazabilidad ni lectura gerencial | SR |
| Gestión ágil (GitHub Project #7) | Transversal | coordinador, autorizador | `docs/AGILE_PROJECT.md`; `.github/ISSUE_TEMPLATE/`; repo `cherrera0001/AC_C20_2026` | Reconciliación de issues del encargo del curso (después de `tasks.md`, nunca antes) | Doble backlog; estado del proyecto irreconocible (principio VII) | SR |

Familias añadidas con fundamento (además del mínimo pedido): **navegación autenticada de
diagnóstico** (sin ella el síntoma del curso no es distinguible de un problema de
permisos — ya demostrado en Fase 1) y **reverse engineering de artefactos aportados**
(el MCP REA ya está instalado y cubre binarios/empaquetados aportados legalmente).

## Qué queda fuera, y por qué

| Herramienta / familia | Por qué queda fuera del proceso C4A |
|---|---|
| Escáneres de red y explotación activa (p. ej. nmap en modo activo, Metasploit, sqlmap, fuerza bruta de credenciales) | Su lugar es la Fase 2 de red de `docs/AUDIT_PROMPT.md`, **suspendida**; solo correrían con compuerta abierta (AU). Hoy su omisión es un estado gobernado, no una brecha. `docs/ESTACION_LOCAL.md` §4 ya las instala condicionadas al relator |
| DoS / técnicas disruptivas, persistencia, exfiltración | Prohibidas por `scope/alcance.md` §5 y §6 y por la constitución (V) |
| Ingeniería social / phishing | Fuera de alcance (§5); exige anexo contratado aparte |
| Escáner SAST comercial o en nube (Semgrep SaaS, Checkmarx, SonarCloud) | Duplica a los detectores propios registrados en `platform/c4a/detectors/`; rompe la regla «solo biblioteca estándar» (`platform/README.md`) que sostiene la reproducibilidad; no aporta trazabilidad C4A que el repo no tenga ya |
| Escáner DAST activo (ZAP/Burp en modo ataque, nuclei con templates ofensivos) | Tráfico activo contra el objetivo: exige compuerta abierta y, aun así, supera el «solo PoC, sin disrupción» de §6. El diagnóstico web del repo es pasivo |
| Gestores de secretos / vault | La regla del repo es más simple y más dura: `.env` no se lee por herramientas y los scripts lo leen solo en runtime enmascarado |
| Segundo tablero (Jira/Trello) o segundo Project GitHub | Prohibido por principio VII: no se duplica backlog |

## Mapa herramienta → fase → producto S01–S10 → carpeta de salida

| Herramienta | Fase | Producto / cadena | Carpeta de salida |
|---|---|---|---|
| CLI `alcance` (`platform/c4a/alcance.py`) | Planificar | S01 El alcance (`alcance_s01.json/.md`, `.firma.json`) | `scope/` |
| CLI `registro` | Recopilar | S02 El registro (`registro_s02.json/.md`) | `02_evidencia/` |
| `inventory.py` + MCP REA (artefactos) | Recopilar | Insumo de S02/S06 | `02_evidencia/inventario.json` |
| Playwright + REA + `platform/tools/` | Recopilar | Ficha de síntoma del encargo del curso (Fase 1) | `evidence/capturas_curso/` |
| `evidence.py` + `ledger.py` + skill `evidencia-integridad` | Recopilar | Custodia: `MANIFEST.json`, `SHA256SUMS.txt`, huellas | `evidence/<run>/` |
| Detectores `php-shell` + skill `auditoria-php` | Analizar | Hallazgos estáticos → S03 El enunciado | `03_hallazgos/` |
| `sca.py` (+ `composer audit` / `pip audit` aportados) | Analizar | Enriquecimiento CVE → S03 | `03_hallazgos/` |
| `cvss.py` / `cvss4.py` + `knowledge/` | Analizar | Severidad vectorizada → S04 La cita (CWE↔control, sugerencia explicada) | `03_hallazgos/` |
| `cita.py` / `perfil.py` / `lista.py` + skill `correlacion-cumplimiento` | Analizar | S04 La cita · S05 El perfil (NIST CSF 2.0) · S06 La lista (CIS v8.1) | `02_evidencia/`, `03_hallazgos/` |
| `triage.py` + `reproduction.py` | Analizar | Decisión humana; `result_hash`; `verify` por hallazgo | `triage/`, `.c4a/` |
| `encargo.py` | Planificar (S07) | S07 El encargo — escrito para repetir, **sin firmar** | `01_plan/` |
| `frases.py` / `borrador.py` / `cierre.py` + `report.py`/`htmlmap.py`/`sarif.py` | Informar | S08 Las dos frases · S09 El borrador · S10 El cierre | `04_informe/` |
| Skills `speckit-*` | Transversal | Specs y `tasks.md` por sprint | `specs/001–010/`, `.specify/` |
| GitHub Project #7 vía `gh` | Transversal | Issues tras `tasks.md` (épica/historia/tarea) | GitHub (no es carpeta) |

## Brechas respecto del estado actual y plan de cierre

**P0 — bloquean la Fase 3 o la firma de productos**

1. `scope/autorizacion.md` sin firmar, sin ventana → compuerta cerrada. Cierre: el
   autorizador completa partes, ventana y firma (humano, no negociable).
2. Acciones humanas S01/S02 abiertas (medición de criterios SC y firma de alcance y
   registro, T032/T033/T038/T039). Cierre: auditor-firma; sin eso la cadena S03–S10
   queda en borrador por diseño.
3. Código de la plataforma del curso **no aportado** → Fase 2 no puede correr sobre el
   objetivo real (solo sobre fixtures). Cierre: el dueño solicita el código al cliente.

**P1 — calidad del análisis cuando llegue el código**

4. Ejecutar SCA (`sca.py`) sobre los manifiestos aportados y registrar versiones exactas.
5. Correlación de amenazas del fallo del curso con advisories públicos (ya en curso:
   ficha en `evidence/capturas_curso/FICHA_SINTOMA_848.md`) y pedir al administrador la
   versión exacta de la plataforma y los registros del despliegue.
6. Verificación en frío de `SHA256SUMS.txt` de cada corrida (skill `evidencia-integridad`).

**P2 — robustez y extensión**

7. Config de auditoría del curso persistida en `platform/config/` (hoy los scripts viven
   en `platform/tools/` con parámetros por CLI) para corridas reproducibles por config.
8. Decisión del dueño: encargo del curso como **S11** del ciclo SDD (skills `speckit-*`)
   o auditoría puntual fuera del ciclo; según eso caen la spec y las issues del Project.
9. Reconciliación del tablero (Project #7) con las tareas humanas abiertas.

> Nota sobre marcos (principio IV): ISO/IEC 27001:2022, NIST CSF 2.0 y CIS Controls v8.1
> están **implementados** como bases de conocimiento y módulos (`knowledge/`, `perfil.py`,
> `lista.py`); las leyes 21.663 (exigible), 21.719 (en preparación) y 21.459 (delimita lo
> permitido) están **mencionadas** con su estado verificado en `scope/alcance.md` §3 y se
> registran por obligación en `knowledge/normativas.json`. Que un marco sea seleccionable
> no acredita cobertura.
