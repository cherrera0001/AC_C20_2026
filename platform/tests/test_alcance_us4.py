"""S01 · US4 — Entregar el alcance a S02: dentro, fuera o pendiente (insumos SINTÉTICOS)."""
import tempfile
import unittest
from pathlib import Path

import alcance_fixtures as fx
from c4a import alcance


class TestUS4(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        self.filas = alcance.proponer(self.raiz)["filas"]

    def tearDown(self):
        self._tmp.cleanup()

    def _id(self, tipo, texto):
        return [f for f in self.filas if f["tipo"] == tipo and texto in f["valor"]][0]["id"]

    def test_esc1_dominio_excluido_es_fuera_con_fila_y_motivo(self):
        fid = self._id("dominio", "Cifrado en tránsito")
        alcance.corregir(self.raiz, fid, "decision", "excluido", "No se evalúa en este ejercicio",
                         "Auditor Sintético")
        r = alcance.consultar(self.raiz, "dominio", "cifrado en tránsito")
        self.assertEqual(r["respuesta"], "fuera")
        self.assertEqual(r["fila"]["id"], fid)
        self.assertEqual(r["motivo"], "No se evalúa en este ejercicio")

    def test_esc2_otro_activo_es_fuera_y_no_admisible(self):
        r = alcance.consultar(self.raiz, "activo", "OtraMaquina")
        self.assertEqual(r["respuesta"], "fuera")
        self.assertIsNone(r["fila"])
        self.assertFalse(alcance.evidencia_admisible(self.raiz, "OtraMaquina"))
        self.assertTrue(alcance.evidencia_admisible(self.raiz, "MaquinaSintetica"))

    def test_esc3_dominio_pendiente_nunca_dentro(self):
        r = alcance.consultar(self.raiz, "dominio", "Superficie de red")
        self.assertEqual(r["respuesta"], "pendiente")

    def test_dominio_confirmado_es_dentro(self):
        fid = self._id("dominio", "Superficie de red")
        alcance.corregir(self.raiz, fid, "decision", "incluido", "Objetivo central del ejercicio",
                         "Auditor Sintético")
        self.assertEqual(alcance.consultar(self.raiz, "dominio", "superficie de red")["respuesta"], "dentro")

    def test_esc4_borrador_dice_que_no_esta_firmado(self):
        r = alcance.consultar(self.raiz, "activo", "MaquinaSintetica")
        self.assertEqual(r["respuesta"], "dentro")
        self.assertIs(r["firmado"], False)

    def test_firmado_se_informa(self):
        alcance.revisar(self.raiz, "Auditor Sintético", "Revisión completa")
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        self.assertIs(alcance.consultar(self.raiz, "activo", "MaquinaSintetica")["firmado"], True)

    def test_lo_no_listado_es_fuera(self):
        self.assertEqual(alcance.consultar(self.raiz, "dominio", "Auditoría de nómina")["respuesta"], "fuera")


if __name__ == "__main__":
    unittest.main()
