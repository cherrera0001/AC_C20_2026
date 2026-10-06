"""Detector: secretos y archivos sensibles en el árbol del repositorio.

Dos reglas:
  - env-file-present: un archivo .env / .env.* dentro del repo (CWE-312/200).
  - hardcoded-credential: líneas que parecen credencial embebida (CWE-798).

Los extractos se guardan SIEMPRE enmascarados. Nunca se vuelca el secreto.
"""
from __future__ import annotations

import re
from typing import List

from ..model import Finding
from ..util import redact_line
from .base import Detector, DetectorContext, build_finding

_CRED = re.compile(
    r"""(?ix)\b(password|passwd|pwd|secret|token|api[_-]?key|apikey|
    access[_-]?key|private[_-]?key|client[_-]?secret|bearer)\b
    \s*[:=]\s*['"]?[A-Za-z0-9/\+\=_\-\.]{6,}""",
    re.VERBOSE,
)
_PLACEHOLDER = re.compile(r"(?i)(example|changeme|your[_-]?|xxx+|<[^>]+>|\$\{|placeholder|dummy|test)")
_MAX_LINES = 20


class SecretsDetector(Detector):
    id = "secrets-files"
    title = "Secretos y archivos sensibles"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []

        for fb in ctx.files:
            name = fb.rel.rsplit("/", 1)[-1]
            if name == ".env" or name.startswith(".env."):
                ev = ctx.evidence.from_file(
                    fb.path, etype="config", responsible_role="Rol de Evidencia",
                    result="archivo de variables de entorno presente en el árbol del repo",
                    description=f"Archivo {fb.rel} detectado dentro del alcance.",
                    relevance="Los .env suelen contener secretos; su presencia versionada es riesgo de exposición.",
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="env-file-present",
                    title=f"Archivo de entorno presente: {fb.rel}",
                    description=(
                        "Se encontró un archivo .env dentro del repositorio. Si está "
                        "versionado o se despliega con el código, puede exponer secretos."
                    ),
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-312", "CWE-200"],
                    cvss_vector="CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
                    reproduction_command=f'test -f "{fb.rel}" && echo PRESENTE',
                    reproduction_expected="PRESENTE",
                    remediation="Sacar el .env del control de versiones, rotar cualquier secreto expuesto y usar un gestor de secretos.",
                    recommendations="Añadir .env al .gitignore y verificar el historial de git por secretos ya commiteados.",
                    impact_compliance="Afecta A.8.24 (criptografía/secretos) y protección de datos.",
                    confidence="direct",
                    notes="Verificar si está en git con: git ls-files | grep -E '(^|/)\\.env'",
                ))
                continue

            if not fb.text:
                continue
            hits = []
            for i, line in enumerate(fb.text.splitlines(), start=1):
                if _CRED.search(line) and not _PLACEHOLDER.search(line):
                    hits.append((i, redact_line(line)[:160]))
                if len(hits) >= _MAX_LINES:
                    break
            if hits:
                excerpt = "\n".join(f"L{n}: {txt}" for n, txt in hits)
                ev = ctx.evidence.from_file(
                    fb.path, etype="code", responsible_role="Rol de Evidencia",
                    result=f"{len(hits)} línea(s) con patrón de credencial",
                    description=f"Patrón de credencial embebida en {fb.rel}.",
                    relevance="Credenciales en código fuente (CWE-798).",
                    excerpt_masked=excerpt, line=hits[0][0],
                )
                findings.append(build_finding(
                    detector_id=self.id, rule="hardcoded-credential",
                    title=f"Posible credencial embebida en {fb.rel}",
                    description=(
                        "Una o más líneas contienen un patrón de credencial asignada en "
                        "claro. Requiere validación manual: puede ser un secreto real o un "
                        "nombre de variable. Los valores se muestran enmascarados."
                    ),
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=["CWE-798"],
                    cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                    reproduction_command=f'grep -niE "(password|secret|token|api[_-]?key)" "{fb.rel}"',
                    reproduction_expected="líneas coincidentes (valores enmascarados en la evidencia)",
                    remediation="Mover el valor a un gestor de secretos o variable de entorno inyectada en despliegue; rotar si es real.",
                    recommendations="Añadir un escaneo de secretos (p. ej. gitleaks) al pipeline de CI.",
                    confidence="indirect",
                    impact_compliance="A.8.28 codificación segura; A.8.24 secretos.",
                    notes="Falso positivo posible si es un nombre de campo sin valor real.",
                ))
        return findings
