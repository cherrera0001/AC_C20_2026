# Data Model: S04 — La cita

## Archivos

| Archivo | Rol | Entra a git |
|---|---|---|
| `03_hallazgos/citas_s04.json` | Contenido canónico y determinista; su huella SHA-256 es la que se firma | Sí |
| `03_hallazgos/citas_s04.firma.json` | Firma: firmante, fecha, justificación, huella y conteos | Sí |
| `03_hallazgos/citas_s04.md` | Vista legible del producto completo | Sí |
| `03_hallazgos/cita-<id>.md` | Una ficha legible por cita (FR-012) | Sí |

Nada escribe fuera de `03_hallazgos/`. Serialización con `alcance.serializar` (claves ordenadas, sangría
2, UTF-8, salto final).

## JSON canónico

```json
{
  "producto": "S04 — La cita",
  "version_esquema": "1",
  "entrega": {
    "archivo": "03_hallazgos/enunciados_s03.json",
    "sha256": "<huella del JSON de S03>",
    "entrega_sha256": "<huella canónica de enunciado.entregar(raiz)>",
    "firmado": false
  },
  "citas": [ ... ],
  "vacios": [ ... ],
  "estado_aprobacion": "borrador",
  "historial": [ ... ],
  "avisos": [ ... ]
}
```

### `citas[]`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | string | `C-` + 10 hex; `short_id("C", riesgo_id)`; estable ante correcciones |
| `riesgo` | objeto | `{id, condicion}` copiado del riesgo de S03 |
| `marco` | string | Uno de `ISO-27001:2022`, `NIST-CSF:2.0`, `CIS-v8.1`, o `aporte del auditor` |
| `control` | string \| null | Identificador del catálogo; `null` si `identificador.estado` es `pendiente-confirmar` |
| `identificador` | objeto | `{estado, fuente}`; `fuente` es el catálogo o la que declare el auditor |
| `fundamento` | string | Términos del catálogo que coincidieron con el dominio, criterio o impacto; no vacío |
| `correspondencias_adicionales` | objeto[] | `{marco, control, fundamento, motivo, autor, fecha}`; solo las añade el auditor |
| `evidencias` | objeto[] | `{id, tipo, ubicacion_original, copia, sha256_original, sha256_guardado}` del riesgo |
| `estado_aprobacion` | string | `borrador` o `revisado` |
| `marcas` | string[] | `descartado` (persistida); `riesgo no vigente`, `evidencia alterada` (calculadas en `verificar`) |
| `correcciones` | objeto[] | `{autor, fecha, campo, anterior, nuevo, motivo}` |

### `vacios[]`

Vacíos heredados de S03 (contexto, sin cita). `{id, activo, dominio, motivo}`.

### `historial[]`

Eventos: `propuesta` (abrir), `correccion`, `descarte`, `restablecimiento`, `revision`, `firma_anulada`.

## Propuesta (FR-005)

| Paso | Regla |
|---|---|
| Candidatos | Términos del riesgo (dominio + criterio + impacto) contra `terminos` de cada control del catálogo |
| Elección | Mayor número de términos coincidentes; empate → orden del catálogo |
| Sin candidato | `marco` y `control: null`; `identificador.estado: pendiente-confirmar`; `fundamento` = «ningún control del catálogo coincide con los términos del riesgo» |
| Identificador | Solo si el control existe en el catálogo del marco elegido (principio IV) |

## Firma

```json
{
  "archivo": "03_hallazgos/citas_s04.json",
  "sha256": "<huella de los bytes ya guardados>",
  "firmante": "...",
  "fecha": "AAAA-MM-DD",
  "motivo": "...",
  "citas_al_firmar": 0,
  "pendientes_al_firmar": 0,
  "nota": "Firmar la cita no abre la compuerta de autorización ni dictamina cumplimiento."
}
```

## Estados

`borrador → revisado → firmado`. Cualquier corrección, descarte, restablecimiento o revisión posterior a
la firma la anula (`firma_anulada`).

## Verificación

`verificar(raiz)` devuelve: `huella_ok` (JSON contra firma), `entrega_ok` (entrega de S03 contra la
registrada), `evidencias_alteradas[]` y `riesgos_no_vigentes[]`, `estado` y `estado_informado`.

## Códigos de error (`CitaError`)

| Código | Uso |
|---|---|
| 1 | Regla de edición: sin motivo/autor, campo no corregible, firmar desde borrador, firmar con un marco fuera de la constitución sin aporte declarado, cita inexistente |
| 2 | Falta la entrega de S03 o un argumento |
| 3 | Huella que no corresponde a los bytes guardados (producto o evidencia citada) |
| 4 | La entrega de S03 cambió: `abrir` firmado o acción del auditor |
