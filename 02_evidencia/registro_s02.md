# El registro (S02) — borrador

> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.
> El registro anota hechos y vacíos: no contiene conclusiones sobre controles.

- **Estado de aprobación**: borrador
- **Huella SHA-256 de `02_evidencia/registro_s02.json`**: `810db8b8afab348649a8b9b5265f1d07c10f3c03c19c0c5c6c37c7723d086394`
- **Firma**: sin firma
- **Alcance de origen**: `scope/alcance_s01.json` · huella 0cb39a0a26ef03cf63c3b4c058be32c73b8fde695b5e69a55f2558757b60757d · **alcance no firmado**
- **Compuerta de autorización**: cerrada (evaluada el 2026-10-22); la herramienta solo la lee.
- **Resumen**: 8 entradas no constan · 0 hechos · 0 rechazos.

«No consta» quiere decir que no se miró o que falta evidencia admisible: no es una ausencia de hallazgos ni un dictamen de cumplimiento.

## No consta (8)

| Id | Activo | Dominio | Resultado | Motivo | Marcas |
|---|---|---|---|---|---|
| `N-14dab2a5a2` | Metasploitable2 | (el activo como un todo) | no-ejecutado | sin evidencia | — |
| `N-aa4ab6a0b6` | Metasploitable2 | Validación controlada de explotabilidad (solo prueba de concepto, no disrupción) | no-ejecutado | compuerta cerrada | alcance pendiente |
| `N-a7de244d2f` | Metasploitable2 | Tecnológicos (A.8): gestión de vulnerabilidades, hardening, criptografía, logging | no-ejecutado | sin evidencia | alcance pendiente |
| `N-fa2c174a34` | Metasploitable2 | Superficie de red y servicios expuestos (puertos, versiones, banners) | no-ejecutado | compuerta cerrada | alcance pendiente |
| `N-e67d5a69f4` | Metasploitable2 | Organizacionales (A.5): gestión de incidentes, políticas, proveedores | no-ejecutado | requiere solicitud documental | alcance pendiente |
| `N-7ed136fffd` | Metasploitable2 | Cifrado en tránsito (TLS/SSH) y exposición de datos | no-ejecutado | compuerta cerrada | alcance pendiente |
| `N-6fe7ab3a93` | Metasploitable2 | Vulnerabilidades conocidas (CVE) y configuraciones inseguras | no-ejecutado | compuerta cerrada | alcance pendiente |
| `N-196c7c4a76` | Metasploitable2 | Autenticación, credenciales por defecto y débiles | no-ejecutado | compuerta cerrada | alcance pendiente |

## Hechos (0)

Ninguno.

## Rechazos (0)

Ninguno.

## Historial (0)

Sin eventos.

## Avisos

- El registro se basa en un alcance no firmado.

Firmar el registro no abre la compuerta de autorización.
