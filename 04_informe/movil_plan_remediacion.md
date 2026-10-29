# Plan de remediación — auditoría móvil WhatsApp Business

Ordenado por prioridad combinada (severidad técnica + contexto del titular).

| Prioridad | ID | Riesgo | Componente | Acción | Responsable sugerido | Plazo sugerido |
|---|---|---|---|---|---|---|
| 1 | R8 | Cleartext base + CA usuario con override de pins | network_security_config | No instalar CA de usuario salvo necesidad transitoria; eliminarlos al terminar; verificar ajustes de seguridad de red. | Titular | Inmediato |
| 2 | R1 | Superficie exportada sin permiso (65; 51 con intent-filter) | AndroidManifest / componentes | Revisar en decompilación jadx los componentes señalados (OTP receivers, WebLoginResultHandler, SmbLinking, Instrumentation); si faltan validaciones, reportar a Meta. | Titular | 30 días |
| 3 | R2 | Permisos sensibles concedidos | Permisos runtime | Dejar ubicación y micrófono en «solo con la app en uso» si el uso lo permite; revisar contactos. | Titular | 7 días |
| 4 | R3 | REQUEST_INSTALL_PACKAGES | Manifiesto | Aceptar solo instalaciones iniciadas por uno mismo; desconfiar de prompts inesperados. | Titular | Continuo |
| 5 | R6 | Parche 2026-09-01 | Plataforma | Mantener actualización automática del SO; verificar parche mensual. | Titular | Continuo |
| 6 | R7 | Versión de la app | WhatsApp Business | Mantener auto-actualización por Play. | Titular | Continuo |
| 7 | R5 | Legacy external storage | Manifiesto | Sin acción: mitigado por denegaciones de runtime (monitorear). | Titular | — |
| 8 | R4 | Backup | Reglas de backup | Sin acción: exclusiones totales verificadas; cifrado FBE activo. | Titular | — |
