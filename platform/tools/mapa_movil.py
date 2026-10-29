#!/usr/bin/env python3
"""Mapa HTML recorrible del informe de cierre movil (canonico: htmlmap.py M1).

Un solo archivo autocontenido (sin red ni CDN): tiles de severidad, tarjetas
por riesgo navegables con su evidencia y huella SHA-256, cadena riesgo ->
CWE -> control ISO/NIST/CIS, matriz de cumplimiento y filtro por severidad y
texto. Paleta y estructura tomadas de platform/c4a/htmlmap.py. Todo texto
dinamico se escapa.

Uso: python mapa_movil.py --raiz <repo>
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

RUN = "evidence/RUN-20261029T003246Z-3802"

SEV_COLOR = {
    "ALTO": "#ec835a",
    "MEDIO": "#fab219",
    "BAJO": "#2a78d6",
    "INFORMACIONAL": "#6b6a66",
}
SEV_ORDER = ["ALTO", "MEDIO", "BAJO", "INFORMACIONAL"]

RIESGOS = [
    {"id": "R1", "sev": "ALTO", "titulo": "Superficie exportada sin permiso (65 componentes; 51 con intent-filter)",
     "condicion": "Componentes exportados sin android:permission; notables: receivers OTP, WebLoginResultHandlerActivity, SmbLinkingService, InstrumentationService.",
     "cwe": "CWE-926 (pendiente de confirmar)", "iso": "A.8.9", "nist": "Proteger, Identificar", "cis": "4, 1",
     "nivel": "parcial",
     "ev": ["rea/06_analisis_propio.json", "raw/dumpsys_com.whatsapp.w4b.txt", "rea/05_inspect_apk.json"]},
    {"id": "R2", "sev": "MEDIO", "titulo": "Permisos sensibles concedidos (ubicación, micrófono, cámara, contactos, medios)",
     "condicion": "Concedidos por decisión del usuario; denegados SMS/llamadas/legacy storage.",
     "cwe": "CWE-250", "iso": "A.8.3", "nist": "Proteger", "cis": "3, 6",
     "nivel": "parcial",
     "ev": ["raw/dumpsys_com.whatsapp.w4b.txt"]},
    {"id": "R3", "sev": "MEDIO", "titulo": "REQUEST_INSTALL_PACKAGES declarado",
     "condicion": "Función de instalación de paquetes presente en manifiesto.",
     "cwe": "CWE-494", "iso": "A.8.9", "nist": "Proteger", "cis": "10",
     "nivel": "parcial",
     "ev": ["rea/06_analisis_propio.json"]},
    {"id": "R4", "sev": "BAJO", "titulo": "Backup (cerrado)",
     "condicion": "full_backup_content y data_extraction_rules excluyen todo; cifrado FBE medido.",
     "cwe": "CWE-312", "iso": "A.8.24", "nist": "Recuperar, Proteger", "cis": "11",
     "nivel": "cumple",
     "ev": ["rea/xml_seguridad/full_backup_content.xml", "rea/xml_seguridad/data_extraction_rules.xml",
            "raw/postura_dispositivo.txt"]},
    {"id": "R5", "sev": "BAJO", "titulo": "Legacy external storage declarado",
     "condicion": "Mitigado por denegaciones de runtime.",
     "cwe": "CWE-200", "iso": "A.8.3", "nist": "Proteger", "cis": "3",
     "nivel": "parcial",
     "ev": ["rea/06_analisis_propio.json", "raw/dumpsys_com.whatsapp.w4b.txt"]},
    {"id": "R6", "sev": "BAJO", "titulo": "Parche de plataforma 2026-09-01 (postura verificada)",
     "condicion": "Bootloader locked, verified boot green, dm-verity enforcing, FBE, Play Protect activo.",
     "cwe": "n/d", "iso": "A.8.8", "nist": "Proteger, Identificar", "cis": "7",
     "nivel": "cumple",
     "ev": ["raw/postura_dispositivo.txt", "rea/01_inspect_adb_device.json"]},
    {"id": "R7", "sev": "BAJO", "titulo": "Versión de la app vigente (2.26.42.74, 2026-10-28)",
     "condicion": "Auto-actualización por Play; firmas v2/v3/v3.1 con certificado WhatsApp verificado.",
     "cwe": "n/d", "iso": "A.8.8", "nist": "Proteger", "cis": "7",
     "nivel": "cumple",
     "ev": ["rea/07_firma_certificados.json", "raw/dumpsys_com.whatsapp.w4b.txt"]},
    {"id": "R8", "sev": "MEDIO", "titulo": "Red: cleartext base y CA de usuario con override de pins",
     "condicion": "base-config cleartextTrafficPermitted=true; trust-anchors user overridePins=true; dominios clave con pin-set (20+ SHA-256).",
     "cwe": "CWE-319", "iso": "A.8.24", "nist": "Proteger", "cis": "4",
     "nivel": "parcial",
     "ev": ["rea/xml_seguridad/network_security_config.xml"]},
]


def _e(x) -> str:
    return html.escape(str(x), quote=True)


TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg:#ffffff; --fg:#1a1a1a; --mut:#6b6a66; --card:#f6f5f2; --line:#e2e0da; }}
html[data-theme="dark"] {{ --bg:#191919; --fg:#e8e6e1; --mut:#9a978f; --card:#222120; --line:#3a3833; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.55 system-ui,Segoe UI,Roboto,sans-serif; }}
header {{ padding:1.4rem 1.6rem .6rem; }}
h1 {{ font-size:1.35rem; margin:.2rem 0; }}
.meta {{ color:var(--mut); font-size:.85rem; }}
.tiles {{ display:flex; flex-wrap:wrap; gap:.6rem; padding:.8rem 1.6rem; }}
.tile {{ display:flex; align-items:center; gap:.45rem; background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:.4rem .8rem; }}
.dot {{ width:.7rem; height:.7rem; border-radius:50%; display:inline-block; }}
.tile-n {{ font-weight:700; font-size:1.05rem; }}
.tile-l {{ color:var(--mut); font-size:.8rem; text-transform:uppercase; letter-spacing:.03em; }}
.controls {{ padding:.2rem 1.6rem .8rem; display:flex; flex-wrap:wrap; gap:.4rem; align-items:center; }}
button {{ background:var(--card); color:var(--fg); border:1px solid var(--line); border-radius:.5rem; padding:.3rem .8rem; cursor:pointer; font-size:.85rem; }}
button.on {{ outline:2px solid var(--fg); }}
input[type=search] {{ flex:1; min-width:12rem; background:var(--card); color:var(--fg); border:1px solid var(--line); border-radius:.5rem; padding:.35rem .7rem; }}
main {{ padding:0 1.6rem 2.5rem; max-width:60rem; }}
details.finding {{ background:var(--card); border:1px solid var(--line); border-radius:.7rem; margin:.7rem 0; }}
details.finding summary {{ cursor:pointer; list-style:none; display:flex; flex-wrap:wrap; align-items:center; gap:.6rem; padding:.75rem .95rem; }}
details.finding summary::-webkit-details-marker {{ display:none; }}
.badge {{ --c:#6b6a66; border-left:.45rem solid var(--c); padding:.12rem .55rem; border-radius:.35rem; background:var(--bg); font-weight:700; font-size:.78rem; text-transform:uppercase; }}
.fid {{ font-weight:700; }}
.ftitle {{ flex:1; min-width:14rem; }}
.body {{ padding:.2rem 1rem 1rem; border-top:1px solid var(--line); }}
.chips {{ display:flex; flex-wrap:wrap; gap:.35rem; margin:.5rem 0; }}
.chip {{ font-size:.75rem; background:var(--bg); border:1px solid var(--line); border-radius:.4rem; padding:.12rem .5rem; color:var(--mut); }}
.ev {{ margin:.5rem 0 0; padding-left:1.1rem; }}
.ev li {{ margin:.25rem 0; font-size:.85rem; }}
code {{ background:var(--bg); border:1px solid var(--line); border-radius:.3rem; padding:.05rem .35rem; font-size:.82rem; }}
.nivel {{ font-weight:700; text-transform:uppercase; font-size:.8rem; }}
.nivel.cumple {{ color:#2a78d6; }} .nivel.parcial {{ color:#b8860b; }}
table {{ border-collapse:collapse; width:100%; font-size:.85rem; margin-top:.8rem; }}
th,td {{ border:1px solid var(--line); padding:.4rem .6rem; text-align:left; vertical-align:top; }}
th {{ background:var(--card); }}
footer {{ padding:1rem 1.6rem 2rem; color:var(--mut); font-size:.8rem; }}
.noresults {{ padding:1rem 1.6rem; color:var(--mut); display:none; }}
</style>
</head>
<body>
<header>
<h1>{title}</h1>
<div class="meta">Run {run_id} · objetivo {target} · {fecha} · APK sha256 <code>{apk}</code> · firmado por {firmante}</div>
</header>
<div class="tiles">
{tiles}
</div>
<div class="controls">
{sev_buttons}
<input id="q" type="search" placeholder="buscar por riesgo, CWE, control…">
<button id="theme" type="button">claro/oscuro</button>
</div>
<main>
{cards}
<table>
<thead><tr><th>Control ISO</th><th>Riesgo</th><th>Nivel propuesto</th><th>CWE</th></tr></thead>
<tbody>{matrix_rows}</tbody>
</table>
<p class="noresults" id="noresults">sin resultados para el filtro actual</p>
</main>
<footer>Informe recorrible hasta la evidencia: cada tarjeta enlaza sus archivos con huella SHA-256 en {run_dir}. Niveles de cumplimiento propuestos por el auditor (principio II); un borrador no se presenta como informe firmado. Generado por platform/tools/mapa_movil.py (canonico: platform/c4a/htmlmap.py M1).</footer>
<script>
var b=document.getElementById('theme');
b.onclick=function(){{var h=document.documentElement;var d=h.getAttribute('data-theme')==='dark';h.setAttribute('data-theme',d?'':'dark');}};
var sev='';
var btns=document.querySelectorAll('.sevbtn');
btns.forEach(function(x){{x.onclick=function(){{sev=(sev===x.dataset.sev)?'':x.dataset.sev;btns.forEach(function(y){{y.classList.toggle('on',y.dataset.sev===sev);}});filtrar();}};}});
var q=document.getElementById('q');
q.oninput=filtrar;
function filtrar(){{
 var t=q.value.toLowerCase();var any=false;
 document.querySelectorAll('details.finding').forEach(function(d){{
  var okS=!sev||d.dataset.sev===sev;
  var okT=!t||d.dataset.text.indexOf(t)>-1;
  var show=okS&&okT;d.style.display=show?'':'none';if(show)any=true;
 }});
 document.getElementById('noresults').style.display=any?'none':'block';
}}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default="..")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    man = json.loads((raiz / RUN / "MANIFEST.json").read_text(encoding="utf-8"))
    sha_por_path = {a["path"]: a["sha256"] for a in man["archivos"]}
    apk_sha = next(a["sha256"] for a in man["archivos"] if a["path"].endswith("base.apk"))

    counts = {s: 0 for s in SEV_ORDER}
    for r in RIESGOS:
        counts[r["sev"]] += 1
    tiles = "\n".join(
        f'<div class="tile"><span class="dot" style="background:{SEV_COLOR[s]}"></span>'
        f'<span class="tile-n">{counts[s]}</span><span class="tile-l">{s}</span></div>'
        for s in SEV_ORDER if counts[s]
    )

    cards = []
    for r in RIESGOS:
        color = SEV_COLOR[r["sev"]]
        ev_html = []
        for pth in r["ev"]:
            sh = sha_por_path.get(pth, "huella-en-MANIFEST")
            ev_html.append(f"<li><code>{_e(pth)}</code> · sha256 <code>{_e(sh[:16])}…</code></li>")
        searchable = _e(" ".join([r["id"], r["titulo"], r["condicion"], r["cwe"],
                                  r["iso"], r["nist"], r["cis"]]).lower())
        cards.append(f"""<details class="finding" data-sev="{_e(r['sev'])}" data-text="{searchable}">
