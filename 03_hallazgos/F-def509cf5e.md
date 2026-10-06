# F-def509cf5e — Dependencias npm sin fijar en platform/examples/vuln-demo/package.json

- **Tipo:** technical
- **Severidad:** MEDIO  ·  **Prioridad combinada:** 7.7
- **Estado:** false-positive  ·  **Confianza:** direct
- **Probabilidad:** media  ·  **Impacto:** medio
- **Componente:** `platform/examples/vuln-demo/package.json`
- **Detector:** dependencies  ·  **Detectado:** 2026-10-06T03:22:56Z
- **Roles:** Rol Técnico de Investigación

## Descripción
1 dependencia(s) usan rangos abiertos (^, ~, *, latest, >=). No implica vulnerabilidad por sí mismo; sí dificulta reproducir builds y rastrear qué versión concreta corre. La correlación con CVE requiere una herramienta de SCA (revisión manual).

## CVSS v3.1
- Vector: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L`
- Puntaje base: **5.6** (MEDIUM)
- Fuente: detector-baseline — Vector base por clase de problema; revisar y ajustar al contexto real.

## Clasificación
- **CWE:** CWE-1104 (Use of Unmaintained Third Party Components), CWE-1395 (Dependency on Vulnerable Third-Party Component)
- **CVE:** sin correlación automática — revisión manual
- **Controles ISO:** A.8.8
- **Normativas:** ISO-27001, LEY-21663
- **Impacto de cumplimiento:** A.8.8 gestión de vulnerabilidades técnicas.

## Evidencia
- `E-e28caaa22e` — platform/examples/vuln-demo/package.json · sha256 `cb3d9bd07eb230b7…` · 1 dependencia(s) con versión sin fijar

  ```
  lodash: ^4.17.4  [dependencies]
  ```

## Reproducción
- Método: re-ejecutar la auditoría y comparar por id y hash de evidencia
- Comando: `jq ".dependencies, .devDependencies" "platform/examples/vuln-demo/package.json"`
- Resultado esperado: objeto con specs que incluyen ^, ~, * o latest
- Entorno: Python 3.10+ (solo librería estándar); acceso de lectura al objetivo

## Remediación
Fijar versiones exactas y confiar en el lockfile; habilitar actualizaciones automáticas controladas (Dependabot/Renovate).

**Recomendaciones:** Ejecutar un SCA (npm audit, osv-scanner, Trivy) para correlacionar con CVEs reales.

**Notas:** Correlación CVE: no automática en este ciclo; requiere feed/SCA. Triaje: false-positive por cristobal (2026-10-06T02:58:05Z): patron del propio detector, no cripto real
