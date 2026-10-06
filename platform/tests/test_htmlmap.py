"""Pruebas del mapa HTML (M1): autocontenido, escapado y navegable."""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator

FIXTURE = {
    # el extracto de evidencia traerá caracteres HTML peligrosos
    "app.py": 'url = "http://x.test/<script>alert(1)</script>&y=1"\n',
    "Dockerfile": "FROM ubuntu:latest\nCMD [\"/a\"]\n",
}


def _run(td: Path):
    target = td / "t"; out = td / "o"
    target.mkdir(); out.mkdir()
    for rel, content in FIXTURE.items():
        (target / rel).write_text(content, encoding="utf-8")
    cfgp = td / "a.json"
    cfgp.write_text(json.dumps({
        "audit_name": "Mapa <test> & demo", "auditor": "t",
        "target": str(target), "output_root": str(out),
        "normativas": ["ISO-27001"], "detectors": ["all"],
        "scope": {"read_only": True},
    }), encoding="utf-8")
    cfg = config_mod.load(cfgp)
    run, findings, _ = orchestrator.run_audit(cfg)
    return cfg, run, findings


class TestHtmlMap(unittest.TestCase):
    def test_written_selfcontained_and_escaped(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, run, findings = _run(Path(td))
            p = cfg.output_root / "04_informe" / "mapa.html"
            self.assertTrue(p.exists())
            doc = p.read_text(encoding="utf-8")

            # autocontenido: sin recursos externos
            self.assertNotIn("<script src", doc)
            self.assertNotIn("http://cdn", doc)
            self.assertNotIn("https://cdn", doc)
            self.assertNotIn("<link", doc)

            # estructura presente
            self.assertIn("Mapa de controles".split()[0], doc)  # "Matriz"/"Mapa"
            self.assertIn("Matriz de controles", doc)
            self.assertIn(run.run_id, doc)
            self.assertIn(findings[0].id or "F-", doc)

            # el código auditado se escapa: nada de <script> crudo del extracto
            self.assertNotIn("<script>alert(1)</script>", doc)
            self.assertIn("&lt;script&gt;alert(1)", doc)
            # el título con < & también escapado
            self.assertIn("Mapa &lt;test&gt; &amp; demo", doc)

    def test_handles_empty_findings(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            target = td / "t"; out = td / "o"
            target.mkdir(); out.mkdir()
            (target / "readme.md").write_text("# nada que ver\n", encoding="utf-8")
            cfgp = td / "a.json"
            cfgp.write_text(json.dumps({
                "audit_name": "vacio", "auditor": "t",
                "target": str(target), "output_root": str(out),
                "normativas": ["ISO-27001"], "detectors": ["all"],
                "scope": {"read_only": True},
            }), encoding="utf-8")
            cfg = config_mod.load(cfgp)
            orchestrator.run_audit(cfg)
            p = cfg.output_root / "04_informe" / "mapa.html"
            self.assertTrue(p.exists())
            self.assertIn("<!doctype html>", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
