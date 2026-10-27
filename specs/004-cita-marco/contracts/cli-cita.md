# Contrato: subcomando `cita` de C4A

Se invoca desde `platform/`. Opción común `--raiz` (por defecto `..`). Ningún subcomando toca la red,
escribe fuera de `03_hallazgos/` ni modifica archivos previos de esa carpeta.

| Subcomando | Argumentos | Efecto |
|---|---|---|
| `abrir` | `[--fecha AAAA-MM-DD]` | Deriva la cita de la entrega de S03 y escribe `citas_s04.json`, `.md` y una ficha `cita-<id>.md` por cita |
| `corregir` | `--cita ID --campo {marco,control,fundamento,motivo} --valor --motivo --autor` | Registra la corrección; anula una firma previa |
| `agregar` | `--cita ID --marco --control --fundamento --motivo --autor` | Añade una correspondencia adicional del auditor |
| `descartar` | `--cita ID --motivo --autor` | Marca la cita descartada; no la borra |
| `restablecer` | `--cita ID --motivo --autor` | Revierte un descarte |
| `revisar` | `--autor --motivo` | Marca el producto «revisado» |
| `firmar` | `--firmante --motivo` | Requiere «revisado»; escribe la firma con la huella de los bytes guardados |
| `verificar` | — | Recalcula la huella del producto, la de la entrega de S03 y la de cada evidencia citada |
| `entregar` | `[--json]` | Lista para S05: citas vigentes con sus campos, estado del identificador y huellas; vacíos heredados; si está firmado |

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Hecho |
| 1 | Rechazado por regla de edición |
| 2 | Falta la entrega de S03 o un argumento |
| 3 | Una huella no corresponde a los bytes guardados |
| 4 | La entrega de S03 cambió: se advierte y no se escribe |

## API de Python (para S05)

- `cita.cargar(raiz)`, `cita.entregar(raiz) -> dict`, `cita.estado_efectivo(raiz) -> str`.
