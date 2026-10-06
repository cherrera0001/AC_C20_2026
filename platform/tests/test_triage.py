"""Pruebas del triaje persistente (revisión humana entre corridas)."""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator, triage


FIXTURE = {
    "Dockerfile": "FROM ubuntu:latest\nCMD [\"/app\"]\n",
    "app.py": "url = 'http://api.example.com/v1'\n",
}


def _setup(td: Path):
    target = td / "target"
    out = td / "out"
    target.mkdir()
    out.mkdir()
    for rel, content in FIXTURE.items():
        (target / rel).write_text(content, encoding="utf-8")
    cfgp = td / "a.json"
    cfgp.write_text(json.dumps({
        "audit_name": "triage-test", "auditor": "t",
        "target": str(target), "output_root": str(out),
        "normativas": ["ISO-27001"], "detectors": ["all"],
        "scope": {"read_only": True},
    }), encoding="utf-8")
    return cfgp


class TestTriage(unittest.TestCase):
    def test_false_positive_suppresses(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cfgp = _setup(td)
            cfg = config_mod.load(cfgp)

            run1, findings1, _ = orchestrator.run_audit(cfg)
            self.assertGreater(len(findings1), 0)
            target_id = findings1[0].id
            open_before = run1.result_summary["triage"]["open"]

            # un humano marca el primer hallazgo como falso positivo
            triage.append_decision(cfg, target_id, "false-positive", "patrón de prueba", "cristobal")

            cfg2 = config_mod.load(cfgp)
            run2, findings2, _ = orchestrator.run_audit(cfg2)
            marked = {f.id: f for f in findings2}[target_id]
            self.assertEqual(marked.status, "false-positive")
            self.assertEqual(run2.result_summary["triage"]["false-positive"], 1)
            self.assertEqual(run2.result_summary["triage"]["open"], open_before - 1)

            # queda trazado en el registro de triaje
            self.assertTrue((cfg.output_root / "04_informe" / "registro_triaje.md").exists())

    def test_invalid_decision_raises(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cfgp = _setup(td)
            cfg = config_mod.load(cfgp)
            with self.assertRaises(ValueError):
                triage.append_decision(cfg, "F-x", "no-existe", "x", "y")

    def test_accepted_risk_stays_open_but_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cfgp = _setup(td)
            cfg = config_mod.load(cfgp)
            run1, findings1, _ = orchestrator.run_audit(cfg)
            fid = findings1[0].id
            triage.append_decision(cfg, fid, "accepted-risk", "lo asume el dueño", "gc")
            cfg2 = config_mod.load(cfgp)
            _, findings2, _ = orchestrator.run_audit(cfg2)
            f = {x.id: x for x in findings2}[fid]
            self.assertEqual(f.status, "accepted-risk")
            # accepted-risk NO es falso positivo: sigue contando como abierto
            self.assertIn(f, triage.open_findings(findings2))


if __name__ == "__main__":
    unittest.main()
