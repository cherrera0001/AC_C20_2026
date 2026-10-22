# Quickstart: validar S01 — El alcance

Guía para comprobar de punta a punta que el alcance funciona. Todo es local, sin red y sin leer
`.env`. Contrato de los subcomandos: [contracts/cli-alcance.md](contracts/cli-alcance.md). Forma de
los archivos: [data-model.md](data-model.md).

## Requisitos

- Python 3.10 o superior. Sin dependencias externas.
- Trabajar desde `platform/`.

## 1. Pruebas automáticas

```text
python -m unittest discover -s tests
```

Esperado: la suite existente (24 pruebas) y `test_alcance.py` en verde. `test_alcance.py` usa insumos
sintéticos, rotulados como tales, y cubre SC-001, SC-002, SC-004, SC-005, SC-006, SC-007 y la parte
automática de SC-003 y SC-008.

## 2. Proponer el alcance del ejercicio

```text
python -m c4a alcance proponer --raiz ..
```

Esperado: se crean `scope/alcance_s01.json` y `scope/alcance_s01.md`. La vista tiene una sola sección
«Pendientes» con su conteo. `scope/alcance.md` y `scope/autorizacion.md` no cambian (comparar su
huella antes y después).

## 3. Compuerta

```text
python -m c4a alcance compuerta --raiz ..
```

Esperado mientras `scope/autorizacion.md` no esté firmada: «cerrada», con los motivos (no firmada,
incompleta, ventana no informada).

## 4. Corregir, revisar y firmar

```text
python -m c4a alcance corregir --raiz .. --fila <ID> --campo decision --valor excluido --motivo "<motivo>" --autor "<auditor>"
python -m c4a alcance firmar   --raiz .. --firmante "<auditor>"
python -m c4a alcance verificar --raiz ..
```

Esperado: después de corregir, estado «revisado»; después de firmar, `verificar` responde «firmado».
Una corrección posterior devuelve el estado a «revisado» y `verificar` responde «sin firma».

## 5. Consulta de S02

```text
python -m c4a alcance consultar --raiz .. --tipo activo --valor "<otro activo>"
```

Esperado: «fuera». Un dominio pendiente responde «pendiente», no «dentro».

## 6. Verificación manual

- SC-003: el auditor abre `scope/alcance_s01.md`, cronometra cuánto tarda en identificar todos los
  pendientes y registra el tiempo en el checklist humano.
- SC-008: un tercero recorre tres filas al azar hasta la sección citada del insumo.
- SC-005: buscar en `scope/alcance_s01.*` direcciones de red, puertos, comandos y credenciales:
  cero coincidencias.
