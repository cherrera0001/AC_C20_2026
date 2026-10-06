"""Carga y validación de la configuración de un encargo de auditoría.

La config decide: qué objetivo se audita, qué entra y qué se excluye, qué
normativas aplican (no se asume que todas apliquen) y qué detectores corren.
Formato JSON (sin dependencias de YAML) para que sea reproducible en cualquier
máquina con Python estándar.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

_KNOWLEDGE = Path(__file__).resolve().parent / "knowledge"


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Config:
    raw: Dict[str, Any]
    config_path: Path
    target: Path
    output_root: Path
    include_ext: List[str]
    exclude_dirs: List[str]
    exclude_globs: List[str]
    max_file_bytes: int
    max_files: int
    normativas: List[str]
    detectors: List[str]
    audit_name: str
    auditor: str
    person: str
    read_only: bool = True

    # catálogos de conocimiento (cargados una vez)
    cwe: Dict[str, Any] = field(default_factory=dict)
    cwe_map: Dict[str, Any] = field(default_factory=dict)
    controls: Dict[str, Any] = field(default_factory=dict)
    norm_catalog: Dict[str, Any] = field(default_factory=dict)

    @property
    def phase(self) -> Dict[str, Path]:
        r = self.output_root
        return {
            "plan": r / "01_plan",
            "evidencia": r / "02_evidencia",
            "hallazgos": r / "03_hallazgos",
            "informe": r / "04_informe",
            "evidence_raw": r / "evidence",
            "state": r / ".c4a",
        }


def load(config_path: str | Path) -> Config:
    config_path = Path(config_path).resolve()
    raw = _load_json(config_path)

    base = config_path.parent
    target = Path(raw["target"]).expanduser()
    if not target.is_absolute():
        target = (base / target).resolve()
    target = target.resolve()

    out = Path(raw.get("output_root", ".")).expanduser()
    if not out.is_absolute():
        out = (base / out).resolve()
    out = out.resolve()

    scope = raw.get("scope", {})
    cfg = Config(
        raw=raw,
        config_path=config_path,
        target=target,
        output_root=out,
        include_ext=[e.lower() for e in scope.get("include_ext", [])],
        exclude_dirs=scope.get("exclude_dirs", [
            ".git", "node_modules", "dist", "build", ".turbo", ".next",
            "vendor", "__pycache__", ".venv", "venv", ".mypy_cache", "coverage",
        ]),
        exclude_globs=scope.get("exclude_globs", []),
        max_file_bytes=int(scope.get("max_file_bytes", 2_000_000)),
        max_files=int(scope.get("max_files", 20_000)),
        normativas=raw.get("normativas", ["ISO-27001"]),
        detectors=raw.get("detectors", ["all"]),
        audit_name=raw.get("audit_name", "Auditoría C4A"),
        auditor=raw.get("auditor", ""),
        person=raw.get("person", raw.get("auditor", "")),
        read_only=bool(scope.get("read_only", True)),
    )

    cfg.cwe = _load_json(_KNOWLEDGE / "cwe.json")
    cfg.cwe_map = _load_json(_KNOWLEDGE / "cwe_map.json")
    cfg.controls = _load_json(_KNOWLEDGE / "controls_iso27001.json")
    cfg.norm_catalog = _load_json(_KNOWLEDGE / "normativas.json")

    _validate(cfg)
    return cfg


def _validate(cfg: Config) -> None:
    if not cfg.target.exists():
        raise ValueError(f"el objetivo no existe: {cfg.target}")
    if not cfg.target.is_dir():
        raise ValueError(f"el objetivo no es un directorio: {cfg.target}")
    unknown = [n for n in cfg.normativas if n not in cfg.norm_catalog]
    if unknown:
        raise ValueError(f"normativas desconocidas en config: {unknown}")
