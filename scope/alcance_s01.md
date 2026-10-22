# El alcance (S01) — borrador

> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.
> Este alcance delimita qué se audita y qué no: no contiene conclusiones sobre controles.

- **Estado de aprobación**: borrador
- **Huella SHA-256 de `scope/alcance_s01.json`**: `0cb39a0a26ef03cf63c3b4c058be32c73b8fde695b5e69a55f2558757b60757d`
- **Firma**: sin firma

## Insumos

| Archivo | Existe | SHA-256 |
|---|---|---|
| `scope/alcance.md` | sí | d19a1fd84561dcfe776c4625e11fb9850f4747c0e451113ab2f91a0073343b71 |
| `scope/autorizacion.md` | sí | b0a8443f3a3c69bf15ef328546a97fde859aeb3f42bb1778b5efb4c1440c6a97 |

## Compuerta de autorización (fecha de referencia 2026-10-21)

| Firma | Completitud | Ventana | Resultado |
|---|---|---|---|
| no firmada | incompleta | no informada | **cerrada** |

Motivos: no firmada; incompleta: Representante que autoriza, Facultad para autorizar, IP de origen del auditor, Inicio, Fin, Nombre, Vía y disponibilidad, Nombre y cargo, Fecha, Firma; ventana no informada.

Firmar el alcance no abre la compuerta de autorización. La herramienta solo lee `scope/autorizacion.md`.

## Pendientes (22)

| Id | Tipo | Valor | Qué falta | Fuente |
|---|---|---|---|---|
| `A-9d8d89c595` | marco | NIST CSF 2.0 | decisión (no consta) | .specify/memory/constitution.md §IV |
| `A-3aa198f837` | marco | CIS Controls v8.1 | decisión (no consta) | .specify/memory/constitution.md §IV |
| `A-0e8b027570` | obligacion | Ley 21.663 + ANCI: Gestión de incidentes, medidas mínimas, reporte a CSIRT/ANCI (3 h alerta temprana, 72 h reporte), delegado de ciberseguridad (si aplica OIV) | VALIDAR: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad | scope/alcance.md §3 |
| `A-a3251ac311` | obligacion | Ley 21.719: Bases de licitud, derechos ARCO+, datos sensibles, seguridad del tratamiento, DPO, transferencias internacionales | VALIDAR: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad | scope/alcance.md §3 |
| `A-641a360a94` | obligacion | Ley 21.459 (delitos informáticos): No se audita: delimita lo legalmente permitido durante las pruebas | VALIDAR: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad | scope/alcance.md §3 |
| `A-7f614b0027` | dominio | Superficie de red y servicios expuestos (puertos, versiones, banners) | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-ca09b441f3` | dominio | Vulnerabilidades conocidas (CVE) y configuraciones inseguras | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-f1a1774093` | dominio | Autenticación, credenciales por defecto y débiles | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-ad0247cfde` | dominio | Cifrado en tránsito (TLS/SSH) y exposición de datos | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-0aea6c19e2` | dominio | Validación controlada de explotabilidad (solo prueba de concepto, no disrupción) | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-25010a8801` | dominio | Tecnológicos (A.8): gestión de vulnerabilidades, hardening, criptografía, logging | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-813b10bb1c` | dominio | Organizacionales (A.5): gestión de incidentes, políticas, proveedores | decisión (declarado: incluido) | scope/alcance.md §4 |
| `A-46766d1c32` | exclusion | Todo sistema, dirección o dominio no listado en este documento, y las actividades de scope/alcance.md §5 | decisión (declarado: excluido) | scope/autorizacion.md §2 |
| `A-830307c098` | exclusion | Ataques de denegación de servicio (DoS/DDoS) y cualquier técnica disruptiva | decisión (declarado: excluido) | scope/alcance.md §5 |
| `A-1a2e134422` | exclusion | Ingeniería social, phishing y acceso físico (salvo anexo contratado aparte) | decisión (declarado: excluido) | scope/alcance.md §5 |
| `A-a2866bd0db` | exclusion | Sistemas, IP o dominios no listados explícitamente en la autorización | decisión (declarado: excluido) | scope/alcance.md §5 |
| `A-7a6c2bf54b` | exclusion | Modificación, borrado o exfiltración real de datos productivos | decisión (declarado: excluido) | scope/alcance.md §5 |
| `A-e0ec21a37f` | exclusion | Auditoría financiera, contable o de RR.HH | decisión (declarado: excluido) | scope/alcance.md §5 |
| `A-66f99624c4` | regla | Manejo de evidencia: toda captura se almacena cifrada, con cadena de custodia y hash. Datos personales que aparezcan se minimizan/enmascaran de inmediato | decisión (declarado: incluido) | scope/alcance.md §6 |
| `A-a79af3dcc0` | compuerta | no firmada | decisión (no consta) | scope/autorizacion.md encabezado y §6 |
| `A-69090a3d64` | compuerta | incompleta | decisión (no consta) | scope/autorizacion.md §1–§6 |
| `A-79d5e52b66` | compuerta | no informada | decisión (no consta) | scope/autorizacion.md §3 |

