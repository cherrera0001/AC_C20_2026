"""Invariante de la compuerta (docs/DECISION_TESIS_CANONICA.md): el núcleo no abre conexiones
de red hacia un objetivo. La única salida de red permitida es la consulta de paquetes a OSV."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "c4a"
URL_PERMITIDA = "https://api.osv.dev/v1/query"


class TestSinRedObjetivo(unittest.TestCase):
    def _fuentes(self):
        return [p for p in RAIZ.rglob("*.py")]

    def test_ningun_modulo_usa_sockets(self):
        for p in self._fuentes():
            texto = p.read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"^\s*(import socket|from socket)", msg=str(p))

    def test_unica_url_de_red_en_codigo_es_osv(self):
        # Solo se consideran URLs usadas como destino de una petición (literal en Request/urlopen).
        patron = re.compile(r"""(?:Request|urlopen)\(\s*\(?\s*["'](https?://[^"']+)["']""")
        encontradas = set()
        for p in self._fuentes():
            encontradas.update(patron.findall(p.read_text(encoding="utf-8")))
        self.assertEqual(encontradas, {URL_PERMITIDA})


if __name__ == "__main__":
    unittest.main()
