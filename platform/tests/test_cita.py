"""S04 — La cita: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import cita_fixtures as fx
import enunciado_fixtures as efx
from c4a import cita
from c4a import cli
from c4a import enunciado
from c4a import registro

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / cita.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_citas_y_vacios(self):
        fx.construir(self.raiz)
        c = cita.abrir(self.raiz)
        self.assertEqual(len(c["citas"]), fx.N_RIESGOS)
        self.assertEqual(len(c["vacios"]), fx.N_VACIOS)
        for x in c["citas"]:
            self.assertRegex(x["id"], r"^C-[0-9a-f]{10}$")
            self.assertEqual(x["estado_aprobacion"], "borrador")
            self.assertTrue(x["marco"] and x["version"])

    def test_esc2_fr001_sin_enunciado_codigo_2(self):
        fx.construir(self.raiz, enunciado_json=False)
        with self.assertRaises(cita.CitaError) as cm:
            cita.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_esc3_fr002_origen_firmado(self):
        fx.construir(self.raiz, firmado=True)
        c = cita.abrir(self.raiz)
        self.assertTrue(c["origen"]["firmado"])

    def test_fr005_identificador_coherente_con_el_catalogo(self):
        fx.construir(self.raiz)
        c = cita.abrir(self.raiz)
        catalogo = cita._catalogo()
        for x in c["citas"]:
            self.assertTrue(x["fundamento"])
            if x["estado_identificador"] == cita.CONFIRMADO:
                self.assertIn(x["identificador"], catalogo)
            else:
                self.assertEqual(x["estado_identificador"], cita.PENDIENTE)
                self.assertEqual(x["identificador"], cita.PENDIENTE)

    def test_fr007_correccion_identificador_confirmado_y_pendiente(self):
        fx.construir(self.raiz)
        c = cita.abrir(self.raiz)
        x = c["citas"][0]
        n = cita.corregir(self.raiz, x["id"], "identificador", "A.8.2", "consta en la base",
                          "Auditor", fx.FECHA)
        self.assertEqual(n["estado_identificador"], cita.CONFIRMADO)
        n2 = cita.corregir(self.raiz, x["id"], "identificador", "X.9.9", "aporte del auditor",
                           "Auditor", fx.FECHA)
        self.assertEqual(n2["estado_identificador"], cita.PENDIENTE)
        self.assertEqual(n2["correcciones"][-1]["anterior"], "A.8.2")

    def test_correspondencia_adicional(self):
        fx.construir(self.raiz)
        c = cita.abrir(self.raiz)
        x = c["citas"][0]
        n = cita.anadir_correspondencia(self.raiz, x["id"], "NIST CSF", "2.0", "PR.DS",
                                        "función Proteger, categoría de datos", "relacionar", "Auditor",
                                        fx.FECHA)
        self.assertEqual(len(n["correspondencias"]), 1)
        self.assertEqual(n["correspondencias"][0]["marco"], "NIST CSF")

    def test_sc007_determinismo(self):
        fx.construir(self.raiz)
        cita.abrir(self.raiz)
        a = (self.raiz / cita.ARCHIVO_JSON).read_bytes()
        cita.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / cita.ARCHIVO_JSON).read_bytes())

    def test_sc003_busqueda_limpia(self):
        fx.construir(self.raiz)
        cita.abrir(self.raiz)
        for nombre in (cita.ARCHIVO_JSON, cita.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotRegex(t, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

    def test_fr012_fichas(self):
        fx.construir(self.raiz)
        c = cita.abrir(self.raiz)
        for x in c["citas"]:
            ficha = self.raiz / f"03_hallazgos/cita-{x['id']}.md"
            self.assertTrue(ficha.is_file())
            self.assertIn("sugerencia", ficha.read_text(encoding="utf-8"))


class TestFirmarYVerificar(Base):
    def _revisar_todo(self):
        cita.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)

    def test_firmar_desde_borrador_y_flujo(self):
        fx.construir(self.raiz)
        cita.abrir(self.raiz, fecha=fx.FECHA)
        with self.assertRaises(cita.CitaError) as cm:
            cita.firmar(self.raiz, "Auditor", "sin revisar")
        self.assertEqual(cm.exception.codigo, 1)
        self._revisar_todo()
        f = cita.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        self.assertEqual(f["citas_al_firmar"], fx.N_RIESGOS)
        self.assertEqual(cita.estado_efectivo(self.raiz), "firmado")
        x = self.leer()["citas"][0]
        cita.corregir(self.raiz, x["id"], "fundamento", "fundamento corregido", "ajuste", "Auditor", fx.FECHA)
        self.assertEqual(cita.estado_efectivo(self.raiz), "revisado")

    def test_sc005_evidencia_alterada_fuera_de_entrega(self):
        fx.construir(self.raiz)
        cita.abrir(self.raiz, fecha=fx.FECHA)
        c = self.leer()
        x = c["citas"][0]
        copia = self.raiz / x["evidencias"][0]["copia"]
        datos = bytearray(copia.read_bytes())
        datos[0] ^= 0x01
        copia.write_bytes(bytes(datos))
        v = cita.verificar(self.raiz)
        self.assertIn(x["id"], v["evidencias_alteradas"])
        d = cita.entregar(self.raiz)
        self.assertNotIn(x["id"], [y["id"] for y in d["citas"]])

    def test_sc013_firmado_y_origen_cambiado_codigo_4(self):
        fx.construir(self.raiz)
        cita.abrir(self.raiz, fecha=fx.FECHA)
        self._revisar_todo()
        cita.firmar(self.raiz, "Auditor", "firma", fx.FECHA)
        import registro_fixtures as rfx
        dom = rfx.fila(self.raiz, "control:2")
        doc = rfx.evidencia(self.raiz, "doc_tardio.txt", "hecho tardío")
        registro.aportar(self.raiz, fx.ACTIVO, dom, "Hecho tardío", "positivo", doc,
                         "documental", fx.FECHA[:10], "Auditor", origen="del ejercicio", fecha=fx.FECHA)
        with self.assertRaises(cita.CitaError) as cm:
            cita.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 4)


class TestCliCita(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["cita", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, enunciado_json=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        c = json.loads((self.raiz / cita.ARCHIVO_JSON).read_text(encoding="utf-8"))
        x = c["citas"][0]["id"]
        self.assertEqual(self.main("corregir", "--cita", x, "--campo", "identificador",
                                   "--valor", "A.8.2", "--motivo", "m", "--autor", "A"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
