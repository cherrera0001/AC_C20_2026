# Contrato: subcomando `enunciado` de C4A

Se invoca desde `platform/`. Opción común `--raiz` (por defecto `..`). Ningún subcomando toca la
red, ni escribe fuera de `03_hallazgos/`, ni modifica los archivos previos de esa carpeta.

| Subcomando | Argumentos | Efecto |
|---|---|---|
| `abrir` | — | Deriva el enunciado de la entrega de S02 y escribe `enunciados_s03.json`, `.md` y una ficha `enunciado-<id>.md` por enunciado |
| `corregir` | `--enunciado ID --campo {condicion,consecuencia,criterio,impacto} --valor --motivo --autor` | Registra la corrección; anula una firma previa |
| `descartar` | `--enunciado ID --motivo --autor` | Marca el enunciado descartado; no lo borra |
| `restablecer` | `--enunciado ID --motivo --autor` | Revierte un descarte |
| `revisar` | `--autor --motivo` | Marca el producto «revisado» |
| `firmar` | `--firmante --motivo` | Requiere «revisado» y criterio/impacto completos en los vigentes; escribe la firma con la huella de los bytes guardados |
| `verificar` | — | Recalcula la huella del producto, la de la entrega de S02 y la de cada evidencia citada; informa «evidencia alterada» y «hecho no vigente» |
| `entregar` | `[--json]` | Lista para S04: enunciados vigentes con campos y huellas, vacíos heredados y si está firmado |

`abrir` acepta `--fecha` (AAAA-MM-DD, uso determinista en pruebas). Sin ella usa la fecha del día
solo en el historial de eventos del auditor, nunca en la propuesta.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Hecho |
| 1 | Rechazado por regla de edición (sin motivo, sin autor, campo no corregible, firmar desde borrador, firmar con criterio/impacto vacíos, enunciado inexistente) |
| 2 | Falta el registro de S02 o un argumento |
| 3 | Una huella no corresponde a los bytes guardados (producto o evidencia citada) |
| 4 | El registro de origen cambió: se advierte y no se escribe |

## API de Python (para S04)

- `enunciado.cargar(raiz)`, `enunciado.entregar(raiz) -> dict`,
  `enunciado.estado_efectivo(raiz) -> str`.
