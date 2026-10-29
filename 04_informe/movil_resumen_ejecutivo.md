# Resumen ejecutivo — Auditoría móvil (dispositivo personal + WhatsApp Business)

**Ejecución:** RUN-20261029T003246Z-3802 · 2026-10-29 · objetivo: teléfono personal del auditor (Xiaomi) y `com.whatsapp.w4b`
**Alcance:** solo lectura (ADB + análisis estático del APK). Sin tráfico de red, sin ejecución de la app, sin datos de terceros.

## Estado en una línea

El teléfono está bien protegido y la aplicación es genuina y está al día; se identificaron **8 riesgos (0 críticos: 1 alto, 3 medios, 4 bajos)**, todos gestionables con configuración y hábitos del titular. Productos firmados y evidencia verificable en cada afirmación.

## Riesgos por severidad

| Severidad | N.º | IDs |
|---|---|---|
| Alto | 1 | R1 |
| Medio | 3 | R2, R3, R8 |
| Bajo | 4 | R4, R5, R6, R7 |

## Los cinco de mayor prioridad

1. **R1 (alto)** — La app expone 65 componentes a otras apps del equipo sin protección de permisos (51 alcanzables directamente); conviene confirmar sus validaciones internas.
2. **R8 (medio)** — La configuración de red permite tráfico sin cifrar fuera de los dominios de WhatsApp y confía en certificadores instalados por el usuario, lo que puede anular el anclaje de certificados.
3. **R3 (medio)** — La app puede iniciar instalaciones de otras aplicaciones; solo aceptar instalaciones propias y esperadas.
4. **R2 (medio)** — Permisos sensibles activos (ubicación precisa, micrófono, cámara, contactos); ajustarlos a «solo con la app en uso» donde se pueda.
5. **R6 (bajo, residual)** — El parche de seguridad tiene ~2 meses; mantener la actualización automática del sistema.

## Qué significa y qué sigue

No hay indicio de compromiso: el arranque del equipo está verificado, el almacenamiento cifrado, el antivirus de Google activo, y la app fue instalada y se actualiza por Google Play con firma criptográfica de WhatsApp comprobada. Los riesgos restantes son de configuración y de superficie propia de una app de mensajería de este tamaño. El plan de remediación (movil_plan_remediacion.md) ordena las acciones; la mayoría es gratuita y toma minutos.

## Decisiones solicitadas

- Aprobar los ajustes de permisos recomendados (ubicación/micrófono solo con la app en uso).
- Acordar la regla de no instalar certificados de empresa/proxy en el equipo personal.
- Mantener activadas las actualizaciones automáticas de sistema y de la app.

## Limitaciones

No se analizó tráfico de red ni comportamiento en ejecución (por diseño del alcance). Una referencia legal (artículo de la Ley 21.719) quedó marcada VALIDAR. La función «Responder» del marco NIST queda sin material: un equipo personal no tiene proceso formal de respuesta a incidentes.

La evidencia de cada afirmación está en evidence/RUN-20261029T003246Z-3802/ con huella SHA-256 y verificación independiente (SHA256SUMS). Este resumen se presenta junto al informe de cierre firmado.
