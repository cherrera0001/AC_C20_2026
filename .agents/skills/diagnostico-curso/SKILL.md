---
name: "diagnostico-curso"
description: "Diagnóstico no invasivo del fallo de un curso en la plataforma: navegación autenticada de solo lectura, captura del síntoma, recon pasivo enmascarado. Sin payloads, fuzzing ni escaneo; no requiere compuerta de autorización."
metadata:
  author: "c4a"
  scope: "project"
  version: "1.0.0"
---

# diagnostico-curso

Fase 1 del encargo del curso (`docs/INSTRUCCION_AUDITORIA_CURSO.md`): reproducir el
fallo con la **cuenta del auditor**, caracterizar el síntoma (mensaje de error, código
HTTP, si el fallo es del curso o del permiso) y dejar evidencia pasiva con hash.
Operación de **solo lectura**: navegación y GET. No exige `scope/autorizacion.md`
firmada, pero tampoco la sustituye: nada de lo que hace esta skill es una prueba activa.

## Cuándo usarla

- El dueño reporta que un curso falla y pide caracterizar el síntoma.
- Antes de cualquier análisis estático o verificación dinámica: es la línea base.

## Cómo correrla

Requiere el venv de la estación con Playwright/Chromium (`~/.venv-c4a-audit`). Los
valores sensibles se leen de `.env` **en runtime** por el script; el agente no lee `.env`
ni recibe los valores.

```bash
cd platform
~/.venv-c4a-audit/bin/python tools/diagnostico_curso.py claves   # nombres de claves .env (nunca valores)
~/.venv-c4a-audit/bin/python tools/diagnostico_curso.py curso     # login + captura del síntoma enmascarada
~/.venv-c4a-audit/bin/python tools/recon_curso.py                 # recon pasivo autenticado (huellas visibles)
```

MCP equivalente (cuando esté cargado en la sesión): **Playwright**
(`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`) con la sesión
autenticada del auditor, y **REA** (`inspect_web_page`, captura web pasiva). Los scripts
de `platform/tools/` son la vía programática del mismo trabajo y la que deja salida
determinista en disco.

## Salida

- `evidence/capturas_curso/`: JSON/HTML/PNG con usuario, clave y `sesskey` enmascarados.
- Ficha del síntoma (estado, mensaje, alcance: ¿solo ese id de curso?) y `huellas.txt`
  con SHA-256 de cada captura.

## Reglas que no se negocian

- **Solo lectura.** Prohibido enviar formularios que modifiquen estado, subir archivos,
  probar payloads o fuzzear parámetros. Si una acción escribe en el objetivo, no es de
  esta skill.
- **Nada de secretos en disco ni en chat.** Los valores de `.env` nunca se imprimen,
  copian ni persisten; enmascarar `sesskey` y credenciales en toda captura es parte de
  la corrida, no un paso opcional.
- **Caracterizar, no concluir.** El síntoma se describe; la causa se propone como
  hipótesis etiquetada. La confirmación activa es Fase 3 y exige compuerta.
- **Trabajo repetible.** Toda captura lleva huella SHA-256 en `huellas.txt` y la ficha
  referencia los archivos por ruta + hash (skill `evidencia-integridad`).
