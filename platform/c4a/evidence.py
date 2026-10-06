"""Gestor de evidencia (Fase 5): cada pieza con fuente, fecha, hash y estado.

Separa evidencia directa de indirecta y fija un nivel de confianza. Los
extractos se guardan con secretos enmascarados. El crudo persiste bajo
`evidence/<run_id>/` con un MANIFEST que lista hash y procedencia de cada
archivo, de modo que un tercero pueda verificar que nada se alteró.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .model import Evidence
from .util import now_iso, sha256_file, sha256_text, short_id


class EvidenceStore:
    def __init__(self, run_id: str, raw_dir: Path, target: Path):
        self.run_id = run_id
        self.target = target
        self.run_dir = raw_dir / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._items: Dict[str, Evidence] = {}

    def from_file(
        self,
        path: Path,
        *,
        etype: str,
        responsible_role: str,
        result: str,
        description: str,
        relevance: str,
        excerpt_masked: str = "",
        line: int | None = None,
        confidence: str = "direct",
    ) -> Evidence:
        rel = path.relative_to(self.target).as_posix()
        location = f"{rel}:{line}" if line else rel
        file_hash = sha256_file(path)
        eid = short_id("E", self.run_id, location, file_hash, etype)
        ev = Evidence(
            id=eid,
            type=etype,
            source=f"file:{rel}",
            location=location,
            collected_at=now_iso(),
            sha256=file_hash,
            responsible_role=responsible_role,
            scope="in-scope",
            status="collected",
            result=result,
            description=description,
            relevance=relevance,
            confidence=confidence,
            excerpt_masked=excerpt_masked,
        )
        self._items[eid] = ev
        return ev

    def from_command(
        self,
        *,
        command: str,
        output: str,
        etype: str,
        responsible_role: str,
        result: str,
        description: str,
        relevance: str,
        confidence: str = "direct",
    ) -> Evidence:
        out_hash = sha256_text(output)
        eid = short_id("E", self.run_id, command, out_hash)
        fname = self.run_dir / f"{eid}.txt"
        with open(fname, "w", encoding="utf-8") as fh:
            fh.write(f"# comando: {command}\n# recolectado: {now_iso()}\n\n{output}")
        ev = Evidence(
            id=eid,
            type=etype,
            source=f"command:{command}",
            location=fname.name,
            collected_at=now_iso(),
            sha256=out_hash,
            responsible_role=responsible_role,
            scope="in-scope",
            status="collected",
            result=result,
            description=description,
            relevance=relevance,
            confidence=confidence,
        )
        self._items[eid] = ev
        return ev

    def items(self) -> List[Evidence]:
        return list(self._items.values())

    def write_manifest(self) -> Path:
        manifest = self.run_dir / "MANIFEST.json"
        data = {
            "run_id": self.run_id,
            "generated_at": now_iso(),
            "count": len(self._items),
            "items": [e.to_dict() for e in self._items.values()],
        }
        with open(manifest, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        # sidecars .sha256 para verificación externa rápida
        sha_index = self.run_dir / "SHA256SUMS.txt"
        with open(sha_index, "w", encoding="utf-8") as fh:
            for e in self._items.values():
                fh.write(f"{e.sha256}  {e.location}\n")
        return manifest
