"""Gestor de riesgo (Fase 7, parcial): deriva severidad, probabilidad e impacto.

La magnitud sale del CVSS calculado (no de una opinión). La probabilidad se
deriva del vector (accesibilidad y requisitos de explotación) y el impacto de
las métricas C/I/A. Un hallazgo de confianza indirecta no se declara validado:
pasa a estado 'requires-validation'. Además se calcula una PRIORIDAD que combina
severidad técnica con impacto de cumplimiento (una obligación exigible escala la
prioridad por encima de un CVSS alto sin encuadre), como pide el alcance.
"""
from __future__ import annotations

from typing import Dict, List

from . import cvss as cvss_mod
from .model import Finding

_RATING_ES = {
    "CRITICAL": "CRITICO", "HIGH": "ALTO", "MEDIUM": "MEDIO",
    "LOW": "BAJO", "NONE": "INFORMACIONAL",
}
_SEV_WEIGHT = {"CRITICO": 5, "ALTO": 4, "MEDIO": 3, "BAJO": 2, "INFORMACIONAL": 1}


def assess(findings: List[Finding]) -> List[Finding]:
    for f in findings:
        if f.cvss:
            rating = f.cvss.get("base_severity", "NONE")
            f.severity = _RATING_ES.get(rating, "INFORMACIONAL")
            metrics = cvss_mod.parse_vector(f.cvss.get("vector", ""))
            f.probability = _probability(metrics)
            f.impact = _impact(metrics)
        else:
            f.severity = "INFORMACIONAL"
            f.probability = "baja"
            f.impact = "bajo"

        if f.confidence in ("indirect", "inferred"):
            f.status = "requires-validation"
            if "Pendiente de validación técnica por un segundo rol." not in f.notes:
                f.notes = (f.notes + " Pendiente de validación técnica por un segundo rol.").strip()
    return findings


def priority(f: Finding) -> float:
    """Prioridad combinada: severidad técnica + bono por obligación exigible."""
    base = float(f.cvss.get("base_score", 0.0)) if f.cvss else 0.0
    sev = _SEV_WEIGHT.get(f.severity, 0)
    score = base + sev * 0.2
    if "LEY-21663" in f.norma:   # deber legal exigible
        score += 1.5
    if "LEY-21719" in f.norma:   # protección de datos
        score += 0.8
    return round(min(score, 12.0), 2)


def gate(findings: List[Finding], threshold: str) -> Dict[str, object]:
    """Compuerta de CI: ¿hay hallazgos ABIERTOS en o por encima del umbral?

    Devuelve si se dispara y cuántos. Los falsos positivos triados no cuentan.
    """
    th = _SEV_WEIGHT.get(threshold.upper(), 0)
    offending = [f for f in findings
                 if f.status != "false-positive" and _SEV_WEIGHT.get(f.severity, 0) >= th]
    return {"threshold": threshold.upper(), "triggered": bool(offending),
            "count": len(offending),
            "ids": [f.id for f in offending][:50]}


def summary(findings: List[Finding]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return counts


def _probability(m: Dict[str, str]) -> str:
    av, ac, pr, ui = m.get("AV"), m.get("AC"), m.get("PR"), m.get("UI")
    if av == "N" and ac == "L" and pr == "N" and ui == "N":
        return "alta"
    if av in ("N", "A") and pr in ("N", "L"):
        return "media"
    return "baja"


def _impact(m: Dict[str, str]) -> str:
    vals = [m.get("C"), m.get("I"), m.get("A")]
    if "H" in vals:
        return "alto"
    if "L" in vals:
        return "medio"
    return "bajo"
