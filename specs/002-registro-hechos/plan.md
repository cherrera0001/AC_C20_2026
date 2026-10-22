# Implementation Plan: S02 — El registro

**Branch**: `002-registro-hechos` (directorio de funcionalidad; sin rama git) | **Date**: 2026-10-21 |
**Spec**: [spec.md](spec.md)

**Input**: especificación de `specs/002-registro-hechos/spec.md`, con la sesión de aclaración del
2026-10-21.

## Summary

S02 deja **el registro**: lo que se puede afirmar sobre el activo del alcance, cada hecho con su
evidencia y su huella, y lo que no consta, en la fase Recopilar. La herramienta **abre** el registro a
partir del alcance de S01 (una entrada «no consta» por activo y dominio dentro o pendiente),
**propone** entradas cuando el auditor aporta una evidencia, **rechaza** la evidencia que no acredita
esta auditoría y deja al auditor **corregir**, **descartar**, **restablecer** y **firmar**. Entrega a S03 los hechos y
los vacíos.

Enfoque técnico: un módulo nuevo `platform/c4a/registro.py` y un subcomando `registro` en
`platform/c4a/cli.py`. Reutiliza de S01 `alcance.consultar`, `alcance.evaluar_compuerta`,
`alcance.cargar`, `alcance.limpiar` y `alcance.serializar`, y de `util` las huellas e identificadores.
Solo librería estándar. Producto en archivos nuevos de `02_evidencia/`; copias de evidencia en
`evidence/registro_s02/` (fuera de git).

## Technical Context

**Language/Version**: Python 3.10+ (igual que `platform/c4a`).

**Primary Dependencies**: ninguna externa; módulo `alcance` de S01.

**Storage**: `02_evidencia/registro_s02.json` (contenido canónico, se firma),
`02_evidencia/registro_s02.md` (vista), `02_evidencia/registro_s02.firma.json` (al firmar). Copias de
evidencia en `evidence/registro_s02/<id>.<ext>`, ignoradas por git (`.gitignore`: `evidence/*`). Ver
[data-model.md](data-model.md).

**Testing**: `unittest` (`python -m unittest discover -s tests`); 78 pruebas en verde el 2026-10-21.
Pruebas nuevas `platform/tests/test_registro_us1..us4.py` y `test_registro_cli.py`, con fixtures
sintéticos rotulados.

**Target Platform**: estación local del auditor (Windows y WSL); sin red.

**Project Type**: CLI y librería dentro de `platform/c4a`.

**Performance Goals**: no críticos; decenas de entradas. Meta humana SC-008 (10 minutos), manual.

**Constraints**: sin red ni pruebas; sin leer `.env`; sin copiar contenido crudo al registro; sin
direcciones de red, comandos, puertos ni credenciales en el producto; determinismo (FR-018); no
sobrescribir `02_evidencia/inventario.json`; fines de línea LF en `02_evidencia/` (la huella firmada
acredita bytes exactos).

**Scale/Scope**: un activo, un registro por ejercicio, un rol humano.

## Constitution Check

*GATE: debe pasar antes de la fase 0 y re-evaluarse después del diseño.*

