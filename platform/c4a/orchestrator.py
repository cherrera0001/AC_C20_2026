"""Orquestador principal: encadena las fases y produce una ejecución reproducible.

Flujo de una corrida:
  alcance → inventario → detección (+ evidencia) → riesgo → correlación →
  matriz de controles → reportes → manifiesto de evidencia → ledger.

El `result_hash` se calcula SOLO del contenido (ids de hallazgo + hashes de
evidencia), nunca de relojes ni rutas, para que dos corridas sobre el mismo
objetivo inalterado produzcan el mismo hash: esa es la prueba de reproducción.
"""
from __future__ import annotations

import platform
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

from . import correlation, report, risk
from . import sca as sca_mod
from . import triage as triage_mod
from .config import Config
from .detectors import select
from .detectors.base import DetectorContext, FileBlob
from .evidence import EvidenceStore
from .inventory import InventoryManager
from .ledger import Ledger
from .model import Finding, Run
from .scope import ScopeManager
from .util import now_iso, sha256_text, short_id


def _result_hash(findings: List[Finding], ev_items) -> str:
    # Los hallazgos de SCA (CVE) dependen de una base externa que cambia en el
    # tiempo: se excluyen para que el hash mida la reproducibilidad del análisis
    # ESTÁTICO. Los de CVE se verifican re-escaneando, no por hash de ciclo.
    parts = []
    for f in sorted(findings, key=lambda x: x.id):
        if f.source.startswith("sca:"):
            continue
        ev_hashes = "+".join(sorted(e.sha256 for e in ev_items if e.id in f.evidence))
        parts.append(f"{f.id}:{f.severity}:{ev_hashes}")
    return sha256_text("\n".join(parts))


def _load_corpus(scope: ScopeManager) -> List[FileBlob]:
    corpus: List[FileBlob] = []
    for path in scope.iter_files():
        text = scope.read_text(path)
        corpus.append(FileBlob(path=path, rel=scope.rel(path), text=text))
    return corpus


def run_audit(cfg: Config, person: str = "", command: str = "run") -> Tuple[Run, List[Finding], Dict]:
    t0 = time.time()
    started = now_iso()
    run_id = f"RUN-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{short_id('', str(cfg.target), started, length=4).lstrip('-')}"
    errors: List[str] = []

    for d in cfg.phase.values():
        d.mkdir(parents=True, exist_ok=True)

    scope = ScopeManager(cfg)
    inventory = InventoryManager(scope).build()

    corpus = _load_corpus(scope)
    store = EvidenceStore(run_id, cfg.phase["evidence_raw"], cfg.target)
    ctx = DetectorContext(cfg=cfg, scope=scope, evidence=store, files=corpus)

    findings: List[Finding] = []
    for det in select(cfg.detectors):
        try:
            findings.extend(det.run(ctx))
        except Exception as exc:  # un detector no debe tumbar la corrida
            errors.append(f"detector {det.id}: {exc!r}")

    # SCA: correlación con CVE reales si hay motor; si no, degrada a manual.
    sca_mgr = sca_mod.SCAManager(cfg)
    sca_refs, sca_meta = sca_mgr.run(scope)
    if sca_meta.get("status") == "error":
        errors.append(f"sca: {sca_meta.get('note')}")
    if sca_refs:
        sca_mod.enrich_dependency_findings(findings, sca_refs)
        findings.extend(sca_mod.to_findings(sca_refs, store, sca_meta))

    risk.assess(findings)
    triage_counts = triage_mod.apply_triage(findings, triage_mod.load_triage(cfg))
    corr = correlation.correlate(findings, cfg)
    matrix = correlation.controls_matrix(findings, cfg, started)
    ev_items = store.items()
    ev_by_id = {e.id: e for e in ev_items}

    report.write_inventory(cfg, inventory)
    report.write_findings_json(cfg, run_id, findings, corr)
    report.write_matrix_csv(cfg, matrix)
    report.write_finding_cards(cfg, findings, ev_by_id)
    store.write_manifest()

    rhash = _result_hash(findings, ev_items)
    finished = now_iso()
    run = Run(
        run_id=run_id,
        started_at=started,
        finished_at=finished,
        person=person or cfg.person,
        target=str(cfg.target),
        command=command,
        params={"detectors": cfg.detectors, "normativas": cfg.normativas},
        result_summary={
            "findings": len(findings),
            "by_severity": risk.summary(findings),
            "evidence_items": len(ev_items),
            "files_scanned": inventory["totals"]["files_scanned"],
            "controls_evaluated": len(matrix),
            "sca": {"engine": sca_meta.get("engine"), "status": sca_meta.get("status"),
                    "packages": sca_meta.get("packages", 0),
                    "cve_findings": sum(1 for f in findings if f.source.startswith("sca:"))},
            "triage": triage_counts,
        },
        errors=errors,
        duration_s=round(time.time() - t0, 3),
        hash=rhash,
        status="completed" if not errors else "completed-with-errors",
        tool_versions={"python": sys.version.split()[0], "c4a": _version()},
        environment={"platform": platform.platform(), "os": platform.system()},
    )

    report.write_reports(cfg, run, findings, inventory, matrix, corr, ev_items)
    Ledger(cfg.phase["state"]).append(run)
    return run, findings, {"inventory": inventory, "matrix": matrix, "correlation": corr}


def reproduce(cfg: Config, run_id: str) -> Dict:
    """Re-ejecuta la auditoría y compara con una corrida previa por id y hash."""
    ledger = Ledger(cfg.phase["state"])
    prior = ledger.get(run_id)
    if not prior:
        raise ValueError(f"no existe la corrida {run_id} en el ledger")
    prior_findings_path = cfg.phase["state"] / "findings" / f"{run_id}.json"
    import json
    prior_ids = set()
    if prior_findings_path.exists():
        with open(prior_findings_path, "r", encoding="utf-8") as fh:
            prior_ids = {f["id"] for f in json.load(fh).get("findings", [])}

    new_run, new_findings, _ = run_audit(cfg, command=f"reproduce:{run_id}")
    new_ids = {f.id for f in new_findings}

    same_hash = new_run.hash == prior["hash"]
    comparison = {
        "prior_run": run_id,
        "new_run": new_run.run_id,
        "prior_hash": prior["hash"],
        "new_hash": new_run.hash,
        "reproduced": same_hash,
        "stable_ids": sorted(prior_ids & new_ids),
        "only_in_prior": sorted(prior_ids - new_ids),
        "only_in_new": sorted(new_ids - prior_ids),
    }
    repro_dir = cfg.phase["state"] / "repro"
    repro_dir.mkdir(parents=True, exist_ok=True)
    with open(repro_dir / f"{run_id}_vs_{new_run.run_id}.json", "w", encoding="utf-8") as fh:
        json.dump(comparison, fh, ensure_ascii=False, indent=2)
    return comparison


def _version() -> str:
    from . import __version__
    return __version__
