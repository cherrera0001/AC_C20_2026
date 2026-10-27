"""Detector: ejecución remota y webshells en código PHP y Python del objetivo.

Reglas (detección estática, sin explotación; la severidad final la deriva el
gestor de riesgo y el hallazgo nace REQUIERE-VALIDACION):
  - php-cmd-exec:       system/exec/shell_exec/passthru/popen/proc_open,
                        backticks, eval, assert, preg_replace con /e,
                        create_function, call_user_func con entrada ($_…, argv).
  - php-dynamic-include: include/require con ruta de entrada (CWE-98).
  - php-unserialize:    unserialize( con entrada alcanzable (CWE-502).
  - php-upload:         move_uploaded_file( (superficie de carga; CWE-434).
  - php-obfuscation:    base64_decode/gzinflate/str_rot13 junto a eval/assert,
                        o llamadas a función por nombre dinámico (webshell).
  - py-cmd-exec:        os.system, subprocess con shell=True, eval/exec con
                        entrada (CWE-78/CWE-94).
  - py-insecure-deser:  pickle.loads / marshal.loads con entrada (CWE-502).

El detector OBSERVA: dos niveles de confianza. «direct» cuando la llamada
peligrosa comparte línea con una fuente de entrada; «indirect» cuando no, para
que el auditor valide el alcance real.
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from ..model import Finding
from ..util import has_ignore_marker, is_comment_line, redact_line
from .base import Detector, DetectorContext, build_finding

_SUFFIXES = (".php", ".inc", ".phtml", ".py", ".pyw")
_MAX_HITS = 12

# Fuentes de entrada que hacen alcanzable una llamada peligrosa.
_INPUT = re.compile(r"(\$_(GET|POST|REQUEST|COOKIE|FILES|SERVER)|\$argv|argv\[|input\(|request\.|sys\.argv)")

_PHP_CMD = re.compile(
    r"""(?ix)\b(
        system|exec|shell_exec|passthru|popen|proc_open|
        eval|assert|create_function|
        preg_replace|call_user_func(_array)?|preg_filter
    )\s*\("""
)
_PHP_BACKTICK = re.compile(r"(?s)`[^`]+`")
_PHP_PREG_E = re.compile(r"(?i)preg_replace\s*\(\s*['\"]/[^'\"]*/e")
_PHP_INCLUDE = re.compile(r"""(?i)\b(include|include_once|require|require_once)\s*[ (].*(\$_(GET|POST|REQUEST)|\$[a-zA-Z_]+)""")
_PHP_UNSERIALIZE = re.compile(r"\bunserialize\s*\(")
_PHP_UPLOAD = re.compile(r"\bmove_uploaded_file\s*\(")
_PHP_OBF = re.compile(r"(?i)(base64_decode|gzinflate|gzuncompress|str_rot13)\s*\(")
_PHP_DYNAMIC_CALL = re.compile(r"(\$\$?[a-zA-Z_][a-zA-Z0-9_]*\s*\()")

_PY_CMD = re.compile(r"""(?ix)\b(
    os\.system|os\.popen|subprocess\.[a-z_]+|commands\.getoutput
)\s*\(""")
_PY_SHELL_TRUE = re.compile(r"(?i)shell\s*=\s*True")
_PY_EVAL = re.compile(r"""(?ix)\b(eval|exec)\s*\(""")
_PY_DESER = re.compile(r"\b(pickle|marshal|cPickle|_pickle)\s*\.\s*(loads?)\s*\(")


def _sin_comentario(line: str) -> str:
    """Corta un comentario // o # de una línea PHP respetando comillas simples y dobles."""
    comilla: Optional[str] = None
    i = 0
    while i < len(line):
        c = line[i]
        if comilla:
            if c == comilla:
                comilla = None
        elif c in ("'", '"'):
            comilla = c
        elif c == "/" and i + 1 < len(line) and line[i + 1] == "/":
            return line[:i]
        elif c == "#":
            return line[:i]
        i += 1
    return line


class PhpShellDetector(Detector):
    id = "php-shell"
    title = "Ejecución remota y webshells (PHP/Python)"
    finding_type = "technical"

    def run(self, ctx: DetectorContext) -> List[Finding]:
        findings: List[Finding] = []
        for fb in ctx.files:
            if not fb.text or not fb.rel.lower().endswith(_SUFFIXES):
                continue
            lineas = fb.text.splitlines()
            es_php = fb.rel.lower().endswith((".php", ".inc", ".phtml"))
            reglas = self._reglas(fb.rel)
            for rule, patrones, cwe, vector, conf_base, titulo, desc, rem, rec in reglas:
                hits: List[Tuple[int, str, str]] = []
                for i, line in enumerate(lineas, start=1):
                    if is_comment_line(line) or has_ignore_marker(line):
                        continue
                    linea = _sin_comentario(line) if es_php else line
                    if not linea.strip():
                        continue
                    for rx, precisa_input in patrones:
                        if not rx.search(linea):
                            continue
                        alcanzable = bool(_INPUT.search(linea))
                        if precisa_input and not alcanzable:
                            continue
                        hits.append((i, redact_line(linea)[:160],
                                     "direct" if alcanzable else conf_base))
                        break
                    if len(hits) >= _MAX_HITS:
                        break
                if hits:
                    excerpt = "\n".join(f"L{n}: {t}" for n, t, _c in hits)
                    ev = ctx.evidence.from_file(
                        fb.path, etype="code", responsible_role="Rol de Evidencia",
                        result=f"{len(hits)} línea(s) con patrón {rule}",
                        description=f"Patrón de {titulo.lower()} en {fb.rel}.",
                        relevance="Superficie potencial de ejecución remota: requiere validación manual.",
                        excerpt_masked=excerpt, line=hits[0][0],
                    )
                    confianza = "direct" if any(c == "direct" for _n, _t, c in hits) else conf_base
                    findings.append(build_finding(
                        detector_id=self.id, rule=rule,
                        title=f"{titulo} en {fb.rel}",
                        description=desc + f" Líneas: "
                        + ", ".join(str(n) for n, _t, _c in hits[:8]) + ".",
                        component=fb.rel, finding_type="technical",
                        evidence_ids=[ev.id], cwe=cwe, cvss_vector=vector,
                        reproduction_command=f'grep -nE "{patrones[0][0].pattern[:40]}" "{fb.rel}"',
                        reproduction_expected="líneas coincidentes (extractos enmascarados en la evidencia)",
                        remediation=rem, recommendations=rec,
                        confidence=confianza,
                        impact_compliance="A.8.28 codificación segura; A.8.25 ciclo de vida de desarrollo seguro.",
                    ))
        return findings

    def _reglas(self, rel: str):
        es_python = rel.lower().endswith((".py", ".pyw"))
        comunes = [
            ("py-cmd-exec",
             [(_PY_CMD, False), (_PY_EVAL, True)],
             ["CWE-78", "CWE-94"],
             "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Ejecución de comandos o código Python",
             "Líneas con os.system/subprocess/eval/exec: si la entrada del usuario "
             "alcanza la llamada, hay ejecución remota potencial.",
             "Parametrizar argv sin shell; nunca concatenar entrada en comandos; "
             "sustituir eval/exec por parsing controlado.",
             "Ejecutar `python -m bandit -r .` en el pipeline para este tipo de patrón."),
            ("py-insecure-deser",
             [(_PY_DESER, True)],
             ["CWE-502"],
             "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Deserialización insegura en Python",
             "pickle.loads/marshal.loads con entrada externa permiten ejecutar "
             "objetos arbitrarios si el flujo de datos no es confiable.",
             "Usar formatos de datos (JSON); si pickle es inevitable, firmar el payload.",
             "Revisar todos los puntos donde se carga un objeto serializado desde la red."),
        ] if es_python else [
            ("php-cmd-exec",
             [(_PHP_CMD, True), (_PHP_PREG_E, False), (_PHP_BACKTICK, True)],
             ["CWE-78", "CWE-94", "CWE-95"],
             "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Ejecución de comandos o código PHP",
             "Funciones de ejecución (system, eval, preg_replace /e…) alcanzables por "
             "entrada del usuario: patrón clásico de webshell/php2shell.",
             "Eliminar eval/assert; usar allowlist y escapeshellarg si el comando es inevitable.",
             "Ejecutar `phpstan`/`psalm` con reglas de seguridad y revisar la superficie HTTP."),
            ("php-dynamic-include",
             [(_PHP_INCLUDE, True)],
             ["CWE-98"],
             "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Inclusión de archivo con ruta de entrada",
             "include/require con ruta controlable: LFI/RFI y ejecución de archivo subido.",
             "Usar allowlist de vistas; nunca incluir con $_GET/$_POST en la ruta.",
             "Revisar el manejo de rutas del front controller."),
            ("php-unserialize",
             [(_PHP_UNSERIALIZE, True)],
             ["CWE-502"],
             "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "unserialize con entrada externa",
             "unserialize sobre datos de la petición permite object injection si hay "
             "clases con __wakeup/__destruct peligrosos.",
             "Usar json_decode; si unserialize es inevitable, pasar allowed_classes=false.",
             "Inventariar clases con magic methods que toquen disco o red."),
            ("php-upload",
             [(_PHP_UPLOAD, False)],
             ["CWE-434"],
             "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Carga de archivos del cliente",
             "move_uploaded_file: validar extensión, MIME, destino fuera del web root "
             "y sin ejecución; combinaciones típicas de upload→shell.",
             "Allowlist de extensiones, nombre aleatorio, directorio sin exec.",
             "Verificar que los uploads no queden bajo el docroot con PHP habilitado."),
            ("php-obfuscation",
             [(_PHP_OBF, False), (_PHP_DYNAMIC_CALL, False)],
             ["CWE-94", "CWE-1007"],
             "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
             "indirect",
             "Ofuscación o llamadas dinámicas",
             "base64_decode/gzinflate/str_rot13 o nombres de función dinámicos: patrón "
             "frecuente en webshells y backdoors (php2shell).",
             "Decodificar y revisar a mano; si es código legítimo, documentarlo con c4a:ignore.",
             "Comparar el archivo con el del paquete/distribución original por hash."),
        ]
        return comunes
