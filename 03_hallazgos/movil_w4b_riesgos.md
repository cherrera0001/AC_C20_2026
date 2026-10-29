# Hallazgos — Auditoría móvil: dispositivo personal + WhatsApp Business (borrador)

**Estado**: FIRMADO por el auditor el 2026-10-29 (registro en `movil_w4b_riesgos.firma.json`: firmante + fecha + huella SHA-256 de estos bytes).
**Alcance**: `scope/alcance_movil.md` con ajuste evidenciado: el paquete instalado es `com.whatsapp.w4b` (WhatsApp Business); `com.whatsapp` no consta instalado.
**Evidencia**: `evidence/RUN-20261029T003246Z-3802/` (SHA256SUMS.txt verificado: 24 archivos; MANIFEST.json; APK base + splits con digest SHA-256 REA).
**Método**: solo lectura ADB + REA (`rea-agents@6.8.0` + `jadx-headless-mcp 0.7.1`) + analizador propio (`platform/tools/analisis_apk_propio.py`, `firma_apk_extracto.py`). Sin tráfico de red, sin ejecución de la app, sin lectura de chats/bases de datos.

## Hechos verificados

| # | Hecho | Fuente (run) |
|---|---|---|
| H1 | Dispositivo Xiaomi `nezha` (2512BPNDAG), Android 17 (API 37), parche 2026-09-01, build user, `ro.debuggable=0` | `rea/01_inspect_adb_device.json` |
| H2 | `com.whatsapp.w4b` v2.26.42.74 (264207414), minSdk 23, targetSdk 36, instalador Play (`com.android.vending`), actualizada 2026-10-28 | `rea/03_inspect_whatsapp.json`, `raw/dumpsys_com.whatsapp.w4b.txt` |
| H3 | APK íntegro en extracción: base 160.177.062 bytes, sha256 `5b1bdcad…7151` + 2 splits, digests REA | `rea/04_pull_whatsapp.json`, SHA256SUMS |
| H4 | Firmas v2+v3+v3.1 con rotación. Certificados: `CN=Brian Acton, O=WhatsApp Inc.` (huella `39:87:D0:43:…`, coincide con base pública verificada) y `CN=WhatsApp LLC` RSA-2048 (`FB:92:0D:38:…`, 2024→2054) | `rea/07_firma_certificados.json` |
| H5 | Permisos runtime concedidos: ubicación precisa/gruesa, cámara, micrófono, contactos R/W, estado teléfono, medios (audio/imagen/video), notificaciones, biometría. Denegados: llamadas, registro llamadas, SMS, almacenamiento externo, Bluetooth/Nearby Wi-Fi | `raw/dumpsys_com.whatsapp.w4b.txt` |
| H6 | 1.192 componentes; 82 exportados (20 actividades, 28 aliases, 13 servicios, 18 receivers, 3 providers); 65 sin permiso, de los cuales 51 con intent-filter (alcanzables por intent implícito) | `rea/06_analisis_propio.json` |
| H7 | `full_backup_content.xml` y `data_extraction_rules.xml` excluyen **todo** (los 9 dominios, cloud-backup y device-transfer; `disableIfNoEncryptionCapabilities="true"`) | `rea/xml_seguridad/` |
| H8 | `network_security_config.xml`: base-config `cleartextTrafficPermitted="true"`; trust-anchors **user con `overridePins="true"`**; dominios WhatsApp/Meta con cleartext=false y pin-set (20+ SHA-256) | `rea/xml_seguridad/` |

## Riesgos (enunciado: condición → consecuencia → lo que falta)

**R1 — Superficie exportada amplia sin permiso (MEDIO-ALTO)**
65 componentes exportados sin `android:permission`; 51 alcanzables por intents implícitos. Notables por sensibilidad:
- `OtpRequestedReceiver` / `OtpIdentityHashRequestedReceiver` — acciones propias sin protección (`com.whatsapp.otp.OTP_REQUESTED`, `…ID_HASH_REQUESTED`).
- `fbusers.smb.weblogin.WebLoginResultHandlerActivity` y `deeplink.ui.TpalOAuthRedirectActivity` — BROWSABLE, manejan resultados de login/OAuth vía URL.
- `accountlinking.ipc.service.SmbLinkingService` — servicio IPC (wfl.OPERATION) sin permiso.
- `instrumentation.product.api.InstrumentationService` — API de instrumentación expuesta.
- `phoneid.PhoneIdRequestReceiver` (`com.facebook.GET_PHONE_ID`), `WAFbnsPreloadReceiver` (FBNS, categoría propia).
- `media.ExternalMediaManager$ExternalMediaStateReceiver` — acciones MEDIA_* (broadcasts del sistema no protegidos; vector histórico de spam/confusión).
- Resto funcional estándar: launcher (Main/Home/Conversation), deeplinks de chat/invitaciones/eventos, AppIcon01–14, share sheet, ContactPicker, Android Auto, widget, backup de Google (acciones de GMS).
*Consecuencia*: una app maliciosa del equipo puede invocar componentes internos; el impacto depende de validaciones internas (no constan — código cerrado). *Falta*: triaje por componente con análisis de las validaciones (decompilación jadx ya disponible en `rea/05_inspect_apk.json`).

