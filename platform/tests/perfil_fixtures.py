"""Insumos SINTÉTICOS para las pruebas de S05 — El perfil (principio III)."""
from __future__ import annotations

from pathlib import Path

import cita_fixtures as cfx
from c4a import cita

ROTULO = cfx.ROTULO
ACTIVO = cfx.ACTIVO
FECHA = cfx.FECHA
N_RIESGOS = cfx.N_RIESGOS
N_VACIOS = cfx.N_VACIOS


def construir(raiz: Path, *, perfil_previo: bool = True, firmado: bool = False) -> Path:
    """Repositorio temporal con la cita de S04 sintética; opcionalmente firmada."""
    cfx.construir(raiz)
    cita.abrir(raiz, fecha=FECHA)
    if firmado:
        cita.revisar(raiz, "Auditor", "revisión", FECHA)
        cita.firmar(raiz, "Auditor", "firma sintética", FECHA)
    return raiz