## Activo

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-ea4a7a8240` | Metasploitable2 (tipo: host; rol: objetivo del laboratorio inicial) | incluido | — | scope/alcance.md §4 | borrador | — |

## Organización auditada

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-dcfd37ef23` | Comercial Andes Sur SpA (cliente del informe de cierre según docs/PROMPT_SPEC_KIT.md; ejercicio de laboratorio) | incluido | — | scope/autorizacion.md §1 | borrador | Consta en la autorización; la firma del representante es aparte. |

## Marcos de referencia

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-de7ee6f434` | ISO/IEC 27001:2022 | incluido | — | scope/alcance.md §3 | borrador | Versión 2022; implementado parcialmente; 12 de 93 controles del Anexo A en el catálogo de la herramienta. |
| `A-9d8d89c595` | NIST CSF 2.0 | pendiente de confirmar | — | .specify/memory/constitution.md §IV | borrador | Versión 2.0; mencionado; el catálogo trae las seis funciones, sin categorías ni subcategorías. Marco de referencia de la constitución; no está declarado en el alcance. |
| `A-3aa198f837` | CIS Controls v8.1 | pendiente de confirmar | — | .specify/memory/constitution.md §IV | borrador | Versión v8.1; mencionado; sin catálogo en la herramienta. Marco de referencia de la constitución; no está declarado en el alcance. |

## Obligaciones candidatas

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-0e8b027570` | Ley 21.663 + ANCI: Gestión de incidentes, medidas mínimas, reporte a CSIRT/ANCI (3 h alerta temprana, 72 h reporte), delegado de ciberseguridad (si aplica OIV) | incluido | — | scope/alcance.md §3 | borrador | Obligación candidata. Falta: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad. La aplicabilidad depende de la clasificación OIV / servicio esencial, que no consta (scope/alcance.md §9). |
| `A-a3251ac311` | Ley 21.719: Bases de licitud, derechos ARCO+, datos sensibles, seguridad del tratamiento, DPO, transferencias internacionales | incluido | — | scope/alcance.md §3 | borrador | Obligación candidata. Falta: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad. |
| `A-641a360a94` | Ley 21.459 (delitos informáticos): No se audita: delimita lo legalmente permitido durante las pruebas | excluido | No se audita: delimita lo legalmente permitido durante las pruebas | scope/alcance.md §3 | borrador | Obligación candidata. Falta: fuente oficial, fecha de consulta, artículo, fundamento de aplicabilidad. |

