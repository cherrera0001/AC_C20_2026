"""S07 — El encargo: el mismo trabajo escrito para que una herramienta lo repita.

La herramienta ABRE el encargo a partir de la cadena completa de entregas S01–S06 y
PROPONE el trabajo como pasos repetibles: fijar el alcance, verificar cada dominio con el
tipo de evidencia esperada, enunciar, citar, perfilar y listar. Los vacíos heredados se
escriben como condiciones de la repetición, con su motivo. El encargo no lleva firma de
aprobación (la guía S07 es «sin firmar»): lleva AUTORÍA registrada y una HUELLA DE
INTEGRIDAD de los bytes guardados; la trazabilidad la dan autor, historial e integridad,
no una aprobación. El encargo MUST NOT contener comandos, direcciones de red, puertos,
credenciales ni procedimientos de explotación (principio V): nombra el tipo de evidencia
y el dominio. Y no abre la compuerta ni la transporta: la corrida que repite verifica
`scope/autorizacion.md` por sí misma (FR-014).

Archivos que produce (FR-010):
  - 01_plan/encargo_s07.json              contenido canónico
  - 01_plan/encargo_s07.integridad.json   huella SHA-256 de los bytes guardados + autoría
  - 01_plan/encargo_s07.md                vista legible para una herramienta ajena y un tercero
  - 01_plan/encargo-<id>.md               una ficha legible por paso (FR-011)

Reglas de diseño (misma forma que S03–S06): el historial es la fuente, nada se borra
(FR-007) y el resultado es determinista (FR-009).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from . import cita
from . import enunciado
from . import lista
from . import perfil
from . import registro
from .util import now_iso, sha256_file, short_id

PRODUCTO = "S07 — El encargo"
VERSION_ESQUEMA = "1"

APROBACION = ("borrador", "revisado")  # no hay «firmado»: el encargo es trabajo, no dictamen
CAMPOS_CORREGIBLES = ("descripcion",)
EVENTOS = ("propuesta", "correccion", "alta", "exclusion", "inclusion", "revision")

REPETIBLE = "inmediata"
CONDICIONADA = "condicionada"
NO_REPETIBLE = "no repetible"

NOTA_COMPUERTA = ("Este encargo no abre ni transporta la autorización: la corrida que repite "
                  "verifica scope/autorizacion.md firmada y con ventana vigente antes de "
                  "cualquier paso técnico.")
NOTA_ENCARGO = ("El encargo describe trabajo para repetir, sin firmar: no es una evaluación "
                "hecha ni un dictamen.")

ARCHIVO_JSON = "01_plan/encargo_s07.json"
ARCHIVO_MD = "01_plan/encargo_s07.md"
ARCHIVO_INTEGRIDAD = "01_plan/encargo_s07.integridad.json"
PREFIJO_FICHA = "01_plan/encargo-"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"

_MODULOS = (("S01", alcance, alcance.ARCHIVO_JSON), ("S02", registro, registro.ARCHIVO_JSON),
            ("S03", enunciado, enunciado.ARCHIVO_JSON), ("S04", cita, cita.ARCHIVO_JSON),
            ("S05", perfil, perfil.ARCHIVO_JSON), ("S06", lista, lista.ARCHIVO_JSON))


class EncargoError(Exception):
    """Operación rechazada. `codigo`: 1 regla, 2 falta un producto anterior, 4 origen cambió."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Cadena de entregas S01–S06 (FR-001, FR-002) ----------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD,
            "integridad": r / ARCHIVO_INTEGRIDAD}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise EncargoError(f"no existe {ARCHIVO_JSON}: ejecute primero «encargo abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise EncargoError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise EncargoError(f"{nombre} contiene {clase}: el encargo no lo admite (FR-005)")
    return alcance.limpiar(v)


def _cadena(raiz) -> Dict[str, Any]:
    """Estado de la cadena S01–S06: archivo, huella y estado de firma de cada entrega."""
    r = Path(raiz)
    cadena: Dict[str, Any] = {}
    faltan: List[str] = []
    for sprint, modulo, archivo in _MODULOS:
        ruta = r / archivo
        if not ruta.exists():
            faltan.append(archivo)
            continue
        try:
            estado = modulo.estado_efectivo(raiz)
        except Exception:
            estado = "desconocido"
        cadena[sprint] = {"archivo": archivo, "sha256": sha256_file(ruta), "estado": estado}
    if faltan:
        raise EncargoError("falta el producto anterior de la cadena S01–S06: "
                           + ", ".join(faltan), 2)
    return cadena


def _entregas() -> Dict[str, Any]:
    """Funciones de entrega de cada sprint, para derivar los pasos."""
    return {"S02": registro.entregar, "S03": enunciado.entregar, "S04": cita.entregar,
            "S05": perfil.entregar, "S06": lista.entregar}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> List[str]:
    """Sprints cuya entrega cambió desde que se abrió el encargo."""
    cambiados: List[str] = []
    try:
        cadena = _cadena(raiz)
    except EncargoError:
        return ["S01–S06"]
    for sprint, actual in cadena.items():
        previo = contenido["cadena"].get(sprint) or {}
        if previo.get("sha256") != actual["sha256"]:
            cambiados.append(sprint)
    return cambiados


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    cambiados = _origen_cambio(raiz, contenido)
    if cambiados:
        raise EncargoError("la cadena de origen cambió desde que se abrió el encargo "
                           f"({', '.join(cambiados)}): ejecute «encargo abrir» y revise", 4)
    return contenido


# --- Derivación: cadena + historial → pasos (FR-003, FR-004) ----------------

def _paso(sprint: str, slug: str, descripcion: str, entrada: str, salida: str,
          huella_origen: str, repetibilidad: str = REPETIBLE, condicion: Optional[str] = None) -> Dict[str, Any]:
    return {"id": short_id("E", sprint, slug), "sprint": sprint, "descripcion": descripcion,
            "entrada": entrada, "salida_esperada": salida, "huella_origen": huella_origen,
            "repetibilidad": repetibilidad, "condicion": condicion,
            "estado_aprobacion": "borrador", "correcciones": []}


def _proponer(raiz, cadena: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    avisos: List[str] = []
    pasos: List[Dict[str, Any]] = []
    entregas = {s: f(raiz) for s, f in _entregas().items()}
    reg = alcance.cargar(raiz)
    activos = [f for f in reg["filas"] if f["tipo"] == "activo" and not alcance.es_pendiente(f)
               and f["decision"] != "excluido"]
    dominios = [f for f in reg["filas"] if f["tipo"] == "dominio"]
    nombre_activo = (activos[0]["valor"].split(" (")[0] if activos else "el activo del alcance")
    dentro = [f for f in dominios if not alcance.es_pendiente(f) and f["decision"] != "excluido"]
    pendientes = [f for f in dominios if alcance.es_pendiente(f)]
    pasos.append(_paso("S01", "alcance",
                       f"Fijar el alcance del ejercicio: activo «{nombre_activo}», "
                       f"{len(dentro)} dominios dentro y {len(pendientes)} pendientes.",
                       "scope/alcance.md y scope/autorizacion.md", "alcance firmado o en borrador",
                       cadena["S01"]["sha256"]))
    entrega_s02 = entregas["S02"]
    hechos_por_dominio: Dict[str, int] = {}
    for e in entrega_s02["entradas"]:
        if e["clase"] == registro.HECHO:
            hechos_por_dominio[e["dominio"]["fila"] or "activo"] = \
                hechos_por_dominio.get(e["dominio"]["fila"] or "activo", 0) + 1
    for f in dominios:
        if f["decision"] == "excluido":
            continue
        f_id = f["id"]
        h = hechos_por_dominio.get(f_id, 0)
        condicion = None
        repetibilidad = REPETIBLE
        if h == 0:
            condicion = "verificar cuando conste evidencia admisible para este dominio"
            repetibilidad = CONDICIONADA
        pasos.append(_paso("S02", f_id,
                           f"Verificar el dominio «{f['valor']}»: aportar evidencia del tipo que "
                           f"corresponda al dominio (técnica si la compuerta está vigente, "
                           f"documental con origen declarado)." + (f" Ya constan {h} hechos: "
                           f"verificar lo que falta." if h else ""),
                           "evidencia del dominio", "hechos del dominio en el registro",
                           cadena["S02"]["sha256"], repetibilidad, condicion))
    n_hechos = sum(1 for e in entrega_s02["entradas"] if e["clase"] == registro.HECHO)
    n_vacios = sum(1 for e in entrega_s02["entradas"] if e["clase"] != registro.HECHO)
    pasos.append(_paso("S03", "enunciado",
                       f"Enunciar el riesgo de cada hecho vigente ({n_hechos} hoy); los {n_vacios} "
                       "vacíos quedan como condición, no se rellenan.",
                       "entrega de S02", "enunciados de riesgo con criterio, impacto y lo que falta",
                       cadena["S03"]["sha256"]))
    n_riesgos = len(entregas["S03"]["enunciados"])
    pasos.append(_paso("S04", "cita",
                       f"Citar cada riesgo en un marco con nombre y versión ({n_riesgos} riesgos); "
                       "los identificadores que no consten quedan pendientes de confirmar.",
                       "entrega de S03", "citas con marco, versión e identificador o su pendiente",
                       cadena["S04"]["sha256"]))
    pasos.append(_paso("S05", "perfil",
                       "Perfilar el activo con las seis funciones del NIST CSF 2.0 (Gobernar, "
                       "Identificar, Proteger, Detectar, Responder, Recuperar).",
                       "entrega de S04", "perfil por función con síntesis del auditor",
                       cadena["S05"]["sha256"]))
    seleccionados = entregas["S06"]["controles"]
    pend_sel = entregas["S06"]["contados"]["pendientes"]
    pasos.append(_paso("S06", "lista",
                       f"Listar los CIS Controls que aplican partiendo por el inventario "
                       f"({len(seleccionados)} seleccionados hoy, {pend_sel} pendientes).",
                       "entrega de S05", "lista de controles aplicables con justificación",
                       cadena["S06"]["sha256"]))
    entrega_s03 = entregas["S03"]
    causas = sorted({v["motivo"] for v in entrega_s03.get("vacios", []) if v.get("motivo")})
    funciones_con = sum(1 for s in entregas["S05"]["secciones"] if s["riesgos"])
    resumen = {"activo": nombre_activo, "dominios": len(dominios),
               "hechos": n_hechos, "vacios": n_vacios,
               "riesgos": len(entrega_s03["enunciados"]),
               "citas": len(entregas["S04"]["citas"]),
               "funciones_con_material": funciones_con,
               "controles_seleccionados": len(seleccionados),
               "controles_pendientes": pend_sel,
               "vacios_causas": causas}
    return pasos, avisos, resumen


def _derivar(raiz, cadena: Dict[str, Any], historial: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    pasos, avisos, resumen = _proponer(raiz, cadena)
    por_id = {p["id"]: p for p in pasos}
    for ev in historial:
        if ev["tipo"] == "correccion":
            p = por_id.get(ev["paso"])
            if p is None:
                continue
            p["descripcion"] = ev["nuevo"]
            p["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": "descripcion",
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"], "motivo": ev["motivo"]})
            p["estado_aprobacion"] = "revisado"
        elif ev["tipo"] == "alta":
            p = dict(ev["paso_nuevo"])
            p["correcciones"] = [{"autor": ev["autor"], "fecha": ev["fecha"], "campo": "alta",
                                  "anterior": "", "nuevo": p["descripcion"][:80], "motivo": ev["motivo"]}]
            por_id[p["id"]] = p
        elif ev["tipo"] in ("exclusion", "inclusion"):
            p = por_id.get(ev["paso"])
            if p is None:
                continue
            if ev["tipo"] == "exclusion":
                p["repetibilidad"] = NO_REPETIBLE
            else:
                p["repetibilidad"] = CONDICIONADA if p["condicion"] else REPETIBLE
            p["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"], "campo": "repetibilidad",
                                      "anterior": ev["anterior"], "nuevo": p["repetibilidad"],
                                      "motivo": ev["motivo"]})
            p["estado_aprobacion"] = "revisado"
    return sorted(por_id.values(), key=lambda p: (p["sprint"], p["id"])), avisos, resumen


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "alta", "exclusion", "inclusion", "revision"):
            estado = "revisado"
    return estado


def _componer(cadena, pasos, resumen, historial, avisos) -> Dict[str, Any]:
    repetibles = sum(1 for p in pasos if p["repetibilidad"] == REPETIBLE)
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "cadena": cadena,
            "pasos": pasos, "resumen": resumen,
            "contados": {"pasos": len(pasos), "repetibles": repetibles,
                                         "condicionados": sum(1 for p in pasos if p["repetibilidad"] == CONDICIONADA),
                                         "no_repetibles": sum(1 for p in pasos if p["repetibilidad"] == NO_REPETIBLE)},
            "estado_aprobacion": _estado(historial), "historial": historial, "avisos": avisos,
            "nota": NOTA_COMPUERTA}


