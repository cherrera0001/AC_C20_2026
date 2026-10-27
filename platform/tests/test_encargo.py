"""S07 — El encargo: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import encargo_fixtures as fx
import lista_fixtures as lfx
from c4a import cli
from c4a import encargo
from c4a import lista

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / encargo.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_cubre_dominios_y_sprints(self):
        fx.construir(self.raiz)
        c = encargo.abrir(self.raiz)
        sprints = {p["sprint"] for p in c["pasos"]}
        self.assertEqual(sprints, {"S01", "S02", "S03", "S04", "S05", "S06"})
        for p in c["pasos"]:
            self.assertTrue(p["huella_origen"])
        plan = self.raiz / "01_plan"
        self.assertTrue((plan / "encargo_s07.json").is_file())
        self.assertFalse((plan / "encargo_s07.firma.json").exists())

    def test_esc2_fr001_falta_producto_codigo_2(self):
        fx.construir(self.raiz, completo=False)  # falta la lista de S06
        with self.assertRaises(encargo.EncargoError) as cm:
            encargo.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_fr004_vacios_como_condiciones(self):
        fx.construir(self.raiz)
        c = encargo.abrir(self.raiz)
        condicionados = [p for p in c["pasos"] if p["repetibilidad"] == "condicionada"]
        self.assertGreaterEqual(len(condicionados), 1)
        for p in condicionados:
            self.assertTrue(p["condicion"])

    def test_fr005_sin_comandos_ni_red(self):
        fx.construir(self.raiz)
        encargo.abrir(self.raiz)
        for nombre in (encargo.ARCHIVO_JSON, encargo.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotRegex(t, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
            self.assertNotIn("password", t.lower())

    def test_fr007_autoria_sin_firma(self):
        fx.construir(self.raiz)
        c = encargo.abrir(self.raiz, fecha=fx.FECHA)
        integridad = json.loads((self.raiz / encargo.ARCHIVO_INTEGRIDAD).read_text(encoding="utf-8"))
        self.assertTrue(integridad["sha256"])
        self.assertIn("autor", integridad)

    def test_sc003_alteracion_detectada(self):
        fx.construir(self.raiz)
        encargo.abrir(self.raiz)
        ruta = self.raiz / encargo.ARCHIVO_JSON
        datos = bytearray(ruta.read_bytes())
        datos[10] ^= 0x01
        ruta.write_bytes(bytes(datos))
        v = encargo.verificar(self.raiz)
        self.assertFalse(v["integro"])

    def test_fr013_cadena_cambiada_señalada(self):
        fx.construir(self.raiz)
        encargo.abrir(self.raiz, fecha=fx.FECHA)
        p = self.leer()["pasos"][0]
        encargo.corregir(self.raiz, p["id"], "descripcion", "descripción corregida", "ajuste",
                         "Auditor", fx.FECHA)
        c2 = self.leer()
        p2 = next(x for x in c2["pasos"] if x["id"] == p["id"])
        self.assertEqual(p2["descripcion"], "descripción corregida")
        # la firma de la corrección es la integridad: autor distinto, sin archivo de firma
        integridad = json.loads((self.raiz / encargo.ARCHIVO_INTEGRIDAD).read_text(encoding="utf-8"))
        self.assertEqual(integridad["autor"], "Auditor")

    def test_exclusion_y_entrega(self):
        fx.construir(self.raiz)
        encargo.abrir(self.raiz, fecha=fx.FECHA)
        p = self.leer()["pasos"][0]
        encargo.excluir(self.raiz, p["id"], "hoy no se repite", "Auditor", fx.FECHA)
        d = encargo.entregar(self.raiz)
        excluido = next(x for x in d["pasos"] if x["id"] == p["id"])
        self.assertEqual(excluido["repetibilidad"], "no repetible")
        self.assertEqual(d["contados"]["no_repetibles"], 1)


class TestCliEncargo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["encargo", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, completo=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        c = json.loads((self.raiz / encargo.ARCHIVO_JSON).read_text(encoding="utf-8"))
        p = c["pasos"][0]["id"]
        self.assertEqual(self.main("corregir", "--paso", p, "--campo", "descripcion",
                                   "--valor", "texto", "--motivo", "m", "--autor", "A"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
