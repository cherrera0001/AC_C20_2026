"""S05 — El perfil: el mismo activo leído con las seis funciones del NIST CSF 2.0.

La herramienta ABRE el perfil a partir de la entrega de S04 (`cita.entregar`), PROPONE la
asignación riesgo citado ↔ función a partir del dominio, el resultado técnico y el fundamento
de la cita, y PROPONE una síntesis por función (borrador que el auditor completa). El auditor
CORRIGE síntesis, REASIGNA riesgos entre funciones, REVISA y FIRMA (principio I). Un perfil
no dictamina: una función sin material queda «no consta» con su motivo, nunca «sin hallazgos»
ni «cumple» (FR-006). Nada de este módulo abre la compuerta ni escribe fuera de
`03_hallazgos/`.

Archivos que produce:
  - 03_hallazgos/perfil_s05.json        contenido canónico (lo que se firma)
  - 03_hallazgos/perfil_s05.firma.json  firma: firmante, fecha, justificación y huella
  - 03_hallazgos/perfil_s05.md          vista legible para un tercero
  - 03_hallazgos/perfil-<funcion>.md    una ficha legible por función (FR-012)

Reglas de diseño (misma forma que S03 y S04): el historial es la fuente, nada se borra
(FR-007), el resultado es determinista (FR-010) y firmar exige las seis síntesis completas
(FR-008). La granularidad es la función, que es la de la fila S05.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from . import cita
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S05 — El perfil"
VERSION_ESQUEMA = "1"

FUNCIONES = ("Gobernar", "Identificar", "Proteger", "Detectar", "Responder", "Recuperar")

APROBACION = ("borrador", "revisado")
CAMPOS_CORREGIBLES = ("sintesis",)
EVENTOS = ("propuesta", "correccion", "reasignacion", "revision", "firma_anulada")

MARCA_ALTERADA = "evidencia alterada"
MARCA_RIESGO_NO_VIGENTE = "riesgo no vigente"

NOTA_FIRMA = "Firmar el perfil no abre la compuerta de autorización."
NOTA_VACIO = ("«No consta» en una función quiere decir que no hay material registrado para "
              "ella: no es una evaluación del control ni una ausencia de hallazgos.")

ARCHIVO_JSON = "03_hallazgos/perfil_s05.json"
ARCHIVO_MD = "03_hallazgos/perfil_s05.md"
ARCHIVO_FIRMA = "03_hallazgos/perfil_s05.firma.json"
PREFIJO_FICHA = "03_hallazgos/perfil-"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

# Propuesta de asignación riesgo ↔ función: términos de contenido por función (castellano).
_TERMINOS_FUNCION = {
    "Gobernar": ("politica", "politicas", "gobierno", "roles", "responsabilidad", "proveedor",
                 "proveedores", "cumplimiento", "auditoria", "supervision", "organizacional"),
    "Identificar": ("inventario", "activos", "superficie", "exposicion", "riesgo", "vulnerabilidad",
                    "vulnerabilidades", "gestion de vulnerabilidades", "evaluacion"),
    "Proteger": ("cifrado", "criptografia", "acceso", "autenticacion", "configuracion", "segmentacion",
                 "parche", "parches", "tls", "ssh", "proteccion", "privilegiado", "codigo fuente",
                 "desarrollo seguro", "entornos"),
    "Detectar": ("monitoreo", "registro", "logs", "deteccion", "anomalia", "alerta", "alertas",
                 "auditoria continua"),
    "Responder": ("incidente", "incidentes", "respuesta", "contingencia", "reporte", "manejo"),
    "Recuperar": ("recuperacion", "copia", "copias", "respaldo", "restauracion", "continuidad",
                  "disaster", "contingencias"),
}


class PerfilError(Exception):
    """Operación rechazada. `codigo` sigue el contrato del subcomando `perfil`."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


