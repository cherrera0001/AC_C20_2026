"""S08 — Las dos frases: el mismo resultado para la gerencia y para quien corrige.

La herramienta ABRE las dos frases a partir de la entrega de S07 (`encargo.entregar`, que
consolida hechos, riesgos, citas, perfil y lista con sus huellas) y PROPONE ambas
redacciones: la frase de gerencia en lenguaje de negocio, sin jerga técnica ni
identificadores de controles, y la frase de quien corrige con remisión a fichas y huellas.
Ambas MUST decir el mismo resultado: mismos conteos, mismos vacíos con la misma causa
(FR-003, FR-005). El auditor CORRIGE con motivo —una corrección que rompa la consistencia
entre registros se rechaza con el detalle (FR-007)—, REVISA y FIRMA (principio I). Las
frases no dictaminan: comunican lo registrado, sin estados de cumplimiento (FR-006).
Nada de este módulo abre la compuerta ni escribe fuera de `04_informe/`.

Archivos que produce:
  - 04_informe/frases_s08.json        contenido canónico (lo que se firma)
  - 04_informe/frases_s08.firma.json  firma: firmante, fecha, justificación y huella
  - 04_informe/frases_s08.md          vista legible para un tercero
  - 04_informe/frase-gerencia.md      ficha legible de la frase de gerencia (FR-012)
  - 04_informe/frase-tecnica.md       ficha legible de la frase de quien corrige
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import alcance
from . import encargo
from . import registro
from .util import now_iso, sha256_bytes, sha256_file

PRODUCTO = "S08 — Las dos frases"
VERSION_ESQUEMA = "1"

APROBACION = ("borrador", "revisado")
FRASES = ("gerencia", "tecnica")
EVENTOS = ("propuesta", "correccion", "revision", "firma_anulada")

NOTA_FIRMA = "Firmar las frases no abre la compuerta de autorización."
NOTA_PARIDAD = ("Las dos frases dicen el mismo resultado: si difieren en un hecho, la "
                "verificación lo marca como inconsistencia.")

ARCHIVO_JSON = "04_informe/frases_s08.json"
ARCHIVO_MD = "04_informe/frases_s08.md"
ARCHIVO_FIRMA = "04_informe/frases_s08.firma.json"
FICHA_GERENCIA = "04_informe/frase-gerencia.md"
FICHA_TECNICA = "04_informe/frase-tecnica.md"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"


class FrasesError(Exception):
    """Operación rechazada. `codigo` sigue el contrato del subcomando `frases`."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "encargo": r / encargo.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise FrasesError(f"no existe {ARCHIVO_JSON}: ejecute primero «frases abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise FrasesError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise FrasesError(f"{nombre} contiene {clase}: las frases no lo admiten (FR-016)")
    return alcance.limpiar(v)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return encargo.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["encargo"].exists():
        raise FrasesError(f"no existe {encargo.ARCHIVO_JSON}: falta el producto anterior de S07; "
                          "ejecute primero «encargo abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": encargo.ARCHIVO_JSON,
            "sha256": sha256_file(p["encargo"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": entrega["integro"],
            "estado": entrega["estado"],
            "cadena": {s: {"firmado": c["estado"]} for s, c in entrega["cadena"].items()}}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["encargo"].exists():
        return True
    if sha256_file(p["encargo"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise FrasesError("el encargo de origen (S07) cambió desde que se abrieron las frases: "
                          "ejecute «frases abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Propuestas (FR-003, FR-004, FR-005) -------------------------------------

def _proponer(entrega: Dict[str, Any]) -> Dict[str, Any]:
    r = entrega["resumen"]
    activo = r.get("activo", "el activo")
    causas = [c for c in r.get("vacios_causas", []) if c]
    causa_txt = "; ".join(causas[:2]) if causas else "autorización o documentación pendiente"
    riesgos, vacios = r.get("riesgos", 0), r.get("vacios", 0)
    controles, pend = r.get("controles_seleccionados", 0), r.get("controles_pendientes", 0)
    if riesgos:
        nucleo_g = (f"La revisión de {activo} dejó {riesgos} riesgos sobre lo verificado")
    else:
        nucleo_g = f"La revisión de {activo} no dejó riesgos sobre lo verificado"
    gerencia = (
        f"{nucleo_g}. Quedan {vacios} vacíos por verificar ({causa_txt}). "
        f"El resultado se organizó con las seis funciones del NIST CSF 2.0 y se proponen "
        f"{controles} medidas de protección aplicables ({pend} pendientes de confirmar). "
        "El detalle técnico y las acciones para quien corrige van en la parte técnica del informe."
    )
    if vacios:
        parte_vacios = f"- {vacios} vacíos: {causa_txt}"
    else:
        parte_vacios = "- Sin vacíos declarados."
    tecnica = (
        f"Resultado técnico de la revisión de {activo} (huella del encargo: "
        f"{entrega['cadena']['S06']['sha256'][:16]}…).\n\n"
        f"Se enunciaron {riesgos} riesgos (fichas en 03_hallazgos/enunciado-*.md y cita-*.md).\n"
        f"Citas con marco y versión: {r.get('citas', 0)}; funciones del perfil con material: "
        f"{r.get('funciones_con_material', 0)} de 6.\n"
        f"Controles CIS propuestos: {controles} ({pend} pendientes de confirmar o documentales).\n\n"
        f"Vacíos declarados (misma causa en ambos registros):\n{parte_vacios}\n\n"
        "Quien corrige: cada riesgo remite a su ficha y a sus evidencias con huella; lo que "
        "falta por verificar quedó escrito como condición en el encargo (01_plan/encargo_s07.json)."
    )
    return {"gerencia": gerencia, "tecnica": tecnica,
            "conteos": {"riesgos": riesgos, "vacios": vacios, "controles": controles,
                        "pendientes": pend}}


def _derivar(entrega: Dict[str, Any], historial: List[Dict[str, Any]]) -> Dict[str, Any]:
    propuesta = _proponer(entrega)
    frases = {nombre: {"texto": propuesta[nombre], "correcciones": []} for nombre in FRASES}
    for ev in historial:
        if ev["tipo"] == "correccion":
            f = frases[ev["frase"]]
            f["texto"] = ev["nuevo"]
            f["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"],
                                      "motivo": ev["motivo"]})
    return {"frases": frases, "conteos": propuesta["conteos"]}


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, derivado, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "frases": derivado["frases"], "conteos": derivado["conteos"],
            "estado_aprobacion": _estado(historial), "historial": historial, "avisos": avisos}


# --- Consistencia entre las dos frases (FR-009) ------------------------------

def _numeros(texto: str, concepto: str) -> List[str]:
    return re.findall(rf"(\d+)\s+{concepto}", texto)


def _inconsistencias(contenido: Dict[str, Any]) -> List[str]:
    """Diferencias de contenido factual entre las dos frases: conteos por concepto."""
    problemas: List[str] = []
    c = contenido["conteos"]
    vistos: Dict[str, List[str]] = {}
    for nombre in FRASES:
        texto = contenido["frases"][nombre]["texto"]
        if not texto.strip():
            problemas.append(f"{nombre}: frase vacía")
            continue
        vistos[nombre] = (_numeros(texto, "riesgos"), _numeros(texto, r"vacío[s]?"))
        esperado = ([str(c["riesgos"])], [str(c["vacios"])])
        if vistos[nombre][0] != esperado[0]:
            problemas.append(f"{nombre}: conteo de riesgos {_celda(vistos[nombre][0])} "
                             f"distinto del registrado ({c['riesgos']})")
        if vistos[nombre][1] != esperado[1]:
            problemas.append(f"{nombre}: conteo de vacíos {_celda(vistos[nombre][1])} "
                             f"distinto del registrado ({c['vacios']})")
    if len({tuple(tuple(x) for x in v) for v in vistos.values()}) > 1:
        problemas.append("las dos frases reportan conteos distintos")
    g = contenido["frases"]["gerencia"]["texto"]
    if re.search(r"\bA\.\d", g):
        problemas.append("gerencia: contiene identificadores de controles (FR-004)")
    return problemas


# --- Abrir (US1, FR-001, FR-014) ---------------------------------------------

def _anular_firma(raiz, historial: List[Dict[str, Any]], autor: str, fecha: str) -> None:
    ruta = _rutas(raiz)["firma"]
    if ruta.exists():
        ruta.unlink()
        historial.append({"tipo": "firma_anulada", "autor": autor, "fecha": fecha,
                          "motivo": "Cambio posterior a la firma: se exige una nueva firma."})


def _escribir(raiz, contenido: Dict[str, Any]) -> None:
    p = _rutas(raiz)
    p["json"].parent.mkdir(parents=True, exist_ok=True)
    p["json"].write_bytes(alcance.serializar(contenido))
    escribir_vista(raiz)


def _guardar(raiz, contenido: Dict[str, Any], evento: Dict[str, Any]) -> Dict[str, Any]:
    historial = contenido["historial"] + [evento]
    _anular_firma(raiz, historial, evento["autor"], evento["fecha"])
    origen = _contexto(raiz, contenido)
    derivado = _derivar(_entrega_actual(raiz), historial)
    nuevo = _componer(origen, derivado, historial, contenido["avisos"])
    _escribir(raiz, nuevo)
    return nuevo


def abrir(raiz, fecha: Optional[str] = None) -> Dict[str, Any]:
    p = _rutas(raiz)
    previo = cargar(raiz) if p["json"].exists() else None
    origen = _contexto(raiz, previo)
    avisos: List[str] = []
    if previo is None:
        historial: List[Dict[str, Any]] = [{
            "tipo": "propuesta", "autor": RESPONSABLE_HERRAMIENTA, "fecha": fecha or now_iso(),
            "motivo": "Propuesta de las dos frases a partir de la entrega vigente de S07."}]
    else:
        historial = previo["historial"]
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió el encargo de origen (S07) desde la versión anterior de las frases.")
    derivado = _derivar(_entrega_actual(raiz), historial)
    contenido = _componer(origen, derivado, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise FrasesError("Las frases están firmadas y el encargo de origen cambió. No se actualizan "
                          "solas: revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, revisar, firmar (US2, FR-007, FR-008) --------------------------

def corregir(raiz, frase: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if frase not in FRASES:
        raise FrasesError(f"frase no válida: {frase} (use {', '.join(FRASES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    propuesto = json.loads(alcance.serializar(contenido))
    propuesto["frases"][frase]["texto"] = nuevo_valor
    problemas = _inconsistencias(propuesto)
    if problemas:
        raise FrasesError("la corrección rompe la consistencia entre registros: " + "; ".join(problemas))
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "frase": frase,
          "anterior": contenido["frases"][frase]["texto"], "nuevo": nuevo_valor, "motivo": motivo}
    return _guardar(raiz, contenido, ev)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige ambas frases completas y consistentes."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise FrasesError("solo se firman frases «revisadas»: registre una corrección o una revisión")
    problemas = _inconsistencias(contenido)
    if problemas:
        raise FrasesError("no se puede firmar con inconsistencias: " + "; ".join(problemas))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "conteos_al_firmar": dict(contenido["conteos"]), "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) -------------------------------

def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise FrasesError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"frases": {}, "origen": {}, "conteos": {}}
        ilegible = True
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["encargo"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except encargo.EncargoError:
            entrega_ok = False
    inconsistencias = [] if ilegible else _inconsistencias(contenido)
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "inconsistencias": inconsistencias}
    if not p["firma"].exists():
        r["estado"] = "sin firma"
    else:
        firma = json.loads(p["firma"].read_bytes().decode("utf-8"))
        r["sha256_firmado"] = firma.get("sha256")
        r["huella_ok"] = firma.get("sha256") == actual
        if r["huella_ok"]:
            r.update(estado="firmado", firmante=firma.get("firmante"), fecha=firma.get("fecha"),
                     motivo=firma.get("motivo"))
        else:
            r["estado"] = "revisado (firma no aplica)"
    if ilegible:
        r["estado"] = "revisado (json ilegible)"
        r["estado_informado"] = r["estado"]
        r["integro"] = False
        return r
    if r["estado"] == "firmado" and (inconsistencias or not entrega_ok):
        partes = []
        if inconsistencias:
            partes.append("inconsistencia entre frases")
        if not entrega_ok:
            partes.append("origen cambiado")
        r["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        r["estado_informado"] = r["estado"]
    r["integro"] = (not inconsistencias and entrega_ok
                    and not r["estado"].startswith("revisado"))
    return r


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


def entregar(raiz) -> Dict[str, Any]:
    """Lo que recibe S09: las dos frases con los conteos verificados (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "origen": contenido["origen"], "gerencia": contenido["frases"]["gerencia"]["texto"],
            "tecnica": contenido["frases"]["tecnica"]["texto"], "conteos": contenido["conteos"],
            "inconsistencias": v["inconsistencias"]}


# --- Vista legible y fichas (FR-012, principio VIII) --------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    c = contenido["conteos"]
    L = [f"# Las dos frases (S08) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         f"> {NOTA_PARIDAD}", "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Encargo de origen**: `{origen['archivo']}` · huella `{origen['sha256']}`",
          f"- **Conteos verificados**: {c['riesgos']} riesgos · {c['vacios']} vacíos · "
          f"{c['controles']} controles · {c['pendientes']} pendientes", "",
          "## Frase para la gerencia", "", contenido["frases"]["gerencia"]["texto"], "",
          "## Frase para quien corrige", "", contenido["frases"]["tecnica"]["texto"], "",
          f"## Inconsistencias ({len(v['inconsistencias'])})", ""]
    if v["inconsistencias"]:
        L += [f"- {p}" for p in v["inconsistencias"]]
    else:
        L.append("Ninguna: ambas frases dicen lo mismo.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Frase | Motivo |", "|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('frase'))} | "
                     f"{_celda(e.get('motivo'))} |")
    else:
        L.append("Sin eventos.")
    if contenido["avisos"]:
        L += ["", "## Avisos", ""] + [f"- {a}" for a in contenido["avisos"]]
    L += ["", NOTA_FIRMA]
    return "\n".join(L) + "\n"


def escribir_vista(raiz) -> Path:
    p = _rutas(raiz)
    p["md"].write_bytes(vista(raiz).encode("utf-8"))
    contenido = cargar(raiz)
    for nombre, ruta in (("gerencia", p["raiz"] / FICHA_GERENCIA),
                         ("tecnica", p["raiz"] / FICHA_TECNICA)):
        f = contenido["frases"][nombre]
        correcciones = "\n".join(f"- {x['fecha']} · {x['autor']} · {x['motivo']}"
                                 for x in f["correcciones"]) or "Sin correcciones."
        titulo = "Frase para la gerencia" if nombre == "gerencia" else "Frase para quien corrige"
        ruta.write_text(f"# {titulo} (S08)\n\n{f['texto']}\n\n## Correcciones "
                        f"({len(f['correcciones'])})\n\n{correcciones}\n", encoding="utf-8")
    return p["md"]