# --- Abrir (US1, FR-001, FR-013) --------------------------------------------

def _escribir(raiz, contenido: Dict[str, Any], autor: Optional[str], fecha: Optional[str]) -> None:
    p = _rutas(raiz)
    p["json"].parent.mkdir(parents=True, exist_ok=True)
    p["json"].write_bytes(alcance.serializar(contenido))
    if autor is not None:
        integridad = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]),
                      "autor": autor, "fecha": fecha or now_iso(), "nota": NOTA_ENCARGO}
        p["integridad"].write_bytes(alcance.serializar(integridad))
    escribir_vista(raiz)


def _guardar(raiz, contenido: Dict[str, Any], evento: Dict[str, Any]) -> Dict[str, Any]:
    historial = contenido["historial"] + [evento]
    cadena = _cadena(raiz)
    pasos, avisos, resumen = _derivar(raiz, cadena, historial)
    nuevo = _componer(cadena, pasos, resumen, historial, avisos)
    _escribir(raiz, nuevo, evento["autor"], evento["fecha"])
    return nuevo


def abrir(raiz, fecha: Optional[str] = None) -> Dict[str, Any]:
    p = _rutas(raiz)
    previo = cargar(raiz) if p["json"].exists() else None
    cadena = _cadena(raiz)
    avisos: List[str] = []
    if previo is None:
        historial: List[Dict[str, Any]] = [{
            "tipo": "propuesta", "autor": RESPONSABLE_HERRAMIENTA, "fecha": fecha or now_iso(),
            "motivo": "Propuesta del encargo a partir de la cadena vigente S01–S06."}]
    else:
        historial = previo["historial"]
        cambiados = _origen_cambio(raiz, previo)
        if cambiados:
            avisos.append("Cambió la cadena de origen (" + ", ".join(cambiados) + ") desde la "
                          "versión anterior del encargo: revise antes de corregir.")
    pasos, avisos_deriv, resumen = _derivar(raiz, cadena, historial)
    avisos.extend(avisos_deriv)
    contenido = _componer(cadena, pasos, resumen, historial, avisos)
    _escribir(raiz, contenido, RESPONSABLE_HERRAMIENTA, fecha)
    return contenido


