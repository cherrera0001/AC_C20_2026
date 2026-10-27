"""S03 US2 — La herramienta propone y el auditor corrige. Insumos SINTÉTICOS (principio III)."""
import json
import tempfile
import unittest
from pathlib import Path

import enunciado_fixtures as fx
from c4a import enunciado


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        enunciado.abrir(self.raiz, fecha=fx.FECHA)
        self.c = json.loads((self.raiz / enunciado.ARCHIVO_JSON).read_text(encoding="utf-8"))

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / enunciado.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestCorregir(Base):
    def test_esc1_correccion_queda_en_historial_y_revisado(self):
        e = self.c["enunciados"][0]
        nuevo = enunciado.corregir(self.raiz, e["id"], "impacto", "Afecta la disponibilidad del servicio",
                                   "criterio del auditor", "Auditor", fx.FECHA)
        self.assertEqual(nuevo["impacto"], "Afecta la disponibilidad del servicio")
        self.assertEqual(nuevo["estado_aprobacion"], "revisado")
        self.assertEqual(nuevo["correcciones"][-1]["autor"], "Auditor")
        self.assertEqual(nuevo["correcciones"][-1]["campo"], "impacto")
        self.assertEqual(nuevo["correcciones"][-1]["anterior"], "")
        self.assertEqual(nuevo["correcciones"][-1]["motivo"], "criterio del auditor")
        c = self.leer()
        self.assertEqual(c["estado_aprobacion"], "revisado")

    def test_esc2_sin_motivo_o_con_cumplimiento_se_rechaza_sin_escribir(self):
        e = self.c["enunciados"][0]
        antes = (self.raiz / enunciado.ARCHIVO_JSON).read_bytes()
        for motivo in ("", "El control cumple"):
            with self.subTest(motivo=motivo):
                with self.assertRaises(enunciado.EnunciadoError) as cm:
                    enunciado.corregir(self.raiz, e["id"], "criterio", "x", motivo, "Auditor")
                self.assertEqual(cm.exception.codigo, 1)
        with self.assertRaises(enunciado.EnunciadoError):
            enunciado.corregir(self.raiz, e["id"], "campanas", "x", "motivo", "Auditor")
        self.assertEqual((self.raiz / enunciado.ARCHIVO_JSON).read_bytes(), antes)

    def test_el_id_no_cambia_al_corregir(self):
        e = self.c["enunciados"][0]
        enunciado.corregir(self.raiz, e["id"], "condicion", "Redacción distinta del auditor",
                           "precisar", "Auditor", fx.FECHA)
        c = self.leer()
        ids = [x["id"] for x in c["enunciados"]]
        self.assertIn(e["id"], ids)
        corr = next(x for x in c["enunciados"] if x["id"] == e["id"])
        self.assertEqual(corr["condicion"], "Redacción distinta del auditor")

    def test_descartar_y_restablecer_con_motivo(self):
        e = self.c["enunciados"][0]
        d = enunciado.descartar(self.raiz, e["id"], "fuera del interés del encargo", "Auditor", fx.FECHA)
        self.assertIn("descartado", d["marcas"])
        with self.assertRaises(enunciado.EnunciadoError):
            enunciado.descartar(self.raiz, e["id"], "otra vez", "Auditor")
        r = enunciado.restablecer(self.raiz, e["id"], "se reevaluó", "Auditor", fx.FECHA)
        self.assertNotIn("descartado", r["marcas"])
        c = self.leer()
        tipos = [h["tipo"] for h in c["historial"]]
        self.assertIn("descarte", tipos)
        self.assertIn("restablecimiento", tipos)


class TestFirmar(Base):
    def _completar(self):
        for e in self.leer()["enunciados"]:
            enunciado.corregir(self.raiz, e["id"], "criterio", "Criterio completo del auditor",
                               "completar", "Auditor", fx.FECHA)
            enunciado.corregir(self.raiz, e["id"], "impacto", "Impacto completo del auditor",
                               "completar", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión completa", fx.FECHA)

    def test_firmar_desde_borrador_se_rechaza(self):
        with self.assertRaises(enunciado.EnunciadoError) as cm:
            enunciado.firmar(self.raiz, "Auditor", "justificación")
        self.assertEqual(cm.exception.codigo, 1)

    def test_firmar_con_impacto_vacio_se_rechaza_informando(self):
        e = self.c["enunciados"][0]
        enunciado.corregir(self.raiz, e["id"], "criterio", "Criterio", "completar", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        with self.assertRaises(enunciado.EnunciadoError) as cm:
            enunciado.firmar(self.raiz, "Auditor", "justificación")
        self.assertEqual(cm.exception.codigo, 1)
        self.assertIn(e["id"], str(cm.exception))

    def test_firma_valida_y_anulacion_por_escritura(self):
        self._completar()
        f = enunciado.firmar(self.raiz, "Auditor Principal", "firma de prueba sintética", fx.FECHA)
        self.assertEqual(f["enunciados_al_firmar"], fx.N_HECHOS)
        self.assertEqual(enunciado.estado_efectivo(self.raiz), "firmado")
        e = self.leer()["enunciados"][0]
        enunciado.corregir(self.raiz, e["id"], "impacto", "Impacto corregido después",
                           "ajuste posterior", "Auditor", fx.FECHA)
        self.assertEqual(enunciado.estado_efectivo(self.raiz), "revisado")
        tipos = [h["tipo"] for h in self.leer()["historial"]]
        self.assertIn("firma_anulada", tipos)


if __name__ == "__main__":
    unittest.main()
