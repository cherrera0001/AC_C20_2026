"""S08 — Las dos frases: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import frases_fixtures as fx
from c4a import cli
from c4a import frases

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / frases.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_dos_frases_mismos_conteos(self):
        fx.construir(self.raiz)
        c = frases.abrir(self.raiz)
        g, t = c["frases"]["gerencia"]["texto"], c["frases"]["tecnica"]["texto"]
        self.assertTrue(g and t)
        self.assertIn(str(fx.N_RIESGOS), g)
        self.assertIn(str(fx.N_RIESGOS), t)
        self.assertIn(str(fx.N_VACIOS), g)
        self.assertIn(str(fx.N_VACIOS), t)
        self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(g))
        self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
        self.assertIsNone(re.search(r"\bA\.\d", g))

    def test_esc2_fr001_sin_encargo_codigo_2(self):
        fx.construir(self.raiz, encargo_json=False)
        with self.assertRaises(frases.FrasesError) as cm:
            frases.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_fr005_vacios_con_la_misma_causa(self):
        fx.construir(self.raiz)
        c = frases.abrir(self.raiz)
        g = c["frases"]["gerencia"]["texto"]
        t = c["frases"]["tecnica"]["texto"]
        self.assertIn("pendientes", g)
        self.assertIn("vacíos", t)

    def test_fr012_fichas(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz)
        self.assertTrue((self.raiz / frases.FICHA_GERENCIA).is_file())
        self.assertTrue((self.raiz / frases.FICHA_TECNICA).is_file())

    def test_sc007_determinismo(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz)
        a = (self.raiz / frases.ARCHIVO_JSON).read_bytes()
        frases.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / frases.ARCHIVO_JSON).read_bytes())


class TestCorregirFirmar(Base):
    def test_esc1_correccion_valida(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz, fecha=fx.FECHA)
        c = self.leer()
        nueva = c["frases"]["gerencia"]["texto"].replace("3 riesgos", "3 riesgos prioritarios")
        f = frases.corregir(self.raiz, "gerencia", nueva, "precisar para la sala", "Auditor", fx.FECHA)
        self.assertIn("prioritarios", f["frases"]["gerencia"]["texto"])
        self.assertEqual(f["frases"]["gerencia"]["correcciones"][-1]["autor"], "Auditor")

    def test_esc3_correccion_que_rompe_conteo_se_rechaza(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz, fecha=fx.FECHA)
        c = self.leer()
        mala = c["frases"]["gerencia"]["texto"].replace("3 riesgos", "2 riesgos")
        with self.assertRaises(frases.FrasesError) as cm:
            frases.corregir(self.raiz, "gerencia", mala, "cambiar un número", "Auditor", fx.FECHA)
        self.assertIn("consistencia", str(cm.exception))

    def test_esc2_texto_prohibido_se_rechaza(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz, fecha=fx.FECHA)
        with self.assertRaises(frases.FrasesError):
            frases.corregir(self.raiz, "gerencia", "El control cumple en su totalidad",
                            "m", "Auditor", fx.FECHA)

    def test_firma_exige_ambas_frases(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz, fecha=fx.FECHA)
        frases.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        f = frases.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        self.assertEqual(f["conteos_al_firmar"]["riesgos"], fx.N_RIESGOS)
        self.assertEqual(frases.estado_efectivo(self.raiz), "firmado")

    def test_fr009_inconsistencia_detectada(self):
        fx.construir(self.raiz)
        frases.abrir(self.raiz, fecha=fx.FECHA)
        frases.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        frases.firmar(self.raiz, "Auditor", "firma", fx.FECHA)
        # alterar un byte de la frase de gerencia rompe un conteo: verificar lo marca
        ruta = self.raiz / frases.ARCHIVO_JSON
        datos = bytearray(ruta.read_bytes())
        idx = datos.find("3 riesgos".encode("utf-8"))
        datos[idx] = ord("2")
        datos[idx + 1] = ord(" ")
        ruta.write_bytes(bytes(datos))
        v = frases.verificar(self.raiz)
        self.assertTrue(v["inconsistencias"])


class TestCliFrases(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["frases", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, encargo_json=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
