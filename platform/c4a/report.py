"""Gestor de reportes (Fase 9): escribe todos los entregables en disco.

Cada entregable es verificable: cita ids de evidencia con su hash, el vector y
puntaje CVSS, los controles y normativas correlacionados, y cómo reproducir.
Separa detección de conclusión y deja explícita la incertidumbre.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

from .config import Config
from .model import Evidence, Finding, Run
from . import risk


def _w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _ordered(findings: List[Finding]) -> List[Finding]:
    return sorted(findings, key=risk.priority, reverse=True)


# --- salidas estructuradas ------------------------------------------------

def write_inventory(cfg: Config, inventory: Dict) -> Path:
    p = cfg.phase["evidencia"] / "inventario.json"
    _w(p, json.dumps(inventory, ensure_ascii=False, indent=2))
    return p


def write_findings_json(cfg: Config, run_id: str, findings: List[Finding], correlation: List[Dict]) -> Path:
    p = cfg.phase["state"] / "findings" / f"{run_id}.json"
    data = {
        "run_id": run_id,
        "count": len(findings),
        "findings": [f.to_dict() for f in findings],
        "correlation": correlation,
    }
    _w(p, json.dumps(data, ensure_ascii=False, indent=2))
    return p


def write_matrix_csv(cfg: Config, rows: List[Dict]) -> Path:
    p = cfg.phase["hallazgos"] / "matriz_cumplimiento.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    cols = ["control", "objetivo", "propietario", "implementacion", "evidencia",
            "frecuencia", "responsable", "estado", "resultado", "riesgo",
            "cumplimiento", "referencia", "requisito", "evidencia_tecnica",
            "ultima_validacion"]
    with open(p, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in cols})
    return p


def write_finding_cards(cfg: Config, findings: List[Finding], ev_by_id: Dict[str, Evidence]) -> List[Path]:
    out: List[Path] = []
    # Cada corrida regenera sus fichas: se retiran las de corridas previas para
    # que 03_hallazgos/ refleje exactamente el resultado actual.
    for stale in cfg.phase["hallazgos"].glob("F-*.md"):
        stale.unlink()
    for f in _ordered(findings):
        lines = [
            f"# {f.id} — {f.title}", "",
            f"- **Tipo:** {f.finding_type}",
            f"- **Severidad:** {f.severity}  ·  **Prioridad combinada:** {risk.priority(f)}",
            f"- **Estado:** {f.status}  ·  **Confianza:** {f.confidence}",
            f"- **Probabilidad:** {f.probability}  ·  **Impacto:** {f.impact}",
            f"- **Componente:** `{f.component}`",
            f"- **Detector:** {f.source}  ·  **Detectado:** {f.detected_at}",
            f"- **Roles:** {', '.join(f.responsible_roles)}",
            "",
            "## Descripción", f.description, "",
        ]
        if f.cvss:
            lines += [
                "## CVSS v3.1",
                f"- Vector: `{f.cvss.get('vector','')}`",
                f"- Puntaje base: **{f.cvss.get('base_score','')}** ({f.cvss.get('base_severity','')})",
                f"- Fuente: {f.cvss.get('source','')} — {f.cvss.get('nota','')}",
                "",
            ]
        cwe_txt = ", ".join(f"{c} ({cfg.cwe.get(c,{}).get('name','')})" for c in f.cwe) or "n/d"
        lines += [
            "## Clasificación",
            f"- **CWE:** {cwe_txt}",
            f"- **CVE:** {', '.join(f.cve) if f.cve else 'sin correlación automática — revisión manual'}",
            f"- **Controles ISO:** {', '.join(f.control) or 'n/d'}",
            f"- **Normativas:** {', '.join(f.norma) or 'n/d'}",
            f"- **Impacto de cumplimiento:** {f.impact_compliance or 'n/d'}",
            "",
            "## Evidencia",
        ]
        for eid in f.evidence:
            ev = ev_by_id.get(eid)
            if ev:
                lines.append(f"- `{eid}` — {ev.location} · sha256 `{ev.sha256[:16]}…` · {ev.result}")
                if ev.excerpt_masked:
                    lines += ["", "  ```", *[f"  {ln}" for ln in ev.excerpt_masked.splitlines()[:12]], "  ```"]
        lines += [
            "",
            "## Reproducción",
            f"- Método: {f.reproduction.get('method','')}",
            f"- Comando: `{f.reproduction.get('command','')}`",
            f"- Resultado esperado: {f.reproduction.get('expected','')}",
            f"- Entorno: {f.reproduction.get('environment','')}",
            "",
            "## Remediación",
            f.remediation or "n/d",
            "",
            f"**Recomendaciones:** {f.recommendations or 'n/d'}",
            "",
            f"**Notas:** {f.notes or 'n/d'}",
            "",
        ]
        p = cfg.phase["hallazgos"] / f"{f.id}.md"
        _w(p, "\n".join(lines))
        out.append(p)
    return out


# --- informes narrativos --------------------------------------------------

def write_reports(cfg, run, findings, inventory, matrix, correlation, ev_items) -> List[Path]:
    paths: List[Path] = []
    # Los informes se centran en lo ABIERTO (los falsos positivos triados se
    # excluyen de los recuentos, pero quedan trazados en el registro de triaje).
    open_f = [f for f in findings if f.status != "false-positive"]
    counts = risk.summary(open_f)
    ordered = _ordered(open_f)

    paths.append(_resumen_ejecutivo(cfg, run, ordered, counts, inventory, matrix, findings))
    paths.append(_informe_tecnico(cfg, run, ordered, inventory))
    paths.append(_plan_remediacion(cfg, ordered))
    paths.append(_riesgos(cfg, ordered))
    paths.append(_mapa_cve_cwe_cvss(cfg, ordered))
    paths.append(_matriz_normativas(cfg, matrix))
    paths.append(_registro_evidencia(cfg, ev_items))
    paths.append(_registro_reproduccion(cfg, run, ordered))
    paths.append(_registro_triaje(cfg, findings))
    paths.append(_indice(cfg, run, paths))
    return paths


def _sev_table(counts: Dict[str, int]) -> str:
    order = ["CRITICO", "ALTO", "MEDIO", "BAJO", "INFORMACIONAL",
             "REQUIERE-VALIDACION", "NO-REPRODUCIDO"]
    rows = [f"| {s} | {counts.get(s, 0)} |" for s in order if counts.get(s, 0)]
    if not rows:
        rows = ["| (sin hallazgos) | 0 |"]
    return "| Severidad | N.º |\n|---|---|\n" + "\n".join(rows)


def _resumen_ejecutivo(cfg, run, ordered, counts, inventory, matrix, all_findings=None) -> Path:
    no_cumple = sum(1 for r in matrix if r["cumplimiento"] == "no-cumple")
    parcial = sum(1 for r in matrix if r["cumplimiento"] == "parcial")
    all_findings = all_findings if all_findings is not None else ordered
    n_fp = sum(1 for f in all_findings if f.status == "false-positive")
    n_acc = sum(1 for f in all_findings if f.status == "accepted-risk")
    top = ordered[:5]
    body = f"""# Resumen ejecutivo — {cfg.audit_name}

