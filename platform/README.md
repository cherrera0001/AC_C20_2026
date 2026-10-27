# C4A — Plataforma de Auditoría de Ciberseguridad de Cumplimiento

Herramienta ejecutable que audita un repositorio o sistema y produce evidencia
verificable, hallazgos clasificados, correlación con CWE/CVSS, controles y
normativas, e informes reproducibles. Primer ciclo: **auditoría estática de
repositorio, de solo lectura**. La fase de red (pentest) permanece tras su
compuerta de autorización y no corre aquí.

Diseño: modular, **sin dependencias externas** (solo librería estándar de
Python 3.10+), para que cualquiera pueda re-ejecutar una auditoría sin instalar
nada. Esa es la base de la reproducibilidad.

## Uso

```bash
cd platform
python3 -m c4a catalog                      # detectores y normativas
python3 -m c4a init      --config config/audit.example.json
python3 -m c4a run       --config config/audit.vt.json
python3 -m c4a run       --config config/audit.vt.json --fail-on ALTO   # corta CI si hay altos abiertos
python3 -m c4a runs      --config config/audit.vt.json
python3 -m c4a reproduce --config config/audit.vt.json --run <RUN-ID>   # por ciclo (hash)
python3 -m c4a verify    --config config/audit.vt.json --run <RUN-ID>   # por hallazgo
python3 -m c4a triage    --config config/audit.example.json --finding <FID> --decision false-positive --reason "..." --by tu-nombre
python3 -m c4a run       --config config/audit.sca-demo.windows.json    # demo SCA (CVE reales vía OSV.dev)
```

En Windows, usa `py -3` o `python` y la config con rutas Windows
(`config/audit.vt.windows.json`). El acceso nativo a `F:\` es más rápido que
leer `/mnt/f` desde WSL.

## El alcance (S01)

`alcance` deja el producto de S01 en archivos nuevos de `scope/`. La herramienta
**propone**; el auditor **corrige** y **firma**. Solo lee `scope/alcance.md` y
`scope/autorizacion.md`; nunca los escribe ni toca la red.

```bash
cd platform
python3 -m c4a alcance proponer  --raiz ..        # borrador: scope/alcance_s01.json + .md
python3 -m c4a alcance compuerta --raiz ..        # firma, completitud y ventana (solo lectura)
python3 -m c4a alcance corregir  --raiz .. --fila <ID> --campo decision --valor excluido --motivo "..." --autor "..."
python3 -m c4a alcance revisar   --raiz .. --autor "..." --motivo "..."
python3 -m c4a alcance firmar    --raiz .. --firmante "..." --motivo "..."
python3 -m c4a alcance verificar --raiz ..        # huella firmada vs. bytes guardados
python3 -m c4a alcance consultar --raiz .. --tipo dominio --valor "..."   # dentro | fuera | pendiente
```

- `alcance_s01.json` es el contenido canónico y determinista; su huella SHA-256 es la que se firma.
- `alcance_s01.firma.json` guarda firmante, fecha, justificación, huella y pendientes al firmar.
  Cualquier corrección posterior anula la firma.
- `alcance_s01.md` es la vista legible, con una sola sección «Pendientes (N)».
- **Firmar el alcance no abre la compuerta de autorización.** Ninguna prueba técnica
  corre sin `scope/autorizacion.md` firmada, completa y con ventana vigente.

Contrato completo: `specs/001-alcance-auditoria/contracts/cli-alcance.md`.

## El registro (S02)

`registro` deja el producto de S02 en archivos nuevos de `02_evidencia/`: lo que se puede
afirmar sobre el activo, cada hecho con su evidencia y su huella, y lo que no consta. La
herramienta **propone**; el auditor **corrige**, **descarta**, **restablece** y **firma**. Lee el
alcance de S01 y la compuerta en solo lectura; no ejecuta pruebas ni toca la red.

```bash
cd platform
python3 -m c4a registro abrir     --raiz ..        # una entrada «no consta» por activo y dominio
python3 -m c4a registro aportar   --raiz .. --activo "..." --dominio <A-…|texto|activo> --afirmacion "..." \
        --resultado positivo --evidencia <ruta> --tipo documental --origen "..." --fecha-recoleccion AAAA-MM-DD --autor "..."
