# Hecho técnico — Síntoma del curso 848 (aula virtual)

**Id**: sintoma-curso-848 · **Fecha**: 2026-10-27 · **Fase**: 1 (diagnóstico no invasivo)
**Rol**: diagnostico-web · **Estado**: borrador — propuesto al auditor para revisión y firma
(principio I de la constitución: la herramienta propone, el auditor firma).

## Resultado técnico

| Dimensión | Valor |
|---|---|
| Resultado | **positivo** (la comprobación se ejecutó y el sistema exhibe el error de aplicación medido) |
| Comprobación | Petición de solo lectura a la vista del curso con sesión autenticada del auditor |
| Código HTTP | 500 |
| Mensaje | «ID de módulo de curso no válida» (`invalidcoursemodule`) |
| Alcance del efecto | Un único curso (id 848); cursos hermanos y resto del aula sin efecto observable |

## Evidencia (rutas bajo `evidence/capturas_curso/`, fuera de git)

Qué bytes acredita cada pieza (skill `evidencia-integridad`): los hashes siguientes
acreditan los **bytes enmascarados persistidos** (usuario, clave y `sesskey` fueron
reemplazados por `***` antes de guardar); no acreditan bytes de tránsito. Verificación:
`cd evidence/capturas_curso && sha256sum -c SHA256SUMS.txt` (7/7 OK el 2026-10-27).

| Pieza | Acredita | SHA-256 |
|---|---|---|
| `02_curso.png` | Representación visual del error 500 en la vista del curso | e57018d8a128e891319dac0a54c7076f9937efa2475e76ef944ac8dd58cddef2 |
| `diagnostico_curso.json` | Medición estructurada: petición, código, mensaje, radio de impacto | f54c1bc80bc989dfd9254de609dba1ea2ec4c03043e70aa5c19fbf2078d8d7a6 |
| `recon/paginas/curso_848.html` | Cuerpo de la respuesta 500 | 67ca1586bf673f26ea2692c282d9159204e49c916acedf37e0cb30ad37d6d92e |
| `recon/paginas/home.html` | Contraste: la cuenta autenticada funciona en el resto del aula | 2effe7b4d0ffe86514c39b3567d28eee1dae98d797e9352a6f582a416e8a99ba |
| `recon/paginas/probe_reportbuilder.html` | Contraste: ruta administrativa de informes accesible y operativa | 5b2ebaed70d8fdc26f212a3a1a2ca880fb2bd6d7e68bb190d11f296bf4f5e06c |
| `recon/resumen.json` | Resumen estructurado del recon pasivo | b762cd845140eee51ad5343d4c4e8e66df600786a7de45d4a24a5867a895d612 |
| `01_login.png` | La sesión autenticada existe (descarta fallo de login) | 7520386e18b98f2d3b37e52c3112097a9d819984c848ed84a392c7ca74d385dd |

## Hipótesis ordenadas (consistentes con el síntoma; ninguna es conclusión)

1. **H1 — Referencia interna rota del curso**: un course module citado en la secuencia del
   curso ya no existe en la base de datos; el renderizado de la portada lo resuelve y
   falla → 500. Es la causa documentada públicamente para `invalidcoursemodule`
   (borrado de sección/módulo, mantenimiento a medias).
2. **H2 — Restauración o actualización incompleta**: un backup/restore o upgrade del curso
   quedó a medio aplicar; deja la misma referencia rota que H1 con origen operativo.
3. **H3 — Plugin de formato/tema**: el formato de curso instalado (multitopic) o el tema
   comercial resuelve secciones de forma distinta al núcleo y expone la referencia rota
   que el formato estándar toleraría.
4. **H4 — Manipulación maliciosa (ejecución remota)**: el síntoma sería efecto de un
   incidente (p. ej. explotación de vulnerabilidad del tipo php2shell con borrado/édito
   de datos del curso). **Estado: pendiente de confirmar** — solo código aportado
   (Fase 2) o verificación con compuerta (Fase 3) la elevan o la descartan.

Prioridad de explicación: H1/H2 (integridad de datos por mantenimiento) antes que H3
(código) antes que H4 (intrusión); la constante de despliegue reciente (2026-10-26 ~06:30)
acomoda las cuatro, así que ninguna se descarta por fecha.

## Encuadre (propuesta, sin dictamen)

- Posible encuadre futuro del hecho: control ISO/IEC 27001:2022 sobre gestión de
  vulnerabilidades/cambios y obligaciones de gestión de incidentes Ley 21.663 — la
  correspondencia exacta la propone la Fase 4 (skill `correlacion-cumplimiento`) una vez
  confirmada la causa. Hoy: **sin encuadre, sin cumplimiento inferido** (principio II).
- Contexto de amenazas público ya fichado en `evidence/capturas_curso/FICHA_SINTOMA_848.md`
  (CVE recientes del ecosistema LMS, incluido el advisory php2shell publicado ~2026-10-14):
  monitoreo defensivo, no evidencia de intrusión.

## Pendientes

- Causa raíz: logs del servidor y/o código aportado (P1 del catálogo).
- Compuerta para Fase 3: `scope/autorizacion.md` firmada con ventana.
- Ubicación formal en la cadena S01–S10/S11: decisión del dueño.
