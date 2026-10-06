"""Verifica la calculadora CVSS v3.1 contra vectores de puntaje conocido."""
import unittest

from c4a import cvss


class TestCvss(unittest.TestCase):
    def test_critical_unchanged(self):
        v = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        self.assertEqual(cvss.base_score(v), 9.8)
        self.assertEqual(cvss.severity_rating(9.8), "CRITICAL")

    def test_critical_scope_changed(self):
        v = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
        self.assertEqual(cvss.base_score(v), 10.0)

    def test_none(self):
        v = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N"
        self.assertEqual(cvss.base_score(v), 0.0)
        self.assertEqual(cvss.severity_rating(0.0), "NONE")

    def test_medium_example(self):
        # Verificación TLS desactivada (vector usado por el detector crypto)
        v = "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N"
        score = cvss.base_score(v)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 10.0)

    def test_incomplete_raises(self):
        with self.assertRaises(ValueError):
            cvss.base_score("CVSS:3.1/AV:N/AC:L")

    def test_rating_boundaries(self):
        self.assertEqual(cvss.severity_rating(3.9), "LOW")
        self.assertEqual(cvss.severity_rating(4.0), "MEDIUM")
        self.assertEqual(cvss.severity_rating(6.9), "MEDIUM")
        self.assertEqual(cvss.severity_rating(7.0), "HIGH")
        self.assertEqual(cvss.severity_rating(9.0), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
