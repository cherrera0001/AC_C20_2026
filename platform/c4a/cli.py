"""Interfaz de línea de comandos del orquestador C4A.

Subcomandos:
  init       valida la config y prepara las carpetas de fase
  run        ejecuta un ciclo completo de auditoría y escribe los entregables
  reproduce  re-ejecuta y compara con una corrida previa (por id y hash)
  catalog    lista detectores y normativas disponibles
  runs       lista las ejecuciones registradas en el ledger
  alcance    S01: propone, corrige, firma y consulta el alcance (scope/)
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
from . import alcance as alcance_mod
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
    print(f"  sarif: {cfg.phase['informe'] / 'hallazgos.sarif.json'}")
    if args.fail_on:
        from . import risk
        g = risk.gate(findings, args.fail_on)
        if g["triggered"]:
            print(f"  ✗ compuerta: {g['count']} hallazgo(s) abiertos en o sobre {g['threshold']}")
            return 2
        print(f"  ✓ compuerta: ningún hallazgo abierto en o sobre {g['threshold']}")
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


def _cmd_alcance(args) -> int:
    """S01 — El alcance: la herramienta propone; el auditor corrige y firma."""
    from datetime import date
    for flujo in (sys.stdout, sys.stderr):
        # una consola cp1252 no debe hacer fallar la salida después de una acción ya hecha
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    raiz = Path(args.raiz)
    ref = date.fromisoformat(args.fecha_referencia) if getattr(args, "fecha_referencia", "") else None
    try:
        if args.accion == "proponer":
            c = alcance_mod.proponer(raiz, ref)
            pend = sum(1 for f in c["filas"] if alcance_mod.es_pendiente(f))
            print(f"✓ alcance propuesto · {len(c['filas'])} filas · {pend} pendientes · estado {alcance_mod.estado_efectivo(raiz)}")
            print(f"  {alcance_mod.ARCHIVO_JSON} · {alcance_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            f = alcance_mod.corregir(raiz, args.fila, args.campo, args.valor, args.motivo, args.autor, args.fecha or None)
            print(f"✓ corrección registrada en {f['id']} ({args.campo}) · alcance «revisado»")
        elif args.accion == "revisar":
            alcance_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ alcance «revisado»")
        elif args.accion == "firmar":
            r = alcance_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ alcance firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  pendientes al firmar: {r['pendientes_al_firmar']} · {r['nota']}")
        elif args.accion == "verificar":
            v = alcance_mod.verificar(raiz)
            print(f"{v['estado']} · sha256 actual {v['sha256_actual']}")
            if v["estado"].startswith("revisado"):
                return 3
        elif args.accion == "consultar":
            r = alcance_mod.consultar(raiz, args.tipo, args.valor)
            fila = f"{r['fila']['id']} ({r['fila']['fuente']})" if r["fila"] else "ninguna"
            print(f"{r['respuesta']} · fila: {fila} · firmado: {'sí' if r['firmado'] else 'no'}")
            if r["motivo"]:
                print(f"  motivo: {r['motivo']}")
        elif args.accion == "compuerta":
            c = alcance_mod.evaluar_compuerta(raiz, ref)
            print(f"compuerta {c['resultado']} · firma: {c['firma']} · completitud: {c['completitud']} · ventana: {c['ventana']}")
            for m in c["motivos"]:
                print(f"  motivo: {m}")
    except alcance_mod.AlcanceError as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_alcance(sub) -> None:
    sp = sub.add_parser("alcance", help="S01 — proponer, corregir, firmar y consultar el alcance")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    a = nuevo("proponer", "deriva el borrador desde scope/alcance.md y scope/autorizacion.md")
    a.add_argument("--fecha-referencia", dest="fecha_referencia", default="", help="AAAA-MM-DD para la ventana")
    a = nuevo("corregir", "registra una corrección del auditor")
    a.add_argument("--fila", required=True)
    a.add_argument("--campo", required=True, choices=list(alcance_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    a.add_argument("--motivo", required=True)
    a.add_argument("--autor", required=True)
    a.add_argument("--fecha", default="")
    a = nuevo("revisar", "marca el alcance «revisado» sin cambiar filas")
    a.add_argument("--autor", required=True)
    a.add_argument("--motivo", required=True)
    a.add_argument("--fecha", default="")
    a = nuevo("firmar", "firma el alcance revisado (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "compara la huella firmada con los bytes guardados")
    a = nuevo("consultar", "¿está dentro, fuera o pendiente?")
    a.add_argument("--tipo", required=True, choices=["activo", "dominio", "marco", "obligacion", "exclusion"])
    a.add_argument("--valor", required=True)
    a = nuevo("compuerta", "evalúa la compuerta de autorización (solo lectura)")
    a.add_argument("--fecha-referencia", dest="fecha_referencia", default="", help="AAAA-MM-DD")
    sp.set_defaults(func=_cmd_alcance)


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
            sp.add_argument("--fail-on", default="", dest="fail_on",
                            choices=["CRITICO", "ALTO", "MEDIO", "BAJO", "INFORMACIONAL"],
                            help="código de salida !=0 si hay hallazgos abiertos en o sobre esta severidad (para CI)")
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
    _parser_alcance(sub)

    args = p.parse_args(argv)
    return args.func(args)