# --- Corregir, alta, exclusión, inclusión, revisar (US2, FR-007) -------------

def _paso_existe(contenido: Dict[str, Any], paso: str) -> Dict[str, Any]:
    x = next((p for p in contenido["pasos"] if p["id"] == paso), None)
    if x is None:
        raise EncargoError(f"no existe el paso {paso}")
    return x


def corregir(raiz, paso: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise EncargoError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    x = _paso_existe(contenido, paso)
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "paso": paso,
          "campo": campo, "anterior": x[campo], "nuevo": nuevo_valor, "motivo": motivo}
    return _paso_existe(_guardar(raiz, contenido, ev), paso)


def anadir(raiz, descripcion: str, entrada: str, salida: str, motivo: str, autor: str,
           fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    desc = _texto_libre(descripcion, "la descripción")
    entrada_l = _texto_libre(entrada, "la entrada")
    salida_l = _texto_libre(salida, "la salida esperada")
    contenido = _cargar_vigente(raiz)
    paso_nuevo = _paso("MAN", desc[:24], desc, entrada_l, salida_l,
                       sha256_file(_rutas(raiz)["json"]), REPETIBLE, None)
    ev = {"tipo": "alta", "autor": autor, "fecha": fecha or now_iso(), "paso_nuevo": paso_nuevo,
          "motivo": motivo}
    return _paso_existe(_guardar(raiz, contenido, ev), paso_nuevo["id"])


def _marcar(raiz, tipo: str, paso: str, motivo: str, autor: str, fecha: Optional[str]) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    x = _paso_existe(contenido, paso)
    if tipo == "exclusion" and x["repetibilidad"] == NO_REPETIBLE:
        raise EncargoError(f"el paso {paso} ya está excluido de la repetición")
    if tipo == "inclusion" and x["repetibilidad"] != NO_REPETIBLE:
        raise EncargoError(f"el paso {paso} no está excluido: no hay nada que incluir")
    ev = {"tipo": tipo, "autor": autor, "fecha": fecha or now_iso(), "paso": paso,
          "anterior": x["repetibilidad"],
          "nuevo": NO_REPETIBLE if tipo == "exclusion" else (CONDICIONADA if x["condicion"] else REPETIBLE),
          "motivo": motivo}
    return _paso_existe(_guardar(raiz, contenido, ev), paso)

def excluir(raiz, paso: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "exclusion", paso, motivo, autor, fecha)


def incluir(raiz, paso: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "inclusion", paso, motivo, autor, fecha)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


# --- Verificar (integridad + cadena) y entregar (FR-008, FR-012) -------------

def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise EncargoError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"pasos": [], "cadena": {}}
        ilegible = True
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_integridad": None,
                         "integridad_ok": None, "cadena_ok": True, "pasos_alterados": []}
    if not p["integridad"].exists():
        r["estado"] = "sin integridad"
    else:
        registro_i = json.loads(p["integridad"].read_bytes().decode("utf-8"))
        r["sha256_integridad"] = registro_i.get("sha256")
        r["integridad_ok"] = registro_i.get("sha256") == actual
        r["estado"] = "integro" if r["integridad_ok"] else "revisado (integridad no aplica)"
        r["autor"] = registro_i.get("autor")
        r["fecha"] = registro_i.get("fecha")
    if ilegible:
        r["estado"] = "revisado (json ilegible)"
        r["integro"] = False
        return r
    try:
        cadena = _cadena(raiz)
        for sprint, previo in contenido["cadena"].items():
            if previo.get("sha256") != cadena[sprint]["sha256"]:
                r["cadena_ok"] = False
                r["pasos_alterados"].append(sprint)
    except EncargoError:
        r["cadena_ok"] = False
    r["integro"] = bool(r["integridad_ok"]) and r["cadena_ok"]
    return r


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "integro":
        return cargar(raiz)["estado_aprobacion"]
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


