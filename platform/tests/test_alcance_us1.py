"""S01 · US1 — Proponer el alcance con insumos incompletos (insumos SINTÉTICOS)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

import alcance_fixtures as fx
from c4a import alcance
from c4a.util import sha256_file

_RE_RED = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
_RE_PUERTO = re.compile(r"(?i)\b(?:puerto|port)s?\s*:?\s*\d+|\b\d{1,5}/(?:tcp|udp)\b")
_RE_COMANDO = re.compile(r"(?i)\b(?:nmap|msfconsole|hydra|sqlmap|nikto|curl|wget)\b|\s-s[A-Z]\b")
_RE_CREDENCIAL = re.compile(r"(?i)\b(?:password|passwd|contraseña|token|api[_-]?key)\s*[:=]")
_RE_CUMPLIMIENTO = re.compile(r"\b(?:cumple|parcial|no-cumple|no-evaluado|no-aplica)\b")


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def filas(self, **kw):
        fx.construir(self.raiz, **kw)
        return alcance.proponer(self.raiz)["filas"]

    def fila(self, filas, tipo, clave_prefijo=""):
        return [f for f in filas if f["tipo"] == tipo and f["clave"].startswith(clave_prefijo)]


class TestUS1(Base):
    def test_esc1_declarado_con_fuente_y_exclusion_de_activos_pendiente(self):
        filas = self.filas()
        activo = self.fila(filas, "activo")[0]
        self.assertEqual(activo["decision"], "incluido")
        self.assertTrue(activo["fuente"].startswith("scope/alcance.md §4"))
        iso = self.fila(filas, "marco", "iso")[0]
        self.assertEqual(iso["atributos"]["version"], "2022")
        self.assertTrue(self.fila(filas, "dominio"))
        excl = self.fila(filas, "exclusion", "activos-no-listados")[0]
        self.assertEqual(excl["decision"], alcance.PENDIENTE)

    def test_esc2_sin_documento_de_alcance(self):
        filas = self.filas(alcance=False)
        contenido = alcance.cargar(self.raiz)
        self.assertTrue(any("scope/alcance.md" in a for a in contenido["avisos"]))
        for t in ("activo", "dominio", "exclusion"):
            for f in self.fila(filas, t):
                if f["fuente"].startswith("scope/alcance.md") or f["fuente"] == "sin fuente":
                    self.assertEqual(f["decision"], alcance.PENDIENTE, f)
        activo = self.fila(filas, "activo")[0]
        self.assertEqual(activo["valor"], "")

    def test_esc3_mas_de_un_activo(self):
        activo = self.fila(self.filas(hosts=2), "activo")[0]
        self.assertEqual(activo["decision"], alcance.PENDIENTE)
        self.assertIn("un solo activo", activo["observacion"])

    def test_esc3_ningun_activo(self):
        activo = self.fila(self.filas(hosts=0), "activo")[0]
        self.assertEqual(activo["decision"], alcance.PENDIENTE)

    def test_esc4_activo_por_tipo_y_rol_sin_direccion(self):
        activo = self.fila(self.filas(), "activo")[0]
        self.assertIn("MaquinaSintetica", activo["valor"])
        self.assertIn("tipo: host", activo["valor"])
        self.assertIn("rol:", activo["valor"])
        self.assertIsNone(_RE_RED.search(activo["valor"]))

    def test_sc001_n_vacios_n_pendientes_sin_valores_inventados(self):
        filas = self.filas()
        self.assertEqual(sum(alcance.es_pendiente(f) for f in filas), fx.VACIOS_FIXTURE_COMPLETO)
        parte = self.fila(filas, "parte")[0]
        self.assertEqual(parte["valor"], "")
        ventana = self.fila(filas, "compuerta", "ventana")[0]
        self.assertIsNone(ventana["atributos"]["inicio"])
        self.assertIsNone(ventana["atributos"]["fin"])

    def test_sc002_fuente_y_aprobacion_en_todas_las_filas(self):
        for f in self.filas():
            self.assertTrue(f["fuente"], f)
            self.assertIn(f["estado_aprobacion"], alcance.APROBACION)

    def test_sc003_una_sola_seccion_de_pendientes_con_su_conteo(self):
        filas = self.filas()
        md = (self.raiz / alcance.ARCHIVO_MD).read_text(encoding="utf-8")
        encabezados = re.findall(r"^## Pendientes \((\d+)\)$", md, re.MULTILINE)
        self.assertEqual(len(encabezados), 1)
        self.assertEqual(int(encabezados[0]), sum(alcance.es_pendiente(f) for f in filas))

    def test_sc005_sin_red_puertos_comandos_ni_credenciales(self):
        self.filas()
        for nombre in (alcance.ARCHIVO_JSON, alcance.ARCHIVO_MD):
            texto = (self.raiz / nombre).read_text(encoding="utf-8")
            for patron in (_RE_RED, _RE_PUERTO, _RE_COMANDO, _RE_CREDENCIAL):
                self.assertIsNone(patron.search(texto), f"{nombre}: {patron.pattern}")

    def test_sc010_sin_estados_de_cumplimiento(self):
        self.filas()
        for nombre in (alcance.ARCHIVO_JSON, alcance.ARCHIVO_MD):
            texto = (self.raiz / nombre).read_text(encoding="utf-8")
            self.assertIsNone(_RE_CUMPLIMIENTO.search(texto), nombre)

    def test_sc008_fuentes_citadas_existen(self):
        filas = self.filas()
        for f in filas:
            if f["fuente"] == "sin fuente" or f["fuente"].startswith(alcance.CONSTITUCION):
                continue
            archivo, _, seccion = f["fuente"].partition(" §")
            archivo = archivo.split(" ")[0]
            texto = (self.raiz / archivo).read_text(encoding="utf-8")
            n = re.match(r"\d+", seccion)
            if n:
                self.assertRegex(texto, rf"(?m)^## {n.group(0)}\. ", f["fuente"])

    def test_fr009_insumos_no_cambian(self):
        fx.construir(self.raiz)
        antes = [sha256_file(self.raiz / r) for r in (alcance.INSUMO_ALCANCE, alcance.INSUMO_AUTORIZACION)]
        alcance.proponer(self.raiz)
        despues = [sha256_file(self.raiz / r) for r in (alcance.INSUMO_ALCANCE, alcance.INSUMO_AUTORIZACION)]
        self.assertEqual(antes, despues)

    def test_fr017_solo_archivos_nuevos_en_scope(self):
        fx.construir(self.raiz)
        alcance.proponer(self.raiz)
        creados = sorted(p.relative_to(self.raiz).as_posix() for p in self.raiz.rglob("*") if p.is_file())
        self.assertEqual(creados, sorted([alcance.INSUMO_ALCANCE, alcance.INSUMO_AUTORIZACION,
                                          alcance.ARCHIVO_JSON, alcance.ARCHIVO_MD]))

    def test_fr005_marcos_de_referencia(self):
        filas = self.filas()
        estados = {f["clave"]: f["atributos"]["estado_herramienta"] for f in self.fila(filas, "marco")}
        self.assertEqual(estados["iso-27001"], "implementado parcialmente")
        self.assertEqual(estados["nist-csf"], "mencionado")
        self.assertEqual(estados["cis-controls"], "mencionado")
        nist = self.fila(filas, "marco", "nist")[0]
        self.assertEqual(nist["decision"], alcance.PENDIENTE)

    def test_marco_sin_version_queda_pendiente(self):
        iso = self.fila(self.filas(version_iso=False), "marco", "iso")[0]
        self.assertEqual(iso["decision"], alcance.PENDIENTE)
        self.assertEqual(iso["atributos"]["version"], alcance.PENDIENTE)

    def test_edge_version_distinta_de_la_referencia(self):
        fx.construir(self.raiz)
        ruta = self.raiz / alcance.INSUMO_ALCANCE
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("ISO/IEC 27001:2022", "ISO/IEC 27001:2013"),
                        encoding="utf-8")
        iso = self.fila(alcance.proponer(self.raiz)["filas"], "marco", "iso")[0]
        self.assertEqual(iso["atributos"]["version"], "2013")
        self.assertEqual(iso["atributos"]["version_referencia"], "2022")
        self.assertIn("distinta de la de referencia", iso["observacion"])

    def test_fr006_obligaciones_en_validar_y_antecedente(self):
        for f in self.fila(self.filas(), "obligacion"):
            self.assertEqual(f["marca_legal"], alcance.VALIDAR)
            self.assertIsNone(f["atributos"]["articulo"])
            self.assertIn("antecedente", f["atributos"])

    def test_fr007_dominio_sin_motivo_conserva_lo_declarado(self):
        for f in self.fila(self.filas(), "dominio"):
            self.assertEqual(f["decision"], alcance.PENDIENTE)
            self.assertEqual(f["declarado"], "incluido")

    def test_edge_politicas_y_cifrado(self):
        filas = self.filas()
        org = [f for f in self.fila(filas, "dominio") if "Organizacionales" in f["valor"]][0]
        self.assertIn("no se acredita con una prueba técnica", org["observacion"])
        cif = [f for f in self.fila(filas, "regla") if "cifrada" in f["valor"]][0]
        self.assertEqual(cif["decision"], alcance.PENDIENTE)
        self.assertIn("no equivale a cifrado", cif["observacion"])

    def test_esquema_de_ids(self):
        filas = self.filas()
        ids = [f["id"] for f in filas]
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertRegex(i, r"^A-[0-9a-f]{10}$")
        contenido = json.loads((self.raiz / alcance.ARCHIVO_JSON).read_text(encoding="utf-8"))
        self.assertEqual(contenido["producto"], alcance.PRODUCTO)


if __name__ == "__main__":
    unittest.main()
