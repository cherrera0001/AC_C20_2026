"""Modelo de datos del dominio de auditoría.

Cuatro registros estructurados, cada uno serializable a JSON:
  - Evidence       (Fase 5): una pieza de evidencia con fuente, fecha y hash.
  - Finding        (sec. 11): el registro completo de un hallazgo.
  - ControlResult  (Fase 4): una fila de la matriz de controles.
  - Run            (sec. 13): un registro de ejecución reproducible.

Regla de diseño: la DETECCIÓN (lo que una herramienta observó) se separa de la
CONCLUSIÓN (si hay riesgo). Por eso `status`, `confidence` y `reproduction`
viven en el hallazgo y los llena un rol distinto del que detecta.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _asdict(obj) -> Dict[str, Any]:
    return dataclasses.asdict(obj)


# --- Estados y vocabulario controlado ------------------------------------

FINDING_TYPES = ("compliance", "control", "technical", "risk", "evidence")

# Estado del ciclo de vida de validación (Fase 7).
STATUS = (
    "detected",            # una herramienta/rol lo observó
    "requires-validation", # pendiente de validación técnica
    "validated",           # confirmado técnicamente por un rol
    "reproduced",          # reproducido de forma estable
    "not-reproduced",      # no se pudo reproducir
    "resolved",            # remediado y verificado
    "accepted-risk",       # riesgo aceptado por el propietario
)

SEVERITIES = ("CRITICO", "ALTO", "MEDIO", "BAJO", "INFORMACIONAL",
              "NO-REPRODUCIDO", "REQUIERE-VALIDACION")

CONFIDENCE = ("direct", "indirect", "inferred")


@dataclass
class Evidence:
    id: str
    type: str                     # config | dependency | ci-cd | dockerfile | permission | code | log
    source: str                   # qué la produjo (detector id o comando)
    location: str                 # ruta[:linea] relativa al objetivo
    collected_at: str
    sha256: str                   # hash del archivo fuente
    responsible_role: str
    scope: str
    status: str                   # collected | verified
    result: str                   # qué mostró
    description: str
    relevance: str
    confidence: str = "direct"
    excerpt_masked: str = ""       # extracto con secretos enmascarados

    def to_dict(self) -> Dict[str, Any]:
        return _asdict(self)


@dataclass
class Finding:
    id: str
    title: str
    description: str
    component: str
    asset: str
    scope: str
    finding_type: str
    severity: str
    probability: str
    impact: str
    status: str
    evidence: List[str] = field(default_factory=list)       # ids de Evidence
    commands: List[str] = field(default_factory=list)        # reproducción
    reproduction: Dict[str, Any] = field(default_factory=dict)
    source: str = ""                                          # detector id
    cve: List[str] = field(default_factory=list)
    cve_note: str = "Sin correlación automática: revisión manual requerida."
    cwe: List[str] = field(default_factory=list)
    cvss: Dict[str, Any] = field(default_factory=dict)
    norma: List[str] = field(default_factory=list)
    control: List[str] = field(default_factory=list)
    owner: str = ""
    detected_at: str = ""
    validated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    remediation: str = ""
    confidence: str = "direct"
    responsible_roles: List[str] = field(default_factory=list)
    requirements: str = ""
    impact_economic: str = ""
    impact_operational: str = ""
    impact_compliance: str = ""
    recommendations: str = ""
    notes: str = ""
    history: List[Dict[str, str]] = field(default_factory=list)

    def log(self, event: str, when: str) -> None:
        self.history.append({"when": when, "event": event})

    def to_dict(self) -> Dict[str, Any]:
        return _asdict(self)


@dataclass
class ControlResult:
    control: str
    objective: str
    owner: str
    implementation: str
    evidence: str
    frequency: str
    responsible: str
    status: str
    result: str
    risk: str
    compliance: str          # cumple | no-cumple | parcial | no-evaluado
    reference: str
    requirement: str
    technical_evidence: str
    last_validation: str

    def to_dict(self) -> Dict[str, Any]:
        return _asdict(self)


@dataclass
class Run:
    run_id: str
    started_at: str
    finished_at: str
    person: str
    target: str
    command: str
    params: Dict[str, Any]
    result_summary: Dict[str, Any]
    errors: List[str]
    duration_s: float
    hash: str
    status: str
    tool_versions: Dict[str, str]
    environment: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return _asdict(self)
