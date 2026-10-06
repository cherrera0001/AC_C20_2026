"""Reproducción POR HALLAZGO (complementa la reproducción por ciclo).

Para cada hallazgo re-ejecuta su comprobación de forma NATIVA: vuelve a leer el
componente, re-calcula su hash y re-corre el mismo detector acotado a ese único
archivo. Si el mismo id reaparece, el hallazgo queda 'reproducido'; si el
archivo cambió o desapareció, 'no-reproducido' o 'cambió'. Es determinista y
multiplataforma (no depende de que exista grep en el sistema).

Los hallazgos de SCA (CVE) no se reproducen aquí: dependen de una base externa
y se re-verifican re-escaneando con el motor SCA.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from .config import Config
from .detectors import REGISTRY
from .detectors.base import DetectorContext, FileBlob
from .evidence import EvidenceStore
from .scope import ScopeManager
from .util import now_iso, sha256_file


def verify_run(cfg: Config, run_id: str, only: Optional[str] = None) -> Dict:
    findings_path = cfg.phase["state"] / "findings" / f"{run_id}.json"
    if not findings_path.exists():
        raise ValueError(f"no hay hallazgos guardados para {run_id}")
    with open(findings_path, "r", encoding="utf-8") as fh:
        stored = json.load(fh)
    records = stored.get("findings", [])
    if only:
        records = [r for r in records if r["id"] == only]
        if not records:
            raise ValueError(f"el hallazgo {only} no está en la corrida {run_id}")

    manifest = _load_manifest(cfg, run_id)
    scope = ScopeManager(cfg)
    tmp_raw = Path(tempfile.mkdtemp(prefix="c4a_verify_"))
    results: List[Dict] = []
    try:
        store = EvidenceStore("_verify", tmp_raw, cfg.target)
        for rec in records:
            results.append(_verify_one(cfg, scope, store, rec, manifest))
    finally:
        shutil.rmtree(tmp_raw, ignore_errors=True)

    counts: Dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    report = {
        "run_id": run_id,
        "verified_at": now_iso(),
        "counts": counts,
        "results": results,
    }
    out_dir = cfg.phase["state"] / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{run_id}.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return report


def _load_manifest(cfg: Config, run_id: str) -> Dict[str, str]:
    """Mapa id_evidencia → sha256 desde el MANIFEST de la corrida."""
    mpath = cfg.phase["evidence_raw"] / run_id / "MANIFEST.json"
    if not mpath.exists():
        return {}
    try:
        with open(mpath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return {it["id"]: it["sha256"] for it in data.get("items", []) if it.get("id")}


def _verify_one(cfg: Config, scope: ScopeManager, store: EvidenceStore, rec: Dict,
                manifest: Dict[str, str]) -> Dict:
    fid = rec["id"]
    source = rec.get("source", "")
    component = rec.get("component", "")

    if source.startswith("sca:"):
        return {"id": fid, "component": component, "status": "external",
                "detail": "CVE: re-verificar re-escaneando con el motor SCA"}

    detector_cls = REGISTRY.get(source)
    if not detector_cls:
        return {"id": fid, "component": component, "status": "unknown-detector",
                "detail": f"detector '{source}' no está en el registro"}

    path = (cfg.target / component)
    if not path.exists():
        return {"id": fid, "component": component, "status": "not-reproduced",
                "detail": "el componente ya no existe"}

    # hash actual vs el de la evidencia original (del MANIFEST de la corrida)
    stored_hashes = {manifest[eid] for eid in rec.get("evidence", []) if eid in manifest}
    try:
        current_hash = sha256_file(path)
    except OSError:
        current_hash = ""
    hash_match = current_hash in stored_hashes if stored_hashes else None

    text = scope.read_text(path)
    fb = FileBlob(path=path, rel=component, text=text)
    ctx = DetectorContext(cfg=cfg, scope=scope, evidence=store, files=[fb])
    try:
        got_ids = {f.id for f in detector_cls().run(ctx)}
    except Exception as exc:
        return {"id": fid, "component": component, "status": "error", "detail": repr(exc)}

    if fid in got_ids:
        status = "reproduced"
        detail = "mismo id re-detectado" + ("" if hash_match else "; contenido del archivo cambió")
    else:
        status = "not-reproduced"
        detail = "el detector ya no produce este hallazgo (posible remediación o cambio)"
    return {"id": fid, "component": component, "status": status,
            "hash_match": hash_match, "detail": detail}
