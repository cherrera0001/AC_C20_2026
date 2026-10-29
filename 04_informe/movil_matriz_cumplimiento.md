# Matriz de cumplimiento — auditoría móvil (anexo del cierre)

**Estado**: FIRMADO el 2026-10-29T01:58:05Z. Niveles: propuesta fundamentada del auditor (principio II); no atribuible al estándar.

| Control | Marco | Riesgo | Hechos | Nivel propuesto | Fundamento |
|---|---|---|---|---|---|
| A.8.9 | ISO/IEC 27001 2022 | R1 | H6 | **parcial** | superficie exportada amplia sin permiso (65 componentes, 51 alcanzables); la configuración está endurecida en dominios clave pero la superficie IPC/deeplink queda expuesta a apps del equipo |
| A.8.3 | ISO/IEC 27001 2022 | R2 | H5 | **parcial** | permisos sensibles concedidos por decisión del usuario; restricciones aplicadas a SMS/llamadas/legacy storage |
| A.8.9 | ISO/IEC 27001 2022 | R3 | H6 | **parcial** | función de instalación de paquetes declarada; su abuso depende de flujos internos no verificados |
| A.8.24 | ISO/IEC 27001 2022 | R4 | H7 | **cumple** | las reglas de backup y transferencia excluyen todo el almacén de la app y exigen capacidad de cifrado; residual: cifrado del dispositivo medido (FBE) |
| A.8.3 | ISO/IEC 27001 2022 | R5 | H5 | **parcial** | almacenamiento legacy declarado pero mitigado por denegaciones de runtime |
| A.8.8 | ISO/IEC 27001 2022 | R6 | H1+postura | **cumple** | bootloader bloqueado, verified boot green, verity enforcing, parche 2026-09-01 dentro de cadencia del fabricante |
| A.8.8 | ISO/IEC 27001 2022 | R7 | H2 | **cumple** | versión 2.26.42.74 vigente (2026-10-28) con auto-actualización por Play |
| A.8.24 | ISO/IEC 27001 2022 | R8 | H8 | **parcial** | cifrado fuerte en dominios de mensajería (pin-set 20+) pero base-config cleartext y CA de usuario con override de pins |

Funciones NIST CSF 2.0 con material: Gobernar, Identificar, Proteger, Detectar y Recuperar (5 de 6); Responder: no consta (sin hechos en equipo personal).
