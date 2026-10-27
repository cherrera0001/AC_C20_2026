# Plan: S03 — El enunciado

**Input**: especificación en `specs/003-enunciado-riesgo/spec.md`.

**Constitution Check**: principios I (la herramienta propone, el auditor firma), II (un enunciado no
dictamina; hecho negativo ≠ cumple), III (huellas sobre los bytes guardados; verificación
independiente), IV (sin identificadores de controles inventados: la cita es de S04), V (nada de red,
nada de `.env`, sin direcciones ni comandos en specs ni en el producto) y VI (se reutiliza
`platform/c4a`, las pruebas existentes siguen pasando).

## Summary técnico

Nuevo módulo `platform/c4a/enunciado.py` que consume `registro.entregar(raiz)` y produce, en
`03_hallazgos/`, el enunciado de riesgo: JSON canónico determinista, vista legible, una ficha por
enunciado y el archivo de firma. Misma forma que S01/S02: la herramienta propone (`abrir`), el
auditor corrige (`corregir`, `descartar`, `restablecer`), revisa (`revisar`) y firma (`firmar`);
`verificar` recalcula huellas; `entregar` deja la lista para S04.

## Decisión 1: el producto anterior es obligatorio

S02 tenía un mínimo de referencia (`scope/alcance.md`) porque podía derivar filas sin escribir en
`scope/`. S03 no tiene equivalente honesto: sin hechos no hay riesgo que enunciar. Si falta
`02_evidencia/registro_s02.json`, `abrir` termina en código 2 y no escribe nada (FR-001). La
simetría con S01 (que exige `scope/alcance.md`) pesa más que la simetría con el mínimo de S02.

## Decisión 2: identidad y estabilidad del identificador

Un enunciado por hecho vigente; el identificador se deriva del identificador del hecho
(`short_id("R", hecho_id)`), no del texto. Corregir la redacción no cambia el identificador
(mismo criterio que S02, FR-020). Si una entrega externa repitiera un hecho (rompiendo FR-020 de
S02), `abrir` toma el primero y agrega un aviso.

## Decisión 3: qué propone la herramienta y qué completa el auditor

La herramienta propone: condición (desde la afirmación del hecho), consecuencia (según el
resultado técnico), criterio (texto cualitativo sin identificadores: la cita del marco es de S04,
principio IV), impacto (vacío) y «lo que falta» (derivado de las marcas y del resultado). Firmar
exige criterio e impacto no vacíos en cada enunciado vigente (FR-008): el juicio de criterio e
impacto es humano por diseño. Los hechos negativos llevan nota fija de no-cumplimiento (FR-006).

## Decisión 4: fichas por enunciado

Cada enunciado también se escribe como `03_hallazgos/enunciado-<id>.md` (FR-012): es la ficha que
`docs/AUDIT_PROMPT.md` pide para la fase Analizar, legible sin la herramienta, sin extractos de
evidencia. La vista agregada `enunciados_s03.md` sigue existiendo para el recorrido rápido
(SC-008).

## Decisión 5: consistencia con el registro

El JSON guarda la huella de `registro_s02.json` y la de la entrega (`entrega_sha256`). `verificar`
recalcula ambas y las de cada evidencia citada; informa «evidencia alterada» y «hecho no vigente»
por enunciado (FR-009). Las acciones del auditor exigen que nada haya cambiado (`_cargar_vigente`,
FR-015); `abrir` con el producto firmado y el registro cambiado rechaza con código 4 (FR-014),
igual que S02.

## Decisión 6: dónde cae y qué no toca

Solo archivos nuevos en `03_hallazgos/` (FR-011): `enunciados_s03.json`, `.md`, `.firma.json` y
`enunciado-*.md`. No se tocan `README.md` ni `matriz_cumplimiento.csv` (producto del ciclo previo
de la plataforma); se demuestra con huellas antes/después (SC-010).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Inventar criterio o encuadre normativo | S03 no cita controles; criterio cualitativo y la cita es de S04 (principio IV) |
| Leer un negativo como cumplimiento | Nota fija en el enunciado y frase en la vista (FR-006); prueba SC-011 |
| Huella que no verifica los bytes guardados | Mismo patrón que S02: firma sobre los bytes ya persistidos (principio III) |
| Escritura encubierta sobre el producto firmado | `_guardar` único punto de escritura anula la firma; `abrir` firmado + cambio = código 4 |
| Textos del auditor con cumplimiento/comandos | Mismo filtro `_texto_libre` que S02 (FR-016) |

## Contratos

- `contracts/cli-enunciado.md`: subcomandos, argumentos y códigos de salida.
- `contracts/enunciados_s03.schema.json`: esquema del JSON canónico.

## Verificación de constitución

- I: firmar exige criterio/impacto humanos y justificación; ningún rol cierra el riesgo. ✔
- II: sin estados de cumplimiento; negativo con nota fija. ✔
- III: huellas sobre bytes guardados; verificación independiente en `verificar`. ✔
- IV: sin identificadores de controles. ✔
- V: sin red, sin `.env`, sin IPs/comandos/puertos en spec, plan, tareas ni issues. ✔
- VI: reutiliza `alcance.serializar`, `alcance.limpiar`, `util.short_id`, `registro.entregar`. ✔
