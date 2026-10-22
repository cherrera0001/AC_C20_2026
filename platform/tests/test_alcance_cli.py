"""S01 — Códigos de salida del subcomando `alcance` (contracts/cli-alcance.md), sobre insumos SINTÉTICOS."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import alcance_fixtures as fx
from c4a import alcance
from c4a.cli import main


def _correr(*args) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main(["alcance", *args])


class TestCliAlcance(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        self.r = str(self.raiz)

    def tearDown(self):
        self._tmp.cleanup()

    def _fila(self):
        d = json.loads((self.raiz / alcance.ARCHIVO_JSON).read_text(encoding="utf-8"))
        return d["filas"][0]["id"]

    def test_codigos_de_salida(self):
        self.assertEqual(_correr("verificar", "--raiz", self.r), 2)            # falta el producto
        self.assertEqual(_correr("proponer", "--raiz", self.r), 0)
        self.assertEqual(_correr("compuerta", "--raiz", self.r, "--fecha-referencia", "2026-10-21"), 0)
        self.assertEqual(_correr("firmar", "--raiz", self.r, "--firmante", "A", "--motivo", "m"), 1)  # borrador
        fid = self._fila()
        self.assertEqual(_correr("corregir", "--raiz", self.r, "--fila", fid, "--campo", "motivo",
                                 "--valor", "x", "--motivo", " ", "--autor", "A"), 1)  # sin motivo
        self.assertEqual(_correr("corregir", "--raiz", self.r, "--fila", fid, "--campo", "motivo",
                                 "--valor", "x", "--motivo", "Revisión", "--autor", "A"), 0)
        self.assertEqual(_correr("firmar", "--raiz", self.r, "--firmante", "A", "--motivo", " "), 1)  # sin justificación
        self.assertEqual(_correr("firmar", "--raiz", self.r, "--firmante", "A", "--motivo", "Revisado"), 0)
        self.assertEqual(_correr("verificar", "--raiz", self.r), 0)
        self.assertEqual(_correr("consultar", "--raiz", self.r, "--tipo", "activo", "--valor", "Otra"), 0)
        ruta = self.raiz / alcance.INSUMO_ALCANCE
        ruta.write_text(ruta.read_text(encoding="utf-8") + "\n- Nuevo supuesto.\n", encoding="utf-8")
        self.assertEqual(_correr("proponer", "--raiz", self.r), 4)            # firmado, insumo cambió
        js = self.raiz / alcance.ARCHIVO_JSON
        js.write_bytes(js.read_bytes() + b" ")
        self.assertEqual(_correr("verificar", "--raiz", self.r), 3)           # alterado


if __name__ == "__main__":
    unittest.main()
