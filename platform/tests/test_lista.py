"""S06 — La lista: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import lista_fixtures as fx
from c4a import cli
from c4a import lista

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / lista.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_cada_propuesta_cita_ancla(self):
        fx.construir(self.raiz)
        c = lista.abrir(self.raiz)
        self.assertGreaterEqual(len(c["filas"]), 1)
        for f in c["filas"]:
            self.assertGreaterEqual(len(f["anclajes"]), 1)
            self.assertTrue(f["justificacion"])
            self.assertEqual(f["marco"], "CIS Controls")
            self.assertEqual(f["version"], "v8.1")

    def test_esc2_fr001_sin_perfil_codigo_2(self):
        fx.construir(self.raiz, perfil_json=False)
        with self.assertRaises(lista.ListaError) as cm:
            lista.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_fr005_documentales_quedan_pendiente(self):
        fx.construir(self.raiz)
        c = lista.abrir(self.raiz)
        catalogo = lista._catalogo()
        for f in c["filas"]:
            esperado = (lista.CONF_DOCUMENTAL if catalogo.get(f["identificador"], {}).get("documental")
                        else lista.CONF_CONFIRMADO)
            self.assertEqual(f["estado_confirmacion"], esperado)

    def test_sc007_determinismo(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz)
        a = (self.raiz / lista.ARCHIVO_JSON).read_bytes()
        lista.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / lista.ARCHIVO_JSON).read_bytes())

    def test_sc003_busqueda_limpia(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz)
        for nombre in (lista.ARCHIVO_JSON, lista.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotRegex(t, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

    def test_fr012_fichas(self):
        fx.construir(self.raiz)
        c = lista.abrir(self.raiz)
        for f in c["filas"]:
            ficha = self.raiz / f"03_hallazgos/lista-{f['id']}.md"
            self.assertTrue(ficha.is_file())


class TestAcciones(Base):
    def test_alta_manual_pendiente_con_fuente(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz, fecha=fx.FECHA)
        f = lista.anadir(self.raiz, "Control de ejemplo", "X.1", "justificación de prueba",
                         "fuente declarada del auditor", "alta de prueba", "Auditor", fx.FECHA)
        self.assertEqual(f["estado_confirmacion"], lista.CONF_PENDIENTE)
        self.assertEqual(f["fuente"], "fuente declarada del auditor")
        with self.assertRaises(lista.ListaError):
            lista.anadir(self.raiz, "Control de ejemplo", "X.1", "otra vez", "fuente", "m", "Auditor")

    def test_alta_manual_exige_fuente(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz, fecha=fx.FECHA)
        with self.assertRaises(lista.ListaError):
            lista.anadir(self.raiz, "Control de ejemplo", "X.1", "justificación", "", "m", "Auditor")

    def test_descarte_y_recuperacion(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz, fecha=fx.FECHA)
        f = self.leer()["filas"][0]
        d = lista.descartar(self.raiz, f["id"], "no aplica a este activo", "Auditor", fx.FECHA)
        self.assertEqual(d["estado_aplicabilidad"], "descartado")
        d2 = lista.recuperar(self.raiz, f["id"], "se reevaluó", "Auditor", fx.FECHA)
        self.assertEqual(d2["estado_aplicabilidad"], "seleccionado")

    def test_firma_y_entrega_seleccionados(self):
        fx.construir(self.raiz)
        lista.abrir(self.raiz, fecha=fx.FECHA)
        lista.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        firma = lista.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        self.assertGreaterEqual(firma["seleccionados_al_firmar"], 1)
        d = lista.entregar(self.raiz)
        self.assertEqual(d["contados"]["seleccionados"], len(d["controles"]))
        for f in d["controles"]:
            self.assertNotEqual(f["estado_aplicabilidad"], "descartado")


class TestCliLista(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["lista", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz, perfil_json=False)
        self.assertEqual(self.main("abrir"), 2)
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        self.assertEqual(self.main("anadir", "--control", "C", "--identificador", "X.1",
                                   "--justificacion", "j", "--fuente", "f", "--motivo", "m",
                                   "--autor", "A"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
