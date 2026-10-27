"""Insumos SINTÉTICOS para las pruebas de S07 — El encargo (principio III)."""
from __future__ import annotations

from pathlib import Path

import lista_fixtures as lfx
from c4a import lista

ROTULO = lfx.ROTULO
ACTIVO = lfx.ACTIVO
FECHA = lfx.FECHA


def construir(raiz: Path, *, completo: bool = True) -> Path:
    """Repositorio temporal con la cadena S01–S06 sintética completa."""
    lfx.construir(raiz)
    if completo:
        lista.abrir(raiz, fecha=FECHA)
    return raiz
