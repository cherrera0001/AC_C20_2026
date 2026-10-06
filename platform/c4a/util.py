"""Utilidades transversales: tiempo, hashing e identificadores deterministas.

Los identificadores de hallazgo y evidencia se derivan del CONTENIDO, no del
reloj: la misma entrada produce el mismo id en cada corrida. Eso es lo que
hace comparable una reproducción contra su detección original.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from datetime import datetime, timezone


def now_iso() -> str:
    """Instante actual en ISO-8601 UTC, con segundos."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8", errors="replace"))


def sha256_file(path) -> str:
    """Hash SHA-256 de un archivo, leído en bloques (no carga todo en memoria)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def short_id(prefix: str, *parts: str, length: int = 10) -> str:
    """Id determinista: prefijo + hash corto del contenido unido.

    Ej.: short_id("F", "dockerfile", "apps/api/Dockerfile", "runs-as-root").
    """
    material = "\x1f".join(str(p) for p in parts)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}-{digest}"


def mask_secret(value: str, keep: int = 4) -> str:
    """Enmascara un valor sensible dejando solo los primeros `keep` caracteres.

    Regla del alcance: los datos sensibles que aparezcan se enmascaran de
    inmediato; nunca se vuelca un secreto en claro a un informe.
    """
    value = value.strip()
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep)


_SECRET_LINE = re.compile(
    r"""(?ix)
    (password|passwd|pwd|secret|token|api[_-]?key|apikey|
     access[_-]?key|private[_-]?key|client[_-]?secret|
     authorization|bearer)
    \s*[:=]\s*
    ['"]?(?P<val>[A-Za-z0-9/\+\=_\-\.]{6,})['"]?
    """
)


def redact_line(line: str) -> str:
    """Devuelve la línea con cualquier valor de secreto enmascarado."""
    def _sub(m: "re.Match") -> str:
        return m.group(0).replace(m.group("val"), mask_secret(m.group("val")))
    return _SECRET_LINE.sub(_sub, line).rstrip("\n")


def shannon_entropy(text: str) -> float:
    """Entropía de Shannon en bits por carácter. Mide cuán 'aleatorio' es un valor.

    Sirve para distinguir un secreto real (alta entropía) de un marcador como
    'password' o 'example' (baja entropía), y así bajar los falsos positivos.
    """
    if not text:
        return 0.0
    n = len(text)
    counts = Counter(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


_COMMENT_PREFIXES = ("#", "//", "*", "--", "<!--", '"""', "'''")


def is_comment_line(line: str) -> bool:
    """Heurística multilenguaje: ¿la línea es un comentario? (no es configuración viva)."""
    s = line.strip()
    return any(s.startswith(p) for p in _COMMENT_PREFIXES)


_IGNORE = re.compile(r"(?i)\b(c4a:ignore|nosec|noqa|lgtm)\b")


def has_ignore_marker(line: str) -> bool:
    """¿La línea trae un marcador de supresión en línea (c4a:ignore / nosec / noqa)?"""
    return bool(_IGNORE.search(line))
