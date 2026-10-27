# Decisión: tesis canónica de la herramienta C4A

Estado: **adoptada** (2026-10-26). Registro de decisión; no modifica los archivos base ni el código.

## Problema

El repositorio sostenía tres definiciones a la vez:

1. **Pentest de red** (`scope/alcance.md`, `docs/AUDIT_PROMPT.md`): cuatro fases, reconocimiento
   sobre 192.168.1.14 (Metasploitable2), compuerta de autorización, CVSS v4.0.
2. **Motor de análisis estático** (`platform/c4a/`): corpus de archivos (repositorio VT), sin red,
   CVSS 3.1, matriz de control con otro esquema.
3. **Copiloto del auditor** (`docs/PROMPT_SPEC_KIT.md`, S01–S10): la herramienta propone, el auditor
   corrige y firma; diez productos en orden.

## Decisión

La tesis canónica es **3, el copiloto del auditor** (`docs/PROMPT_SPEC_KIT.md`). Razón: es la
definición más reciente y concreta, y declara su propia precedencia («si chocan con este hilo,
manda este hilo y la guía»).

## Consecuencias

| Elemento | Estado bajo la tesis canónica |
|---|---|
| `docs/PROMPT_SPEC_KIT.md` | Fuente de verdad del producto. |
| `scope/alcance.md`, `docs/historia_usuario.md` | Contexto y contrato del alcance. Las fases de red y los escenarios que las exigen quedan **sin vigencia** hasta revisarlos. |
| `docs/AUDIT_PROMPT.md` | Vigente solo para la Fase 1–4 como formato de salida. Su Fase 2 (red) queda **suspendida**. |
| `platform/c4a/` (motor estático) | Se reclasifica como **posible insumo de «Recopilar»** para repositorios, sin red. Su alcance propio se define en una épica nueva si se decide usarlo. |
| S01 (`specs/001`), S02 (`specs/002`) | Coherentes con la tesis canónica. |

## Decisiones derivadas (pendientes de implementar)

- **CVSS:** se fija **v4.0** como objetivo del copiloto, porque `scope/alcance.md` §7 lo exige. El
  motor que hoy calcula 3.1 (`platform/ROADMAP.md`) queda como deuda, no como norma.
- **Compuerta de autorización:** aplica a **cualquier acción de red** contra un objetivo. El análisis
  estático de archivos locales no la requiere, pero debe declararse en el alcance. Hoy
  `run_audit` no la consulta; eso es deuda registrada, no se resuelve aquí.
- **Esquema de la matriz:** el de `docs/AUDIT_PROMPT.md` (`id,hallazgo,control_iso,ley_articulo,brecha,severidad,prioridad,accion`)
  es la referencia; la matriz actual de `03_hallazgos/` queda como deuda.

## Lo que no se decide aquí

- Reescribir `scope/alcance.md`, `docs/historia_usuario.md` o `docs/AUDIT_PROMPT.md`.
- Cambiar la constitución de Spec Kit (`/speckit-constitution`), que se hace en una etapa propia.
- Cerrar S02 (`/speckit-converge`) y las tareas humanas T032, T033, T038 y T039.
- Autorizar comandos de red: `scope/autorizacion.md` sigue sin firmar.

## Procedencia

El origen en el chat de los tres archivos base es declarado por el dueño; el repositorio
verifica su presencia conjunta en el commit `be93fd3` (2026-10-05). Ver `docs/LINEA_ORIGEN.md`.

## Estado de cierre (2026-10-26)

| Pendiente | Estado | Evidencia |
|---|---|---|
| Tesis canónica | Cerrado (adoptado) | Este documento; constitución 1.1.0 (Gobernanza); vigencias en los tres archivos base |
| Constitución alineada | Cerrado | `.specify/memory/constitution.md` 1.1.0 |
| CVSS v4.0 como objetivo | Cerrado en el módulo; **abierto en los hallazgos** | `platform/c4a/cvss4.py` y `tests/test_cvss4.py`; los hallazgos siguen en v3.1 (`platform/c4a/cvss.py`) |
| Compuerta para red contra objetivos | Cerrado como invariante | `tests/test_sin_red_objetivo.py`: la única URL de red es `api.osv.dev`; sin `socket` |
| Restos de «30-sep» en procedencia | Cerrado | `docs/LINEA_ORIGEN.md` |
| Vigencia en archivos base | Cerrado | Banners en `scope/alcance.md`, `docs/AUDIT_PROMPT.md`, `docs/historia_usuario.md` |
| `/speckit-converge` de S02 | Cerrado: converged (2.ª pasada, 2026-10-26) | `tasks.md` sin cambios; fase 8 verificada en código y pruebas; 136 pruebas OK; SC-009 queda manual (T038) |
| T032, T033, T038, T039 | **Humano** | Mediciones SC-003/SC-008 y firmas del auditor; no las puede hacer la herramienta |
| Firma de `scope/autorizacion.md` | **Humano** | Firmante, facultad, origen, ventana y contacto de emergencia no constan |

Dependencia opcional: `cvss==3.6` (LGPL-3.0) solo para el cálculo v4.0. El núcleo sigue sin
dependencias. Sin el paquete, el bloque v4.0 sale sin puntaje y con motivo.