**R2 — Permisos sensibles concedidos (MEDIO)**
Ubicación precisa, micrófono, cámara, contactos y medios activos. Es el modelo funcional de WhatsApp; el riesgo es de privacidad ante compromiso de la app o de la cuenta, y de exposición por ubicación en tiempo real. Mitigación ya aplicada por el auditor: SMS/llamadas/legacy storage denegados. *Falta*: revisar el uso «solo con la app en uso» de ubicación y micrófono (settings de permisos por uso en background — no consta).

**R3 — `REQUEST_INSTALL_PACKAGES` (MEDIO)**
Declarado en manifiesto. Vector clásico de malvertising si se abuse para iniciar instalaciones. *Falta*: confirmar en qué flujos se usa (decompilación) y si hay prompt de confirmación del sistema (lo habitual).

**R4 — Backup (BAJA → prácticamente cerrado)**
`allowBackup="true"` con `backupAgent` propio, pero H7 demuestra que backup y transfer excluyen todo el almacén de la app. Residual: comprobación de cifrado del dispositivo (no consta; medible con `ro.crypto.state` al reconectar).

**R5 — Almacenamiento legacy (BAJA)**
`requestLegacyExternalStorage="true"` + `preserveLegacyExternalStorage="true"` amplían superficie de datos en Android 17; mitigado por la denegación de `READ/WRITE_EXTERNAL_STORAGE` observada en H5.

**R6 — Parche de seguridad 2026-09-01 (BAJA-MEDIA)**
Ventana de ~2 meses respecto al parche más reciente; plataforma reciente (Android 17). *Falta*: estado de verified boot / bootloader / cifrado — `getprop` no se pudo medir (dispositivo se desconectó durante la corrida; comando preparado para reintento).

**R7 — CVEs conocidos de WhatsApp (BAJA)**
Versión 2.26.42.74 del 2026-10-28 (vigente). CVEs históricos críticos (p. ej. CVE-2022-36934, RCE en parser de video) afectan versiones antiguas. Riesgo residual bajo con auto-actualización activa.

**R8 — Configuración de red: cleartext global y CA de usuario con override de pins (MEDIO)**
H8: `base-config cleartextTrafficPermitted="true"` permite HTTP en claro fuera de los dominios configurados; `trust-anchors` confía en CA de usuario con `overridePins="true"`, lo que anula la eficacia del pin-set (20+ pins SHA-256 en dominios WhatsApp) frente a un CA instalado por el usuario (proxy corporativo, MITM con acceso físico). Los dominios de mensajería WhatsApp quedan bien cubiertos (cleartext=false + pins); el resto del tráfico de la app queda en el nivel base.

## Limitaciones declaradas

- El digest de contenido v2/v3 **no se re-derivó** con las construcciones clásicas (el APK usa formato v3.1 con rotación de claves). La autenticidad se sustenta en H4 (huella pública coincidente) + H2 (origen Play) + parse completo jadx (113.857 clases). Verificación independiente recomendada: `apksigner verify --print-certs base.apk`.
- Tráfico de red y comportamiento dinámico: fuera de alcance por diseño.
- Las validaciones internas de los componentes de R1 requieren lectura del código decompilado (disponible; no ejecutado aún).
- Estado de bootloader/verified boot/cifrado: pendiente de medición (dispositivo desconectado).

## Trazabilidad

Todo hecho citado es verificable contra los bytes custodiados: `cd evidence/RUN-20261029T003246Z-3802 && sha256sum -c SHA256SUMS.txt` (24 archivos OK al cierre de la corrida). Artefactos nuevos de esta fase: `rea/xml_seguridad/` (6 archivos) y el presente documento queda en `03_hallazgos/`.