<summary><span class="badge" style="--c:{color}">{_e(r['sev'])}</span>
<span class="fid">{_e(r['id'])}</span><span class="ftitle">{_e(r['titulo'])}</span></summary>
<div class="body">
<p>{_e(r['condicion'])}</p>
<div class="chips">
<span class="chip">ISO/IEC 27001:2022 {_e(r['iso'])}</span>
<span class="chip">NIST CSF 2.0: {_e(r['nist'])}</span>
<span class="chip">CIS v8.1: {_e(r['cis'])}</span>
<span class="chip">{_e(r['cwe'])}</span>
<span class="chip">cumplimiento propuesto: <span class="nivel {_e(r['nivel'])}">{_e(r['nivel'])}</span></span>
</div>
<strong>Evidencia (custodia verificable):</strong>
<ul class="ev">{''.join(ev_html)}</ul>
</div>
</details>""")

    matrix_rows = "\n".join(
        f"<tr><td>ISO/IEC 27001:2022 {_e(r['iso'])}</td><td>{_e(r['id'])} — {_e(r['titulo'])}</td>"
        f"<td><span class='nivel {_e(r['nivel'])}'>{_e(r['nivel'])}</span></td><td>{_e(r['cwe'])}</td></tr>"
        for r in RIESGOS
    )

    doc = TEMPLATE.format(
        title="Cierre de la auditoría móvil — Dispositivo personal + WhatsApp Business (com.whatsapp.w4b)",
        run_id=RUN.split("/")[-1],
        target="dispositivo a525a763 + com.whatsapp.w4b v2.26.42.74",
        fecha="2026-10-29",
        apk=apk_sha[:32] + "…",
        firmante="Cristóbal Herrera",
        tiles=tiles,
        sev_buttons="\n".join(f'<button class="sevbtn" data-sev="{s}">{s}</button>' for s in SEV_ORDER),
        cards="\n".join(cards),
        matrix_rows=matrix_rows,
        run_dir=RUN,
    )
    out = raiz / "04_informe" / "movil_mapa.html"
    out.write_text(doc, encoding="utf-8")
    print("movil_mapa.html:", len(doc), "bytes")


if __name__ == "__main__":
    main()
