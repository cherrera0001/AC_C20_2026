# Línea de origen: del chat inicial al repositorio actual

## Resumen ejecutivo

El origen del repositorio C4A **no fueron dos archivos sueltos**, sino una
conversación (este chat) que convirtió un encargo del usuario en **tres archivos
base** entregados en un solo acto. Esos tres archivos son el contrato del proyecto:

1. `scope/alcance.md` — qué se audita, con qué criterios y qué queda fuera.
2. `AUDIT_PROMPT.md` — rol, reglas, orden de las cuatro fases y estructura de salida.
3. `historia_usuario.md` — actor, objetivo, criterios de aceptación y desglose para GitHub Projects.

Los tres fueron creados juntos el **30-sep 21:21** (timestamp idéntico en los tres
ficheros), lo que confirma que salieron de una única entrega del chat.

> Nota de ubicación (2026-10-21): la documentación de gobierno e historia del proyecto
> vive en `docs/`. Ahí están hoy los archivos base `AUDIT_PROMPT.md` e `historia_usuario.md`,
> este mismo documento y los prompts locales; las menciones sin carpeta del relato
> histórico se refieren a esos archivos. `scope/alcance.md` conserva su ruta canónica.

Antes de ellos
hubo un **Insumo 0** (un prompt maestro que reordenó el encargo del usuario) y una
**verificación normativa** que fijó el estado vigente de la ley chilena. Después de
ellos, el repositorio creció por maduraciones sucesivas (N1→N4, M1) y por la estación
local (`CLAUDE_CODE_PROMPT.md`, `ESTACION_LOCAL.md`).

> Corrección respecto de la versión anterior de este documento: ya **no** se afirma
> que el origen sean dos archivos, ni que los "tres archivos base" queden en `VALIDAR`.
> La evidencia del chat y los timestamps idénticos los confirman.

## 1. La secuencia real, paso a paso

Reconstrucción de lo que ocurrió en el chat, en orden:

| # | Momento | Entrada | Qué produjo |
|---|---------|---------|-------------|
| 1 | Encargo del usuario | Dos imágenes (diagrama de 4 cajas: Planificar → Recopilar → Analizar → Informar) + pedido de **3 insumos** | Define la necesidad: servicio híbrido *ethical hacking* + auditor normativo (ISO 27001, Ley 21.663, Ley 21.719) |
| 2 | Verificación normativa | Búsqueda web sobre vigencia de la normativa chilena | Dato clave: Ley 21.663 **operativa** (ANCI desde ene-2025, nómina OIV 24-jul-2026, reporte 3 h / 72 h); Ley 21.719 **en flujo** (vigencia 01-dic-2026 con proyecto de postergación a 01-dic-2027) |
| 3 | **Insumo 0** | El propio encargo, reordenado | Prompt maestro limpio (ROL / OBJETIVO / CONTEXTO / RESTRICCIONES / MÉTODO) sobre el cual iterar |
| 4 | **Insumo 1** | Insumo 0 + verificación normativa | Definición de alcance (naturaleza híbrida, mapeo normativo con estado vigente, reglas de enganche, severidad, entregables) |
| 5 | **Insumo 2** | Insumo 0 + diagrama de 4 fases | Prompt para Claude Code (CLI): las 4 cajas convertidas en 4 fases con entrada/salida en disco |
| 6 | **Insumo 3** | Insumo 0 + criterios de aceptación | Historia de usuario con épica, Gherkin, 10 issues y configuración de GitHub Projects |
| 7 | Entrega | Pedido del usuario: "entregar los 3 insumos por separado como archivos markdown" | Se crearon y compartieron **3 archivos**: `alcance.md`, `AUDIT_PROMPT.md`, `historia_usuario.md` |

El paso 7 es el momento exacto de nacimiento del repositorio: los tres ficheros con
timestamp 30-sep 21:21.

## 2. Diagrama de génesis (cómo nacieron los tres archivos)

