# El encargo (S07) — borrador

> Producto de la herramienta C4A. Trabajo escrito para que una herramienta lo repita.
> El encargo describe trabajo para repetir, sin firmar: no es una evaluación hecha ni un dictamen.
> Este encargo no abre ni transporta la autorización: la corrida que repite verifica scope/autorizacion.md firmada y con ventana vigente antes de cualquier paso técnico.

- **Estado**: borrador (sin firma de aprobación, por diseño de la guía S07)
- **Huella SHA-256 de `01_plan/encargo_s07.json`**: `f7964ec8d55097a2856d689195c11f21ddf13df1a6736bfa0457b757730c7c6c`
- **Integridad**: integro (autor: C4A (propuesta de la herramienta))
- **Resumen**: 12 pasos · 5 repetibles de inmediato · 7 condicionados · 0 no repetibles.

## Cadena de origen (S01–S06)

| Sprint | Archivo | SHA-256 | Estado |
|---|---|---|---|
| S01 | `scope/alcance_s01.json` | `0cb39a0a26ef03cf63c3b4c058be32c73b8fde695b5e69a55f2558757b60757d` | borrador |
| S02 | `02_evidencia/registro_s02.json` | `810db8b8afab348649a8b9b5265f1d07c10f3c03c19c0c5c6c37c7723d086394` | borrador |
| S03 | `03_hallazgos/enunciados_s03.json` | `f7b8d1e13704ae58c86e15e9c30be63cd3d3c20621b8bb3c22d7c7b1a3253941` | borrador |
| S04 | `03_hallazgos/citas_s04.json` | `caa20b0f97e984a102b401ff5d166f20d36675d732fe56c6393c163ac351b967` | borrador |
| S05 | `03_hallazgos/perfil_s05.json` | `a08fefb6dda1cca8362eef93e6f53f614f36bb94a14b22d4ae95ed4434d163f2` | borrador |
| S06 | `03_hallazgos/lista_s06.json` | `1b2767827262d643a0c44af2cca45be45cf51b48f58dab0ca9fd45d047a76097` | borrador |

## Pasos (12)

| Id | Sprint | Repetibilidad | Condición | Descripción |
|---|---|---|---|---|
| `E-156d138e1e` | S01 | inmediata | — | Fijar el alcance del ejercicio: activo «Metasploitable2», 0 dominios dentro y 7 pendientes |
| `E-3601ef79e8` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Superficie de red y servicios expuestos (puertos, versiones, banners |
| `E-3adad4e8ef` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Organizacionales (A.5): gestión de incidentes, políticas, proveedore |
| `E-5f0f370a56` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Cifrado en tránsito (TLS/SSH) y exposición de datos»: aportar eviden |
| `E-769783a840` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Autenticación, credenciales por defecto y débiles»: aportar evidenci |
| `E-a46e8ca5f5` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Vulnerabilidades conocidas (CVE) y configuraciones inseguras»: aport |
| `E-abdd19494a` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Tecnológicos (A.8): gestión de vulnerabilidades, hardening, criptogr |
| `E-d1baeeb536` | S02 | condicionada | verificar cuando conste evidencia admisible para este dominio | Verificar el dominio «Validación controlada de explotabilidad (solo prueba de concepto, no |
| `E-dc14dfddbc` | S03 | inmediata | — | Enunciar el riesgo de cada hecho vigente (0 hoy); los 8 vacíos quedan como condición, no s |
| `E-7b286b492d` | S04 | inmediata | — | Citar cada riesgo en un marco con nombre y versión (0 riesgos); los identificadores que no |
| `E-ad94c6997c` | S05 | inmediata | — | Perfilar el activo con las seis funciones del NIST CSF 2.0 (Gobernar, Identificar, Protege |
| `E-8b50345b66` | S06 | inmediata | — | Listar los CIS Controls que aplican partiendo por el inventario (13 seleccionados hoy, 3 p |

## Historial (1)

| Fecha | Tipo | Autor | Paso | Nuevo | Motivo |
|---|---|---|---|---|---|
| 2026-10-27T02:12:13Z | propuesta | C4A (propuesta de la herramienta) | — | None | Propuesta del encargo a partir de la cadena vigente S01–S06. |

Este encargo no abre ni transporta la autorización: la corrida que repite verifica scope/autorizacion.md firmada y con ventana vigente antes de cualquier paso técnico.
