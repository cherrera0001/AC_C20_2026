#!/usr/bin/env python3
"""Cadena S04-S06 para la auditoria movil WhatsApp Business (com.whatsapp.w4b).

Consume los riesgos firmados (03_hallazgos/movil_w4b_riesgos.md, R1-R8) y las
bases de conocimiento del repositorio (platform/c4a/knowledge/) y propone:
  - S04 movil_citas_s04:    cada riesgo en un marco con nombre, version e identificador
  - S05 movil_perfil_s05:   el activo leido por las seis funciones del NIST CSF 2.0
  - S06 movil_lista_s06:    CIS Controls v8.1 aplicables anclados en hechos

Reglas respetadas (skill correlacion-cumplimiento):
  - Cita completa o nada: el identificador solo se propone si consta en la base de
    conocimiento; si no, queda "pendiente de confirmar" (p. ej. CWE-926 no esta en
    cwe_map.json y asi se declara).
  - Sugerencia != prueba; marco mencionado != marco implementado.
  - Obligaciones legales con ficha y articulo "VALIDAR" cuando no consta.
  - Productos separados de la auditoria del curso (sufijo movil_); la herramienta
    propone y el auditor firma (registro .firma.json por producto).

Uso: python correlacion_movil.py --raiz <repo>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FIRMANTE = "Cristóbal Herrera <herrera.jara.cristobal@gmail.com>"
JUSTIFICACION_FIRMA = (
    "Aprobacion electronica del auditor en sesion 2026-10-29 "
    "(«Adelante, queda todo firmado en este proceso»); huella SHA-256 de los bytes "
    "guardados; anulable con evento firma_anulada."
)

RIESGOS = [
    {
        "id": "R1", "hechos": ["H6"], "funciones": ["Proteger", "Identificar"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.9",
                 "fundamento": "65 componentes exportados sin permiso (51 con intent-filter): la "
                               "gestion de la configuracion exige endurecer la superficie expuesta; "
                               "A.8.9 consta en la base de conocimiento."},
        "cwe": {"id": "CWE-926", "estado": "pendiente de confirmar",
                "nota": "Improper Export of Android Application Components; no consta en "
                        "cwe_map.json, se propone sin confirmar."},
        "cis": ["4", "1"],
    },
    {
        "id": "R2", "hechos": ["H5"], "funciones": ["Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.3",
                 "fundamento": "Permisos sensibles concedidos (ubicacion precisa, microfono, "
                               "camara, contactos, medios): la restriccion de acceso a la "
                               "informacion limita la exposicion; A.8.3 consta en la base."},
        "cwe": {"id": "CWE-250", "estado": "confirmado en cwe_map.json",
                "nota": "Execution with Unnecessary Privileges; menor privilegio."},
        "cis": ["3", "6"],
    },
    {
        "id": "R3", "hechos": ["H6"], "funciones": ["Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.9",
                 "fundamento": "REQUEST_INSTALL_PACKAGES declarado: la configuracion segura "
                               "restringe funciones de instalacion; A.8.9 consta en la base."},
        "cwe": {"id": "CWE-494", "estado": "confirmado en cwe_map.json",
                "nota": "Download of Code Without Integrity Check; ajuste explicado: la "
                        "instalacion de paquetes sin verificacion adicional es el vector."},
        "cis": ["10"],
    },
    {
        "id": "R4", "hechos": ["H7"], "funciones": ["Recuperar", "Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.24",
                 "fundamento": "Backup: la app excluye todo su almacen y exige capacidad de "
                               "cifrado (disableIfNoEncryptionCapabilities); el uso de "
                               "criptografia protege lo respaldado; A.8.24 consta en la base."},
        "cwe": {"id": "CWE-312", "estado": "confirmado en cwe_map.json",
                "nota": "Cleartext Storage of Sensitive Information; cruzado por LEY-21719 "
                        "en el mapa (cifrado de datos)."},
        "cis": ["11"],
    },
    {
        "id": "R5", "hechos": ["H5"], "funciones": ["Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.3",
                 "fundamento": "requestLegacyExternalStorage activo: la restriccion de acceso "
                               "a la informacion cubre la superficie de almacenamiento "
                               "amplificada; mitigado por denegaciones de runtime (H5)."},
        "cwe": {"id": "CWE-200", "estado": "confirmado en cwe_map.json",
                "nota": "Exposure of Sensitive Information to an Unauthorized Actor."},
        "cis": ["3"],
    },
    {
        "id": "R6", "hechos": ["H1"], "funciones": ["Proteger", "Identificar"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.8",
                 "fundamento": "Parche de seguridad 2026-09-01 (~2 meses): la gestion de "
                               "vulnerabilidades tecnicas cubre la actualizacion oportuna de "
                               "plataforma; A.8.8 consta y cruza LEY-21663."},
        "cwe": None,
        "cis": ["7"],
    },
    {
        "id": "R7", "hechos": ["H2"], "funciones": ["Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.8",
                 "fundamento": "Version 2.26.42.74 del 2026-10-28 con auto-actualizacion: "
                               "gestion de vulnerabilidades del software instalado; A.8.8."},
        "cwe": None,
        "cis": ["7"],
    },
    {
        "id": "R8", "hechos": ["H8"], "funciones": ["Proteger"],
        "cita": {"marco": "ISO/IEC 27001", "version": "2022", "identificador": "A.8.24",
                 "fundamento": "cleartextTrafficPermitted=true en base-config y CA de usuario "
                               "con overridePins=true: el uso de criptografia exige proteger "
                               "la confidencialidad e integridad en transito; A.8.24 consta "
                               "y cruza LEY-21719."},
        "cwe": {"id": "CWE-319", "estado": "confirmado en cwe_map.json",
                "nota": "Cleartext Transmission of Sensitive Information."},
        "cis": ["4"],
    },
]

NORMATIVAS_LEGALES = [
    {"normativa": "Ley 21.663 (Marco de Ciberseguridad, Chile)", "estado": "exigible",
     "fuente_oficial": "BCN LeyChile: https://www.bcn.cl/leychile/navegar?idLey=21663 (texto oficial; sitio SPA en fecha de consulta — numeración de artículos verificada contra análisis doctrinal de Anguita Osorio, 2026-09-10)",
     "fecha_consulta": "2026-10-29", "articulo": "Art. 2 (sujetos: Servicios Esenciales) y Art. 8 (obligaciones de OIV); deberes generales de gestión continua de riesgos",
     "fundamento_aplicabilidad": "No aplicable de manera directa: el dispositivo auditado es personal y su titular no es Servicio Esencial (Art. 2) ni OIV calificado por ANCI (Arts. 6 y 8). Se cita como marco de referencia para la gestión continua de riesgos (R6/R7) sin que ello constituya obligación legal del titular. Una vulnerabilidad no acredita por sí sola incumplimiento legal."},
    {"normativa": "Ley 21.719 (Protección de Datos Personales, Chile)", "estado": "preparación (publicada el 13-12-2024; vigencia diferida — verificar a la fecha de ejecución)",
     "fuente_oficial": "BCN LeyChile: https://www.bcn.cl/leychile/navegar?idNorma=1209272 (texto oficial; sitio SPA en fecha de consulta — artículos verificados contra Prey 2026-06-03, Garrigues 04-2025 y repositorio UChile)",
     "fecha_consulta": "2026-10-29", "articulo": "Art. 2 letras f) y g) (dato personal y sensible); Art. 14 quinquies (medidas técnicas y organizativas de seguridad); Art. 15 ter (EIPD en tratamiento sistemático de datos sensibles). Exclusión de ámbito puramente personal/familiar: VALIDAR",
     "fundamento_aplicabilidad": "Aplicabilidad indirecta: el titular procesa sus propios datos; los datos de terceros (contactos, chats en WhatsApp) los trata el responsable de la plataforma (WhatsApp LLC). La auditoría no recolectó datos personales (el alcance lo prohibió). Art. 14 quinquies sustenta el criterio de cifrado de R4/R8 (CWE-312/CWE-319); la EIPD no aplica al titular personal salvo tratamiento sistemático a terceros."},
]

SINTESIS = {
    "Gobernar": "Consta para este ejercicio: alcance y hallazgos firmados (alcance_movil.firma.json, "
                "movil_w4b_riesgos.firma.json) con autorizacion y ventana. Politicas del titular del "
                "dispositivo fuera de este ejercicio: no consta.",
    "Identificar": "Inventario realizado: dispositivo (H1), aplicación y origen (H2), superficie "
                   "exportada medida (H6). Postura medida el 2026-10-29 (raw/postura_dispositivo.txt): "
                   "bootloader bloqueado (ro.boot.flash.locked=1), verified boot green, dm-verity "
                   "enforcing, cifrado de archivos (FBE) activo, build user no depurable.",
    "Proteger": "Concentra la mayor parte del material: R1-R3, R5-R8. Medidas activas observadas: "
                "pin-set (20+ SHA-256) y cleartext=false en dominios de mensajeria (H8), exclusion "
                "total de backups (H7), denegaciones de permisos por el usuario (H5), firma y origen "
                "Play verificados (H4). Cifrado del dispositivo (FBE) y verified boot reforzando la "
                "postura (medido 2026-10-29).",
    "Detectar": "Play Protect activo: package_verifier_user_consent=1 y upload_apk_enable=1 "
                "(verificacion de apps con envio de APKs a Google); el toggle legacy "
                "package_verifier_enable queda sin fijar (default). Medido el 2026-10-29 "
                "(raw/postura_dispositivo.txt). Monitoreo adicional del SO: no consta.",
    "Responder": "No consta: sin hechos sobre respuesta a incidentes del activo.",
    "Recuperar": "La app excluye todo su almacen de respaldo y transferencia (H7); cifrado del "
                 "dispositivo (FBE) activo, medido 2026-10-29. Copias a nivel SO fuera de alcance "
                 "del proveedor de la app: no consta.",
}

FUNCIONES = ("Gobernar", "Identificar", "Proteger", "Detectar", "Responder", "Recuperar")


def cargar_kb(raiz: Path):
    k = raiz / "platform" / "c4a" / "knowledge"
    return {
        "iso": json.loads((k / "controls_iso27001.json").read_text(encoding="utf-8")),
        "cis": json.loads((k / "controls_cis.json").read_text(encoding="utf-8")),
        "cwe": json.loads((k / "cwe_map.json").read_text(encoding="utf-8")),
        "norm": json.loads((k / "normativas.json").read_text(encoding="utf-8")),
    }


def verifica_identificadores(kb):
    """Valida que cada identificador ISO citado conste en la base; CWE segun mapa."""
    problemas = []
    for r in RIESGOS:
        ident = r["cita"]["identificador"]
        if ident not in kb["iso"]:
            problemas.append(f"{r['id']}: {ident} no consta en controls_iso27001.json")
        cwe = r.get("cwe")
        if cwe and cwe["id"] not in kb["cwe"] and "confirmado" in cwe["estado"]:
            problemas.append(f"{r['id']}: {cwe['id']} declarado confirmado pero no consta en cwe_map")
    return problemas


def firma(path: Path, ahora: str):
    doc = {
        "archivo": path.name,
        "firmante": FIRMANTE,
        "fecha_utc": ahora,
        "sha256_bytes_firmados": hashlib.sha256(path.read_bytes()).hexdigest(),
        "justificacion": JUSTIFICACION_FIRMA,
    }
    out = path.parent / (path.name + ".firma.json")
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc["sha256_bytes_firmados"]


def escribe(raiz: Path, nombre: str, contenido_json: dict, vista_md: str, ahora: str):
    hallazgos = raiz / "03_hallazgos"
    jp = hallazgos / f"{nombre}.json"
    mp = hallazgos / f"{nombre}.md"
    jp.write_text(json.dumps(contenido_json, indent=2, ensure_ascii=False), encoding="utf-8")
    mp.write_text(vista_md, encoding="utf-8")
    h1 = firma(jp, ahora)
    h2 = firma(mp, ahora)
    return h1, h2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default="..")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    kb = cargar_kb(raiz)

    problemas = verifica_identificadores(kb)
    if problemas:
        print("IDENTIFICADORES CON PROBLEMA:")
        for p in problemas:
            print(" -", p)
        sys.exit(1)

    # ---- S04 citas
    citas = {"producto": "S04 movil — La cita", "version_esquema": "1",
             "fuente": "03_hallazgos/movil_w4b_riesgos.md (firmado)", "citas": [], "normativas_legales": NORMATIVAS_LEGALES}
    md = ["# S04 (móvil) — La cita: riesgos ubicados en marco con versión e identificador",
          "",
          f"**Estado**: FIRMADO el {ahora} — registro en `movil_citas_s04.firma.json`. Propuesta de la herramienta; "
          "correspondencia = sugerencia explicada (principio II).",
          ""]
    for r in RIESGOS:
        citas["citas"].append({"riesgo": r["id"], "hechos": r["hechos"], **r["cita"],
                               "cwe": r.get("cwe")})
        md.append(f"## {r['id']}")
        md.append(f"- Marco: {r['cita']['marco']} — versión {r['cita']['version']} — identificador **{r['cita']['identificador']}**")
        md.append(f"- Fundamento: {r['cita']['fundamento']}")
        if r.get("cwe"):
            md.append(f"- CWE sugerido: {r['cwe']['id']} ({r['cwe']['estado']}) — {r['cwe']['nota']}")
        md.append(f"- Hechos ancla: {', '.join(r['hechos'])}")
        md.append("")
    md.append("## Obligaciones legales (fichas)")
    for nl in NORMATIVAS_LEGALES:
        md.append(f"- **{nl['normativa']}** ({nl['estado']}) — artículo: {nl['articulo']} — "
                  f"consulta: {nl['fecha_consulta']} — fundamento: {nl['fundamento_aplicabilidad']}")
    h = escribe(raiz, "movil_citas_s04", citas, "\n".join(md), ahora)
    print("movil_citas_s04", h[0][:16], h[1][:16])

    # ---- S05 perfil
    asignaciones = []
    for r in RIESGOS:
        for f in r["funciones"]:
            asignaciones.append({"riesgo": r["id"], "funcion": f,
                                 "fundamento": f"{r['id']} vive en {f}: {r['cita']['fundamento'][:110]}…"})
    perfil = {"producto": "S05 movil — El perfil", "version_esquema": "1",
              "fuente": "movil_citas_s04 (firmado)", "funciones": FUNCIONES,
              "asignaciones": asignaciones, "sintesis": SINTESIS}
    md = ["# S05 (móvil) — El perfil: el activo leído con las seis funciones del NIST CSF 2.0",
          "",
          f"**Estado**: FIRMADO el {ahora} — `movil_perfil_s05.firma.json`. Función sin material queda «no consta», "
          "nunca «sin hallazgos» (FR-06).",
          ""]
    for f in FUNCIONES:
        md.append(f"## {f}")
        rel = [a for a in asignaciones if a["funcion"] == f]
        if rel:
            for a in rel:
                md.append(f"- {a['riesgo']}: {a['fundamento']}")
        md.append(f"- Síntesis: {SINTESIS[f]}")
        md.append("")
    h = escribe(raiz, "movil_perfil_s05", perfil, "\n".join(md), ahora)
    print("movil_perfil_s05", h[0][:16], h[1][:16])

    # ---- S06 lista CIS
    anclas = {
        "1": "H1+H2+H6: inventario del dispositivo, la aplicación y su superficie exportada realizado y custodiado.",
        "2": "H2: versión exacta, instalador (Play) y fecha de actualización registrados; APK con digest verificado.",
        "3": "H5+H7: permisos sensibles concedidos/denegados y exclusión total de backups (datos protegidos por diseño de la app).",
        "4": "R1+R6+R8: superficie exportada sin permiso, parche 2026-09-01 y configuración de red (cleartext base, CA usuario con override de pins, pin-set en dominios clave).",
        "6": "H5: gestión de accesos del usuario — denegaciones de SMS/llamadas/legacy storage; biometría concedida.",
        "7": "R6+R7: parche de plataforma (~2 meses) y versión vigente de la app con auto-actualización.",
        "10": "R3: REQUEST_INSTALL_PACKAGES declarado — superficie a vigilar ante malvertising.",
        "11": "H7: alcance de respaldo — la app excluye todo su almacén en backup y transferencia.",
        "16": "R1+R8: seguridad de la aplicación — componentes exportados y configuración de red del APK analizados estáticamente.",
    }
    lista = {"producto": "S06 movil — La lista", "version_esquema": "1",
             "fuente": "movil_perfil_s05 (firmado) + inventario de la auditoría móvil",
             "controles": [{"id": cid, "titulo": kb["cis"][cid]["titulo"],
                            "justificacion": anclas[cid], "estado": "propuesto-firmado"}
                           for cid in anclas]}
    md = ["# S06 (móvil) — La lista: CIS Controls v8.1 aplicables, anclados en hechos",
          "",
          f"**Estado**: FIRMADO el {ahora} — `movil_lista_s06.firma.json`. Seleccionar un control no es un dictamen "
          "de cumplimiento; la versión del catálogo es v8.1 (fuente oficial CIS).",
          ""]
    for c in lista["controles"]:
        md.append(f"## {c['id']} — {c['titulo']}")
        md.append(f"Justificación de aplicabilidad: {c['justificacion']}")
        md.append("")
    md.append("No seleccionados (alcance personal/monousuario): 5, 8, 9, 12, 13, 14, 15, 17, 18 — "
              "orientados a organización, red corporativa o procesos no presentes en este ejercicio; "
              "quedan fuera sin perjuicio de reconsiderarlos si el alcance cambia.")
    h = escribe(raiz, "movil_lista_s06", lista, "\n".join(md), ahora)
    print("movil_lista_s06", h[0][:16], h[1][:16])

    # verificacion
    ok = True
    for nombre in ("movil_citas_s04", "movil_perfil_s05", "movil_lista_s06"):
        for ext in (".json", ".md"):
            p = raiz / "03_hallazgos" / f"{nombre}{ext}"
            f = json.loads((p.parent / (p.name + ".firma.json")).read_text(encoding="utf-8"))
            real = hashlib.sha256(p.read_bytes()).hexdigest()
            if real != f["sha256_bytes_firmados"]:
                ok = False
                print("FALLA VERIFICACION:", p.name)
    print("VERIFICACION FIRMAS:", "OK" if ok else "FALLA")


if __name__ == "__main__":
    main()
