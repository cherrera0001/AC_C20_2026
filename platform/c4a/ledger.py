"""Ledger de ejecución: append-only, para reproducibilidad (sec. 13).

Cada corrida deja un registro inmutable en `.c4a/runs.jsonl`. No se edita ni
se borra: solo se agrega. Así el historial de auditoría es verificable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .model import Run


class Ledger:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.state_dir / "runs.jsonl"

    def append(self, run: Run) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(run.to_dict(), ensure_ascii=False) + "\n")

    def all(self) -> List[Dict]:
        if not self.path.exists():
            return []
        out: List[Dict] = []
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def get(self, run_id: str) -> Optional[Dict]:
        for r in self.all():
            if r.get("run_id") == run_id:
                return r
        return None

    def last(self) -> Optional[Dict]:
        runs = self.all()
        return runs[-1] if runs else None
