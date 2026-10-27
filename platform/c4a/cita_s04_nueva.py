"""S04 — La cita: cada riesgo vigente de S03 ubicado en un marco, con su identificador.

La herramienta ABRE la cita a partir de la entrega de S03 (`enunciado.entregar`) y PROPONE una
correspondencia riesgo ↔ control como sugerencia explicada. El identificador de un control solo
se propone si consta en la base de conocimiento; si no, queda «pendiente-confirmar» (principio
IV). El auditor CORRIGE, AÑADE correspondencias, DESCARTA, RESTABLECE, REVISA y FIRMA (principio I).
Una cita no dictamina cumplimiento (principio II). Nada de este módulo abre la compuerta de
autorización, ejecuta pruebas ni escribe fuera de `03_hallazgos/`.

Archivos que produce (ver specs/004-cita-marco/data-model.md):
  - 03_hallazgos/citas_s04.json        contenido canónico (lo que se firma)
  - 03_hallazgos/citas_s04.firma.json  firma: firmante, fecha, justificación y huella
  - 03_hallazgos/citas_s04.md          vista legible
  - 03_hallazgos/cita-<id>.md          ficha legible por cita

Esta versión es la reescritura decidida en T002 (specs/004-cita-marco/tasks.md → Notes). La
construcción sigue el orden de tasks.md: este archivo contiene por ahora la base (T004).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from . import alcance
from .util import sha256_file

PRODUCTO = "S04 — La cita"
VERSION_ESQUEMA = "1"
ARCHIVO_ENTREGA = "03_hallazgos/enunciados_s03.json"
ARCHIVO_JSON = "03_hallazgos/citas_s04.json"
ARCHIVO_FIRMA = "03_hallazgos/citas_s04.firma.json"
ARCHIVO_MD = "03_hallazgos/citas_s04.md"
PREFIJO_FICHA = "03_hallazgos/cita-"

# Marcos de la constitución (principio IV). Ningún otro se propone.
MARCOS = ("ISO-27001:2022", "NIST-CSF:2.0", "CIS-v8.1", "aporte del auditor")
ESTADOS_IDENTIFICADOR = ("confirmado", "pendiente-confirmar")
APROBACION = ("borrador", "revisado")  # «firmado» se deriva de una firma válida
CAMPOS_CORREGIBLES = ("marco", "control", "fundamento", "motivo")
MARCA_DESCARTADO = "descartado"
MARCA_RIESGO_NO_VIGENTE = "riesgo no vigente"
MARCA_ALTERADA = "evidencia alterada"
MARCAS = (MARCA_DESCARTADO, MARCA_RIESGO_NO_VIGENTE, MARCA_ALTERADA)
EVENTOS = ("propuesta", "correccion", "correspondencia", "descarte", "restablecimiento",
           "revision", "firma_anulada")

# Claves exactas del contenido canónico (contracts/citas_s04.schema.json, additionalProperties: false).
CLAVES_CANONICAS = ("producto", "version_esquema", "entrega", "citas", "vacios",
                    "estado_aprobacion", "historial", "avisos")


class CitaError(Exception):
    """Error de la cita con código de salida (ver contracts/cli-cita.md).

    1 regla de edición · 2 falta el producto anterior o un argumento · 3 huella que no
    corresponde · 4 la entrega de S03 cambió.
    """

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "firma": r / ARCHIVO_FIRMA, "md": r / ARCHIVO_MD,
            "entrega": r / ARCHIVO_ENTREGA}


def cargar(raiz) -> Dict[str, Any]:
    """Lee el contenido canónico. Sin el producto, código 2 (no se escribe nada)."""
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise CitaError(f"no existe {ARCHIVO_JSON}: ejecute primero «cita abrir»", 2)
    return _leer(ruta)


def _leer(ruta: Path) -> Dict[str, Any]:
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _validar_forma(contenido: Dict[str, Any]) -> None:
    """Exige exactamente las claves canónicas (FR-018). Una forma distinta no se escribe."""
    if sorted(contenido.keys()) != sorted(CLAVES_CANONICAS):
        faltan = sorted(set(CLAVES_CANONICAS) - set(contenido))
        sobran = sorted(set(contenido) - set(CLAVES_CANONICAS))
        raise CitaError(f"contenido no canónico (faltan {faltan or 'ninguna'}, sobran {sobran or 'ninguna'})", 1)


def _escribir(raiz, contenido: Dict[str, Any]) -> None:
    """Escribe el JSON canónico con bytes exactos. No escribe la vista (eso es T010)."""
    _validar_forma(contenido)
    p = _rutas(raiz)
    p["json"].parent.mkdir(parents=True, exist_ok=True)
    p["json"].write_bytes(alcance.serializar(contenido))


def _anular_firma(raiz, historial: list, autor: str, fecha: str) -> None:
    """Si hay firma, la elimina y deja constancia en el historial (FR-008)."""
    ruta = _rutas(raiz)["firma"]
    if ruta.exists():
        ruta.unlink()
        historial.append({"tipo": "firma_anulada", "autor": autor, "fecha": fecha,
                          "motivo": "Cambio posterior a la firma: se exige una nueva firma."})


def _guardar(raiz, contenido: Dict[str, Any], evento: Dict[str, Any]) -> Dict[str, Any]:
    """Único punto de escritura de las acciones del auditor (FR-015). Agrega el evento, anula una
    firma previa y escribe. Quien llama modifica antes `citas`; aquí solo se registra y persiste."""
    if evento.get("tipo") not in EVENTOS:
        raise CitaError(f"evento no válido: {evento.get('tipo')}", 1)
    historial = list(contenido["historial"]) + [evento]
    _anular_firma(raiz, historial, evento["autor"], evento["fecha"])
    nuevo = dict(contenido, historial=historial)
    _escribir(raiz, nuevo)
    return nuevo


def _texto_libre(valor: Optional[str], nombre: str) -> str:
    """Texto escrito por el auditor: obligatorio y limpio de direcciones de red."""
    v = (valor or "").strip()
    if not v:
        raise CitaError(f"falta {nombre}: es obligatorio")
    return alcance.limpiar(v)
