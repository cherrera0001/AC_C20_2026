"""Integración SCA (Software Composition Analysis) para correlación con CVE.

El enganche está IMPLEMENTADO, no solo documentado. Motores soportados:
  - osv-scanner  (binario local, salida JSON)
  - trivy        (binario local, `trivy fs`, salida JSON)
  - osv-api      (API pública de OSV.dev por HTTP; requiere red, opt-in)

Reglas de honestidad:
  - Si ningún motor está disponible/habilitado, NO se inventa nada: se deja
    constancia y la CVE sigue marcada como revisión manual.
  - Los hallazgos de CVE dependen de una base externa que cambia en el tiempo,
    así que se excluyen del `result_hash` de reproducibilidad del ciclo estático
    y llevan la fecha de consulta.

Sin dependencias: solo subprocess y urllib de la librería estándar.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import cvss as cvss_mod
from .config import Config
from .scope import ScopeManager
from .util import now_iso


@dataclass
class CveRef:
    cve_id: str
    package: str
    version: str
    ecosystem: str
    summary: str = ""
    cvss_vector: str = ""
    source: str = ""
    references: List[str] = field(default_factory=list)
    component: str = ""


# --- extracción de paquetes con versión EXACTA desde lockfiles --------------

def _npm_from_lock(text: str) -> List[Tuple[str, str]]:
    """package-lock.json v2/v3: mapa 'packages' con rutas node_modules/<name>."""
    out: List[Tuple[str, str]] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return out
    pkgs = data.get("packages") or {}
    for path, meta in pkgs.items():
        if not path or "node_modules/" not in path:
            continue
        name = path.split("node_modules/")[-1]
        ver = (meta or {}).get("version")
        if name and ver:
            out.append((name, ver))
    # lockfile v1: dependencies anidadas
    def walk(deps):
        for name, meta in (deps or {}).items():
            ver = meta.get("version")
            if ver:
                out.append((name, ver))
            walk(meta.get("dependencies"))
    walk(data.get("dependencies"))
    return out


def _pip_from_requirements(text: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        if "==" in line:
            name, _, ver = line.partition("==")
            name = name.split("[")[0].strip()
            ver = ver.split(";")[0].strip()
            if name and ver:
                out.append((name, ver))
    return out


def collect_packages(scope: ScopeManager, max_packages: int) -> List[Tuple[str, str, str, str]]:
    """Devuelve (name, version, ecosystem, component) desde lockfiles del objetivo."""
    found: List[Tuple[str, str, str, str]] = []
    for path in scope.iter_files():
        rel = scope.rel(path)
        base = rel.rsplit("/", 1)[-1]
        if base == "package-lock.json":
            for n, v in _npm_from_lock(scope.read_text(path)):
                found.append((n, v, "npm", rel))
        elif base == "requirements.txt":
            for n, v in _pip_from_requirements(scope.read_text(path)):
                found.append((n, v, "PyPI", rel))
        if len(found) >= max_packages:
            break
    # dedup preservando componente
    seen = set()
    uniq = []
    for item in found:
        key = (item[0], item[1], item[2])
        if key not in seen:
            seen.add(key)
            uniq.append(item)
    return uniq[:max_packages]


# --- parsers de salida de herramientas --------------------------------------

def _pick_vector(severity_list) -> str:
    for s in severity_list or []:
        if isinstance(s, dict) and str(s.get("type", "")).upper().startswith("CVSS_V3"):
            return s.get("score", "")
    return ""


def parse_osv_scanner(stdout: str) -> List[CveRef]:
    refs: List[CveRef] = []
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return refs
    for result in data.get("results", []):
        source = (result.get("source") or {}).get("path", "")
        for pkg in result.get("packages", []):
            p = pkg.get("package", {})
            for v in pkg.get("vulnerabilities", []):
                refs.append(CveRef(
                    cve_id=_prefer_cve(v),
                    package=p.get("name", ""),
                    version=p.get("version", ""),
                    ecosystem=p.get("ecosystem", ""),
                    summary=v.get("summary", "") or v.get("details", "")[:200],
                    cvss_vector=_pick_vector(v.get("severity")),
                    source="osv-scanner",
                    references=[r.get("url", "") for r in v.get("references", [])][:5],
                    component=source,
                ))
    return refs


def parse_trivy(stdout: str) -> List[CveRef]:
    refs: List[CveRef] = []
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return refs
    for result in data.get("Results", []):
        target = result.get("Target", "")
        for v in result.get("Vulnerabilities", []) or []:
            vector = ""
            for src in (v.get("CVSS") or {}).values():
                if isinstance(src, dict) and src.get("V3Vector"):
                    vector = "CVSS:3.1/" + src["V3Vector"].split("/", 1)[-1] if not src["V3Vector"].startswith("CVSS") else src["V3Vector"]
                    break
            refs.append(CveRef(
                cve_id=v.get("VulnerabilityID", ""),
                package=v.get("PkgName", ""),
                version=v.get("InstalledVersion", ""),
                ecosystem=result.get("Type", ""),
                summary=v.get("Title", "") or v.get("Description", "")[:200],
                cvss_vector=vector,
                source="trivy",
                references=(v.get("References") or [])[:5],
                component=target,
            ))
    return refs


def parse_osv_api(package: str, version: str, ecosystem: str, component: str, payload: str) -> List[CveRef]:
    refs: List[CveRef] = []
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return refs
    for v in data.get("vulns", []) or []:
        refs.append(CveRef(
            cve_id=_prefer_cve(v),
            package=package, version=version, ecosystem=ecosystem,
            summary=v.get("summary", "") or (v.get("details", "") or "")[:200],
            cvss_vector=_pick_vector(v.get("severity")),
            source="osv-api",
            references=[r.get("url", "") for r in (v.get("references") or [])][:5],
            component=component,
        ))
    return refs


def _prefer_cve(vuln: Dict) -> str:
    vid = vuln.get("id", "")
    for alias in vuln.get("aliases", []) or []:
        if str(alias).startswith("CVE-"):
            return alias
    return vid


# --- gestor ------------------------------------------------------------------

class SCAManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conf = cfg.raw.get("sca", {}) or {}

    @property
    def enabled(self) -> bool:
        return bool(self.conf.get("enabled", False))

    def resolve_engine(self) -> Optional[str]:
        engine = self.conf.get("engine", "auto")
        if engine in ("osv-scanner", "trivy"):
            return engine if shutil.which(engine) else None
        if engine == "osv-api":
            return "osv-api" if self.conf.get("allow_network", False) else None
        # auto
        if shutil.which("osv-scanner"):
            return "osv-scanner"
        if shutil.which("trivy"):
            return "trivy"
        if self.conf.get("allow_network", False):
            return "osv-api"
        return None

    def run(self, scope: ScopeManager) -> Tuple[List[CveRef], Dict]:
        meta = {"enabled": self.enabled, "engine": None, "status": "skipped",
                "queried_at": now_iso(), "packages": 0, "note": ""}
        if not self.enabled:
            meta["note"] = "SCA desactivado en config; CVE queda como revisión manual."
            return [], meta

        engine = self.resolve_engine()
        meta["engine"] = engine
        if not engine:
            meta["status"] = "unavailable"
            meta["note"] = ("Ningún motor SCA disponible (osv-scanner/trivy no instalados "
                            "y red no habilitada). CVE sigue manual.")
            return [], meta

        timeout = int(self.conf.get("timeout", 180))
        try:
            if engine == "osv-scanner":
                refs = self._run_binary(["osv-scanner", "--format", "json", str(self.cfg.target)], parse_osv_scanner, timeout)
            elif engine == "trivy":
                refs = self._run_binary(["trivy", "fs", "--quiet", "--format", "json",
                                         "--scanners", "vuln", str(self.cfg.target)], parse_trivy, timeout)
            else:
                refs = self._run_osv_api(scope, timeout)
            meta["status"] = "completed"
            meta["packages"] = len({(r.package, r.version) for r in refs})
            return refs, meta
        except Exception as exc:  # no tumbar la auditoría por el SCA
            meta["status"] = "error"
            meta["note"] = f"SCA falló: {exc!r}"
            return [], meta

    def _run_binary(self, argv, parser, timeout) -> List[CveRef]:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        # osv-scanner devuelve exit!=0 cuando encuentra vulnerabilidades: eso no es error
        return parser(proc.stdout or "")

    def _run_osv_api(self, scope: ScopeManager, timeout) -> List[CveRef]:
        max_pkgs = int(self.conf.get("max_packages", 200))
        pkgs = collect_packages(scope, max_pkgs)
        refs: List[CveRef] = []
        for name, version, ecosystem, component in pkgs:
            body = json.dumps({"version": version, "package": {"name": name, "ecosystem": ecosystem}}).encode()
            req = urllib.request.Request(
                "https://api.osv.dev/v1/query", data=body,
                headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    payload = resp.read().decode("utf-8", "replace")
            except urllib.error.URLError:
                continue
            refs.extend(parse_osv_api(name, version, ecosystem, component, payload))
        return refs


def _worst_vector(refs: List[CveRef]) -> str:
    best, best_score = "", -1.0
    for r in refs:
        if not r.cvss_vector:
            continue
        try:
            s = cvss_mod.base_score(r.cvss_vector)
        except ValueError:
            continue
        if s > best_score:
            best, best_score = r.cvss_vector, s
    return best


def to_findings(refs: List[CveRef], store, meta: Dict) -> List:
    """Convierte las vulnerabilidades del SCA en hallazgos, uno por paquete.

    Cada hallazgo lleva CVE REALES del motor, su peor CVSS, evidencia con la
    invocación de la herramienta y la fecha de consulta. Importa aquí dentro
    para evitar ciclos de importación con los detectores.
    """
    from .detectors.base import build_finding

    grouped: Dict[tuple, List[CveRef]] = {}
    for r in refs:
        grouped.setdefault((r.component, r.package, r.version, r.ecosystem, r.source), []).append(r)

    findings = []
    for (component, package, version, ecosystem, source), group in grouped.items():
        cve_ids = sorted({r.cve_id for r in group if r.cve_id})
        vector = _worst_vector(group)
        ev = store.from_command(
            command=f"{source} :: {ecosystem} {package}@{version}",
            output=json.dumps([r.__dict__ for r in group], ensure_ascii=False, indent=2),
            etype="dependency", responsible_role="Rol Técnico de Investigación",
            result=f"{len(cve_ids)} vulnerabilidad(es) para {package}@{version}",
            description=f"{source} reportó vulnerabilidades en {package}@{version}.",
            relevance="Dependencia con vulnerabilidad conocida (CWE-1395).",
            confidence="direct",
        )
        summary = group[0].summary or ""
        refs_txt = "; ".join(sorted({u for r in group for u in r.references if u}))[:400]
        f = build_finding(
            detector_id=f"sca:{source}", rule=f"{ecosystem}:{package}@{version}",
            title=f"Dependencia vulnerable: {package}@{version} ({len(cve_ids)} CVE)",
            description=(f"{source} identificó {len(cve_ids)} vulnerabilidad(es) en "
                        f"{package}@{version} ({ecosystem}). {summary}"),
            component=component or f"{ecosystem}:{package}",
            finding_type="technical",
            evidence_ids=[ev.id], cwe=["CWE-1395"],
            cvss_vector=vector or None,
            reproduction_command=f"{source} (volver a escanear {ecosystem} {package}@{version})",
            reproduction_expected=f"{len(cve_ids)} CVE para {package}@{version}",
            remediation="Actualizar a una versión corregida o aplicar el parche del aviso.",
            recommendations="Fijar la versión corregida en el manifiesto y el lockfile.",
            confidence="direct",
            impact_compliance="A.8.8 gestión de vulnerabilidades técnicas; deber de diligencia (Ley 21.663).",
            notes=f"Fuente: {source} · consultado {meta.get('queried_at')} · refs: {refs_txt}",
        )
        f.cve = cve_ids
        f.cve_note = f"Correlación por {source} ({len(cve_ids)} CVE); confirmar explotabilidad en contexto."
        findings.append(f)
    return findings


def enrich_dependency_findings(static_findings: List, refs: List[CveRef]) -> None:
    """Añade CVE a los hallazgos de dependencias estáticas cuyo paquete coincide."""
    by_pkg: Dict[str, List[str]] = {}
    for r in refs:
        if r.cve_id:
            by_pkg.setdefault(r.package.lower(), []).append(r.cve_id)
    for f in static_findings:
        if f.source != "dependencies":
            continue
        hit = sorted({cve for pkg, cves in by_pkg.items() if pkg in f.description.lower() for cve in cves})
        if hit:
            f.cve = sorted(set(f.cve) | set(hit))
            f.cve_note = "Correlación SCA por nombre de paquete; verificar versión afectada."