python3 -m c4a registro corregir  --raiz .. --entrada <ID> --campo resultado --valor inconcluso --motivo "..." --autor "..."
python3 -m c4a registro descartar --raiz .. --entrada <ID> --motivo "..." --autor "..."   # restablecer: igual
python3 -m c4a registro revisar   --raiz .. --autor "..." --motivo "..."
python3 -m c4a registro firmar    --raiz .. --firmante "..." --motivo "..."
python3 -m c4a registro verificar --raiz ..        # huella del registro y de cada evidencia
python3 -m c4a registro entregar  --raiz .. --json # entradas vigentes para S03
```

- `registro_s02.json` es el contenido canónico y determinista; su huella SHA-256 es la que se firma.
  `registro_s02.firma.json` guarda firmante, fecha, justificación, huella y cuántas «no consta» había.
  Cualquier escritura posterior anula la firma.
- `registro_s02.md` es la vista legible, con una sola sección «No consta (N)» y otra de rechazos.
- Cada evidencia aportada se copia a `evidence/registro_s02/` (fuera de git) y se registra la huella
  del original y la de la copia guardada. `--sin-copia` declara una referencia sin copia.
- Se rechaza, con su motivo, la evidencia de otro activo, de un dominio fuera del alcance, de una
  corrida sobre otro objetivo, la técnica sin autorización vigente en su fecha y la documental sin
  origen declarado.
- **«No consta» no es «sin hallazgos».** Quiere decir que no se miró o que falta evidencia.
- **Firmar el registro no abre la compuerta de autorización.**

Contrato completo: `specs/002-registro-hechos/contracts/cli-registro.md`.

## El ciclo de productos S03–S10

Cada sprint deja su producto con la misma forma: la herramienta **propone** (`abrir`),
el auditor **corrige** (`corregir` u su acción propia), **revisa** y **firma**; `verificar`
recalcula huellas y `entregar` da la lista vigente al sprint siguiente. Todo es
determinista (mismos insumos → mismos bytes), nada se borra y los archivos previos de
cada carpeta quedan intactos.

```bash
cd platform
python3 -m c4a enunciado abrir --raiz ..     # S03: un riesgo por hecho vigente (03_hallazgos/)
python3 -m c4a cita abrir --raiz ..          # S04: cada riesgo en un marco, con nombre y versión
python3 -m c4a perfil abrir --raiz ..        # S05: seis funciones del NIST CSF 2.0
python3 -m c4a lista abrir --raiz ..         # S06: CIS Controls v8.1 aplicables, partiendo por el inventario
python3 -m c4a encargo abrir --raiz ..       # S07: el trabajo escrito para repetir, SIN firmar (01_plan/)
python3 -m c4a frases abrir --raiz ..        # S08: el mismo resultado para gerencia y para quien corrige
python3 -m c4a borrador abrir --raiz ..      # S09: borrador del informe de cierre (04_informe/)
python3 -m c4a cierre abrir --raiz ..        # S10: exige el borrador FIRMADO (código 5 si no lo está)
```

Lo específico de cada producto:

- **enunciado**: propone condición, consecuencia, criterio y «lo que falta»; un hecho
  negativo lleva nota fija de que no acredita cumplimiento. Firmar exige criterio e
  impacto completados por el auditor.
- **cita**: la correspondencia riesgo ↔ control es sugerencia explicada; el identificador
  solo se propone si consta en la base de conocimiento — si no, queda «pendiente de
  confirmar». Se puede corregir marco/versión/identificador/fundamento y añadir
  correspondencias.
- **perfil**: propone la asignación riesgo ↔ función a partir del dominio y el fundamento;
  el auditor reasigna con motivo. Una función sin material queda «no consta», nunca
  «sin hallazgos». Firmar exige las seis síntesis.
- **lista**: propone controles CIS anclados en hechos del inventario; los que requieren
  políticas, personas o procesos quedan «pendiente-documental». Se pueden descartar,
  recuperar y añadir a mano con fuente.
- **encargo**: sin firma de aprobación (la guía S07 es «sin firmar»): lleva autoría y una
  huella de integridad. Nunca contiene comandos, direcciones de red, puertos ni
  credenciales, y no abre ni transporta la autorización: la corrida que repite verifica
  `scope/autorizacion.md` por sí misma.
- **frases**: las dos frases deben decir el mismo resultado (mismos conteos, mismos
  vacíos con la misma causa); una corrección que rompe la consistencia se rechaza, y la
  de gerencia no lleva identificadores de controles.
- **borrador**: ensambla encabezado (cliente Comercial Andes Sur SpA), resumen,
  desarrollo, acciones sin responsables ni fechas inventados, vacíos y anexo de
  trazabilidad. Solo archivos nuevos en `04_informe/`.
- **cierre**: tabla de recorrido (afirmación → ficha → huella); el tercero recorre y se
  registra con `cierre registrar --tercero ...` (la herramienta no simula el recorrido).
  Firmar exige los enlaces resueltos. **El cierre no publica ni entrega el informe:**
  eso es decisión del dueño.

Especificaciones: `specs/003-enunciado-riesgo/` a `specs/010-cierre/`.

## Cómo funciona el workflow

Cuatro fases, cada una alimenta a la siguiente; todo lo escribe en las carpetas
del laboratorio (`01_plan/ … 04_informe/`, `evidence/`, `.c4a/`):

1. **Alcance** (`scope.py`) — resuelve el objetivo, aplica exclusiones y hace
   cumplir el acceso de SOLO LECTURA (nunca escribe en el objetivo; guarda
   contra path traversal).
2. **Inventario** (`inventory.py`) — recorre el objetivo una vez y describe
   lenguajes, dependencias, contenedores, IaC, CI/CD y archivos sensibles.
3. **Detección + evidencia** (`detectors/`, `evidence.py`) — cada detector
   observa y aporta evidencia con hash; **no concluye el riesgo**.
4. **Riesgo + correlación + reporte** (`risk.py`, `correlation.py`,
   `report.py`) — deriva severidad del CVSS, correlaciona a controles y
   normativas, y escribe los entregables.

El `orchestrator.py` encadena todo y registra una ejecución en el ledger.

## Cómo se integran Skills, MCP y scripts

- **Scripts**: el propio paquete `c4a` es el conjunto de scripts idempotentes
  (inventario, detección, validación de hashes, reportes, reproducción). Cada
  corrida es parametrizable por config y deja registro de ejecución.
- **Skills**: los detectores son la primera encarnación de *skills* de dominio
  (secretos, dependencias, Dockerfile, CI/CD, criptografía, permisos). Añadir
  una skill = añadir una subclase de `Detector` al registro.
- **SCA / CVE** (`sca.py`, implementado): ejecuta `osv-scanner`/`trivy` locales
  o consulta la API de OSV.dev por red, parsea el resultado y genera hallazgos
  con CVE reales. Es el primer conector externo real; los demás (gitleaks,
  escaneo de imágenes, y la fase de red nmap/sslscan tras autorización) quedan
  como enganches marcados, sin fabricar resultados.

## Cómo se captura la evidencia

`evidence.py` registra cada pieza con identificador, tipo, fuente, ubicación,
fecha, **hash SHA-256**, responsable, alcance, estado, resultado y nivel de
confianza (directa/indirecta). El crudo se guarda bajo `evidence/<run_id>/` con
un `MANIFEST.json` y un `SHA256SUMS.txt` para verificación externa. Los
secretos se enmascaran siempre; nunca se vuelca un valor en claro.

## Cómo se clasifica un hallazgo

Tipo (`compliance | control | technical | risk | evidence`), severidad
(`CRITICO … INFORMACIONAL`, más `REQUIERE-VALIDACION` y `NO-REPRODUCIDO`),
estado del ciclo de vida (`detected → requires-validation → validated →
reproduced …`) y confianza. La severidad se **deriva del CVSS calculado**, no de
una opinión. La prioridad combina severidad técnica con impacto de cumplimiento:
una obligación exigible (p. ej. Ley 21.663) escala por encima de un CVSS alto
sin encuadre.

## Cómo se relaciona con CVE, CWE, CVSS y normas

- **CVSS**: `cvss.py` calcula el puntaje base v3.1 del vector con la fórmula
  oficial de FIRST. Verificable contra la calculadora oficial (ver pruebas).
- **CWE**: cada detector asigna CWE justificadas (catálogo en `knowledge/`).
- **Normas/controles**: `correlation.py` usa un mapa curado CWE→control→norma y
  solo adjunta normativas que la config declaró aplicables.
- **CVE**: correlación REAL por SCA (`sca.py`), no inventada. Si hay motor
  habilitado —`osv-scanner` o `trivy` locales, o la API de OSV.dev por red
  (opt-in)— se generan hallazgos con CVE reales, su peor CVSS y evidencia de la
  herramienta. Si no hay motor, se degrada con honestidad: «revisión manual».
  Config en el bloque `"sca"` (desactivado por defecto). Demostrado contra
  OSV.dev: `lodash@4.17.4` → 8 CVE, `minimist@1.2.0` → CVE-2020-7598 (CVSS 9.8).

## Cómo se genera el reporte

`report.py` escribe: resumen ejecutivo, informe técnico, plan de remediación,
reporte de riesgos, mapa CVE/CWE/CVSS, matriz de normativas, registro de
evidencia, de reproducción y de triaje, más un índice. En `03_hallazgos/` deja
una ficha por hallazgo y la `matriz_cumplimiento.csv`; en `02_evidencia/` el
`inventario.json`. `htmlmap.py` genera `04_informe/mapa.html`: un mapa de
evidencia y resultados navegable, de un solo archivo sin red (tiles de
severidad, hallazgos con su detalle, filtro por texto/severidad y claro/oscuro).
Para integración con CI y code scanning, `sarif.py` emite
`04_informe/hallazgos.sarif.json` (SARIF 2.1.0); `--fail-on <sev>` corta el
pipeline con código de salida !=0 si queda algún hallazgo abierto en o sobre esa
severidad (los falsos positivos triados no cuentan).

## Cómo se reproduce una auditoría

Dos niveles:

- **Por ciclo** (`reproduce`): cada corrida calcula un `result_hash` a partir
  **solo del contenido** (ids de hallazgo deterministas + hashes de evidencia),
  nunca de relojes ni rutas. Re-ejecuta y compara: si el objetivo no cambió, el
  hash coincide; si cambió, lista qué hallazgos aparecen o desaparecen. Los
  hallazgos de SCA se excluyen del hash porque dependen de una base externa.
- **Por hallazgo** (`verify`, `reproduction.py`): re-ejecuta la comprobación de
  cada hallazgo de forma nativa (re-lee el componente, re-calcula su hash y
  re-corre el mismo detector acotado a ese archivo) y lo marca `reproduced`,
  `not-reproduced` o `external` (CVE, se re-verifica re-escaneando). Determinista
  y multiplataforma; no depende de que exista grep. Resultado en
  `.c4a/verify/<run_id>.json`.

Todo queda en el ledger append-only `.c4a/runs.jsonl`.

## Cómo entra la revisión humana (triaje)

`triage.py` + el subcomando `triage` guardan la decisión de un humano sobre un
hallazgo —`false-positive`, `accepted-risk` o `confirmed`— en `triage.json`,
indexada por el id determinista del hallazgo. En cada corrida la plataforma
aplica el triaje: cambia el estado, separa *abiertos* de *triados* y deja
`registro_triaje.md` con quién decidió y por qué. El triaje no altera el
`result_hash` (cambia estado, no severidad), así que la reproducibilidad del
análisis estático se preserva. Es la encarnación de «detección ≠ conclusión»:
el detector observa, el humano concluye, y la conclusión persiste entre corridas.

## Cómo se evita la sobreespeculación

- La detección se separa de la conclusión: un detector observa, otro rol valida.
- Los hallazgos de confianza indirecta nacen en `requires-validation`.
- No se afirma «seguro» sin evidencia; se registra la incertidumbre y los
  posibles falsos positivos en las notas.
- No se inventan CVEs ni resultados de herramientas no ejecutadas.
- Controles de falso positivo en origen: se ignoran coincidencias en comentarios,
  se exige entropía mínima a los valores de secreto (un `password=example` no es
  secreto), y se respeta un marcador en línea `# c4a:ignore` (estilo `nosec`).
  Lo que el control no decide, lo decide el humano con el triaje.

