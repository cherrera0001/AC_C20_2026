"""M1 · Mapa de evidencia y resultados en HTML (autocontenido, sin dependencias).

Genera un `mapa.html` de un solo archivo: tiles de severidad, hallazgos
navegables con su detalle (evidencia con hash, reproducción, remediación) y el
enlace hallazgo → CWE/CVE → control → normativa. Sin red ni CDN: estilos y
script en línea, claro/oscuro. Todo el texto dinámico se escapa (el objetivo es
código: los extractos traen <, >, & y comillas).

Colores de estado tomados de la paleta validada de la skill dataviz; la
severidad siempre lleva etiqueta de texto, nunca color solo.
"""
from __future__ import annotations

import html
import json
from typing import Dict, List

from . import risk
from .config import Config
from .model import Evidence, Finding, Run

# severidad → (rol de estado, color claro, color oscuro)
_SEV_COLOR = {
    "CRITICO": ("#d03b3b", "#d03b3b"),
    "ALTO": ("#ec835a", "#ec835a"),
    "MEDIO": ("#fab219", "#fab219"),
    "BAJO": ("#2a78d6", "#3987e5"),
    "INFORMACIONAL": ("#6b6a66", "#8a8984"),
    "REQUIERE-VALIDACION": ("#6b6a66", "#8a8984"),
    "NO-REPRODUCIDO": ("#6b6a66", "#8a8984"),
}
_SEV_ORDER = ["CRITICO", "ALTO", "MEDIO", "BAJO", "INFORMACIONAL"]


def _e(x) -> str:
    return html.escape(str(x), quote=True)


def render(cfg: Config, run: Run, findings: List[Finding], inventory: Dict,
           matrix: List[Dict], ev_items: List[Evidence]) -> str:
    ev_by_id = {e.id: e for e in ev_items}
    ordered = sorted(findings, key=risk.priority, reverse=True)
    open_f = [f for f in ordered if f.status != "false-positive"]
    counts = risk.summary(open_f)
    n_fp = sum(1 for f in findings if f.status == "false-positive")
    n_acc = sum(1 for f in findings if f.status == "accepted-risk")
    sca = (run.result_summary or {}).get("sca", {})

    tiles = []
    for sev in _SEV_ORDER:
        c = counts.get(sev, 0)
        color = _SEV_COLOR[sev][0]
        tiles.append(
            f'<div class="tile"><span class="dot" style="background:{color}"></span>'
            f'<span class="tile-n">{c}</span><span class="tile-l">{sev}</span></div>'
        )
    tiles.append(
        f'<div class="tile"><span class="tile-n">{n_fp}</span>'
        f'<span class="tile-l">falsos positivos</span></div>'
    )
    tiles.append(
        f'<div class="tile"><span class="tile-n">{n_acc}</span>'
        f'<span class="tile-l">riesgo aceptado</span></div>'
    )

    cards = "\n".join(_card(f, ev_by_id, cfg) for f in ordered)
    matrix_rows = "\n".join(
        f"<tr><td>{_e(r['control'])}</td><td>{_e(r['objetivo'])}</td>"
        f"<td class='cmp cmp-{_e(r['cumplimiento'])}'>{_e(r['cumplimiento'])}</td>"
        f"<td>{_e(r['riesgo'])}</td><td>{_e(r['referencia'])}</td></tr>"
        for r in matrix
    )

    sca_line = ""
    if sca.get("status") and sca.get("status") != "skipped":
        sca_line = (f"· SCA {_e(sca.get('engine'))} {_e(sca.get('status'))} "
                    f"({sca.get('cve_findings', 0)} CVE)")

    return _TEMPLATE.format(
        title=_e(cfg.audit_name),
        run_id=_e(run.run_id),
        target=_e(run.target),
        started=_e(run.started_at),
        version=_e(run.tool_versions.get("c4a", "")),
        files=inventory.get("totals", {}).get("files_scanned", 0),
        open_n=len(open_f),
        sca_line=sca_line,
        tiles="\n".join(tiles),
        cards=cards,
        matrix_rows=matrix_rows or "<tr><td colspan='5'>sin controles</td></tr>",
        sev_buttons="\n".join(
            f'<button class="sevbtn" data-sev="{s}">{s}</button>' for s in _SEV_ORDER
        ),
    )


