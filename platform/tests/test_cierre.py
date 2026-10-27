"""S10 — El cierre: US1 a US4 y contrato de códigos (2 y 5). Insumos SINTÉTICOS."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import cierre_fixtures as fx
from c4a import cierre
from c4a import cli

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / cierre.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_secciones_y_tabla(self):
        fx.construir(self.raiz)
        c = cierre.abrir(self.raiz)
        self.assertEqual(len(c["secciones"]), 6)
        self.assertGreaterEqual(len(c["tabla"]), 8)  # fichas + entregas del anexo
        self.assertEqual(c["conteos"]["pendientes"], 0)
        self.assertTrue((self.raiz / cierre.ARCHIVO_MD).is_file())
        md = (self.raiz / cierre.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn("Tabla de recorrido", md)
        self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(md))

    def test_esc2_fr001_sin_borrador_codigo_2(self):
        fx.construir(self.raiz, borrador_json=False)
        with self.assertRaises(cierre.CierreError) as cm:
            cierre.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_esc_fr001_borrador_sin_firmar_codigo_5(self):
        fx.construir(self.raiz, firmado=False)
        with self.assertRaises(cierre.CierreError) as cm:
            cierre.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 5)

    def test_fr005_enlace_roto_marcado(self):
        fx.construir(self.raiz)
        cierre.abrir(self.raiz)
        ruta = self.raiz / "03_hallazgos/citas_s04.json"
        datos = bytearray(ruta.read_bytes())
        datos[10] ^= 0x01
        ruta.write_bytes(bytes(datos))
        v = cierre.verificar(self.raiz)  # el anexo del borrador firma la huella buena
        self.assertIn("03_hallazgos/citas_s04.json", v["anexo_rotos"])


class TestRecorrido(Base):
    def test_fr007_correccion_contradiccion(self):
        fx.construir(self.raiz)
        cierre.abrir(self.raiz, fecha=fx.FECHA)
        e = self.leer()["tabla"][0]
        with self.assertRaises(cierre.CierreError) as cm:
            cierre.corregir(self.raiz, e["id"], "Afirmación que ya no cita nada", "m", "Auditor",
                            fx.FECHA)
        self.assertIn("contradice", str(cm.exception))

    def test_resolucion_y_firma(self):
        fx.construir(self.raiz)
        cierre.abrir(self.raiz, fecha=fx.FECHA)
        # romper un enlace de verdad: borrar una ficha citada por la tabla
        primera = self.leer()["tabla"][0]
        (self.raiz / primera["ficha"]).unlink()
        cierre.abrir(self.raiz)
        rota = next(e for e in self.leer()["tabla"] if e["estado"] == "no-verifica")
        cierre.resolver(self.raiz, rota["id"], "se verificó el original a mano", "Auditor", fx.FECHA)
        c = self.leer()
        self.assertEqual(next(e for e in c["tabla"] if e["id"] == rota["id"])["estado"], "declarado")
        cierre.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        f = cierre.firmar(self.raiz, "Auditor Principal", "cierre sintético", fx.FECHA)
        self.assertEqual(cierre.estado_efectivo(self.raiz), "firmado")

    def test_firmar_con_enlaces_abiertos_se_rechaza(self):
        fx.construir(self.raiz)
        cierre.abrir(self.raiz, fecha=fx.FECHA)
        primera = self.leer()["tabla"][0]
        (self.raiz / primera["ficha"]).unlink()
        cierre.abrir(self.raiz)
        cierre.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        with self.assertRaises(cierre.CierreError) as cm:
            cierre.firmar(self.raiz, "Auditor", "firma")
        self.assertEqual(cm.exception.codigo, 1)

    def test_fr013_registro_del_tercero(self):
        fx.construir(self.raiz)
        cierre.abrir(self.raiz, fecha=fx.FECHA)
        cierre.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        reg = cierre.registrar(self.raiz, "Revisor Ajeno", "recorrí todas las entradas y verifican",
                               fecha=fx.FECHA)
        self.assertEqual(reg["tercero"], "Revisor Ajeno")
        c = self.leer()
        self.assertIsNotNone(c["registro_tercero"])
        self.assertEqual(c["registro_tercero"]["conteos"]["entradas"], c["conteos"]["entradas"])


class TestCliCierre(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["cierre", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, borrador_json=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz, firmado=False)
        self.assertEqual(self.main("abrir"), 5)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)


if __name__ == "__main__":
    unittest.main()
