"""Gestor de inventario (Fase 2): qué hay en el objetivo.

Recorre el objetivo una sola vez y clasifica: lenguajes, gestores de paquetes,
contenedorización, IaC, CI/CD, integraciones y archivos de configuración
notables. No concluye nada; describe el terreno para las fases siguientes.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from .scope import ScopeManager
from .util import now_iso

_LANG_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".py": "Python", ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".sql": "SQL", ".sh": "Shell", ".ps1": "PowerShell",
}

_MANIFESTS = {
    "package.json": "npm/pnpm/yarn (Node.js)",
    "pnpm-lock.yaml": "pnpm (lockfile)",
    "package-lock.json": "npm (lockfile)",
    "yarn.lock": "yarn (lockfile)",
    "requirements.txt": "pip (Python)",
    "pyproject.toml": "PEP 517 (Python)",
    "poetry.lock": "poetry (lockfile)",
    "go.mod": "Go modules",
    "Cargo.toml": "Cargo (Rust)",
    "Gemfile": "Bundler (Ruby)",
    "composer.json": "Composer (PHP)",
    "pom.xml": "Maven (Java)",
}

_CONTAINER = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"}
_IAC = {".tf", ".tfvars"}
_K8S_HINT = ("apiVersion:", "kind:")


class InventoryManager:
    def __init__(self, scope: ScopeManager):
        self.scope = scope

    def build(self) -> Dict[str, Any]:
        ext_counter: Counter = Counter()
        languages: Counter = Counter()
        manifests: List[str] = []
        containers: List[str] = []
        iac: List[str] = []
        ci_cd: List[str] = []
        env_files: List[str] = []
        k8s: List[str] = []
        total_files = 0

        for path in self.scope.iter_files():
            total_files += 1
            rel = self.scope.rel(path)
            ext = path.suffix.lower()
            ext_counter[ext or "(sin extensión)"] += 1
            if ext in _LANG_BY_EXT:
                languages[_LANG_BY_EXT[ext]] += 1
            name = path.name
            if name in _MANIFESTS:
                manifests.append(f"{rel} → {_MANIFESTS[name]}")
            if name in _CONTAINER or name.startswith("Dockerfile"):
                containers.append(rel)
            if ext in _IAC:
                iac.append(rel)
            if ".github/workflows/" in rel or ".gitlab-ci" in rel or name in (
                "azure-pipelines.yml", "Jenkinsfile", ".circleci",
            ):
                ci_cd.append(rel)
            if name == ".env" or name.startswith(".env."):
                env_files.append(rel)
            if ext in (".yml", ".yaml"):
                head = self.scope.read_text(path)[:200]
                if all(h in head for h in _K8S_HINT):
                    k8s.append(rel)

        return {
            "generated_at": now_iso(),
            "target": str(self.scope.target),
            "totals": {
                "files_scanned": total_files,
                "skipped_large": len(self.scope.skipped_large),
                "skipped_binary": len(self.scope.skipped_binary),
            },
            "languages": dict(languages.most_common()),
            "extensions": dict(ext_counter.most_common(25)),
            "package_managers": sorted(set(manifests)),
            "containerization": sorted(set(containers)),
            "infrastructure_as_code": sorted(set(iac)),
            "kubernetes_manifests": sorted(set(k8s)),
            "ci_cd": sorted(set(ci_cd)),
            "env_files": sorted(set(env_files)),
        }
