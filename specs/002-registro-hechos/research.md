# Research: S02 — El registro

Fase 0 de `/speckit-plan` (2026-10-21). Sin «NEEDS CLARIFICATION» en el contexto técnico. Decisiones
de diseño con fundamento y alternativas.

## D1. Aportaciones como eventos, entradas derivadas

- **Decision**: el contenido canónico guarda el historial (aportes, correcciones, descartes,
  revisiones). Las entradas se derivan del alcance vigente más ese historial reaplicado en orden.
- **Rationale**: igual que las correcciones de S01. Hace el registro determinista (FR-018), impide
  borrar (FR-013) y permite regenerar sin perder trabajo (FR-015).
- **Alternatives considered**: editar las entradas en el lugar (pierde la historia de «antes no
  constaba», US2 esc. 5).

## D2. Copia de la evidencia y doble huella

- **Decision**: por defecto, `aportar` copia el archivo a `evidence/registro_s02/<id>.<ext>` y calcula
  `sha256_guardado` sobre la copia ya escrita; además registra `sha256_original` del archivo de
  origen. Con `--sin-copia`, la entrada declara «referencia sin copia» y solo hay huella del original.
- **Rationale**: principio III (huella = bytes persistidos; original vs guardado; referencia
  declarada). `evidence/` ya está fuera de git, de modo que la copia no publica crudo.
- **Alternatives considered**: solo referencia (la evidencia puede cambiar sin rastro); copiar dentro
  de `02_evidencia/` (publicaría crudo en git).

## D3. Admisibilidad (FR-007)

- **Decision**, en este orden, y el primer motivo que falle es el rechazo:
  1. Archivo inexistente o ilegible → no se crea nada; error.
  2. Activo: `alcance.consultar("activo", …)` = «fuera» → rechazo con la fila del alcance (o «no
     figura en el alcance»).
  3. Dominio: `alcance.consultar("dominio", …)` = «fuera» → rechazo con la fila.
  4. Corrida de c4a: si se aporta con `--corrida RUN-…`, se lee su objetivo del ledger (`.c4a/runs.jsonl`
     del repositorio); si no es el activo del alcance → rechazo «otro objetivo».
  5. Técnica: `alcance.evaluar_compuerta(raiz, fecha_de_recolección)` distinto de «abierta» → rechazo
     «sin autorización vigente».
  6. Documental: sin origen declarado → rechazo «origen no declarado».
- **Rationale**: reutiliza el contrato de S01 en vez de duplicar reglas. El rechazo se guarda como
  evento para que conste (FR-007, FR-016).
- **Alternatives considered**: aceptar y marcar (dejaría hechos no admisibles en lo que recibe S03).

## D4. Identidad y discrepancias

- **Decision**: id de entrada `short_id("H", activo, dominio, afirmación normalizada)`. Aportar el
  mismo hecho agrega la evidencia. Si las evidencias de una entrada traen resultados distintos, el
  resultado propuesto es «inconcluso»; una corrección del auditor lo fija.
- **Rationale**: aclaración Q2 y Q3.

## D5. Entradas «no consta»

- **Decision**: id `short_id("N", activo, dominio)`. Resultado `no-ejecutado`. Motivo: «compuerta
  cerrada» para dominios técnicos; «requiere solicitud documental» para dominios cuya fila del
  alcance trae la observación de políticas, personas o procesos; «sin evidencia» en otro caso. Cuando
  llega un hecho para ese activo y dominio, la entrada «no consta» pasa a «superada por H-…» y deja de
  contarse, pero no se borra.
- **Rationale**: US1, US2 esc. 5, US3; FR-009, FR-010.

## D6. Cambio del alcance

- **Decision**: el registro guarda la huella del `scope/alcance_s01.json` del que derivó, la de
  `scope/autorizacion.md` y el estado de la compuerta con su fecha de evaluación (así la misma entrada
  produce los mismos bytes, FR-018). Si alguno cambia,
  `abrir` avisa; las entradas cuyo dominio ahora es «fuera» quedan marcadas «fuera del alcance
  vigente» y no se entregan a S03. Si el registro está firmado y el alcance cambió, no se escribe
  (código 4), como en S01.

## D7. Sin crudo en el registro

- **Decision**: el registro guarda tipo, origen, ubicación, fechas, responsable y huellas. Nunca el
  contenido. La afirmación, el origen y los nombres pasan por `alcance.limpiar` (sin direcciones de
  red). La ubicación de la copia es una ruta relativa dentro de `evidence/`.

## D8. Fines de línea

- **Decision**: extender `.gitattributes` a `02_evidencia/registro_s02.*` con `eol=lf`.
- **Rationale**: lección de S01 (con `core.autocrlf=true` la firma dejaría de verificar en un clon).

## D9. Entrega a S03

- **Decision**: `registro.entregar(raiz)` devuelve las entradas vigentes de FR-019 (hechos no
  descartados, dentro del alcance vigente y sin evidencia alterada; «no consta» no superadas) con
  activo, dominio, resultado, marcas, evidencias con huella y `firmado`.

## D10. Pendientes del alcance y restablecimiento

- **Decision**: lo «pendiente» en el alcance admite evidencia con la marca «alcance pendiente»
  (FR-021). Un descarte se revierte con el evento `restablecimiento` (FR-013); nada se borra.
