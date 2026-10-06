"""Exportación a SARIF 2.1.0: la salida estándar para integrarse con CI y otras
herramientas (GitHub code scanning, editores, etc.).

Mapea cada hallazgo a un `result`, con su regla (el detector), nivel, ubicación,
y propiedades (CVSS, CWE, CVE, controles, normativas, estado). Los hallazgos
triados como falso positivo se marcan con `suppressions`, que es el mecanismo
nativo de SARIF para «esto ya fue revisado y descartado».
"""
from __future__ import annotations

from typing import Dict, List

from .config import Config
from .model import Evidence, Finding, Run

# severidad C4A → nivel SARIF
_LEVEL = {
    "CRITICO": "error", "ALTO": "error", "MEDIO": "warning",
    "BAJO": "note", "INFORMACIONAL": "note",
    "REQUIERE-VALIDACION": "note", "NO-REPRODUCIDO": "note",
}


def _line_of(finding: Finding, ev_by_id: Dict[str, Evidence]) -> int:
    for eid in finding.evidence:
        ev = ev_by_id.get(eid)
        if ev and ":" in ev.location:
            tail = ev.location.rsplit(":", 1)[-1]
            if tail.isdigit():
                return int(tail)
    return 1


def to_sarif(cfg: Config, run: Run, findings: List[Finding], ev_items: List[Evidence]) -> Dict:
    ev_by_id = {e.id: e for e in ev_items}

    # reglas: una por detector presente
    rule_ids = sorted({f.source for f in findings})
    rules = []
    for rid in rule_ids:
        sample = next(f for f in findings if f.source == rid)
        help_uri = ""
        if sample.cwe:
            help_uri = cfg.cwe.get(sample.cwe[0], {}).get("url", "")
        rules.append({
            "id": rid,
            "name": rid.replace(":", "_"),
            "shortDescription": {"text": sample.title[:120]},
            "helpUri": help_uri or "https://cwe.mitre.org/",
        })

    results = []
    for f in findings:
        result = {
            "ruleId": f.source,
            "level": _LEVEL.get(f.severity, "note"),
            "message": {"text": f"{f.title} — {f.description}"[:1000]},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.component.replace("\\", "/")},
                    "region": {"startLine": _line_of(f, ev_by_id)},
                }
            }],
            "properties": {
                "severidad": f.severity,
                "estado": f.status,
                "confianza": f.confidence,
                "cvss": f.cvss.get("vector", "") if f.cvss else "",
                "cvss_base": f.cvss.get("base_score") if f.cvss else None,
                "cwe": f.cwe,
                "cve": f.cve,
                "controles": f.control,
                "normativas": f.norma,
                "finding_id": f.id,
            },
        }
        if f.status == "false-positive":
            result["suppressions"] = [{"kind": "external",
                                       "justification": "triaje humano: falso positivo"}]
        results.append(result)

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "C4A",
                "version": run.tool_versions.get("c4a", "0.1.0"),
                "informationUri": "https://example.local/c4a",
                "rules": rules,
            }},
            "automationDetails": {"id": run.run_id},
            "results": results,
        }],
    }