def _card(f: Finding, ev_by_id: Dict[str, Evidence], cfg: Config) -> str:
    color = _SEV_COLOR.get(f.severity, _SEV_COLOR["INFORMACIONAL"])[0]
    searchable = _e(" ".join([
        f.id, f.title, f.component, f.source, " ".join(f.cwe),
        " ".join(f.cve), " ".join(f.control), " ".join(f.norma),
    ]).lower())
    cvss = ""
    if f.cvss:
        cvss = f"{_e(f.cvss.get('vector',''))} → {_e(f.cvss.get('base_score',''))}"
    cwe = ", ".join(
        f"{_e(c)} ({_e(cfg.cwe.get(c, {}).get('name',''))})" for c in f.cwe
    ) or "n/d"
    cve = ", ".join(_e(c) for c in f.cve) or "revisión manual"
    controles = ", ".join(_e(c) for c in f.control) or "n/d"
    normas = ", ".join(_e(n) for n in f.norma) or "n/d"

    ev_html = []
    for eid in f.evidence:
        ev = ev_by_id.get(eid)
        if not ev:
            continue
        ex = ""
        if ev.excerpt_masked:
            ex = f"<pre>{_e(ev.excerpt_masked)}</pre>"
        ev_html.append(
            f"<li><code>{_e(ev.location)}</code> · sha256 "
            f"<code>{_e(ev.sha256[:16])}…</code> · {_e(ev.result)}{ex}</li>"
        )
    ev_block = "<ul class='ev'>" + "".join(ev_html) + "</ul>" if ev_html else "<p>sin evidencia</p>"

    suppressed = " suppressed" if f.status == "false-positive" else ""
    return f"""<details class="finding{suppressed}" data-sev="{_e(f.severity)}" data-status="{_e(f.status)}" data-text="{searchable}">
  <summary>
    <span class="badge" style="--c:{color}">{_e(f.severity)}</span>
    <span class="f-title">{_e(f.title)}</span>
    <span class="f-meta">{_e(f.component)} · {_e(f.status)} · prio {risk.priority(f)}</span>
  </summary>
  <div class="detail">
    <p>{_e(f.description)}</p>
    <dl>
      <dt>ID</dt><dd><code>{_e(f.id)}</code> <span class="notes">(para triar: <code>c4a triage --finding {_e(f.id)} --decision …</code>)</span></dd>
      <dt>CVSS</dt><dd>{cvss or 'n/d'}</dd>
      <dt>CWE</dt><dd>{cwe}</dd>
      <dt>CVE</dt><dd>{cve}</dd>
      <dt>Controles ISO</dt><dd>{controles}</dd>
      <dt>Normativas</dt><dd>{normas}</dd>
      <dt>Confianza</dt><dd>{_e(f.confidence)}</dd>
    </dl>
    <h4>Evidencia</h4>
    {ev_block}
    <h4>Reproducción</h4>
    <pre>{_e(f.reproduction.get('command',''))}</pre>
    <h4>Remediación</h4>
    <p>{_e(f.remediation or 'n/d')}</p>
    <p class="notes">{_e(f.notes or '')}</p>
  </div>
</details>"""


