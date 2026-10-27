"""S09 — El borrador: el informe de cierre ensamblado desde las entregas S01–S08.

La herramienta ABRE el borrador a partir de la entrega de S08 (`frases.entregar`) y
ENSAMBLA las secciones del informe de cierre, cada una derivada de la entrega que la
sostiene y citando su huella (FR-004): encabezado (cliente y alcance), resumen para la
gerencia (la frase de gerencia), desarrollo (riesgos citados, perfil por funciones y
lista CIS), acciones sugeridas para quien corrige (la frase técnica y las condiciones),
vacíos declarados y anexo de trazabilidad (huellas de la cadena). El auditor CORRIGE con
motivo —una corrección que contradice su entrega de origen se rechaza (FR-007)—, REVISA
y FIRMA (principio I). El borrador no dictamina: presenta el trabajo hecho, sin estados
de cumplimiento y sin responsables ni fechas inventados (FR-006). Solo escribe archivos
nuevos en `04_informe/`: los informes previos de la carpeta quedan intactos (FR-011).

Archivos que produce:
  - 04_informe/borrador_s09.json        contenido canónico (lo que se firma)
  - 04_informe/borrador_s09.firma.json  firma: firmante, fecha, justificación y huella
  - 04_informe/borrador-informe-cierre.md  informe legible, mismo contenido que el JSON

Reglas de diseño (misma forma que S03–S08): el historial es la fuente, nada se borra
(FR-007), el resultado es determinista (FR-010) y firmar exige todas las secciones
completas (FR-008).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import alcance
from . import cita
from . import encargo
from . import frases
from . import lista
from . import perfil
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S09 — El borrador"
VERSION_ESQUEMA = "1"
CLIENTE = "Comercial Andes Sur SpA"

APROBACION = ("borrador", "revisado")
EVENTOS = ("propuesta", "correccion", "revision", "firma_anulada")

NOTA_FIRMA = "Firmar el borrador no abre la compuerta de autorización."
NOTA_BORRADOR = ("El borrador presenta el trabajo registrado y citado: no contiene "
                 "conclusiones de cumplimiento ni responsables ni fechas inventados.")

ARCHIVO_JSON = "04_informe/borrador_s09.json"
ARCHIVO_MD = "04_informe/borrador-informe-cierre.md"
ARCHIVO_FIRMA = "04_informe/borrador_s09.firma.json"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

SECCIONES = ("encabezado", "resumen", "desarrollo", "acciones", "vacios", "anexo")


class BorradorError(Exception):
    """Operación rechazada. `codigo`: 1 regla, 2 falta S08, 4 origen cambió."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "frases": r / frases.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise BorradorError(f"no existe {ARCHIVO_JSON}: ejecute primero «borrador abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise BorradorError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise BorradorError(f"{nombre} contiene {clase}: el borrador no lo admite (FR-016)")
    return alcance.limpiar(v)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return frases.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["frases"].exists():
        raise BorradorError(f"no existe {frases.ARCHIVO_JSON}: falta el producto anterior de S08; "
                            "ejecute primero «frases abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": frases.ARCHIVO_JSON,
            "sha256": sha256_file(p["frases"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": bool(entrega["firmado"]),
            "estado": entrega["estado"],
            "cadena": {s: c["firmado"] for s, c in entrega["origen"]["cadena"].items()}}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["frases"].exists():
        return True
    if sha256_file(p["frases"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise BorradorError("las frases de origen (S08) cambiaron desde que se abrió el borrador: "
                            "ejecute «borrador abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Ensamblaje de secciones (FR-003, FR-004, FR-005) ------------------------

def _seccion(nombre: str, contenido: str, huella: str, origen: str) -> Dict[str, Any]:
    return {"id": short_id("B", nombre), "nombre": nombre, "contenido": contenido,
            "huella_origen": huella, "origen": origen, "estado_aprobacion": "borrador",
            "correcciones": []}


def _ensamblar(raiz, frases_entrega: Dict[str, Any]) -> List[Dict[str, Any]]:
    r = Path(raiz)
    enc = encargo.cargar(raiz)
    resumen = enc.get("resumen", {})
    activo = resumen.get("activo", "el activo")
    conteos = frases_entrega["conteos"]
    # encabezado
    alcance_sha = sha256_file(r / alcance.ARCHIVO_JSON)
    encabezado = (f"Informe de cierre — {CLIENTE}\n\n"
                  f"Activo auditado: {activo}.\n"
                  f"Alcance: `scope/alcance_s01.json` (huella `{alcance_sha}`).\n"
                  f"Cliente: {CLIENTE}.\n"
                  f"Cadena de productos: S01–S08, con huellas en el anexo de trazabilidad.")
    # desarrollo
    citas = cita.cargar(raiz)["citas"]
    lineas_citas = "\n".join(f"- `{x['id']}` · {x['riesgo']['condicion']} · {x['marco']} "
                             f"{x['version']} · `{x['identificador']}` ({x['estado_identificador']})"
                             for x in citas) or "- no consta: sin riesgos citados."
    per = perfil.cargar(raiz)["secciones"]
    lineas_perfil = "\n".join(f"- {s['funcion']}: {len(s['riesgos'])} riesgo(s) citado(s)"
                              + ("" if s["sintesis"].strip() else " · «no consta»") for s in per)
    lis = lista.cargar(raiz)["filas"]
    seleccionados = [f for f in lis if f["estado_aplicabilidad"] != "descartado"]
    lineas_lista = "\n".join(f"- {f['control']} ({f['estado_confirmacion']})" for f in seleccionados) \
        or "- no consta: sin controles seleccionados."
    desarrollo = (
        f"Riesgos citados ({conteos['riesgos']}):\n{lineas_citas}\n\n"
        f"Perfil por funciones del NIST CSF 2.0:\n{lineas_perfil}\n\n"
        f"Controles CIS propuestos ({conteos['controles']}, {conteos['pendientes']} pendientes):\n"
        f"{lineas_lista}")
    # acciones sugeridas: frase técnica + condiciones del encargo, sin responsables ni fechas
    condiciones = [p for p in enc["pasos"] if p["repetibilidad"] == "condicionada"]
    lineas_cond = "\n".join(f"- Verificar según el paso `{p['id']}`: {p['descripcion']}"
                            for p in condiciones) or "- Sin condiciones pendientes."
    acciones = (frases_entrega["tecnica"] + "\n\nAcciones sugeridas para quien corrige "
                "(sin responsables ni fechas: los define quien ejecuta):\n" + lineas_cond)
    # vacíos
    causas = "; ".join(resumen.get("vacios_causas", [])) or "sin causa registrada"
    vacios = (f"Vacíos declarados: {conteos['vacios']}.\nCausas: {causas}.\n"
              "Los vacíos no se presentan como resultado favorable: son trabajo pendiente.")
    # anexo
    archivos = [alcance.ARCHIVO_JSON, registro.ARCHIVO_JSON, enunciado_archivo(),
                cita.ARCHIVO_JSON, perfil.ARCHIVO_JSON, lista.ARCHIVO_JSON,
                encargo.ARCHIVO_JSON, frases.ARCHIVO_JSON]
    lineas_anexo = "\n".join(f"- `{a}` · `{sha256_file(r / a)}`" for a in archivos)
    anexo = ("Trazabilidad de las entregas de las que deriva este borrador (huellas SHA-256 "
             "sobre los bytes guardados):\n" + lineas_anexo)
    return [
        _seccion("encabezado", encabezado, alcance_sha, "S01 (alcance)"),
        _seccion("resumen", frases_entrega["gerencia"],
                 frases_entrega["origen"]["sha256"], "S08 (frases de gerencia)"),
        _seccion("desarrollo", desarrollo, sha256_file(r / cita.ARCHIVO_JSON),
                 "S04/S05/S06 (cita, perfil, lista)"),
        _seccion("acciones", acciones, frases_entrega["origen"]["sha256"],
                 "S08 (frase técnica) y S07 (condiciones)"),
        _seccion("vacios", vacios, encargo_archivo_huella(r), "S07 (resumen del encargo)"),
        _seccion("anexo", anexo, frases_entrega["origen"]["entrega_sha256"], "S01–S08"),
    ]


def enunciado_archivo() -> str:
    return "03_hallazgos/enunciados_s03.json"


def encargo_archivo_huella(r: Path) -> str:
    return sha256_file(r / encargo.ARCHIVO_JSON)


def _derivar(raiz, historial: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    secciones = _ensamblar(raiz, _entrega_actual(raiz))
    por_nombre = {s["nombre"]: s for s in secciones}
    for ev in historial:
        if ev["tipo"] == "correccion":
            s = por_nombre.get(ev["seccion"])
            if s is None:
                continue
            s["contenido"] = ev["nuevo"]
            s["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"],
                                      "motivo": ev["motivo"]})
            s["estado_aprobacion"] = "revisado"
    return [por_nombre[n] for n in SECCIONES]


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, secciones, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "cliente": CLIENTE, "secciones": secciones,
            "estado_aprobacion": _estado(historial), "historial": historial, "avisos": avisos}


# --- Contradicción con el origen (FR-007) ------------------------------------

def _contradicciones(contenido: Dict[str, Any], frases_entrega: Dict[str, Any]) -> List[str]:
    """Una corrección no puede contradecir su entrega de origen: conteos de riesgos y
    vacíos deben mantenerse en resumen y acciones; toda sección debe seguir completa."""
    problemas: List[str] = []
    conteos = frases_entrega["conteos"]
    for nombre in ("resumen", "acciones"):
        s = next(x for x in contenido["secciones"] if x["nombre"] == nombre)
        numeros_riesgos = re.findall(r"(\d+)\s+riesgos", s["contenido"])
        numeros_vacios = re.findall(r"(\d+)\s+vacío[s]?", s["contenido"])
        if nombre == "resumen" and numeros_riesgos and numeros_riesgos != [str(conteos["riesgos"])]:
            problemas.append(f"{nombre}: conteo de riesgos contradice la entrega de S08 "
                             f"({frases_entrega['origen']['sha256'][:12]}…)")
        if numeros_vacios and numeros_vacios != [str(conteos["vacios"])]:
            problemas.append(f"{nombre}: conteo de vacíos contradice la entrega de S08 "
                             f"({frases_entrega['origen']['sha256'][:12]}…)")
    return problemas


# --- Abrir (US1, FR-001, FR-014) ----------------------------------------------

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
    secciones = _derivar(raiz, historial)
    nuevo = _componer(origen, secciones, historial, contenido["avisos"])
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
            "motivo": "Ensamblaje del borrador a partir de la entrega vigente de S08."}]
    else:
        historial = previo["historial"]
        if _origen_cambio(raiz, previo):
            avisos.append("Cambiaron las frases de origen (S08) desde la versión anterior del borrador.")
    secciones = _derivar(raiz, historial)
    contenido = _componer(origen, secciones, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise BorradorError("El borrador está firmado y las frases de origen cambiaron. No se "
                            "actualiza solo: revise y vuelva a firmar a partir de un cambio "
                            "explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, revisar, firmar (US2, FR-007, FR-008) ---------------------------

def corregir(raiz, seccion: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if seccion not in SECCIONES:
        raise BorradorError(f"sección no válida: {seccion} (use {', '.join(SECCIONES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    if re.search(r"(?i)\b(puerto\s*:?\s*\d{1,5})\b", nuevo_valor):
        raise BorradorError("las acciones sugeridas no admiten números de puerto ni responsables "
                            "ni fechas inventados (FR-006)")
    contenido = _cargar_vigente(raiz)
    propuesto = json.loads(alcance.serializar(contenido))
    next(s for s in propuesto["secciones"] if s["nombre"] == seccion)["contenido"] = nuevo_valor
    problemas = _contradicciones(propuesto, _entrega_actual(raiz))
    if problemas:
        raise BorradorError("la corrección contradice su entrega de origen: " + "; ".join(problemas))
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "seccion": seccion,
          "anterior": next(s for s in contenido["secciones"] if s["nombre"] == seccion)["contenido"],
          "nuevo": nuevo_valor, "motivo": motivo}
    return next(s for s in _guardar(raiz, contenido, ev)["secciones"] if s["nombre"] == seccion)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige todas las secciones completas."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise BorradorError("solo se firma un borrador «revisado»: registre una corrección o una revisión")
    incompletas = [s["nombre"] for s in contenido["secciones"] if not s["contenido"].strip()]
    if incompletas:
        raise BorradorError("no se puede firmar: secciones incompletas en " + ", ".join(incompletas))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "secciones_al_firmar": len(contenido["secciones"]), "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) --------------------------------

def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise BorradorError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"secciones": [], "origen": {}}
        ilegible = True
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["frases"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except frases.FrasesError:
            entrega_ok = False
    anexo_rotos: List[str] = []
    if not ilegible:
        r = Path(raiz)
        anexo = next((s for s in contenido["secciones"] if s["nombre"] == "anexo"), None)
        if anexo:
            for m in re.finditer(r"`([^`]+\.json)` · `([0-9a-f]{64})`", anexo["contenido"]):
                archivo, huella = m.group(1), m.group(2)
                if not (r / archivo).is_file() or sha256_file(r / archivo) != huella:
                    anexo_rotos.append(archivo)
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "anexo_rotos": anexo_rotos}
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
    if r["estado"] == "firmado" and (anexo_rotos or not entrega_ok):
        partes = []
        if anexo_rotos:
            partes.append("anexo con enlaces rotos")
        if not entrega_ok:
            partes.append("origen cambiado")
        r["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        r["estado_informado"] = r["estado"]
    r["integro"] = (not anexo_rotos and entrega_ok and not r["estado"].startswith("revisado"))
    return r


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


def entregar(raiz) -> Dict[str, Any]:
    """Lo que recibe S10: el borrador completo con las huellas de S01–S08 (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "cliente": contenido["cliente"], "origen": contenido["origen"],
            "secciones": contenido["secciones"], "anexo_rotos": v["anexo_rotos"]}


# --- Vista legible (FR-012, principio VIII) -------------------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    partes: List[str] = []
    for s in contenido["secciones"]:
        partes.append(s["contenido"])
    informe = "\n\n---\n\n".join(partes)
    cabecera = (f"> Borrador del informe de cierre — {CLIENTE}. Producto de la herramienta C4A: "
                f"propone; el auditor corrige y firma.\n> {NOTA_BORRADOR}\n\n"
                f"- Estado: {estado} · huella `{v['sha256_actual']}`\n"
                f"- Origen: `{origen['archivo']}` (huella `{origen['sha256']}`)\n\n---\n\n")
    return cabecera + informe + "\n"


def escribir_vista(raiz) -> Path:
    p = _rutas(raiz)
    p["md"].write_bytes(vista(raiz).encode("utf-8"))
    return p["md"]
