"""S02 US2 — La herramienta propone un hecho y el auditor lo corrige. Insumos SINTÉTICOS."""
import json
import tempfile
import unittest
from pathlib import Path

import registro_fixtures as fx
from c4a import registro
from c4a.util import sha256_file

A = "Auditor Sintético"


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        registro.abrir(self.raiz)
        self.dom = fx.fila(self.raiz, "control:1")

    def tearDown(self):
        self._tmp.cleanup()

    def aportar(self, nombre="doc.txt", afirmacion="La política de parches existe", resultado="positivo",
                dominio=None, **kw):
        doc = fx.evidencia(self.raiz, nombre)
        kw.setdefault("origen", "documento del ejercicio")
        return registro.aportar(self.raiz, fx.ACTIVO, dominio or self.dom, afirmacion, resultado, doc,
                                "documental", fx.DIA, A, fecha=fx.FECHA, **kw)

    def leer(self):
        return json.loads((self.raiz / registro.ARCHIVO_JSON).read_text(encoding="utf-8"))

    def entrada(self, eid):
        return next(e for e in self.leer()["entradas"] if e["id"] == eid)

    def bytes(self):
        return (self.raiz / registro.ARCHIVO_JSON).read_bytes()


class TestProponer(Base):
    def test_esc1_sc002_fr005_hecho_propuesto_con_evidencia_completa(self):
        r = self.aportar()
        self.assertTrue(r["aceptada"])
        e = self.entrada(r["entrada"])
        self.assertEqual(e["clase"], registro.HECHO)
        self.assertRegex(e["id"], r"^H-[0-9a-f]{10}$")
        self.assertEqual(e["estado_aprobacion"], "borrador")
        self.assertEqual(e["resultado"], "positivo")
        ev = e["evidencias"][0]
        self.assertRegex(ev["id"], r"^E-[0-9a-f]{10}$")
        for k in ("tipo", "origen", "ubicacion_original", "fecha_recoleccion", "responsable", "sha256_guardado"):
            self.assertTrue(ev[k], k)
        self.assertEqual(ev["sha256_guardado"], sha256_file(self.raiz / ev["copia"]))
        self.assertEqual(ev["sha256_original"], sha256_file(self.raiz / ev["ubicacion_original"]))
        self.assertTrue(ev["copia"].startswith(registro.CARPETA_COPIAS + "/"))

    def test_fr005_documental_sin_origen_rechazada(self):
        r = self.aportar(origen="")
        self.assertFalse(r["aceptada"])
        self.assertEqual(r["motivo"], registro.RECHAZO_ORIGEN)
        self.assertFalse(any(e["clase"] == registro.HECHO for e in self.leer()["entradas"]))

    def test_fr005_referencia_sin_copia(self):
        r = self.aportar(sin_copia=True)
        ev = self.entrada(r["entrada"])["evidencias"][0]
        self.assertTrue(ev["sin_copia"])
        self.assertIsNone(ev["copia"])
        self.assertIsNone(ev["sha256_guardado"])
        self.assertFalse((self.raiz / registro.CARPETA_COPIAS).exists())

    def test_fr006_evidencias_que_discrepan_dan_inconcluso(self):
        self.aportar("a.txt", resultado="positivo")
        r = self.aportar("b.txt", resultado="negativo")
        e = self.entrada(r["entrada"])
        self.assertEqual(len(e["evidencias"]), 2)
        self.assertEqual(e["resultado"], "inconcluso")

    def test_sc011_mismo_hecho_una_entrada_y_misma_evidencia_sin_duplicar(self):
        r1 = self.aportar("a.txt")
        r2 = self.aportar("b.txt", afirmacion="  la POLÍTICA de parches   existe ")
        self.assertEqual(r1["entrada"], r2["entrada"])
        self.assertEqual(len(self.entrada(r1["entrada"])["evidencias"]), 2)
        self.aportar("a.txt")
        self.assertEqual(len(self.entrada(r1["entrada"])["evidencias"]), 2)
        self.assertEqual(sum(1 for e in self.leer()["entradas"] if e["clase"] == registro.HECHO), 1)

    def test_esc5_no_consta_superada_conserva_historia(self):
        nc = registro.id_no_consta(fx.ACTIVO, self.dom)
        r = self.aportar()
        e = self.entrada(nc)
        self.assertIn(registro.MARCA_SUPERADA + r["entrada"], e["marcas"])
        self.assertNotIn(e, registro.no_consta_vigentes(self.leer()))

    def test_archivo_inexistente_codigo_2_sin_escribir(self):
        antes = self.bytes()
        with self.assertRaises(registro.RegistroError) as cm:
            registro.aportar(self.raiz, fx.ACTIVO, self.dom, "x", "positivo", self.raiz / "no-existe.txt",
                             "documental", fx.DIA, A, origen="o")
        self.assertEqual(cm.exception.codigo, 2)
        self.assertEqual(self.bytes(), antes)


