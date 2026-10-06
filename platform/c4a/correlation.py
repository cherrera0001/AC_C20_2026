"""Gestor de correlación (Fase 8): une hallazgos con controles y normativas.

Para cada CWE del hallazgo consulta el mapa curado (knowledge/cwe_map.json) y le
adjunta los controles ISO y las normativas con su porqué. Solo adjunta
normativas que la config del encargo declaró aplicables: no se asume que todas
apliquen. La CVE NO se inventa: si no hay fuente, queda marcada como manual.
"""
from __future__ import annotations

from typing import Dict, List

from .config import Config
from .model import Finding


def correlate(findings: List[Finding], cfg: Config) -> List[Dict]:
    """Rellena norma/control de cada hallazgo y devuelve el detalle de correlación."""
    enabled = set(cfg.normativas)
    details: List[Dict] = []

    for f in findings:
        controls: set = set()
        normativas: set = set()
        reasons: List[str] = []
        for cwe in f.cwe:
            entry = cfg.cwe_map.get(cwe)
            if not entry:
                continue
            for c in entry.get("controles", []):
                controls.add(c)
            for n in entry.get("normativas", []):
                if n in enabled:
                    normativas.add(n)
            if entry.get("porque"):
                reasons.append(f"{cwe}: {entry['porque']}")

        f.control = sorted(controls)
        f.norma = sorted(normativas)

        if not f.cve:
            f.cve = []  # explícito: sin correlación automática

        details.append({
            "finding_id": f.id,
            "cwe": f.cwe,
            "controles": f.control,
            "normativas": f.norma,
            "cve": f.cve or "sin-correlacion-automatica",
            "cvss": f.cvss.get("base_score") if f.cvss else None,
            "porque": reasons,
        })
    return details


def controls_matrix(findings: List[Finding], cfg: Config, when: str) -> List[Dict]:
    """Construye la matriz de controles (Fase 4) a partir de los hallazgos.

    Un control con hallazgos abiertos se marca no-cumple/parcial; los controles
    del catálogo sin hallazgos quedan 'no-evaluado' en este ciclo estático.
    """
    by_control: Dict[str, List[Finding]] = {}
    for f in findings:
        for c in f.control:
            by_control.setdefault(c, []).append(f)

    rows: List[Dict] = []
    for ctrl_id, meta in cfg.controls.items():
        if ctrl_id.startswith("_"):
            continue
        hits = by_control.get(ctrl_id, [])
        norms = [n for n in meta.get("normativas", []) if n in set(cfg.normativas)]
        if hits:
            worst = _worst_sev(hits)
            compliance = "no-cumple" if worst in ("CRITICO", "ALTO") else "parcial"
            result = f"{len(hits)} hallazgo(s) asociados; peor severidad {worst}"
            status = "con-observaciones"
            risk = worst
            tech_ev = ", ".join(sorted({eid for h in hits for eid in h.evidence}))[:300]
        else:
            compliance = "no-evaluado"
            result = "sin hallazgos en este ciclo estático"
            status = "no-evaluado"
            risk = "n/d"
            tech_ev = ""
        rows.append({
            "control": ctrl_id,
            "objetivo": meta.get("objetivo", ""),
            "propietario": "por-asignar",
            "implementacion": "no-determinada (ciclo estático)",
            "evidencia": tech_ev or "n/d",
            "frecuencia": "por-ciclo",
            "responsable": "Rol de Control de Seguridad",
            "estado": status,
            "resultado": result,
            "riesgo": risk,
            "cumplimiento": compliance,
            "referencia": "; ".join(norms),
            "requisito": meta.get("objetivo", ""),
            "evidencia_tecnica": tech_ev,
            "ultima_validacion": when,
        })
    return rows


_SEV_ORDER = {"CRITICO": 5, "ALTO": 4, "MEDIO": 3, "BAJO": 2, "INFORMACIONAL": 1,
              "REQUIERE-VALIDACION": 0, "NO-REPRODUCIDO": 0}


def _worst_sev(findings: List[Finding]) -> str:
    return max((f.severity for f in findings), key=lambda s: _SEV_ORDER.get(s, 0))
