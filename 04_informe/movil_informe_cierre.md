# Cierre de la auditoría móvil — Dispositivo personal + WhatsApp Business (com.whatsapp.w4b)

**Estado**: FIRMADO el 2026-10-29T01:58:05Z (registro `.firma.json` por archivo). Plantilla: `PLANTILLA_CIERRE_C4A.md`.

## 1. Identificación y autorización

- Encargo: autouditoría del dispositivo móvil personal del auditor y su aplicación WhatsApp.
- Organización: titular personal del activo (laboratorio controlado).
- Auditor y firmante: Cristóbal Herrera <herrera.jara.cristobal@gmail.com>.
- Fecha de ejecución: 2026-10-29 (UTC). Run de evidencia: `evidence/RUN-20261029T003246Z-3802`.
- Alcance y autorización: `scope/alcance_movil.md` firmado (`alcance_movil.firma.json`); ajuste evidenciado: el paquete real es `com.whatsapp.w4b` (WhatsApp Business).
- Exclusiones: tráfico de red/TLS, ejecución dinámica, datos de chats/cuentas/terceros, otros paquetes del dispositivo (salvo inventario), sistemas ajenos al dispositivo.
- Huella del APK analizado: `5b1bdcad6e615a4488aba59c381add57932fd48b75bd5f96fa1ba0407e064151`.

## 2. Resumen ejecutivo

Objetivo: medir los riesgos del WhatsApp Business instalado en el teléfono personal del auditor, con método de solo lectura (ADB + REA + análisis estático) y evidencia verificable.

Resultado sustentado: la **plataforma del dispositivo está sólida** (bootloader bloqueado, verified boot green, dm-verity enforcing, cifrado FBE, Play Protect activo) y la **autenticidad del APK está confirmada** (firmas v2/v3/v3.1 con rotación; certificado WhatsApp con huella coincidente con fuente pública; instalación y actualización por Play Store). Se identificaron **8 riesgos** (R1–R8): los prioritarios son la superficie de componentes exportados sin permiso (R1), la configuración de red global (R8) y la función de instalación de paquetes (R3).

Decisiones solicitadas: (a) revisar los permisos sensibles «solo con la app en uso»; (b) no instalar CA de usuario salvo necesidad transitoria; (c) mantener auto-actualización SO + app. Limitaciones: sin tráfico de red ni análisis dinámico por diseño del alcance; validación legal pendiente en un artículo (Ley 21.719).

## 3. Criterios y cobertura

- ISO/IEC 27001:2022 (Anexo A): 4 controles citados (A.8.24, A.8.3, A.8.8, A.8.9); identificadores constan en `platform/c4a/knowledge/`. Citas propuestas: 8 (una por riesgo R1–R8).
- NIST CSF 2.0: 6 funciones; con material: 5 de 6 (Responder queda «no consta»: sin hechos medibles en equipo personal).
- CIS Controls v8.1: 9 controles seleccionados de 18, con justificación anclada en hechos (H1–H8).
- Obligaciones legales: Ley 21.663 (arts. 2, 6, 8 — no aplica directamente, marco de referencia) y Ley 21.719 (arts. 2 f/g, 14 quinquies, 15 ter — aplicabilidad indirecta). VALIDAR: artículo de exclusión de ámbito personal en Ley 21.719.
- Regla de separación (principio II): resultado técnico, cumplimiento y aprobación son dimensiones independientes; los niveles de cumplimiento de la sección 4 son **propuestas** fundamentadas, no dictámenes del estándar.

## 4. Evaluación por control

Herramientas y versiones: REA `rea-agents@6.8.0` con `jadx-headless-mcp 0.7.1` (huella verificada), adb 37.0.1, analizador propio `platform/tools/`. Evidencia: 29 archivos con SHA-256 en `evidence/RUN-20261029T003246Z-3802/SHA256SUMS.txt` (verificación OK).

