# F-7aaa3301bd — Verificación tls desactivada en platform/c4a/detectors/crypto_config.py

- **Tipo:** technical
- **Severidad:** ALTO  ·  **Prioridad combinada:** 9.0
- **Estado:** requires-validation  ·  **Confianza:** indirect
- **Probabilidad:** media  ·  **Impacto:** alto
- **Componente:** `platform/c4a/detectors/crypto_config.py`
- **Detector:** crypto-config  ·  **Detectado:** 2026-10-06T02:21:33Z
- **Roles:** Rol Técnico de Investigación

## Descripción
Se detectó verificación TLS desactivada. Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

## CVSS v3.1
- Vector: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`
- Puntaje base: **7.4** (HIGH)
- Fuente: detector-baseline — Vector base por clase de problema; revisar y ajustar al contexto real.

## Clasificación
- **CWE:** CWE-319 (Cleartext Transmission of Sensitive Information), CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)
- **CVE:** sin correlación automática — revisión manual
- **Controles ISO:** A.8.24
- **Normativas:** ISO-27001, LEY-21719
- **Impacto de cumplimiento:** A.8.24 uso de criptografía; protección de datos en tránsito.

## Evidencia
- `E-09236bfa06` — platform/c4a/detectors/crypto_config.py:4 · sha256 `fb3988de1a9843fe…` · 1 coincidencia(s): verificación TLS desactivada

  ```
  L4: desactivada (rejectUnauthorized:false, verify=False, InsecureSkipVerify) y
  ```

## Reproducción
- Método: re-ejecutar la auditoría y comparar por id y hash de evidencia
- Comando: `grep -niE "(?i)(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*0)" "platform/c4a/detectors/crypto_config.py"`
- Resultado esperado: líneas coincidentes
- Entorno: Python 3.10+ (solo librería estándar); acceso de lectura al objetivo

## Remediación
Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles.

**Recomendaciones:** Centralizar la política criptográfica y revisar con un linter de seguridad.

**Notas:** Falso positivo posible: MD5/SHA1 fuera de contexto de seguridad, o http a servicios internos. Pendiente de validación técnica por un segundo rol.
