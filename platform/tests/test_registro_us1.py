"""S02 US1 — Abrir el registro sin alcance firmado. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import registro_fixtures as fx
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
        return json.loads((self.raiz / registro.ARCHIVO_JSON).read_text(encoding="utf-8"))

    def vista(self):
        return (self.raiz / registro.ARCHIVO_MD).read_text(encoding="utf-8")


class TestAbrir(Base):
    def test_sc001_n_mas_uno_no_consta_y_cero_hechos(self):
        fx.construir(self.raiz)
        c = registro.abrir(self.raiz)
        nc = [e for e in c["entradas"] if e["clase"] == registro.NO_CONSTA]
        self.assertEqual(len(nc), fx.N_DOMINIOS_FIXTURE + 1)
        self.assertEqual([e for e in c["entradas"] if e["clase"] == registro.HECHO], [])
        for e in nc:
            self.assertEqual(e["afirmacion"], registro.NO_CONSTA)
            self.assertEqual(e["resultado"], "no-ejecutado")
            self.assertEqual(e["estado_aprobacion"], "borrador")
            self.assertRegex(e["id"], r"^N-[0-9a-f]{10}$")
        activo = [e for e in nc if e["dominio"]["fila"] is None]
        self.assertEqual(len(activo), 1)
        self.assertEqual(activo[0]["activo"], fx.ACTIVO)

    def test_esc1_fr002_declara_alcance_no_firmado_y_su_huella(self):
        fx.construir(self.raiz)
        c = registro.abrir(self.raiz)
        self.assertFalse(c["alcance"]["firmado"])
        self.assertEqual(c["alcance"]["sha256"], sha256_file(self.raiz / "scope/alcance_s01.json"))
        self.assertIn("alcance no firmado", self.vista())

    def test_esc2_fr001_sin_alcance_s01_usa_minimo_de_referencia(self):
        fx.construir(self.raiz, alcance_json=False)
        antes = fx.huellas(self.raiz / "scope")
        c = registro.abrir(self.raiz)
        self.assertTrue(c["alcance"]["minimo_de_referencia"])
        self.assertTrue(any("Falta el producto anterior" in a for a in c["avisos"]))
        self.assertTrue(all(e["clase"] == registro.NO_CONSTA for e in c["entradas"]))
        self.assertEqual(len(c["entradas"]), fx.N_DOMINIOS_FIXTURE + 1)
        self.assertEqual(fx.huellas(self.raiz / "scope"), antes)
        doc = fx.evidencia(self.raiz)
        with self.assertRaises(registro.RegistroError) as cm:
            registro.aportar(self.raiz, fx.ACTIVO, "activo", "x", "positivo", doc, "documental", fx.DIA,
                             "Auditor", origen="del ejercicio")
        self.assertEqual(cm.exception.codigo, 2)

    def test_esc3_alcance_firmado_cita_su_huella(self):
        fx.construir(self.raiz)
        from c4a import alcance
        alcance.revisar(self.raiz, "Auditor Sintético", "revisión sintética", fx.FECHA)
        alcance.firmar(self.raiz, "Auditor Sintético", "firma sintética", fx.FECHA)
        c = registro.abrir(self.raiz)
        self.assertTrue(c["alcance"]["firmado"])
        self.assertEqual(c["alcance"]["sha256"], sha256_file(self.raiz / "scope/alcance_s01.json"))

    def test_esc4_fr003_dominio_fuera_no_genera_entradas(self):
        fx.construir(self.raiz)
        fuera = fx.fila(self.raiz, "tecnico:2")
        fx.decidir(self.raiz, fuera, "excluido")
        c = registro.abrir(self.raiz)
        self.assertFalse(any(e["dominio"]["fila"] == fuera for e in c["entradas"]))
        self.assertEqual(len(c["entradas"]), fx.N_DOMINIOS_FIXTURE)

    def test_sc012_solo_crea_archivos_del_registro(self):
        fx.construir(self.raiz)
        inventario = self.raiz / "02_evidencia" / "inventario.json"
        inventario.parent.mkdir(parents=True, exist_ok=True)
        inventario.write_text('{"fixture": "sintético"}\n', encoding="utf-8")
        antes_scope = fx.huellas(self.raiz / "scope")
        antes_inv = sha256_file(inventario)
        registro.abrir(self.raiz)
        self.assertEqual(fx.huellas(self.raiz / "scope"), antes_scope)
        self.assertEqual(sha256_file(inventario), antes_inv)
        self.assertEqual(sorted(p.name for p in inventario.parent.iterdir()),
                         ["inventario.json", "registro_s02.json", "registro_s02.md"])

    def test_sc008_una_sola_seccion_no_consta_con_su_conteo(self):
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        md = self.vista()
        secciones = re.findall(r"^## No consta \((\d+)\)$", md, re.MULTILINE)
        self.assertEqual(len(secciones), 1)
        n = sum(1 for e in self.leer()["entradas"] if e["clase"] == registro.NO_CONSTA)
        self.assertEqual(int(secciones[0]), n)

    def test_fr011_sin_estados_de_cumplimiento(self):
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        for texto in ((self.raiz / registro.ARCHIVO_JSON).read_text(encoding="utf-8"), self.vista()):
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(texto))
            self.assertNotIn("sin hallazgos", texto.lower())

    def test_sc007_dos_aperturas_dan_bytes_identicos(self):
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        a = (self.raiz / registro.ARCHIVO_JSON).read_bytes()
        registro.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / registro.ARCHIVO_JSON).read_bytes())


class TestSinContenidoProhibido(Base):
    """SC-005 (T033): evidencias sintéticas con direcciones de documentación, una línea con forma
    de comando y otra con forma de credencial no dejan rastro en el registro."""

    def test_sc005_cero_red_comandos_puertos_credenciales(self):
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        texto = "host 198.51.100.7 puerto 8443\n$ comando --objetivo 203.0.113.9\nclave=Sintetica123\n"
        doc = fx.evidencia(self.raiz, "con_crudo.txt", texto)
        registro.aportar(self.raiz, fx.ACTIVO, "activo", "Documento sobre 203.0.113.9 del ejercicio",
                         "positivo", doc, "documental", fx.DIA, "Auditor", origen="del ejercicio", fecha=fx.FECHA)
        for ruta in (registro.ARCHIVO_JSON, registro.ARCHIVO_MD):
            t = (self.raiz / ruta).read_text(encoding="utf-8")
            self.assertNotRegex(t, r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
            self.assertNotIn("8443", t)
            self.assertNotIn("comando --objetivo", t)
            self.assertNotIn("Sintetica123", t)
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))


class TestTextosLibres(Base):
    """T043: los textos que escribe el auditor no admiten estados de cumplimiento, puertos,
    comandos ni credenciales (FR-011, FR-012)."""

    def test_textos_prohibidos_se_rechazan_sin_escribir(self):
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        dom = fx.fila(self.raiz, "control:1")
        doc = fx.evidencia(self.raiz)
        antes = (self.raiz / registro.ARCHIVO_JSON).read_bytes()
        malos = ["El control cumple", "Servicio en el puerto 8443", "Expuesto en :8443",
                 "$ comando sintetico", "se ejecutó con --objetivo", "password=Sintetica123"]
        for texto in malos:
            with self.subTest(texto=texto):
                with self.assertRaises(registro.RegistroError) as cm:
                    registro.aportar(self.raiz, fx.ACTIVO, dom, texto, "positivo", doc, "documental", fx.DIA,
                                     "Auditor", origen="del ejercicio", fecha=fx.FECHA)
                self.assertEqual(cm.exception.codigo, 1)
                with self.assertRaises(registro.RegistroError):
                    registro.revisar(self.raiz, "Auditor", texto, fx.FECHA)
        self.assertEqual((self.raiz / registro.ARCHIVO_JSON).read_bytes(), antes)
        r = registro.aportar(self.raiz, fx.ACTIVO, dom, "La política de parches existe", "positivo", doc,
                             "documental", fx.DIA, "Auditor", origen="del ejercicio", fecha=fx.FECHA)
        self.assertTrue(r["aceptada"])
        with self.assertRaises(registro.RegistroError):
            registro.corregir(self.raiz, r["entrada"], "afirmacion", "Cumplimiento parcial", "m", "Auditor")


if __name__ == "__main__":
    unittest.main()
