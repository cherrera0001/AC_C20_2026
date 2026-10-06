# Plan de remediación

Ordenado por prioridad combinada (severidad técnica + obligación legal).

| Prioridad | ID | Hallazgo | Componente | Acción | Responsable sugerido | Plazo sugerido |
|---|---|---|---|---|---|---|
| 9.0 | F-7aaa3301bd | Verificación tls desactivada en platform/c4a/detec | `platform/c4a/detectors/crypto_config.py` | Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles. | Rol Técnico de Investigación | 7 días |
| 7.3 | F-e69a421257 | Cifrador débil u obsoleto en platform/c4a/detector | `platform/c4a/detectors/crypto_config.py` | Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles. | Rol Técnico de Investigación | 30 días |
| 6.2 | F-4839799cf8 | Algoritmo hash débil para seguridad en platform/te | `platform/tests/test_smoke.py` | Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles. | Rol Técnico de Investigación | 30 días |
| 4.9 | F-909427ccba | Endpoint sobre http:// (texto claro) en platform/c | `platform/c4a/detectors/crypto_config.py` | Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles. | Rol Técnico de Investigación | 90 días |
| 4.9 | F-00bb89fb81 | Endpoint sobre http:// (texto claro) en platform/t | `platform/tests/test_smoke.py` | Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles. | Rol Técnico de Investigación | 90 días |