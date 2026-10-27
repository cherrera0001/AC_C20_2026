"""S04 — La cita: cada riesgo vigente ubicado en un marco, con nombre y versión.

La herramienta ABRE la cita a partir de la entrega de S03 (`enunciado.entregar`),
PROPONE una correspondencia riesgo ↔ control como sugerencia explicada (el identificador
solo se propone si consta en la base de conocimiento de la herramienta; si no, queda
«pendiente de confirmar», principio IV). El auditor CORRIGE, añade correspondencias,
DESCARTA, RESTABLECE, REVISA y FIRMA (principio I). Una cita no dictamina: ubicar un
riesgo en un control no concluye cumplimiento, y un marco mencionado no acredita
cobertura (FR-006). Nada de este módulo abre la compuerta ni escribe fuera de
`03_hallazgos/`.

Archivos que produce:
  - 03_hallazgos/citas_s04.json        contenido canónico (lo que se firma)
  - 03_hallazgos/citas_s04.firma.json  firma: firmante, fecha, justificación y huella
  - 03_hallazgos/citas_s04.md          vista legible para un tercero
  - 03_hallazgos/cita-<id>.md          una ficha legible por cita (FR-012)

Reglas de diseño (misma forma que S03):
  - El historial es la fuente: las citas se derivan de la entrega más el historial
    reaplicado en orden. Nada se borra (FR-007) y el resultado es determinista (FR-010).
  - El identificador de la cita deriva del riesgo, no del texto (FR-004).
  - Firmar exige marco y versión completos en cada cita vigente; el identificador puede
    quedar «pendiente de confirmar», declarado (FR-008).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from . import enunciado
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S04 — La cita"
VERSION_ESQUEMA = "1"

APROBACION = ("borrador", "revisado")
CAMPOS_CORREGIBLES = ("marco", "version", "identificador", "fundamento")
EVENTOS = ("propuesta", "correccion", "correspondencia", "descarte", "restablecimiento",
           "revision", "firma_anulada")

MARCO_DEFECTO = "ISO/IEC 27001"
VERSION_DEFECTO = "2022"
PENDIENTE = "pendiente-confirmar"
CONFIRMADO = "confirmado"

MARCA_DESCARTADO = "descartado"
MARCA_RIESGO_NO_VIGENTE = "riesgo no vigente"
MARCA_ALTERADA = "evidencia alterada"
MARCAS = (MARCA_DESCARTADO, MARCA_RIESGO_NO_VIGENTE, MARCA_ALTERADA)

NOTA_FIRMA = "Firmar la cita no abre la compuerta de autorización."
NOTA_CITA = ("La correspondencia riesgo ↔ control es una sugerencia explicada: no es prueba "
             "de incumplimiento, y un marco mencionado no acredita cobertura.")

ARCHIVO_JSON = "03_hallazgos/citas_s04.json"
ARCHIVO_MD = "03_hallazgos/citas_s04.md"
ARCHIVO_FIRMA = "03_hallazgos/citas_s04.firma.json"
PREFIJO_FICHA = "03_hallazgos/cita-"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

_KNOWLEDGE = Path(__file__).resolve().parent / "knowledge"


class CitaError(Exception):
    """Operación rechazada. `codigo` sigue el contrato del subcomando `cita`."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Base de conocimiento (principio IV: identificadores que constan) -------

def _catalogo() -> Dict[str, str]:
    """Identificadores conocidos → objetivo. Solo fuentes abiertas ya usadas por la plataforma."""
    try:
        data = json.loads((_KNOWLEDGE / "controls_iso27001.json").read_text(encoding="utf-8"))
    except OSError:
        return {}
    return {k: v.get("objetivo", "") for k, v in data.items() if not k.startswith("_")}


def identificador_confirmado(identificador: Optional[str]) -> bool:
    return bool(identificador) and identificador in _catalogo()


_STOPWORDS = set((
    "ante bajo con contra desde durante entre hacia hasta para por segun según sin sobre tras "
    "una unas uno unos unos el la los las de del al y o u en a como mas más menos muy su sus "
    "que se no si al uso usa usan ejemplo tipo texto riesgo riesgos cita citas marco controles "
    "control seguridad información informacion evidencia evidencias resultado resultados condicion "
    "consecuencia criterio impacto falta origen herramienta propuesta propuestas"
).split())


def _terminos(texto: str) -> set:
    return {t for t in alcance._norm(texto).split() if len(t) >= 4 and t not in _STOPWORDS}


