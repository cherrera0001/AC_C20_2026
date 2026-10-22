# Data Model: S02 — El registro

Esquema formal: [contracts/registro_s02.schema.json](contracts/registro_s02.schema.json).

## Archivos

| Archivo | Qué guarda | ¿Se firma? |
|---|---|---|
| `02_evidencia/registro_s02.json` | Contenido canónico: alcance de origen, entradas derivadas, rechazos, historial | Sí |
| `02_evidencia/registro_s02.firma.json` | Firma: firmante, fecha, justificación, huella, «no consta» al firmar | No |
| `02_evidencia/registro_s02.md` | Vista: resumen, sección «No consta (N)», hechos, rechazos, historial | No |
| `evidence/registro_s02/<id>.<ext>` | Copia de la evidencia aportada (fuera de git) | Su huella está en el registro |

## Registro (raíz)

| Campo | Tipo | Regla |
|---|---|---|
| `producto` | texto | `"S02 — El registro"` |
| `version_esquema` | texto | `"1"` |
| `alcance` | objeto | `{archivo, sha256, firmado, minimo_de_referencia, autorizacion_sha256, compuerta, compuerta_fecha}`; `minimo_de_referencia` verdadero si no había `scope/alcance_s01.json`; `compuerta` es `abierta` o `cerrada`, evaluada en `compuerta_fecha` |
| `entradas` | lista de Entrada | Ordenadas: «no consta» y hechos por activo, dominio |
| `rechazos` | lista de Rechazo | Derivados del historial |
| `estado_aprobacion` | `borrador` \| `revisado` | «firmado» se deriva de una firma válida |
| `historial` | lista de Evento | Solo se agrega |
| `avisos` | lista de texto | |

## Entrada

| Campo | Tipo | Regla |
|---|---|---|
| `id` | texto | Hecho: `H-` + 10 hex de (activo, dominio, afirmación normalizada). «No consta»: `N-` + 10 hex de (activo, dominio) |
| `clase` | `hecho` \| `no consta` | |
| `activo`, `dominio` | texto | `dominio` = id de la fila del alcance (`A-…`) y su valor legible |
| `afirmacion` | texto | «no consta» en la clase homónima; filtrada con `limpiar` |
| `resultado` | `positivo` \| `negativo` \| `inconcluso` \| `no-ejecutado` | `no-ejecutado` solo en «no consta»; «inconcluso» si las evidencias discrepan |
| `motivo` | texto | En «no consta»: «compuerta cerrada», «requiere solicitud documental» o «sin evidencia» |
| `evidencias` | lista de Evidencia citada | Al menos una en `hecho` (FR-006) |
| `responsable` | texto | Quien aportó |
| `estado_aprobacion` | `borrador` \| `revisado` | |
| `marcas` | lista | Persistidas: `descartada`, `superada por H-…` (solo por un hecho vigente), `fuera del alcance vigente`, `alcance pendiente`. Calculada al verificar, no persistida: `evidencia alterada` |

## Evidencia citada

| Campo | Tipo | Regla |
|---|---|---|
| `id` | texto | `E-` + 10 hex de (`sha256_original`, tipo) |
| `tipo` | `documental` \| `tecnica` | |
| `origen` | texto | Obligatorio en documental (aclaración Q1) |
| `ubicacion_original` | texto | Ruta relativa al repositorio si está dentro; si no, solo el nombre del archivo |
| `copia` | texto \| nulo | Ruta de la copia en `evidence/registro_s02/`; nulo si `sin_copia` |
| `sin_copia` | booleano | Declara referencia sin copia (principio III) |
| `sha256_original` | texto | Huella del archivo de origen al aportar |
| `sha256_guardado` | texto \| nulo | Huella de la copia ya escrita |
| `fecha_recoleccion` | fecha ISO | La declara el auditor |
| `responsable` | texto | |
| `resultado` | resultado técnico | Lo que esa evidencia muestra |
| `corrida` | texto \| nulo | `RUN-…` si viene de una corrida de c4a |

## Rechazo

`{evidencia (tipo, ubicación, huella), activo, dominio, motivo, regla, fila_alcance, fecha, autor}`.

## Evento (historial)

| `tipo` | Campos |
|---|---|
| `aporte` | activo, dominio, afirmación, evidencia (como arriba), autor, fecha |
| `rechazo` | Rechazo |
| `correccion` | entrada, campo (`afirmacion` \| `resultado` \| `motivo`), anterior, nuevo, motivo, autor, fecha |
| `descarte` | entrada, motivo, autor, fecha |
| `restablecimiento` | entrada, motivo, autor, fecha (revierte un descarte) |
| `revision` | motivo, autor, fecha |
| `firma_anulada` | motivo, autor, fecha |

## Transiciones

```text
abrir ─▶ borrador ─aportar─▶ borrador ─corregir/descartar/revisar─▶ revisado ─firmar─▶ firmado*
                                                    ▲                                  │
                                                    └──── cualquier cambio (anula) ────┘
* firmado = existe la firma y su sha256 coincide con los bytes de registro_s02.json.
```

- `firmar` exige «revisado», firmante y justificación; guarda `no_consta_al_firmar`.
- Toda escritura posterior a la firma (aporte, rechazo, corrección, descarte, restablecimiento o revisión) la anula (evento `firma_anulada`).
- Un aporte sobre un registro «revisado» lo devuelve a «borrador».
- Si el hecho que superó una «no consta» se descarta, la «no consta» vuelve a valer.
- `verificar` con una evidencia alterada: la entrada se informa «evidencia alterada» y sale de la entrega; si el registro está firmado, se informa «firmado con evidencia alterada».
- `abrir` sobre un registro firmado cuyo alcance cambió: aviso, código 4, no escribe.
