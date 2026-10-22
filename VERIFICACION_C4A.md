# Registro de verificación del lineamiento

Fecha: 19-10-2026, America/Santiago. Repositorio local y `main` remoto coinciden en `6a68de78e7d5f7900dbcd8b022b7ae24fb1bea9f`. Esta revisión entrega documentos; no modifica el motor ni acredita el laboratorio.

## Pruebas del motor

Ejecutadas desde WSL en `platform/`: `python3 -m unittest discover -s tests -v`. Resultado: **24 pruebas, OK**, 1,088 segundos reportados por unittest. Cubren CVSS, detectores/falsos positivos, HTML, SARIF, parsers SCA, ciclo/reproducción y triaje. No acreditan cobertura CIS, dictamen humano ni pruebas reales contra Metasploitable. Python/py no estaban disponibles en el shell Windows; se usó el Python existente en WSL.

## Comprobaciones adicionales con fixtures

El script local `.audit-tools/check-matrix.py` llama directamente a `controls_matrix` con un único control y un hallazgo sintético ALTO, variando el estado. No detecta vulnerabilidades ni ejecuta comandos contra un objetivo. Resultados:

- `requires-validation` → `no-cumple`.
- `false-positive` → `no-cumple`.
- `accepted-risk` → `no-cumple`.

Esto confirma que el estado no evita el dictamen automático de la matriz. No demuestra por sí solo cuál sería el cumplimiento real del control; ese es precisamente el dato pendiente de evaluación.

El mismo script crea evidencia de comando sintética mediante `EvidenceStore.from_command`, escribe manifiesto y compara el SHA-256 del archivo persistido con el registrado. Resultado: **False**. La salida original se hashea antes de añadir encabezados al archivo. Los temporales de esta comprobación se eliminan al terminar. No se corrigió el código: se incorpora como condición del MVP.

## GitHub

Consultas de solo lectura con `gh api user`, `gh project view`, `gh project field-list`, `gh project item-list --limit 200`, `gh issue list --state all --limit 150`, API de repositorio, contenido de README y commit de main. Identidad: `cherrera0001`. Project #7 privado, abierto, 18 campos, total 40 elementos, 40 `Todo`. Issues #1–#40 abiertas. Consulta explícita de `assignees` de issues: ninguna asignada. Sin sprint informado en los elementos. No se modificaron issues, campos, workflows, vistas ni visibilidad.

Se verificó existencia del README remoto y SHA de main. Esto contradice la descripción histórica de #40 sobre remoto vacío; no implica que el resto de sus criterios esté satisfecho. La configuración efectiva de auto-add y de vistas continúa sin comprobar.

## REA por MCP

Clone solicitado: `gh repo clone morluto/rea .audit-tools/rea`. Fuente SHA `833136507dd79d959340b09862a53af344e4f1b3`. Paquete local `rea-agents@6.7.0`, instalado con `--ignore-scripts --no-audit --no-fund` bajo `.audit-tools/runtime`, sin setup global. Node v24.19.0. No se leyó `.env`.

Cliente temporal `.audit-tools/rea-mcp-review.mjs` inicia un proceso `rea mcp` por stdio, realiza `initialize`, `notifications/initialized`, `tools/list` y llamadas reales a `list_browser_targets` / `inspect_web_page`. El servidor se identifica como REA 6.7.0 y publica 207 herramientas. Chrome headless con perfiles temporales aislados; inspección pasiva de documentación pública. Al terminar se cierra el navegador creado y el proceso MCP.

1. **DefectDojo** — [documentación](https://docs.defectdojo.com/). Evidencia `ev_f90c46784591637500823f6f972079e41a64f4aef5861c5d5c4258c4374404c1`. Observación 23:47:29–23:47:30 UTC (20:47 local). Captura accesible de 328 nodos, incluyendo documentación sobre triaje, deduplicación y priorización. Archivo local `.audit-tools/rea-defectdojo.json`; SHA-256 `4f568501bb373640e6a061701b9ff5054f16a42021a00eaa7c2d324ba4265d0b`.
2. **eramba** — [Compliance Management](https://www.eramba.org/compliance-management). Evidencia `ev_3bd458814cca66bb3fc020c94e21d7f5638167e9ffb18a3458a63af6f46c91ee`. Observación 23:47:53–23:47:54 UTC (20:47 local), 697 nodos. La página describe pruebas manuales/automatizadas de controles y delimita su función respecto de gestión de vulnerabilidades. Archivo `.audit-tools/rea-www.eramba.org.json`; SHA-256 `8f50fdf968c2a62cda8155c4e971c40deefbde01863ff84b4e365210b73fa341`.
3. **Drata** — [producto](https://drata.com/products/compliance-automation). Evidencia `ev_b29c9059506913abec0e2ef4dce423265bd14bbbaf46a1bc07f0efa5fefe6018`. Observación 23:48:02–23:48:03 UTC (20:48 local), 42 nodos. REA observó una página de comprobación de acceso titulada «Un momento…»; **no observó funcionalidades del producto**. No se intentó eludirla. Archivo `.audit-tools/rea-drata.com.json`; SHA-256 `744c5371715c5269e456f15ff24de84471b4e9d5c0ae42e36513303b1237acc4`. La comparativa de Drata se apoya en las fuentes oficiales consultadas por búsqueda web, incluida [Evidence Overview](https://help.drata.com/en/articles/13404035-evidence-overview).

Límites comunes de REA: ventana desde la conexión, actividad previa no capturada, sin cuerpos/cookies/valores de storage, sin source maps descargados, plataforma/arquitectura del navegador no observadas. La evidencia recoge lo declarado en páginas públicas; no demuestra implementación interna, eficacia, precios, licencias ni capacidades contratadas. Las capturas y dependencias quedan locales y excluidas de Git mediante `.audit-tools/`.

## Alcance entregado

Se conservó `PROMPT_SPEC_KIT.md` sin modificar. No se inicializó `.specify/`, no se invocaron comandos Spec Kit ni se implementó el MVP: la entrega es la instrucción y el lineamiento solicitados. No hubo pruebas contra Metasploitable, commit, push ni escrituras en GitHub. La autorización permanece sin firmar.
