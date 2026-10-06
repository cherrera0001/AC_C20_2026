"""Registro de detectores del primer ciclo.

Para añadir un detector: créalo como subclase de Detector y súmalo a _ALL.
El orquestador selecciona los habilitados según la config ("all" o una lista
de ids).
"""
from __future__ import annotations

from typing import Dict, List, Type

from .base import Detector
from .cicd import CicdDetector
from .crypto_config import CryptoConfigDetector
from .dependencies import DependenciesDetector
from .dockerfile import DockerfileDetector
from .permissions import PermissionsDetector
from .secrets_files import SecretsDetector

_ALL: List[Type[Detector]] = [
    SecretsDetector,
    DependenciesDetector,
    DockerfileDetector,
    CicdDetector,
    CryptoConfigDetector,
    PermissionsDetector,
]

REGISTRY: Dict[str, Type[Detector]] = {d.id: d for d in _ALL}


def select(enabled: List[str]) -> List[Detector]:
    if not enabled or "all" in enabled:
        return [cls() for cls in _ALL]
    out: List[Detector] = []
    for name in enabled:
        if name in REGISTRY:
            out.append(REGISTRY[name]())
    return out


def catalog() -> List[Dict[str, str]]:
    return [{"id": d.id, "title": d.title, "finding_type": d.finding_type} for d in _ALL]
