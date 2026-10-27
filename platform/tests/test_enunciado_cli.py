"""S03 — Contrato del subcomando `enunciado`: códigos de salida 0, 1, 2 y 4."""
import json
import tempfile
import unittest
from pathlib import Path

import enunciado_fixtures as fx
from c4a import cli
from c4a import enunciado


class TestCliEnunciado(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        self._out = None

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["enunciado", *argv, "--raiz", str(self.raiz)])

    def test_abrir_sin_registro_codigo_2(self):
        self.assertEqual(self.main("abrir"), 2)

    def test_flujo_codigos_0_y_1(self):
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        self.assertEqual(self.main("corregir", "--enunciado", "R-0000000000", "--campo", "impacto",
                                   "--valor", "x", "--motivo", "m", "--autor", "A"), 1)
        c = json.loads((self.raiz / enunciado.ARCHIVO_JSON).read_text(encoding="utf-8"))
        eid = c["enunciados"][0]["id"]
        self.assertEqual(self.main("corregir", "--enunciado", eid, "--campo", "impacto",
                                   "--valor", "impacto", "--motivo", "m", "--autor", "A"), 0)
        self.assertEqual(self.main("firmar", "--firmante", "A", "--motivo", "sin revisar"), 1)
        self.assertEqual(self.main("entregar"), 0)

    def test_entregar_json(self):
        fx.construir(self.raiz)
        self.main("abrir")
        # entregar con --json no cambia el estado
        self.assertEqual(self.main("entregar", "--json"), 0)


if __name__ == "__main__":
    unittest.main()
