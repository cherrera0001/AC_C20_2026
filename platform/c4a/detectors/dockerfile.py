"""Detector: configuraciones inseguras en Dockerfile.

Reglas: imagen base con tag flotante (:latest o sin tag), ausencia de USER no
root, y descarga de código sin verificación (ADD con URL o curl | sh).
"""
from __future__ import annotations

import re
from typing import List

from ..model import Finding
from .base import Detector, DetectorContext, build_finding

_FROM = re.compile(r"^\s*FROM\s+(\S+)", re.IGNORECASE | re.MULTILINE)
_USER = re.compile(r"^\s*USER\s+(\S+)", re.IGNORECASE | re.MULTILINE)
_CURL_PIPE = re.compile(r"(curl|wget)[^\n|]*\|\s*(sudo\s+)?(sh|bash)", re.IGNORECASE)
_ADD_URL = re.compile(r"^\s*ADD\s+https?://", re.IGNORECASE | re.MULTILINE)


class DockerfileDetector(Detector):
    id = "dockerfile"
    title = "Configuración de contenedores (Dockerfile)"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []
        for fb in ctx.files:
            base = fb.rel.rsplit("/", 1)[-1]
            if not (base == "Dockerfile" or base.startswith("Dockerfile")):
                continue
            if not fb.text:
                continue

            froms = _FROM.findall(fb.text)
            floating = [f for f in froms if (":" not in f.split("@")[0]) or f.endswith(":latest")]
            users = _USER.findall(fb.text)
            non_root = [u for u in users if u.split(":")[0] not in ("root", "0")]

            if floating:
                ev = ctx.evidence.from_file(
                    fb.path, etype="dockerfile", responsible_role="Rol Técnico de Investigación",
                    result=f"imagen base con tag flotante: {', '.join(floating)}",
                    description=f"FROM sin versión fija en {fb.rel}.",
                    relevance="Tag flotante rompe reproducibilidad y arrastra cambios no revisados.",
                    excerpt_masked="; ".join(f"FROM {f}" for f in floating),
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="floating-base-tag",
                    title=f"Imagen base sin fijar en {fb.rel}",
                    description="La imagen base usa :latest o no especifica tag; el build no es reproducible y puede introducir cambios no auditados.",
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-829", "CWE-16"],
                    cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L",
                    reproduction_command=f'grep -niE "^\\s*FROM" "{fb.rel}"',
                    reproduction_expected="FROM con :latest o sin tag",
                    remediation="Fijar la imagen base por versión y preferentemente por digest (FROM img@sha256:...).",
                    recommendations="Escanear imágenes con Trivy/Grype en CI.",
                    confidence="direct",
                    impact_compliance="A.8.9 gestión de la configuración.",
                ))

            if froms and not non_root:
                ev = ctx.evidence.from_file(
                    fb.path, etype="dockerfile", responsible_role="Rol de Control de Seguridad",
                    result="no se declara USER no-root",
                    description=f"Ausencia de directiva USER no-root en {fb.rel}.",
                    relevance="El contenedor correría como root (CWE-250).",
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="runs-as-root",
                    title=f"Contenedor sin usuario no-root en {fb.rel}",
                    description="No hay directiva USER no-root; por defecto el proceso corre como root dentro del contenedor, ampliando el impacto de una ejecución comprometida.",
                    component=fb.rel, finding_type="control",
                    evidence_ids=[ev.id], cwe=["CWE-250"],
                    cvss_vector="CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H",
                    reproduction_command=f'grep -niE "^\\s*USER" "{fb.rel}" || echo "sin USER"',
                    reproduction_expected='"sin USER" o solo USER root',
                    remediation="Crear un usuario sin privilegios y añadir USER antes del ENTRYPOINT/CMD.",
                    recommendations="Aplicar principio de menor privilegio y readonly rootfs donde sea posible.",
                    confidence="direct",
                    impact_compliance="A.8.2 acceso privilegiado.",
                ))

            if _CURL_PIPE.search(fb.text) or _ADD_URL.search(fb.text):
                ev = ctx.evidence.from_file(
                    fb.path, etype="dockerfile", responsible_role="Rol Técnico de Investigación",
                    result="descarga de código sin verificación de integridad",
                    description=f"Patrón curl|sh o ADD <url> en {fb.rel}.",
                    relevance="Código traído de la red sin verificar hash/firma (CWE-494).",
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="download-without-verify",
                    title=f"Descarga sin verificar integridad en {fb.rel}",
                    description="Se trae y ejecuta código desde la red sin verificar hash ni firma (curl | sh o ADD con URL).",
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-494", "CWE-829"],
                    cvss_vector="CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    reproduction_command=f'grep -niE "curl.*\\| *(sh|bash)|^\\s*ADD\\s+https?://" "{fb.rel}"',
                    reproduction_expected="líneas con curl|sh o ADD <url>",
                    remediation="Descargar con versión fija, verificar checksum/firma antes de ejecutar, o usar paquetes del repositorio de la distro.",
                    recommendations="Preferir artefactos verificados y multi-stage builds.",
                    confidence="direct",
                    impact_compliance="A.8.25 desarrollo seguro.",
                ))
        return findings
