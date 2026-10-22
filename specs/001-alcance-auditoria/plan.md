# Implementation Plan: S01 — El alcance

**Branch**: `001-alcance-auditoria` (directorio de funcionalidad; sin rama git) | **Date**: 2026-10-21 |
**Spec**: [spec.md](spec.md)

**Input**: especificación de `specs/001-alcance-auditoria/spec.md`, con la sesión de aclaración del
2026-10-21.

## Summary

S01 deja **el alcance**: un registro, legible por un tercero, de qué se audita y qué no, derivado de
`scope/alcance.md` y `scope/autorizacion.md`. La herramienta lo **propone** (borrador con fuente por
fila y pendientes agrupados), el auditor lo **corrige** (historial con autor, fecha, valor anterior,
valor nuevo y motivo) y lo **firma** (firmante, fecha y huella SHA-256 de los bytes guardados). El
alcance responde a S02 si un activo o un dominio está «dentro», «fuera» o «pendiente».

Enfoque técnico: un módulo nuevo `platform/c4a/alcance.py` y un subcomando `alcance` en
`platform/c4a/cli.py`, reutilizando `util.sha256_file`, `util.short_id` y `util.now_iso`. Solo
librería estándar. El producto se escribe en archivos nuevos de `scope/`.

## Technical Context

**Language/Version**: Python 3.10+ (el mismo de `platform/c4a`; la estación tiene 3.14).

**Primary Dependencies**: ninguna externa; solo librería estándar (decisión vigente de
`platform/README.md`: «sin dependencias externas»).

**Storage**: archivos en `scope/`: `alcance_s01.json` (contenido canónico), `alcance_s01.md` (vista
legible) y `alcance_s01.firma.json` (registro de firma). Ver [data-model.md](data-model.md).

**Testing**: `unittest` de la librería estándar, como la suite existente (`platform/tests/`, 24
pruebas en verde el 2026-10-21, `python -m unittest discover -s tests`). Prueba nueva:
`platform/tests/test_alcance.py`, con insumos sintéticos rotulados como tales.

**Target Platform**: estación local Windows del auditor y WSL Ubuntu 24.04; sin red.

**Project Type**: CLI y librería dentro de `platform/c4a`.

**Performance Goals**: no críticos; dos documentos markdown de pocos KB. Meta humana SC-003 (menos de
10 minutos para identificar pendientes), verificada de forma manual.

**Constraints**: sin red; sin leer `.env`; sin escribir en `scope/alcance.md` ni en
`scope/autorizacion.md`; ninguna dirección de red, puerto, comando ni credencial en el producto
(FR-004); salida determinista (FR-018).

**Scale/Scope**: un único activo, un alcance por ejercicio, un solo rol humano (el auditor).

## Constitution Check

*GATE: debe pasar antes de la fase 0 y re-evaluarse después del diseño.*

| Principio | Exigencia aplicable a S01 | Cómo la cumple el diseño | Estado |
|---|---|---|---|
| I. La herramienta propone, el auditor firma | Ningún rol de la herramienta firma; toda decisión registra quién, cuándo y por qué | `proponer` solo produce «borrador»; `corregir` y `revisar` exigen autor y motivo; `firmar` es la única vía a «firmado» y requiere el nombre del firmante | PASA |
| II. Separación técnico / cumplimiento / aprobación | Tres dimensiones independientes; «sin hallazgos» no implica «cumple» | El alcance solo usa la dimensión de aprobación (`borrador`, `revisado`, `firmado`); no contiene estados de cumplimiento ni resultados técnicos (FR-015, verificado por prueba) | PASA |
| III. Integridad verificable | Hash publicado = bytes persistidos; alteración detectada; verificación independiente | La huella se calcula con `util.sha256_file` sobre el archivo ya escrito; `verificar` recalcula sin regenerar; prueba de un byte alterado (SC-006). No se usa `evidence.from_command` (defecto conocido del principio III, fuera de S01) | PASA |
| IV. Controles con marco, versión e identificador | Marco mencionado ≠ implementado; leyes con fuente, fecha, artículo y fundamento, si no «VALIDAR» | Cada marco lleva nombre, versión, estado en la herramienta y cobertura declarada (ISO: catálogo parcial; NIST CSF 2.0 y CIS v8.1: mencionados). Las leyes entran como obligación candidata en «VALIDAR» | PASA |
| V. Alcance y compuerta | Un único activo; ninguna prueba sin autorización firmada, completa y vigente; sin IP, comandos, puertos ni credenciales en spec, plan, tareas e issues | Fila de activo único; la compuerta se evalúa en solo lectura y no se abre; el producto filtra direcciones de red y se prueba con búsqueda (SC-005). S01 no ejecuta nada contra el objetivo | PASA |
| VI. Proceso canónico y reutilización | Sin árbol paralelo; reutilizar `platform/c4a`; pruebas existentes en verde | Producto en `scope/` (fase Planificar); módulo dentro de `platform/c4a`; reutiliza `util`; la suite existente se corre antes y después | PASA |
| VII. Trazabilidad ágil sin duplicar | Issues después de `tasks.md`; sin duplicar backlog; tallas relativas | El tablero se reconcilia contra `tasks.md` en solo lectura, con aprobación expresa antes de escribir | PASA |
| VIII. Legibilidad | Castellano; entendible sin haber estado en la sala; sin nombrar la institución del curso | Vista `alcance_s01.md` en castellano con fuente por fila; nombres de módulo y campos en castellano | PASA |

