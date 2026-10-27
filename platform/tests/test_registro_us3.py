"""S02 US3 — Un dato no consta y la fila se conserva. Insumos SINTÉTICOS (principio III)."""
import json
import tempfile
import unittest
from pathlib import Path

import registro_fixtures as fx
from c4a import registro
from c4a.util import sha256_file

A = "Auditor Sintético"


class TestNoConsta(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)

    def tearDown(self):
        self._tmp.cleanup()

    def entrada(self, c, prefijo):
        fila = fx.fila(self.raiz, prefijo)
        return next(e for e in c["entradas"] if e["dominio"]["fila"] == fila and e["clase"] == registro.NO_CONSTA)

    def test_esc1_fr009_dominio_tecnico_compuerta_cerrada(self):
        aut = self.raiz / "scope" / "autorizacion.md"
        antes = sha256_file(aut)
        c = registro.abrir(self.raiz)
        self.assertEqual(c["alcance"]["compuerta"], "cerrada")
        for pref in ("tecnico:1", "tecnico:2"):
            e = self.entrada(c, pref)
            self.assertEqual((e["resultado"], e["motivo"]), ("no-ejecutado", registro.MOTIVO_COMPUERTA))
        self.assertEqual(sha256_file(aut), antes)

    def test_esc2_fr010_politicas_personas_procesos_requiere_solicitud_documental(self):
        c = registro.abrir(self.raiz)
        self.assertEqual(self.entrada(c, "control:2")["motivo"], registro.MOTIVO_DOCUMENTAL)
        self.assertEqual(self.entrada(c, "control:1")["motivo"], registro.MOTIVO_SIN_EVIDENCIA)

    def test_compuerta_abierta_deja_de_ser_motivo(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            fx.construir(raiz, autorizada=True)
            from datetime import date
            c = registro.abrir(raiz, date(2026, 10, 15))
            self.assertEqual(c["alcance"]["compuerta"], "abierta")
            self.assertTrue(all(e["motivo"] != registro.MOTIVO_COMPUERTA for e in c["entradas"]))

    def test_esc3_no_consta_se_conserva_al_regenerar(self):
        c1 = registro.abrir(self.raiz)
        c2 = registro.abrir(self.raiz)
        self.assertEqual([e["id"] for e in c1["entradas"]], [e["id"] for e in c2["entradas"]])

    def test_esc4_resumen_cuenta_no_consta_y_nunca_dice_sin_hallazgos(self):
        registro.abrir(self.raiz)
        md = (self.raiz / registro.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn(f"{fx.N_DOMINIOS_FIXTURE + 1} entradas no constan", md)
        self.assertIn(registro.NOTA_NO_CONSTA, md)
        for ruta in (registro.ARCHIVO_JSON, registro.ARCHIVO_MD):
            t = (self.raiz / ruta).read_text(encoding="utf-8").lower()
            self.assertNotIn("sin hallazgos", t)

    def test_firmar_con_no_consta_guarda_el_conteo(self):
        registro.abrir(self.raiz)
        registro.revisar(self.raiz, A, "revisado sin evidencias", fx.FECHA)
        f = registro.firmar(self.raiz, A, "se firma con lo que no consta", fx.FECHA)
        self.assertEqual(f["no_consta_al_firmar"], fx.N_DOMINIOS_FIXTURE + 1)
        firma = json.loads((self.raiz / registro.ARCHIVO_FIRMA).read_text(encoding="utf-8"))
        self.assertEqual(firma["no_consta_al_firmar"], fx.N_DOMINIOS_FIXTURE + 1)

    def test_ninguna_funcion_abre_la_compuerta(self):
        aut = self.raiz / "scope" / "autorizacion.md"
        antes = sha256_file(aut)
        registro.abrir(self.raiz)
        registro.revisar(self.raiz, A, "r", fx.FECHA)
        registro.firmar(self.raiz, A, "f", fx.FECHA)
        registro.verificar(self.raiz)
        registro.entregar(self.raiz)
        self.assertEqual(sha256_file(aut), antes)
        from c4a import alcance
        self.assertEqual(alcance.evaluar_compuerta(self.raiz)["resultado"], "cerrada")


if __name__ == "__main__":
    unittest.main()