def _slug(texto: str, largo: int = 24) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:largo].strip("-")


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "cita": r / cita.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise PerfilError(f"no existe {ARCHIVO_JSON}: ejecute primero «perfil abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise PerfilError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise PerfilError(f"{nombre} contiene {clase}: el perfil no lo admite (FR-016)")
    return alcance.limpiar(v)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return cita.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["cita"].exists():
        raise PerfilError(f"no existe {cita.ARCHIVO_JSON}: falta el producto anterior de S04; "
                          "ejecute primero «cita abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": cita.ARCHIVO_JSON,
            "sha256": sha256_file(p["cita"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": bool(entrega["firmado"]),
            "estado": entrega["estado"]}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["cita"].exists():
        return True
    if sha256_file(p["cita"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise PerfilError("la cita de origen (S04) cambió desde que se abrió el perfil: "
                          "ejecute «perfil abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Derivación: entrega + historial → secciones (FR-003 a FR-005) ----------

def _terminos_funcion(texto: str) -> set:
    return {t for t in alcance._norm(texto).split() if len(t) >= 4}


def _proponer_funcion(c: Dict[str, Any]) -> Optional[str]:
    texto = " ".join([c["riesgo"]["condicion"], c["fundamento"]])
    terminos = _terminos_funcion(texto)
    mejor, puntaje = None, 0
    for funcion, claves in _TERMINOS_FUNCION.items():
        p = len(terminos & set(claves))
        if p > puntaje:
            mejor, puntaje = funcion, p
    return mejor


def _proponer_sintesis(funcion: str, riesgos: List[Dict], vacios: List[Dict]) -> str:
    if riesgos or vacios:
        return (f"Borrador: la función {funcion} recoge {len(riesgos)} riesgo(s) citado(s) y "
                f"{len(vacios)} vacío(s) con motivo. Lo completa el auditor con su lectura.")
    return ""


def _derivar(entrega: Dict[str, Any], historial: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], List[Dict], List[str]]:
    asignaciones: Dict[str, Optional[str]] = {}   # cita_id → función | None
    for c in entrega["citas"]:
        asignaciones[c["id"]] = _proponer_funcion(c)
    vacios_por_funcion: Dict[str, List[Dict]] = {f: [] for f in FUNCIONES}
    comunes: List[Dict] = []
    for v in entrega.get("vacios", []):
        texto = " ".join([v["dominio"]["valor"], v.get("motivo") or ""])
        funcion = _proponer_funcion({"riesgo": {"condicion": texto}, "fundamento": ""})
        destino = vacios_por_funcion.get(funcion) if funcion else None
        if destino is None:
            comunes.append(v)
        else:
            destino.append(v)
    for ev in historial:
        if ev["tipo"] == "reasignacion":
            asignaciones[ev["cita"]] = ev["funcion"]
    secciones: List[Dict[str, Any]] = []
    por_funcion: Dict[str, List[Dict]] = {f: [] for f in FUNCIONES}
    for c in entrega["citas"]:
        f = asignaciones.get(c["id"])
        if f in FUNCIONES:
            por_funcion[f].append(c)
    for ev in historial:
        if ev["tipo"] == "correccion":
            pass  # se aplica sobre la sección compuesta, abajo
    sin_asignar = [c for c in entrega["citas"] if asignaciones.get(c["id"]) not in FUNCIONES]
    for funcion in FUNCIONES:
        riesgos = sorted(por_funcion[funcion], key=lambda c: c["id"])
        vacios = sorted(vacios_por_funcion[funcion], key=lambda v: v["id"])
        sintesis = _proponer_sintesis(funcion, riesgos, vacios)
        seccion = {
            "id": short_id("P", funcion),
            "funcion": funcion,
            "sintesis": sintesis,
            "riesgos": [{"cita": x["id"], "riesgo": x["riesgo"], "marco": x["marco"],
                         "version": x["version"], "identificador": x["identificador"],
                         "estado_identificador": x["estado_identificador"]} for x in riesgos],
            "vacios": vacios,
            "falta": [v["motivo"] for v in vacios if v.get("motivo")],
            "evidencias": sorted({ev["id"]: ev for x in riesgos for ev in x["evidencias"]}.values(),
                                  key=lambda e: e["id"]),
            "estado_aprobacion": "borrador",
            "correcciones": [],
        }
        for ev in historial:
            if ev["tipo"] == "correccion" and ev["seccion"] == funcion:
                seccion["sintesis"] = ev["nuevo"]
                seccion["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"],
                                                "campo": "sintesis", "anterior": ev["anterior"],
                                                "nuevo": ev["nuevo"], "motivo": ev["motivo"]})
                seccion["estado_aprobacion"] = "revisado"
        if any(ev["tipo"] == "reasignacion" and ev["funcion"] == funcion for ev in historial):
            seccion["estado_aprobacion"] = "revisado"
        secciones.append(seccion)
    return secciones, sin_asignar, comunes, []


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "reasignacion", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, secciones, sin_asignar, vacios_comunes, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "secciones": secciones, "sin_asignar": sin_asignar, "vacios_comunes": vacios_comunes,
            "estado_aprobacion": _estado(historial), "historial": historial, "avisos": avisos}


# --- Abrir (US1, FR-001 a FR-003, FR-014) -----------------------------------

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
    secciones, sin_asignar, comunes, avisos = _derivar(_entrega_actual(raiz), historial)
    nuevo = _componer(origen, secciones, sin_asignar, comunes, historial, avisos)
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
            "motivo": "Propuesta de perfil a partir de la entrega vigente de S04."}]
    else:
        historial = previo["historial"]
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió la cita de origen (S04) desde la versión anterior del perfil.")
    if not origen["firmado"]:
        avisos.append("El perfil se basa en una cita no firmada.")
    secciones, sin_asignar, comunes, avisos_deriv = _derivar(_entrega_actual(raiz), historial)
    avisos.extend(avisos_deriv)
    contenido = _componer(origen, secciones, sin_asignar, comunes, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise PerfilError("El perfil está firmado y la cita de origen cambió. No se actualiza solo: "
                          "revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir síntesis, reasignar, revisar, firmar (US2, FR-007, FR-008) ----

def _seccion(contenido: Dict[str, Any], funcion: str) -> Dict[str, Any]:
    if funcion not in FUNCIONES:
        raise PerfilError(f"función no válida: {funcion} (use {', '.join(FUNCIONES)})")
    return next(s for s in contenido["secciones"] if s["funcion"] == funcion)


def corregir(raiz, funcion: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise PerfilError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    s = _seccion(contenido, funcion)
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "seccion": funcion,
          "campo": campo, "anterior": s[campo], "nuevo": nuevo_valor, "motivo": motivo}
    return _seccion(_guardar(raiz, contenido, ev), funcion)


def reasignar(raiz, cita_id: str, funcion: Optional[str], motivo: str, autor: str,
              fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if funcion is not None and funcion not in FUNCIONES:
        raise PerfilError(f"función no válida: {funcion} (use {', '.join(FUNCIONES)} o ninguna)")
    contenido = _cargar_vigente(raiz)
    if not any(x["id"] == cita_id for x in _entrega_actual(raiz)["citas"]):
        raise PerfilError(f"la cita {cita_id} no está en la entrega de S04")
    ev = {"tipo": "reasignacion", "autor": autor, "fecha": fecha or now_iso(), "cita": cita_id,
          "funcion": funcion, "anterior": None, "nuevo": funcion or "no asignado", "motivo": motivo}
    nuevo = _guardar(raiz, contenido, ev)
    return nuevo


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige la síntesis completa de las seis secciones."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise PerfilError("solo se firma un perfil «revisado»: registre una corrección o una revisión")
    vacias = [s["funcion"] for s in contenido["secciones"] if not s["sintesis"].strip()]
    if vacias:
        raise PerfilError("no se puede firmar: síntesis incompleta en " + ", ".join(vacias))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "secciones_al_firmar": len(contenido["secciones"]),
             "sin_asignar_al_firmar": len(contenido["sin_asignar"]),
             "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) ------------------------------

def _evidencias_alteradas(raiz, contenido: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    r = Path(raiz)
    secciones, evidencias = [], []
    for s in contenido["secciones"]:
        for ev in s["evidencias"]:
            if ev["copia"]:
                ruta, esperado = r / ev["copia"], ev["sha256_guardado"]
            else:
                ruta, esperado = r / ev["ubicacion_original"], ev["sha256_original"]
                if not ruta.is_file():
                    continue
            if not ruta.is_file() or sha256_file(ruta) != esperado:
                evidencias.append(ev["id"])
                if s["funcion"] not in secciones:
                    secciones.append(s["funcion"])
    return secciones, sorted(set(evidencias))


def _riesgos_no_vigentes(raiz, contenido: Dict[str, Any]) -> List[str]:
    vigentes = {x["id"] for x in _entrega_actual(raiz)["citas"]}
    return [x["cita"] for s in contenido["secciones"] for x in s["riesgos"] if x["cita"] not in vigentes]


def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise PerfilError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"secciones": [], "origen": {}}
        ilegible = True
    secciones_alteradas, evidencias = _evidencias_alteradas(raiz, contenido)
    no_vigentes = _riesgos_no_vigentes(raiz, contenido) if contenido["secciones"] else []
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["cita"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except cita.CitaError:
            entrega_ok = False
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "secciones_alteradas": secciones_alteradas,
                         "evidencias_alteradas": evidencias, "riesgos_no_vigentes": no_vigentes}
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
    if r["estado"] == "firmado" and (secciones_alteradas or no_vigentes or not entrega_ok):
        partes = []
        if secciones_alteradas:
            partes.append("evidencia alterada")
        if no_vigentes:
            partes.append("riesgo no vigente")
        if not entrega_ok:
            partes.append("origen cambiado")
        r["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        r["estado_informado"] = r["estado"]
    r["integro"] = (not secciones_alteradas and not no_vigentes and entrega_ok
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
    """Lo que recibe S06: las seis secciones con sus riesgos citados vigentes (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    secciones_alteradas = set(v["secciones_alteradas"])
    no_vigentes = set(v["riesgos_no_vigentes"])
    secciones = []
    for s in contenido["secciones"]:
        riesgos = [x for x in s["riesgos"] if x["cita"] not in no_vigentes]
        secciones.append({"id": s["id"], "funcion": s["funcion"], "sintesis": s["sintesis"],
                          "riesgos": riesgos, "vacios": s["vacios"],
                          "evidencias": s["evidencias"],
                          "marcas": ([MARCA_ALTERADA] if s["funcion"] in secciones_alteradas else [])})
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "origen": contenido["origen"], "secciones": secciones,
            "sin_asignar": [x for x in contenido["sin_asignar"] if x["id"] not in no_vigentes],
            "vacios_comunes": contenido["vacios_comunes"]}


# --- Vista legible y fichas (FR-012, principio VIII) -------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def _ficha(s: Dict[str, Any]) -> str:
    riesgos = "\n".join(f"- `{x['cita']}` ({x['riesgo']['id']}) · {x['marco']} {x['version']} · "
                        f"`{x['identificador']}` ({x['estado_identificador']})" for x in s["riesgos"]) or "- —"
    vacios = "\n".join(f"- `{v['id']}` · {v['dominio']['valor']} · {v['motivo']}" for v in s["vacios"]) or "- —"
    if s["correcciones"]:
        correcciones = "\n".join(f"- {x['fecha']} · {x['autor']} · «{x['anterior']}» → "
                                 f"«{x['nuevo']}» · {x['motivo']}" for x in s["correcciones"])
    else:
        correcciones = "Sin correcciones."
    return f"""# Perfil — función {s['funcion']}

> Producto de la herramienta C4A (S05 — El perfil). La herramienta propone; el auditor corrige y firma.
> {NOTA_VACIO}

- **Función**: {s['funcion']} (NIST CSF 2.0)
- **Estado de aprobación**: {s['estado_aprobacion']}

## Síntesis (la completa el auditor)

{s['sintesis'] or '— (pendiente de síntesis del auditor)'}

## Riesgos citados ({len(s['riesgos'])})

{riesgos}

## Vacíos de la función ({len(s['vacios'])})

{vacios}

## Correcciones ({len(s['correcciones'])})

{correcciones}
"""


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    secciones_alteradas = set(v["secciones_alteradas"])
    sin_material = [s for s in contenido["secciones"] if not s["riesgos"]]
    L = [f"# El perfil (S05) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         f"> {NOTA_VACIO}", "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Cita de origen**: `{origen['archivo']}` · huella {_celda(origen['sha256'])} · "
          + ("firmada" if origen["firmado"] else "**cita no firmada**"),
          f"- **Resumen**: {len(contenido['secciones'])} funciones · "
          f"{len(contenido['secciones']) - len(sin_material)} con material · {len(sin_material)} «no consta» · "
          f"{len(contenido['sin_asignar'])} riesgos sin asignar · {len(contenido['vacios_comunes'])} vacíos comunes.",
          "", f"## Funciones «no consta» ({len(sin_material)})", ""]
    if sin_material:
        L += ["| Función | Motivo |", "|---|---|"]
        for s in sin_material:
            motivos = "; ".join(s["falta"]) or "sin material en la entrega de S04"
            L.append(f"| {s['funcion']} | {_celda(motivos)} |")
    else:
        L.append("Ninguna.")
    for s in contenido["secciones"]:
        L += ["", f"## {s['funcion']} — {len(s['riesgos'])} riesgo(s) citado(s)", "",
              f"Síntesis: {_celda(s['sintesis'])}", ""]
        if s["riesgos"]:
            L += ["| Cita | Riesgo | Marco | Identificador |", "|---|---|---|---|"]
            for x in s["riesgos"]:
                L.append(f"| `{x['cita']}` | `{x['riesgo']['id']}` | "
                         f"{_celda(x['marco'] + ' ' + x['version'])} | `{_celda(x['identificador'])}` |")
        else:
            L.append("Sin riesgos citados.")
        if s["vacios"]:
            L += ["", "Vacíos:", ""] + [f"- `{x['id']}` · {_celda(x['dominio']['valor'])} · "
                                        f"{_celda(x['motivo'])}" for x in s["vacios"]]
    if contenido["sin_asignar"]:
        L += ["", f"## Riesgos sin asignar ({len(contenido['sin_asignar'])})", ""]
        L += [f"- `{x['id']}` · {x['riesgo']['id']}" for x in contenido["sin_asignar"]]
    if contenido["vacios_comunes"]:
        L += ["", f"## Vacíos sin función derivable ({len(contenido['vacios_comunes'])})", ""]
        L += [f"- `{x['id']}` · {_celda(x['dominio']['valor'])} · {_celda(x['motivo'])}"
              for x in contenido["vacios_comunes"]]
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Sección | Cita | Nuevo | Motivo |", "|---|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('seccion'))} | "
                     f"{_celda(e.get('cita'))} | {_celda(e.get('nuevo'))} | {_celda(e.get('motivo'))} |")
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
    for s in contenido["secciones"]:
        (p["raiz"] / f"{PREFIJO_FICHA}{_slug(s['funcion'])}.md").write_bytes(
            _ficha(s).encode("utf-8"))
    return p["md"]
