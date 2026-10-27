"""Insumos SINTÉTICOS para las pruebas de S03 — El enunciado.

Rotulados como fixture (principio III de la constitución): su resultado demuestra la
herramienta, no audita el objetivo del ejercicio. Reutiliza el registro sintético de S02 y
deja hechos con cada resultado técnico (positivo, negativo, inconcluso) y «no consta».
"""
from __future__ import annotations

import json
from pathlib import Path

import registro_fixtures as rfx
from c4a import alcance
from c4a import registro

ROTULO = rfx.ROTULO
ACTIVO = rfx.ACTIVO
FECHA = rfx.FECHA
DIA = rfx.DIA

# Registro sintético completo: un hecho por resultado técnico + M «no consta».
N_HECHOS = 3
N_VACIOS = rfx.N_DOMINIOS_FIXTURE + 1 - N_HECHOS  # 5 entradas − 3 dominios con hecho = 2


def _dominio(raiz: Path, prefijo: str) -> str:
    return rfx.fila(raiz, prefijo)


def construir(raiz: Path, *, registro_json: bool = True, firmado: bool = False) -> Path:
    """Repositorio temporal con el registro de S02 sintético (H hechos y M «no consta»)."""
    rfx.construir(raiz)
    if not registro_json:
        return raiz
    registro.abrir(raiz)
    plan = [
        ("tecnico:1", "Se observa una condición de ejemplo en la superficie de red", "positivo"),
        ("tecnico:2", "Se buscó la condición y la evidencia muestra que no está", "negativo"),
        ("control:1", "La evidencia no permite decidir si la condición se materializa", "inconcluso"),
    ]
    for prefijo, afirmacion, resultado in plan:
        dom = _dominio(raiz, prefijo)
        doc = rfx.evidencia(raiz, f"doc_{prefijo.replace(':', '_')}.txt", afirmacion)
        registro.aportar(raiz, ACTIVO, dom, afirmacion, resultado, doc, "documental", DIA,
                         "Auditor Sintético", origen="del ejercicio", fecha=FECHA)
    if firmado:
        registro.revisar(raiz, "Auditor Sintético", "revisión sintética", FECHA)
        registro.firmar(raiz, "Auditor Sintético", "firma sintética", FECHA)
    return raiz


def leer(raiz: Path, modulo, archivo: str) -> dict:
    return json.loads((raiz / archivo).read_text(encoding="utf-8"))