def _proponer_control(texto: str) -> Tuple[Optional[str], str]:
    """→ (identificador, fundamento) o (None, fundamento genérico). Coincidencia por
    solapamiento de términos de contenido (sin palabras vacías) entre el texto del
    riesgo y el objetivo del control."""
    catalogo = _catalogo()
    if not catalogo:
        return None, ("Sin catálogo de controles en la herramienta: el identificador queda "
                      "«pendiente de confirmar» y la correspondencia se propone solo por el dominio.")
    terminos = _terminos(texto)
    mejor, puntaje = None, 0
    for ident, objetivo in catalogo.items():
        p = len(terminos & _terminos(objetivo))
        if p > puntaje:
            mejor, puntaje = ident, p
    if mejor is None:
        return None, ("Ningún control del catálogo se relaciona con el texto del riesgo: el "
                      "identificador queda «pendiente de confirmar».")
    return mejor, (f"El texto del riesgo se relaciona con el objetivo del control {mejor} "
                   f"(«{catalogo[mejor]}») por términos comunes. Es una sugerencia explicada, "
                   "no prueba de incumplimiento.")


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "enunciado": r / enunciado.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise CitaError(f"no existe {ARCHIVO_JSON}: ejecute primero «cita abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise CitaError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise CitaError(f"{nombre} contiene {clase}: la cita no lo admite (FR-016)")
    return alcance.limpiar(v)


def id_cita(riesgo_id: str) -> str:
    return short_id("C", riesgo_id)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return enunciado.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["enunciado"].exists():
        raise CitaError(f"no existe {enunciado.ARCHIVO_JSON}: falta el producto anterior de S03; "
                        "ejecute primero «enunciado abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": enunciado.ARCHIVO_JSON,
            "sha256": sha256_file(p["enunciado"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": bool(entrega["firmado"]),
            "estado": entrega["estado"]}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["enunciado"].exists():
        return True
    if sha256_file(p["enunciado"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise CitaError("el enunciado de origen (S03) cambió desde que se abrió la cita: "
                        "ejecute «cita abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Derivación: entrega + historial → citas (FR-003 a FR-005) --------------

def _proponer(riesgo: Dict[str, Any]) -> Dict[str, Any]:
    texto = " ".join([riesgo["dominio"]["valor"], riesgo["condicion"], riesgo["criterio"]])
    identificador, fundamento = _proponer_control(texto)
    return {
        "id": id_cita(riesgo["id"]),
        "riesgo": {"id": riesgo["id"], "condicion": riesgo["condicion"]},
        "marco": MARCO_DEFECTO,
        "version": VERSION_DEFECTO,
        "identificador": identificador or PENDIENTE,
        "estado_identificador": CONFIRMADO if identificador else PENDIENTE,
        "fundamento": fundamento,
        "correspondencias": [],
        "evidencias": list(riesgo["evidencias"]),
        "estado_aprobacion": "borrador",
        "marcas": [],
        "correcciones": [],
    }


def _reestado_identificador(c: Dict[str, Any]) -> None:
    if c["identificador"] == PENDIENTE:
        c["estado_identificador"] = PENDIENTE
    else:
        c["estado_identificador"] = CONFIRMADO if identificador_confirmado(c["identificador"]) else PENDIENTE


def _derivar(entrega: Dict[str, Any], historial: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], List[str]]:
    avisos: List[str] = []
    citas: Dict[str, Dict] = {}
    vistos = set()
    for riesgo in entrega["enunciados"]:
        cid = id_cita(riesgo["id"])
        if cid in vistos:
            avisos.append(f"La entrega repite el riesgo {riesgo['id']}: se usa el primero.")
            continue
        vistos.add(cid)
        citas[cid] = _proponer(riesgo)
    for ev in historial:
        if ev["tipo"] == "correccion":
            c = citas.get(ev["cita"])
            if c is None:
                continue
            c[ev["campo"]] = ev["nuevo"]
            if ev["campo"] == "identificador":
                _reestado_identificador(c)
            c["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": ev["campo"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"], "motivo": ev["motivo"]})
            c["estado_aprobacion"] = "revisado"
        elif ev["tipo"] == "correspondencia":
            c = citas.get(ev["cita"])
            if c is None:
                continue
            c["correspondencias"].append({"marco": ev["marco"], "version": ev["version"],
                                          "identificador": ev["identificador"], "fundamento": ev["fundamento"],
                                          "autor": ev["autor"], "fecha": ev["fecha"]})
            c["estado_aprobacion"] = "revisado"
        elif ev["tipo"] in ("descarte", "restablecimiento"):
            c = citas.get(ev["cita"])
            if c is None:
                continue
            if ev["tipo"] == "descarte":
                if MARCA_DESCARTADO not in c["marcas"]:
                    c["marcas"].append(MARCA_DESCARTADO)
            else:
                c["marcas"] = [m for m in c["marcas"] if m != MARCA_DESCARTADO]
            c["estado_aprobacion"] = "revisado"
    vacios = entrega.get("vacios", [])
    return sorted(citas.values(), key=lambda c: c["id"]), vacios, avisos


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "correspondencia", "descarte", "restablecimiento", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, citas, vacios, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "citas": citas, "vacios": vacios, "estado_aprobacion": _estado(historial),
            "historial": historial, "avisos": avisos}


# --- Abrir (US1, FR-001 a FR-005, FR-014) -----------------------------------

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
    citas, vacios, avisos = _derivar(_entrega_actual(raiz), historial)
    nuevo = _componer(origen, citas, vacios, historial, avisos)
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
            "motivo": "Propuesta de citas a partir de la entrega vigente de S03."}]
    else:
        historial = previo["historial"]
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió el enunciado de origen (S03) desde la versión anterior de la cita.")
    if not origen["firmado"]:
        avisos.append("La cita se basa en un enunciado no firmado.")
    citas, vacios, avisos_deriv = _derivar(_entrega_actual(raiz), historial)
    avisos.extend(avisos_deriv)
    contenido = _componer(origen, citas, vacios, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise CitaError("La cita está firmada y el enunciado de origen cambió. No se actualiza solo: "
                        "revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, correspondencia, descartar, restablecer, revisar, firmar -----

def _cita(contenido: Dict[str, Any], cita: str) -> Dict[str, Any]:
    c = next((x for x in contenido["citas"] if x["id"] == cita), None)
    if c is None:
        raise CitaError(f"no existe la cita {cita}")
    return c


def corregir(raiz, cita: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise CitaError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    c = _cita(contenido, cita)
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "cita": cita,
          "campo": campo, "anterior": c[campo], "nuevo": nuevo_valor, "motivo": motivo}
    return _cita(_guardar(raiz, contenido, ev), cita)


def anadir_correspondencia(raiz, cita: str, marco: str, version: str, identificador: str,
                           fundamento: str, motivo: str, autor: str,
                           fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    marco_l = _texto_libre(marco, "el marco")
    version_l = _texto_libre(version, "la versión")
    ident_l = _texto_libre(identificador, "el identificador")
    fundamento_l = _texto_libre(fundamento, "el fundamento")
    contenido = _cargar_vigente(raiz)
    _cita(contenido, cita)
    ev = {"tipo": "correspondencia", "autor": autor, "fecha": fecha or now_iso(), "cita": cita,
          "marco": marco_l, "version": version_l, "identificador": ident_l,
          "fundamento": fundamento_l, "motivo": motivo}
    return _cita(_guardar(raiz, contenido, ev), cita)


def _marcar(raiz, tipo: str, cita: str, motivo: str, autor: str, fecha: Optional[str]) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    c = _cita(contenido, cita)
    descartado = MARCA_DESCARTADO in c["marcas"]
    if tipo == "descarte" and descartado:
        raise CitaError(f"la cita {cita} ya está descartada")
    if tipo == "restablecimiento" and not descartado:
        raise CitaError(f"la cita {cita} no está descartada: no hay nada que restablecer")
    ev = {"tipo": tipo, "autor": autor, "fecha": fecha or now_iso(), "cita": cita,
          "anterior": "descartado" if descartado else "vigente",
          "nuevo": "vigente" if descartado else "descartado", "motivo": motivo}
    return _cita(_guardar(raiz, contenido, ev), cita)


def descartar(raiz, cita: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "descarte", cita, motivo, autor, fecha)


def restablecer(raiz, cita: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "restablecimiento", cita, motivo, autor, fecha)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige marco y versión en cada cita vigente; el
    identificador puede quedar «pendiente de confirmar», declarado."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise CitaError("solo se firma una cita «revisada»: registre una corrección o una revisión")
    incompletas = [c["id"] for c in contenido["citas"]
                   if MARCA_DESCARTADO not in c["marcas"] and not (c["marco"].strip() and c["version"].strip())]
    if incompletas:
        raise CitaError("no se puede firmar: marco o versión incompletos en " + ", ".join(incompletas))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "citas_al_firmar": len(contenido["citas"]),
             "pendientes_al_firmar": sum(1 for c in contenido["citas"] if c["estado_identificador"] == PENDIENTE),
             "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) ------------------------------

def _evidencias_alteradas(raiz, contenido: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    r = Path(raiz)
    citas, evidencias = [], []
    for c in contenido["citas"]:
        for ev in c["evidencias"]:
            if ev["copia"]:
                ruta, esperado = r / ev["copia"], ev["sha256_guardado"]
            else:
                ruta, esperado = r / ev["ubicacion_original"], ev["sha256_original"]
                if not ruta.is_file():
                    continue
            if not ruta.is_file() or sha256_file(ruta) != esperado:
                evidencias.append(ev["id"])
                if c["id"] not in citas:
                    citas.append(c["id"])
    return citas, sorted(set(evidencias))


def _riesgos_no_vigentes(raiz, contenido: Dict[str, Any]) -> List[str]:
    vigentes = {x["id"] for x in _entrega_actual(raiz)["enunciados"]}
    return [c["id"] for c in contenido["citas"] if c["riesgo"]["id"] not in vigentes]


def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise CitaError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"citas": [], "origen": {}}
        ilegible = True
    alterados, evidencias = _evidencias_alteradas(raiz, contenido)
    no_vigentes = _riesgos_no_vigentes(raiz, contenido) if contenido["citas"] else []
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["enunciado"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except enunciado.EnunciadoError:
            entrega_ok = False
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "evidencias_alteradas": alterados,
                         "riesgos_no_vigentes": no_vigentes}
    if not p["firma"].exists():
        r["estado"] = "sin firma"
    else:
        firma = json.loads(p["firma"].read_bytes().decode("utf-8"))
        r["sha256_firmado"] = firma.get("sha256")
        r["huella_ok"] = firma.get("sha256") == actual
        if r["huella_ok"]:
            r.update(estado="firmado", firmante=firma.get("firmante"), fecha=firma.get("fecha"),
                     motivo=firma.get("motivo"), citas_al_firmar=firma.get("citas_al_firmar"),
                     pendientes_al_firmar=firma.get("pendientes_al_firmar"))
        else:
            r["estado"] = "revisado (firma no aplica)"
    if ilegible:
        r["estado"] = "revisado (json ilegible)"
        r["estado_informado"] = r["estado"]
        r["integro"] = False
        return r
    if r["estado"] == "firmado" and (alterados or no_vigentes or not entrega_ok):
        partes = []
        if alterados:
            partes.append("evidencia alterada")
        if no_vigentes:
            partes.append("riesgo no vigente")
        if not entrega_ok:
            partes.append("origen cambiado")
        r["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        r["estado_informado"] = r["estado"]
    r["integro"] = (not alterados and not no_vigentes and entrega_ok
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
    """Lo que recibe S05: solo las citas vigentes (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    alterados = set(v["evidencias_alteradas"])
    no_vigentes = set(v["riesgos_no_vigentes"])
    salida = []
    for c in contenido["citas"]:
        if MARCA_DESCARTADO in c["marcas"] or c["id"] in alterados or c["riesgo"]["id"] in no_vigentes:
            continue
        salida.append({k: c[k] for k in ("id", "riesgo", "marco", "version", "identificador",
                                         "estado_identificador", "fundamento", "correspondencias",
                                         "evidencias")})
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "origen": contenido["origen"], "citas": salida, "vacios": contenido["vacios"]}


# --- Vista legible y fichas (FR-012, principio VIII) -------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def _ficha(c: Dict[str, Any]) -> str:
    corres = "\n".join(f"- {x['marco']} {x['version']} · `{x['identificador']}` · {x['fundamento']} "
                       f"({x['autor']}, {x['fecha']})" for x in c["correspondencias"]) or "Sin correspondencias adicionales."
    evs = "\n".join(f"- `{x['id']}` · {x['tipo']} · "
                    f"{x['copia'] or x['ubicacion_original'] + ' (sin copia)'} · "
                    f"`{x['sha256_guardado'] or x['sha256_original']}`" for x in c["evidencias"]) or "- —"
    return f"""# Cita {c['id']}

> Producto de la herramienta C4A (S04 — La cita). La herramienta propone; el auditor corrige y firma.
> {NOTA_CITA}

- **Riesgo de origen**: `{c['riesgo']['id']}` — {c['riesgo']['condicion']}
- **Marco**: {c['marco']} · **Versión**: {c['version']}
- **Identificador de control**: `{c['identificador']}` ({c['estado_identificador']})
- **Estado de aprobación**: {c['estado_aprobacion']}
- **Marcas**: {', '.join(c['marcas']) or 'ninguna'}

## Fundamento de la correspondencia

{c['fundamento']}

## Correspondencias adicionales

{corres}

## Evidencias citadas (tipo · ubicación · huella)

{evs}

## Correcciones ({len(c['correcciones'])})

"""
    if c["correcciones"]:
        return _ficha_cuerpo(c, "\n".join(f"- {x['fecha']} · {x['autor']} · {x['campo']}: «{x['anterior']}» → "
                                        f"«{x['nuevo']}» · {x['motivo']}" for x in c["correcciones"]))
    return _ficha_cuerpo(c, "Sin correcciones.")


def _ficha_cuerpo(c: Dict[str, Any], correcciones: str) -> str:
    return f"""# Cita {c['id']}

> Producto de la herramienta C4A (S04 — La cita). La herramienta propone; el auditor corrige y firma.
> {NOTA_CITA}

- **Riesgo de origen**: `{c['riesgo']['id']}` — {c['riesgo']['condicion']}
- **Marco**: {c['marco']} · **Versión**: {c['version']}
- **Identificador de control**: `{c['identificador']}` ({c['estado_identificador']})
- **Estado de aprobación**: {c['estado_aprobacion']}
- **Marcas**: {', '.join(c['marcas']) or 'ninguna'}

## Fundamento de la correspondencia

{c['fundamento']}

## Correspondencias adicionales

"""
    + ("\n".join(f"- {x['marco']} {x['version']} · `{x['identificador']}` · {x['fundamento']} "
                 f"({x['autor']}, {x['fecha']})" for x in c["correspondencias"]) or "Sin correspondencias adicionales.") \
    + """

## Evidencias citadas (tipo · ubicación · huella)

""" \
    + ("\n".join(f"- `{x['id']}` · {x['tipo']} · "
                 f"{x['copia'] or x['ubicacion_original'] + ' (sin copia)'} · "
                 f"`{x['sha256_guardado'] or x['sha256_original']}`" for x in c["evidencias"]) or "- —") \
    + f"""

## Correcciones ({len(c['correcciones'])})

{correcciones}
"""


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    alterados = set(v["evidencias_alteradas"])
    no_vigentes = set(v["riesgos_no_vigentes"])
    pendientes = [c for c in contenido["citas"] if c["estado_identificador"] == PENDIENTE]
    L = [f"# La cita (S04) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         f"> {NOTA_CITA}", "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Enunciado de origen**: `{origen['archivo']}` · huella {_celda(origen['sha256'])} · "
          + ("firmado" if origen["firmado"] else "**enunciado no firmado**"),
          f"- **Resumen**: {len(contenido['citas'])} citas · {len(pendientes)} identificadores «{PENDIENTE}» · "
          f"{len(contenido['vacios'])} vacíos heredados.", "",
          f"## Identificadores pendientes de confirmar ({len(pendientes)})", ""]
    if pendientes:
        L += ["| Cita | Identificador | Marco |", "|---|---|---|"]
        for c in pendientes:
            L.append(f"| `{c['id']}` | `{_celda(c['identificador'])}` | {_celda(c['marco'] + ' ' + c['version'])} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Citas ({len(contenido['citas'])})", ""]
    if contenido["citas"]:
        L += ["| Id | Riesgo | Marco | Versión | Identificador | Estado id. | Marcas |",
              "|---|---|---|---|---|---|---|"]
        for c in contenido["citas"]:
            marcas = c["marcas"] + ([MARCA_ALTERADA] if c["id"] in alterados else []) \
                + ([MARCA_RIESGO_NO_VIGENTE] if c["id"] in no_vigentes else [])
            L.append(f"| `{c['id']}` | `{c['riesgo']['id']}` | {_celda(c['marco'])} | {_celda(c['version'])} | "
                     f"`{_celda(c['identificador'])}` | {c['estado_identificador']} | {_celda(', '.join(marcas))} |")
    else:
        L.append("Ninguna.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Cita | Campo | Anterior | Nuevo | Motivo |",
              "|---|---|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('cita'))} | "
                     f"{_celda(e.get('campo'))} | {_celda(e.get('anterior'))} | {_celda(e.get('nuevo'))} | "
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
    for c in contenido["citas"]:
        (p["raiz"] / f"{PREFIJO_FICHA}{c['id']}.md").write_bytes(_ficha(c).encode("utf-8"))
    return p["md"]