```text
        Usuario
   ┌───────────────────────────────┐
   │ 2 imágenes (diagrama 4 cajas)  │
   │ + "construir 3 insumos"        │
   └───────────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────┐        ┌───────────────────────────┐
        │  Verificación web     │───────▶│ Estado normativo vigente   │
        │  (normativa chilena)  │        │ 21.663 exigible · 21.719   │
        └──────────┬───────────┘        │ en preparación (postergable)│
                   │                     └──────────────┬─────────────┘
                   ▼                                    │
        ┌──────────────────────┐                        │
        │ INSUMO 0             │◀───────────────────────┘
        │ Prompt maestro       │  (reordena el encargo, base limpia)
        └──────────┬───────────┘
                   │  deriva los tres insumos coherentes entre sí
      ┌────────────┼─────────────────────┐
      ▼            ▼                      ▼
 ┌─────────┐  ┌──────────────┐   ┌──────────────────┐
 │INSUMO 1 │  │ INSUMO 2     │   │ INSUMO 3         │
 │alcance  │  │ AUDIT_PROMPT │   │ historia_usuario │
 └────┬────┘  └──────┬───────┘   └────────┬─────────┘
      │              │                    │
      └──────────────┼────────────────────┘
                     ▼
         Entrega: 3 archivos .md  (30-sep 21:21)
         scope/alcance.md · AUDIT_PROMPT.md · historia_usuario.md
```

## 3. Los tres archivos base (confirmados)

| Archivo | Insumo | Rol en el proyecto | Timestamp | Estado |
|---------|--------|--------------------|-----------|--------|
| `scope/alcance.md` | Insumo 1 | Define qué se audita, criterios y fuera de alcance | 30-sep 21:21 | Confirmado |
| `AUDIT_PROMPT.md` | Insumo 2 | Define rol, reglas, 4 fases y estructura de salida | 30-sep 21:21 | Confirmado |
| `historia_usuario.md` | Insumo 3 | Define actor, objetivo, aceptación y seguimiento | 30-sep 21:21 | Confirmado |

El timestamp idéntico en los tres es la evidencia de que fueron una única entrega
del chat, no tres creaciones separadas. Esto resuelve y cierra la incógnita que la
versión anterior dejaba en `VALIDAR`.

## 4. Del diagrama de 4 cajas a las 4 fases del prompt

Las dos imágenes del encargo mostraban un flujo de cuatro cajas. El Insumo 2
(`AUDIT_PROMPT.md`) las convirtió en cuatro fases con entrada y salida explícitas en
disco, de modo que ninguna fase se salta:

```text
  Imagen (4 cajas)            AUDIT_PROMPT.md (4 fases con E/S)
  ───────────────             ─────────────────────────────────
  Planificar      ──────────▶ Fase 1 → 01_plan/plan.md
  Recopilar       ──────────▶ Fase 2 → 02_evidencia/inventario.json + evidence/
  Analizar        ──────────▶ Fase 3 → 03_hallazgos/<id>.md + matriz_cumplimiento.csv
  Informar        ──────────▶ Fase 4 → 04_informe/{informe,resumen,plan}.md
```

Cada fase consume el producto de la anterior; esa dependencia es la misma que la
historia de usuario expresa como criterios Gherkin ("las fases respetan el orden").

## 5. De los tres archivos base al repositorio actual

Los tres archivos base son el **contrato**. El repositorio actual es el resultado de
aplicar ese contrato y madurarlo. Capas, en orden de aparición:

```text
  [1] GÉNESIS (chat, 30-sep)
      scope/alcance.md · AUDIT_PROMPT.md · historia_usuario.md
                 │
                 ▼
  [2] OPERACIÓN
      scope/autorizacion.md · platform/c4a/ · README.md
                 │
                 ▼
  [3] ESTACIÓN LOCAL
      CLAUDE_CODE_PROMPT.md (prompt consolidado) · ESTACION_LOCAL.md
                 │
                 ▼
  [4] MADURACIÓN (commits)
      N1  triaje persistente
      N2  SARIF 2.1.0 + compuerta de CI
      N3  reducción de falsos positivos en origen
      N4  enriquecimiento CVE + re-verificación SCA
      M1  mapa de evidencia y resultados en HTML
                 │
                 ▼
  [5] RESULTADOS DE EJECUCIÓN
      01_plan/ · 02_evidencia/ · 03_hallazgos/ · 04_informe/ · evidence/ · reports/ · triage/
```

