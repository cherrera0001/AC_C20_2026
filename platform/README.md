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
python3 -m c4a runs      --config config/audit.vt.json
python3 -m c4a reproduce --config config/audit.vt.json --run <RUN-ID>   # por ciclo (hash)
python3 -m c4a verify    --config config/audit.vt.json --run <RUN-ID>   # por hallazgo
python3 -m c4a run       --config config/audit.sca-demo.windows.json    # demo SCA (CVE reales vía OSV.dev)
```

En Windows, usa `py -3` o `python` y la config con rutas Windows
(`config/audit.vt.windows.json`). El acceso nativo a `F:\` es más rápido que
leer `/mnt/f` desde WSL.

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
evidencia y registro de reproducción, más un índice. En `03_hallazgos/` deja una
ficha por hallazgo y la `matriz_cumplimiento.csv`; en `02_evidencia/` el
`inventario.json`.

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

## Cómo se evita la sobreespeculación

- La detección se separa de la conclusión: un detector observa, otro rol valida.
- Los hallazgos de confianza indirecta nacen en `requires-validation`.
- No se afirma «seguro» sin evidencia; se registra la incertidumbre y los
  posibles falsos positivos en las notas.
- No se inventan CVEs ni resultados de herramientas no ejecutadas.

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
    cli.py  orchestrator.py  config.py  scope.py  inventory.py
    evidence.py  ledger.py  model.py  cvss.py  risk.py  correlation.py  report.py
    sca.py  reproduction.py
    detectors/  (secrets_files, dependencies, dockerfile, cicd, crypto_config, permissions)
    knowledge/  (cwe.json, cwe_map.json, controls_iso27001.json, normativas.json)
  config/   (audit.example.json, audit.vt*.json, audit.sca-demo.windows.json)
  examples/ (vuln-demo/ — fixture con dependencias vulnerables para el SCA)
  tests/    (test_cvss.py, test_sca.py, test_smoke.py)
```

## Pruebas

```bash
cd platform && python3 -m unittest discover -s tests -v
```
