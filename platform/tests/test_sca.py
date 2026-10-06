"""Pruebas de la integración SCA: parsers deterministas, sin red."""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import sca
from c4a.evidence import EvidenceStore


OSV_SCANNER = json.dumps({
    "results": [{
        "source": {"path": "/t/package-lock.json"},
        "packages": [{
            "package": {"name": "lodash", "version": "4.17.4", "ecosystem": "npm"},
            "vulnerabilities": [{
                "id": "GHSA-jf85-cpcp-j695",
                "aliases": ["CVE-2019-10744"],
                "summary": "Prototype pollution in lodash",
                "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}],
                "references": [{"url": "https://example.test/advisory"}],
            }],
        }],
    }],
})

OSV_API = json.dumps({
    "vulns": [{
        "id": "GHSA-vh95-rmgr-6w4m",
        "aliases": ["CVE-2020-7598"],
        "summary": "minimist prototype pollution",
        "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L"}],
        "references": [{"url": "https://example.test/minimist"}],
    }],
})


class TestScaParsers(unittest.TestCase):
    def test_osv_scanner(self):
        refs = sca.parse_osv_scanner(OSV_SCANNER)
        self.assertEqual(len(refs), 1)
        r = refs[0]
        self.assertEqual(r.cve_id, "CVE-2019-10744")   # se prefiere el alias CVE
        self.assertEqual(r.package, "lodash")
        self.assertEqual(r.ecosystem, "npm")
        self.assertTrue(r.cvss_vector.startswith("CVSS:3.1"))

    def test_osv_api(self):
        refs = sca.parse_osv_api("minimist", "1.2.0", "npm", "package-lock.json", OSV_API)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].cve_id, "CVE-2020-7598")

    def test_to_findings_sets_cve_and_cvss(self):
        refs = sca.parse_osv_scanner(OSV_SCANNER)
        with tempfile.TemporaryDirectory() as td:
            store = EvidenceStore("t", Path(td), Path(td))
            findings = sca.to_findings(refs, store, {"queried_at": "2026-01-01T00:00:00Z"})
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f.cve, ["CVE-2019-10744"])
        self.assertIn("CWE-1395", f.cwe)
        self.assertEqual(f.cvss["base_score"], 9.8)
        self.assertTrue(f.source.startswith("sca:"))

    def test_npm_lock_extraction(self):
        lock = json.dumps({"packages": {
            "": {"name": "root"},
            "node_modules/lodash": {"version": "4.17.4"},
            "node_modules/express": {"version": "4.18.2"},
        }})
        pkgs = sca._npm_from_lock(lock)
        self.assertIn(("lodash", "4.17.4"), pkgs)
        self.assertIn(("express", "4.18.2"), pkgs)

    def test_enrich_matches_package_in_evidence(self):
        from c4a.model import Evidence, Finding
        refs = sca.parse_osv_scanner(OSV_SCANNER)  # lodash → CVE-2019-10744
        ev = Evidence(
            id="E1", type="dependency", source="file:package.json",
            location="package.json", collected_at="t", sha256="x",
            responsible_role="r", scope="in-scope", status="collected",
            result="", description="", relevance="",
            excerpt_masked="lodash: ^4.17.4 [dependencies]\nexpress: ^4.0.0",
        )
        f = Finding(
            id="F1", title="deps", description="dependencias sin fijar",
            component="package.json", asset="package.json", scope="in-scope",
            finding_type="technical", severity="MEDIO", probability="media",
            impact="medio", status="detected", evidence=["E1"], source="dependencies",
        )
        sca.enrich_dependency_findings([f], refs, {"E1": ev})
        self.assertIn("CVE-2019-10744", f.cve)

    def test_enrich_no_false_match(self):
        from c4a.model import Evidence, Finding
        refs = sca.parse_osv_scanner(OSV_SCANNER)  # lodash
        ev = Evidence(
            id="E1", type="dependency", source="f", location="package.json",
            collected_at="t", sha256="x", responsible_role="r", scope="in-scope",
            status="collected", result="", description="", relevance="",
            excerpt_masked="express: ^4.0.0\nreact: ^18.0.0",
        )
        f = Finding(
            id="F1", title="deps", description="x", component="package.json",
            asset="package.json", scope="in-scope", finding_type="technical",
            severity="MEDIO", probability="media", impact="medio", status="detected",
            evidence=["E1"], source="dependencies",
        )
        sca.enrich_dependency_findings([f], refs, {"E1": ev})
        self.assertEqual(f.cve, [])  # lodash no está en la evidencia → no se correlaciona

    def test_disabled_by_default(self):
        from c4a import config as cm
        from c4a.scope import ScopeManager
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "t").mkdir()
            cfgp = td / "a.json"
            cfgp.write_text(json.dumps({"target": "t", "output_root": "t"}), encoding="utf-8")
            cfg = cm.load(cfgp)
            mgr = sca.SCAManager(cfg)
            self.assertFalse(mgr.enabled)
            refs, meta = mgr.run(ScopeManager(cfg))
            self.assertEqual(refs, [])
            self.assertEqual(meta["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
