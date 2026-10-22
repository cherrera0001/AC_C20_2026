# Research: S01 — El alcance

Fase 0 de `/speckit-plan` (2026-10-21). El contexto técnico no dejó ningún «NEEDS CLARIFICATION». Este
documento registra las decisiones de diseño, con su fundamento y las alternativas descartadas. Lo que
no consta en el repositorio queda «pendiente de confirmar» o «VALIDAR».

## D1. Mecanismo de firma

- **Decision**: la firma es un registro aparte (`scope/alcance_s01.firma.json`) con firmante, fecha y
  la huella SHA-256 de los bytes de `scope/alcance_s01.json`, calculada con `util.sha256_file` sobre
  el archivo ya escrito.
- **Rationale**: es la opción A de la aclaración. Si la firma viviera dentro del mismo archivo
  firmado, la huella no podría cubrir sus propios bytes. Separar contenido y firma permite que la
  huella publicada corresponda exactamente a los bytes persistidos (principio III) y que cualquier
  cambio la anule.
- **Alternatives considered**: firma con clave GPG (descartada en la aclaración); huella del texto
  antes de escribirlo (repite el defecto de `evidence.from_command`); firma embebida con la huella del
  contenido «sin la firma» (exige una canonicalización que un tercero no verifica con `sha256sum`).

## D2. Formato del producto

- **Decision**: `alcance_s01.json` es el contenido canónico, serializado de forma determinista (claves
  ordenadas, sangría de 2, UTF-8, salto de línea final). `alcance_s01.md` es una vista derivada para
  personas; no se firma.
- **Rationale**: JSON con la librería estándar mantiene la decisión «sin dependencias externas» y lo
  puede leer S02. La vista en markdown cumple FR-017 (un tercero la lee sin la herramienta).
- **Alternatives considered**: solo markdown (frágil de releer por máquina); YAML (agrega una
  dependencia); CSV (no representa bien el historial).

## D3. Determinismo (FR-018)

- **Decision**: el contenido canónico no lleva hora de generación. Los identificadores de fila se
  derivan con `util.short_id("A", tipo, clave)`. Las correcciones guardan su propia fecha y se
  reaplican tal cual.
- **Rationale**: con los mismos insumos y las mismas correcciones, los bytes coinciden. Un alcance
  firmado sigue firmado si se vuelve a proponer sin cambios en los insumos.
- **Alternatives considered**: marca de tiempo por generación (rompe la firma en cada corrida).

## D4. Compuerta de autorización

- **Decision**: el contenido canónico guarda lo **declarado** en `scope/autorizacion.md` (encabezado de
  estado, campos que constan y campos por completar, inicio y fin de la ventana). El **resultado** de
  la compuerta (abierta/cerrada y su motivo) se calcula con una fecha de referencia al consultar y se
  muestra en la vista. La herramienta nunca escribe en la autorización.
- **Rationale**: «vencida» depende del día. Si el resultado entrara en el contenido firmado, el paso
  del tiempo anularía la firma del alcance, que es independiente de la compuerta (aclaración Q2).
- **Alternatives considered**: guardar el resultado en el JSON (firma inestable).

## D5. Lectura de los insumos

- **Decision**: lector dirigido a la estructura real de `scope/alcance.md` (secciones `## N.`, tablas
  `| Campo | Valor |`, listas) y de `scope/autorizacion.md`. Lo que el lector no reconoce no se
  inventa: genera una fila «pendiente de confirmar» con la observación.
- **Rationale**: los dos documentos son el contrato confirmado (`docs/LINEA_ORIGEN.md`); un lector general
  de markdown sería más código sin más garantía.
- **Alternatives considered**: pedir al auditor un formulario nuevo (rompe la trazabilidad al origen).

## D6. Regla del motivo

- **Decision**: una fila de tipo dominio o exclusión queda «pendiente de confirmar» si el insumo no da
  su motivo en el mismo ítem; se conserva lo declarado (`declarado: incluido|excluido`) para que el
  auditor confirme con una corrección.
- **Rationale**: FR-007 exige motivo; el título de la sección no es un motivo. La decisión es del
  auditor (principio I).
- **Alternatives considered**: tomar el título de la sección como motivo (sería una conclusión
  automática).

## D7. Marcos de referencia y cobertura

- **Decision**: ISO/IEC 27001:2022 figura «implementado parcialmente», con la cobertura que declara el
  catálogo `platform/c4a/knowledge/controls_iso27001.json` (cantidad de controles del Anexo A
  presentes, contada al proponer). NIST CSF 2.0 figura «mencionado» (el catálogo solo trae las seis
  funciones). CIS Controls v8.1 figura «mencionado» (sin catálogo). NIST CSF 2.0 y CIS v8.1 no están
  declarados en `scope/alcance.md`, así que su decisión queda «pendiente de confirmar».
- **Rationale**: principio IV, ser seleccionable no acredita cobertura.

## D8. Obligaciones legales

- **Decision**: Ley 21.663, Ley 21.719 y Ley 21.459 entran como obligación candidata en «VALIDAR»:
  los insumos no traen fuente oficial, fecha de consulta ni artículo. El estado anotado en
  `scope/alcance.md` §3 («sep-2026») se conserva como antecedente histórico, no como vigencia
  verificada. La aplicabilidad de la Ley 21.663 depende de la clasificación OIV (§9), que no consta.
- **Rationale**: principio IV y supuesto de la spec; S01 no hace validación jurídica.

## D9. Sin datos de red en el producto

- **Decision**: todo valor que pase del insumo al producto se filtra con un patrón de direcciones IPv4
  y de rango; si coincide, se reemplaza por la remisión a `scope/autorizacion.md`. Una prueba busca
  direcciones, puertos, comandos y credenciales en el producto (SC-005).
- **Rationale**: FR-004 y principio V. `scope/alcance.md` §4 sí contiene el detalle de red.

## D10. Firma con pendientes

- **Decision**: se puede firmar un alcance «revisado» aunque tenga pendientes; el registro de firma
  guarda cuántos había y la vista lo dice.
- **Rationale**: la spec permite entregar a S02 un alcance explícitamente incompleto; impedirlo no
  está pedido. Confirmado por el dueño el 2026-10-21 (compuerta F).
