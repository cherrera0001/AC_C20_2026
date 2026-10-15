# Estación local para el flujo académico

## Objetivo

Permite ejecutar el repositorio C4A en Windows, con PowerShell y WSL, sin instalar dependencias externas para el núcleo. El estudiante conserva la responsabilidad de ejecutar las pruebas dentro de un laboratorio autorizado y aislado.

## 1. Requisitos

- Windows 10/11 con PowerShell 5.1 o PowerShell 7.
- Git.
- Python 3.10 o superior.
- WSL 2 con Ubuntu si se quiere ejecutar las herramientas de red.
- Claude Code CLI con una cuenta autorizada.
- VirtualBox o VMware con Metasploitable 2, solo si el relator autoriza la ejecución.

## 2. Clonar o abrir el repositorio

El repositorio de trabajo debe estar en una ruta local, por ejemplo:

```powershell
cd "C:\Users\herre\OneDrive\Documentos\AC_C20_2026"
```

Si el repositorio está en WSL, use una ruta accesible, por ejemplo:

```bash
cd /mnt/c/Users/herre/OneDrive/Documentos/AC_C20_2026
```

No se debe crear una copia de los materiales de clase en una carpeta de red o en una ruta compartida sin autorización.

## 3. Python y comandos

En PowerShell, verificar:

```powershell
python --version
git --version
```

Ejecutar la plataforma desde la raíz:

```powershell
cd .\platform
python -m c4a --help
```

El núcleo usa la biblioteca estándar de Python y no necesita una instalación de paquetes para su ejecución básica.

## 4. WSL y herramientas de red

En WSL, instalar y verificar las herramientas únicamente si el relator del laboratorio las exige:

```bash
sudo apt update
sudo apt install -y nmap netcat-openbsd curl jq python3
```

Verificar:

```bash
nmap --version
python3 --version
```

No ejecutar `nmap` sobre una dirección fuera del alcance autorizado. La ejecución debe ser revisada antes de cada comando.

## 5. Claude Code

Verificar la instalación:

```powershell
claude --version
```

Ejecutar el prompt consolidado:

```powershell
$prompt = Get-Content .\CLAUDE_CODE_PROMPT.md -Raw
claude -p $prompt
```

La forma anterior puede variar según el SKU y la versión del CLI. Si el comando de `claude -p` no acepta el contenido, copie el archivo al prompt de una nueva sesión y use exactamente el contenido de `CLAUDE_CODE_PROMPT.md`.

## 6. Estructura de en ejecución

```text
scope/
01_plan/
02_evidencia/
03_hallazgos/
04_informe/
evidence/
platform/
```

Cada archivo generado debe conservar la fecha, la fuente, el responsable y el estado de revisión.

## 7. Autorización y seguridad

Antes de cualquier prueba técnica:

1. Confirmar que `scope/autorizacion.md` está firmada.
2. Confirmar el objetivo, la red, la ventana y el representante autoriza.
3. Verificar que el objetivo está dentro del rango.
4. Inscribir el comando que se ejecutará.
5. Registrar la salida en `evidence/` con timestamp y hash.
6. Detenerse si aparece una señal de impacto productivo o una condición no autorizada.

Prohibido: DoS, pivoting, persistencia, modificación, borrado, exfiltración, ingeniería social, acceso a cualquier host fuera del alcance y pruebas sobre terceros.

## 8. Flujo local

```powershell
# 1. Revisar el alcance y la autorización
Get-Content .\scope\alcance.md
Get-Content .\scope\autorizacion.md

# 2. Ejecutar el prompt consolidado
$prompt = Get-Content .\CLAUDE_CODE_PROMPT.md -Raw
claude -p $prompt

# 3. Revisar los artefactos y el estado de VALIDAR
Get-ChildItem .\01_plan, .\02_evidencia, .\03_hallazgos, .\04_informe, .\evidence -Recurse

# 4. Verificar la fuente del material de clase
Get-ChildItem -Path "F:\Code\Auditoría a la Ciberseguridad\entregables\contenido" -Filter "S0*.json"
```

No se debe ejecutar el flujo de red si la autorización no está firmada. El comando de `nmap` no debe ser ejecutado como sustituto del control de autorización.

## 9. Reproducibilidad

Para cada evidencia:

- Guardar la salida bruta.
- Guardar el comando ejecutado.
- Guardar la fecha y la zona horaria.
- Guardar el hash SHA-256.
- Guardar la persona o agente que ejecutó el procedimiento.
- Guardar la revisión humana.

## 10. Conclusión

El entorno local es una herramienta de soporte, no una fuente de autoridad normativa. Las decisiones de alcance, marco, requisitos y cumplimiento deben quedar en archivos firmados y revisados por el estudiante.