### R1 — A.8.9 (ISO/IEC 27001 2022)
- Aplicabilidad: 65 componentes exportados sin permiso (51 con intent-filter): la gestion de la configuracion exige endurecer la superficie expuesta; A.8.9 consta en la base de conocimiento.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-926 (pendiente de confirmar).
- Cumplimiento **propuesto**: **parcial** — superficie exportada amplia sin permiso (65 componentes, 51 alcanzables); la configuración está endurecida en dominios clave pero la superficie IPC/deeplink queda expuesta a apps del equipo.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R2 — A.8.3 (ISO/IEC 27001 2022)
- Aplicabilidad: Permisos sensibles concedidos (ubicacion precisa, microfono, camara, contactos, medios): la restriccion de acceso a la informacion limita la exposicion; A.8.3 consta en la base.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-250 (confirmado en cwe_map.json).
- Cumplimiento **propuesto**: **parcial** — permisos sensibles concedidos por decisión del usuario; restricciones aplicadas a SMS/llamadas/legacy storage.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R3 — A.8.9 (ISO/IEC 27001 2022)
- Aplicabilidad: REQUEST_INSTALL_PACKAGES declarado: la configuracion segura restringe funciones de instalacion; A.8.9 consta en la base.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-494 (confirmado en cwe_map.json).
- Cumplimiento **propuesto**: **parcial** — función de instalación de paquetes declarada; su abuso depende de flujos internos no verificados.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R4 — A.8.24 (ISO/IEC 27001 2022)
- Aplicabilidad: Backup: la app excluye todo su almacen y exige capacidad de cifrado (disableIfNoEncryptionCapabilities); el uso de criptografia protege lo respaldado; A.8.24 consta en la base.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-312 (confirmado en cwe_map.json).
- Cumplimiento **propuesto**: **cumple** — las reglas de backup y transferencia excluyen todo el almacén de la app y exigen capacidad de cifrado; residual: cifrado del dispositivo medido (FBE).
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R5 — A.8.3 (ISO/IEC 27001 2022)
- Aplicabilidad: requestLegacyExternalStorage activo: la restriccion de acceso a la informacion cubre la superficie de almacenamiento amplificada; mitigado por denegaciones de runtime (H5).
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-200 (confirmado en cwe_map.json).
- Cumplimiento **propuesto**: **parcial** — almacenamiento legacy declarado pero mitigado por denegaciones de runtime.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R6 — A.8.8 (ISO/IEC 27001 2022)
- Aplicabilidad: Parche de seguridad 2026-09-01 (~2 meses): la gestion de vulnerabilidades tecnicas cubre la actualizacion oportuna de plataforma; A.8.8 consta y cruza LEY-21663.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- Cumplimiento **propuesto**: **cumple** — bootloader bloqueado, verified boot green, verity enforcing, parche 2026-09-01 dentro de cadencia del fabricante.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R7 — A.8.8 (ISO/IEC 27001 2022)
- Aplicabilidad: Version 2.26.42.74 del 2026-10-28 con auto-actualizacion: gestion de vulnerabilidades del software instalado; A.8.8.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- Cumplimiento **propuesto**: **cumple** — versión 2.26.42.74 vigente (2026-10-28) con auto-actualización por Play.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

### R8 — A.8.24 (ISO/IEC 27001 2022)
- Aplicabilidad: cleartextTrafficPermitted=true en base-config y CA de usuario con overridePins=true: el uso de criptografia exige proteger la confidencialidad e integridad en transito; A.8.24 consta y cruza LEY-21719.
- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.
- Evidencia: `evidence/RUN-20261029T003246Z-3802/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, rea/06_analisis_propio.json, rea/07_firma_certificados.json, raw/postura_dispositivo.txt) con huellas en MANIFEST.json.
- CWE: CWE-319 (confirmado en cwe_map.json).
- Cumplimiento **propuesto**: **parcial** — cifrado fuerte en dominios de mensajería (pin-set 20+) pero base-config cleartext y CA de usuario con override de pins.
- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.
- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).

## 5. Remediación y seguimiento

Ver `movil_plan_remediacion.md` (ordenado por prioridad combinada). No se inventan responsables ni fechas: las sugeridas son del titular del activo y modificables. Issues del Project #7: no creados (ejercicio personal; el repositorio remite si se escala).

## 6. Cierre y anexos

Dictamen limitado al alcance y a la fecha: el dispositivo y la aplicación objetivo no presentan riesgos críticos en lo verificado; los riesgos R1, R2, R3, R5 y R8 son gestionables por configuración y hábitos del titular. Riesgos residuales: ventana de parche (~2 meses), confianza en el proveedor de la plataforma y de la app.

Pendientes declarados: (1) VALIDAR artículo de exclusión personal, Ley 21.719; (2) triaje fino de R1 sobre decompilación jadx (evidencia disponible); (3) push a origin (decisión del dueño).

Anexos: `movil_matriz_cumplimiento.md`; mapa HTML recorrible `movil_mapa.html` (índice de evidencia en `evidence/RUN-20261029T003246Z-3802/MANIFEST.json`); productos S03–S06 firmados en `03_hallazgos/`.
