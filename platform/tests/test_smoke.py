"""Ciclo de humo de punta a punta sobre un repositorio de prueba.

Crea un objetivo mínimo con problemas conocidos, corre la auditoría completa y
verifica que: hay hallazgos, se escriben los entregables, y una segunda corrida
sobre el mismo objetivo produce el MISMO result_hash (reproducibilidad).
"""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator
from c4a import reproduction


FIXTURE = {
    "Dockerfile": "FROM ubuntu:latest\nRUN curl http://x.test/install.sh | sh\nCMD [\"/app\"]\n",
    "package.json": json.dumps({
        "name": "fx", "dependencies": {"left-pad": "^1.0.0", "express": "latest"}
    }),
    ".env": "API_TOKEN=abc123secretvalue\nDB_PASSWORD=supersecret123\n",
    "app.py": "import hashlib\nh = hashlib.md5(b'x')\nurl = 'http://api.example.com/v1'\n",
    ".github/workflows/ci.yml": "on: push\njobs:\n  b:\n    steps:\n      - uses: actions/checkout@v4\n",
}


def _make_target(root: Path):
    for rel, content in FIXTURE.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


class TestSmoke(unittest.TestCase):
    def test_full_cycle_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            target = td / "target"
            out = td / "out"
            target.mkdir()
            out.mkdir()
            _make_target(target)

            cfg_path = td / "audit.json"
            cfg_path.write_text(json.dumps({
                "audit_name": "smoke",
                "auditor": "test",
                "target": str(target),
                "output_root": str(out),
                "normativas": ["ISO-27001", "LEY-21663", "LEY-21719", "NIST-800-218", "NIST-CSF"],
                "detectors": ["all"],
                "scope": {"read_only": True, "max_file_bytes": 1000000},
            }), encoding="utf-8")

            cfg = config_mod.load(cfg_path)
            run1, findings1, extra = orchestrator.run_audit(cfg)

            # Hay hallazgos de varias clases
            self.assertGreater(len(findings1), 0)
            kinds = {f.source for f in findings1}
            self.assertIn("secrets-files", kinds)
            self.assertIn("dockerfile", kinds)
            self.assertIn("dependencies", kinds)

            # Entregables escritos
            self.assertTrue((out / "02_evidencia" / "inventario.json").exists())
            self.assertTrue((out / "03_hallazgos" / "matriz_cumplimiento.csv").exists())
            self.assertTrue((out / "04_informe" / "informe_tecnico.md").exists())
            self.assertTrue((out / "04_informe" / "resumen_ejecutivo.md").exists())
            self.assertTrue((out / ".c4a" / "runs.jsonl").exists())

            # Cada hallazgo tiene evidencia y, si es técnico con CVSS, puntaje válido
            for f in findings1:
                self.assertTrue(f.evidence, f"{f.id} sin evidencia")
                if f.cvss:
                    self.assertLessEqual(f.cvss["base_score"], 10.0)

            # Reproducibilidad: segunda corrida, mismo objetivo → mismo result_hash
            cfg2 = config_mod.load(cfg_path)
            run2, _, _ = orchestrator.run_audit(cfg2)
            self.assertEqual(run1.hash, run2.hash)

            # CVE nunca inventada (SCA desactivado en esta config)
            for f in findings1:
                self.assertEqual(f.cve, [])

            # Reproducción POR HALLAZGO: sobre el mismo objetivo, todo reproduce
            rep = reproduction.verify_run(cfg, run1.run_id)
            self.assertGreater(rep["counts"].get("reproduced", 0), 0)
            self.assertEqual(rep["counts"].get("not-reproduced", 0), 0)
            self.assertTrue((out / ".c4a" / "verify" / f"{run1.run_id}.json").exists())

            # Verificar un solo hallazgo también funciona
            one = findings1[0].id
            rep1 = reproduction.verify_run(cfg, run1.run_id, only=one)
            self.assertEqual(len(rep1["results"]), 1)


if __name__ == "__main__":
    unittest.main()
