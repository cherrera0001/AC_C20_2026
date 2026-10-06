# Informe técnico — Autoauditoría del laboratorio C4A

**Ejecución:** RUN-20261006T023239Z-c625 · **Objetivo:** `C:\Users\herre\OneDrive\Documentos\AC_C20_2026`
**Auditor:** Cristóbal Herrera Jara · **Inicio:** 2026-10-06T02:32:39Z · **Fin:** 2026-10-06T02:32:39Z

## Metodología

Auditoría estática de solo lectura en 4 fases (planificar, recopilar, analizar, informar). Detectores deterministas sobre el árbol del repositorio; evidencia con hash SHA-256 y timestamp; CVSS v3.1 calculado del vector; correlación curada a CWE, controles ISO 27001 y normativas declaradas. No se ejecutó nada contra sistemas de red.

## Entorno evaluado

- Lenguajes: Python
- Gestores de paquetes: 3
- Contenedorización: 0 archivo(s)
- CI/CD: 0 workflow(s)
- Archivos .env detectados: 0
- Archivos analizados: 47 (omitidos por tamaño: 0, binarios: 0)

## Hallazgos (por prioridad)

### F-7aaa3301bd — Verificación tls desactivada en platform/c4a/detectors/crypto_config.py
- Severidad **ALTO** · prioridad 9.0 · estado requires-validation · confianza indirect
- Componente `platform/c4a/detectors/crypto_config.py` · detector crypto-config
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N` = **7.4**
- CWE CWE-319, CWE-327 · CVE manual · Controles A.8.24 · Normativas ISO-27001, LEY-21719
- Evidencia: E-b845af1047
- Reproducir: `grep -niE "(?i)(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*0)" "platform/c4a/detectors/crypto_config.py"`
- Se detectó verificación TLS desactivada. Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

### F-def509cf5e — Dependencias npm sin fijar en platform/examples/vuln-demo/package.json
- Severidad **MEDIO** · prioridad 7.7 · estado detected · confianza direct
- Componente `platform/examples/vuln-demo/package.json` · detector dependencies
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L` = **5.6**
- CWE CWE-1104, CWE-1395 · CVE manual · Controles A.8.8 · Normativas ISO-27001, LEY-21663
- Evidencia: E-570bce2325
- Reproducir: `jq ".dependencies, .devDependencies" "platform/examples/vuln-demo/package.json"`
- 1 dependencia(s) usan rangos abiertos (^, ~, *, latest, >=). No implica vulnerabilidad por sí mismo; sí dificulta reproducir builds y rastrear qué versión concreta corre. La correlación con CVE requiere una herramienta de SCA (revisión manual).

### F-e69a421257 — Cifrador débil u obsoleto en platform/c4a/detectors/crypto_config.py
- Severidad **MEDIO** · prioridad 7.3 · estado requires-validation · confianza indirect
- Componente `platform/c4a/detectors/crypto_config.py` · detector crypto-config
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N` = **5.9**
- CWE CWE-327 · CVE manual · Controles A.8.24 · Normativas ISO-27001, LEY-21719
- Evidencia: E-033b8f660a
- Reproducir: `grep -niE "(?i)\b(DES|RC4|3DES|ECB)\b" "platform/c4a/detectors/crypto_config.py"`
- Se detectó cifrador débil u obsoleto. Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

### F-4839799cf8 — Algoritmo hash débil para seguridad en platform/tests/test_smoke.py
- Severidad **MEDIO** · prioridad 6.2 · estado requires-validation · confianza indirect
- Componente `platform/tests/test_smoke.py` · detector crypto-config
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N` = **4.8**
- CWE CWE-327 · CVE manual · Controles A.8.24 · Normativas ISO-27001, LEY-21719
- Evidencia: E-ad59783ce1
- Reproducir: `grep -niE "(?i)\b(md5|sha1)\s*\(" "platform/tests/test_smoke.py"`
- Se detectó algoritmo hash débil para seguridad. Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

### F-909427ccba — Endpoint sobre http:// (texto claro) en platform/c4a/detectors/crypto_config.py
- Severidad **BAJO** · prioridad 4.9 · estado requires-validation · confianza indirect
- Componente `platform/c4a/detectors/crypto_config.py` · detector crypto-config
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N` = **3.7**
- CWE CWE-319 · CVE manual · Controles A.8.24 · Normativas ISO-27001, LEY-21719
- Evidencia: E-b2ca379010
- Reproducir: `grep -niE "http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+" "platform/c4a/detectors/crypto_config.py"`
- Se detectó endpoint sobre http:// (texto claro). Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.

### F-00bb89fb81 — Endpoint sobre http:// (texto claro) en platform/tests/test_smoke.py
- Severidad **BAJO** · prioridad 4.9 · estado requires-validation · confianza indirect
- Componente `platform/tests/test_smoke.py` · detector crypto-config
- CVSS `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N` = **3.7**
- CWE CWE-319 · CVE manual · Controles A.8.24 · Normativas ISO-27001, LEY-21719
- Evidencia: E-5e3a6637ac
- Reproducir: `grep -niE "http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+" "platform/tests/test_smoke.py"`
- Se detectó endpoint sobre http:// (texto claro). Requiere validación: puede ser uso legítimo (p. ej. hash no de seguridad) o un control criptográfico débil real.
