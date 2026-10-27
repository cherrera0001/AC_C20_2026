# Quickstart: S04 — La cita

Validación de punta a punta con fixtures sintéticos rotulados como tales, y luego con el producto real.
Ningún paso toca la red ni el objetivo.

## 1. Línea base

Desde `platform/`:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Debe quedar en verde antes de tocar nada. Si falla, detenerse y reportar.

## 2. Sin entrega de S03

Con un repositorio sin `03_hallazgos/enunciados_s03.json`, `cita abrir --raiz <raiz>` termina con código 2 y
no crea archivos (FR-001; ver `contracts/cli-cita.md`).

## 3. Abrir con una entrega sintética

Con `tests/cita_fixtures.py` (entrega de S03 sintética, rotulada «FIXTURE SINTÉTICO»):

```text
cita abrir --raiz <raiz_fixture> --fecha 2026-10-26
```

Esperado: una cita por riesgo vigente; `citas_s04.json`, `.md` y una ficha por cita; cada cita con
`marco`, `fundamento` no vacío e `identificador.estado` (`confirmado` solo si el control consta en el
catálogo). Repetir el comando produce bytes idénticos (SC-007).

## 4. Corregir, revisar y firmar

```text
cita corregir --raiz <raiz_fixture> --cita <C-…> --campo control --valor <id> --motivo "..." --autor "..."
cita revisar  --raiz <raiz_fixture> --autor "..." --motivo "..."
cita firmar   --raiz <raiz_fixture> --firmante "..." --motivo "..."
```

Esperado: la corrección queda en el historial; la firma existe solo tras `revisar`; cambiar algo después
elimina la firma (`firma_anulada`).

## 5. Verificar integridad

```text
cita verificar --raiz <raiz_fixture>
```

Alterar un byte de `citas_s04.json` o de una copia de evidencia citada debe producir código 3 y la marca
correspondiente (SC-004, SC-005).

## 6. Entregar a S05

```text
cita entregar --raiz <raiz_fixture> --json
```

Esperado: solo citas vigentes (no descartadas, riesgo vigente, sin evidencia alterada), con su estado de
identificador y huellas; vacíos heredados; estado de firma (SC-009).

## 7. Producto real

Con el registro y el enunciado reales del repositorio, `cita abrir` debe generar los archivos en
`03_hallazgos/` sin tocar `enunciados_s03.*`, `README.md` ni `matriz_cumplimiento.csv` (SC-010). Registrar en
`tasks.md` → Notes el conteo de citas, pendientes y marcos. El auditor completa el recorrido de SC-008 y
SC-012 (acción humana).
