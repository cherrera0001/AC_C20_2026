# Minuta del encargo — Curso 848 del aula virtual

**Fecha**: 2026-10-27 · **Fase**: 0 (encargo) · **Autor**: equipo C4A (rol coordinador)
**Marco**: `docs/INSTRUCCION_AUDITORIA_CURSO.md` y `docs/EQUIPO_C4A.md`. La herramienta
propone; el auditor firma.

## 1. Hechos del encargo (lo reportado y lo confirmado)

| Elemento | Valor |
|---|---|
| Objetivo | Aula virtual del ejercicio (L Moodle; URL remitida por el dueño, registrada en `.env` con claves `URL_CURSO`/`USUARIO`/`CLAVE`; nombres de claves solo, valores jamás versionados) |
| Curso afectado | id **848**, «Auditoría a la Ciberseguridad» (Cuarto Ciclo) |
| Síntoma reportado | El curso «está fallando» al abrirlo con la cuenta del auditor |
| Fecha/hora de medición | capturas 2026-10-26 23:49–23:51; recon pasivo 2026-10-27 00:03–00:22 (hora local) |
| Fase 1 ejecutada | Sí — diagnóstico no invasivo de solo lectura (skill `diagnostico-curso`) |

## 2. Resultado medido (Fase 1)

| Medición | Resultado |
|---|---|
| Petición | `GET /course/view.php?id=848` con sesión autenticada |
| Código HTTP | **500** |
| Mensaje exacto | «Error — ID de módulo de curso no válida» (código de error Moodle `invalidcoursemodule`) |
| Radio de impacto | **Solo el curso 848**: los cursos hermanos «Auditoría a la Ciberseguridad» (id 121, 273, 664, 728) y 10+ cursos relacionados devuelven **200** |
| Perfil pasivo | Moodle ≥ 4.5; formato de curso `multitopic` (plugin GPL) + tema comercial; frente que reescribe rutas de administración; constante de despliegue `jsrev` consistente con un cambio el 2026-10-26 ~06:30 |

## 3. Lo descartado en Fase 1

- **No es fallo de login**: la autenticación funciona; la cuenta ve 37 cursos y accede a
  Report builder (captura `01_login.png`).
- **No es falta de permisos sobre el curso**: cursos del mismo nombre con la misma cuenta
  responden 200; el 500 es de aplicación, no de autorización.
- **No es caída general del aula**: el resto de las rutas navegadas responden con normalidad.

## 4. Decisiones y estado

- Evidencia cruda en `evidence/capturas_curso/` (fuera de git) con `SHA256SUMS.txt`
  generado y verificado el 2026-10-27; las 7 huellas coinciden con el registro previo.
- Hecho técnico formalizado en `03_hallazgos/sintoma_curso_848.md` (resultado: positivo
  al error de aplicación; hipótesis H1–H4, H4 «pendiente de confirmar»).
- Alcance del nuevo objetivo propuesto en `scope/alcance_curso_848.*` (borrador).
- Fase 2 queda **lista y bloqueada por código aportado**: config
  `platform/config/audit.curso.example.json` y bandeja `evidence/codigo_aportado/`.
- **Compuerta: CERRADA** (`scope/autorizacion.md` sin firmar). Sin tráfico activo;
  solo lectura y análisis estático de aportes.

## 5. Comando listo para Fase 2 (cuando exista código aportado)

```bash
cd platform
python3 -m c4a run --config config/audit.curso.example.json
python3 -m c4a verify --config config/audit.curso.example.json --run <RUN-ID>
```
