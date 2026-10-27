"""Verifica el bloque CVSS v4.0 contra vectores de puntaje conocido y sin el paquete opcional."""
import unittest
from unittest import mock

from c4a import cvss4

CRITICO = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N"
NULO = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N"
ALTO_SOLO_CONF = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N"


@unittest.skipUnless(cvss4.disponible(), "requiere el paquete opcional 'cvss'")
class TestCvss4Con(unittest.TestCase):
    def test_critico(self):
        self.assertEqual(cvss4.base_score(CRITICO), 9.3)
        b = cvss4.evaluate(CRITICO)
        self.assertEqual(b["version"], "4.0")
        self.assertEqual(b["base_severity"], "Critical")
        self.assertNotIn("motivo", b)

    def test_sin_impacto(self):
        self.assertEqual(cvss4.base_score(NULO), 0.0)

    def test_solo_confidencialidad_alta(self):
        self.assertEqual(cvss4.base_score(ALTO_SOLO_CONF), 8.7)

    def test_vector_sin_prefijo_se_rechaza(self):
        with self.assertRaises(ValueError):
            cvss4.evaluate("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")


class TestCvss4Sin(unittest.TestCase):
    def test_sin_paquete_no_inventa_puntaje(self):
        with mock.patch.object(cvss4, "disponible", return_value=False):
            self.assertIsNone(cvss4.base_score(CRITICO))
            b = cvss4.evaluate(CRITICO)
        self.assertIsNone(b["base_score"])
        self.assertNotIn("base_severity", b)
        self.assertIn("no calculado", b["motivo"])


if __name__ == "__main__":
    unittest.main()
