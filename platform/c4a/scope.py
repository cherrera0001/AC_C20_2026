"""Gestor de alcance (Fase 1) y acceso de SOLO LECTURA al objetivo.

Hace cumplir tres reglas del alcance:
  1. Nada fuera del directorio objetivo se lee (guarda contra path traversal).
  2. La plataforma nunca escribe en el objetivo: solo abre archivos para leer.
  3. Se respetan exclusiones (node_modules, .git, binarios, archivos enormes).
"""
from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterator, List

from .config import Config

# Extensiones de activo/binario que no se abren: no son auditables como texto y
# leerlas enteras es el grueso del costo en repos grandes.
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff", ".svg",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".mov", ".mp3", ".wav", ".webm", ".avi", ".mkv", ".flac",
    ".zip", ".gz", ".tar", ".tgz", ".bz2", ".rar", ".7z", ".jar", ".whl", ".xz",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".a", ".class", ".wasm", ".node",
    ".pdf", ".parquet", ".sqlite", ".db", ".mo", ".map", ".pyc", ".pack", ".idx",
}


class ScopeManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.target = cfg.target
        self.skipped_large: List[str] = []
        self.skipped_binary: List[str] = []
        self.skipped_symlink: List[str] = []
        self.skipped_asset: int = 0
        self.truncated: bool = False

    def within_scope(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.target)
            return True
        except ValueError:
            return False

    def _excluded(self, rel: Path) -> bool:
        parts = set(rel.parts)
        if parts & set(self.cfg.exclude_dirs):
            return True
        rel_str = rel.as_posix()
        for pat in self.cfg.exclude_globs:
            if fnmatch.fnmatch(rel_str, pat):
                return True
        return False

    def iter_files(self) -> Iterator[Path]:
        """Itera archivos del objetivo, aplicando exclusiones y límites.

        Usa os.walk y PODA los directorios excluidos EN EL RECORRIDO, sin
        descender en ellos. Es la diferencia entre tocar unos miles de archivos
        y perderse en el almacén .pnpm de node_modules (miles de symlinks). No
        se siguen symlinks, para evitar bucles y salidas del alcance.
        """
        excl = set(self.cfg.exclude_dirs)
        emitted = 0
        for dirpath, dirnames, filenames in os.walk(self.target, followlinks=False):
            # poda in-place: os.walk no desciende en lo que se quita de dirnames
            dirnames[:] = [
                d for d in dirnames
                if d not in excl and not os.path.islink(os.path.join(dirpath, d))
            ]
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                if os.path.islink(full):
                    self.skipped_symlink.append(fn)
                    continue
                path = Path(full)
                ext = path.suffix.lower()
                if ext in BINARY_EXT:
                    self.skipped_asset += 1
                    continue
                rel = path.relative_to(self.target)
                if self._excluded(rel):
                    continue
                # include_ext vacío = todas las extensiones; si se define, solo esas.
                if self.cfg.include_ext and ext not in self.cfg.include_ext:
                    continue
                try:
                    size = os.path.getsize(full)
                except OSError:
                    continue
                if size > self.cfg.max_file_bytes:
                    self.skipped_large.append(rel.as_posix())
                    continue
                emitted += 1
                if emitted > self.cfg.max_files:
                    self.truncated = True
                    return
                yield path

    def rel(self, path: Path) -> str:
        return path.relative_to(self.target).as_posix()

    def read_text(self, path: Path) -> str:
        """Lee un archivo como texto (solo lectura). Devuelve '' si es binario."""
        if not self.within_scope(path):
            raise PermissionError(f"fuera de alcance: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except (UnicodeDecodeError, ValueError):
            self.skipped_binary.append(self.rel(path))
            return ""
        except OSError:
            return ""
