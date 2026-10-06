"""Detector: permisos de archivo riesgosos (POSIX).

Marca archivos world-writable (otros pueden escribir). En Windows/NTFS los bits
POSIX no son significativos; en ese caso el detector no reporta y lo deja dicho,
para no concluir sobre un dato que el sistema de archivos no expresa.
"""
from __future__ import annotations

import os
import stat
from typing import List

from ..model import Finding
from .base import Detector, DetectorContext, build_finding

_MAX = 50


class PermissionsDetector(Detector):
    id = "permissions"
    title = "Permisos de archivos"
    finding_type = "control"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        if os.name != "posix":
            return []  # los bits POSIX no aplican en este FS; sin conclusión
        findings: List[Finding] = []
        world_writable: List[str] = []
        for fb in ctx.files:
            try:
                mode = os.stat(fb.path).st_mode
            except OSError:
                continue
            if mode & stat.S_IWOTH:
                world_writable.append(f"{fb.rel} ({stat.filemode(mode)})")
            if len(world_writable) >= _MAX:
                break
        if not world_writable:
            return findings
        first = world_writable[0].split(" ")[0]
        ev = ctx.evidence.from_command(
            command="find <target> -type f -perm -o+w",
            output="\n".join(world_writable),
            etype="permission", responsible_role="Rol de Control de Seguridad",
            result=f"{len(world_writable)} archivo(s) world-writable",
            description="Archivos escribibles por cualquier usuario del sistema.",
            relevance="Permisos incorrectos sobre recurso crítico (CWE-732).",
        )
        findings.append(build_finding(
            detector_id=self.id, rule="world-writable",
            title=f"{len(world_writable)} archivo(s) world-writable",
            description="Uno o más archivos del objetivo son escribibles por cualquier usuario (bit o+w), lo que permite manipular su contenido.",
            component=first, finding_type="control",
            evidence_ids=[ev.id], cwe=["CWE-732"],
            cvss_vector="CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N",
            reproduction_command="find <target> -type f -perm -o+w",
            reproduction_expected="lista de archivos con permiso de escritura para otros",
            remediation="Retirar el permiso de escritura a 'otros' (chmod o-w) y revisar la política de permisos del repositorio.",
            recommendations="Aplicar umask restrictivo y revisar en CI.",
            confidence="direct",
            impact_compliance="A.8.3 restricción de acceso; A.8.9 configuración.",
        ))
        return findings
