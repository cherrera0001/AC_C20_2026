---
name: "auditoria-php"
description: "Análisis estático defensivo de código PHP y Python propio: ejecución remota (php2shell/python2shell), deserialización insegura, carga de archivos, inclusión dinámica y ofuscación tipo webshell. Sin explotación: detecta, fichas y prioriza."
metadata:
  author: "c4a"
  scope: "project"
  version: "1.0.0"
---

# auditoria-php

Análisis estático defensivo de código **aportado por el cliente** (repositorio o
comprimido descomprimido localmente). No se extrae código del objetivo en red y no se
ejecuta nada del código analizado: se lee, se detectan patrones y se fichan hallazgos.

## Cuándo usarla

- Fase 2 del proceso de auditoría del curso (`docs/INSTRUCCION_AUDITORIA_CURSO.md`).
- Cualquier revisión de código PHP/Python propio donde se sospeche ejecución remota,
  webshells o deserialización insegura.

## Cómo correrla

1. Asegúrate de que el código objetivo está en local (clonado o descomprimido) y de que
   es código del propio solicitante. Si no es así, detente: esto no audita sistemas ajenos.
2. Ejecuta la plataforma con el detector habilitado:

   ```bash
   cd platform
   cat > /tmp/audit-php.json <<'EOF'
   {
     "audit_name": "php-estatico", "auditor": "tu-nombre",
     "target": "/ruta/al/codigo", "output_root": "/tmp/salida-php",
     "normativas": ["ISO-27001"], "detectors": ["php-shell", "secrets-files", "dependencies"],
     "scope": {"read_only": true}
   }
   EOF
   python3 -m c4a run --config /tmp/audit-php.json
   python3 -m c4a verify --config /tmp/audit-php.json --run <RUN-ID>
   ```

3. Revisa los hallazgos: cada uno trae archivo, línea, extracto enmascarado, CWE, vector
   CVSS y severidad derivada. La confianza «direct» indica que la llamada peligrosa
   comparte línea con una fuente de entrada (`$_GET`, `request.`, `input()`…).

## Reglas que no se negocian

- **Detección, no explotación.** Nunca ejecutes el código analizado, nunca armemos
  payloads, nunca «confirmemos» nada contra un sistema en red. La confirmación activa es
  Fase 3 y exige `scope/autorizacion.md` firmada y vigente.
- **Sin secretos en la salida.** Los extractos van enmascarados; si aparece un valor
  sensible, se enmascara antes de citarlo.
- **Un hallazgo no es una conclusión.** Cada patrón se reporta con su contexto y queda en
  estado de validación para el auditor humano (principio I de la constitución).
- Los patrones legítimos pueden marcarse en el código con `c4a:ignore` en la línea
  (se respeta igual que en los demás detectores).

## Patrones cubiertos (detector `php-shell`)

- PHP: `system/exec/shell_exec/passthru/popen/proc_open`, backticks, `eval/assert`,
  `preg_replace` con `/e`, `create_function`, `call_user_func` con entrada; `include` con
  ruta de entrada (LFI); `unserialize` con entrada (CWE-502); `move_uploaded_file`
  (CWE-434); ofuscación `base64_decode/gzinflate/str_rot13` + `eval` o llamadas dinámicas
  (webshell, CWE-94/CWE-1007).
- Python: `os.system`, `subprocess` con `shell=True`, `eval/exec` con entrada;
  `pickle.loads/marshal.loads` con entrada (CWE-502).

Para dependencias, complementar con `composer audit` y `pip audit` sobre los manifiestos
aportados, y registrar versiones exactas en la ficha del hallazgo.
