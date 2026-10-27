"""Insumos SINTÉTICOS para las pruebas de S08 — Las dos frases (principio III)."""
from __future__ import annotations

from pathlib import Path

import encargo_fixtures as efx
from c4a import encargo

ROTULO = efx.ROTULO
ACTIVO = efx.ACTIVO
FECHA = efx.FECHA
N_RIESGOS = 3
N_VACIOS = 2


def construir(raiz: Path, *, encargo_json: bool = True) -> Path:
    """Repositorio temporal con el encargo de S07 sintético."""
    efx.construir(raiz)
    if encargo_json:
        encargo.abrir(raiz, fecha=FECHA)
    return raiz
