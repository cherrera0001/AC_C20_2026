# Research: S04 — La cita

Resuelve las incógnitas del plan. Sin NEEDS CLARIFICATION abiertos.

## D1: qué marcos y catálogos

- **Decision**: ISO/IEC 27001:2022 (`platform/c4a/knowledge/controls_iso27001.json`), NIST CSF 2.0
  (`normativas.json`, entrada `NIST-CSF`) y CIS Controls v8.1 (`controls_cis.json`).
- **Rationale**: son los tres de la constitución (IV). Los catálogos existen en el repositorio.
- **Alternatives**: consultar catálogos en línea (descartado: S04 no toca red); incluir Ley 21.663 y
  21.719 como marcos (descartado: son obligaciones legales, no controles; la cita de obligaciones es de
  la matriz normativa).
- **Limitación declarada**: el catálogo ISO es un subconjunto. El completo es la issue #9.

## D2: fuente de la sugerencia de control

- **Decision**: la correspondencia se propone por coincidencia de términos entre el dominio, el criterio
  y el impacto del riesgo y el campo `terminos` del catálogo (mismo patrón que `controls_cis.json`).
- **Rationale**: determinista (FR-010), sin red, sin modelo de lenguaje; el fundamento se escribe como
  los términos que coincidieron (SC-011).
- **Alternatives**: clasificación por modelo (descartado: no determinista, no reproducible, y fuera de
  la política de red); correspondencia manual total (descartado: no es la función de la herramienta).

## D3: identificador de la cita

- **Decision**: `short_id("C", riesgo_id)`, patrón `^C-[0-9a-f]{10}$`.
- **Rationale**: misma técnica que S02/S03 (FR-020 de S02); estable ante correcciones.
- **Alternatives**: identificador secuencial (descartado: depende del orden, rompe SC-007 si cambian
  entradas).

## D4: huellas y verificación

- **Decision**: firma sobre los bytes guardados de `citas_s04.json` (`util.sha256_file`); `verificar`
  recalcula la del producto, la de la entrega de S03 y la de cada evidencia citada, igual que S02/S03.
- **Rationale**: principio III; reutiliza `registro._evidencias_alteradas` por su forma de datos.
- **Alternatives**: firma con clave criptográfica (descartado: spec clarificación de S01, huella basta).

## D5: estados del identificador y del producto

- **Decision**: `identificador.estado` ∈ {`confirmado`, `pendiente-confirmar`}; `estado_aprobacion` ∈
  {`borrador`, `revisado`}; `firmado` se deriva de una firma válida.
- **Rationale**: FR-004 y el patrón de S02/S03.

## D6: convivencia con `platform/c4a/cita.py` existente

- **Decision**: no se asume ni se borra. La fase de implementación compara ese archivo contra FR-001 a
  FR-016 y decide reescribir o adoptar, dejando la decisión escrita en `tasks.md`.
- **Rationale**: el archivo fue escrito por otra sesión sin spec de plan ni tareas; sobrescribirlo sin
  revisión destruiría trabajo ajeno.
