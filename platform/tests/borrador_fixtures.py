"""Insumos SINTÉTICOS para las pruebas de S09 — El borrador (principio III)."""
from __future__ import annotations

from pathlib import Path

import frases_fixtures as ffx
from c4a import frases

ROTULO = ffx.ROTULO
ACTIVO = ffx.ACTIVO
FECHA = ffx.FECHA
N_RIESGOS = ffx.N_RIESGOS
N_VACIOS = ffx.N_VACIOS


def construir(raiz: Path, *, frases_json: bool = True, firmado: bool = False) -> Path:
    """Repositorio temporal con las frases de S08 sintéticas; opcionalmente firmadas."""
    ffx.construir(raiz)
    if not frases_json:
        return raiz
    frases.abrir(raiz, fecha=FECHA)
    if firmado:
        frases.revisar(raiz, "Auditor", "revisión", FECHA)
        frases.firmar(raiz, "Auditor", "firma sintética", FECHA)
    return raiz
