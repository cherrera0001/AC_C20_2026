"""S02 — Códigos de salida del subcomando `registro` (contracts/cli-registro.md), sobre insumos SINTÉTICOS."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import registro_fixtures as fx
from c4a import registro
from c4a.cli import main

A = "Auditor Sintético"


def _correr(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        codigo = main(["registro", *args])
    return codigo, out.getvalue()


class TestCliRegistro(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        fx.construir(self.raiz)
        self.r = str(self.raiz)
        self.dom = fx.fila(self.raiz, "control:1")

    def tearDown(self):
        self._tmp.cleanup()

    def aportar(self, nombre, *extra):
        doc = fx.evidencia(self.raiz, nombre)
        return _correr("aportar", "--raiz", self.r, "--activo", fx.ACTIVO, "--dominio", self.dom, "--afirmacion",
                       "Hecho sintético", "--resultado", "positivo", "--evidencia", str(doc), "--tipo", "documental",
                       "--fecha-recoleccion", fx.DIA, "--autor", A, *extra)

    def test_codigos_de_salida(self):
        self.assertEqual(_correr("verificar", "--raiz", self.r)[0], 2)          # falta el registro
        self.assertEqual(_correr("abrir", "--raiz", self.r)[0], 0)
        self.assertEqual(self.aportar("a.txt", "--origen", "del ejercicio")[0], 0)
        codigo, salida = self.aportar("b.txt")                                  # rechazo anotado
        self.assertEqual(codigo, 0)
        self.assertIn(registro.RECHAZO_ORIGEN, salida)
        self.assertEqual(_correr("aportar", "--raiz", self.r, "--activo", fx.ACTIVO, "--dominio", self.dom,
                                 "--afirmacion", "x", "--resultado", "positivo", "--evidencia",
                                 str(self.raiz / "no-existe.txt"), "--tipo", "documental",
                                 "--fecha-recoleccion", fx.DIA, "--autor", A, "--origen", "o")[0], 2)
        self.assertEqual(_correr("firmar", "--raiz", self.r, "--firmante", A, "--motivo", "m")[0], 1)  # borrador
        hecho = next(e["id"] for e in registro.cargar(self.raiz)["entradas"] if e["clase"] == registro.HECHO)
        self.assertEqual(_correr("corregir", "--raiz", self.r, "--entrada", hecho, "--campo", "motivo",
                                 "--valor", "x", "--motivo", " ", "--autor", A)[0], 1)              # sin motivo
        self.assertEqual(_correr("descartar", "--raiz", self.r, "--entrada", "H-0000000000",
                                 "--motivo", "m", "--autor", A)[0], 1)                              # inexistente
        self.assertEqual(_correr("corregir", "--raiz", self.r, "--entrada", hecho, "--campo", "resultado",
                                 "--valor", "inconcluso", "--motivo", "m", "--autor", A)[0], 0)
        self.assertEqual(_correr("descartar", "--raiz", self.r, "--entrada", hecho, "--motivo", "m", "--autor", A)[0], 0)
        self.assertEqual(_correr("restablecer", "--raiz", self.r, "--entrada", hecho, "--motivo", "m", "--autor", A)[0], 0)
        self.assertEqual(_correr("revisar", "--raiz", self.r, "--autor", A, "--motivo", "m")[0], 0)
        self.assertEqual(_correr("firmar", "--raiz", self.r, "--firmante", A, "--motivo", "m")[0], 0)
        self.assertEqual(_correr("verificar", "--raiz", self.r)[0], 0)
        codigo, salida = _correr("entregar", "--raiz", self.r, "--json")
        self.assertEqual(codigo, 0)
        self.assertTrue(json.loads(salida)["firmado"])
        fx.decidir(self.raiz, self.dom, "excluido")                             # el alcance cambia
        self.assertEqual(_correr("abrir", "--raiz", self.r)[0], 4)
        ruta = self.raiz / registro.ARCHIVO_JSON
        ruta.write_bytes(ruta.read_bytes().replace(b"Hecho", b"Hecha", 1))      # alteración
        self.assertEqual(_correr("verificar", "--raiz", self.r)[0], 3)


if __name__ == "__main__":
    unittest.main()
