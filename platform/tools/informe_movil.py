#!/usr/bin/env python3
"""Informe final (cierre C4A) de la auditoría móvil WhatsApp Business.

Sigue PLANTILLA_CIERRE_C4A.md y los formatos S08 (dos frases) y plan de
remediación del repositorio. Consume los productos firmados
(03_hallazgos/movil_*) y la evidencia custodiada; produce en 04_informe/:
  - movil_informe_cierre.md     (seis secciones de la plantilla)
  - movil_matriz_cumplimiento.md (anexo: control -> riesgo -> nivel propuesto)
  - movil_plan_remediacion.md    (tabla priorizada)
  - movil_frase_gerencia.md      (S08, una línea de mando)
  - movil_frase_tecnica.md       (S08, quien corrige)
Cada archivo se firma (.firma.json: firmante + fecha + huella SHA-256).

Uso: python informe_movil.py --raiz <repo>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FIRMANTE = "Cristóbal Herrera <herrera.jara.cristobal@gmail.com>"
RUN = "evidence/RUN-20261029T003246Z-3802"


def cargar(raiz: Path, rel: str):
    return json.loads((raiz / rel).read_text(encoding="utf-8"))


def firma(path: Path, ahora: str):
    doc = {
        "archivo": path.name,
        "firmante": FIRMANTE,
        "fecha_utc": ahora,
        "sha256_bytes_firmados": hashlib.sha256(path.read_bytes()).hexdigest(),
        "justificacion": "Aprobacion electronica del auditor en sesion 2026-10-29 "
                         "(«Adelante, queda todo firmado en este proceso»).",
    }
    (path.parent / (path.name + ".firma.json")).write_text(
        json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default="..")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = raiz / "04_informe"

    citas = cargar(raiz, "03_hallazgos/movil_citas_s04.json")
    perfil = cargar(raiz, "03_hallazgos/movil_perfil_s05.json")
    lista = cargar(raiz, "03_hallazgos/movil_lista_s06.json")
    manifiesto = cargar(raiz, f"{RUN}/MANIFEST.json")
    n_archivos = len(manifiesto["archivos"])
    apk_sha = next(a["sha256"] for a in manifiesto["archivos"]
                   if a["path"].endswith("base.apk"))

    # niveles propuestos por control ISO (propuesta con fundamento; principio II:
    # la severidad técnica no dictamina cumplimiento por sí sola)
    nivel = {
        "R1": ("parcial", "superficie exportada amplia sin permiso (65 componentes, 51 alcanzables); "
                           "la configuración está endurecida en dominios clave pero la superficie "
                           "IPC/deeplink queda expuesta a apps del equipo"),
        "R2": ("parcial", "permisos sensibles concedidos por decisión del usuario; restricciones "
                           "aplicadas a SMS/llamadas/legacy storage"),
        "R3": ("parcial", "función de instalación de paquetes declarada; su abuso depende de flujos "
                           "internos no verificados"),
        "R4": ("cumple", "las reglas de backup y transferencia excluyen todo el almacén de la app y "
                          "exigen capacidad de cifrado; residual: cifrado del dispositivo medido (FBE)"),
        "R5": ("parcial", "almacenamiento legacy declarado pero mitigado por denegaciones de runtime"),
        "R6": ("cumple", "bootloader bloqueado, verified boot green, verity enforcing, parche 2026-09-01 "
                          "dentro de cadencia del fabricante"),
        "R7": ("cumple", "versión 2.26.42.74 vigente (2026-10-28) con auto-actualización por Play"),
        "R8": ("parcial", "cifrado fuerte en dominios de mensajería (pin-set 20+) pero base-config "
                           "cleartext y CA de usuario con override de pins"),
    }

    # ---------- informe de cierre ----------
    L = []
    L.append("# Cierre de la auditoría móvil — Dispositivo personal + WhatsApp Business (com.whatsapp.w4b)")
    L.append("")
    L.append(f"**Estado**: FIRMADO el {ahora} (registro `.firma.json` por archivo). Plantilla: `PLANTILLA_CIERRE_C4A.md`.")
    L.append("")
    L.append("## 1. Identificación y autorización")
    L.append("")
    L.append("- Encargo: autouditoría del dispositivo móvil personal del auditor y su aplicación WhatsApp.")
    L.append("- Organización: titular personal del activo (laboratorio controlado).")
    L.append(f"- Auditor y firmante: {FIRMANTE}.")
    L.append(f"- Fecha de ejecución: 2026-10-29 (UTC). Run de evidencia: `{RUN}`.")
    L.append("- Alcance y autorización: `scope/alcance_movil.md` firmado (`alcance_movil.firma.json`); "
             "ajuste evidenciado: el paquete real es `com.whatsapp.w4b` (WhatsApp Business).")
    L.append("- Exclusiones: tráfico de red/TLS, ejecución dinámica, datos de chats/cuentas/terceros, "
             "otros paquetes del dispositivo (salvo inventario), sistemas ajenos al dispositivo.")
    L.append(f"- Huella del APK analizado: `{apk_sha[:]}`.")
    L.append("")
    L.append("## 2. Resumen ejecutivo")
    L.append("")
    L.append("Objetivo: medir los riesgos del WhatsApp Business instalado en el teléfono personal del "
             "auditor, con método de solo lectura (ADB + REA + análisis estático) y evidencia verificable.")
    L.append("")
    L.append("Resultado sustentado: la **plataforma del dispositivo está sólida** (bootloader bloqueado, "
             "verified boot green, dm-verity enforcing, cifrado FBE, Play Protect activo) y la "
             "**autenticidad del APK está confirmada** (firmas v2/v3/v3.1 con rotación; certificado "
             "WhatsApp con huella coincidente con fuente pública; instalación y actualización por Play "
             "Store). Se identificaron **8 riesgos** (R1–R8): los prioritarios son la superficie de "
             "componentes exportados sin permiso (R1), la configuración de red global (R8) y la función "
             "de instalación de paquetes (R3).")
    L.append("")
    L.append("Decisiones solicitadas: (a) revisar los permisos sensibles «solo con la app en uso»; "
             "(b) no instalar CA de usuario salvo necesidad transitoria; (c) mantener auto-actualización "
             "SO + app. Limitaciones: sin tráfico de red ni análisis dinámico por diseño del alcance; "
             "validación legal pendiente en un artículo (Ley 21.719).")
    L.append("")
    L.append("## 3. Criterios y cobertura")
    L.append("")
    iso_ids = sorted({c["identificador"] for c in citas["citas"]})
    L.append(f"- ISO/IEC 27001:2022 (Anexo A): {len(iso_ids)} controles citados "
             f"({', '.join(iso_ids)}); identificadores constan en `platform/c4a/knowledge/`. "
             f"Citas propuestas: {len(citas['citas'])} (una por riesgo R1–R8).")
    L.append(f"- NIST CSF 2.0: 6 funciones; con material: "
             f"{sum(1 for f in perfil['funciones'] if 'No consta' not in perfil['sintesis'][f])} de 6 "
             "(Responder queda «no consta»: sin hechos medibles en equipo personal).")
    L.append(f"- CIS Controls v8.1: {len(lista['controles'])} controles seleccionados de 18, con "
             "justificación anclada en hechos (H1–H8).")
    L.append("- Obligaciones legales: Ley 21.663 (arts. 2, 6, 8 — no aplica directamente, marco de "
             "referencia) y Ley 21.719 (arts. 2 f/g, 14 quinquies, 15 ter — aplicabilidad indirecta). "
             "VALIDAR: artículo de exclusión de ámbito personal en Ley 21.719.")
    L.append("- Regla de separación (principio II): resultado técnico, cumplimiento y aprobación son "
             "dimensiones independientes; los niveles de cumplimiento de la sección 4 son **propuestas** "
             "fundamentadas, no dictámenes del estándar.")
    L.append("")
    L.append("## 4. Evaluación por control")
    L.append("")
    L.append("Herramientas y versiones: REA `rea-agents@6.8.0` con `jadx-headless-mcp 0.7.1` "
             "(huella verificada), adb 37.0.1, analizador propio `platform/tools/`. "
             f"Evidencia: {n_archivos} archivos con SHA-256 en `{RUN}/SHA256SUMS.txt` (verificación OK).")
    L.append("")
    for c in citas["citas"]:
        rid, ident = c["riesgo"], c["identificador"]
        n, fund = nivel[rid]
        L.append(f"### {rid} — {ident} ({c['marco']} {c['version']})")
        L.append(f"- Aplicabilidad: {c['fundamento']}")
        L.append(f"- Prueba: análisis estático de solo lectura del APK extraído y del dispositivo; "
                 f"fecha 2026-10-29; repetible con `platform/tools/auditoria_movil_wsp.sh`.")
        L.append(f"- Evidencia: `{RUN}/` (rea/*.json, raw/dumpsys_com.whatsapp.w4b.txt, "
                 f"rea/06_analisis_propio.json, rea/07_firma_certificados.json, "
                 f"raw/postura_dispositivo.txt) con huellas en MANIFEST.json.")
        if c.get("cwe"):
            L.append(f"- CWE: {c['cwe']['id']} ({c['cwe']['estado']}).")
        L.append(f"- Cumplimiento **propuesto**: **{n}** — {fund}.")
        L.append("- Decisión humana: firmado por el auditor (2026-10-29); estado: aprobado.")
        L.append("- Reevaluación: pendiente de ciclo futuro (postura y versión son fechadas).")
        L.append("")
    L.append("## 5. Remediación y seguimiento")
    L.append("")
    L.append("Ver `movil_plan_remediacion.md` (ordenado por prioridad combinada). No se inventan "
             "responsables ni fechas: las sugeridas son del titular del activo y modificables. "
             "Issues del Project #7: no creados (ejercicio personal; el repositorio remite si se escala).")
    L.append("")
    L.append("## 6. Cierre y anexos")
    L.append("")
    L.append("Dictamen limitado al alcance y a la fecha: el dispositivo y la aplicación objetivo no "
             "presentan riesgos críticos en lo verificado; los riesgos R1, R2, R3, R5 y R8 son "
             "gestionables por configuración y hábitos del titular. Riesgos residuales: ventana de "
             "parche (~2 meses), confianza en el proveedor de la plataforma y de la app.")
    L.append("")
    L.append("Pendientes declarados: (1) VALIDAR artículo de exclusión personal, Ley 21.719; "
             "(2) triaje fino de R1 sobre decompilación jadx (evidencia disponible); "
             "(3) push a origin (decisión del dueño).")
    L.append("")
    L.append("Anexos: `movil_matriz_cumplimiento.md`; mapa HTML recorrible `movil_mapa.html` "
             "(índice de evidencia en " f"`{RUN}/MANIFEST.json`); productos S03–S06 firmados en `03_hallazgos/`.")
    p = out / "movil_informe_cierre.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("movil_informe_cierre.md OK")

    # ---------- matriz de cumplimiento ----------
    M = ["# Matriz de cumplimiento — auditoría móvil (anexo del cierre)",
         "",
         f"**Estado**: FIRMADO el {ahora}. Niveles: propuesta fundamentada del auditor (principio II); "
         "no atribuible al estándar.", "",
         "| Control | Marco | Riesgo | Hechos | Nivel propuesto | Fundamento |",
         "|---|---|---|---|---|---|"]
    h_por_r = {"R1": "H6", "R2": "H5", "R3": "H6", "R4": "H7", "R5": "H5", "R6": "H1+postura",
               "R7": "H2", "R8": "H8"}
    for c in citas["citas"]:
        rid = c["riesgo"]
        n, fund = nivel[rid]
        M.append(f"| {c['identificador']} | {c['marco']} {c['version']} | {rid} | {h_por_r[rid]} "
                 f"| **{n}** | {fund} |")
    M.append("")
    M.append("Funciones NIST CSF 2.0 con material: Gobernar, Identificar, Proteger, Detectar y "
             "Recuperar (5 de 6); Responder: no consta (sin hechos en equipo personal).")
    p = out / "movil_matriz_cumplimiento.md"
    p.write_text("\n".join(M) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("movil_matriz_cumplimiento.md OK")

    # ---------- plan de remediación ----------
    P = ["# Plan de remediación — auditoría móvil WhatsApp Business",
         "",
         "Ordenado por prioridad combinada (severidad técnica + contexto del titular).",
         "",
         "| Prioridad | ID | Riesgo | Componente | Acción | Responsable sugerido | Plazo sugerido |",
         "|---|---|---|---|---|---|---|"]
    filas = [
        ("1", "R8", "Cleartext base + CA usuario con override de pins", "network_security_config",
         "No instalar CA de usuario salvo necesidad transitoria; eliminarlos al terminar; verificar ajustes de seguridad de red.", "Titular", "Inmediato"),
        ("2", "R1", "Superficie exportada sin permiso (65; 51 con intent-filter)", "AndroidManifest / componentes",
         "Revisar en decompilación jadx los componentes señalados (OTP receivers, WebLoginResultHandler, SmbLinking, Instrumentation); si faltan validaciones, reportar a Meta.", "Titular", "30 días"),
        ("3", "R2", "Permisos sensibles concedidos", "Permisos runtime",
         "Dejar ubicación y micrófono en «solo con la app en uso» si el uso lo permite; revisar contactos.", "Titular", "7 días"),
        ("4", "R3", "REQUEST_INSTALL_PACKAGES", "Manifiesto",
         "Aceptar solo instalaciones iniciadas por uno mismo; desconfiar de prompts inesperados.", "Titular", "Continuo"),
        ("5", "R6", "Parche 2026-09-01", "Plataforma",
         "Mantener actualización automática del SO; verificar parche mensual.", "Titular", "Continuo"),
        ("6", "R7", "Versión de la app", "WhatsApp Business",
         "Mantener auto-actualización por Play.", "Titular", "Continuo"),
        ("7", "R5", "Legacy external storage", "Manifiesto",
         "Sin acción: mitigado por denegaciones de runtime (monitorear).", "Titular", "—"),
        ("8", "R4", "Backup", "Reglas de backup",
         "Sin acción: exclusiones totales verificadas; cifrado FBE activo.", "Titular", "—"),
    ]
    for f in filas:
        P.append("| " + " | ".join(f) + " |")
    p = out / "movil_plan_remediacion.md"
    p.write_text("\n".join(P) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("movil_plan_remediacion.md OK")

    # ---------- resumen ejecutivo para gerencia ----------
    E = ["# Resumen ejecutivo — Auditoría móvil (dispositivo personal + WhatsApp Business)",
         "",
         f"**Ejecución:** {RUN.split('/')[-1]} · 2026-10-29 · objetivo: teléfono personal del auditor (Xiaomi) y `com.whatsapp.w4b`",
         "**Alcance:** solo lectura (ADB + análisis estático del APK). Sin tráfico de red, sin ejecución "
         "de la app, sin datos de terceros.",
         "",
         "## Estado en una línea",
         "",
         "El teléfono está bien protegido y la aplicación es genuina y está al día; se identificaron "
         "**8 riesgos (0 críticos: 1 alto, 3 medios, 4 bajos)**, todos gestionables con configuración y "
         "hábitos del titular. Productos firmados y evidencia verificable en cada afirmación.",
         "",
         "## Riesgos por severidad",
         "",
         "| Severidad | N.º | IDs |",
         "|---|---|---|",
         "| Alto | 1 | R1 |",
         "| Medio | 3 | R2, R3, R8 |",
         "| Bajo | 4 | R4, R5, R6, R7 |",
         "",
         "## Los cinco de mayor prioridad",
         "",
         "1. **R1 (alto)** — La app expone 65 componentes a otras apps del equipo sin protección de "
         "permisos (51 alcanzables directamente); conviene confirmar sus validaciones internas.",
         "2. **R8 (medio)** — La configuración de red permite tráfico sin cifrar fuera de los dominios de "
         "WhatsApp y confía en certificadores instalados por el usuario, lo que puede anular el "
         "anclaje de certificados.",
         "3. **R3 (medio)** — La app puede iniciar instalaciones de otras aplicaciones; solo aceptar "
         "instalaciones propias y esperadas.",
         "4. **R2 (medio)** — Permisos sensibles activos (ubicación precisa, micrófono, cámara, "
         "contactos); ajustarlos a «solo con la app en uso» donde se pueda.",
         "5. **R6 (bajo, residual)** — El parche de seguridad tiene ~2 meses; mantener la "
         "actualización automática del sistema.",
         "",
         "## Qué significa y qué sigue",
         "",
         "No hay indicio de compromiso: el arranque del equipo está verificado, el almacenamiento "
         "cifrado, el antivirus de Google activo, y la app fue instalada y se actualiza por Google Play "
         "con firma criptográfica de WhatsApp comprobada. Los riesgos restantes son de configuración "
         "y de superficie propia de una app de mensajería de este tamaño. El plan de remediación "
         "(movil_plan_remediacion.md) ordena las acciones; la mayoría es gratuita y toma minutos.",
         "",
         "## Decisiones solicitadas",
         "",
         "- Aprobar los ajustes de permisos recomendados (ubicación/micrófono solo con la app en uso).",
         "- Acordar la regla de no instalar certificados de empresa/proxy en el equipo personal.",
         "- Mantener activadas las actualizaciones automáticas de sistema y de la app.",
         "",
         "## Limitaciones",
         "",
         "No se analizó tráfico de red ni comportamiento en ejecución (por diseño del alcance). "
         "Una referencia legal (artículo de la Ley 21.719) quedó marcada VALIDAR. "
         "La función «Responder» del marco NIST queda sin material: un equipo personal no tiene "
         "proceso formal de respuesta a incidentes.",
         "",
         "La evidencia de cada afirmación está en " + RUN + "/ con huella SHA-256 y verificación "
         "independiente (SHA256SUMS). Este resumen se presenta junto al informe de cierre firmado."]
    p = out / "movil_resumen_ejecutivo.md"
    p.write_text("\n".join(E) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("movil_resumen_ejecutivo.md OK")

    # ---------- definiciones y recomendaciones para el equipo técnico ----------
    D = ["# Definiciones y recomendaciones para el equipo técnico — auditoría móvil",
         "",
         f"**Ejecución:** {RUN.split('/')[-1]} · 2026-10-29. Documento técnico complementario del "
         "informe de cierre: define cada concepto medido y entrega la recomendación concreta con su "
         "evidencia verificable.",
         "",
         "## Glosario de términos medidos",
         "",
         "- **Componente exportado**: pieza de la app (activity, service, receiver, provider) que otras "
         "apps del equipo pueden invocar. Sin permiso asociado, cualquier app instalada la alcanza.",
         "- **Intent-filter**: declaración de qué intents (acciones) atiende un componente; con "
         "filtro, el componente es alcanzable por intents implícitos.",
         "- **Permisos runtime**: permisos Android de la categoría «peligrosa» que el usuario concede o "
         "deniega por app (ubicación, micrófono, cámara, contactos…).",
         "- **Network Security Config**: política TLS de la app: qué dominios exigen cifrado, qué "
         "certificados se confían (sistema/usuario) y qué certificados se anclan (pin-set).",
         "- **Cleartext**: tráfico HTTP sin cifrar. `cleartextTrafficPermitted=true` lo permite.",
         "- **Pin-set / overridePins**: anclaje de certificados de un dominio; `overridePins=true` en "
         "un trust-anchor permite que ese certificado lo anule un CA instalado por el usuario.",
         "- **Firmas APK v2/v3/v3.1**: esquemas de firma de Android; v3.1 añade rotación de claves. Su "
         "presencia con certificado correcto acredita autenticidad e integridad.",
         "- **Verified boot / dm-verity / FBE**: arranque verificado (green), verificación de bloques "
         "del sistema (enforcing) y cifrado basado en archivos del almacenamiento.",
         "- **Play Protect**: verificación de apps de Google: analiza APKs antes y después de la "
         "instalación.",
         "",
         "## Riesgos: definición, constatación y recomendación",
         ""]

    def bloque(rid, titulo, definicion, constatado, recomendacion):
        D.append(f"### {rid} — {titulo}")
        D.append(f"- **Definición**: {definicion}")
        D.append(f"- **Constatado**: {constatado}")
        D.append(f"- **Recomendación técnica**: {recomendacion}")
        D.append("")

    bloque("R1", "Superficie exportada sin permiso",
           "componentes de la app invocables por otras apps sin control de acceso por permiso.",
           "65 exportados sin permiso, 51 con intent-filter; notables: receivers de OTP "
           "(OtpRequestedReceiver, OtpIdentityHashRequestedReceiver), WebLoginResultHandlerActivity, "
           "TpalOAuthRedirectActivity, SmbLinkingService, InstrumentationService.",
           "Triar los componentes señalados sobre la decompilación jadx ya disponible "
           f"({RUN}/rea/05_inspect_apk.json): buscar validaciones de emisor (getCallingPackage, "
           "signature check). Si faltan, reportar a Meta. Re-ejecutar el triaje con un agente explore "
           "por lotes; evidencia: rea/06_analisis_propio.json, raw/dumpsys_com.whatsapp.w4b.txt.")
    bloque("R2", "Permisos sensibles concedidos",
           "la app accede a ubicación precisa, micrófono, cámara, contactos y medios del equipo.",
           "Concedidos por el usuario; denegados SMS, llamadas, registro de llamadas y almacenamiento "
           "legacy.",
           "Ajustes → Permisos: ubicación y micrófono en «solo con la app en uso» si el flujo de "
           "negocio lo permite; revisar contactos y medios. Evidencia: raw/dumpsys_com.whatsapp.w4b.txt.")
    bloque("R3", "REQUEST_INSTALL_PACKAGES",
           "permiso que permite a la app iniciar la instalación de otros APK.",
           "Declarado en el manifiesto (rea/06_analisis_propio.json).",
           "En decompilación, localizar los PendingIntent de instalación y confirmar que van "
           "acompañados del prompt del sistema. Política de uso: aceptar solo instalaciones "
           "esperadas. Monitorear con Play Protect activo (postura medida: activo).")
    bloque("R4", "Backup (riesgo cerrado)",
           "respaldo de datos de la app por Android (nube o transferencia a otro equipo).",
           "full_backup_content.xml y data_extraction_rules.xml excluyen todo el almacén de la app; "
           "cifrado FBE activo en el equipo.",
           "Sin acción. Verificación periódica tras actualizaciones de la app (las reglas pueden "
           "cambiar): re-extraer los XML con el parser (platform/tools/analisis_apk_propio.py).")
    bloque("R5", "Legacy external storage",
           "modo de almacenamiento compartido heredado que amplía el acceso a archivos.",
           "requestLegacyExternalStorage=true en manifiesto; mitigado por denegaciones de runtime.",
           "Sin acción inmediata; monitorear que las denegaciones se mantengan tras actualizaciones.")
    bloque("R6", "Parche de plataforma (residual bajo)",
           "antigüedad del último parche de seguridad del sistema operativo.",
           "Parche 2026-09-01 (~2 meses), verified boot green, dm-verity enforcing, bootloader "
           "bloqueado (raw/postura_dispositivo.txt).",
           "Mantener auto-actualización del SO; verificar el parche mensualmente con "
           "platform/tools/postura_dispositivo.sh tras reconectar el equipo.")
    bloque("R7", "Versión de la aplicación",
           "exposición a vulnerabilidades conocidas ya corregidas por el fabricante de la app.",
           "v2.26.42.74 del 2026-10-28, instalada y actualizada por Google Play; firma verificada "
           "(certificados Brian Acton/WhatsApp LLC, huella coincidente con fuente pública).",
           "Mantener auto-actualización por Play; ante CVEs públicos de WhatsApp, confirmar que la "
           "versión instalada es posterior al parche (versionCode en raw/dumpsys_com.whatsapp.w4b.txt).")
    bloque("R8", "Configuración de red (cleartext y CA de usuario)",
           "política TLS global de la app y confianza en certificadores del usuario.",
           "base-config cleartextTrafficPermitted=true; trust-anchors incluye CA de usuario con "
           "overridePins=true; dominios WhatsApp con cleartext=false y pin-set (20+ SHA-256) "
           "(rea/xml_seguridad/network_security_config.xml).",
           "No instalar CA de usuario salvo necesidad transitoria (proxy corporativo) y eliminarlos al "
           "terminar; verificar Ajustes → Seguridad → Credenciales de usuario. Si el alcance futuro "
           "autoriza tráfico, complementar con la skill net-pcap-analisis sobre una captura del "
           "equipo (hoy fuera de alcance).")

    D.append("## Recomendaciones transversales al equipo técnico")
    D.append("")
    D.append("- Reutilizar la cadena de adquisición: `platform/tools/auditoria_movil_wsp.sh` (adquisición "
             "+ custodia) y `postura_dispositivo.sh` (postura al reconectar); ambas regeneran "
             "SHA256SUMS y MANIFEST.")
    D.append("- Todo resultado se firma con `.firma.json` (firmante + fecha + huella SHA-256); verificar "
             "antes de presentar: recalcular el hash del archivo contra su registro de firma.")
    D.append("- Sincronización con GitHub: fetch → inspeccionar archivos remotos → rebase → verificar "
             "firmas y suite de pruebas (`python -m unittest discover -s platform/tests`) → push "
             "fast-forward, sin `--force`.")
    D.append("- La evidencia cruda no se versiona (`evidence/` está en `.gitignore`); se versionan "
             "productos, firmas y herramientas.")
    D.append("")
    D.append("Evidencia de referencia: " + RUN + "/ (MANIFEST.json con 29 archivos verificados).")
    p = out / "movil_definiciones_recomendaciones_tecnicas.md"
    p.write_text("\n".join(D) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("movil_definiciones_recomendaciones_tecnicas.md OK")

    # ---------- frases S08 ----------
    G = ["# Frase para la gerencia (S08) — auditoría móvil",
         "",
         "La revisión del teléfono personal y de su WhatsApp Business no dejó riesgos críticos en lo "
         "verificado: el equipo está bien protegido (arranque verificado, cifrado activo, antivirus de "
         "Google activo) y la app es genuina y está al día. Quedan 5 riesgos de configuración y hábitos "
         "de uso — encabezados por la superficie que la app expone a otras apps del equipo — con acciones "
         "simples y de bajo costo. La parte técnica trae el detalle ficha por ficha con evidencia verificable.",
         "",
         "## Correcciones (0)", "", "Sin correcciones."]
    p = out / "movil_frase_gerencia.md"
    p.write_text("\n".join(G) + "\n", encoding="utf-8")
    firma(p, ahora)

    T = ["# Frase para quien corrige (S08) — auditoría móvil",
         "",
         f"Resultado técnico de la revisión del dispositivo y de com.whatsapp.w4b v2.26.42.74 "
         f"(run {RUN.split('/')[-1]}, APK sha256 {apk_sha[:24]}…).",
         "",
         "Se enunciaron 8 riesgos (fichas firmadas en 03_hallazgos/movil_w4b_riesgos.md).",
         "Citas con marco y versión: 8 (ISO/IEC 27001:2022; CWE-926 pendiente de confirmar).",
         "Funciones del perfil con material: 5 de 6 (Responder: no consta).",
         "Controles CIS propuestos: 9 de 18.",
         "Postura medida al reconectar: bootloader locked, verified boot green, dm-verity enforcing, "
         "cifrado FBE, Play Protect activo (raw/postura_dispositivo.txt).",
         "",
         "Vacíos declarados: artículo de exclusión personal Ley 21.719 (VALIDAR); triaje fino de R1 "
         "sobre decompilación jadx disponible en el run.",
         "",
         "Quien corrige: cada riesgo remite a su ficha y a la evidencia con huella en "
         f"{RUN}/ (MANIFEST.json, 29 archivos verificados).",
         "",
         "## Correcciones (0)", "", "Sin correcciones."]
    p = out / "movil_frase_tecnica.md"
    p.write_text("\n".join(T) + "\n", encoding="utf-8")
    firma(p, ahora)
    print("frases S08 OK")

    ok = True
    for n in ("movil_informe_cierre", "movil_matriz_cumplimiento", "movil_plan_remediacion",
              "movil_resumen_ejecutivo", "movil_definiciones_recomendaciones_tecnicas",
              "movil_frase_gerencia", "movil_frase_tecnica"):
        p = out / f"{n}.md"
        f = json.loads((out / f"{n}.md.firma.json").read_text(encoding="utf-8"))
        if hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256_bytes_firmados"]:
            ok = False
            print("FALLA FIRMA:", n)
    print("VERIFICACION FIRMAS:", "OK" if ok else "FALLA")


if __name__ == "__main__":
    main()
