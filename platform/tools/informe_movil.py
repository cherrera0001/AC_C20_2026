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
    L.append("Anexos: `movil_matriz_cumplimiento.md`; índice de evidencia en "
             f"`{RUN}/MANIFEST.json`; productos S03–S06 firmados en `03_hallazgos/`.")
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
              "movil_frase_gerencia", "movil_frase_tecnica"):
        p = out / f"{n}.md"
        f = json.loads((out / f"{n}.md.firma.json").read_text(encoding="utf-8"))
        if hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256_bytes_firmados"]:
            ok = False
            print("FALLA FIRMA:", n)
    print("VERIFICACION FIRMAS:", "OK" if ok else "FALLA")


if __name__ == "__main__":
    main()
