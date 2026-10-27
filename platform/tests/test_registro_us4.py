"""S02 US4 — Rechazar evidencia que no acredita esta auditoría. Insumos SINTÉTICOS (principio III)."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import registro_fixtures as fx
from c4a import alcance, registro

A = "Auditor Sintético"


class Base(unittest.TestCase):
    autorizada = False

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz, autorizada=self.autorizada)
        self.dom = fx.fila(self.raiz, "control:1")

    def tearDown(self):
        self._tmp.cleanup()

    def aportar(self, nombre="doc.txt", *, activo=fx.ACTIVO, dominio=None, tipo="documental", origen="del ejercicio",
                fecha_rec=fx.DIA, afirmacion="Hecho sintético", **kw):
        doc = fx.evidencia(self.raiz, nombre)
        return registro.aportar(self.raiz, activo, dominio or self.dom, afirmacion, "positivo", doc, tipo, fecha_rec,
                                A, origen=origen, fecha=fx.FECHA, **kw)

    def leer(self):
        return json.loads((self.raiz / registro.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestRechazos(Base):
    def setUp(self):
        super().setUp()
        self.fuera = fx.fila(self.raiz, "tecnico:2")
        fx.decidir(self.raiz, self.fuera, "excluido")
        registro.abrir(self.raiz)

    def test_sc003_las_cinco_causas(self):
        casos = {
            registro.RECHAZO_ACTIVO: dict(activo="OtraMaquinaSintetica"),
            registro.RECHAZO_DOMINIO: dict(dominio=self.fuera),
            registro.RECHAZO_OBJETIVO: dict(corrida=fx.RUN_OTRO),
            registro.RECHAZO_AUTORIZACION: dict(tipo="tecnica"),
            registro.RECHAZO_ORIGEN: dict(origen=""),
        }
        for i, (motivo, kw) in enumerate(casos.items()):
            with self.subTest(motivo=motivo):
                r = self.aportar(f"e{i}.txt", **kw)
                self.assertFalse(r["aceptada"])
                self.assertEqual(r["motivo"], motivo)
        c = self.leer()
        self.assertEqual([r["motivo"] for r in c["rechazos"]], list(casos))
        self.assertFalse(any(e["clase"] == registro.HECHO for e in c["entradas"]))
        por_motivo = {r["motivo"]: r for r in c["rechazos"]}
        self.assertEqual(por_motivo[registro.RECHAZO_DOMINIO]["fila_alcance"], self.fuera)
        md = (self.raiz / registro.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn("## Rechazos (5)", md)

    def test_corrida_inexistente_y_corrida_del_activo(self):
        self.assertEqual(self.aportar("a.txt", corrida="RUN-NO-EXISTE")["motivo"], registro.RECHAZO_OBJETIVO)
        self.assertTrue(self.aportar("b.txt", corrida=fx.RUN_ACTIVO)["aceptada"])

    def test_documental_se_acepta_con_compuerta_cerrada(self):
        self.assertEqual(alcance.evaluar_compuerta(self.raiz)["resultado"], "cerrada")
        self.assertTrue(self.aportar()["aceptada"])

    def test_sc013_pendiente_aceptada_con_marca(self):
        r = self.aportar()
        e = next(x for x in self.leer()["entradas"] if x["id"] == r["entrada"])
        self.assertIn(registro.MARCA_PENDIENTE, e["marcas"])
        entregada = next(x for x in registro.entregar(self.raiz)["entradas"] if x["id"] == r["entrada"])
        self.assertIn(registro.MARCA_PENDIENTE, entregada["marcas"])


class TestTecnicaAutorizada(Base):
    autorizada = True

    def test_tecnica_con_autorizacion_vigente_en_su_fecha(self):
        registro.abrir(self.raiz, date(2026, 10, 15))
        dom = fx.fila(self.raiz, "tecnico:1")
        self.assertTrue(self.aportar(dominio=dom, tipo="tecnica", fecha_rec="2026-10-15")["aceptada"])
        r = self.aportar("fuera_de_ventana.txt", dominio=dom, tipo="tecnica", fecha_rec="2026-11-15")
        self.assertEqual(r["motivo"], registro.RECHAZO_AUTORIZACION)


class TestAlteracionYCambios(Base):
    def setUp(self):
        super().setUp()
        registro.abrir(self.raiz)

    def test_sc004_evidencia_alterada(self):
        r = self.aportar()
        registro.revisar(self.raiz, A, "r", fx.FECHA)
        registro.firmar(self.raiz, A, "f", fx.FECHA)
        ev = next(x for x in self.leer()["entradas"] if x["id"] == r["entrada"])["evidencias"][0]
        copia = self.raiz / ev["copia"]
        copia.write_bytes(copia.read_bytes() + b"x")
        v = registro.verificar(self.raiz)
        self.assertEqual(v["entradas_alteradas"], [r["entrada"]])
        self.assertEqual(v["estado_informado"], "firmado con evidencia alterada")
        self.assertFalse(v["integro"])
        self.assertNotIn(r["entrada"], [e["id"] for e in registro.entregar(self.raiz)["entradas"]])

    def test_fr015_dominio_pasa_a_fuera(self):
        r = self.aportar()
        fx.decidir(self.raiz, self.dom, "excluido")
        c = registro.abrir(self.raiz)
        e = next(x for x in c["entradas"] if x["id"] == r["entrada"])
        self.assertIn(registro.MARCA_FUERA, e["marcas"])
        self.assertTrue(any(r["entrada"] in a for a in c["avisos"]))
        self.assertNotIn(r["entrada"], [x["id"] for x in registro.entregar(self.raiz)["entradas"]])

    def test_fr015_firmado_y_alcance_o_autorizacion_cambiados_codigo_4(self):
        for cambio in ("alcance", "autorizacion", "compuerta"):
            with self.subTest(cambio=cambio):
                registro.abrir(self.raiz)
                registro.revisar(self.raiz, A, "r", fx.FECHA)
                registro.firmar(self.raiz, A, "f", fx.FECHA)
                antes = (self.raiz / registro.ARCHIVO_JSON).read_bytes()
                aut = self.raiz / "scope" / "autorizacion.md"
                aut_original = aut.read_bytes()
                ref = None
                if cambio == "alcance":
                    fx.decidir(self.raiz, fx.fila(self.raiz, "tecnico:1"), "incluido")
                elif cambio == "autorizacion":
                    aut.write_bytes(aut_original + b"\n<!-- cambio sintetico -->\n")
                else:
                    ref = date(2030, 1, 1)  # misma autorización, otra fecha de evaluación
                with self.assertRaises(registro.RegistroError) as cm:
                    registro.abrir(self.raiz, ref)
                self.assertEqual(cm.exception.codigo, 4)
                self.assertEqual((self.raiz / registro.ARCHIVO_JSON).read_bytes(), antes)
                aut.write_bytes(aut_original)
                (self.raiz / registro.ARCHIVO_FIRMA).unlink()

    def test_t040_no_consta_descartada_no_se_entrega(self):
        nc = registro.id_no_consta(fx.ACTIVO, self.dom)
        registro.descartar(self.raiz, nc, "no aplica a este ejercicio", A, fx.FECHA)
        c = self.leer()
        self.assertNotIn(nc, [e["id"] for e in registro.no_consta_vigentes(c)])
        self.assertNotIn(nc, [e["id"] for e in registro.entregar(self.raiz)["entradas"]])
        registro.revisar(self.raiz, A, "r", fx.FECHA)
        f = registro.firmar(self.raiz, A, "f", fx.FECHA)
        self.assertEqual(f["no_consta_al_firmar"], fx.N_DOMINIOS_FIXTURE)
        md = (self.raiz / registro.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn(f"## No consta ({fx.N_DOMINIOS_FIXTURE})", md)

    def test_t042_copia_alterada_no_se_reutiliza(self):
        r = self.aportar()
        ev = next(x for x in self.leer()["entradas"] if x["id"] == r["entrada"])["evidencias"][0]
        copia = self.raiz / ev["copia"]
        copia.write_bytes(copia.read_bytes() + b"x")
        antes = (self.raiz / registro.ARCHIVO_JSON).read_bytes()
        with self.assertRaises(registro.RegistroError) as cm:
            self.aportar(afirmacion="Otro hecho con la misma evidencia")
        self.assertEqual(cm.exception.codigo, 3)
        self.assertEqual((self.raiz / registro.ARCHIVO_JSON).read_bytes(), antes)

    def test_t044_alcance_que_se_firma_se_advierte(self):
        alcance.revisar(self.raiz, A, "revisión sintética", fx.FECHA)
        alcance.firmar(self.raiz, A, "firma sintética", fx.FECHA)
        c = registro.abrir(self.raiz)
        self.assertTrue(c["alcance"]["firmado"])
        self.assertTrue(any("la firma del alcance" in a for a in c["avisos"]), c["avisos"])

    def test_fr018_dos_aperturas_en_fechas_distintas_mismos_bytes(self):
        a = (self.raiz / registro.ARCHIVO_JSON).read_bytes()
        registro.abrir(self.raiz)  # sin fecha de referencia: conserva la compuerta guardada
        self.assertEqual((self.raiz / registro.ARCHIVO_JSON).read_bytes(), a)

    def test_sc010_entrega_solo_vigentes(self):
        r1 = self.aportar("a.txt", afirmacion="Hecho A")
        r2 = self.aportar("b.txt", afirmacion="Hecho B")
        registro.descartar(self.raiz, r2["entrada"], "no corresponde", A, fx.FECHA)
        ids = [e["id"] for e in registro.entregar(self.raiz)["entradas"]]
        self.assertIn(r1["entrada"], ids)
        self.assertNotIn(r2["entrada"], ids)
        nc = registro.id_no_consta(fx.ACTIVO, self.dom)
        self.assertNotIn(nc, ids)  # superada por el hecho vigente
        registro.descartar(self.raiz, r1["entrada"], "tampoco", A, fx.FECHA)
        d = registro.entregar(self.raiz)
        ids = [e["id"] for e in d["entradas"]]
        self.assertIn(nc, ids)  # sin hechos vigentes, la «no consta» vuelve (U3)
        self.assertFalse(d["firmado"])
        for e in d["entradas"]:
            for x in e["evidencias"]:
                self.assertTrue(x["sha256_original"])


if __name__ == "__main__":
    unittest.main()