**Resultado previo a la fase 0**: PASA, sin violaciones. Sin entradas en *Complexity Tracking*.

**Re-evaluación tras el diseño (fase 1)**: PASA. El diseño de [data-model.md](data-model.md) separa
el contenido firmado (`alcance_s01.json`) del registro de firma (`alcance_s01.firma.json`), de modo
que la huella firmada acredita exactamente los bytes del contenido persistido (III). La evaluación de
la ventana depende de la fecha y por eso no forma parte del contenido firmado: se calcula al consultar
y se muestra en la vista (V, FR-008).

## Módulos de `platform/c4a`

| Módulo | Acción en S01 | Motivo |
|---|---|---|
| `util.py` | Se reutiliza sin cambios (`sha256_file`, `short_id`, `now_iso`) | Huellas e identificadores deterministas ya probados |
| `cli.py` | Se modifica: se agrega el subcomando `alcance` | Punto de entrada único de la herramienta |
| `alcance.py` | **Nuevo**: derivación, correcciones, firma, verificación, consulta y vista | Producto de S01 |
| `knowledge/controls_iso27001.json` | Solo lectura | Declarar la cobertura parcial del catálogo ISO |
| `scope.py` | No se toca | Es el gestor de alcance del análisis estático de repositorios (otra cosa) |
| `model.py`, `ledger.py`, `evidence.py`, `report.py`, `sarif.py`, `htmlmap.py`, `triage.py`, `correlation.py` | No se tocan | S01 no produce evidencia, hallazgos ni informes; sus defectos conocidos (II en `correlation.py`, III en `evidence.py`) quedan para los sprints que los usan |

## Project Structure

### Documentation (this feature)

```text
specs/001-alcance-auditoria/
├── spec.md
├── plan.md              # este archivo
├── research.md          # fase 0
├── data-model.md        # fase 1
├── quickstart.md        # fase 1
├── contracts/
│   ├── cli-alcance.md           # contrato del subcomando
│   └── alcance_s01.schema.json  # esquema del contenido canónico
├── checklists/
│   ├── requirements.md  # calidad de redacción (aprobado por el dueño)
│   └── alcance.md       # compuerta humana de /speckit-checklist
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
platform/
├── c4a/
│   ├── alcance.py       # nuevo
│   └── cli.py           # subcomando `alcance`
└── tests/
    └── test_alcance.py  # nuevo; insumos sintéticos rotulados

scope/
├── alcance.md               # insumo, solo lectura para la herramienta
├── autorizacion.md          # insumo, solo lectura para la herramienta
├── alcance_s01.json         # producto: contenido canónico
├── alcance_s01.md           # producto: vista legible
└── alcance_s01.firma.json   # producto: registro de firma (solo tras firmar)
```

**Structure Decision**: se extiende el proyecto existente `platform/c4a`; no se abre un árbol nuevo.
El producto cae en `scope/`, carpeta de la fase Planificar.

## Pendientes declarados

- Medición humana de SC-003 (minutos): la registra el auditor; la herramienta no la automatiza.
- Validación jurídica de las obligaciones candidatas: fuera de S01; quedan en «VALIDAR».
- Firma de `scope/autorizacion.md` (firmante, facultad, origen del auditor, ventana, contacto):
  acción humana.
- D10 de [research.md](research.md): firmar con pendientes está permitido (confirmado por el dueño el
  2026-10-21).

## Complexity Tracking

Sin violaciones de la constitución que justificar.
