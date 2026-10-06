"""Pruebas de los controles de falsos positivos (N3):
comentarios, entropía de secretos y marcador c4a:ignore.
"""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator
from c4a.util import is_comment_line, has_ignore_marker, shannon_entropy

FIXTURE = {
    # secreto real de alta entropía → SÍ se marca
    "real_secret.py": 'token = "aB3xZ9qL7mKp2WdF8vNcH1"\n',
    # mismo patrón pero en comentario → NO
    "commented.py": '# token = "aB3xZ9qL7mKp2WdF8vNcH1"\n',
    # baja entropía / marcador → NO
    "weak.py": 'password = "password"\n',
    # con marcador de supresión en línea → NO
    "ignored.py": 'api_key = "aB3xZ9qL7mKp2WdF8vNcH1"  # c4a:ignore\n',
    # endpoint http en código → SÍ (cripto)
    "endpoint.py": 'URL = "http://evil.example.com/api"\n',
    # endpoint http en comentario → NO
    "endpoint_comment.py": '# URL = "http://evil.example.com/api"\n',
}


def _run(td: Path):
    target = td / "t"
    out = td / "o"
    target.mkdir(); out.mkdir()
    for rel, content in FIXTURE.items():
        (target / rel).write_text(content, encoding="utf-8")
    cfgp = td / "a.json"
    cfgp.write_text(json.dumps({
        "audit_name": "fp", "auditor": "t",
        "target": str(target), "output_root": str(out),
        "normativas": ["ISO-27001"], "detectors": ["secrets-files", "crypto-config"],
        "scope": {"read_only": True},
    }), encoding="utf-8")
    cfg = config_mod.load(cfgp)
    _, findings, _ = orchestrator.run_audit(cfg)
    return findings


class TestFalsePositiveControls(unittest.TestCase):
    def test_helpers(self):
        self.assertTrue(is_comment_line("   # algo"))
        self.assertTrue(is_comment_line("// algo"))
        self.assertFalse(is_comment_line("x = 1  # http://a"))
        self.assertTrue(has_ignore_marker("x = 1  # c4a:ignore"))
        self.assertTrue(has_ignore_marker("y # nosec"))
        self.assertGreater(shannon_entropy("aB3xZ9qL7mKp2WdF"), 3.0)
        self.assertLess(shannon_entropy("password"), 3.0)

    def test_detection_respects_controls(self):
        with tempfile.TemporaryDirectory() as td:
            findings = _run(Path(td))
            flagged = {(f.source, f.component) for f in findings}

            self.assertIn(("secrets-files", "real_secret.py"), flagged)
            self.assertIn(("crypto-config", "endpoint.py"), flagged)

            self.assertNotIn(("secrets-files", "commented.py"), flagged)
            self.assertNotIn(("secrets-files", "weak.py"), flagged)
            self.assertNotIn(("secrets-files", "ignored.py"), flagged)
            self.assertNotIn(("crypto-config", "endpoint_comment.py"), flagged)


if __name__ == "__main__":
    unittest.main()
