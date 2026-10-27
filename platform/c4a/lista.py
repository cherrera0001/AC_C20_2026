"""S06 — La lista: los CIS Controls que aplican, partiendo por el inventario.

La herramienta ABRE la lista a partir de la entrega de S05 (`perfil.entregar`) y del
inventario que la sostiene (los hechos vigentes del registro de S02, organizados por el
perfil), PROPONE los controles CIS Controls v8.1 aplicables como sugerencia explicada:
cada propuesta cita sus anclas —hechos o vacíos del inventario— y los controles que
requieren políticas, personas o procesos quedan «pendiente-documental». El auditor
CORRIGE justificaciones, DESCARTA y RECUPERA, AÑADE controles a mano con fuente, REVISA
y FIRMA (principio I). Una lista no dictamina: seleccionar un control no es prueba de
incumplimiento ni de cobertura (FR-006). Nada de este módulo abre la compuerta ni escribe
fuera de `03_hallazgos/`.

Archivos que produce:
  - 03_hallazgos/lista_s06.json        contenido canónico (lo que se firma)
  - 03_hallazgos/lista_s06.firma.json  firma: firmante, fecha, justificación y huella
  - 03_hallazgos/lista_s06.md          vista legible para un tercero
  - 03_hallazgos/lista-<id>.md         una ficha legible por fila (FR-012)

Reglas de diseño (misma forma que S03–S05): el historial es la fuente, nada se borra
(FR-007), el resultado es determinista (FR-010) y firmar exige justificación completa en
cada fila seleccionada (FR-008).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from . import perfil
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S06 — La lista"
VERSION_ESQUEMA = "1"
MARCO = "CIS Controls"
VERSION = "v8.1"

APROBACION = ("borrador", "revisado")
CAMPOS_CORREGIBLES = ("justificacion",)
EVENTOS = ("propuesta", "correccion", "alta", "descarte", "recuperacion", "revision", "firma_anulada")

EST_APLICABILIDAD = ("propuesto", "seleccionado", "descartado")
CONF_CONFIRMADO = "confirmado"
CONF_PENDIENTE = "pendiente-confirmar"
CONF_DOCUMENTAL = "pendiente-documental"

MARCA_DESCARTADO = "descartado"
MARCA_ALTERADA = "evidencia alterada"
MARCA_ANCLA_NO_VIGENTE = "ancla no vigente"

NOTA_FIRMA = "Firmar la lista no abre la compuerta de autorización."
NOTA_LISTA = ("La aplicabilidad de un control se propone como sugerencia explicada anclada en "
              "el inventario: no es prueba de incumplimiento ni de cobertura.")

ARCHIVO_JSON = "03_hallazgos/lista_s06.json"
ARCHIVO_MD = "03_hallazgos/lista_s06.md"
ARCHIVO_FIRMA = "03_hallazgos/lista_s06.firma.json"
PREFIJO_FICHA = "03_hallazgos/lista-"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

_KNOWLEDGE = Path(__file__).resolve().parent / "knowledge"


class ListaError(Exception):
    """Operación rechazada. `codigo` sigue el contrato del subcomando `lista`."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


