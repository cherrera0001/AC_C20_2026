"""Insumos SINTÉTICOS para las pruebas de S02 — El registro.

Rotulados como fixture (principio III de la constitución): su resultado demuestra la
herramienta, no audita el objetivo del ejercicio. Reutiliza el alcance sintético de S01.
"""
from __future__ import annotations

import json
from pathlib import Path

import alcance_fixtures as afx
from c4a import alcance

ROTULO = afx.ROTULO

# Del alcance sintético completo de S01: un activo y cuatro dominios (dos técnicos y dos de
# control), todos «pendiente de confirmar» hasta que el auditor decida (SC-001: N + 1).
N_DOMINIOS_FIXTURE = 4
ACTIVO = "MaquinaSintetica"
FECHA = "2026-10-22T10:00:00Z"
DIA = "2026-10-22"
VENTANA_VIGENTE = ("2026-10-01 09:00", "2026-10-31 18:00")
RUN_OTRO = "RUN-SINTETICO-OTRO"
RUN_ACTIVO = "RUN-SINTETICO-ACTIVO"


def construir(raiz: Path, *, alcance_json: bool = True, autorizada: bool = False, ledger: bool = True) -> Path:
    """Repositorio temporal con el alcance sintético de S01; opcionalmente una autorización
    firmada, completa y vigente, y un ledger con una corrida sobre otro objetivo."""
    kw = {}
    if autorizada:
        kw = {"firmada": True, "ventana": VENTANA_VIGENTE, "organizacion": "Org Sintética",
              "exclusiones": "Ninguna adicional"}
    afx.construir(raiz, **kw)
    if alcance_json:
        alcance.proponer(raiz)
    if ledger:
        estado = raiz / ".c4a"
        estado.mkdir(parents=True, exist_ok=True)
        corridas = [{"run_id": RUN_OTRO, "target": "/repos/otro-proyecto-sintetico"},
                    {"run_id": RUN_ACTIVO, "target": ACTIVO}]
        (estado / "runs.jsonl").write_text("".join(json.dumps(c) + "\n" for c in corridas), encoding="utf-8")
    return raiz


def evidencia(raiz: Path, nombre: str = "documento.txt", texto: str = "") -> Path:
    """Archivo de evidencia sintético, fuera de evidence/ (como lo traería el auditor)."""
    carpeta = raiz / "aportes"
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    ruta.write_text(f"{ROTULO}\n{texto or nombre}\n", encoding="utf-8")
    return ruta


def fila(raiz: Path, clave_prefijo: str) -> str:
    """Id de la fila de dominio del alcance cuya clave empieza por el prefijo dado."""
    filas = alcance.cargar(raiz)["filas"]
    return next(f["id"] for f in filas if f["tipo"] == "dominio" and f["clave"].startswith(clave_prefijo))


def decidir(raiz: Path, fila_id: str, decision: str) -> None:
    """El auditor sintético decide una fila del alcance (para tener «dentro» y «fuera»)."""
    alcance.corregir(raiz, fila_id, "decision", decision, "decisión sintética de prueba", "Auditor Sintético", FECHA)


def huellas(carpeta: Path) -> dict:
    from c4a.util import sha256_file
    return {p.relative_to(carpeta).as_posix(): sha256_file(p) for p in sorted(carpeta.rglob("*")) if p.is_file()}
