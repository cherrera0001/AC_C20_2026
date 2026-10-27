"""Puntaje base CVSS v4.0 (decisión: docs/DECISION_TESIS_CANONICA.md).

El núcleo de C4A no tiene dependencias externas (ver requirements.txt). El cálculo v4.0
necesita las tablas de macrovectores de FIRST, así que se delega en el paquete opcional
`cvss` (LGPL-3.0, instalado a mano; no se copia su código aquí). Si el paquete no está,
el bloque sale sin puntaje y con el motivo: no se inventa ningún valor.
"""

from typing import Dict, Optional

PREFIJO = "CVSS:4.0/"


def disponible() -> bool:
    try:
        import cvss  # noqa: F401
        return True
    except ImportError:
        return False


def base_score(vector: str) -> Optional[float]:
    """Puntaje base CVSS v4.0 para un vector completo, o None si el paquete no está."""
    if not disponible():
        return None
    from cvss import CVSS4
    return float(CVSS4(vector).base_score)


def evaluate(vector: str, source: str = "detector-baseline") -> Dict[str, object]:
    """Bloque CVSS v4.0 de un hallazgo. Sin el paquete opcional, la puntuación queda vacía."""
    if not vector.startswith(PREFIJO):
        raise ValueError("el vector CVSS v4.0 debe empezar por 'CVSS:4.0/'")
    score = base_score(vector)
    bloque: Dict[str, object] = {
        "version": "4.0",
        "vector": vector,
        "base_score": score,
        "source": source,
    }
    if score is None:
        bloque["motivo"] = "paquete opcional 'cvss' no instalado; puntaje no calculado"
    else:
        from cvss import CVSS4
        bloque["base_severity"] = CVSS4(vector).severity
    return bloque
