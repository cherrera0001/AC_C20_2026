"""Calculadora de puntaje base CVSS v3.1 a partir de un vector.

No inventa puntajes: aplica la fórmula oficial de FIRST (CVSS v3.1) al vector
que se le entrega. El vector que asigna cada detector es una línea base por
CLASE de problema, explícitamente marcada para revisión manual; el puntaje, en
cambio, es un cálculo determinista y verificable contra la calculadora oficial.
"""
from __future__ import annotations

import math
from typing import Dict

_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_AC = {"L": 0.77, "H": 0.44}
_PR_U = {"N": 0.85, "L": 0.62, "H": 0.27}
_PR_C = {"N": 0.85, "L": 0.68, "H": 0.5}
_UI = {"N": 0.85, "R": 0.62}
_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}


def _roundup(value: float) -> float:
    """Roundup de CVSS v3.1 (aritmética entera, redondeo hacia arriba a 0.1)."""
    int_input = round(value * 100000)
    if int_input % 10000 == 0:
        return int_input / 100000.0
    return (math.floor(int_input / 10000) + 1) / 10.0


def parse_vector(vector: str) -> Dict[str, str]:
    metrics: Dict[str, str] = {}
    for part in vector.strip().split("/"):
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
        key = key.strip().upper()
        if key == "CVSS":
            continue
        metrics[key] = val.strip().upper()
    return metrics


def base_score(vector: str) -> float:
    """Puntaje base CVSS v3.1 para el vector dado (0.0–10.0)."""
    m = parse_vector(vector)
    required = ("AV", "AC", "PR", "UI", "S", "C", "I", "A")
    missing = [k for k in required if k not in m]
    if missing:
        raise ValueError(f"vector CVSS incompleto, faltan: {missing}")

    scope_changed = m["S"] == "C"
    pr_table = _PR_C if scope_changed else _PR_U

    iss = 1 - (1 - _CIA[m["C"]]) * (1 - _CIA[m["I"]]) * (1 - _CIA[m["A"]])
    if scope_changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        impact = 6.42 * iss

    exploitability = 8.22 * _AV[m["AV"]] * _AC[m["AC"]] * pr_table[m["PR"]] * _UI[m["UI"]]

    if impact <= 0:
        return 0.0
    if scope_changed:
        return _roundup(min(1.08 * (impact + exploitability), 10))
    return _roundup(min(impact + exploitability, 10))


def severity_rating(score: float) -> str:
    """Rating cualitativo CVSS v3.1 a partir del puntaje base."""
    if score == 0.0:
        return "NONE"
    if score < 4.0:
        return "LOW"
    if score < 7.0:
        return "MEDIUM"
    if score < 9.0:
        return "HIGH"
    return "CRITICAL"


def evaluate(vector: str, source: str = "detector-baseline") -> Dict[str, object]:
    """Devuelve el bloque CVSS estructurado de un hallazgo."""
    score = base_score(vector)
    return {
        "version": "3.1",
        "vector": vector,
        "base_score": score,
        "base_severity": severity_rating(score),
        "source": source,
        "nota": "Vector base por clase de problema; revisar y ajustar al contexto real.",
    }
