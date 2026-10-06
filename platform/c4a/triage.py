"""Triaje persistente: la revisión humana que sobrevive entre corridas.

Un humano decide sobre un hallazgo (falso positivo, riesgo aceptado, confirmado)
y esa decisión se guarda en `triage.json`, indexada por el id DETERMINISTA del
hallazgo (que es estable mientras el detector, el componente y la regla no
cambien). En cada corrida la plataforma aplica el triaje: cambia el estado del
hallazgo y lo separa de los «abiertos». Así el ruido se marca una vez, no en cada
corrida, y queda explícito quién decidió y por qué.

Encarna «separar detección de conclusión»: el detector observa; el humano concluye.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .config import Config
from .model import Finding
from .util import now_iso

VALID_DECISIONS = ("false-positive", "accepted-risk", "confirmed")

# decisión de triaje → estado del hallazgo
_DECISION_STATUS = {
    "false-positive": "false-positive",
    "accepted-risk": "accepted-risk",
    "confirmed": "validated",
}


def _triage_path(cfg: Config) -> Path:
    rel = cfg.raw.get("triage_file", "triage/triage.json")
    p = Path(rel)
    if not p.is_absolute():
        p = cfg.output_root / p
    return p


def load_triage(cfg: Config) -> Dict[str, Dict]:
    path = _triage_path(cfg)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return {e["finding_id"]: e for e in data.get("entries", []) if e.get("finding_id")}


def apply_triage(findings: List[Finding], triage: Dict[str, Dict]) -> Dict[str, int]:
    counts = {"open": 0, "false-positive": 0, "accepted-risk": 0, "confirmed": 0}
    for f in findings:
        entry = triage.get(f.id)
        if not entry:
            counts["open"] += 1
            continue
        decision = entry.get("decision")
        if decision not in _DECISION_STATUS:
            counts["open"] += 1
            continue
        f.status = _DECISION_STATUS[decision]
        if decision == "confirmed":
            f.confidence = "direct"
        stamp = f"Triaje: {decision} por {entry.get('by', 'n/d')} ({entry.get('date', 'n/d')})"
        reason = entry.get("reason", "")
        note = f"{stamp}: {reason}".strip(": ")
        if note not in f.notes:
            f.notes = (f.notes + " " + note).strip()
        f.log(f"triage:{decision}", entry.get("date", now_iso()))
        counts[decision] = counts.get(decision, 0) + 1
    return counts


def append_decision(cfg: Config, finding_id: str, decision: str, reason: str, by: str) -> Path:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"decisión inválida: {decision}; use una de {VALID_DECISIONS}")
    path = _triage_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"entries": []}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            pass
    entries = [e for e in data.get("entries", []) if e.get("finding_id") != finding_id]
    entries.append({
        "finding_id": finding_id,
        "decision": decision,
        "reason": reason,
        "by": by or "revisor",
        "date": now_iso(),
    })
    data["entries"] = entries
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return path


def open_findings(findings: List[Finding]) -> List[Finding]:
    """Hallazgos que siguen 'abiertos' (no descartados como falso positivo)."""
    return [f for f in findings if f.status != "false-positive"]
