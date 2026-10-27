#!/usr/bin/env python3
"""Reconocimiento pasivo autenticado de la plataforma del curso (Fase 1/2).

Solo lectura con la cuenta del auditor: navega páginas normales de Moodle y guarda
señales de huella (versión vía M.cfg, cabeceras, pie, plugins visibles). Nada de
escaneo ni pruebas activas. Los valores sensibles (.env) y la sesskey se enmascaran
antes de persistir; el crudo queda en evidence/ (fuera de git).

Salida: evidence/capturas_curso/recon/{resumen.json,paginas/*.html,*.png}
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENV = RAIZ / ".env"
SALIDA = RAIZ / "evidence" / "capturas_curso" / "recon"


def _cargar_env() -> dict:
    vals: dict = {}
    for linea in ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", linea)
        if not m or linea.strip().startswith("#"):
            continue
        vals[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return vals


def _clave_env(env: dict, *candidatas: str) -> str | None:
    bajos = {k.lower(): v for k, v in env.items()}
    for c in candidatas:
        for k, v in bajos.items():
            if c in k:
                return v
    return None


def main() -> None:
    env = _cargar_env()
    url_curso = _clave_env(env, "url", "curso", "site")
    usuario = _clave_env(env, "user", "usuario", "mail")
    clave = _clave_env(env, "pass", "clave", "password")
    if not (url_curso and usuario and clave):
        sys.exit("faltan URL_CURSO/USUARIO/CLAVE en .env")
    from playwright.sync_api import sync_playwright

    base = re.match(r"https?://[^/]+", url_curso).group(0)
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "paginas").mkdir(exist_ok=True)

    def masc(texto: str) -> str:
        for v in (clave, usuario):
            if v and len(v) >= 3:
                texto = texto.replace(v, "***")
        texto = re.sub(r'"sesskey"\s*:\s*"[^"]+"', '"sesskey":"***"', texto)
        texto = re.sub(r"(sesskey=)[0-9a-zA-Z]+", r"\1***", texto)
        return texto

    rutas = [
        ("/", "home"),
        ("/login/index.php", "login"),
        ("/my/", "panel"),
        ("/course/index.php", "catalogo"),
        ("/course/view.php?id=848", "curso_848"),
        ("/admin/index.php", "admin_index"),
        ("/admin/plugins.php", "admin_plugins"),
        ("/admin/search.php", "admin_buscar"),
        ("/lib/upgrade.txt", "upgrade_txt"),
        ("/composer.json", "composer_json"),
        ("/package.json", "package_json"),
        ("/version.php", "version_php"),
        ("/reportbuilder/", "probe_reportbuilder"),
        ("/h5p/", "probe_h5p"),
        ("/contentbank/", "probe_contentbank"),
        ("/course/format/", "probe_format"),
        ("/mod/forum/view.php?id=1", "probe_forum"),
    ]

    resumen: dict = {"base": base, "paginas": []}
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        ctx = navegador.new_context(locale="es-CL", viewport={"width": 1366, "height": 900})
        pg = ctx.new_page()
        # autenticación
        pg.goto(url_curso, timeout=45000, wait_until="domcontentloaded")
        if not pg.query_selector("input[type='password']"):
            try:
                with pg.expect_navigation(timeout=20000, wait_until="domcontentloaded"):
                    pg.click("a:has-text('Acceder'), a:has-text('Iniciar sesión')", timeout=6000)
                pg.wait_for_timeout(1500)
            except Exception:
                pass
        cp = pg.query_selector("input[type='password']")
        if cp:
            cu = pg.query_selector("input[type='email'],input[name*='user' i],input[type='text']")
            if cu:
                cu.fill(usuario)
            cp.fill(clave)
            try:
                with pg.expect_navigation(timeout=20000, wait_until="domcontentloaded"):
                    pg.click("button[type='submit'],input[type='submit']", timeout=5000)
            except Exception:
                cp.press("Enter")
            pg.wait_for_timeout(2000)
        resumen["autenticado"] = pg.query_selector("input[type='password']") is None

        for ruta, nombre in rutas:
            url = base + ruta
            entrada = {"ruta": ruta, "url": url}
            try:
                resp = ctx.request.get(url, timeout=45000)
                cuerpo = resp.text()
                entrada["http"] = resp.status
                cab = {}
                for k in ("server", "x-powered-by", "set-cookie", "x-moodle-cache"):
                    v = resp.headers.get(k)
                    if v:
                        cab[k] = re.sub(r"(?i)(moodlesession=)[^;]+", r"\1***", v)
                entrada["cabeceras"] = cab
                # huella de versión de Moodle: M.cfg = {..., "version":"2022112800", ...}
                m = re.search(r'"version"\s*:\s*"(\d{10})"', cuerpo)
                entrada["moodle_version_interna"] = m.group(1) if m else None
                m2 = re.search(r'"branch"\s*:\s*"?(\d+\.\d+)', cuerpo)
                entrada["moodle_branch"] = m2.group(1) if m2 else None
                plugins = sorted(set(re.findall(r'"name"\s*:\s*"([a-z]+_[a-z0-9_]+)"', cuerpo)))[:20]
                if plugins and nombre.startswith("admin"):
                    entrada["plugins_visibles"] = plugins
                (SALIDA / "paginas" / f"{nombre}.html").write_text(
                    masc(cuerpo)[:400_000], encoding="utf-8")
            except Exception as e:
                entrada["error"] = f"{e.__class__.__name__}: {str(e)[:200]}"
            resumen["paginas"].append(entrada)
            if nombre in ("curso_848", "admin_index"):
                try:
                    pg.goto(url, timeout=30000, wait_until="domcontentloaded")
                    pg.wait_for_timeout(1500)
                    pg.screenshot(path=str(SALIDA / f"{nombre}.png"), full_page=False)
                except Exception:
                    pass
        navegador.close()

    (SALIDA / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    for e in resumen["paginas"]:
        print(f"{e['ruta']:24} http={e.get('http', 'ERR'):>4} "
              f"version={e.get('moodle_version_interna') or '-'} "
              f"{('server=' + e['cabeceras']['server']) if e.get('cabeceras', {}).get('server') else ''}")
    print(f"resumen en {SALIDA.relative_to(RAIZ)}/resumen.json")


if __name__ == "__main__":
    main()
