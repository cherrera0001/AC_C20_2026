# Registro de reproducción

Ejecución RUN-20261006T023239Z-c625 · hash de resultado `2abdbefecf9e1520…`

Cómo reproducir la auditoría completa:

```
python3 -m c4a run --config audit.example.json
python3 -m c4a reproduce --run RUN-20261006T023239Z-c625
```

La reproducción re-ejecuta la auditoría y compara cada hallazgo por id determinista y por hash de evidencia. Estados posibles: reproducido, parcial, no reproducido.

| ID | Estado | Comando de verificación |
|---|---|---|
| F-7aaa3301bd | requires-validation | `grep -niE "(?i)(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*0)" "platform/c4a/detectors/crypto_config.py"` |
| F-def509cf5e | detected | `jq ".dependencies, .devDependencies" "platform/examples/vuln-demo/package.json"` |
| F-e69a421257 | requires-validation | `grep -niE "(?i)\b(DES|RC4|3DES|ECB)\b" "platform/c4a/detectors/crypto_config.py"` |
| F-4839799cf8 | requires-validation | `grep -niE "(?i)\b(md5|sha1)\s*\(" "platform/tests/test_smoke.py"` |
| F-909427ccba | requires-validation | `grep -niE "http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+" "platform/c4a/detectors/crypto_config.py"` |
| F-00bb89fb81 | requires-validation | `grep -niE "http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+" "platform/tests/test_smoke.py"` |