class TestCorregir(Base):
    def test_esc2_correccion_con_historial_y_revisado(self):
        r = self.aportar()
        e = registro.corregir(self.raiz, r["entrada"], "resultado", "inconcluso", "falta fecha del documento", A, fx.FECHA)
        self.assertEqual(e["resultado"], "inconcluso")
        self.assertEqual(e["estado_aprobacion"], "revisado")
        ev = self.leer()["historial"][-1]
        self.assertEqual((ev["tipo"], ev["autor"], ev["fecha"], ev["anterior"], ev["nuevo"], ev["motivo"]),
                         ("correccion", A, fx.FECHA, "positivo", "inconcluso", "falta fecha del documento"))

    def test_esc3_rechazos_de_edicion_no_modifican_el_archivo(self):
        r = self.aportar()
        antes = self.bytes()
        casos = [("resultado", "inconcluso", " ", A), ("resultado", "inconcluso", "m", " "),
                 ("responsable", "x", "m", A), ("resultado", "cumple", "m", A)]
        for campo, valor, motivo, autor in casos:
            with self.subTest(campo=campo, motivo=motivo, autor=autor):
                with self.assertRaises(registro.RegistroError) as cm:
                    registro.corregir(self.raiz, r["entrada"], campo, valor, motivo, autor)
                self.assertEqual(cm.exception.codigo, 1)
                self.assertEqual(self.bytes(), antes)
        with self.assertRaises(registro.RegistroError):
            registro.corregir(self.raiz, "H-0000000000", "motivo", "x", "m", A)

    def test_t041_sin_evidencia_no_se_afirma_un_hecho(self):
        nc = registro.id_no_consta(fx.ACTIVO, self.dom)
        antes = self.bytes()
        for campo, valor in (("resultado", "positivo"), ("resultado", "negativo"),
                             ("afirmacion", "La política existe")):
            with self.subTest(campo=campo, valor=valor):
                with self.assertRaises(registro.RegistroError) as cm:
                    registro.corregir(self.raiz, nc, campo, valor, "m", A)
                self.assertEqual(cm.exception.codigo, 1)
                self.assertEqual(self.bytes(), antes)
        e = registro.corregir(self.raiz, nc, "motivo", "se pidió el documento", "m", A, fx.FECHA)
        self.assertEqual(e["resultado"], "no-ejecutado")

    def test_fr013_campos_corregibles(self):
        r = self.aportar()
        for campo, valor in (("afirmacion", "La política de parches existe y está vigente"),
                             ("resultado", "negativo"), ("motivo", "documento firmado")):
            e = registro.corregir(self.raiz, r["entrada"], campo, valor, "ajuste", A, fx.FECHA)
            self.assertEqual(e[campo], valor)
        self.assertEqual(e["id"], r["entrada"])  # el id se fija en el primer aporte

    def test_fr013_descartar_y_restablecer_sin_borrar(self):
        r = self.aportar()
        nc = registro.id_no_consta(fx.ACTIVO, self.dom)
        n = len(self.leer()["entradas"])
        e = registro.descartar(self.raiz, r["entrada"], "documento de otro período", A, fx.FECHA)
        self.assertIn(registro.MARCA_DESCARTADA, e["marcas"])
        self.assertEqual(len(self.leer()["entradas"]), n)
        self.assertIn(self.entrada(nc), registro.no_consta_vigentes(self.leer()))  # U3: vuelve a valer
        with self.assertRaises(registro.RegistroError):
            registro.descartar(self.raiz, r["entrada"], "otra vez", A)
        e = registro.restablecer(self.raiz, r["entrada"], "era del período", A, fx.FECHA)
        self.assertNotIn(registro.MARCA_DESCARTADA, e["marcas"])
        self.assertNotIn(self.entrada(nc), registro.no_consta_vigentes(self.leer()))
        with self.assertRaises(registro.RegistroError):
            registro.restablecer(self.raiz, r["entrada"], "no está descartada", A)
        tipos = [ev["tipo"] for ev in self.leer()["historial"]]
        self.assertEqual(tipos.count("descarte"), 1)
        self.assertEqual(tipos.count("restablecimiento"), 1)


