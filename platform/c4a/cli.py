"""Interfaz de línea de comandos del orquestador C4A.

Subcomandos:
  init       valida la config y prepara las carpetas de fase
  run        ejecuta un ciclo completo de auditoría y escribe los entregables
  reproduce  re-ejecuta y compara con una corrida previa (por id y hash)
  catalog    lista detectores y normativas disponibles
  runs       lista las ejecuciones registradas en el ledger
  alcance    S01: propone, corrige, firma y consulta el alcance (scope/)
  registro   S02: abre, alimenta, corrige, firma y entrega el registro (02_evidencia/)
  enunciado  S03: propone riesgos desde el registro, corrige, firma y entrega (03_hallazgos/)
  cita       S04: ubica cada riesgo en un marco con nombre y versión (03_hallazgos/)
  perfil     S05: lee el activo con las seis funciones del NIST CSF 2.0 (03_hallazgos/)
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
from . import registro as registro_mod
from . import enunciado as enunciado_mod
from . import cita as cita_mod
from . import perfil as perfil_mod
from . import lista as lista_mod
from . import encargo as encargo_mod
from . import frases as frases_mod
from . import borrador as borrador_mod
from . import cierre as cierre_mod
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


def _consola() -> None:
    for flujo in (sys.stdout, sys.stderr):
        # una consola cp1252 no debe hacer fallar la salida después de una acción ya hecha
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")


def _cmd_registro(args) -> int:
    """S02 — El registro: la herramienta propone; el auditor corrige y firma."""
    from datetime import date
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            ref = date.fromisoformat(args.fecha_referencia) if args.fecha_referencia else None
            c = registro_mod.abrir(raiz, ref)
            nc = len(registro_mod.no_consta_vigentes(c))
            hechos = sum(1 for e in c["entradas"] if e["clase"] == registro_mod.HECHO)
            print(f"✓ registro abierto · {nc} entradas no constan · {hechos} hechos · "
                  f"{len(c['rechazos'])} rechazos · estado {registro_mod.estado_efectivo(raiz)}")
            print(f"  {registro_mod.ARCHIVO_JSON} · {registro_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "aportar":
            r = registro_mod.aportar(raiz, args.activo, args.dominio, args.afirmacion, args.resultado,
                                     args.evidencia, args.tipo, args.fecha_recoleccion, args.autor,
                                     args.origen or None, args.corrida or None, args.sin_copia, args.fecha or None)
            if r["aceptada"]:
                print(f"✓ evidencia {r['evidencia']} aportada a la entrada {r['entrada']} (borrador)")
            else:
                print(f"✗ evidencia rechazada: {r['motivo']} · {r['regla']}"
                      + (f" · fila {r['fila_alcance']}" if r["fila_alcance"] else ""))
                print("  el rechazo quedó anotado en el registro")
        elif args.accion == "corregir":
            e = registro_mod.corregir(raiz, args.entrada, args.campo, args.valor, args.motivo, args.autor,
                                      args.fecha or None)
            print(f"✓ corrección registrada en {e['id']} ({args.campo}) · entrada «revisado»")
        elif args.accion in ("descartar", "restablecer"):
            f = registro_mod.descartar if args.accion == "descartar" else registro_mod.restablecer
            e = f(raiz, args.entrada, args.motivo, args.autor, args.fecha or None)
            print(f"✓ {e['id']} {'descartada' if args.accion == 'descartar' else 'restablecida'} (no se borra nada)")
        elif args.accion == "revisar":
            registro_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ registro «revisado»")
        elif args.accion == "firmar":
            r = registro_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ registro firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  no consta al firmar: {r['no_consta_al_firmar']} · {r['nota']}")
        elif args.accion == "verificar":
            v = registro_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            for e in v["entradas_alteradas"]:
                print(f"  {registro_mod.MARCA_ALTERADA}: {e}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = registro_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{len(d['entradas'])} entradas vigentes para S03 · estado {d['estado']}")
                for e in d["entradas"]:
                    print(f"  {e['id']} · {e['clase']} · {e['dominio']['valor']} · {e['resultado']}")
    except (registro_mod.RegistroError, alcance_mod.AlcanceError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_registro(sub) -> None:
    sp = sub.add_parser("registro", help="S02 — abrir, aportar, corregir, firmar y entregar el registro")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "deriva el registro del alcance de S01 (o del mínimo de referencia)")
    a.add_argument("--fecha-referencia", dest="fecha_referencia", default="",
                   help="AAAA-MM-DD para reevaluar la compuerta (por defecto se conserva la guardada)")
    a = nuevo("aportar", "aporta una evidencia; si no es admisible, anota el rechazo")
    a.add_argument("--activo", required=True)
    a.add_argument("--dominio", required=True, help="id A-… de la fila del alcance, un texto del dominio o «activo»")
    a.add_argument("--afirmacion", required=True)
    a.add_argument("--resultado", required=True, choices=list(registro_mod.RESULTADOS_EVIDENCIA))
    a.add_argument("--evidencia", required=True, help="ruta del archivo de evidencia")
    a.add_argument("--tipo", required=True, choices=list(registro_mod.TIPOS_EVIDENCIA))
    a.add_argument("--fecha-recoleccion", dest="fecha_recoleccion", required=True, help="AAAA-MM-DD")
    a.add_argument("--autor", required=True)
    a.add_argument("--origen", default="", help="de dónde viene (obligatorio en documental)")
    a.add_argument("--corrida", default="", help="RUN-… si la evidencia sale de una corrida de c4a")
    a.add_argument("--sin-copia", dest="sin_copia", action="store_true", help="declara referencia sin copia")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige la afirmación, el resultado o el motivo de una entrada")
    a.add_argument("--entrada", required=True)
    a.add_argument("--campo", required=True, choices=list(registro_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    for nombre, ayuda in (("descartar", "marca una entrada descartada; no la borra"),
                          ("restablecer", "revierte un descarte")):
        a = nuevo(nombre, ayuda)
        a.add_argument("--entrada", required=True)
        autor_motivo(a)
    a = nuevo("revisar", "marca el registro «revisado»")
    autor_motivo(a)
    a = nuevo("firmar", "firma el registro revisado (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula la huella del registro y de cada evidencia")
    a = nuevo("entregar", "entradas vigentes para S03")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_registro)


def _cmd_enunciado(args) -> int:
    """S03 — El enunciado: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = enunciado_mod.abrir(raiz, args.fecha or None)
            print(f"✓ enunciado abierto · {len(c['enunciados'])} enunciados · "
                  f"{len(c['vacios'])} vacíos heredados · estado {enunciado_mod.estado_efectivo(raiz)}")
            print(f"  {enunciado_mod.ARCHIVO_JSON} · {enunciado_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            e = enunciado_mod.corregir(raiz, args.enunciado, args.campo, args.valor, args.motivo,
                                       args.autor, args.fecha or None)
            print(f"✓ corrección registrada en {e['id']} ({args.campo}) · enunciado «revisado»")
        elif args.accion in ("descartar", "restablecer"):
            f = enunciado_mod.descartar if args.accion == "descartar" else enunciado_mod.restablecer
            e = f(raiz, args.enunciado, args.motivo, args.autor, args.fecha or None)
            print(f"✓ {e['id']} {'descartado' if args.accion == 'descartar' else 'restablecido'} "
                  "(no se borra nada)")
        elif args.accion == "revisar":
            enunciado_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ enunciado «revisado»")
        elif args.accion == "firmar":
            r = enunciado_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ enunciado firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  enunciados al firmar: {r['enunciados_al_firmar']} · vacíos: {r['vacios_al_firmar']} · "
                  f"{r['nota']}")
        elif args.accion == "verificar":
            v = enunciado_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            for e in v["evidencias_alteradas"]:
                print(f"  {enunciado_mod.MARCA_ALTERADA}: {e}")
            for e in v["hechos_no_vigentes"]:
                print(f"  {enunciado_mod.MARCA_HECHO_NO_VIGENTE}: {e}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = enunciado_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{len(d['enunciados'])} enunciados vigentes para S04 · estado {d['estado']}")
                for e in d["enunciados"]:
                    print(f"  {e['id']} · {e['dominio']['valor']} · {e['hecho']['resultado']}")
    except (enunciado_mod.EnunciadoError, registro_mod.RegistroError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_enunciado(sub) -> None:
    sp = sub.add_parser("enunciado", help="S03 — abrir, corregir, firmar y entregar el enunciado")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "propone un riesgo por hecho vigente de la entrega de S02")
    a.add_argument("--fecha", default="", help="AAAA-MM-DDThh:mm:ssZ (solo para el historial; uso determinista)")
    a = nuevo("corregir", "corrige la condición, la consecuencia, el criterio o el impacto")
    a.add_argument("--enunciado", required=True)
    a.add_argument("--campo", required=True, choices=list(enunciado_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    for nombre, ayuda in (("descartar", "marca un enunciado descartado; no lo borra"),
                          ("restablecer", "revierte un descarte")):
        a = nuevo(nombre, ayuda)
        a.add_argument("--enunciado", required=True)
        autor_motivo(a)
    a = nuevo("revisar", "marca el enunciado «revisado»")
    autor_motivo(a)
    a = nuevo("firmar", "firma el enunciado revisado con criterio e impacto completos (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula la huella del producto, la entrega de S02 y cada evidencia citada")
    a = nuevo("entregar", "enunciados vigentes para S04")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_enunciado)


def _cmd_cita(args) -> int:
    """S04 — La cita: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = cita_mod.abrir(raiz, args.fecha or None)
            pend = sum(1 for x in c["citas"] if x["estado_identificador"] == cita_mod.PENDIENTE)
            print(f"✓ cita abierta · {len(c['citas'])} citas · {pend} identificadores pendientes · "
                  f"estado {cita_mod.estado_efectivo(raiz)}")
            print(f"  {cita_mod.ARCHIVO_JSON} · {cita_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            x = cita_mod.corregir(raiz, args.cita, args.campo, args.valor, args.motivo,
                                  args.autor, args.fecha or None)
            print(f"✓ corrección registrada en {x['id']} ({args.campo}) · cita «revisado»")
        elif args.accion == "anadir":
            x = cita_mod.anadir_correspondencia(raiz, args.cita, args.marco, args.version,
                                                args.identificador, args.fundamento, args.motivo,
                                                args.autor, args.fecha or None)
            print(f"✓ correspondencia añadida a {x['id']} ({len(x['correspondencias'])} adicionales)")
        elif args.accion in ("descartar", "restablecer"):
            f = cita_mod.descartar if args.accion == "descartar" else cita_mod.restablecer
            x = f(raiz, args.cita, args.motivo, args.autor, args.fecha or None)
            print(f"✓ {x['id']} {'descartada' if args.accion == 'descartar' else 'restablecida'} "
                  "(no se borra nada)")
        elif args.accion == "revisar":
            cita_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ cita «revisada»")
        elif args.accion == "firmar":
            r = cita_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ cita firmada por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  citas al firmar: {r['citas_al_firmar']} · pendientes: {r['pendientes_al_firmar']} · "
                  f"{r['nota']}")
        elif args.accion == "verificar":
            v = cita_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            for e in v["evidencias_alteradas"]:
                print(f"  {cita_mod.MARCA_ALTERADA}: {e}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = cita_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{len(d['citas'])} citas vigentes para S05 · estado {d['estado']}")
                for x in d["citas"]:
                    print(f"  {x['id']} · {x['marco']} {x['version']} · {x['identificador']}")
    except (cita_mod.CitaError, enunciado_mod.EnunciadoError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_cita(sub) -> None:
    sp = sub.add_parser("cita", help="S04 — abrir, corregir, firmar y entregar la cita")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "propone una cita por riesgo vigente de la entrega de S03")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige el marco, la versión, el identificador o el fundamento")
    a.add_argument("--cita", required=True)
    a.add_argument("--campo", required=True, choices=list(cita_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("anadir", "añade una correspondencia adicional al riesgo")
    a.add_argument("--cita", required=True)
    a.add_argument("--marco", required=True)
    a.add_argument("--version", required=True)
    a.add_argument("--identificador", required=True)
    a.add_argument("--fundamento", required=True)
    autor_motivo(a)
    for nombre, ayuda in (("descartar", "marca una cita descartada; no la borra"),
                          ("restablecer", "revierte un descarte")):
        a = nuevo(nombre, ayuda)
        a.add_argument("--cita", required=True)
        autor_motivo(a)
    a = nuevo("revisar", "marca la cita «revisada»")
    autor_motivo(a)
    a = nuevo("firmar", "firma la cita revisada con marco y versión completos (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula la huella del producto, la entrega de S03 y cada evidencia citada")
    a = nuevo("entregar", "citas vigentes para S05")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_cita)


def _cmd_perfil(args) -> int:
    """S05 — El perfil: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = perfil_mod.abrir(raiz, args.fecha or None)
            con_material = sum(1 for s in c["secciones"] if s["riesgos"])
            print(f"✓ perfil abierto · 6 funciones · {con_material} con material · "
                  f"{len(c['sin_asignar'])} sin asignar · estado {perfil_mod.estado_efectivo(raiz)}")
            print(f"  {perfil_mod.ARCHIVO_JSON} · {perfil_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            s = perfil_mod.corregir(raiz, args.funcion, args.campo, args.valor, args.motivo,
                                    args.autor, args.fecha or None)
            print(f"✓ síntesis corregida en {s['funcion']} · sección «revisada»")
        elif args.accion == "asignar":
            perfil_mod.reasignar(raiz, args.cita, args.funcion or None, args.motivo,
                                 args.autor, args.fecha or None)
            print(f"✓ {args.cita} asignado a {args.funcion or 'ninguna función'}")
        elif args.accion == "revisar":
            perfil_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ perfil «revisado»")
        elif args.accion == "firmar":
            r = perfil_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ perfil firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  {r['nota']}")
        elif args.accion == "verificar":
            v = perfil_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = perfil_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"6 secciones para S06 · estado {d['estado']}")
                for s in d["secciones"]:
                    print(f"  {s['funcion']}: {len(s['riesgos'])} riesgo(s)")
    except (perfil_mod.PerfilError, cita_mod.CitaError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_perfil(sub) -> None:
    sp = sub.add_parser("perfil", help="S05 — abrir, corregir, firmar y entregar el perfil")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "propone la lectura del activo por las seis funciones del NIST CSF 2.0")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige la síntesis de una función")
    a.add_argument("--funcion", required=True, choices=list(perfil_mod.FUNCIONES))
    a.add_argument("--campo", required=True, choices=list(perfil_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("asignar", "reasigna un riesgo citado a otra función (o a ninguna)")
    a.add_argument("--cita", required=True)
    a.add_argument("--funcion", default="", choices=list(perfil_mod.FUNCIONES))
    autor_motivo(a)
    a = nuevo("revisar", "marca el perfil «revisado»")
    autor_motivo(a)
    a = nuevo("firmar", "firma el perfil revisado con las seis síntesis completas (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula la huella del producto, la entrega de S04 y cada evidencia citada")
    a = nuevo("entregar", "seis secciones para S06")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_perfil)


def _cmd_lista(args) -> int:
    """S06 — La lista: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = lista_mod.abrir(raiz, args.fecha or None)
            sel = sum(1 for f in c["filas"] if f["estado_aplicabilidad"] != "descartado")
            pend = sum(1 for f in c["filas"] if f["estado_confirmacion"] != lista_mod.CONF_CONFIRMADO)
            print(f"✓ lista abierta · {len(c['filas'])} controles propuestos · {sel} seleccionados · "
                  f"{pend} pendientes · estado {lista_mod.estado_efectivo(raiz)}")
            print(f"  {lista_mod.ARCHIVO_JSON} · {lista_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            f = lista_mod.corregir(raiz, args.fila, args.campo, args.valor, args.motivo,
                                   args.autor, args.fecha or None)
            print(f"✓ justificación corregida en {f['id']} · fila «revisada»")
        elif args.accion == "anadir":
            f = lista_mod.anadir(raiz, args.control, args.identificador, args.justificacion,
                                 args.fuente, args.motivo, args.autor, args.fecha or None)
            print(f"✓ control añadido a mano {f['id']} ({f['estado_confirmacion']})")
        elif args.accion in ("descartar", "recuperar"):
            f = lista_mod.descartar if args.accion == "descartar" else lista_mod.recuperar
            x = f(raiz, args.fila, args.motivo, args.autor, args.fecha or None)
            print(f"✓ {x['id']} {'descartado' if args.accion == 'descartar' else 'recuperado'}")
        elif args.accion == "revisar":
            lista_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ lista «revisada»")
        elif args.accion == "firmar":
            r = lista_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ lista firmada por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  seleccionados: {r['seleccionados_al_firmar']} · pendientes: {r['pendientes_al_firmar']} · "
                  f"{r['nota']}")
        elif args.accion == "verificar":
            v = lista_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = lista_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{d['contados']['seleccionados']} controles seleccionados para S07 · "
                      f"{d['contados']['pendientes']} pendientes · estado {d['estado']}")
    except (lista_mod.ListaError, perfil_mod.PerfilError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_lista(sub) -> None:
    sp = sub.add_parser("lista", help="S06 — abrir, corregir, firmar y entregar la lista")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "propone los CIS Controls aplicables partiendo por el inventario")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige la justificación de aplicabilidad de una fila")
    a.add_argument("--fila", required=True)
    a.add_argument("--campo", required=True, choices=list(lista_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("anadir", "añade un control a mano, con fuente (queda pendiente de confirmar)")
    a.add_argument("--control", required=True)
    a.add_argument("--identificador", required=True)
    a.add_argument("--justificacion", required=True)
    a.add_argument("--fuente", required=True)
    autor_motivo(a)
    for nombre, ayuda in (("descartar", "marca un control descartado (no aplica); no lo borra"),
                          ("recuperar", "recupera un control descartado")):
        a = nuevo(nombre, ayuda)
        a.add_argument("--fila", required=True)
        autor_motivo(a)
    a = nuevo("revisar", "marca la lista «revisada»")
    autor_motivo(a)
    a = nuevo("firmar", "firma la lista revisada con justificaciones completas (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula la huella del producto, la entrega de S05 y cada evidencia ancla")
    a = nuevo("entregar", "controles seleccionados para S07")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_lista)


def _cmd_encargo(args) -> int:
    """S07 — El encargo: trabajo escrito para repetir, sin firmar."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = encargo_mod.abrir(raiz, args.fecha or None)
            print(f"✓ encargo abierto · {c['contados']['pasos']} pasos · "
                  f"{c['contados']['repetibles']} repetibles · {c['contados']['condicionados']} condicionados · "
                  f"{c['contados']['no_repetibles']} no repetibles")
            print(f"  {encargo_mod.ARCHIVO_JSON} · {encargo_mod.ARCHIVO_MD}")
            print(f"  sin firma de aprobación, por diseño (guía S07)")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            p = encargo_mod.corregir(raiz, args.paso, args.campo, args.valor, args.motivo,
                                     args.autor, args.fecha or None)
            print(f"✓ corrección registrada en {p['id']} (autoría, no firma)")
        elif args.accion == "anadir":
            p = encargo_mod.anadir(raiz, args.descripcion, args.entrada, args.salida,
                                   args.motivo, args.autor, args.fecha or None)
            print(f"✓ paso añadido {p['id']}")
        elif args.accion in ("excluir", "incluir"):
            f = encargo_mod.excluir if args.accion == "excluir" else encargo_mod.incluir
            p = f(raiz, args.paso, args.motivo, args.autor, args.fecha or None)
            print(f"✓ {p['id']} ahora «{p['repetibilidad']}»")
        elif args.accion == "revisar":
            encargo_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ encargo «revisado»")
        elif args.accion == "verificar":
            v = encargo_mod.verificar(raiz)
            print(f"{v['estado']} · sha256 actual {v['sha256_actual']}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = encargo_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{len(d['pasos'])} pasos para S08 · integro: {'sí' if d['integro'] else 'no'}")
    except encargo_mod.EncargoError as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_encargo(sub) -> None:
    sp = sub.add_parser("encargo", help="S07 — abrir, corregir y entregar el encargo (sin firmar)")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "consolida el trabajo S01–S06 como pasos repetibles")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige la descripción de un paso (autoría registrada, sin firma)")
    a.add_argument("--paso", required=True)
    a.add_argument("--campo", required=True, choices=list(encargo_mod.CAMPOS_CORREGIBLES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("anadir", "añade un paso a mano")
    a.add_argument("--descripcion", required=True)
    a.add_argument("--entrada", required=True)
    a.add_argument("--salida", required=True)
    autor_motivo(a)
    for nombre, ayuda in (("excluir", "marca un paso «no repetible» (no se borra)"),
                          ("incluir", "revierte la exclusión")):
        a = nuevo(nombre, ayuda)
        a.add_argument("--paso", required=True)
        autor_motivo(a)
    a = nuevo("revisar", "marca el encargo «revisado»")
    autor_motivo(a)
    nuevo("verificar", "recalcula la huella de integridad y la cadena S01–S06")
    a = nuevo("entregar", "encargo completo para S08")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_encargo)


def _cmd_frases(args) -> int:
    """S08 — Las dos frases: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = frases_mod.abrir(raiz, args.fecha or None)
            print(f"✓ frases abiertas · estado {frases_mod.estado_efectivo(raiz)} · "
                  f"{c['conteos']['riesgos']} riesgos · {c['conteos']['vacios']} vacíos")
            print(f"  {frases_mod.ARCHIVO_JSON} · {frases_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            f = frases_mod.corregir(raiz, args.frase, args.valor, args.motivo,
                                    args.autor, args.fecha or None)
            print(f"✓ frase «{args.frase}» corregida (consistencia verificada con la otra frase)")
        elif args.accion == "revisar":
            frases_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ frases «revisadas»")
        elif args.accion == "firmar":
            r = frases_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ frases firmadas por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  {r['nota']}")
        elif args.accion == "verificar":
            v = frases_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            for p in v["inconsistencias"]:
                print(f"  inconsistencia: {p}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = frases_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"2 frases para S09 · estado {d['estado']} · "
                      f"{len(d['inconsistencias'])} inconsistencias")
    except (frases_mod.FrasesError, encargo_mod.EncargoError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_frases(sub) -> None:
    sp = sub.add_parser("frases", help="S08 — abrir, corregir, firmar y entregar las dos frases")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "propone la frase de gerencia y la de quien corrige desde la entrega de S07")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige una frase; se rechaza si rompe la consistencia con la otra")
    a.add_argument("--frase", required=True, choices=list(frases_mod.FRASES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("revisar", "marca las frases «revisadas»")
    autor_motivo(a)
    a = nuevo("firmar", "firma las frases revisadas y consistentes (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula huellas y la consistencia entre las dos frases")
    a = nuevo("entregar", "las dos frases para S09")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_frases)


def _cmd_borrador(args) -> int:
    """S09 — El borrador: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = borrador_mod.abrir(raiz, args.fecha or None)
            print(f"✓ borrador abierto · {len(c['secciones'])} secciones · cliente {c['cliente']} · "
                  f"estado {borrador_mod.estado_efectivo(raiz)}")
            print(f"  {borrador_mod.ARCHIVO_JSON} · {borrador_mod.ARCHIVO_MD}")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            s = borrador_mod.corregir(raiz, args.seccion, args.valor, args.motivo,
                                      args.autor, args.fecha or None)
            print(f"✓ sección «{s['nombre']}» corregida (contradicción con el origen verificada)")
        elif args.accion == "revisar":
            borrador_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ borrador «revisado»")
        elif args.accion == "firmar":
            r = borrador_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ borrador firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  {r['nota']}")
        elif args.accion == "verificar":
            v = borrador_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            for a in v["anexo_rotos"]:
                print(f"  anexo roto: {a}")
            if not v["integro"]:
                return 3
        elif args.accion == "entregar":
            d = borrador_mod.entregar(raiz)
            if args.json:
                print(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{len(d['secciones'])} secciones para S10 · firmado: "
                      f"{'sí' if d['firmado'] else 'no'}")
    except (borrador_mod.BorradorError, frases_mod.FrasesError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_borrador(sub) -> None:
    sp = sub.add_parser("borrador", help="S09 — abrir, corregir, firmar y entregar el borrador")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "ensambla el borrador del informe de cierre desde la entrega de S08")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige una sección; se rechaza si contradice su entrega de origen")
    a.add_argument("--seccion", required=True, choices=list(borrador_mod.SECCIONES))
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("revisar", "marca el borrador «revisado»")
    autor_motivo(a)
    a = nuevo("firmar", "firma el borrador revisado y completo (no abre la compuerta)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula huellas, el origen y cada enlace del anexo")
    a = nuevo("entregar", "borrador completo para S10")
    a.add_argument("--json", action="store_true")
    sp.set_defaults(func=_cmd_borrador)


def _cmd_cierre(args) -> int:
    """S10 — El cierre: la herramienta propone; el auditor corrige y firma."""
    _consola()
    raiz = Path(args.raiz)
    try:
        if args.accion == "abrir":
            c = cierre_mod.abrir(raiz, args.fecha or None)
            print(f"✓ cierre abierto · {c['conteos']['entradas']} entradas de recorrido · "
                  f"{c['conteos']['verifican']} verifican · {c['conteos']['pendientes']} pendientes · "
                  f"estado {cierre_mod.estado_efectivo(raiz)}")
            print(f"  {cierre_mod.ARCHIVO_JSON} · {cierre_mod.ARCHIVO_MD}")
            print("  publicar o entregar el informe es decisión del dueño: el cierre no lo ejecuta")
            for a in c["avisos"]:
                print(f"  aviso: {a}")
        elif args.accion == "corregir":
            e = cierre_mod.corregir(raiz, args.entrada, args.valor, args.motivo,
                                    args.autor, args.fecha or None)
            print(f"✓ entrada {e['id']} corregida (contradicción con el borrador verificada)")
        elif args.accion == "resolver":
            e = cierre_mod.resolver(raiz, args.entrada, args.motivo, args.autor, args.fecha or None)
            print(f"✓ entrada {e['id']} declarada con motivo")
        elif args.accion == "registrar":
            reg = cierre_mod.registrar(raiz, args.tercero, args.observaciones, fecha=args.fecha or None)
            print(f"✓ recorrido registrado por {reg['tercero']} · {reg['fecha']}")
        elif args.accion == "revisar":
            cierre_mod.revisar(raiz, args.autor, args.motivo, args.fecha or None)
            print("✓ cierre «revisado»")
        elif args.accion == "firmar":
            r = cierre_mod.firmar(raiz, args.firmante, args.motivo, args.fecha or None)
            print(f"✓ cierre firmado por {r['firmante']} · sha256 {r['sha256']}")
            print(f"  {r['nota']}")
        elif args.accion == "verificar":
            v = cierre_mod.verificar(raiz)
            print(f"{v['estado_informado']} · sha256 actual {v['sha256_actual']}")
            if not v["integro"]:
                return 3
    except (cierre_mod.CierreError, borrador_mod.BorradorError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return e.codigo
    return 0


def _parser_cierre(sub) -> None:
    sp = sub.add_parser("cierre", help="S10 — abrir, corregir, firmar el informe de cierre")
    acc = sp.add_subparsers(dest="accion", required=True)

    def nuevo(nombre, ayuda):
        a = acc.add_parser(nombre, help=ayuda)
        a.add_argument("--raiz", default="..", help="raíz del repositorio del ejercicio (por defecto ..)")
        return a

    def autor_motivo(a):
        a.add_argument("--motivo", required=True)
        a.add_argument("--autor", required=True)
        a.add_argument("--fecha", default="")

    a = nuevo("abrir", "informe de cierre a partir del borrador firmado de S09")
    a.add_argument("--fecha", default="")
    a = nuevo("corregir", "corrige la afirmación de una entrada de la tabla de recorrido")
    a.add_argument("--entrada", required=True)
    a.add_argument("--valor", required=True)
    autor_motivo(a)
    a = nuevo("resolver", "declara con motivo un enlace que no verifica (lo revisa el auditor)")
    a.add_argument("--entrada", required=True)
    autor_motivo(a)
    a = nuevo("registrar", "registra el recorrido del tercero (la herramienta no lo simula)")
    a.add_argument("--tercero", required=True)
    a.add_argument("--observaciones", required=True)
    a.add_argument("--fecha", default="")
    a = nuevo("revisar", "marca el cierre «revisado»")
    autor_motivo(a)
    a = nuevo("firmar", "firma el cierre revisado y con el recorrido resuelto (no publica nada)")
    a.add_argument("--firmante", required=True)
    a.add_argument("--motivo", required=True, help="justificación de la firma (principio I)")
    a.add_argument("--fecha", default="")
    nuevo("verificar", "recalcula huellas, el origen y el estado de cada enlace")
    sp.set_defaults(func=_cmd_cierre)


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
    _parser_registro(sub)
    _parser_enunciado(sub)
    _parser_cita(sub)
    _parser_perfil(sub)
    _parser_lista(sub)
    _parser_encargo(sub)
    _parser_frases(sub)
    _parser_borrador(sub)
    _parser_cierre(sub)

    args = p.parse_args(argv)
    return args.func(args)
