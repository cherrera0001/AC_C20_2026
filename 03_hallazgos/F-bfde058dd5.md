# F-bfde058dd5 — Endpoint sobre http:// (texto claro) en platform/tests/test_triage.py

- **Tipo:** technical
- **Severidad:** BAJO  ·  **Prioridad combinada:** 4.9
- **Estado:** requires-validation  ·  **Confianza:** indirect
- **Probabilidad:** media  ·  **Impacto:** medio
- **Componente:** `platform/tests/test_triage.py`
- **Detector:** crypto-config  ·  **Detectado:** 2026-10-06T03:22:56Z
- **Roles:** Rol Técnico de Investigación

## Descripción
Se detectó endpoint sobre http:// (texto claro). Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

## CVSS v3.1
- Vector: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N`
- Puntaje base: **3.7** (LOW)
- Fuente: detector-baseline — Vector base por clase de problema; revisar y ajustar al contexto real.

## Clasificación
- **CWE:** CWE-319 (Cleartext Transmission of Sensitive Information)
- **CVE:** sin correlación automática — revisión manual
- **Controles ISO:** A.8.24
- **Normativas:** ISO-27001, LEY-21719
- **Impacto de cumplimiento:** A.8.24 uso de criptografía; protección de datos en tránsito.

## Evidencia
- `E-4f6f9a6531` — platform/tests/test_triage.py:13 · sha256 `76ff923860726c8d…` · 1 coincidencia(s): endpoint sobre http:// (texto claro)

  ```
  L13: "app.py": "url = 'http://api.example.com/v1'\n",
  ```

## Reproducción
- Método: re-ejecutar la auditoría y comparar por id y hash de evidencia
- Comando: `grep -niE "http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+" "platform/tests/test_triage.py"`
- Resultado esperado: líneas coincidentes
- Entorno: Python 3.10+ (solo librería estándar); acceso de lectura al objetivo

## Remediación
Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles.

**Recomendaciones:** Centralizar la política criptográfica y revisar con un linter de seguridad.

**Notas:** Falso positivo posible: MD5/SHA1 fuera de contexto de seguridad, o http a servicios internos. Pendiente de validación técnica por un segundo rol.