class TestFirmar(Base):
    def firmar_valido(self):
        self.aportar()
        registro.revisar(self.raiz, A, "revisado", fx.FECHA)
        return registro.firmar(self.raiz, A, "registro completo para S03", fx.FECHA)

    def test_esc4_firma_y_anulacion(self):
        f = self.firmar_valido()
        self.assertEqual(registro.estado_efectivo(self.raiz), "firmado")
        self.assertEqual(f["sha256"], sha256_file(self.raiz / registro.ARCHIVO_JSON))
        self.assertEqual(f["no_consta_al_firmar"], fx.N_DOMINIOS_FIXTURE)  # una superada por el hecho
        self.assertEqual(f["nota"], registro.NOTA_FIRMA)
        self.aportar("otro.txt")
        self.assertFalse((self.raiz / registro.ARCHIVO_FIRMA).exists())
        self.assertEqual(self.leer()["historial"][-1]["tipo"], "firma_anulada")
        self.assertNotEqual(registro.estado_efectivo(self.raiz), "firmado")

    def test_fr014_firmar_rechazado(self):
        self.aportar()
        with self.assertRaises(registro.RegistroError):
            registro.firmar(self.raiz, A, "m")  # borrador
        registro.revisar(self.raiz, A, "revisado", fx.FECHA)
        for firmante, motivo in ((" ", "m"), (A, " ")):
            with self.assertRaises(registro.RegistroError):
                registro.firmar(self.raiz, firmante, motivo)
        self.assertFalse((self.raiz / registro.ARCHIVO_FIRMA).exists())

    def test_u4_aporte_tras_revisar_vuelve_a_borrador(self):
        self.aportar()
        registro.revisar(self.raiz, A, "revisado", fx.FECHA)
        self.assertEqual(self.leer()["estado_aprobacion"], "revisado")
        self.aportar("nuevo.txt")
        self.assertEqual(self.leer()["estado_aprobacion"], "borrador")
        with self.assertRaises(registro.RegistroError):
            registro.firmar(self.raiz, A, "m")

    def test_i1_rechazo_y_revision_tras_firma_la_anulan(self):
        for accion in ("rechazo", "revision"):
            with self.subTest(accion=accion):
                registro.revisar(self.raiz, A, "revisado", fx.FECHA)
                registro.firmar(self.raiz, A, "firma", fx.FECHA)
                if accion == "rechazo":
                    self.aportar("sin_origen.txt", origen="")
                else:
                    registro.revisar(self.raiz, A, "otra revisión", fx.FECHA)
                self.assertEqual(self.leer()["historial"][-1]["tipo"], "firma_anulada")
                v = registro.verificar(self.raiz)
                self.assertEqual(v["estado"], "sin firma")
                self.assertTrue(v["integro"])

    def test_sc004_alterar_un_byte_del_registro_se_detecta(self):
        self.firmar_valido()
        ruta = self.raiz / registro.ARCHIVO_JSON
        original = ruta.read_bytes()
        for pos in (0, len(original) // 3, len(original) // 2, len(original) - 2):
            with self.subTest(pos=pos):
                b = bytearray(original)
                b[pos] = (b[pos] + 1) % 256
                ruta.write_bytes(bytes(b))
                v = registro.verificar(self.raiz)
                self.assertFalse(v["integro"])
                self.assertEqual(v["estado"], "revisado (firma no aplica)")
                ruta.write_bytes(original)
        self.assertEqual(registro.verificar(self.raiz)["estado"], "firmado")

    def test_sc006_firmado_solo_por_firmar_y_eventos_con_autor_fecha_motivo(self):
        r = self.aportar()
        registro.corregir(self.raiz, r["entrada"], "motivo", "m", "motivo", A, fx.FECHA)
        registro.descartar(self.raiz, r["entrada"], "d", A, fx.FECHA)
        registro.restablecer(self.raiz, r["entrada"], "r", A, fx.FECHA)
        registro.revisar(self.raiz, A, "rev", fx.FECHA)
        self.assertNotEqual(registro.estado_efectivo(self.raiz), "firmado")
        for ev in self.leer()["historial"]:
            if ev["tipo"] in ("correccion", "descarte", "restablecimiento", "revision"):
                self.assertTrue(ev["autor"] and ev["fecha"] and ev["motivo"], ev)

    def test_sc007_mismas_entradas_mismos_bytes(self):
        def generar(raiz):
            fx.construir(raiz)
            registro.abrir(raiz)
            dom = fx.fila(raiz, "control:1")
            doc = fx.evidencia(raiz, "doc.txt")
            r = registro.aportar(raiz, fx.ACTIVO, dom, "La política existe", "positivo", doc, "documental",
                                 fx.DIA, A, origen="o", fecha=fx.FECHA)
            registro.corregir(raiz, r["entrada"], "resultado", "inconcluso", "m", A, fx.FECHA)
            return (raiz / registro.ARCHIVO_JSON).read_bytes()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertEqual(generar(Path(a)), generar(Path(b)))


if __name__ == "__main__":
    unittest.main()