def _catalogo() -> Dict[str, Dict[str, Any]]:
    try:
        data = json.loads((_KNOWLEDGE / "controls_cis.json").read_text(encoding="utf-8"))
    except OSError:
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "perfil": r / perfil.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise ListaError(f"no existe {ARCHIVO_JSON}: ejecute primero «lista abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise ListaError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise ListaError(f"{nombre} contiene {clase}: la lista no lo admite (FR-016)")
    return alcance.limpiar(v)


def id_fila(control: str, identificador: str) -> str:
    return short_id("L", MARCO, VERSION, control, identificador)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return perfil.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["perfil"].exists():
        raise ListaError(f"no existe {perfil.ARCHIVO_JSON}: falta el producto anterior de S05; "
                         "ejecute primero «perfil abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": perfil.ARCHIVO_JSON,
            "sha256": sha256_file(p["perfil"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": bool(entrega["firmado"]),
            "estado": entrega["estado"]}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["perfil"].exists():
        return True
    if sha256_file(p["perfil"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise ListaError("el perfil de origen (S05) cambió desde que se abrió la lista: "
                         "ejecute «lista abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Derivación: entrega + historial → filas (FR-003 a FR-005) --------------

def _terminos(texto: str) -> set:
    return {t for t in alcance._norm(texto).split() if len(t) >= 4}


def _materiales(entrega: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Anclas posibles: riesgos citados y vacíos, con el texto que alimenta la propuesta."""
    out: List[Dict[str, Any]] = []
    for s in entrega["secciones"]:
        for x in s["riesgos"]:
            out.append({"tipo": "riesgo", "id": x["cita"], "funcion": s["funcion"],
                        "texto": " ".join([s["funcion"], x["riesgo"].get("condicion", "")])})
        for v in s["vacios"]:
            out.append({"tipo": "vacio", "id": v["id"], "funcion": s["funcion"],
                        "texto": " ".join([s["funcion"], v["dominio"]["valor"], v.get("motivo") or ""])})
    for x in entrega.get("sin_asignar", []):
        out.append({"tipo": "riesgo", "id": x["id"], "funcion": None,
                    "texto": x["riesgo"].get("condicion", "")})
    for v in entrega.get("vacios_comunes", []):
        out.append({"tipo": "vacio", "id": v["id"], "funcion": None,
                    "texto": " ".join([v["dominio"]["valor"], v.get("motivo") or ""])})
    return out


def _proponer(entrega: Dict[str, Any]) -> List[Dict[str, Any]]:
    catalogo = _catalogo()
    materiales = _materiales(entrega)
    filas: Dict[str, Dict[str, Any]] = {}
    for numero, ctrl in sorted(catalogo.items()):
        terminos = _terminos(ctrl.get("terminos", "") + " " + ctrl.get("titulo", ""))
        anclas = [m for m in materiales if terminos & _terminos(m["texto"])]
        if not anclas:
            continue
        evidencias = sorted({ev["id"]: ev for s in entrega["secciones"] if any(
            a["tipo"] == "riesgo" and a["id"] in {r["cita"] for r in s["riesgos"]} for a in anclas)
            for ev in s["evidencias"]}.values(), key=lambda e: e["id"])
        documental = bool(ctrl.get("documental"))
        fid = id_fila(numero, ctrl["titulo"])
        filas[fid] = {
            "id": fid,
            "control": f"Control {numero}: {ctrl['titulo']}",
            "identificador": numero,
            "marco": MARCO,
            "version": VERSION,
            "justificacion": (f"Se propone porque el inventario y el perfil tratan «{ctrl['titulo'].lower()}»: "
                              + "; ".join(f"{a['tipo']} {a['id']}" for a in anclas[:3])
                              + ". Sugerencia explicada, no dictamen."),
            "anclajes": [{"tipo": a["tipo"], "id": a["id"], "texto": a["texto"][:200]} for a in anclas],
            "estado_aplicabilidad": "propuesto",
            "estado_confirmacion": CONF_DOCUMENTAL if documental else CONF_CONFIRMADO,
            "evidencias": evidencias,
            "estado_aprobacion": "borrador",
            "marcas": [],
            "correcciones": [],
            "fuente": None,
        }
    return sorted(filas.values(), key=lambda f: f["id"])


def _derivar(entrega: Dict[str, Any], historial: List[Dict[str, Any]]) -> Tuple[List[Dict], List[str]]:
    filas = {f["id"]: f for f in _proponer(entrega)}
    avisos: List[str] = []
    for ev in historial:
        if ev["tipo"] == "correccion":
            f = filas.get(ev["fila"])
            if f is None:
                continue
            f[ev["campo"]] = ev["nuevo"]
            f["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": ev["campo"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"], "motivo": ev["motivo"]})
            f["estado_aprobacion"] = "revisado"
        elif ev["tipo"] == "alta":
            f = dict(ev["fila_nueva"])
            f["correcciones"] = [{"autor": ev["autor"], "fecha": ev["fecha"], "campo": "alta",
                                  "anterior": "", "nuevo": f["control"], "motivo": ev["motivo"]}]
            filas[f["id"]] = f
        elif ev["tipo"] in ("descarte", "recuperacion"):
            f = filas.get(ev["fila"])
            if f is None:
                continue
            f["estado_aplicabilidad"] = "descartado" if ev["tipo"] == "descarte" else "seleccionado"
            f["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": "aplicabilidad",
                                      "anterior": ev["anterior"], "nuevo": f["estado_aplicabilidad"],
                                      "motivo": ev["motivo"]})
            f["estado_aprobacion"] = "revisado"
    if not filas:
        avisos.append("Sin catálogo o sin anclajes: la lista queda vacía; el auditor puede añadir "
                      "controles a mano con fuente.")
    return sorted(filas.values(), key=lambda f: f["id"]), avisos


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "alta", "descarte", "recuperacion", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, filas, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "filas": filas, "estado_aprobacion": _estado(historial), "historial": historial,
            "avisos": avisos}


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
    filas, avisos = _derivar(_entrega_actual(raiz), historial)
    nuevo = _componer(origen, filas, historial, avisos)
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
            "motivo": "Propuesta de controles CIS aplicables a partir del inventario y el perfil."}]
    else:
        historial = previo["historial"]
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió el perfil de origen (S05) desde la versión anterior de la lista.")
    if not origen["firmado"]:
        avisos.append("La lista se basa en un perfil no firmado.")
    filas, avisos_deriv = _derivar(_entrega_actual(raiz), historial)
    avisos.extend(avisos_deriv)
    contenido = _componer(origen, filas, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise ListaError("La lista está firmada y el perfil de origen cambió. No se actualiza solo: "
                         "revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, alta, descartar, recuperar, revisar, firmar (US2, FR-007/8) --

def _fila(contenido: Dict[str, Any], fila: str) -> Dict[str, Any]:
    f = next((x for x in contenido["filas"] if x["id"] == fila), None)
    if f is None:
        raise ListaError(f"no existe la fila {fila}")
    return f


def corregir(raiz, fila: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise ListaError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    f = _fila(contenido, fila)
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "fila": fila,
          "campo": campo, "anterior": f[campo], "nuevo": nuevo_valor, "motivo": motivo}
    return _fila(_guardar(raiz, contenido, ev), fila)


def anadir(raiz, control: str, identificador: str, justificacion: str, fuente: str,
           motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Alta a mano: exige justificación y fuente; queda «pendiente-confirmar»."""
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    control_l = _texto_libre(control, "el control")
    ident_l = _texto_libre(identificador, "el identificador")
    just_l = _texto_libre(justificacion, "la justificación")
    fuente_l = _texto_libre(fuente, "la fuente")
    contenido = _cargar_vigente(raiz)
    fid = id_fila(control_l, ident_l)
    if any(x["id"] == fid for x in contenido["filas"]):
        raise ListaError(f"ya existe la fila {fid}")
    fila_nueva = {"id": fid, "control": control_l, "identificador": ident_l, "marco": MARCO,
                  "version": VERSION, "justificacion": just_l,
                  "anclajes": [], "estado_aplicabilidad": "seleccionado",
                  "estado_confirmacion": CONF_PENDIENTE, "evidencias": [],
                  "estado_aprobacion": "revisado", "marcas": [], "correcciones": [],
                  "fuente": fuente_l}
    ev = {"tipo": "alta", "autor": autor, "fecha": fecha or now_iso(), "fila_nueva": fila_nueva,
          "motivo": motivo}
    return _fila(_guardar(raiz, contenido, ev), fid)


def _marcar(raiz, tipo: str, fila: str, motivo: str, autor: str, fecha: Optional[str]) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    f = _fila(contenido, fila)
    descartado = f["estado_aplicabilidad"] == "descartado"
    if tipo == "descarte" and descartado:
        raise ListaError(f"la fila {fila} ya está descartada")
    if tipo == "recuperacion" and not descartado:
        raise ListaError(f"la fila {fila} no está descartada: no hay nada que recuperar")
    ev = {"tipo": tipo, "autor": autor, "fecha": fecha or now_iso(), "fila": fila,
          "anterior": "descartado" if descartado else "seleccionado",
          "nuevo": "seleccionado" if descartado else "descartado", "motivo": motivo}
    return _fila(_guardar(raiz, contenido, ev), fila)


def descartar(raiz, fila: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "descarte", fila, motivo, autor, fecha)


def recuperar(raiz, fila: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "recuperacion", fila, motivo, autor, fecha)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige justificación completa en cada seleccionado."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise ListaError("solo se firma una lista «revisada»: registre una corrección o una revisión")
    incompletas = [f["id"] for f in contenido["filas"]
                   if f["estado_aplicabilidad"] != "descartado" and not f["justificacion"].strip()]
    if incompletas:
        raise ListaError("no se puede firmar: justificación incompleta en " + ", ".join(incompletas))
    p = _rutas(raiz)
    seleccionados = [f for f in contenido["filas"] if f["estado_aplicabilidad"] != "descartado"]
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "filas_al_firmar": len(contenido["filas"]),
             "seleccionados_al_firmar": len(seleccionados),
             "pendientes_al_firmar": sum(1 for f in seleccionados if f["estado_confirmacion"] != CONF_CONFIRMADO),
             "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) ------------------------------

def _ids_entrega(raiz) -> Tuple[set, set, Dict[str, List[Dict[str, Any]]]]:
    entrega = _entrega_actual(raiz)
    riesgos = {x["cita"] for s in entrega["secciones"] for x in s["riesgos"]} | \
              {x["id"] for x in entrega.get("sin_asignar", [])}
    vacios = {v["id"] for s in entrega["secciones"] for v in s["vacios"]} | \
             {v["id"] for v in entrega.get("vacios_comunes", [])}
    evidencias = {ev["id"]: ev for s in entrega["secciones"] for ev in s["evidencias"]}
    return riesgos, vacios, evidencias


def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise ListaError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"filas": [], "origen": {}}
        ilegible = True
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["perfil"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except perfil.PerfilError:
            entrega_ok = False
    filas_alteradas, filas_ancla, evidencias_alteradas = [], [], []
    if not ilegible:
        try:
            riesgos_ids, vacios_ids, ev_map = _ids_entrega(raiz)
        except perfil.PerfilError:
            riesgos_ids, vacios_ids, ev_map = set(), set(), {}
        r = Path(raiz)
        for f in contenido["filas"]:
            anclas_rotas = [a for a in f["anclajes"]
                            if (a["tipo"] == "riesgo" and a["id"] not in riesgos_ids)
                            or (a["tipo"] == "vacio" and a["id"] not in vacios_ids)]
            if anclas_rotas:
                filas_ancla.append(f["id"])
            for ev in f["evidencias"]:
                real = ev_map.get(ev["id"])
                if real is None:
                    continue
                if real.get("copia"):
                    ruta, esperado = r / real["copia"], real["sha256_guardado"]
                else:
                    ruta, esperado = r / real["ubicacion_original"], real["sha256_original"]
                    if not ruta.is_file():
                        continue
                if not ruta.is_file() or sha256_file(ruta) != esperado:
                    evidencias_alteradas.append(ev["id"])
                    if f["id"] not in filas_alteradas:
                        filas_alteradas.append(f["id"])
    v: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "filas_alteradas": sorted(filas_alteradas),
                         "evidencias_alteradas": sorted(set(evidencias_alteradas)),
                         "anclas_no_vigentes": sorted(filas_ancla)}
    if not p["firma"].exists():
        v["estado"] = "sin firma"
    else:
        firma = json.loads(p["firma"].read_bytes().decode("utf-8"))
        v["sha256_firmado"] = firma.get("sha256")
        v["huella_ok"] = firma.get("sha256") == actual
        if v["huella_ok"]:
            v.update(estado="firmado", firmante=firma.get("firmante"), fecha=firma.get("fecha"),
                     motivo=firma.get("motivo"))
        else:
            v["estado"] = "revisado (firma no aplica)"
    if ilegible:
        v["estado"] = "revisado (json ilegible)"
        v["estado_informado"] = v["estado"]
        v["integro"] = False
        return v
    if v["estado"] == "firmado" and (filas_alteradas or filas_ancla or not entrega_ok):
        partes = []
        if filas_alteradas:
            partes.append("evidencia alterada")
        if filas_ancla:
            partes.append("ancla no vigente")
        if not entrega_ok:
            partes.append("origen cambiado")
        v["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        v["estado_informado"] = v["estado"]
    v["integro"] = (not filas_alteradas and not filas_ancla and entrega_ok
                    and not v["estado"].startswith("revisado"))
    return v


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


def entregar(raiz) -> Dict[str, Any]:
    """Lo que recibe S07: solo los controles seleccionados (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    alteradas = set(v["filas_alteradas"])
    anclas_rotas = set(v["anclas_no_vigentes"])
    salida = []
    for f in contenido["filas"]:
        if f["estado_aplicabilidad"] == "descartado" or f["id"] in alteradas or f["id"] in anclas_rotas:
            continue
        salida.append({k: f[k] for k in ("id", "control", "identificador", "marco", "version",
                                         "justificacion", "anclajes", "estado_confirmacion",
                                         "estado_aplicabilidad", "evidencias", "fuente")})
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "origen": contenido["origen"], "controles": salida,
            "contados": {"seleccionados": len(salida),
                         "pendientes": sum(1 for f in salida if f["estado_confirmacion"] != CONF_CONFIRMADO)}}


# --- Vista legible y fichas (FR-012, principio VIII) -------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def _ficha(f: Dict[str, Any]) -> str:
    anclas = "\n".join(f"- {a['tipo']} `{a['id']}` · {a['texto']}" for a in f["anclajes"]) or "- —"
    evs = "\n".join(f"- `{x['id']}` · {x['tipo']} · "
                    f"{x['copia'] or x['ubicacion_original'] + ' (sin copia)'} · "
                    f"`{x['sha256_guardado'] or x['sha256_original']}`" for x in f["evidencias"]) or "- —"
    correcciones = "\n".join(f"- {x['fecha']} · {x['autor']} · {x['campo']}: «{x['anterior']}» → "
                             f"«{x['nuevo']}» · {x['motivo']}" for x in f["correcciones"]) or "Sin correcciones."
    fuente = f"\n- **Fuente (alta manual)**: {f['fuente']}" if f.get("fuente") else ""
    return f"""# Lista — {f['control']}

> Producto de la herramienta C4A (S06 — La lista). La herramienta propone; el auditor corrige y firma.
> {NOTA_LISTA}

- **Marco**: {f['marco']} · **Versión**: {f['version']} · **Identificador**: `{f['identificador']}`
- **Aplicabilidad**: {f['estado_aplicabilidad']} · **Confirmación**: {f['estado_confirmacion']}
- **Estado de aprobación**: {f['estado_aprobacion']}{fuente}

## Justificación de aplicabilidad

{f['justificacion']}

## Anclajes en el inventario y el perfil

{anclas}

## Evidencias citadas (tipo · ubicación · huella)

{evs}

## Correcciones ({len(f['correcciones'])})

{correcciones}
"""


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    seleccionados = [f for f in contenido["filas"] if f["estado_aplicabilidad"] != "descartado"]
    pendientes = [f for f in seleccionados if f["estado_confirmacion"] != CONF_CONFIRMADO]
    L = [f"# La lista (S06) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         f"> {NOTA_LISTA}", "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Perfil de origen**: `{origen['archivo']}` · huella {_celda(origen['sha256'])} · "
          + ("firmado" if origen["firmado"] else "**perfil no firmado**"),
          f"- **Resumen**: {len(seleccionados)} seleccionados · {len(pendientes)} «pendiente» "
          f"(confirmar o documental) · {len(contenido['filas']) - len(seleccionados)} descartados.",
          "", f"## Pendientes ({len(pendientes)})", ""]
    if pendientes:
        L += ["| Fila | Control | Estado |", "|---|---|---|"]
        for f in pendientes:
            L.append(f"| `{f['id']}` | {_celda(f['control'])} | {f['estado_confirmacion']} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Controles seleccionados ({len(seleccionados)})", ""]
    if seleccionados:
        L += ["| Id | Control | Confirmación | Anclas |", "|---|---|---|---|"]
        for f in seleccionados:
            L.append(f"| `{f['id']}` | {_celda(f['control'])} | {f['estado_confirmacion']} | "
                     f"{len(f['anclajes'])} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Fila | Nuevo | Motivo |", "|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('fila'))} | "
                     f"{_celda(e.get('nuevo'))} | {_celda(e.get('motivo'))} |")
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
    for f in contenido["filas"]:
        (p["raiz"] / f"{PREFIJO_FICHA}{f['id']}.md").write_bytes(_ficha(f).encode("utf-8"))
    return p["md"]