**Ejecución:** {run.run_id} · {run.started_at} · objetivo `{run.target}`
**Alcance:** auditoría estática de repositorio (solo lectura). El pentest de red
permanece tras su compuerta de autorización y no forma parte de esta ejecución.

## Estado en una línea

Se analizaron {inventory['totals']['files_scanned']} archivos y hay {len(ordered)}
hallazgos ABIERTOS. Controles con incumplimiento: {no_cumple}; parciales: {parcial}.
Triaje humano: {n_fp} descartado(s) como falso positivo, {n_acc} con riesgo aceptado
(trazados en registro_triaje.md, fuera de este recuento).

## Hallazgos por severidad

{_sev_table(counts)}

## Los cinco de mayor prioridad

"""
    if top:
        for f in top:
            body += f"- **[{f.severity}]** {f.title} — `{f.component}` (prioridad {risk.priority(f)}, {', '.join(f.norma) or 'sin normativa'})\n"
    else:
        body += "- Sin hallazgos en este ciclo.\n"
    body += """
## Qué significa y qué sigue

Cada hallazgo tiene evidencia con hash, un CVSS calculado y su encuadre en
controles y normativas. Los de confianza indirecta están marcados como
*requiere validación*: son observaciones que un segundo rol debe confirmar antes
de tratarlas como incumplimiento. El plan de remediación ordena el trabajo por
prioridad combinada (técnica + obligación legal).
"""
    p = cfg.phase["informe"] / "resumen_ejecutivo.md"
    _w(p, body)
    return p


def _informe_tecnico(cfg, run, ordered, inventory) -> Path:
    body = [f"# Informe técnico — {cfg.audit_name}", "",
            f"**Ejecución:** {run.run_id} · **Objetivo:** `{run.target}`",
            f"**Auditor:** {cfg.auditor or 'n/d'} · **Inicio:** {run.started_at} · **Fin:** {run.finished_at}",
            "",
            "## Metodología", "",
            "Auditoría estática de solo lectura en 4 fases (planificar, recopilar, "
            "analizar, informar). Detectores deterministas sobre el árbol del "
            "repositorio; evidencia con hash SHA-256 y timestamp; CVSS v3.1 "
            "calculado del vector; correlación curada a CWE, controles ISO 27001 y "
            "normativas declaradas. No se ejecutó nada contra sistemas de red.", "",
            "## Entorno evaluado", "",
            f"- Lenguajes: {', '.join(inventory['languages']) or 'n/d'}",
            f"- Gestores de paquetes: {len(inventory['package_managers'])}",
            f"- Contenedorización: {len(inventory['containerization'])} archivo(s)",
            f"- CI/CD: {len(inventory['ci_cd'])} workflow(s)",
            f"- Archivos .env detectados: {len(inventory['env_files'])}",
            f"- Archivos analizados: {inventory['totals']['files_scanned']} "
            f"(omitidos por tamaño: {inventory['totals']['skipped_large']}, "
            f"binarios: {inventory['totals']['skipped_binary']})",
            "",
            "## Hallazgos (por prioridad)", ""]
    if not ordered:
        body.append("Sin hallazgos en este ciclo.")
    for f in ordered:
        body += [
            f"### {f.id} — {f.title}",
            f"- Severidad **{f.severity}** · prioridad {risk.priority(f)} · estado {f.status} · confianza {f.confidence}",
            f"- Componente `{f.component}` · detector {f.source}",
            f"- CVSS `{f.cvss.get('vector','n/d')}` = **{f.cvss.get('base_score','n/d')}**" if f.cvss else "- CVSS n/d",
            f"- CWE {', '.join(f.cwe) or 'n/d'} · CVE {', '.join(f.cve) if f.cve else 'manual'} · Controles {', '.join(f.control) or 'n/d'} · Normativas {', '.join(f.norma) or 'n/d'}",
            f"- Evidencia: {', '.join(f.evidence)}",
            f"- Reproducir: `{f.reproduction.get('command','')}`",
            f"- {f.description}",
            "",
        ]
    p = cfg.phase["informe"] / "informe_tecnico.md"
    _w(p, "\n".join(body))
    return p


def _plan_remediacion(cfg, ordered) -> Path:
    body = ["# Plan de remediación", "",
            "Ordenado por prioridad combinada (severidad técnica + obligación legal).",
            "", "| Prioridad | ID | Hallazgo | Componente | Acción | Responsable sugerido | Plazo sugerido |",
            "|---|---|---|---|---|---|---|"]
    for f in ordered:
        plazo = _plazo(f.severity)
        action = (f.remediation or "n/d").replace("\n", " ")[:160]
        body.append(f"| {risk.priority(f)} | {f.id} | {f.title[:50]} | `{f.component}` | {action} | {f.responsible_roles[0] if f.responsible_roles else 'n/d'} | {plazo} |")
    if not ordered:
        body.append("| - | - | sin hallazgos | - | - | - | - |")
    p = cfg.phase["informe"] / "plan_remediacion.md"
    _w(p, "\n".join(body))
    return p


def _plazo(sev: str) -> str:
    return {"CRITICO": "72 h", "ALTO": "7 días", "MEDIO": "30 días",
            "BAJO": "90 días", "INFORMACIONAL": "siguiente ciclo"}.get(sev, "por-definir")


def _riesgos(cfg, ordered) -> Path:
    body = ["# Reporte de riesgos", "",
            "| ID | Severidad | Probabilidad | Impacto | Prioridad | Estado |",
            "|---|---|---|---|---|---|"]
    for f in ordered:
        body.append(f"| {f.id} | {f.severity} | {f.probability} | {f.impact} | {risk.priority(f)} | {f.status} |")
    if not ordered:
        body.append("| - | - | - | - | - | - |")
    p = cfg.phase["informe"] / "riesgos.md"
    _w(p, "\n".join(body))
    return p


def _mapa_cve_cwe_cvss(cfg, ordered) -> Path:
    con_cve = sum(1 for f in ordered if f.cve)
    if con_cve:
        nota = (f"CVE: {con_cve} hallazgo(s) con CVE correlacionadas por SCA. "
                "El resto queda para revisión manual. CWE y CVSS presentes.")
    else:
        nota = ("CVE: en este ciclo no corrió SCA; se marca para revisión manual "
                "con una herramienta de SCA. CWE y CVSS sí están presentes.")
    body = ["# Mapa CVE / CWE / CVSS", "", nota, "",
            "| ID | CWE | CVSS (vector → base) | CVE |", "|---|---|---|---|"]
    for f in ordered:
        cwe = ", ".join(f.cwe) or "n/d"
        cvss = f"`{f.cvss.get('vector','')}` → {f.cvss.get('base_score','')}" if f.cvss else "n/d"
        cve = ", ".join(f.cve) if f.cve else "revisión manual"
        body.append(f"| {f.id} | {cwe} | {cvss} | {cve} |")
    if not ordered:
        body.append("| - | - | - | - |")
    p = cfg.phase["informe"] / "mapa_cve_cwe_cvss.md"
    _w(p, "\n".join(body))
    return p


def _matriz_normativas(cfg, matrix) -> Path:
    body = ["# Matriz de normativas y controles", "",
            f"Normativas aplicables declaradas: {', '.join(cfg.normativas)}", "",
            "| Control | Objetivo | Cumplimiento | Riesgo | Referencia | Última validación |",
            "|---|---|---|---|---|---|"]
    for r in matrix:
        body.append(f"| {r['control']} | {r['objetivo'][:48]} | {r['cumplimiento']} | {r['riesgo']} | {r['referencia']} | {r['ultima_validacion']} |")
    p = cfg.phase["informe"] / "matriz_normativas.md"
    _w(p, "\n".join(body))
    return p


def _registro_evidencia(cfg, ev_items) -> Path:
    body = ["# Registro de evidencia", "",
            f"Total: {len(ev_items)} pieza(s). Cada una con fuente, fecha, hash y confianza.",
            "", "| ID | Tipo | Ubicación | sha256 | Confianza | Estado |",
            "|---|---|---|---|---|---|"]
    for e in ev_items:
        body.append(f"| {e.id} | {e.type} | {e.location} | `{e.sha256[:16]}…` | {e.confidence} | {e.status} |")
    if not ev_items:
        body.append("| - | - | - | - | - | - |")
    p = cfg.phase["informe"] / "registro_evidencia.md"
    _w(p, "\n".join(body))
    return p


def _registro_reproduccion(cfg, run, ordered) -> Path:
    body = ["# Registro de reproducción", "",
            f"Ejecución {run.run_id} · hash de resultado `{run.hash[:16]}…`", "",
            "Cómo reproducir la auditoría completa:", "",
            "```",
            f"python3 -m c4a run --config {cfg.config_path.name}",
            f"python3 -m c4a reproduce --run {run.run_id}",
            "```", "",
            "La reproducción re-ejecuta la auditoría y compara cada hallazgo por id "
            "determinista y por hash de evidencia. Estados posibles: reproducido, "
            "parcial, no reproducido.", "",
            "| ID | Estado | Comando de verificación |", "|---|---|---|"]
    for f in ordered:
        body.append(f"| {f.id} | {f.status} | `{f.reproduction.get('command','')}` |")
    if not ordered:
        body.append("| - | - | - |")
    p = cfg.phase["informe"] / "registro_reproduccion.md"
    _w(p, "\n".join(body))
    return p


def _registro_triaje(cfg, all_findings) -> Path:
    triaged = [f for f in all_findings if f.status in ("false-positive", "accepted-risk")]
    body = ["# Registro de triaje", "",
            "Decisiones humanas que cambian el tratamiento de un hallazgo. Persisten "
            "entre corridas vía `triage.json` y se aplican en cada auditoría.", "",
            "| ID | Decisión (estado) | Componente | Nota |", "|---|---|---|---|"]
    for f in triaged:
        nota = (f.notes or "").replace("\n", " ")[:160]
        body.append(f"| {f.id} | {f.status} | `{f.component}` | {nota} |")
    if not triaged:
        body.append("| - | (sin decisiones de triaje todavía) | - | - |")
    p = cfg.phase["informe"] / "registro_triaje.md"
    _w(p, "\n".join(body))
    return p


def _indice(cfg, run, paths) -> Path:
    names = [p.name for p in paths if p.name != "README.md"]
    body = [f"# Índice del informe — {cfg.audit_name}", "",
            f"Ejecución {run.run_id} · {run.started_at}", "",
            "## Documentos", ""]
    for n in names:
        body.append(f"- [{n}]({n})")
    body += ["", "## Artefactos relacionados", "",
             "- Mapa navegable (HTML, abrir en el navegador): [mapa.html](mapa.html)",
             "- SARIF 2.1.0 (CI / code scanning): `hallazgos.sarif.json`",
             "- Inventario: `../02_evidencia/inventario.json`",
             "- Fichas de hallazgo y matriz: `../03_hallazgos/`",
             "- Evidencia cruda con hash: `../evidence/" + run.run_id + "/`",
             "- Ledger de ejecución: `../.c4a/runs.jsonl`"]
    p = cfg.phase["informe"] / "README.md"
    _w(p, "\n".join(body))
    return p
