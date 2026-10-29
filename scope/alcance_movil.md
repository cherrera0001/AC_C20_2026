# Alcance — Objetivo «Dispositivo móvil personal y aplicación WhatsApp» (borrador)

**Estado**: AUTORIZADO por el auditor responsable en sesión (2026-10-28); **FIRMADO** por el
auditor el 2026-10-29 — registro en `alcance_movil.firma.json` (firmante + fecha + huella
SHA-256 de estos bytes).
**No sustituye** a `scope/alcance.md` ni a `scope/alcance_curso_848.md`.

**Autorización registrada**: Cristóbal Herrera, auditor responsable, indica por escrito en la
sesión que el entorno es controlado, que él es responsable de la auditoría y que autoriza
continuar con el proceso (instalación de `adb`, descarga verificada de `jadx-headless-mcp` 0.7.1
y análisis estático del APK de WhatsApp Business del dispositivo propio).

**Ventana de trabajo**: 2026-10-28 hasta el cierre de esta auditoría.

**Firma del auditor**: `_____Cristóbal Herrera firma y autoriza la operación_______` (pendiente — la completa el auditor).

## 1. Activo

| Campo | Valor |
|---|---|
| Tipo / rol | Teléfono móvil personal del auditor (Android) |
| Aplicación objetivo | WhatsApp Business (`com.whatsapp.w4b`), instalada en ese mismo dispositivo |
| Serie del dispositivo | pendiente (se registra al conectar; no se versiona) |

## 2. Dominios incluidos (in-scope)

1. **Inventario local del dispositivo**: paquetes instalados, permisos declarados de WhatsApp.
2. **Extracción local del APK base de WhatsApp** desde el dispositivo del auditor (`adb pull`), solo lectura del sistema de archivos del paquete.
3. **Análisis estático offline** del APK extraído con REA: firma y certificados, manifiesto, permisos, componentes exportados, recursos y cadenas. Sin ejecutar la app.

## 4. Método permitido (sin tráfico activo)

- Solo lectura vía ADB (`list`, `resolve`, `pull` del APK base).
- Análisis estático local del binario extraído (REA `inspect_apk_signature`, análisis de manifiesto y recursos).
- Hash SHA-256 de cada artefacto antes y después del análisis.

## 3. Exclusiones (out-of-scope)

- Tráfico de red de la app, interceptación TLS o proxy sobre WhatsApp.
- Eludir cifrado end-to-end, autenticación, licencias o protecciones del cliente.
- Extraer o leer chats, bases de datos, cuentas, contactos, medios o datos personales de terceros.
- Modificar, reinstalar, re-empaquetar o ejecutar la app; instrumentación (Frida) sobre la app en vivo.
- Otros paquetes del dispositivo fuera de WhatsApp (salvo inventario de permisos del sistema).
- Cualquier sistema ajeno al dispositivo del auditor.

## 5. Pendientes

- P1: firma manual del auditor (campo arriba).
- P2: cerrado — dispositivo `a525a763` conectado y reconocido por `adb`.
- P3: reinicio de Claude Code para que REA lea `REA_ADB_PATH` y `REA_JADX_MCP_JAR`.

_Ruta de adb verificada: `C:\Users\herre\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe` (v1.0.41)._
