"""Insumos SINTÉTICOS para las pruebas de S04 — La cita (principio III)."""
from __future__ import annotations

from pathlib import Path

import enunciado_fixtures as efx
from c4a import enunciado

ROTULO = efx.ROTULO
ACTIVO = efx.ACTIVO
FECHA = efx.FECHA
N_RIESGOS = efx.N_HECHOS
N_VACIOS = efx.N_VACIOS


def construir(raiz: Path, *, enunciado_json: bool = True, firmado: bool = False) -> Path:
    """Repositorio temporal con el enunciado de S03 sintético y la cita abierta."""
    efx.construir(raiz)
    if not enunciado_json:
        return raiz
    enunciado.abrir(raiz, fecha=FECHA)
    if firmado:
        c = enunciado.cargar(raiz)
        for e in c["enunciados"]:
            enunciado.corregir(raiz, e["id"], "criterio", "Criterio", "x", "Auditor", FECHA)
            enunciado.corregir(raiz, e["id"], "impacto", "Impacto", "x", "Auditor", FECHA)
        enunciado.revisar(raiz, "Auditor", "revisión", FECHA)
        enunciado.firmar(raiz, "Auditor", "firma sintética", FECHA)
    return raiz
