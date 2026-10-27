"""S09 — El borrador: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import borrador_fixtures as fx
from c4a import borrador
from c4a import cli

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / borrador.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_secciones_completas(self):
        fx.construir(self.raiz)
        c = borrador.abrir(self.raiz)
        self.assertEqual([s["nombre"] for s in c["secciones"]],
                         ["encabezado", "resumen", "desarrollo", "acciones", "vacios", "anexo"])
        self.assertIn("Comercial Andes Sur SpA", c["cliente"])
        self.assertIn(str(fx.N_RIESGOS), next(s for s in c["secciones"] if s["nombre"] == "resumen")["contenido"])
        for s in c["secciones"]:
            self.assertTrue(s["huella_origen"])
        md = (self.raiz / borrador.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn("Informe de cierre", md)
        self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(md))

    def test_esc2_fr001_sin_frases_codigo_2(self):
        fx.construir(self.raiz, frases_json=False)
        with self.assertRaises(borrador.BorradorError) as cm:
            borrador.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_sc005_secciones_sin_material_conservadas(self):
        fx.construir(self.raiz)
        c = borrador.abrir(self.raiz)
        vacios = next(s for s in c["secciones"] if s["nombre"] == "vacios")
        self.assertIn("Vacíos declarados", vacios["contenido"])
        self.assertNotIn("sin hallazgos", vacios["contenido"].lower())

    def test_fr012_informe_legible_sin_extractos(self):
        fx.construir(self.raiz)
        borrador.abrir(self.raiz)
        md = (self.raiz / borrador.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertNotIn("FIXTURE SINTÉTICO", md)
        self.assertNotRegex(md, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

    def test_fr011_no_toca_previos(self):
        fx.construir(self.raiz)
        informe = self.raiz / "04_informe"
        informe.mkdir(parents=True, exist_ok=True)
        previo = informe / "informe_tecnico.md"
        previo.write_text("corrida previa\n", encoding="utf-8")
        import hashlib
        antes = hashlib.sha256(previo.read_bytes()).hexdigest()
        borrador.abrir(self.raiz)
        self.assertEqual(hashlib.sha256(previo.read_bytes()).hexdigest(), antes)


class TestCorregirFirmar(Base):
    def test_fr007_correccion_contradiccion_rechazada(self):
        fx.construir(self.raiz)
        borrador.abrir(self.raiz, fecha=fx.FECHA)
        resumen = next(s for s in self.leer()["secciones"] if s["nombre"] == "resumen")
        mala = resumen["contenido"].replace(f"{fx.N_RIESGOS} riesgos", "1 riesgos")
        with self.assertRaises(borrador.BorradorError) as cm:
            borrador.corregir(self.raiz, "resumen", mala, "cambiar el número", "Auditor", fx.FECHA)
        self.assertIn("contradice", str(cm.exception))

    def test_correccion_valida_queda_en_historial(self):
        fx.construir(self.raiz)
        borrador.abrir(self.raiz, fecha=fx.FECHA)
        resumen = next(s for s in self.leer()["secciones"] if s["nombre"] == "resumen")
        nueva = resumen["contenido"] + " (versión corregida por el auditor)."
        s = borrador.corregir(self.raiz, "resumen", nueva, "aclarar", "Auditor", fx.FECHA)
        self.assertIn("versión corregida", s["contenido"])
        self.assertEqual(s["correcciones"][-1]["autor"], "Auditor")

    def test_fr008_firma_y_entrega(self):
        fx.construir(self.raiz)
        borrador.abrir(self.raiz, fecha=fx.FECHA)
        borrador.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        f = borrador.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        self.assertEqual(f["secciones_al_firmar"], 6)
        d = borrador.entregar(self.raiz)
        self.assertTrue(d["firmado"])
        self.assertEqual(len(d["secciones"]), 6)

    def test_fr009_anexo_roto_detectado(self):
        fx.construir(self.raiz)
        borrador.abrir(self.raiz, fecha=fx.FECHA)
        ruta = self.raiz / "03_hallazgos/citas_s04.json"
        datos = bytearray(ruta.read_bytes())
        datos[10] ^= 0x01
        ruta.write_bytes(bytes(datos))
        v = borrador.verificar(self.raiz)
        self.assertIn("03_hallazgos/citas_s04.json", v["anexo_rotos"])


class TestCliBorrador(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["borrador", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, frases_json=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
