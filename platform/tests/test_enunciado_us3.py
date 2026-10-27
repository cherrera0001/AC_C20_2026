"""S03 US3 — Un hecho negativo o inconcluso no es un cumplimiento. Insumos SINTÉTICOS."""
import re
import tempfile
import unittest
from pathlib import Path

import enunciado_fixtures as fx
from c4a import enunciado

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class TestNegativoNoEsCumplimiento(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        self.c = enunciado.abrir(self.raiz)

    def tearDown(self):
        self._tmp.cleanup()

    def test_esc1_negativo_con_nota_fija(self):
        neg = next(e for e in self.c["enunciados"] if e["hecho"]["resultado"] == "negativo")
        self.assertIn("no acredita cumplimiento", neg["consecuencia"])
        self.assertIn("reevaluar", " ".join(neg["falta"]))

    def test_esc2_inconcluso_pide_evidencia_adicional(self):
        inc = next(e for e in self.c["enunciados"] if e["hecho"]["resultado"] == "inconcluso")
        self.assertIn("evidencia adicional para decidir", inc["falta"])

    def test_esc3_cero_estados_de_cumplimiento_en_todo(self):
        for nombre in (enunciado.ARCHIVO_JSON, enunciado.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
        for e in self.c["enunciados"]:
            t = (self.raiz / f"03_hallazgos/enunciado-{e['id']}.md").read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotIn("sin hallazgos", t.lower())

    def test_esc4_resumen_sin_sin_hallazgos(self):
        vista = (self.raiz / enunciado.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn(f"{fx.N_HECHOS} enunciados", vista)
        self.assertIn(f"{fx.N_VACIOS} vacíos", vista)
        self.assertNotIn("sin hallazgos", vista.lower())


if __name__ == "__main__":
    unittest.main()
