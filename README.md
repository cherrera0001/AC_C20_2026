# Laboratorio C4A — Auditoría de Ciberseguridad de Cumplimiento

Repositorio de trabajo para la auditoría híbrida (ethical hacking + cumplimiento
ISO/IEC 27001:2022, Ley 21.663 y Ley 21.719) descrita en `AUDIT_PROMPT.md`.

## Cómo se ejecuta

El motor son las 4 fases del `AUDIT_PROMPT.md`, en orden, cada una escribe su
salida en disco y la siguiente la consume:

1. **Planificar** → `01_plan/plan.md`
2. **Recopilar** → `02_evidencia/inventario.json` + crudos en `evidence/`
3. **Analizar** → `03_hallazgos/<id>.md` + `03_hallazgos/matriz_cumplimiento.csv`
4. **Informar** → `04_informe/` (técnico, resumen ejecutivo, plan de remediación)

Las 4 fases son la definición canónica del proceso de auditoría a la
ciberseguridad. La herramienta que asiste al auditor se construye aparte, en 10
sprints (S01–S10), con Spec Kit: cada sprint es una épica con sus historias de
usuario, y su avance se mide en el Project. El ciclo de construcción está en
`PROMPT_SPEC_KIT.md` y sus artefactos en `.specify/` y `specs/`. Lo que la
herramienta produce cae en las carpetas de las 4 fases; no abre un árbol paralelo.

## Planificación y versionado

- Revisión y propuesta del MVP: [LINEAMIENTO_C4A.md](LINEAMIENTO_C4A.md).
- Instrucción única: [INSTRUCCION_UNICA_C4A.md](INSTRUCCION_UNICA_C4A.md).
- Evidencia de verificación: [VERIFICACION_C4A.md](VERIFICACION_C4A.md).
- Plantilla complementaria de cierre: [PLANTILLA_CIERRE_C4A.md](04_informe/PLANTILLA_CIERRE_C4A.md).

- Project ágil: [C4A — Gestión Ágil 2026](https://github.com/users/cherrera0001/projects/7), enlazado al repositorio GitHub.
- Método de trabajo, estimación por tallas, métricas y DoR/DoD: `AGILE_PROJECT.md`.
- Formularios GitHub Issues: `.github/ISSUE_TEMPLATE/`.
- Prompt técnico único para Claude Code (auditoría, GitHub y gestión ágil): `CLAUDE_CODE_PROMPT.md`.
- Las tallas son esfuerzo relativo y no equivalen a horas. No publicar evidencia cruda, secretos ni datos personales.

## Compuerta de seguridad

**No se toca el objetivo sin `scope/autorizacion.md` firmado y con ventana
vigente** (Ley 21.459). La plantilla ya está puesta; está marcada como NO FIRMADA.

## Estructura

| Ruta | Qué vive aquí |
|---|---|
| `scope/alcance.md` | Qué se audita, con qué criterios, qué queda fuera |
| `scope/autorizacion.md` | La autorización escrita (compuerta) |
| `01_plan/` | Plan de la Fase 1 |
| `02_evidencia/` | Inventario estructurado (puertos, servicios, versiones) |
| `03_hallazgos/` | Fichas de hallazgo + matriz de cumplimiento |
| `04_informe/` | Entregables finales |
| `evidence/` | Salidas crudas, con timestamp y hash (no entran a git en crudo) |

## Estación del auditor (WSL)

Las pruebas se ejecutan desde Ubuntu en WSL. Instrumental instalado: `nmap`,
`nikto`, `whatweb`, `sslscan`, `hydra`, `smbclient`, más `jq`, `python3`, `dig`,
`nc`, `curl`. Metasploit no está instalado por defecto.
