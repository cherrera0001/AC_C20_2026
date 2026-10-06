# Historia de Usuario — Motor de Auditoría de 4 fases (GitHub Projects)

## Épica

```
[ÉPICA] Auditoría de Ciberseguridad de Cumplimiento — Motor de 4 fases
Objetivo: Ejecutar, con Claude Code, una auditoría híbrida (ethical hacking +
cumplimiento ISO 27001 / Ley 21.663 / Ley 21.719) sobre un objetivo autorizado,
produciendo informe técnico, matriz de cumplimiento y resumen ejecutivo.
Label: epic   ·   Milestone: Sprint 1 — MVP Auditoría
```

## Historia de usuario (issue principal)

```markdown
## Historia de usuario
Como **auditor de ciberseguridad de C4A**,
quiero **un flujo automatizado de 4 fases (Planificar → Recopilar → Analizar → Informar)
ejecutado desde Claude Code sobre un objetivo autorizado**,
para **entregar hallazgos técnicos verificados y mapeados a ISO 27001, Ley 21.663 y
Ley 21.719, con evidencia reproducible y un informe listo para el cliente**.

## Criterios de aceptación (Gherkin)

Escenario: No se ejecuta sin autorización
  Dado que no existe ./scope/autorizacion.md con ventana y rango vigentes
  Cuando se inicia el flujo
  Entonces el sistema se detiene y solicita la autorización antes de tocar la red

Escenario: Las fases respetan el orden
  Dado que la Fase 1 no ha producido ./01_plan/plan.md
  Cuando se intenta iniciar la Fase 2
  Entonces el flujo no avanza hasta que exista el plan

Escenario: Cada hallazgo queda encuadrado
  Dado un hallazgo técnico verificado en la Fase 3
  Cuando se registra su ficha
  Entonces incluye CVSS v4 con vector, control ISO 27001 y artículo legal afectado

Escenario: Entregable final completo
  Dado que la Fase 4 finalizó
  Entonces existen informe_tecnico.md, resumen_ejecutivo.md, plan_remediacion.md
  Y la matriz_cumplimiento.csv enlaza hallazgo → control → ley → acción

## Definition of Done
- [ ] Las 4 fases corren de punta a punta sobre el objetivo de laboratorio (192.168.1.14)
- [ ] Toda evidencia versionada, con hash y timestamp
- [ ] Datos personales enmascarados
- [ ] Revisión de castellano del informe (¿¡, tildes en mayúsculas, « », coma decimal)
- [ ] Revisado por un segundo par antes de entrega

Labels: user-story, auditoria, claude-code
Estimación: 8 story points
```

## Desglose en issues (tareas), mapeado a las 4 fases

| # | Issue (tarea) | Fase | Labels | Pts |
|---|---|---|---|---|
| 1 | Redactar `scope/alcance.md` y plantilla de `autorizacion.md` | Planificar | `scope` | 2 |
| 2 | Definir criterios de severidad (CVSS v4 + impacto cumplimiento) en `plan.md` | Planificar | `scope` | 2 |
| 3 | Implementar reconocimiento/enumeración autorizados y registro en `./evidence/` | Recopilar | `recon` | 3 |
| 4 | Generar `inventario.json` (puertos, servicios, versiones) | Recopilar | `recon` | 2 |
| 5 | Correlacionar servicios ↔ CVE y malas configuraciones | Analizar | `analysis` | 3 |
| 6 | Crear fichas de hallazgo con mapeo ISO / ley | Analizar | `compliance` | 3 |
| 7 | Generar `matriz_cumplimiento.csv` | Analizar | `compliance` | 2 |
| 8 | Ensamblar informe técnico (skill pentest-report) | Informar | `report` | 3 |
| 9 | Resumen ejecutivo (1 página) | Informar | `report` | 1 |
| 10 | Plan de remediación con plazos | Informar | `report` | 2 |

## Configuración sugerida en GitHub Projects

- **Campos personalizados:** `Fase` (Planificar/Recopilar/Analizar/Informar), `Prioridad`, `Story Points`, `Estado` (Todo/In Progress/Review/Done).
- **Vistas:** tablero Kanban por `Estado` + tabla agrupada por `Fase` para ver la cadena de dependencias.
- **Dependencias:** issues 3-4 bloqueados por 1-2; 5-7 por 3-4; 8-10 por 5-7 (refleja que ninguna fase se salta).
