"""Detector: riesgos en CI/CD (GitHub Actions).

Reglas: acciones de terceros sin fijar por SHA (uses: org/action@vX o @main),
y uso de pull_request_target, que corre con secretos sobre código no confiable.
"""
from __future__ import annotations

import re
from typing import List

from ..model import Finding
from .base import Detector, DetectorContext, build_finding

_USES = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.IGNORECASE | re.MULTILINE)
_SHA = re.compile(r"@[0-9a-f]{40}$")
_PR_TARGET = re.compile(r"pull_request_target", re.IGNORECASE)
_MAX = 40


class CicdDetector(Detector):
    id = "cicd"
    title = "Integración y entrega continua (CI/CD)"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []
        for fb in ctx.files:
            if ".github/workflows/" not in fb.rel or not fb.text:
                continue

            unpinned = []
            for m in _USES.findall(fb.text):
                ref = m.strip().strip('"\'')
                if ref.startswith("./") or ref.startswith("docker://"):
                    continue
                if "@" not in ref:
                    unpinned.append(ref)
                elif not _SHA.search(ref):
                    unpinned.append(ref)
            if unpinned:
                ev = ctx.evidence.from_file(
                    fb.path, etype="ci-cd", responsible_role="Rol Técnico de Investigación",
                    result=f"{len(unpinned)} acción(es) sin fijar por SHA",
                    description=f"Acciones de terceros referenciadas por tag/rama en {fb.rel}.",
                    relevance="Una acción no fijada puede cambiar bajo el mismo tag (CWE-829).",
                    excerpt_masked="\n".join(sorted(set(unpinned))[:_MAX]),
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="unpinned-action",
                    title=f"Acciones de CI sin fijar por SHA en {fb.rel}",
                    description="Acciones de terceros referenciadas por tag o rama (p. ej. @v4, @main) en lugar de un SHA de commit. El contenido puede cambiar sin revisión y ejecutarse con los permisos del pipeline.",
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-829", "CWE-494"],
                    cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N",
                    reproduction_command=f'grep -niE "uses:" "{fb.rel}"',
                    reproduction_expected="uses: org/action@<tag o rama> (sin SHA de 40 hex)",
                    remediation="Fijar cada acción por SHA de commit completo y revisar actualizaciones con Dependabot.",
                    recommendations="Restringir permisos del GITHUB_TOKEN (permissions:) al mínimo.",
                    confidence="direct",
                    impact_compliance="A.8.25/A.8.28 cadena de suministro de software.",
                ))

            if _PR_TARGET.search(fb.text):
                ev = ctx.evidence.from_file(
                    fb.path, etype="ci-cd", responsible_role="Rol de Pentesting Ético",
                    result="uso de pull_request_target",
                    description=f"Disparador pull_request_target en {fb.rel}.",
                    relevance="Corre con secretos en contexto de código potencialmente no confiable.",
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="pr-target",
                    title=f"pull_request_target en {fb.rel}",
                    description="El workflow usa pull_request_target, que expone secretos al contexto de un PR externo. Si además hace checkout del código del PR y lo ejecuta, es un vector de robo de secretos.",
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-829"],
                    cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N",
                    reproduction_command=f'grep -n "pull_request_target" "{fb.rel}"',
                    reproduction_expected="línea con pull_request_target",
                    remediation="Evitar checkout+ejecución de código del PR bajo pull_request_target; separar build sin secretos del paso privilegiado.",
                    recommendations="Revisar la guía de seguridad de GitHub sobre pull_request_target.",
                    confidence="indirect",
                    impact_compliance="A.8.25 desarrollo seguro.",
                    notes="Requiere validación: el riesgo real depende de si se hace checkout del head del PR.",
                ))
        return findings
