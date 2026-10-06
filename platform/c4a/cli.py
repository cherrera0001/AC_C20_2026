"""Interfaz de línea de comandos del orquestador C4A.

Subcomandos:
  init       valida la config y prepara las carpetas de fase
  run        ejecuta un ciclo completo de auditoría y escribe los entregables
  reproduce  re-ejecuta y compara con una corrida previa (por id y hash)
  catalog    lista detectores y normativas disponibles
  runs       lista las ejecuciones registradas en el ledger
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from . import config as config_mod
from . import orchestrator
from . import reproduction
from . import triage as triage_mod
from .detectors import catalog as det_catalog
from .ledger import Ledger

_DEFAULT_CONFIG = "config/audit.example.json"


def _load(args) -> "config_mod.Config":
    path = Path(args.config)
    if not path.exists():
        print(f"✗ no existe la config: {path}", file=sys.stderr)
        raise SystemExit(2)
    return config_mod.load(path)


def _cmd_init(args) -> int:
    cfg = _load(args)
    for name, d in cfg.phase.items():
        d.mkdir(parents=True, exist_ok=True)
    print(f"✓ init · objetivo: {cfg.target}")
    print(f"  salida: {cfg.output_root}")
    print(f"  normativas: {', '.join(cfg.normativas)}")
    print(f"  detectores: {', '.join(cfg.detectors)}")
    print(f"  solo lectura: {cfg.read_only}")
    return 0


def _cmd_run(args) -> int:
    cfg = _load(args)
    run, findings, _ = orchestrator.run_audit(cfg, person=args.person or cfg.person)
    s = run.result_summary
    print(f"✓ auditoría {run.run_id} · {run.status} · {run.duration_s}s")
    print(f"  archivos analizados: {s['files_scanned']}")
    print(f"  hallazgos: {s['findings']}  {json.dumps(s['by_severity'], ensure_ascii=False)}")
    tri = s.get("triage", {})
    if tri.get("false-positive") or tri.get("accepted-risk") or tri.get("confirmed"):
        print(f"  triaje: {json.dumps(tri, ensure_ascii=False)}")
    sca = s.get("sca", {})
    if sca.get("status") not in (None, "skipped"):
        print(f"  sca: {sca.get('engine')} {sca.get('status')} · {sca.get('cve_findings',0)} hallazgo(s) CVE")
    print(f"  evidencia: {s['evidence_items']} pieza(s) · controles: {s['controls_evaluated']}")
    print(f"  result_hash: {run.hash}")
    if run.errors:
        print(f"  ⚠ errores: {run.errors}")
    print(f"  informe: {cfg.phase['informe'] / 'README.md'}")
    return 0


def _cmd_reproduce(args) -> int:
    cfg = _load(args)
    cmp = orchestrator.reproduce(cfg, args.run)
    estado = "REPRODUCIDO (hash idéntico)" if cmp["reproduced"] else "DIFERENCIAS detectadas"
    print(f"{'✓' if cmp['reproduced'] else '⚠'} {estado}")
    print(f"  previa {cmp['prior_run']} → nueva {cmp['new_run']}")
    print(f"  hash previo: {cmp['prior_hash'][:16]}…  nuevo: {cmp['new_hash'][:16]}…")
    print(f"  estables: {len(cmp['stable_ids'])} · solo-previa: {len(cmp['only_in_prior'])} · solo-nueva: {len(cmp['only_in_new'])}")
    return 0 if cmp["reproduced"] else 1


def _cmd_verify(args) -> int:
    cfg = _load(args)
    report = reproduction.verify_run(cfg, args.run, only=args.finding or None)
    c = report["counts"]
    print(f"Verificación por hallazgo · corrida {args.run} · {report['verified_at']}")
    print(f"  {json.dumps(c, ensure_ascii=False)}")
    for r in report["results"]:
        if r["status"] not in ("reproduced",):
            print(f"  · {r['id']} [{r['status']}] {r['component']} — {r.get('detail','')}")
    repro = c.get("reproduced", 0)
    total = sum(c.values())
    print(f"  reproducidos {repro}/{total}")
    return 0


def _cmd_triage(args) -> int:
    cfg = _load(args)
    path = triage_mod.append_decision(cfg, args.finding, args.decision, args.reason, args.by)
    print(f"✓ triaje registrado: {args.finding} → {args.decision}")
    print(f"  motivo: {args.reason or '(sin motivo)'} · por: {args.by or 'revisor'}")
    print(f"  archivo: {path}")
    print("  Se aplica en la próxima corrida (c4a run).")
    return 0


def _cmd_catalog(args) -> int:
    print("Detectores:")
    for d in det_catalog():
        print(f"  - {d['id']:16} {d['title']} ({d['finding_type']})")
    cfg_path = Path(args.config)
    if cfg_path.exists():
        cfg = config_mod.load(cfg_path)
        print("\nNormativas en catálogo:")
        for k, v in cfg.norm_catalog.items():
            if k.startswith("_"):
                continue
            print(f"  - {k:12} {v.get('nombre','')}")
    return 0


def _cmd_runs(args) -> int:
    cfg = _load(args)
    for r in Ledger(cfg.phase["state"]).all():
        s = r["result_summary"]
        print(f"{r['run_id']} · {r['started_at']} · {s['findings']} hallazgos · hash {r['hash'][:12]}… · {r['status']}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="c4a", description="Plataforma de auditoría C4A")
    p.add_argument("--version", action="version", version=f"c4a {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, func, extra in [
        ("init", _cmd_init, False),
        ("run", _cmd_run, True),
        ("reproduce", _cmd_reproduce, "repro"),
        ("verify", _cmd_verify, "verify"),
        ("triage", _cmd_triage, "triage"),
        ("catalog", _cmd_catalog, False),
        ("runs", _cmd_runs, False),
    ]:
        sp = sub.add_parser(name)
        sp.add_argument("--config", default=_DEFAULT_CONFIG, help="ruta a la config JSON del encargo")
        if extra is True:
            sp.add_argument("--person", default="", help="quién ejecuta (para el ledger)")
        if extra == "repro":
            sp.add_argument("--run", required=True, help="run_id de la corrida a reproducir")
        if extra == "verify":
            sp.add_argument("--run", required=True, help="run_id a verificar por hallazgo")
            sp.add_argument("--finding", default="", help="verificar solo este id de hallazgo")
        if extra == "triage":
            sp.add_argument("--finding", required=True, help="id del hallazgo a triar")
            sp.add_argument("--decision", required=True,
                            choices=list(triage_mod.VALID_DECISIONS),
                            help="false-positive | accepted-risk | confirmed")
            sp.add_argument("--reason", default="", help="motivo de la decisión")
            sp.add_argument("--by", default="", help="quién decide")
        sp.set_defaults(func=func)

    args = p.parse_args(argv)
    return args.func(args)