_TEMPLATE = """<!doctype html>
<html lang="es" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa C4A — {title}</title>
<style>
  :root {{
    --surface: #fcfcfb; --panel: #ffffff; --ink: #0b0b0b; --ink2: #52514e;
    --line: #e4e3df; --accent: #2a78d6;
  }}
  :root[data-theme="dark"] {{
    --surface: #1a1a19; --panel: #232322; --ink: #ffffff; --ink2: #c3c2b7;
    --line: #383835; --accent: #3987e5;
  }}
  @media (prefers-color-scheme: dark) {{
    :root[data-theme="auto"] {{
      --surface: #1a1a19; --panel: #232322; --ink: #ffffff; --ink2: #c3c2b7;
      --line: #383835; --accent: #3987e5;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--surface); color:var(--ink);
    font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
  header {{ padding:20px 24px; border-bottom:1px solid var(--line); }}
  h1 {{ font-size:19px; margin:0 0 4px; }}
  .sub {{ color:var(--ink2); font-size:13px; }}
  main {{ padding:20px 24px; max-width:1100px; margin:0 auto; }}
  .tiles {{ display:flex; flex-wrap:wrap; gap:10px; margin:0 0 18px; }}
  .tile {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
    padding:10px 14px; min-width:92px; display:flex; flex-direction:column; gap:2px; }}
  .tile-n {{ font-size:22px; font-weight:650; }}
  .tile-l {{ font-size:11px; color:var(--ink2); text-transform:uppercase; letter-spacing:.04em; }}
  .dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; }}
  .controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:0 0 14px; }}
  input[type=search] {{ flex:1; min-width:200px; padding:8px 10px; border:1px solid var(--line);
    border-radius:8px; background:var(--panel); color:var(--ink); }}
  .sevbtn, .toggle {{ padding:6px 10px; border:1px solid var(--line); border-radius:8px;
    background:var(--panel); color:var(--ink2); cursor:pointer; font-size:12px; }}
  .sevbtn.active {{ color:var(--ink); border-color:var(--accent); }}
  .finding {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
    margin:0 0 8px; overflow:hidden; }}
  .finding.suppressed {{ opacity:.55; }}
  summary {{ list-style:none; cursor:pointer; padding:11px 14px; display:grid;
    grid-template-columns:120px 1fr auto; gap:12px; align-items:center; }}
  summary::-webkit-details-marker {{ display:none; }}
  .badge {{ font-size:11px; font-weight:650; color:#fff; background:var(--c);
    padding:3px 8px; border-radius:999px; text-align:center; }}
  .f-title {{ font-weight:550; }}
  .f-meta {{ color:var(--ink2); font-size:12px; text-align:right; }}
  .detail {{ padding:4px 16px 16px; border-top:1px solid var(--line); }}
  dl {{ display:grid; grid-template-columns:140px 1fr; gap:4px 12px; margin:10px 0; }}
  dt {{ color:var(--ink2); font-size:13px; }}
  h4 {{ margin:14px 0 6px; font-size:13px; }}
  pre {{ background:var(--surface); border:1px solid var(--line); border-radius:8px;
    padding:8px 10px; overflow:auto; font-size:12px; white-space:pre-wrap; word-break:break-word; }}
  ul.ev {{ margin:0; padding-left:18px; }}
  ul.ev li {{ margin:0 0 6px; }}
  code {{ font-size:12px; }}
  table {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:13px; }}
  th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ color:var(--ink2); font-weight:550; }}
  .cmp-no-cumple {{ color:#d03b3b; }} .cmp-parcial {{ color:#ec835a; }}
  .notes {{ color:var(--ink2); font-size:12px; }}
  h2 {{ font-size:15px; margin:26px 0 8px; }}
  footer {{ color:var(--ink2); font-size:12px; padding:18px 24px; border-top:1px solid var(--line); }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="sub">Ejecución {run_id} · {started} · objetivo <code>{target}</code> ·
    {files} archivos · {open_n} hallazgos abiertos {sca_line}
    <button class="toggle" id="themebtn" style="float:right">tema</button></div>
</header>
<main>
  <div class="tiles">{tiles}</div>
  <div class="controls">
    <input type="search" id="q" placeholder="filtrar por texto, CWE, CVE, componente…">
    {sev_buttons}
    <label class="toggle"><input type="checkbox" id="showsup"> ver suprimidos</label>
  </div>
  <div id="list">
  {cards}
  </div>

  <h2>Matriz de controles</h2>
  <table>
    <thead><tr><th>Control</th><th>Objetivo</th><th>Cumplimiento</th><th>Riesgo</th><th>Referencia</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
</main>
<footer>
  Generado por C4A {version}. Reproduce la auditoría con
  <code>python -m c4a run</code> y verifícala con <code>c4a verify</code> /
  <code>c4a reproduce</code>. Mapa autocontenido, sin red.
</footer>
<script>
  var active = new Set();
  function apply() {{
    var q = document.getElementById('q').value.toLowerCase();
    var sup = document.getElementById('showsup').checked;
    document.querySelectorAll('.finding').forEach(function(el) {{
      var okText = !q || (el.getAttribute('data-text')||'').indexOf(q) >= 0;
      var okSev = active.size === 0 || active.has(el.getAttribute('data-sev'));
      var okSup = sup || el.getAttribute('data-status') !== 'false-positive';
      el.style.display = (okText && okSev && okSup) ? '' : 'none';
    }});
  }}
  document.getElementById('q').addEventListener('input', apply);
  document.getElementById('showsup').addEventListener('change', apply);
  document.querySelectorAll('.sevbtn').forEach(function(b) {{
    b.addEventListener('click', function() {{
      var s = b.getAttribute('data-sev');
      if (active.has(s)) {{ active.delete(s); b.classList.remove('active'); }}
      else {{ active.add(s); b.classList.add('active'); }}
      apply();
    }});
  }});
  document.getElementById('themebtn').addEventListener('click', function() {{
    var r = document.documentElement;
    r.setAttribute('data-theme', r.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  }});
  apply();
</script>
</body>
</html>"""
