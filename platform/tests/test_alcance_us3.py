"""S01 · US3 — Un dato no consta y la fila se conserva; compuerta en solo lectura (SINTÉTICO)."""
import itertools
import tempfile
import unittest
from datetime import date
from pathlib import Path

import alcance_fixtures as fx
from c4a import alcance
from c4a.util import sha256_file

HOY = date(2026, 10, 21)


class TestUS3(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _compuerta(self, **kw):
        fx.construir(self.raiz, **kw)
        return alcance.evaluar_compuerta(self.raiz, HOY)

    def test_esc1_ventana_no_informada(self):
        fx.construir(self.raiz)
        filas = alcance.proponer(self.raiz, HOY)["filas"]
        ventana = [f for f in filas if f["tipo"] == "compuerta" and f["clave"] == "ventana"][0]
        self.assertEqual(ventana["decision"], alcance.PENDIENTE)
        c = alcance.evaluar_compuerta(self.raiz, HOY)
        self.assertEqual(c["resultado"], "cerrada")
        self.assertIn("ventana no informada", c["motivos"])

    def test_esc2_no_firmada_aunque_el_alcance_este_firmado(self):
        fx.construir(self.raiz, ventana=("2026-10-01", "2026-12-31"))
        filas = alcance.proponer(self.raiz, HOY)["filas"]
        alcance.corregir(self.raiz, filas[0]["id"], "motivo", "x", "revisión", "Auditor Sintético")
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        c = alcance.evaluar_compuerta(self.raiz, HOY)
        self.assertEqual(alcance.estado_efectivo(self.raiz), "firmado")
        self.assertEqual(c["resultado"], "cerrada")
        self.assertIn("no firmada", c["motivos"])

    def test_esc3_firmada_completa_y_vencida(self):
        c = self._compuerta(firmada=True, organizacion="Org Sintética", exclusiones="Ninguna adicional",
                            ventana=("2026-09-01", "2026-09-30"))
        self.assertEqual((c["firma"], c["completitud"], c["ventana"]), ("firmada", "completa", "vencida"))
        self.assertEqual(c["resultado"], "cerrada")
        self.assertIn("ventana vencida", c["motivos"])

    def test_ventana_que_aun_no_comienza_cierra(self):
        c = self._compuerta(firmada=True, organizacion="Org Sintética", exclusiones="Ninguna adicional",
                            ventana=("2026-11-01", "2026-11-30"))
        self.assertEqual(c["ventana"], "no vigente (aún no comienza)")
        self.assertEqual(c["resultado"], "cerrada")

    def test_fecha_ilegible_es_no_informada(self):
        c = self._compuerta(ventana=("pronto", "2026-12-31"))
        self.assertEqual(c["ventana"], "no informada")
        self.assertEqual(c["resultado"], "cerrada")

    def test_sin_autorizacion(self):
        c = self._compuerta(autorizacion=False)
        self.assertEqual(c["resultado"], "cerrada")

    def test_sc004_toda_combinacion_no_favorable_cierra(self):
        ventanas = {"vigente": ("2026-10-01", "2026-12-31"), "vencida": ("2026-01-01", "2026-02-01"),
                    "no informada": None}
        for firmada, completa, (nombre, v) in itertools.product((True, False), (True, False), ventanas.items()):
            with self.subTest(firmada=firmada, completa=completa, ventana=nombre):
                kw = {"firmada": firmada, "ventana": v}
                if completa:
                    kw.update(organizacion="Org Sintética", exclusiones="Ninguna adicional")
                c = self._compuerta(**kw)
                favorable = firmada and completa and nombre == "vigente"
                self.assertEqual(c["resultado"], "abierta" if favorable else "cerrada", c)
                if not favorable:
                    self.assertTrue(c["motivos"])

    def test_esc4_la_autorizacion_no_se_modifica(self):
        fx.construir(self.raiz)
        ruta = self.raiz / alcance.INSUMO_AUTORIZACION
        antes = sha256_file(ruta)
        filas = alcance.proponer(self.raiz, HOY)["filas"]
        alcance.evaluar_compuerta(self.raiz, HOY)
        alcance.corregir(self.raiz, filas[0]["id"], "motivo", "x", "revisión", "Auditor Sintético")
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        self.assertEqual(antes, sha256_file(ruta))


if __name__ == "__main__":
    unittest.main()
