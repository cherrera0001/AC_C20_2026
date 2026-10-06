# Resumen ejecutivo — Autoauditoría del laboratorio C4A

**Ejecución:** RUN-20261006T025849Z-d4e4 · 2026-10-06T02:58:49Z · objetivo `C:\Users\herre\OneDrive\Documentos\AC_C20_2026`
**Alcance:** auditoría estática de repositorio (solo lectura). El pentest de red
permanece tras su compuerta de autorización y no forma parte de esta ejecución.

## Estado en una línea

Se analizaron 50 archivos y hay 6
hallazgos ABIERTOS. Controles con incumplimiento: 1; parciales: 1.
Triaje humano: 1 descartado(s) como falso positivo, 0 con riesgo aceptado
(trazados en registro_triaje.md, fuera de este recuento).

## Hallazgos por severidad

| Severidad | N.º |
|---|---|
| ALTO | 1 |
| MEDIO | 2 |
| BAJO | 3 |

## Los cinco de mayor prioridad

- **[ALTO]** Verificación tls desactivada en platform/c4a/detectors/crypto_config.py — `platform/c4a/detectors/crypto_config.py` (prioridad 9.0, ISO-27001, LEY-21719)
- **[MEDIO]** Cifrador débil u obsoleto en platform/c4a/detectors/crypto_config.py — `platform/c4a/detectors/crypto_config.py` (prioridad 7.3, ISO-27001, LEY-21719)
- **[MEDIO]** Algoritmo hash débil para seguridad en platform/tests/test_smoke.py — `platform/tests/test_smoke.py` (prioridad 6.2, ISO-27001, LEY-21719)
- **[BAJO]** Endpoint sobre http:// (texto claro) en platform/c4a/detectors/crypto_config.py — `platform/c4a/detectors/crypto_config.py` (prioridad 4.9, ISO-27001, LEY-21719)
- **[BAJO]** Endpoint sobre http:// (texto claro) en platform/tests/test_smoke.py — `platform/tests/test_smoke.py` (prioridad 4.9, ISO-27001, LEY-21719)

## Qué significa y qué sigue

Cada hallazgo tiene evidencia con hash, un CVSS calculado y su encuadre en
controles y normativas. Los de confianza indirecta están marcados como
*requiere validación*: son observaciones que un segundo rol debe confirmar antes
de tratarlas como incumplimiento. El plan de remediación ordena el trabajo por
prioridad combinada (técnica + obligación legal).
