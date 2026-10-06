# Cómo seguir madurando la plataforma C4A

Hoja de ruta derivada del estado real (commits `24b410c` → `6766f18` →
`e2e491a`) y de lo aprendido ejecutando los primeros ciclos. Cada ítem lleva el
porqué y un criterio de aceptación verificable. Se trabaja de arriba hacia
abajo; el `/loop` de maduración implementa uno por iteración.

## Lo que ya existe (línea base)

- 4 fases, 6 detectores estáticos, evidencia con SHA-256, CVSS 3.1 calculado,
  correlación a CWE/controles/normativas, reportes, ledger append-only.
- SCA real (osv-scanner / trivy / OSV.dev) con CVE verdaderas.
- Reproducción por ciclo (hash) y por hallazgo (`verify`).
- 12 pruebas en verde. Verificado contra la autoauditoría, VT (65.920 archivos,
  1450 hallazgos) y un fixture de dependencias vulnerables.

## Deudas observadas (lo que duele hoy)

1. **Ruido de falsos positivos.** Los detectores de criptografía y secretos
   marcan sus propios patrones y los fixtures de prueba. Sin triaje humano que
   persista, cada corrida repite el ruido.
2. **Sin salida para integrarse.** No hay SARIF ni código de salida por
   severidad, así que no puede cortar un pipeline de CI.
3. **Enriquecimiento CVE parcial.** El SCA crea hallazgos de CVE, pero no siempre
   los adjunta al hallazgo de dependencia estática (coincidencia por descripción).
4. **Catálogos mínimos.** CWE, controles y normativas son subconjuntos.
5. **Sin "mapa de evidencia y resultados" navegable** (lo pide la spec, §2).

## Near-term (próximas iteraciones del loop)

- **N1 · [HECHO, commit `9610d99`] Triaje persistente (revisión humana).** Un
  `triage.json` donde un humano marca `false-positive`, `accepted-risk` o
  `confirmed`; la plataforma lo aplica en cada corrida y separa *abiertos* de
  *triados*. Encarna «separar detección de conclusión».
- **N2 · [HECHO] Exportar SARIF + compuerta de CI.** `hallazgos.sarif.json`
  (SARIF 2.1.0, con `suppressions` para los falsos positivos triados) y
  `--fail-on <sev>` con código de salida !=0 para cortar un pipeline.
- **N3 · [HECHO] Menos falsos positivos.** Tres controles generales: se ignoran
  coincidencias en comentarios, se exige entropía mínima a los secretos, y se
  respeta un marcador en línea `c4a:ignore` (estilo `nosec`/`noqa`). Las propias
  reglas del detector y los fixtures se excluyen del alcance de la autoauditoría.
  *Resultado:* la autoauditoría pasó de 10 hallazgos ruidosos a 0 reales; los
  controles quedan probados con casos positivos y negativos.
- **N4 · Enriquecimiento CVE robusto + re-verificación SCA.** Correlacionar por
  nombre y versión exactos leyendo la evidencia, y que `verify` re-escanee los
  hallazgos de CVE. Ataca la deuda 3.
  *Aceptación:* el hallazgo de dependencia de `lodash` queda con sus CVE.

## Mid-term

- **M1 · Mapa de evidencia y resultados en HTML** navegable (un `index.html`
  autocontenido, sin dependencias) que enlace hallazgos ↔ evidencia ↔ controles.
- **M2 · Baseline y diff entre corridas**: «nuevos vs conocidos» para triage de
  regresiones, con tendencia de cumplimiento en el tiempo.
- **M3 · Catálogos completos** de CWE/controles y perfiles de normativa por
  encargo (ISO 27001 completo, NIST CSF 2.0, Ley 21.663/21.719 con artículos).
- **M4 · Empaquetado**: `pyproject.toml` con entrypoint `c4a`, para instalar y
  ejecutar como comando.
- **M5 · Más detectores**: IaC (Terraform/K8s), secretos con entropía, SAST
  ligero por lenguaje, permisos de nube.

## Long-term (alineado con la evolución de la spec, §14)

- Fase de red (nmap/sslscan) tras `scope/autorizacion.md` firmado, como módulo
  separado con las mismas garantías de evidencia y reproducción.
- Conectores MCP a bases de amenazas y a sistemas de tickets/flujo.
- Auditoría de APIs, cloud, identidad, contenedores y cadena de suministro.
- Integración con SIEM/EDR y gestión de vulnerabilidades.

## Principios que no se negocian al madurar

- No inventar: toda conclusión con evidencia reproducible.
- Detección separada de conclusión; la incertidumbre se declara.
- Solo lectura sobre el objetivo; la fase de red exige autorización escrita.
- Sin dependencias para el núcleo; los conectores externos degradan con honestidad.
- Cada cambio llega con prueba y queda en un commit verificable.
