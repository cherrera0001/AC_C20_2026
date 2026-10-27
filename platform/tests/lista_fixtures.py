"""Insumos SINTÉTICOS para las pruebas de S06 — La lista (principio III)."""
from __future__ import annotations

from pathlib import Path

import perfil_fixtures as pfx
from c4a import perfil

ROTULO = pfx.ROTULO
ACTIVO = pfx.ACTIVO
FECHA = pfx.FECHA


def construir(raiz: Path, *, perfil_json: bool = True, firmado: bool = False) -> Path:
    """Repositorio temporal con el perfil de S05 sintético; opcionalmente firmado."""
    pfx.construir(raiz)
    if not perfil_json:
        return raiz
    perfil.abrir(raiz, fecha=FECHA)
    if firmado:
        for f in perfil.FUNCIONES:
            perfil.corregir(raiz, f, "sintesis", f"Lectura sintética de {f}", "completar",
                            "Auditor", FECHA)
        perfil.revisar(raiz, "Auditor", "revisión", FECHA)
        perfil.firmar(raiz, "Auditor", "firma sintética", FECHA)
    return raiz
