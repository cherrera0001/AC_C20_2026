# Registro de triaje

Decisiones humanas que cambian el tratamiento de un hallazgo. Persisten entre corridas vía `triage.json` y se aplican en cada auditoría.

| ID | Decisión (estado) | Componente | Nota |
|---|---|---|---|
| F-def509cf5e | false-positive | `platform/examples/vuln-demo/package.json` | Correlación CVE: no automática en este ciclo; requiere feed/SCA. Triaje: false-positive por cristobal (2026-10-06T02:58:05Z): patron del propio detector, no cri |