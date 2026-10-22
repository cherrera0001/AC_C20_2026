# Contrato: subcomando `alcance` de C4A

Interfaz que S01 expone al auditor y a S02. Se invoca desde `platform/`. Ningún subcomando toca la
red ni escribe en `scope/alcance.md` o `scope/autorizacion.md`.

Opción común: `--raiz <ruta>`, la raíz del repositorio del ejercicio (por defecto `..`, el padre de
`platform/`). Los archivos de producto se resuelven como `<raiz>/scope/alcance_s01.*`.

| Subcomando | Argumentos | Efecto | Salida |
|---|---|---|---|
| `proponer` | `[--fecha-referencia AAAA-MM-DD]` | Lee los insumos, deriva las filas, reaplica correcciones previas, escribe `alcance_s01.json` y `alcance_s01.md` | Conteo de filas y de pendientes; avisos |
| `corregir` | `--fila ID --campo {decision,valor,motivo,version} --valor TEXTO --motivo TEXTO --autor NOMBRE [--fecha ISO]` | Registra la corrección, deja el alcance en `revisado`, anula una firma previa | Fila corregida |
| `revisar` | `--autor NOMBRE --motivo TEXTO [--fecha ISO]` | Marca el alcance `revisado` sin cambiar filas | Estado |
| `firmar` | `--firmante NOMBRE --motivo TEXTO [--fecha ISO]` | Requiere `revisado` y una justificación (principio I); escribe `alcance_s01.firma.json` con la huella de los bytes guardados | Huella firmada |
| `verificar` | — | Recalcula la huella del archivo guardado y la compara con la firma | `firmado`, `revisado (firma no aplica)` o `sin firma` |
| `consultar` | `--tipo {activo,dominio,marco,obligacion,exclusion} --valor TEXTO` | Responde si está en el alcance | `dentro`, `fuera` o `pendiente`, con fila, motivo y si está firmado |
| `compuerta` | `[--fecha-referencia AAAA-MM-DD]` | Evalúa la compuerta de autorización en solo lectura | Atributos, resultado y motivos |

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Operación hecha |
| 1 | Rechazada por regla (sin motivo, firmar desde borrador o sin justificación, fila inexistente) |
| 2 | Falta el producto o un argumento |
| 3 | La firma no corresponde a los bytes guardados (alteración o cambio posterior) |
| 4 | El alcance está firmado y los insumos cambiaron: se advierte y no se escribe |

## API de Python (para S02)

- `alcance.cargar(raiz) -> dict`: lee `alcance_s01.json`.
- `alcance.consultar(raiz, tipo, valor) -> dict`: igual que el subcomando.
- `alcance.evidencia_admisible(raiz, activo) -> bool`: verdadero solo si el activo está `dentro`.
- `alcance.estado_efectivo(raiz) -> str`: `borrador`, `revisado` o `firmado`.
