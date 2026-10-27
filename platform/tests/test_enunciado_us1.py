"""S03 US1 — Abrir el enunciado sin registro firmado. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import enunciado_fixtures as fx
import registro_fixtures as rfx
from c4a import enunciado
from c4a import registro
from c4a.util import sha256_file

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / enunciado.ARCHIVO_JSON).read_text(encoding="utf-8"))

    def vista(self):
        return (self.raiz / enunciado.ARCHIVO_MD).read_text(encoding="utf-8")


class TestAbrir(Base):
    def test_sc001_h_enunciados_y_m_vacios(self):
        fx.construir(self.raiz)
        c = enunciado.abrir(self.raiz)
        self.assertEqual(len(c["enunciados"]), fx.N_HECHOS)
        self.assertEqual(len(c["vacios"]), fx.N_VACIOS)
        for e in c["enunciados"]:
            self.assertRegex(e["id"], r"^R-[0-9a-f]{10}$")
            self.assertEqual(e["estado_aprobacion"], "borrador")
            self.assertEqual(e["impacto"], "")
            self.assertGreaterEqual(len(e["evidencias"]), 1)

    def test_esc2_fr001_sin_registro_codigo_2_y_nada_escrito(self):
        rfx.construir(self.raiz)
        hall = self.raiz / "03_hallazgos"
        hall.mkdir(parents=True)
        antes = sorted(p.name for p in hall.iterdir())
        with self.assertRaises(enunciado.EnunciadoError) as cm:
            enunciado.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)
        self.assertEqual(sorted(p.name for p in hall.iterdir()), antes)

    def test_esc3_fr002_registro_firmado_cita_huella(self):
        fx.construir(self.raiz, firmado=True)
        c = enunciado.abrir(self.raiz)
        self.assertTrue(c["origen"]["firmado"])
        self.assertEqual(c["origen"]["sha256"], sha256_file(self.raiz / registro.ARCHIVO_JSON))
        self.assertIn("firmado", self.vista())

    def test_fr004_fr005_campos_y_propuestas(self):
        fx.construir(self.raiz)
        c = enunciado.abrir(self.raiz)
        for e in c["enunciados"]:
            self.assertEqual(e["condicion"], e["hecho"]["afirmacion"])
            self.assertTrue(e["consecuencia"])
            self.assertTrue(e["criterio"])
            self.assertIn("S04", e["criterio"])
            if e["hecho"]["resultado"] == "positivo":
                self.assertIn("se observa", e["consecuencia"])
            if e["hecho"]["resultado"] == "inconcluso":
                self.assertIn("evidencia adicional para decidir", e["falta"])
            if e["hecho"]["resultado"] == "negativo":
                self.assertTrue(any("reevaluar" in f for f in e["falta"]))

    def test_sc002_citan_hecho_y_evidencia_con_huella(self):
        fx.construir(self.raiz)
        c = enunciado.abrir(self.raiz)
        for e in c["enunciados"]:
            self.assertTrue(e["hecho"]["id"])
            for ev in e["evidencias"]:
                self.assertTrue(ev["sha256_original"])

    def test_sc003_busqueda_limpia(self):
        fx.construir(self.raiz)
        enunciado.abrir(self.raiz)
        for nombre in (enunciado.ARCHIVO_JSON, enunciado.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotIn("sin hallazgos", t.lower())
            self.assertNotRegex(t, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

    def test_sc007_dos_aperturas_bytes_identicos(self):
        fx.construir(self.raiz)
        enunciado.abrir(self.raiz)
        a = (self.raiz / enunciado.ARCHIVO_JSON).read_bytes()
        enunciado.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / enunciado.ARCHIVO_JSON).read_bytes())

    def test_sc010_no_toca_previos_de_hallazgos(self):
        fx.construir(self.raiz)
        hall = self.raiz / "03_hallazgos"
        hall.mkdir(parents=True)
        previo = hall / "matriz_cumplimiento.csv"
        previo.write_text("fixture\n", encoding="utf-8")
        antes = sha256_file(previo)
        enunciado.abrir(self.raiz)
        self.assertEqual(sha256_file(previo), antes)

    def test_fr012_fichas_por_enunciado(self):
        fx.construir(self.raiz)
        c = enunciado.abrir(self.raiz)
        for e in c["enunciados"]:
            ficha = self.raiz / f"03_hallazgos/enunciado-{e['id']}.md"
            self.assertTrue(ficha.is_file())
            texto = ficha.read_text(encoding="utf-8")
            self.assertIn(e["condicion"], texto)
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(texto))
            self.assertNotIn("FIXTURE SINTÉTICO", texto)


if __name__ == "__main__":
    unittest.main()
