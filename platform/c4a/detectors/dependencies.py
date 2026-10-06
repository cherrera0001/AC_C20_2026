"""Detector: higiene de dependencias (sin inventar CVEs).

Observa manifiestos y marca rangos sin fijar (^, ~, *, latest, >=). NO afirma
que una dependencia sea vulnerable: eso exige una herramienta de SCA con feed
de CVEs. Deja constancia explícita de que la correlación con CVE es manual.
"""
from __future__ import annotations

import json
import re
from typing import List

from ..model import Finding
from .base import Detector, DetectorContext, build_finding

_NPM_UNPINNED = re.compile(r"^[\^~]|^\*$|^latest$|^>=|\s-\s|\|\||x$", re.IGNORECASE)
_MAX = 40


class DependenciesDetector(Detector):
    id = "dependencies"
    title = "Higiene de dependencias"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []
        for fb in ctx.files:
            name = fb.rel.rsplit("/", 1)[-1]
            if name == "package.json" and fb.text:
                findings += self._npm(ctx, fb)
            elif name == "requirements.txt" and fb.text:
                findings += self._pip(ctx, fb)
        return findings

    def _npm(self, ctx, fb) -> List[Finding]:
        try:
            data = json.loads(fb.text)
        except json.JSONDecodeError:
            return []
        unpinned = []
        for section in ("dependencies", "devDependencies", "optionalDependencies"):
            for pkg, spec in (data.get(section) or {}).items():
                if isinstance(spec, str) and _NPM_UNPINNED.search(spec.strip()):
                    unpinned.append(f"{pkg}: {spec}  [{section}]")
        if not unpinned:
            return []
        sample = unpinned[:_MAX]
        ev = ctx.evidence.from_file(
            fb.path, etype="dependency", responsible_role="Rol Técnico de Investigación",
            result=f"{len(unpinned)} dependencia(s) con versión sin fijar",
            description=f"Rangos de versión abiertos en {fb.rel}.",
            relevance="Versiones no fijadas dificultan reproducibilidad y gestión de vulnerabilidades.",
            excerpt_masked="\n".join(sample),
        )
        return [build_finding(
            detector_id=self.id, rule="npm-unpinned",
            title=f"Dependencias npm sin fijar en {fb.rel}",
            description=(
                f"{len(unpinned)} dependencia(s) usan rangos abiertos (^, ~, *, latest, >=). "
                "No implica vulnerabilidad por sí mismo; sí dificulta reproducir builds y "
                "rastrear qué versión concreta corre. La correlación con CVE requiere una "
                "herramienta de SCA (revisión manual)."
            ),
            component=fb.rel, finding_type="technical",
            evidence_ids=[ev.id], cwe=["CWE-1104", "CWE-1395"],
            cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L",
            reproduction_command=f'jq ".dependencies, .devDependencies" "{fb.rel}"',
            reproduction_expected="objeto con specs que incluyen ^, ~, * o latest",
            remediation="Fijar versiones exactas y confiar en el lockfile; habilitar actualizaciones automáticas controladas (Dependabot/Renovate).",
            recommendations="Ejecutar un SCA (npm audit, osv-scanner, Trivy) para correlacionar con CVEs reales.",
            confidence="direct",
            impact_compliance="A.8.8 gestión de vulnerabilidades técnicas.",
            notes="Correlación CVE: no automática en este ciclo; requiere feed/SCA.",
        )]

    def _pip(self, ctx, fb) -> List[Finding]:
        unpinned = []
        for raw in fb.text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "==" not in line and not line.endswith(".whl"):
                unpinned.append(line)
        if not unpinned:
            return []
        ev = ctx.evidence.from_file(
            fb.path, etype="dependency", responsible_role="Rol Técnico de Investigación",
            result=f"{len(unpinned)} requisito(s) Python sin fijar con ==",
            description=f"Requisitos sin versión exacta en {fb.rel}.",
            relevance="Sin versión fijada no hay build reproducible.",
            excerpt_masked="\n".join(unpinned[:_MAX]),
        )
        return [build_finding(
            detector_id=self.id, rule="pip-unpinned",
            title=f"Requisitos Python sin fijar en {fb.rel}",
            description=(
                f"{len(unpinned)} requisito(s) no usan '==' para fijar versión. "
                "La correlación con CVE requiere SCA (revisión manual)."
            ),
            component=fb.rel, finding_type="technical",
            evidence_ids=[ev.id], cwe=["CWE-1104"],
            cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L",
            reproduction_command=f'grep -vE "==|^#|^-|^$" "{fb.rel}"',
            reproduction_expected="líneas sin '=='",
            remediation="Fijar versiones con '==' y usar un archivo de constraints o un lockfile (pip-tools, uv).",
            recommendations="Ejecutar pip-audit / osv-scanner para CVEs reales.",
            confidence="direct",
            impact_compliance="A.8.8 gestión de vulnerabilidades técnicas.",
        )]
