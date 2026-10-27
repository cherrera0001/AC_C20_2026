# Data Model: S03 — El enunciado

**Input**: especificación en `specs/003-enunciado-riesgo/spec.md`.

## Archivos

| Archivo | Rol | Entra a git |
|---|---|---|
| `03_hallazgos/enunciados_s03.json` | Contenido canónico y determinista; su huella SHA-256 es la que se firma | Sí |
| `03_hallazgos/enunciados_s03.firma.json` | Firma: firmante, fecha, justificación, huella y conteos | Sí |
| `03_hallazgos/enunciados_s03.md` | Vista legible del producto completo | Sí |
| `03_hallazgos/enunciado-<id>.md` | Una ficha legible por enunciado (FR-012) | Sí |

Nada escribe fuera de `03_hallazgos/`. El JSON se serializa con `alcance.serializar` (orden de
claves, sangría 2, UTF-8, salto final): dos aperturas con los mismos insumos producen bytes
idénticos (FR-010).

## JSON canónico

```json
{
  "producto": "S03 — El enunciado",
  "version_esquema": "1",
  "registro": {
    "archivo": "02_evidencia/registro_s02.json",
    "sha256": "<huella del registro de S02>",
    "entrega_sha256": "<huella canónica de registro.entregar(raiz)>",
    "firmado": false,
    "estado": "borrador"
  },
  "enunciados": [ ... ],
  "vacios": [ ... ],
  "estado_aprobacion": "borrador",
  "historial": [ ... ],
  "avisos": [ ... ]
}
```

### `enunciados[]`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | string | `R-` + 10 hex; deriva del id del hecho (`short_id("R", hecho_id)`); estable ante correcciones |
| `activo` | string | Copia del hecho |
| `dominio` | objeto | `{fila, valor}` del hecho |
| `hecho` | objeto | `{id, afirmacion, resultado}` del hecho de origen |
| `condicion` | string | Propuesta desde la afirmación; corregible |
| `consecuencia` | string | Propuesta según el resultado técnico; corregible |
| `criterio` | string | Propuesta cualitativa; el auditor lo completa antes de firmar |
| `impacto` | string | Vacío en la propuesta; el auditor lo completa antes de firmar |
| `falta` | string[] | Derivado: marcas y resultado (ver reglas abajo) |
| `evidencias` | objeto[] | `{id, tipo, ubicacion_original, copia, sha256_original, sha256_guardado}` citadas del hecho |
| `estado_aprobacion` | string | `borrador` o `revisado` («firmado» se deriva de la firma válida) |
| `marcas` | string[] | `descartado` (persistida); `hecho no vigente`, `evidencia alterada` (calculadas en `verificar`) |
| `correcciones` | objeto[] | `{autor, fecha, campo, anterior, nuevo, motivo}` |

### `vacios[]`

Entradas «no consta» vigentes de la entrega: `{id, activo, dominio, resultado, motivo, marcas}`.
No son riesgos enunciados (FR-003); alimentan «lo que falta» a nivel de producto.

### `historial[]`

Eventos: `propuesta` (abrir), `correccion`, `descarte`, `restablecimiento`, `revision`,
`firma_anulada`. Cada uno con `autor`, `fecha`, `enunciado` (cuando aplica), `campo`, `anterior`,
`nuevo`, `motivo` según el tipo. Nada se borra.

### Reglas de derivación de `falta`

| Condición del hecho | Elemento de `falta` |
|---|---|
| Marca «alcance pendiente» | `confirmar el alcance (pendiente)` |
| Resultado `inconcluso` | `evidencia adicional para decidir` |
| Resultado `negativo` | `reevaluar en una próxima revisión (la no observación no descarta la reaparición)` |
| Evidencia sin copia (`sha256_guardado` ausente) | `verificar el original de la evidencia sin copia` |
| Registro de origen no firmado | `el registro de origen no está firmado` |

### Propuestas de texto (FR-005)

| Campo | Regla |
|---|---|
| `condicion` | La afirmación del hecho |
| `consecuencia` (positivo) | La condición se observa en la evidencia citada; su materialización puede afectar la confidencialidad, la integridad o la disponibilidad del activo |
| `consecuencia` (negativo) | La condición no se observó en la evidencia citada; esto no acredita cumplimiento ni descarta su reaparición |
| `consecuencia` (inconcluso) | La evidencia citada no permite decidir si la condición se materializa |
| `criterio` | Propuesta cualitativa: evidencia directa de tipo documental o técnica y resultado observado; la cita del marco corresponde a S04 |
| `impacto` | Cadena vacía (lo completa el auditor) |

## Firma

```json
{
  "archivo": "03_hallazgos/enunciados_s03.json",
  "sha256": "<huella de los bytes ya guardados>",
  "firmante": "...",
  "fecha": "AAAA-MM-DD",
  "motivo": "...",
  "enunciados_al_firmar": 0,
  "vacios_al_firmar": 8,
  "nota": "Firmar el enunciado no abre la compuerta de autorización."
}
```

## Estados

`borrador → revisado → firmado`. Un aporte posterior a la revisión no aplica (S03 no admite
aportes: propone desde S02); cualquier corrección, descarte, restablecimiento o revisión posterior
a la firma la anula (`firma_anulada`), como en S01 y S02.

## Verificación

`verificar(raiz)` devuelve: `huella_ok` (JSON contra firma), `entrega_ok` (entrega de S02 contra la
registrada), `evidencias_alteradas[]` y `hechos_no_vigentes[]` (por enunciado), `estado` y
`estado_informado` («firmado con evidencia alterada», «firmado con hecho no vigente», etc.).
`estado_efectivo(raiz)` devuelve `borrador`, `revisado` o `firmado`.

## Códigos de error (`EnunciadoError`)

| Código | Uso |
|---|---|
| 1 | Regla de edición: sin motivo/autor, campo no corregible, firmar desde borrador, firmar con campos vacíos, enunciado inexistente |
| 2 | Falta el producto anterior (registro de S02) o un argumento |
| 3 | Huella que no corresponde a los bytes guardados (detectada en `verificar`) |
| 4 | El registro de origen cambió (`abrir` firmado o acción del auditor) |
