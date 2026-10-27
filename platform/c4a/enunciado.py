"""S03 — El enunciado: un riesgo por hecho vigente, con criterio, impacto y lo que falta.

La herramienta ABRE el enunciado a partir de la entrega de S02 (`registro.entregar`),
PROPONE un riesgo por cada hecho vigente —condición desde la afirmación, consecuencia por
resultado técnico, criterio cualitativo sin identificadores (la cita del marco es de S04,
principio IV), impacto vacío para el auditor— y lista los «no consta» como vacíos heredados.
El auditor CORRIGE, DESCARTA, RESTABLECE, REVISA y FIRMA (constitución, principio I). Un
enunciado no dictamina: un hecho negativo lleva nota fija de que no acredita cumplimiento
(FR-006). Nada de este módulo abre la compuerta, ejecuta pruebas ni escribe fuera de
`03_hallazgos/`.

Archivos que produce (ver specs/003-enunciado-riesgo/data-model.md):
  - 03_hallazgos/enunciados_s03.json        contenido canónico (lo que se firma)
  - 03_hallazgos/enunciados_s03.firma.json  firma: firmante, fecha, justificación y huella
  - 03_hallazgos/enunciados_s03.md          vista legible para un tercero
  - 03_hallazgos/enunciado-<id>.md          una ficha legible por enunciado (FR-012)

Reglas de diseño (plan de S03):
  - El historial es la fuente: los enunciados se derivan de la entrega más el historial
    reaplicado en orden. Nada se borra (FR-007) y el resultado es determinista (FR-010).
  - El identificador deriva del hecho, no del texto: corregir no cambia el id (FR-004).
  - La firma exige criterio e impacto completos en cada enunciado vigente (FR-008).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S03 — El enunciado"
VERSION_ESQUEMA = "1"

APROBACION = ("borrador", "revisado")  # «firmado» se deriva de una firma válida
CAMPOS_CORREGIBLES = ("condicion", "consecuencia", "criterio", "impacto")
EVENTOS = ("propuesta", "correccion", "descarte", "restablecimiento", "revision", "firma_anulada")

MARCA_DESCARTADO = "descartado"
MARCA_HECHO_NO_VIGENTE = "hecho no vigente"   # calculada en verificar; no se persiste
MARCA_ALTERADA = "evidencia alterada"         # calculada en verificar; no se persiste
MARCAS = (MARCA_DESCARTADO, MARCA_HECHO_NO_VIGENTE, MARCA_ALTERADA)

NOTA_FIRMA = "Firmar el enunciado no abre la compuerta de autorización."
NOTA_NEGATIVO = ("La condición no se observó en la evidencia citada; esto no acredita cumplimiento "
                 "ni descarta su reaparición.")
NOTA_VACIOS = ("Los vacíos heredados son entradas «no consta» del registro: no son riesgos "
               "enunciados ni acreditan cumplimiento.")

ARCHIVO_JSON = "03_hallazgos/enunciados_s03.json"
ARCHIVO_MD = "03_hallazgos/enunciados_s03.md"
ARCHIVO_FIRMA = "03_hallazgos/enunciados_s03.firma.json"
PREFIJO_FICHA = "03_hallazgos/enunciado-"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

_CONSECUENCIA = {
    "positivo": ("La condición se observa en la evidencia citada; su materialización puede afectar "
                 "la confidencialidad, la integridad o la disponibilidad del activo."),
    "negativo": NOTA_NEGATIVO,
    "inconcluso": "La evidencia citada no permite decidir si la condición se materializa.",
}
_CRITERIO = ("Evidencia {tipos} con resultado {resultado}; el riesgo se enuncia con criterio "
             "cualitativo y la cita del marco corresponde a S04.")


class EnunciadoError(Exception):
    """Operación rechazada. `codigo` sigue contracts/cli-enunciado.md."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "registro": r / registro.ARCHIVO_JSON,
            "previos": [r / "03_hallazgos" / n for n in ("README.md", "matriz_cumplimiento.csv")]}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise EnunciadoError(f"no existe {ARCHIVO_JSON}: ejecute primero «enunciado abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise EnunciadoError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    """Texto escrito por el auditor: sin estados de cumplimiento, puertos, comandos ni
    credenciales (FR-016); las direcciones de red se reemplazan con `limpiar`."""
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise EnunciadoError(f"{nombre} contiene {clase}: el enunciado no lo admite (FR-016)")
    return alcance.limpiar(v)


def id_enunciado(hecho_id: str) -> str:
    return short_id("R", hecho_id)


# --- Contexto de origen (FR-001, FR-002) ------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return registro.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Exige el registro de S02 y fija el contexto: huellas de archivo y de entrega."""
    p = _rutas(raiz)
    if not p["registro"].exists():
        raise EnunciadoError(f"no existe {registro.ARCHIVO_JSON}: falta el producto anterior de S02; "
                             "ejecute primero «registro abrir»", 2)
    entrega = _entrega_actual(raiz)
    return {"archivo": registro.ARCHIVO_JSON,
            "sha256": sha256_file(p["registro"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": bool(entrega["firmado"]),
            "estado": entrega["estado"]}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    """True si el registro de origen cambió desde que se abrió (FR-014, FR-015)."""
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["registro"].exists():
        return True
    if sha256_file(p["registro"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise EnunciadoError("el registro de origen (S02) cambió desde que se abrió el enunciado: "
                             "ejecute «enunciado abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Derivación: entrega + historial → enunciados (FR-003 a FR-005) ---------

def _falta(entrada: Dict[str, Any], registro_firmado: bool) -> List[str]:
    falta: List[str] = []
    marcas = entrada.get("marcas", [])
    if registro.MARCA_PENDIENTE in marcas:
        falta.append("confirmar el alcance (pendiente)")
    if entrada["resultado"] == "inconcluso":
        falta.append("evidencia adicional para decidir")
    if entrada["resultado"] == "negativo":
        falta.append("reevaluar en una próxima revisión (la no observación no descarta la reaparición)")
    if any(not x.get("sha256_guardado") for x in entrada["evidencias"]):
        falta.append("verificar el original de la evidencia sin copia")
    if not registro_firmado:
        falta.append("el registro de origen no está firmado")
    return falta


def _proponer(entrada: Dict[str, Any], registro_firmado: bool) -> Dict[str, Any]:
    tipos = sorted({x["tipo"] for x in entrada["evidencias"]})
    return {
        "id": id_enunciado(entrada["id"]),
        "activo": entrada["activo"],
        "dominio": dict(entrada["dominio"]),
        "hecho": {"id": entrada["id"], "afirmacion": entrada["afirmacion"], "resultado": entrada["resultado"]},
        "condicion": entrada["afirmacion"],
        "consecuencia": _CONSECUENCIA[entrada["resultado"]],
        "criterio": _CRITERIO.format(tipos=" y ".join(tipos) or "sin tipo", resultado=entrada["resultado"]),
        "impacto": "",
        "falta": _falta(entrada, registro_firmado),
        "evidencias": [{k: x[k] for k in ("id", "tipo", "ubicacion_original", "copia",
                                          "sha256_original", "sha256_guardado")}
                       for x in entrada["evidencias"]],
        "estado_aprobacion": "borrador",
        "marcas": [],
        "correcciones": [],
    }


def _derivar(entrega: Dict[str, Any], historial: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], List[str]]:
    """Una propuesta por hecho vigente, con el historial reaplicado en orden (FR-007, FR-010)."""
    avisos: List[str] = []
    registro_firmado = bool(entrega["firmado"])
    enunciados: Dict[str, Dict] = {}
    vistos = set()
    for entrada in entrega["entradas"]:
        if entrada["clase"] != registro.HECHO:
            continue
        rid = id_enunciado(entrada["id"])
        if rid in vistos:  # entrega externa que repitió un hecho: se toma el primero
            avisos.append(f"La entrega repite el hecho {entrada['id']}: se usa el primero.")
            continue
        vistos.add(rid)
        enunciados[rid] = _proponer(entrada, registro_firmado)
    for ev in historial:
        if ev["tipo"] == "correccion":
            e = enunciados.get(ev["enunciado"])
            if e is None:
                continue
            e[ev["campo"]] = ev["nuevo"]
            e["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": ev["campo"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"], "motivo": ev["motivo"]})
            e["estado_aprobacion"] = "revisado"
        elif ev["tipo"] in ("descarte", "restablecimiento"):
            e = enunciados.get(ev["enunciado"])
            if e is None:
                continue
            if ev["tipo"] == "descarte":
                if MARCA_DESCARTADO not in e["marcas"]:
                    e["marcas"].append(MARCA_DESCARTADO)
            else:
                e["marcas"] = [m for m in e["marcas"] if m != MARCA_DESCARTADO]
            e["estado_aprobacion"] = "revisado"
    vacios = [{"id": e["id"], "activo": e["activo"], "dominio": e["dominio"], "resultado": e["resultado"],
               "motivo": e["motivo"], "marcas": e["marcas"]}
              for e in entrega["entradas"] if e["clase"] != registro.HECHO]
    return sorted(enunciados.values(), key=lambda e: e["id"]), vacios, avisos


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "descarte", "restablecimiento", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, enunciados, vacios, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "enunciados": enunciados, "vacios": vacios, "estado_aprobacion": _estado(historial),
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
    """Único punto de escritura de las acciones del auditor (análisis I1 de S02)."""
    historial = contenido["historial"] + [evento]
    _anular_firma(raiz, historial, evento["autor"], evento["fecha"])
    origen = _contexto(raiz, contenido)
    enunciados, vacios, avisos = _derivar(_entrega_actual(raiz), historial)
    nuevo = _componer(origen, enunciados, vacios, historial, avisos)
    _escribir(raiz, nuevo)
    return nuevo


def abrir(raiz, fecha: Optional[str] = None) -> Dict[str, Any]:
    p = _rutas(raiz)
    previo = cargar(raiz) if p["json"].exists() else None
    origen = _contexto(raiz, previo)
    if previo is None:
        historial: List[Dict[str, Any]] = [{
            "tipo": "propuesta", "autor": RESPONSABLE_HERRAMIENTA, "fecha": fecha or now_iso(),
            "motivo": "Propuesta de enunciados a partir de la entrega vigente de S02."}]
        avisos: List[str] = []
        if not origen["firmado"]:
            avisos.append("El enunciado se basa en un registro no firmado.")
    else:
        historial = previo["historial"]
        avisos = []
        if not origen["firmado"]:
            avisos.append("El enunciado se basa en un registro no firmado.")
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió el registro de origen (S02) desde la versión anterior del enunciado.")
    enunciados, vacios, avisos_deriv = _derivar(_entrega_actual(raiz), historial)
    avisos.extend(avisos_deriv)
    contenido = _componer(origen, enunciados, vacios, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise EnunciadoError("El enunciado está firmado y el registro de origen cambió. No se actualiza "
                             "solo: revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, descartar, restablecer, revisar, firmar (US2, FR-007, FR-008) -

def _enunciado(contenido: Dict[str, Any], enunciado: str) -> Dict[str, Any]:
    e = next((x for x in contenido["enunciados"] if x["id"] == enunciado), None)
    if e is None:
        raise EnunciadoError(f"no existe el enunciado {enunciado}")
    return e


def corregir(raiz, enunciado: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise EnunciadoError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    e = _enunciado(contenido, enunciado)
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "enunciado": enunciado,
          "campo": campo, "anterior": e[campo], "nuevo": nuevo_valor, "motivo": motivo}
    return _enunciado(_guardar(raiz, contenido, ev), enunciado)


def _marcar(raiz, tipo: str, enunciado: str, motivo: str, autor: str, fecha: Optional[str]) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    e = _enunciado(contenido, enunciado)
    descartado = MARCA_DESCARTADO in e["marcas"]
    if tipo == "descarte" and descartado:
        raise EnunciadoError(f"el enunciado {enunciado} ya está descartado")
    if tipo == "restablecimiento" and not descartado:
        raise EnunciadoError(f"el enunciado {enunciado} no está descartado: no hay nada que restablecer")
    ev = {"tipo": tipo, "autor": autor, "fecha": fecha or now_iso(), "enunciado": enunciado,
          "anterior": "descartado" if descartado else "vigente",
          "nuevo": "vigente" if descartado else "descartado", "motivo": motivo}
    return _enunciado(_guardar(raiz, contenido, ev), enunciado)


def descartar(raiz, enunciado: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "descarte", enunciado, motivo, autor, fecha)


def restablecer(raiz, enunciado: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "restablecimiento", enunciado, motivo, autor, fecha)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige criterio e impacto humanos en cada vigente."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise EnunciadoError("solo se firma un enunciado «revisado»: registre una corrección o una revisión")
    incompletos = [e["id"] for e in contenido["enunciados"]
                   if MARCA_DESCARTADO not in e["marcas"] and not (e["criterio"].strip() and e["impacto"].strip())]
    if incompletos:
        raise EnunciadoError("no se puede firmar: criterio e impacto incompletos en "
                             + ", ".join(incompletos))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "enunciados_al_firmar": len(contenido["enunciados"]),
             "vacios_al_firmar": len(contenido["vacios"]), "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (US4, FR-009, FR-013) ------------------------------

def _evidencias_alteradas(raiz, contenido: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    r = Path(raiz)
    enunciados, evidencias = [], []
    for e in contenido["enunciados"]:
        for ev in e["evidencias"]:
            if ev["copia"]:
                ruta, esperado = r / ev["copia"], ev["sha256_guardado"]
            else:
                ruta, esperado = r / ev["ubicacion_original"], ev["sha256_original"]
                if not ruta.is_file():
                    continue  # referencia sin copia fuera de alcance: no verificable, no alterada
            if not ruta.is_file() or sha256_file(ruta) != esperado:
                evidencias.append(ev["id"])
                if e["id"] not in enunciados:
                    enunciados.append(e["id"])
    return enunciados, sorted(set(evidencias))


def _hechos_no_vigentes(raiz, contenido: Dict[str, Any]) -> List[str]:
    vigentes = {registro.HECHO: [x["id"] for x in _entrega_actual(raiz)["entradas"] if x["clase"] == registro.HECHO]}
    return [e["id"] for e in contenido["enunciados"] if e["hecho"]["id"] not in vigentes[registro.HECHO]]


def verificar(raiz) -> Dict[str, Any]:
    """Recalcula huella del producto, de la entrega de S02 y de cada evidencia citada."""
    p = _rutas(raiz)
    if not p["json"].exists():
        raise EnunciadoError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"enunciados": [], "origen": {}}
        ilegible = True
    alterados, evidencias = _evidencias_alteradas(raiz, contenido)
    no_vigentes = _hechos_no_vigentes(raiz, contenido) if contenido["enunciados"] else []
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["registro"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except registro.RegistroError:
            entrega_ok = False
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "evidencias_alteradas": alterados,
                         "hechos_no_vigentes": no_vigentes}
    if not p["firma"].exists():
        r["estado"] = "sin firma"
    else:
        firma = json.loads(p["firma"].read_bytes().decode("utf-8"))
        r["sha256_firmado"] = firma.get("sha256")
        r["huella_ok"] = firma.get("sha256") == actual
        if r["huella_ok"]:
            r.update(estado="firmado", firmante=firma.get("firmante"), fecha=firma.get("fecha"),
                     motivo=firma.get("motivo"), enunciados_al_firmar=firma.get("enunciados_al_firmar"),
                     vacios_al_firmar=firma.get("vacios_al_firmar"))
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
            partes.append("hecho no vigente")
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
    """Lo que recibe S04: solo los enunciados vigentes (FR-013)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    alterados = set(v["evidencias_alteradas"])
    no_vigentes = set(v["hechos_no_vigentes"])
    salida = []
    for e in contenido["enunciados"]:
        if MARCA_DESCARTADO in e["marcas"] or e["id"] in alterados or e["hecho"]["id"] in no_vigentes:
            continue
        salida.append({k: e[k] for k in ("id", "activo", "dominio", "hecho", "condicion", "consecuencia",
                                         "criterio", "impacto", "falta", "evidencias")})
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "origen": contenido["origen"], "enunciados": salida, "vacios": contenido["vacios"]}


# --- Vista legible y fichas (FR-012, principio VIII) -------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def _ficha_correcciones(e: Dict[str, Any], correcciones: str) -> str:
    # separada para mantener la ficha legible; el contenido ya pasó por el filtro (FR-016)
    cuerpo = f"""# Enunciado {e['id']}

> Producto de la herramienta C4A (S03 — El enunciado). La herramienta propone; el auditor
> corrige y firma. Un enunciado interpreta hechos registrados: no evalúa controles.

- **Activo**: {e['activo']}
- **Dominio**: {e['dominio']['valor']}
- **Hecho de origen**: `{e['hecho']['id']}` — {e['hecho']['afirmacion']} (resultado: {e['hecho']['resultado']})
- **Estado de aprobación**: {e['estado_aprobacion']}
- **Marcas**: {', '.join(e['marcas']) or 'ninguna'}

## Condición

{e['condicion']}

## Consecuencia

{e['consecuencia']}

## Criterio (cualitativo; la cita del marco es de S04)

{e['criterio']}

## Impacto

{e['impacto'] or '— (lo completa el auditor antes de firmar)'}

## Lo que falta

"""
    cuerpo += "\n".join(f"- {f}" for f in e["falta"]) or "- —"
    cuerpo += """

## Evidencias citadas (tipo · ubicación · huella)

"""
    cuerpo += "\n".join(f"- `{x['id']}` · {x['tipo']} · "
                        f"{x['copia'] or x['ubicacion_original'] + ' (sin copia)'} · "
                        f"`{x['sha256_guardado'] or x['sha256_original']}`" for x in e["evidencias"]) or "- —"
    cuerpo += f"""

## Correcciones ({len(e['correcciones'])})

{correcciones}
"""
    return cuerpo


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    origen = contenido["origen"]
    alterados = set(v["evidencias_alteradas"])
    no_vigentes = set(v["hechos_no_vigentes"])
    L = [f"# El enunciado (S03) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         "> El enunciado interpreta hechos registrados: no contiene conclusiones sobre controles.",
         "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Registro de origen**: `{origen['archivo']}` · huella {_celda(origen['sha256'])} · "
          + ("firmado" if origen["firmado"] else "**registro no firmado**"),
          f"- **Entrega de origen**: huella `{origen['entrega_sha256']}`",
          f"- **Resumen**: {len(contenido['enunciados'])} enunciados · {len(contenido['vacios'])} vacíos heredados.",
          "", NOTA_VACIOS, "", f"## Enunciados ({len(contenido['enunciados'])})", ""]
    if contenido["enunciados"]:
        L += ["| Id | Activo | Dominio | Hecho | Condición | Consecuencia | Criterio | Impacto | Evidencias | Marcas |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for e in contenido["enunciados"]:
            marcas = e["marcas"] + ([MARCA_ALTERADA] if e["id"] in alterados else []) \
                + ([MARCA_HECHO_NO_VIGENTE] if e["id"] in no_vigentes else [])
            evs = "<br>".join(f"`{x['id']}` · {x['tipo']}" for x in e["evidencias"])
            L.append(f"| `{e['id']}` | {_celda(e['activo'])} | {_celda(e['dominio']['valor'])} | "
                     f"`{e['hecho']['id']}` | {_celda(e['condicion'])} | {_celda(e['consecuencia'])} | "
                     f"{_celda(e['criterio'])} | {_celda(e['impacto'])} | {evs} | {_celda(', '.join(marcas))} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Vacíos heredados del registro ({len(contenido['vacios'])})", ""]
    if contenido["vacios"]:
        L += ["| Id | Activo | Dominio | Resultado | Motivo |", "|---|---|---|---|---|"]
        for e in contenido["vacios"]:
            L.append(f"| `{e['id']}` | {_celda(e['activo'])} | {_celda(e['dominio']['valor'])} | "
                     f"{e['resultado']} | {_celda(e['motivo'])} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Enunciado | Campo | Anterior | Nuevo | Motivo |",
              "|---|---|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('enunciado'))} | "
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
    for e in contenido["enunciados"]:
        (p["raiz"] / f"{PREFIJO_FICHA}{e['id']}.md").write_bytes(_ficha_correcciones(
            e, "\n".join(f"- {c['fecha']} · {c['autor']} · {c['campo']}: «{c['anterior']}» → "
                         f"«{c['nuevo']}» · {c['motivo']}" for c in e["correcciones"]) or "Sin correcciones."
        ).encode("utf-8"))
    return p["md"]