| Principio | Exigencia aplicable a S02 | Cómo la cumple el diseño | Estado |
|---|---|---|---|
| I. Propone / firma | Ningún rol de la herramienta firma; decisión con quién, cuándo y justificación | `abrir` y `aportar` producen «borrador»; `corregir`, `descartar` y `restablecer` exigen autor y motivo; `firmar` exige firmante y justificación | PASA |
| II. Separación técnico / cumplimiento / aprobación | Resultado técnico en su vocabulario; «sin hallazgos» ≠ «cumple» | Cada entrada usa solo `positivo`, `negativo`, `inconcluso`, `no-ejecutado` y aprobación; cero estados de cumplimiento (FR-011, prueba); el resumen cuenta «no consta», nunca dice «sin hallazgos» | PASA |
| III. Integridad verificable | Hash = bytes persistidos; original vs guardado; referencia sin copia declarada; otra corrida u otro activo no acredita; fixtures rotulados | La evidencia se copia a `evidence/registro_s02/` y se hashea la copia ya escrita; se registra también la huella del original; `--sin-copia` declara la referencia; `verificar` recalcula todo; rechazo de otro activo y de corridas de otro objetivo (ledger) | PASA |
| IV. Controles con marco y versión | No aplica a S02 (no cita controles) | El registro no cita controles ni marcos; eso es S04 | PASA (no aplica) |
| V. Alcance y compuerta | Ninguna prueba sin autorización; sin IP, comandos, puertos ni credenciales | Evidencia técnica solo si la compuerta estaba abierta en su fecha de recolección; la herramienta no ejecuta nada; `alcance.limpiar` filtra direcciones; prueba de búsqueda (SC-005) | PASA |
| VI. Proceso canónico y reutilización | Sin árbol paralelo; reutilizar `platform/c4a`; pruebas en verde | Producto en `02_evidencia/`; crudos en `evidence/`; reutiliza `alcance` y `util`; suite completa antes y después | PASA |
| VII. Trazabilidad ágil | Issues después de `tasks.md`; sin duplicar | Igual que S01: reconciliación en solo lectura y escritura con aprobación | PASA |
| VIII. Legibilidad | Castellano; sin nombrar la institución del curso | Vista `registro_s02.md` en castellano, con evidencia y huella por entrada | PASA |

**Resultado previo a la fase 0**: PASA. Sin violaciones.

**Re-evaluación tras el diseño (fase 1)**: PASA. El registro guarda las aportaciones como eventos
del historial y deriva las entradas reaplicándolos, igual que las correcciones de S01: así es
determinista y nada se borra (I, III, FR-013, FR-018). La admisibilidad de la evidencia técnica se
evalúa con la compuerta de S01 en la fecha de recolección, en solo lectura (V).

## Módulos de `platform/c4a`

| Módulo | Acción | Motivo |
|---|---|---|
| `registro.py` | **Nuevo** | Producto de S02 |
| `cli.py` | Se modifica: subcomando `registro` | Punto de entrada único |
| `alcance.py` | Se reutiliza sin cambios (`cargar`, `consultar`, `evaluar_compuerta`, `limpiar`, `serializar`, `estado_efectivo`) | Contrato con S01 |
| `util.py` | Se reutiliza (`sha256_file`, `short_id`, `now_iso`) | Huellas e identificadores |
| `ledger.py` | Se reutiliza en solo lectura (`Ledger.get`) | Saber sobre qué objetivo corrió una corrida (US4) |
| `evidence.py`, `model.py`, `report.py`, `correlation.py`, demás | No se tocan | Su defecto conocido (III en `evidence.from_command`) no se replica ni se corrige aquí |

## Project Structure

### Documentation (this feature)

```text
specs/002-registro-hechos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli-registro.md
│   └── registro_s02.schema.json
├── checklists/
│   ├── requirements.md
│   └── registro.md
└── tasks.md
```

### Source Code (repository root)

```text
platform/
├── c4a/
│   ├── registro.py      # nuevo
│   └── cli.py           # subcomando `registro`
└── tests/
    ├── registro_fixtures.py
    ├── test_registro_us1.py … test_registro_us4.py
    └── test_registro_cli.py

02_evidencia/
├── inventario.json          # existente, no se toca
├── registro_s02.json        # producto: contenido canónico
├── registro_s02.md          # producto: vista
└── registro_s02.firma.json  # producto: firma (solo tras firmar)

evidence/registro_s02/       # copias de evidencia aportada (fuera de git)
```

**Structure Decision**: se extiende `platform/c4a`; el producto cae en `02_evidencia/`, carpeta de la
fase Recopilar, y la evidencia cruda en `evidence/`, como fija `02_evidencia/README.md`.

## Pendientes declarados

- `.gitattributes` fija LF solo en `scope/`; hay que extenderlo a `02_evidencia/registro_s02.*` para
  que la firma verifique en un clon (tarea de S02).
- Medición humana de SC-008 y recorrido de SC-009.
- Firma del registro por el auditor.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