def entregar(raiz) -> Dict[str, Any]:
    """Lo que recibe S08: el encargo completo, con sus pasos, condiciones y huellas."""
    contenido = cargar(raiz)
    ver = verificar(raiz)
    return {"producto": PRODUCTO, "integro": ver["integro"], "estado": contenido["estado_aprobacion"],
            "cadena": contenido["cadena"], "pasos": contenido["pasos"],
            "resumen": contenido.get("resumen", {}),
            "contados": contenido["contados"], "nota": NOTA_COMPUERTA}


# --- Vista legible y fichas (FR-011, principio VIII) -------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def _ficha(paso: Dict[str, Any]) -> str:
    correcciones = "\n".join(f"- {x['fecha']} · {x['autor']} · {x['campo']}: «{x['anterior']}» → "
                             f"«{x['nuevo']}» · {x['motivo']}" for x in paso["correcciones"]) or "Sin correcciones."
    condicion = f" · **Condición**: {paso['condicion']}" if paso["condicion"] else ""
    return f"""# Encargo — paso {paso['id']}

> Producto de la herramienta C4A (S07 — El encargo). Trabajo escrito para repetir, sin firmar.
> {NOTA_ENCARGO}

- **Sprint**: {paso['sprint']}
- **Repetibilidad**: {paso['repetibilidad']}{condicion}
- **Entrada**: {paso['entrada']}
- **Salida esperada**: {paso['salida_esperada']}
- **Huella de la entrega de origen**: `{paso['huella_origen']}`

## Descripción

{paso['descripcion']}

## Correcciones ({len(paso['correcciones'])})

{correcciones}
"""


