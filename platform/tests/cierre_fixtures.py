"""Insumos SINTÉTICOS para las pruebas de S10 — El cierre (principio III)."""
from __future__ import annotations

from pathlib import Path

import borrador_fixtures as bfx
from c4a import borrador

ROTULO = bfx.ROTULO
ACTIVO = bfx.ACTIVO
FECHA = bfx.FECHA


def construir(raiz: Path, *, borrador_json: bool = True, firmado: bool = True) -> Path:
    """Repositorio temporal con el borrador de S09 sintético (firmado por defecto)."""
    bfx.construir(raiz)
    if not borrador_json:
        return raiz
    borrador.abrir(raiz, fecha=FECHA)
    if firmado:
        borrador.revisar(raiz, "Auditor", "revisión", FECHA)
        borrador.firmar(raiz, "Auditor", "firma sintética", FECHA)
    return raiz
