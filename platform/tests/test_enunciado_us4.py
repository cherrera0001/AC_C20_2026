"""S03 US4 — Verificar la consistencia con el registro y entregar a S04. Insumos SINTÉTICOS."""
import json
import tempfile
import unittest
from pathlib import Path

import enunciado_fixtures as fx
from c4a import alcance
from c4a import enunciado
from c4a import registro


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        enunciado.abrir(self.raiz, fecha=fx.FECHA)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self):
        return json.loads((self.raiz / enunciado.ARCHIVO_JSON).read_text(encoding="utf-8"))


class TestVerificar(Base):
    def test_sc004_alterar_byte_del_json_se_detecta(self):
        c = self.leer()
        for e in c["enunciados"]:
            enunciado.corregir(self.raiz, e["id"], "criterio", "Criterio", "x", "Auditor", fx.FECHA)
            enunciado.corregir(self.raiz, e["id"], "impacto", "Impacto", "x", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        enunciado.firmar(self.raiz, "Auditor", "firma", fx.FECHA)
        ruta = self.raiz / enunciado.ARCHIVO_JSON
        datos = bytearray(ruta.read_bytes())
        datos[10] ^= 0x01
        ruta.write_bytes(bytes(datos))
        v = enunciado.verificar(self.raiz)
        self.assertFalse(v["integro"])
        self.assertTrue(v["estado"].startswith("revisado"))

    def test_sc005_alterar_evidencia_marca_enunciado(self):
        c = self.leer()
        e = c["enunciados"][0]
        copia = self.raiz / e["evidencias"][0]["copia"]
        datos = bytearray(copia.read_bytes())
        datos[0] ^= 0x01
        copia.write_bytes(bytes(datos))
        v = enunciado.verificar(self.raiz)
        self.assertIn(e["id"], v["evidencias_alteradas"])
        d = enunciado.entregar(self.raiz)
        self.assertNotIn(e["id"], [x["id"] for x in d["enunciados"]])

    def test_sc005_estado_firmado_con_evidencia_alterada(self):
        for e in self.leer()["enunciados"]:
            enunciado.corregir(self.raiz, e["id"], "criterio", "Criterio", "completar", "Auditor", fx.FECHA)
            enunciado.corregir(self.raiz, e["id"], "impacto", "Impacto", "completar", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        enunciado.firmar(self.raiz, "Auditor", "firma sintética", fx.FECHA)
        c = self.leer()
        copia = self.raiz / c["enunciados"][0]["evidencias"][0]["copia"]
        datos = bytearray(copia.read_bytes())
        datos[0] ^= 0x01
        copia.write_bytes(bytes(datos))
        v = enunciado.verificar(self.raiz)
        self.assertEqual(v["estado"], "firmado")
        self.assertIn("firmado con evidencia alterada", v["estado_informado"])

    def test_fr009_hecho_no_vigente(self):
        c = self.leer()
        e = c["enunciados"][0]
        for x in c["enunciados"]:
            enunciado.corregir(self.raiz, x["id"], "criterio", "Criterio", "x", "Auditor", fx.FECHA)
            enunciado.corregir(self.raiz, x["id"], "impacto", "Impacto", "x", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        enunciado.firmar(self.raiz, "Auditor", "firma", fx.FECHA)
        # el hecho deja de estar en la entrega: se informa «hecho no vigente» sin tocar nada
        registro.descartar(self.raiz, e["hecho"]["id"], "sale de la entrega", "Auditor", fx.FECHA)
        v = enunciado.verificar(self.raiz)
        self.assertIn(e["id"], v["hechos_no_vigentes"])
        self.assertIn("hecho no vigente", v["estado_informado"])

    def test_sc009_entrega_exactamente_vigentes(self):
        c = self.leer()
        e = c["enunciados"][0]
        enunciado.descartar(self.raiz, e["id"], "descarte de prueba", "Auditor", fx.FECHA)
        d = enunciado.entregar(self.raiz)
        self.assertEqual(len(d["enunciados"]), fx.N_HECHOS - 1)
        self.assertNotIn(e["id"], [x["id"] for x in d["enunciados"]])
        enunciado.restablecer(self.raiz, e["id"], "vuelve", "Auditor", fx.FECHA)
        d = enunciado.entregar(self.raiz)
        self.assertEqual(len(d["enunciados"]), fx.N_HECHOS)
        self.assertEqual(len(d["vacios"]), fx.N_VACIOS)

    def test_sc013_origen_cambiado_codigo_4(self):
        c = self.leer()
        for e in c["enunciados"]:
            enunciado.corregir(self.raiz, e["id"], "criterio", "Criterio", "x", "Auditor", fx.FECHA)
            enunciado.corregir(self.raiz, e["id"], "impacto", "Impacto", "x", "Auditor", fx.FECHA)
        enunciado.revisar(self.raiz, "Auditor", "revisión", fx.FECHA)
        enunciado.firmar(self.raiz, "Auditor", "firma", fx.FECHA)
        # el registro de origen cambia: un aporte nuevo altera la entrega
        import registro_fixtures as rfx
        dom = rfx.fila(self.raiz, "control:2")
        doc = rfx.evidencia(self.raiz, "doc_tardio.txt", "hecho tardío")
        registro.aportar(self.raiz, fx.ACTIVO, dom, "Hecho tardío del auditor", "positivo", doc,
                         "documental", fx.DIA, "Auditor", origen="del ejercicio", fecha=fx.FECHA)
        with self.assertRaises(enunciado.EnunciadoError) as cm:
            enunciado.abrir(self.raiz)
        self.assertEqual(cm.exception.codigo, 4)
        e = self.leer()["enunciados"][0]
        with self.assertRaises(enunciado.EnunciadoError) as cm2:
            enunciado.corregir(self.raiz, e["id"], "impacto", "otro", "m", "Auditor")
        self.assertEqual(cm2.exception.codigo, 4)
