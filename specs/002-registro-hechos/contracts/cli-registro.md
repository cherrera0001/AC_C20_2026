# Contrato: subcomando `registro` de C4A

Se invoca desde `platform/`. Opción común `--raiz` (por defecto `..`). Ningún subcomando toca la red,
ni escribe en `scope/` ni en `02_evidencia/inventario.json`.

| Subcomando | Argumentos | Efecto |
|---|---|---|
| `abrir` | — | Deriva el registro del alcance de S01 (o del mínimo de referencia), reaplica el historial y escribe `registro_s02.json` y `.md` |
| `aportar` | `--activo --dominio --afirmacion --resultado {positivo,negativo,inconcluso} --evidencia RUTA --tipo {documental,tecnica} --fecha-recoleccion AAAA-MM-DD --autor [--origen TEXTO] [--corrida RUN-ID] [--sin-copia]` | Evalúa la admisibilidad; si pasa, copia la evidencia y agrega el aporte; si no, registra el rechazo |
| `corregir` | `--entrada ID --campo {afirmacion,resultado,motivo} --valor --motivo --autor` | Registra la corrección; anula una firma previa |
| `descartar` | `--entrada ID --motivo --autor` | Marca la entrada descartada; no la borra |
| `restablecer` | `--entrada ID --motivo --autor` | Revierte un descarte |
| `revisar` | `--autor --motivo` | Marca el registro «revisado» |
| `firmar` | `--firmante --motivo` | Requiere «revisado»; escribe la firma con la huella de los bytes guardados |
| `verificar` | — | Recalcula la huella del registro y de cada evidencia copiada; informa las entradas con «evidencia alterada» |
| `entregar` | `[--json]` | Lista para S03: entradas vigentes con evidencias, huellas y si está firmado |

`--dominio` acepta el id de la fila del alcance (`A-…`) o un texto que `alcance.consultar` resuelva.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Hecho (un aporte rechazado también termina en 0 si el rechazo quedó registrado; se informa el motivo) |
| 1 | Rechazado por regla de edición (sin motivo, sin autor, firmar desde borrador o sin justificación, entrada inexistente) |
| 2 | Falta el registro, el archivo de evidencia o un argumento |
| 3 | Una huella no corresponde a los bytes guardados (registro o evidencia) |
| 4 | El registro está firmado y el alcance cambió: se advierte y no se escribe |

## API de Python (para S03)

- `registro.cargar(raiz)`, `registro.entregar(raiz) -> dict`, `registro.estado_efectivo(raiz) -> str`.
