"""S01 · US2 — El auditor corrige y firma la propuesta (insumos SINTÉTICOS)."""
import json
import tempfile
import unittest
from pathlib import Path

import alcance_fixtures as fx
from c4a import alcance


class TestUS2(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        self.contenido = alcance.proponer(self.raiz)
        self.cifrado = [f for f in self.contenido["filas"]
                        if f["tipo"] == "dominio" and "Cifrado en tránsito" in f["valor"]][0]

    def tearDown(self):
        self._tmp.cleanup()

    def _json(self):
        return (self.raiz / alcance.ARCHIVO_JSON).read_bytes()

    def _corregir(self, **kw):
        base = dict(fila=self.cifrado["id"], campo="decision", valor="excluido",
                    motivo="Fuera del alcance acordado", autor="Auditor Sintético",
                    fecha="2026-10-21T12:00:00Z")
        base.update(kw)
        return alcance.corregir(self.raiz, **base)

    def test_esc1_correccion_registrada_y_revisado(self):
        self._corregir()
        c = alcance.cargar(self.raiz)
        ev = c["historial"][-1]
        self.assertEqual((ev["autor"], ev["fecha"], ev["anterior"], ev["nuevo"], ev["motivo"]),
                         ("Auditor Sintético", "2026-10-21T12:00:00Z", alcance.PENDIENTE,
                          "excluido", "Fuera del alcance acordado"))
        self.assertEqual(c["estado_aprobacion"], "revisado")
        fila = [f for f in c["filas"] if f["id"] == self.cifrado["id"]][0]
        self.assertEqual(fila["estado_aprobacion"], "revisado")

    def test_esc2_sin_motivo_se_rechaza_sin_modificar(self):
        antes = self._json()
        for motivo in ("", "   "):
            with self.assertRaises(alcance.AlcanceError):
                self._corregir(motivo=motivo)
        self.assertEqual(antes, self._json())

    def test_sin_autor_o_campo_invalido_se_rechaza(self):
        antes = self._json()
        with self.assertRaises(alcance.AlcanceError):
            self._corregir(autor="")
        with self.assertRaises(alcance.AlcanceError):
            self._corregir(campo="estado_aprobacion")
        with self.assertRaises(alcance.AlcanceError):
            self._corregir(valor="cumple")
        self.assertEqual(antes, self._json())

    def test_esc3_firmar_revisado(self):
        self._corregir()
        reg = alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo", fecha="2026-10-21T13:00:00Z")
        self.assertEqual(alcance.estado_efectivo(self.raiz), "firmado")
        self.assertEqual(reg["firmante"], "Auditor Sintético")
        self.assertEqual(reg["sha256"], alcance.verificar(self.raiz)["sha256_actual"])
        self.assertIn("no abre la compuerta", reg["nota"])
        self.assertEqual(alcance.evaluar_compuerta(self.raiz)["resultado"], "cerrada")

    def test_firmar_desde_borrador_o_sin_nombre_se_rechaza(self):
        with self.assertRaises(alcance.AlcanceError):
            alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        self._corregir()
        with self.assertRaises(alcance.AlcanceError):
            alcance.firmar(self.raiz, "  ", "Alcance revisado completo")
        self.assertFalse((self.raiz / alcance.ARCHIVO_FIRMA).exists())

    def test_firmar_sin_justificacion_se_rechaza(self):
        self._corregir()
        for motivo in ("", "  "):
            with self.assertRaises(alcance.AlcanceError):
                alcance.firmar(self.raiz, "Auditor Sintético", motivo)
        self.assertFalse((self.raiz / alcance.ARCHIVO_FIRMA).exists())

    def test_firma_registra_justificacion(self):
        self._corregir()
        reg = alcance.firmar(self.raiz, "Auditor Sintético", "Revisé cada fila contra su fuente")
        self.assertEqual(reg["motivo"], "Revisé cada fila contra su fuente")
        self.assertEqual(alcance.verificar(self.raiz)["motivo"], reg["motivo"])
        md = (self.raiz / alcance.ARCHIVO_MD).read_text(encoding="utf-8")
        self.assertIn("Justificación: Revisé cada fila contra su fuente", md)

    def test_esc4_cambio_posterior_anula_la_firma(self):
        self._corregir()
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        self._corregir(campo="motivo", valor="Motivo precisado", motivo="Precisión")
        self.assertEqual(alcance.estado_efectivo(self.raiz), "revisado")
        self.assertFalse((self.raiz / alcance.ARCHIVO_FIRMA).exists())
        self.assertEqual(alcance.cargar(self.raiz)["historial"][-1]["tipo"], "firma_anulada")

    def test_esc5_regenerar_conserva_correcciones(self):
        self._corregir()
        alcance.proponer(self.raiz)
        fila = [f for f in alcance.cargar(self.raiz)["filas"] if f["id"] == self.cifrado["id"]][0]
        self.assertEqual(fila["decision"], "excluido")

    def test_sc006_un_byte_alterado_se_detecta(self):
        self._corregir()
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        original = self._json()
        ruta = self.raiz / alcance.ARCHIVO_JSON
        for pos in (0, len(original) // 2, len(original) - 2):
            datos = bytearray(original)
            datos[pos] = (datos[pos] + 1) % 256
            ruta.write_bytes(bytes(datos))
            self.assertEqual(alcance.verificar(self.raiz)["estado"], "revisado (firma no aplica)")
            self.assertNotEqual(alcance.estado_efectivo(self.raiz), "firmado")
        ruta.write_bytes(original)
        self.assertEqual(alcance.verificar(self.raiz)["estado"], "firmado")

    def test_sc007_solo_firmar_lleva_a_firmado(self):
        self.assertEqual(alcance.estado_efectivo(self.raiz), "borrador")
        self._corregir()
        alcance.revisar(self.raiz, "Auditor Sintético", "Revisado completo")
        alcance.proponer(self.raiz)
        self.assertEqual(alcance.estado_efectivo(self.raiz), "revisado")
        for ev in alcance.cargar(self.raiz)["historial"]:
            self.assertTrue(ev["autor"] and ev["fecha"] and ev["motivo"])

    def test_sc009_determinismo(self):
        self._corregir()
        primero = self._json()
        alcance.proponer(self.raiz)
        self.assertEqual(primero, self._json())

    def test_sc009_determinismo_en_repositorio_nuevo(self):
        with tempfile.TemporaryDirectory() as otro:
            otro = Path(otro)
            fx.construir(otro)
            alcance.proponer(otro)
            self.assertEqual((otro / alcance.ARCHIVO_JSON).read_bytes(), self._json())

    def test_fr013_insumo_cambiado_marca_la_fila(self):
        self._corregir()
        ruta = self.raiz / alcance.INSUMO_ALCANCE
        ruta.write_text(ruta.read_text(encoding="utf-8").replace(
            "Superficie de red", "Superficie de red ampliada"), encoding="utf-8")
        alcance.proponer(self.raiz)
        fila = [f for f in alcance.cargar(self.raiz)["filas"] if f["id"] == self.cifrado["id"]][0]
        self.assertTrue(fila["insumo_cambio"])
        self.assertEqual(fila["decision"], "excluido")

    def test_fr013_firmado_con_insumos_cambiados_no_se_escribe(self):
        self._corregir()
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        antes = self._json()
        ruta = self.raiz / alcance.INSUMO_ALCANCE
        ruta.write_text(ruta.read_text(encoding="utf-8") + "\n- Nuevo supuesto.\n", encoding="utf-8")
        with self.assertRaises(alcance.AlcanceError) as ctx:
            alcance.proponer(self.raiz)
        self.assertEqual(ctx.exception.codigo, 4)
        self.assertEqual(antes, self._json())
        self.assertEqual(alcance.estado_efectivo(self.raiz), "firmado")

    def test_firmado_sin_cambios_sigue_firmado(self):
        self._corregir()
        alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        alcance.proponer(self.raiz)
        self.assertEqual(alcance.estado_efectivo(self.raiz), "firmado")

    def test_fr004_autor_y_firmante_sin_direcciones_de_red(self):
        self._corregir(autor="Auditor 192.0.2.50")
        alcance.revisar(self.raiz, "Revisor 192.0.2.51", "Revisión")
        reg = alcance.firmar(self.raiz, "Firmante 192.0.2.52", "Alcance revisado completo")
        for nombre in (alcance.ARCHIVO_JSON, alcance.ARCHIVO_MD, alcance.ARCHIVO_FIRMA):
            self.assertNotIn("192.0.2.", (self.raiz / nombre).read_text(encoding="utf-8"), nombre)
        self.assertIn(alcance.REMISION_RED, reg["firmante"])

    def test_firma_guarda_pendientes(self):
        self._corregir()
        reg = alcance.firmar(self.raiz, "Auditor Sintético", "Alcance revisado completo")
        guardado = json.loads((self.raiz / alcance.ARCHIVO_FIRMA).read_text(encoding="utf-8"))
        self.assertEqual(guardado["pendientes_al_firmar"], reg["pendientes_al_firmar"])
        self.assertEqual(reg["pendientes_al_firmar"], fx.VACIOS_FIXTURE_COMPLETO - 1)


if __name__ == "__main__":
    unittest.main()
