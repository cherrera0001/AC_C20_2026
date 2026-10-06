"""Interfaz de detector y utilidades para construir hallazgos.

Un detector OBSERVA y aporta evidencia; no concluye el riesgo. Por eso aquí el
hallazgo nace con severidad `REQUIERE-VALIDACION` y estado `detected`: el
gestor de riesgo deriva la severidad final y el gestor de correlación le añade
controles y normativas. Separar detección de conclusión es una regla del
encargo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config import Config
from ..evidence import EvidenceStore
from ..model import Finding
from ..scope import ScopeManager
from ..util import now_iso, short_id
from .. import cvss as cvss_mod


@dataclass
class FileBlob:
    """Un archivo del objetivo ya leído: ruta absoluta, ruta relativa y texto.

    `text` es "" para binarios o ilegibles. Se construye una sola vez y se
    comparte entre detectores para no recorrer el árbol repetidamente.
    """
    path: "Any"
    rel: str
    text: str


@dataclass
class DetectorContext:
    cfg: Config
    scope: ScopeManager
    evidence: EvidenceStore
    files: List[FileBlob]


class Detector:
    id: str = "base"
    title: str = "Detector base"
    finding_type: str = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:  # pragma: no cover
        raise NotImplementedError


def build_finding(
    *,
    detector_id: str,
    rule: str,
    title: str,
    description: str,
    component: str,
    finding_type: str,
    evidence_ids: List[str],
    cwe: Optional[List[str]] = None,
    cvss_vector: Optional[str] = None,
    reproduction_command: str = "",
    reproduction_expected: str = "",
    remediation: str = "",
    recommendations: str = "",
    requirements: str = "",
    probability: str = "por-determinar",
    impact: str = "por-determinar",
    confidence: str = "direct",
    responsible_roles: Optional[List[str]] = None,
    notes: str = "",
    impact_compliance: str = "",
) -> Finding:
    fid = short_id("F", detector_id, component, rule)
    cvss_block: Dict[str, Any] = {}
    if cvss_vector:
        cvss_block = cvss_mod.evaluate(cvss_vector)
    reproduction = {
        "method": "re-ejecutar la auditoría y comparar por id y hash de evidencia",
        "command": reproduction_command,
        "expected": reproduction_expected,
        "environment": "Python 3.10+ (solo librería estándar); acceso de lectura al objetivo",
    }
    f = Finding(
        id=fid,
        title=title,
        description=description,
        component=component,
        asset=component,
        scope="in-scope",
        finding_type=finding_type,
        severity="REQUIERE-VALIDACION",
        probability=probability,
        impact=impact,
        status="detected",
        evidence=list(evidence_ids),
        commands=[reproduction_command] if reproduction_command else [],
        reproduction=reproduction,
        source=detector_id,
        cwe=cwe or [],
        cvss=cvss_block,
        detected_at=now_iso(),
        remediation=remediation,
        recommendations=recommendations,
        requirements=requirements,
        confidence=confidence,
        responsible_roles=responsible_roles or ["Rol Técnico de Investigación"],
        notes=notes,
        impact_compliance=impact_compliance,
    )
    f.log("detected", f.detected_at)
    return f
