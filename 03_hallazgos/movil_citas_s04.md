# S04 (móvil) — La cita: riesgos ubicados en marco con versión e identificador

**Estado**: FIRMADO el 2026-10-29T01:50:33Z — registro en `movil_citas_s04.firma.json`. Propuesta de la herramienta; correspondencia = sugerencia explicada (principio II).

## R1
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.9**
- Fundamento: 65 componentes exportados sin permiso (51 con intent-filter): la gestion de la configuracion exige endurecer la superficie expuesta; A.8.9 consta en la base de conocimiento.
- CWE sugerido: CWE-926 (pendiente de confirmar) — Improper Export of Android Application Components; no consta en cwe_map.json, se propone sin confirmar.
- Hechos ancla: H6

## R2
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.3**
- Fundamento: Permisos sensibles concedidos (ubicacion precisa, microfono, camara, contactos, medios): la restriccion de acceso a la informacion limita la exposicion; A.8.3 consta en la base.
- CWE sugerido: CWE-250 (confirmado en cwe_map.json) — Execution with Unnecessary Privileges; menor privilegio.
- Hechos ancla: H5

## R3
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.9**
- Fundamento: REQUEST_INSTALL_PACKAGES declarado: la configuracion segura restringe funciones de instalacion; A.8.9 consta en la base.
- CWE sugerido: CWE-494 (confirmado en cwe_map.json) — Download of Code Without Integrity Check; ajuste explicado: la instalacion de paquetes sin verificacion adicional es el vector.
- Hechos ancla: H6

## R4
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.24**
- Fundamento: Backup: la app excluye todo su almacen y exige capacidad de cifrado (disableIfNoEncryptionCapabilities); el uso de criptografia protege lo respaldado; A.8.24 consta en la base.
- CWE sugerido: CWE-312 (confirmado en cwe_map.json) — Cleartext Storage of Sensitive Information; cruzado por LEY-21719 en el mapa (cifrado de datos).
- Hechos ancla: H7

## R5
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.3**
- Fundamento: requestLegacyExternalStorage activo: la restriccion de acceso a la informacion cubre la superficie de almacenamiento amplificada; mitigado por denegaciones de runtime (H5).
- CWE sugerido: CWE-200 (confirmado en cwe_map.json) — Exposure of Sensitive Information to an Unauthorized Actor.
- Hechos ancla: H5

## R6
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.8**
- Fundamento: Parche de seguridad 2026-09-01 (~2 meses): la gestion de vulnerabilidades tecnicas cubre la actualizacion oportuna de plataforma; A.8.8 consta y cruza LEY-21663.
- Hechos ancla: H1

## R7
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.8**
- Fundamento: Version 2.26.42.74 del 2026-10-28 con auto-actualizacion: gestion de vulnerabilidades del software instalado; A.8.8.
- Hechos ancla: H2

## R8
- Marco: ISO/IEC 27001 — versión 2022 — identificador **A.8.24**
- Fundamento: cleartextTrafficPermitted=true en base-config y CA de usuario con overridePins=true: el uso de criptografia exige proteger la confidencialidad e integridad en transito; A.8.24 consta y cruza LEY-21719.
- CWE sugerido: CWE-319 (confirmado en cwe_map.json) — Cleartext Transmission of Sensitive Information.
- Hechos ancla: H8

## Obligaciones legales (fichas)
- **Ley 21.663 (Marco de Ciberseguridad, Chile)** (exigible) — artículo: Art. 2 (sujetos: Servicios Esenciales) y Art. 8 (obligaciones de OIV); deberes generales de gestión continua de riesgos — consulta: 2026-10-29 — fundamento: No aplicable de manera directa: el dispositivo auditado es personal y su titular no es Servicio Esencial (Art. 2) ni OIV calificado por ANCI (Arts. 6 y 8). Se cita como marco de referencia para la gestión continua de riesgos (R6/R7) sin que ello constituya obligación legal del titular. Una vulnerabilidad no acredita por sí sola incumplimiento legal.
- **Ley 21.719 (Protección de Datos Personales, Chile)** (preparación (publicada el 13-12-2024; vigencia diferida — verificar a la fecha de ejecución)) — artículo: Art. 2 letras f) y g) (dato personal y sensible); Art. 14 quinquies (medidas técnicas y organizativas de seguridad); Art. 15 ter (EIPD en tratamiento sistemático de datos sensibles). Exclusión de ámbito puramente personal/familiar: VALIDAR — consulta: 2026-10-29 — fundamento: Aplicabilidad indirecta: el titular procesa sus propios datos; los datos de terceros (contactos, chats en WhatsApp) los trata el responsable de la plataforma (WhatsApp LLC). La auditoría no recolectó datos personales (el alcance lo prohibió). Art. 14 quinquies sustenta el criterio de cifrado de R4/R8 (CWE-312/CWE-319); la EIPD no aplica al titular personal salvo tratamiento sistemático a terceros.