## Dominios

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-7f614b0027` | Superficie de red y servicios expuestos (puertos, versiones, banners) | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-ca09b441f3` | Vulnerabilidades conocidas (CVE) y configuraciones inseguras | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-f1a1774093` | Autenticación, credenciales por defecto y débiles | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-ad0247cfde` | Cifrado en tránsito (TLS/SSH) y exposición de datos | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-0aea6c19e2` | Validación controlada de explotabilidad (solo prueba de concepto, no disrupción) | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-25010a8801` | Tecnológicos (A.8): gestión de vulnerabilidades, hardening, criptografía, logging | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Declarado incluido, sin motivo en el ítem. |
| `A-813b10bb1c` | Organizacionales (A.5): gestión de incidentes, políticas, proveedores | pendiente de confirmar | — | scope/alcance.md §4 | borrador | Requiere políticas, personas o procesos: no se acredita con una prueba técnica. Declarado incluido, sin motivo en el ítem. |

## Exclusiones

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-46766d1c32` | Todo sistema, dirección o dominio no listado en este documento, y las actividades de scope/alcance.md §5 | pendiente de confirmar | — | scope/autorizacion.md §2 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |
| `A-830307c098` | Ataques de denegación de servicio (DoS/DDoS) y cualquier técnica disruptiva | pendiente de confirmar | — | scope/alcance.md §5 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |
| `A-1a2e134422` | Ingeniería social, phishing y acceso físico (salvo anexo contratado aparte) | pendiente de confirmar | — | scope/alcance.md §5 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |
| `A-a2866bd0db` | Sistemas, IP o dominios no listados explícitamente en la autorización | pendiente de confirmar | — | scope/alcance.md §5 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |
| `A-7a6c2bf54b` | Modificación, borrado o exfiltración real de datos productivos | pendiente de confirmar | — | scope/alcance.md §5 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |
| `A-e0ec21a37f` | Auditoría financiera, contable o de RR.HH | pendiente de confirmar | — | scope/alcance.md §5 | borrador | Declarado fuera de alcance, sin motivo en el ítem. |

## Reglas de enganche

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-0ee5d708b2` | El rango y el host objetivo constan en scope/autorizacion.md §2; no se copian aquí | incluido | — | scope/alcance.md §4 | borrador | — |
| `A-d88fecd59b` | Autorización escrita previa de un representante con facultad, con ventana temporal, IP de origen del auditor y rango objetivo. Sin esto no se ejecuta nada (Ley 21.459) | incluido | — | scope/alcance.md §6 | borrador | — |
| `A-a01ccc1a81` | Ventana de ejecución acordada; fuera de ella, solo análisis documental | incluido | — | scope/alcance.md §6 | borrador | — |
| `A-f572be7525` | Técnicas permitidas: reconocimiento pasivo/activo, enumeración, escaneo de vulnerabilidades, verificación de explotabilidad en modo seguro | incluido | — | scope/alcance.md §6 | borrador | — |
| `A-44eafd5d03` | Técnicas prohibidas: disrupción de servicio, pivoting fuera del rango, persistencia, alteración de datos | incluido | — | scope/alcance.md §6 | borrador | — |
| `A-66f99624c4` | Manejo de evidencia: toda captura se almacena cifrada, con cadena de custodia y hash. Datos personales que aparezcan se minimizan/enmascaran de inmediato | pendiente de confirmar | — | scope/alcance.md §6 | borrador | Requisito declarado que el sistema no garantiza hoy: tener huellas de integridad no equivale a cifrado. |
| `A-75a6580704` | Contacto de emergencia y criterio de «stop»: ante señal de impacto productivo o hallazgo crítico activo, se detiene y se escala | incluido | — | scope/alcance.md §6 | borrador | — |

## Compuerta de autorización (declarado)

| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |
|---|---|---|---|---|---|---|
| `A-a79af3dcc0` | no firmada | pendiente de confirmar | — | scope/autorizacion.md encabezado y §6 | borrador | — |
| `A-69090a3d64` | incompleta | pendiente de confirmar | — | scope/autorizacion.md §1–§6 | borrador | — |
| `A-79d5e52b66` | no informada | pendiente de confirmar | — | scope/autorizacion.md §3 | borrador | — |

## Historial (0)

Sin correcciones.
