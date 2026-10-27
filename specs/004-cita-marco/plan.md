# Plan: S04 — La cita

**Input**: especificación en `specs/004-cita-marco/spec.md`.

**Constitution Check**: principios I (la herramienta propone, el auditor firma), II (una cita no
dictamina cumplimiento), III (huellas sobre los bytes guardados; verificación independiente), IV (sin
identificadores de control inventados; marcos solo de la constitución; «pendiente de confirmar» cuando
no consta), V (nada de red, nada de `.env`, sin direcciones ni comandos en spec, plan, tareas ni
producto) y VI (se reutiliza `platform/c4a`; las pruebas existentes siguen pasando).

**Desviación de compuerta declarada**: la constitución (VI) ordena no especificar un sprint hasta que el
anterior converja. S03 no converge: su spec y tareas existen, pero su código está en curso en otra
sesión y no se ha verificado. El dueño ordenó avanzar a S04 («si está en proceso la S03, pasa a la S04»,
2026-10-26). La desviación queda registrada aquí, en la spec y en `tasks.md`.

## Estado del repositorio que este plan reconcilia

Lo que ya existe y **no se toca** en esta épica (escrito por otra sesión, sin verificar):

| Archivo | Estado observado (2026-10-26, 23:00) | Tratamiento en S04 |
|---|---|---|
| `platform/c4a/enunciado.py` | Existe (S03), sin commit, sin converger | S04 lo consume solo a través de `enunciado.entregar(raiz)`. Si la API cambia, S04 se adapta; no se edita |
| `platform/c4a/cita.py` | Existe (30 KB, 22:29), sin spec de plan ni tareas | **No se usa como base**. Se trata como borrador ajeno: se reconcilia en la fase de implementación (ver «Reconciliación») |
| `platform/tests/test_cita.py`, `cita_fixtures.py` | Existen | Igual que `cita.py`: se revisan contra la spec antes de aceptarlos |
| `platform/c4a/knowledge/controls_cis.json` | CIS v8.1, 18 controles, fuente declarada | Se usa como base de CIS. La fuente es declarada, no verificada en línea |
| `platform/c4a/knowledge/controls_iso27001.json` | Subconjunto del Anexo A | Se usa tal cual; el catálogo completo es la issue #9 (fuera de S04) |
| `platform/c4a/knowledge/normativas.json` | Contiene NIST CSF 2.0 entre otros | Se usa para NIST CSF 2.0 |

## Summary técnico

Nuevo módulo `platform/c4a/cita.py`. El archivo existente es de otra sesión (**reconciliar**). La fase
de implementación decide entre (a) reescribirlo desde la spec o (b) adoptarlo y ajustarlo a FR-001 a
FR-016. Este plan fija el contrato, no la implementación.

El producto vive en `03_hallazgos/` (carpeta de la fase Analizar, `docs/AUDIT_PROMPT.md`):
`citas_s04.json` (canónico, lo que se firma), `citas_s04.firma.json`, `citas_s04.md` y una ficha
`cita-<id>.md` por cita. Misma forma que S01 a S03: la herramienta propone (`abrir`), el auditor corrige
(`corregir`, `descartar`, `restablecer`), revisa (`revisar`) y firma (`firmar`); `verificar` recalcula
huellas; `entregar` deja la lista para S05.

## Decisión 1: el producto anterior es obligatorio

Si falta la entrega de S03 (`enunciado.entregar` no la encuentra o `03_hallazgos/enunciados_s03.json`
no existe), `abrir` termina en código 2 y no escribe nada (FR-001). Sin riesgos no hay cita. Mismo
criterio que S03 con el registro de S02.

## Decisión 2: identidad de la cita

Una cita por riesgo vigente de la entrega, con identificador derivado del riesgo: `short_id("C", riesgo_id)`
(`C-` + 10 hex). Corregir el texto no cambia el identificador (FR-003, mismo criterio que FR-020 de S02).

## Decisión 3: marcos y estado del identificador

Solo tres marcos, los de la constitución (IV): ISO/IEC 27001:2022, NIST CSF 2.0 y CIS Controls v8.1
(v8 solo si la v8.1 no se obtiene, y se declara). La herramienta propone un identificador solo si consta
en su base (catálogo de `platform/c4a/knowledge/`); si no consta, queda `pendiente-confirmar`. El
auditor puede añadir un marco fuera de los tres, que se registra como su aporte con estado
`pendiente-confirmar` (spec, clarificaciones). Ningún identificador se inventa.

## Decisión 4: propuesta explicada, no dictamen

La correspondencia principal se propone desde el dominio, el criterio y el impacto del riesgo (FR-005).
Cada correspondencia lleva un fundamento no vacío (SC-011). Ninguna propuesta contiene estados de
cumplimiento ni conclusiones sobre controles (FR-006). Las correspondencias adicionales son del auditor,
con motivo.

## Decisión 5: consistencia con S03

El producto guarda la huella de la entrega de S03 (`entrega_sha256`). `abrir` compara con la entrega
actual; si cambió, lo señala (FR-014), y si el producto está firmado rechaza con código 4. Las marcas
del riesgo de origen (descartado, evidencia alterada, hecho no vigente) se heredan y un riesgo marcado
no genera cita vigente (spec, evaluación de coherencia). Los vacíos heredados viajan como contexto, sin
cita.

## Decisión 6: dónde cae y qué no toca

Solo archivos nuevos en `03_hallazgos/` (FR-011): `citas_s04.json`, `.firma.json`, `.md` y
`cita-*.md`. No se tocan `enunciados_s03.*`, `README.md` ni `matriz_cumplimiento.csv`. SC-010 se
demuestra con huellas antes y después.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Inventar un identificador de control | Solo catálogo existente; sin base → `pendiente-confirmar`; prueba por cada identificador (SC-002) |
| Leer una correspondencia como cumplimiento | Fundamento obligatorio; vista con nota fija de «sugerencia, no dictamen» (FR-006, SC-003) |
| Base de ISO incompleta | Declarado en la vista; catálogo completo es la issue #9, fuera de S04 |
| Código de otra sesión (`cita.py`) en conflicto | Reconciliar contra la spec antes de aceptar; no sobrescribir sin revisión |
| S03 todavía no converge | Desviación declarada; S04 depende solo de la API `entregar`, que S03 ya publica en su spec |

## Contratos

- `contracts/cli-cita.md`: subcomandos, argumentos y códigos de salida.
- `contracts/citas_s04.schema.json`: esquema del JSON canónico.

## Verificación de constitución

- I: el auditor firma; ninguna acción de la herramienta cierra una cita. ✔
- II: sin estados de cumplimiento; la cita es sugerencia explicada. ✔
- III: huellas sobre bytes guardados; verificación independiente en `verificar`. ✔
- IV: marcos limitados a la constitución; identificadores solo de catálogo; «pendiente de confirmar». ✔
- V: sin red, sin `.env`, sin IPs, comandos ni puertos en el plan ni en el producto. ✔
- VI: reutiliza `enunciado.entregar`, `alcance.serializar`, `alcance.limpiar`, `util.short_id`. Desviación de
  orden declarada arriba. ✔ con desviación

## Reconciliación pendiente (fase de implementación)

1. Decidir sobre `platform/c4a/cita.py` existente: reescribir desde el contrato o adoptar y ajustar.
2. Confirmar la API real de `enunciado.entregar` cuando S03 la estabilice.
3. Comparar `test_cita.py` con FR-001 a FR-016 y SC-001 a SC-013 antes de conservarlo.