def vista(raiz) -> str:
    contenido = cargar(raiz)
    ver = verificar(raiz)
    estado = contenido["estado_aprobacion"]
    L = [f"# El encargo (S07) — {estado}", "",
         "> Producto de la herramienta C4A. Trabajo escrito para que una herramienta lo repita.",
         f"> {NOTA_ENCARGO}", f"> {NOTA_COMPUERTA}", "",
         f"- **Estado**: {estado} (sin firma de aprobación, por diseño de la guía S07)",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{ver['sha256_actual']}`",
         f"- **Integridad**: {ver['estado']}" + (f" (autor: {ver.get('autor')})" if ver.get("autor") else ""),
         f"- **Resumen**: {contenido['contados']['pasos']} pasos · "
         f"{contenido['contados']['repetibles']} repetibles de inmediato · "
         f"{contenido['contados']['condicionados']} condicionados · "
         f"{contenido['contados']['no_repetibles']} no repetibles.", "",
         "## Cadena de origen (S01–S06)", "", "| Sprint | Archivo | SHA-256 | Estado |", "|---|---|---|---|"]
    for sprint, c in sorted(contenido["cadena"].items()):
        L.append(f"| {sprint} | `{c['archivo']}` | `{c['sha256']}` | {c['estado']} |")
    L += ["", f"## Pasos ({len(contenido['pasos'])})", ""]
    if contenido["pasos"]:
        L += ["| Id | Sprint | Repetibilidad | Condición | Descripción |", "|---|---|---|---|---|"]
        for p in contenido["pasos"]:
            L.append(f"| `{p['id']}` | {p['sprint']} | {p['repetibilidad']} | "
                     f"{_celda(p['condicion'])} | {_celda(p['descripcion'][:90])} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Paso | Nuevo | Motivo |", "|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('paso'))} | "
                     f"{_celda(str(e.get('nuevo'))[:40])} | {_celda(e.get('motivo'))} |")
    else:
        L.append("Sin eventos.")
    if contenido["avisos"]:
        L += ["", "## Avisos", ""] + [f"- {a}" for a in contenido["avisos"]]
    L += ["", NOTA_COMPUERTA]
    return "\n".join(L) + "\n"


def escribir_vista(raiz) -> Path:
    p = _rutas(raiz)
    p["md"].write_bytes(vista(raiz).encode("utf-8"))
    contenido = cargar(raiz)
    for paso in contenido["pasos"]:
        (p["raiz"] / f"{PREFIJO_FICHA}{paso['id']}.md").write_bytes(_ficha(paso).encode("utf-8"))
    return p["md"]