## Cómo se controla el acceso

- Solo lectura sobre el objetivo; la plataforma jamás escribe en él.
- Guarda contra salir del directorio objetivo (path traversal).
- La fase de red exige `scope/autorizacion.md` firmado (Ley 21.459) y NO forma
  parte de este ciclo.
- El ledger es append-only: no se borran registros de auditoría.

## Estructura del código

```
platform/
  c4a/
    cli.py  orchestrator.py  config.py  scope.py  inventory.py  alcance.py
    evidence.py  ledger.py  model.py  cvss.py  risk.py  correlation.py  report.py
    sca.py  reproduction.py
    detectors/  (secrets_files, dependencies, dockerfile, cicd, crypto_config, permissions)
    knowledge/  (cwe.json, cwe_map.json, controls_iso27001.json, normativas.json)
  config/   (audit.example.json, audit.vt*.json, audit.sca-demo.windows.json)
  examples/ (vuln-demo/ — fixture con dependencias vulnerables para el SCA)
  tests/    (test_cvss.py, test_sca.py, test_smoke.py, test_alcance_us1..us4.py, alcance_fixtures.py)
```

## Pruebas

```bash
cd platform && python3 -m unittest discover -s tests -v
```

## Equipo e instrumental

Esta plataforma es el núcleo del instrumental C4A. Los roles que la operan (agente
propone, auditor humano firma), los skills (`auditoria-php`, `diagnostico-curso`,
`correlacion-cumplimiento`, `evidencia-integridad`, `speckit-*`), los MCP configurados
(REA, Playwright) y los scripts locales de diagnóstico (`tools/`) están definidos en
[`../docs/EQUIPO_C4A.md`](../docs/EQUIPO_C4A.md) y justificados por fase en
[`../docs/CATALOGO_HERRAMIENTAS_AUDITORIA.md`](../docs/CATALOGO_HERRAMIENTAS_AUDITORIA.md).