`CLAUDE_CODE_PROMPT.md` es la evolución consolidada del Insumo 2: añade fuentes
canónicas (S01–S04, `extraccion/G4.md`), el paso explícito de "Línea de origen" y la
regla `VALIDAR`. No reemplaza a `AUDIT_PROMPT.md`; lo extiende para la estación local.

## 6. Qué se puede afirmar con el origen confirmado

Con la secuencia del chat y los tres archivos base se afirma:

- El origen es **este chat**, no un repositorio previo ni un manifiesto externo.
- Hubo un **Insumo 0** (prompt maestro) del que derivan coherentemente los tres insumos.
- Los **tres archivos base** son `alcance.md`, `AUDIT_PROMPT.md` e `historia_usuario.md`,
  entregados juntos el 30-sep 21:21.
- El estado normativo (21.663 exigible, 21.719 en preparación postergable) fue
  **verificado en origen** y quedó reflejado en el alcance.

Sigue sin poder afirmarse solo desde el origen (pertenece a la ejecución, no al contrato):

- Qué activos se evaluaron, qué servicios/CVEs se encontraron y qué hallazgos se registraron.
- Qué hashes, timestamps y firmas conserva cada evidencia.
- Qué marco y versión se fijó para S04 ni el resultado de cumplimiento.
- La firma de `scope/autorizacion.md` (hoy plantilla, no firmada).

## 7. Estado de provenance actualizado

| Fuente o capa | Estado | Explicación |
|---|---|---|
| `historia_usuario.md` | Confirmado | Insumo 3 del chat; objetivo y aceptación (30-sep 21:21) |
| `AUDIT_PROMPT.md` | Confirmado | Insumo 2 del chat; rol, fases y restricciones (30-sep 21:21) |
| `scope/alcance.md` | Confirmado | Insumo 1 del chat; alcance y criterios (30-sep 21:21) |
| Insumo 0 (prompt maestro) | Confirmado | Reordenamiento del encargo; vive en el historial del chat, no como fichero |
| Verificación normativa | Confirmado | Búsqueda web en origen; fijó el estado de 21.663 y 21.719 |
| **Tres archivos base exactos** | **Confirmado** | Son los tres insumos; timestamp idéntico 30-sep 21:21 |
| `scope/autorizacion.md` | Confirmado (sin firmar) | Plantilla de autorización creada después (05-oct) |
| `CLAUDE_CODE_PROMPT.md` | Confirmado | Consolidación del Insumo 2 para la estación local |
| `platform/c4a/` | Confirmado | Implementación técnica del motor |
| `01_plan/` … `04_informe/`, `evidence/`, `reports/`, `triage/` | Confirmado | Productos de ejecución y maduración N1–N4, M1 |
| S01–S04, `extraccion/G4.md` | Confirmado | Materiales académicos; no sustituyen texto oficial |

## 8. Regla de interpretación

```text
encargo del usuario (2 imágenes + 3 insumos pedidos)
        ↓
verificación normativa vigente
        ↓
Insumo 0 (prompt maestro)
        ↓
tres archivos base: alcance · AUDIT_PROMPT · historia_usuario   ← ORIGEN
        ↓
operación + estación local
        ↓
maduración N1–N4, M1
        ↓
resultados de ejecución y revisión humana
```

El origen es el chat, concretado en tres archivos base. Todo lo posterior es
implementación y maduración. Las conclusiones de ejecución no verificadas siguen la
regla `VALIDAR`; el **contrato de origen** ya está confirmado y no vuelve a `VALIDAR`.
