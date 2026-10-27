"""Pruebas del detector php-shell (ejecución remota y webshells).

Insumos SINTÉTICOS (principio III): los archivos PHP/Python son fixtures de
texto, no código del objetivo; su resultado demuestra la herramienta.
"""
import json
import tempfile
import unittest
from pathlib import Path

from c4a import config as config_mod
from c4a import orchestrator

FIXTURE = {
    # php2shell clásico: eval con $_GET → SÍ, confianza direct
    "shell_eval.php": "<?php eval($_GET['c']); ?>\n",
    # system con entrada → SÍ
    "cmd.php": "<?php system($_POST['x']); ?>\n",
    # comentario con el mismo patrón → NO
    "comentario.php": "<?php // eval($_GET['c']); ?>\n",
    # marcador de supresión → NO
    "ignorado.php": "<?php eval($_GET['c']); // c4a:ignore\n",
    # llamada peligrosa sin entrada en la línea → NO (no alcanzable por línea)
    "sin_entrada.php": "<?php\n$x = 'ls';\nsystem($x);\n",
    # include con entrada → SÍ (LFI)
    "include_lfi.php": "<?php include($_GET['p']); ?>\n",
    # unserialize con entrada → SÍ
    "deser.php": "<?php $o = unserialize($_COOKIE['s']); ?>\n",
    # upload → SÍ
    "upload.php": "<?php move_uploaded_file($_FILES['f']['tmp_name'], 'u/'.$_FILES['f']['name']); ?>\n",
    # ofuscación → SÍ
    "obf.php": "<?php eval(base64_decode($_POST['d']));\n$y = 'str';\n$$y('x');\n",
    # python2shell: subprocess shell=True con entrada → SÍ
    "py_shell.py": "import subprocess\nsubprocess.Popen(input(), shell=True)\n",
    # eval python con entrada → SÍ
    "py_eval.py": "eval(request.args['q'])\n",
    # pickle con entrada → SÍ
    "py_pickle.py": "import pickle\npickle.loads(request.data)\n",
    # python limpio → NO
    "limpio.py": "import json\njson.loads('{}')\n",
    # archivo no código → ignorado
    "notas.txt": "eval($_GET['c'])\n",
}


def _run(td: Path):
    target = td / "t"
    out = td / "o"
    target.mkdir(); out.mkdir()
    for rel, content in FIXTURE.items():
        (target / rel).write_text(content, encoding="utf-8")
    cfgp = td / "a.json"
    cfgp.write_text(json.dumps({
        "audit_name": "php-shell-fixture", "auditor": "auditor sintetico",
        "target": str(target), "output_root": str(out),
        "normativas": ["ISO-27001"], "detectors": ["php-shell"],
        "scope": {"read_only": True},
    }), encoding="utf-8")
    cfg = config_mod.load(cfgp)
    _, findings, _ = orchestrator.run_audit(cfg)
    return findings


class TestPhpShellDetector(unittest.TestCase):
    def test_reglas_y_falsos_positivos(self):
        with tempfile.TemporaryDirectory() as td:
            findings = _run(Path(td))
        por_componente = {}
        for f in findings:
            por_componente.setdefault(f.component, []).append(f.title)

        self.assertIn("shell_eval.php", por_componente)
        self.assertTrue(any("Ejecución de comandos o código PHP" in t
                            for t in por_componente["shell_eval.php"]))
        self.assertIn("cmd.php", por_componente)
        self.assertTrue(any("Inclusión de archivo" in t for t in por_componente["include_lfi.php"]))
        self.assertTrue(any("unserialize" in t for t in por_componente["deser.php"]))
        self.assertTrue(any("Carga de archivos" in t for t in por_componente["upload.php"]))
        self.assertTrue(any("Ofuscación" in t for t in por_componente["obf.php"]))
        self.assertTrue(any("Ejecución de comandos o código Python" in t
                            for t in por_componente["py_shell.py"]))
        self.assertIn("py_eval.py", por_componente)
        self.assertTrue(any("Deserialización insegura" in t
                            for t in por_componente["py_pickle.py"]))

        # controles de falso positivo
        self.assertNotIn("comentario.php", por_componente)
        self.assertNotIn("ignorado.php", por_componente)
        self.assertNotIn("sin_entrada.php", por_componente)
        self.assertNotIn("limpio.py", por_componente)
        self.assertNotIn("notas.txt", por_componente)

    def test_confianza_directa_con_entrada(self):
        with tempfile.TemporaryDirectory() as td:
            findings = _run(Path(td))
        eval_f = next(f for f in findings if f.component == "shell_eval.php")
        self.assertEqual(eval_f.confidence, "direct")
        self.assertTrue(eval_f.cwe)
        # la plataforma deriva la severidad final del vector (gestor de riesgo)
        self.assertEqual(eval_f.severity, "CRITICO")
        self.assertTrue(eval_f.cvss)
        # el extracto quedó en la evidencia, enmascarado y con línea
        self.assertTrue(eval_f.evidence)

    def test_catalogo_incluye_detector(self):
        from c4a.detectors import catalog
        ids = [d["id"] for d in catalog()]
        self.assertIn("php-shell", ids)


if __name__ == "__main__":
    unittest.main()
