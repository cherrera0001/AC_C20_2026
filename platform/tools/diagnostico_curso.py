#!/usr/bin/env python3
"""Diagnóstico no invasivo del curso (Fase 1 de docs/INSTRUCCION_AUDITORIA_CURSO.md).

Uso de credenciales con minimización de exposición:
  - Las credenciales se leen de .env en runtime por ESTE proceso (del dueño) y jamás
    se imprimen, copian ni persisten: el agente solo ve nombres de claves y el
    diagnóstico ya enmascarado.
  - La captura se guarda en evidence/ (fuera de git) y reemplaza cualquier ocurrencia
    de los valores sensibles por «***» antes de escribir.

Solo lectura: navega, inicia sesión con la cuenta del auditor y caracteriza el fallo.
Sin escaneo, sin payloads, sin pruebas activas (esas exigen scope/autorizacion.md).

Subcomandos:
  claves        → lista los NOMBRES de las claves de .env (sin valores).
  curso         → inicia sesión, abre el curso y escribe el diagnóstico en evidence/.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENV = RAIZ / ".env"
SALIDA = RAIZ / "evidence" / "capturas_curso"


def _cargar_env() -> dict:
    vals: dict = {}
    if not ENV.is_file():
        sys.exit(f"no existe {ENV}")
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


def cmd_claves() -> None:
    env = _cargar_env()
    print("claves presentes en .env (nombres y longitud del valor, nunca el valor):")
    for k in sorted(env):
        v = env[k]
        print(f"  {k:24} longitud={len(v):3} {'(vacía)' if not v else ''}")


def cmd_curso() -> None:
    env = _cargar_env()
    url_login = _clave_env(env, "url", "login", "site", "host", "curso")
    usuario = _clave_env(env, "user", "usuario", "mail", "email", "rut")
    clave = _clave_env(env, "pass", "clave", "password", "token")
    curso = _clave_env(env, "curso_id", "course", "id_curso", "curso")
    if curso == url_login:
        curso = None  # la URL del curso ya es la de entrada; no hay ruta extra
    if not (url_login and usuario and clave):
        sys.exit("faltan claves: se necesita url, usuario y contraseña en .env "
                 "(use «claves» para ver los nombres disponibles)")
    from playwright.sync_api import sync_playwright

    SALIDA.mkdir(parents=True, exist_ok=True)
    consola: list[dict] = []
    red_fallos: list[dict] = []
    hallazgo: dict = {"pasos": []}

    def log(paso: str, detalle: str = "") -> None:
        hallazgo["pasos"].append({"paso": paso, "detalle": detalle})

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        ctx = navegador.new_context(locale="es-CL", viewport={"width": 1366, "height": 900},
                                    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                               "(KHTML, like Gecko) Chrome/124 Safari/537.36")
        pg = ctx.new_page()
        pg.on("console", lambda m: consola.append({"tipo": m.type, "texto": m.text[:300]})
              if m.type in ("error", "warning") else None)
        pg.on("response", lambda r: red_fallos.append({"url": r.url[:200], "estado": r.status})
              if r.status >= 400 else None)
        try:
            log("abrir_login", url_login.split("?")[0])
            r = pg.goto(url_login, timeout=45000, wait_until="domcontentloaded")
            log("login_http", str(r.status if r else "sin respuesta"))
            pg.wait_for_timeout(2500)
            campo_pass = pg.query_selector("input[type='password']")
            if not campo_pass:
                log("login_form", "sin campo de contraseña en la página inicial; se busca «Acceder»")
                try:
                    with pg.expect_navigation(timeout=20000, wait_until="domcontentloaded"):
                        pg.click("a:has-text('Acceder'), a:has-text('Iniciar sesión'), "
                                 "a:has-text('Log in'), a:has-text('Login')", timeout=6000)
                    pg.wait_for_timeout(2000)
                except Exception:
                    pass
                campo_pass = pg.query_selector("input[type='password']")
            if not campo_pass:
                log("login_form", "no se encontró campo de contraseña; se guarda captura")
                pg.screenshot(path=str(SALIDA / "01_login.png"), full_page=False)
                hallazgo["estado"] = "formulario de login no identificado"
            else:
                campo_user = pg.query_selector("input[type='email'],input[name*='user' i],"
                                               "input[name*='mail' i],input[type='text']")
                if campo_user:
                    campo_user.fill(usuario)
                campo_pass.fill(clave)
                with pg.expect_navigation(timeout=20000, wait_until="domcontentloaded"):
                    try:
                        pg.click("button[type='submit'],input[type='submit'],button:has-text('Ingresar'),"
                                 "button:has-text('Entrar'),button:has-text('Login'),button:has-text('Acceder')",
                                 timeout=5000)
                    except Exception:
                        campo_pass.press("Enter")
                log("post_login_url", pg.url.split("?")[0])
                pg.wait_for_timeout(2500)
                destino = curso if curso and curso.startswith("http") else \
                    (url_login.rstrip("/") + ("/" + curso.lstrip("/") if curso else ""))
                log("abrir_curso", destino.split("?")[0])
                try:
                    r2 = pg.goto(destino, timeout=45000, wait_until="domcontentloaded")
                    log("curso_http", str(r2.status if r2 else "sin respuesta"))
                except Exception as e:  # la página puede fallar y eso ES el síntoma
                    log("curso_error_navegacion", str(e)[:300])
                pg.wait_for_timeout(3000)
                hallazgo["url_final"] = pg.url.split("?")[0]
                hallazgo["titulo"] = pg.title()
                try:
                    cuerpo = pg.inner_text("body")[:4000]
                except Exception:
                    cuerpo = ""
                hallazgo["texto_visible"] = cuerpo
                pg.screenshot(path=str(SALIDA / "02_curso.png"), full_page=False)
                hallazgo["estado"] = "capturado"
        except Exception as e:
            hallazgo["estado"] = f"excepcion: {e.__class__.__name__}: {str(e)[:300]}"
            try:
                pg.screenshot(path=str(SALIDA / "00_error.png"), full_page=False)
            except Exception:
                pass
        finally:
            navegador.close()

    # enmascarar valores sensibles antes de persistir
    def masc(texto: str) -> str:
        for v in (clave, usuario):
            if v and len(v) >= 3:
                texto = texto.replace(v, "***")
        return texto

    hallazgo["consola"] = [{**c, "texto": masc(c["texto"])} for c in consola[:40]]
    hallazgo["red_fallos"] = [{**r, "url": masc(r["url"])} for r in red_fallos[:40]]
    for k in ("texto_visible", "url_final"):
        if k in hallazgo:
            hallazgo[k] = masc(hallazgo[k])
    ruta = SALIDA / "diagnostico_curso.json"
    ruta.write_text(json.dumps(hallazgo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"diagnóstico escrito en {ruta.relative_to(RAIZ)} (valores sensibles enmascarados)")
    print(f"estado: {hallazgo['estado']}")
    if "curso_http" in hallazgo:
        print(f"http del curso: {hallazgo['curso_http']}")
    if "titulo" in hallazgo:
        print(f"título: {hallazgo['titulo']}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("claves", "curso"):
        print(__doc__)
        sys.exit(2)
    {"claves": cmd_claves, "curso": cmd_curso}[sys.argv[1]]()
