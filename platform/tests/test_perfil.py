"""S05 — El perfil: US1 a US4 y contrato de códigos. Insumos SINTÉTICOS (principio III)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import perfil_fixtures as fx
from c4a import cli
from c4a import perfil

ESTADOS_CUMPLIMIENTO = re.compile(r"\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b", re.IGNORECASE)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / perfil.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestAbrir(Base):
    def test_sc001_seis_secciones_y_vacios(self):
        fx.construir(self.raiz)
        c = perfil.abrir(self.raiz)
        self.assertEqual([s["funcion"] for s in c["secciones"]], list(perfil.FUNCIONES))
        citas_en_secciones = sum(len(s["riesgos"]) for s in c["secciones"])
        self.assertEqual(citas_en_secciones + len(c["sin_asignar"]), fx.N_RIESGOS)
        self.assertEqual(len(c["vacios_comunes"]) + sum(len(s["vacios"]) for s in c["secciones"]),
                         fx.N_VACIOS)

    def test_esc2_fr001_sin_cita_codigo_2(self):
        import cita_fixtures as cfx
        cfx.construir(self.raiz, enunciado_json=False)
        with self.assertRaises(perfil.PerfilError) as cm:
            perfil.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 2)

    def test_fr006_funcion_sin_material_no_consta(self):
        fx.construir(self.raiz)
        c = perfil.abrir(self.raiz)
        for s in c["secciones"]:
            if not s["riesgos"] and not s["vacios"]:
                self.assertEqual(s["sintesis"], "")
                vista = perfil.vista(self.raiz)
                self.assertIn("no consta", vista)
                break
        else:
            self.fail("se esperaba al menos una función sin material")

    def test_sc003_busqueda_limpia(self):
        fx.construir(self.raiz)
        perfil.abrir(self.raiz)
        for nombre in (perfil.ARCHIVO_JSON, perfil.ARCHIVO_MD):
            t = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(ESTADOS_CUMPLIMIENTO.search(t))
            self.assertNotIn("sin hallazgos", t.lower())

    def test_sc007_determinismo(self):
        fx.construir(self.raiz)
        perfil.abrir(self.raiz)
        a = (self.raiz / perfil.ARCHIVO_JSON).read_bytes()
        perfil.abrir(self.raiz)
        self.assertEqual(a, (self.raiz / perfil.ARCHIVO_JSON).read_bytes())

    def test_fr012_fichas(self):
        fx.construir(self.raiz)
        c = perfil.abrir(self.raiz)
        for s in c["secciones"]:
            ficha = self.raiz / f"03_hallazgos/perfil-{perfil._slug(s['funcion'])}.md"
            self.assertTrue(ficha.is_file())
            self.assertIn(s["funcion"], ficha.read_text(encoding="utf-8"))


class TestCorregirFirmar(Base):
    def test_esc1_reasignacion_con_historial(self):
        fx.construir(self.raiz)
        c = perfil.abrir(self.raiz, fecha=fx.FECHA)
        x = next(x for s in c["secciones"] for x in s["riesgos"])
        perfil.reasignar(self.raiz, x["cita"], "Detectar", "me encaja mejor allí", "Auditor", fx.FECHA)
        c2 = self.leer()
        destino = next(s for s in c2["secciones"] if s["funcion"] == "Detectar")
        self.assertIn(x["cita"], [y["cita"] for y in destino["riesgos"]])
        tipos = [h["tipo"] for h in c2["historial"]]
        self.assertIn("reasignacion", tipos)

    def test_no_asignado_declarado(self):
        fx.construir(self.raiz)
        c = perfil.abrir(self.raiz, fecha=fx.FECHA)
        x = next(x for s in c["secciones"] for x in s["riesgos"])
        perfil.reasignar(self.raiz, x["cita"], None, "no aplica a ninguna función", "Auditor", fx.FECHA)
        c2 = self.leer()
        self.assertIn(x["cita"], [y["id"] for y in c2["sin_asignar"]])

    def test_firmar_exige_seis_sintesis(self):
        fx.construir(self.raiz)
        perfil.abrir(self.raiz, fecha=fx.FECHA)
        for f in perfil.FUNCIONES:
            perfil.corregir(self.raiz, f, "sintesis", f"Lectura del auditor para {f}", "completar",
                            "Auditor", fx.FECHA)
        perfil.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        f = perfil.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        self.assertEqual(f["secciones_al_firmar"], 6)
        self.assertEqual(perfil.estado_efectivo(self.raiz), "firmado")

    def test_firmar_con_sintesis_vacia_se_rechaza(self):
        fx.construir(self.raiz)
        perfil.abrir(self.raiz, fecha=fx.FECHA)
        # solo algunas síntesis: las vacías siguen vacías en funciones sin material
        perfil.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        with self.assertRaises(perfil.PerfilError) as cm:
            perfil.firmar(self.raiz, "Auditor", "firma")
        self.assertEqual(cm.exception.codigo, 1)


class TestCliPerfil(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def main(self, *argv):
        return cli.main(["perfil", *argv, "--raiz", str(self.raiz)])

    def test_codigos(self):
        fx.construir(self.raiz)
        self.assertEqual(self.main("abrir"), 0)
        self.assertEqual(self.main("corregir", "--funcion", "Proteger", "--campo", "sintesis",
                                   "--valor", "texto", "--motivo", "m", "--autor", "A"), 0)
        self.assertEqual(self.main("entregar"), 0)


if __name__ == "__main__":
    unittest.main()
