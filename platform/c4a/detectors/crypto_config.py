"""Detector: criptografía y transporte débiles en configuración/código.

Reglas: algoritmos rotos (MD5/SHA1 para seguridad, DES/RC4), verificación TLS
desactivada (rejectUnauthorized:false, verify=False, InsecureSkipVerify) y
endpoints sensibles sobre http://.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from ..model import Finding
from .base import Detector, DetectorContext, build_finding

_RULES: List[Tuple[str, "re.Pattern", str, List[str], str]] = [
    ("weak-hash", re.compile(r"(?i)\b(md5|sha1)\s*\(", ), "algoritmo hash débil para seguridad",
     ["CWE-327"], "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N"),
    ("weak-cipher", re.compile(r"(?i)\b(DES|RC4|3DES|ECB)\b"), "cifrador débil u obsoleto",
     ["CWE-327"], "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N"),
    ("tls-verify-off", re.compile(r"(?i)(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*0)"),
     "verificación TLS desactivada", ["CWE-319", "CWE-327"],
     "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N"),
    ("cleartext-endpoint", re.compile(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[A-Za-z0-9.\-]+"),
     "endpoint sobre http:// (texto claro)", ["CWE-319"],
     "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N"),
]
_SKIP_EXT = {".md", ".txt", ".lock", ".csv", ".svg", ".map"}
_MAX_LINES = 15


class CryptoConfigDetector(Detector):
    id = "crypto-config"
    title = "Criptografía y transporte"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []
        for fb in ctx.files:
            if not fb.text:
                continue
            if any(fb.rel.lower().endswith(e) for e in _SKIP_EXT):
                continue
            lines = fb.text.splitlines()
            for rule_id, pat, label, cwe, vector in _RULES:
                hits = []
                for i, line in enumerate(lines, start=1):
                    if pat.search(line):
                        hits.append((i, line.strip()[:160]))
                    if len(hits) >= _MAX_LINES:
                        break
                if not hits:
                    continue
                excerpt = "\n".join(f"L{n}: {t}" for n, t in hits)
                ev = ctx.evidence.from_file(
                    fb.path, etype="config", responsible_role="Rol Técnico de Investigación",
                    result=f"{len(hits)} coincidencia(s): {label}",
                    description=f"{label} en {fb.rel}.",
                    relevance=f"Indicador de {label} ({', '.join(cwe)}).",
                    excerpt_masked=excerpt, line=hits[0][0],
                )
                findings.append(build_finding(
                    detector_id=self.id, rule=rule_id,
                    title=f"{label.capitalize()} en {fb.rel}",
                    description=(
                        f"Se detectó {label}. Requiere validación: puede ser uso legítimo "
                        "(p. ej. hash no de seguridad) o un control criptográfico débil real."
                    ),
                    component=fb.rel, finding_type="technical",
                    evidence_ids=[ev.id], cwe=cwe, cvss_vector=vector,
                    reproduction_command=f'grep -niE "{pat.pattern}" "{fb.rel}"',
                    reproduction_expected="líneas coincidentes",
                    remediation="Usar algoritmos vigentes (SHA-256+, AES-GCM), activar verificación TLS y forzar https en endpoints sensibles.",
                    recommendations="Centralizar la política criptográfica y revisar con un linter de seguridad.",
                    confidence="indirect",
                    impact_compliance="A.8.24 uso de criptografía; protección de datos en tránsito.",
                    notes="Falso positivo posible: MD5/SHA1 fuera de contexto de seguridad, o http a servicios internos.",
                ))
        return findings
