# Data Model: S01 — El alcance

Fase 1 de `/speckit-plan` (2026-10-21). Entidades de la spec (Key Entities) llevadas a la forma en que
se guardan. Esquema formal: [contracts/alcance_s01.schema.json](contracts/alcance_s01.schema.json).

## Archivos

| Archivo | Qué guarda | ¿Se firma? |
|---|---|---|
| `scope/alcance_s01.json` | Contenido canónico: insumos, filas, estado de aprobación e historial | Sí: su huella SHA-256 es la que se firma |
| `scope/alcance_s01.firma.json` | Registro de firma | No (es la firma) |
| `scope/alcance_s01.md` | Vista legible derivada, con la compuerta evaluada y la sección de pendientes | No |

## Alcance (`alcance_s01.json`, raíz)

| Campo | Tipo | Regla |
|---|---|---|
| `producto` | texto | Siempre `"S01 — El alcance"` |
| `version_esquema` | texto | `"1"` |
| `insumos` | lista de Insumo | Uno por documento de origen |
| `filas` | lista de Fila | Ordenadas por `orden`; ids únicos |
| `estado_aprobacion` | `borrador` \| `revisado` | `firmado` no se guarda: se deriva de una firma válida (ver Transiciones) |
| `historial` | lista de Evento | Solo se agrega; nunca se edita |
| `avisos` | lista de texto | Insumos faltantes, filas con insumo cambiado |

## Insumo

| Campo | Tipo | Regla |
|---|---|---|
| `archivo` | ruta relativa | `scope/alcance.md` o `scope/autorizacion.md` |
| `existe` | booleano | Si es falso, FR-002: se informa y todas sus filas quedan pendientes |
| `sha256` | texto \| nulo | Huella de los bytes del insumo al proponer |

## Fila

| Campo | Tipo | Regla |
|---|---|---|
| `id` | texto | `short_id("A", tipo, clave)`; estable entre corridas |
| `orden` | entero | Orden de presentación |
| `tipo` | `activo` \| `parte` \| `marco` \| `obligacion` \| `dominio` \| `exclusion` \| `regla` \| `compuerta` | |
| `clave` | texto | Identidad estable dentro del tipo |
| `valor` | texto | Lo afirmado, sin direcciones de red (FR-004) |
| `decision` | `incluido` \| `excluido` \| `pendiente de confirmar` | |
| `declarado` | texto \| nulo | Lo que dice el insumo cuando la decisión quedó pendiente (por ejemplo, `incluido` sin motivo) |
| `motivo` | texto | Vacío si no consta |
| `fuente` | texto | `archivo §sección`, o `"sin fuente"` (FR-010) |
| `huella_fuente` | texto \| nulo | SHA-256 del texto de la sección de origen; detecta cambios del insumo (FR-013) |
| `estado_aprobacion` | `borrador` \| `revisado` | Pasa a `revisado` al corregirse la fila |
| `marca_legal` | `VALIDAR` \| nulo | Solo en `obligacion` (FR-006) |
| `atributos` | objeto | Por tipo: `version`, `estado_herramienta`, `cobertura` (marco); `fuente_oficial`, `fecha_consulta`, `articulo`, `fundamento`, `antecedente` (obligación); `campos_faltantes`, `inicio`, `fin` (compuerta) |
| `observacion` | texto | Notas: «no se acredita con prueba técnica», «diferencia con la versión de referencia», etc. |
| `insumo_cambio` | booleano | Verdadero si la fila fue corregida y su sección de origen cambió |

**Fila pendiente**: `decision == "pendiente de confirmar"` o `marca_legal == "VALIDAR"`. Todas se
listan juntas en la vista, con su conteo (FR-019, SC-003).

## Evento (historial)

| Campo | Tipo | Regla |
|---|---|---|
| `tipo` | `correccion` \| `revision` \| `firma_anulada` | |
| `autor` | texto | Obligatorio |
| `fecha` | ISO-8601 UTC | La entrega el comando o `now_iso()` |
| `fila` | id \| nulo | Obligatorio en `correccion` |
| `campo` | `decision` \| `valor` \| `motivo` \| `version` | Solo en `correccion` |
| `anterior`, `nuevo` | texto | Solo en `correccion` |
| `motivo` | texto | Obligatorio y no vacío (FR-011) |

## Firma (`alcance_s01.firma.json`)

| Campo | Tipo | Regla |
|---|---|---|
| `archivo` | texto | `alcance_s01.json` |
| `sha256` | texto | `util.sha256_file` del archivo ya persistido |
| `firmante` | texto | Obligatorio |
| `fecha` | ISO-8601 UTC | |
| `motivo` | texto | Justificación de la firma; obligatoria (principio I) |
| `pendientes_al_firmar` | entero | Conteo de filas pendientes |
| `nota` | texto | «Firmar el alcance no abre la compuerta de autorización» |

## Estado de compuerta (derivado, no se guarda)

Se calcula desde las filas `compuerta` y una fecha de referencia.

| Atributo | Valores | Fuente |
|---|---|---|
| `firma` | `firmada` \| `no firmada` | Encabezado `ESTADO:` de `scope/autorizacion.md` y sección de firma |
| `completitud` | `completa` \| `incompleta` | Campos «por completar» de `scope/autorizacion.md` |
| `ventana` | `vigente` \| `vencida` \| `no informada` \| `no vigente (aún no comienza)` | Inicio y fin de `scope/autorizacion.md` §3. El cuarto valor extiende FR-008 para una ventana futura; como no es favorable, la compuerta queda cerrada. Una fecha ilegible cuenta como `no informada` |
| `resultado` | `abierta` \| `cerrada` | Abierta solo si los tres son favorables |
| `motivos` | lista | Uno por atributo no favorable |

La herramienta solo informa este estado; no lo cambia (FR-009).

## Transiciones de aprobación

```text
proponer ──▶ borrador ──corregir/revisar (autor + motivo)──▶ revisado ──firmar (firmante)──▶ firmado*
                                  ▲                                                     │
                                  └──────── corregir (anula la firma, evento) ──────────┘

* firmado = existe alcance_s01.firma.json y su sha256 coincide con los bytes de alcance_s01.json.
  Si no coincide (alteración externa), la firma no aplica y el estado efectivo es «revisado».
```

Reglas:

- `firmar` exige estado `revisado`; desde `borrador` se rechaza.
- `corregir` sin motivo se rechaza y no modifica nada.
- `proponer` sobre un alcance firmado: si los insumos no cambiaron, los bytes son idénticos y la firma
  sigue valiendo; si cambiaron, la herramienta advierte y no escribe.

## Consulta (contrato con S02)

`consultar(tipo, valor)` devuelve `respuesta` (`dentro` \| `fuera` \| `pendiente`), `fila` (id y
fuente), `motivo` y `firmado` (booleano). Un valor que no figura entre los activos o dominios del
alcance responde `fuera`. `evidencia_admisible(activo)` es verdadero solo si la respuesta es `dentro`.
