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
