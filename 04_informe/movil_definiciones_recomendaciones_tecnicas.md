# Definiciones y recomendaciones para el equipo técnico — auditoría móvil

**Ejecución:** RUN-20261029T003246Z-3802 · 2026-10-29. Documento técnico complementario del informe de cierre: define cada concepto medido y entrega la recomendación concreta con su evidencia verificable.

## Glosario de términos medidos

- **Componente exportado**: pieza de la app (activity, service, receiver, provider) que otras apps del equipo pueden invocar. Sin permiso asociado, cualquier app instalada la alcanza.
- **Intent-filter**: declaración de qué intents (acciones) atiende un componente; con filtro, el componente es alcanzable por intents implícitos.
- **Permisos runtime**: permisos Android de la categoría «peligrosa» que el usuario concede o deniega por app (ubicación, micrófono, cámara, contactos…).
- **Network Security Config**: política TLS de la app: qué dominios exigen cifrado, qué certificados se confían (sistema/usuario) y qué certificados se anclan (pin-set).
- **Cleartext**: tráfico HTTP sin cifrar. `cleartextTrafficPermitted=true` lo permite.
- **Pin-set / overridePins**: anclaje de certificados de un dominio; `overridePins=true` en un trust-anchor permite que ese certificado lo anule un CA instalado por el usuario.
- **Firmas APK v2/v3/v3.1**: esquemas de firma de Android; v3.1 añade rotación de claves. Su presencia con certificado correcto acredita autenticidad e integridad.
- **Verified boot / dm-verity / FBE**: arranque verificado (green), verificación de bloques del sistema (enforcing) y cifrado basado en archivos del almacenamiento.
- **Play Protect**: verificación de apps de Google: analiza APKs antes y después de la instalación.

## Riesgos: definición, constatación y recomendación

### R1 — Superficie exportada sin permiso
- **Definición**: componentes de la app invocables por otras apps sin control de acceso por permiso.
- **Constatado**: 65 exportados sin permiso, 51 con intent-filter; notables: receivers de OTP (OtpRequestedReceiver, OtpIdentityHashRequestedReceiver), WebLoginResultHandlerActivity, TpalOAuthRedirectActivity, SmbLinkingService, InstrumentationService.
- **Recomendación técnica**: Triar los componentes señalados sobre la decompilación jadx ya disponible (evidence/RUN-20261029T003246Z-3802/rea/05_inspect_apk.json): buscar validaciones de emisor (getCallingPackage, signature check). Si faltan, reportar a Meta. Re-ejecutar el triaje con un agente explore por lotes; evidencia: rea/06_analisis_propio.json, raw/dumpsys_com.whatsapp.w4b.txt.

### R2 — Permisos sensibles concedidos
- **Definición**: la app accede a ubicación precisa, micrófono, cámara, contactos y medios del equipo.
- **Constatado**: Concedidos por el usuario; denegados SMS, llamadas, registro de llamadas y almacenamiento legacy.
- **Recomendación técnica**: Ajustes → Permisos: ubicación y micrófono en «solo con la app en uso» si el flujo de negocio lo permite; revisar contactos y medios. Evidencia: raw/dumpsys_com.whatsapp.w4b.txt.

### R3 — REQUEST_INSTALL_PACKAGES
- **Definición**: permiso que permite a la app iniciar la instalación de otros APK.
- **Constatado**: Declarado en el manifiesto (rea/06_analisis_propio.json).
- **Recomendación técnica**: En decompilación, localizar los PendingIntent de instalación y confirmar que van acompañados del prompt del sistema. Política de uso: aceptar solo instalaciones esperadas. Monitorear con Play Protect activo (postura medida: activo).

### R4 — Backup (riesgo cerrado)
- **Definición**: respaldo de datos de la app por Android (nube o transferencia a otro equipo).
- **Constatado**: full_backup_content.xml y data_extraction_rules.xml excluyen todo el almacén de la app; cifrado FBE activo en el equipo.
- **Recomendación técnica**: Sin acción. Verificación periódica tras actualizaciones de la app (las reglas pueden cambiar): re-extraer los XML con el parser (platform/tools/analisis_apk_propio.py).

### R5 — Legacy external storage
- **Definición**: modo de almacenamiento compartido heredado que amplía el acceso a archivos.
- **Constatado**: requestLegacyExternalStorage=true en manifiesto; mitigado por denegaciones de runtime.
- **Recomendación técnica**: Sin acción inmediata; monitorear que las denegaciones se mantengan tras actualizaciones.

### R6 — Parche de plataforma (residual bajo)
- **Definición**: antigüedad del último parche de seguridad del sistema operativo.
- **Constatado**: Parche 2026-09-01 (~2 meses), verified boot green, dm-verity enforcing, bootloader bloqueado (raw/postura_dispositivo.txt).
- **Recomendación técnica**: Mantener auto-actualización del SO; verificar el parche mensualmente con platform/tools/postura_dispositivo.sh tras reconectar el equipo.

### R7 — Versión de la aplicación
- **Definición**: exposición a vulnerabilidades conocidas ya corregidas por el fabricante de la app.
- **Constatado**: v2.26.42.74 del 2026-10-28, instalada y actualizada por Google Play; firma verificada (certificados Brian Acton/WhatsApp LLC, huella coincidente con fuente pública).
- **Recomendación técnica**: Mantener auto-actualización por Play; ante CVEs públicos de WhatsApp, confirmar que la versión instalada es posterior al parche (versionCode en raw/dumpsys_com.whatsapp.w4b.txt).

### R8 — Configuración de red (cleartext y CA de usuario)
- **Definición**: política TLS global de la app y confianza en certificadores del usuario.
- **Constatado**: base-config cleartextTrafficPermitted=true; trust-anchors incluye CA de usuario con overridePins=true; dominios WhatsApp con cleartext=false y pin-set (20+ SHA-256) (rea/xml_seguridad/network_security_config.xml).
- **Recomendación técnica**: No instalar CA de usuario salvo necesidad transitoria (proxy corporativo) y eliminarlos al terminar; verificar Ajustes → Seguridad → Credenciales de usuario. Si el alcance futuro autoriza tráfico, complementar con la skill net-pcap-analisis sobre una captura del equipo (hoy fuera de alcance).

## Recomendaciones transversales al equipo técnico

- Reutilizar la cadena de adquisición: `platform/tools/auditoria_movil_wsp.sh` (adquisición + custodia) y `postura_dispositivo.sh` (postura al reconectar); ambas regeneran SHA256SUMS y MANIFEST.
- Todo resultado se firma con `.firma.json` (firmante + fecha + huella SHA-256); verificar antes de presentar: recalcular el hash del archivo contra su registro de firma.
- Sincronización con GitHub: fetch → inspeccionar archivos remotos → rebase → verificar firmas y suite de pruebas (`python -m unittest discover -s platform/tests`) → push fast-forward, sin `--force`.
- La evidencia cruda no se versiona (`evidence/` está en `.gitignore`); se versionan productos, firmas y herramientas.

Evidencia de referencia: evidence/RUN-20261029T003246Z-3802/ (MANIFEST.json con 29 archivos verificados).
