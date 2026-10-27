"""S10 — El cierre: un informe que un tercero recorre hasta la evidencia.

La herramienta ABRE el cierre a partir del borrador FIRMADO de S09 (ausente → código 2;
sin firmar → código 5), reproduce el contenido del borrador y le añade la TABLA DE
RECORRIDO: una entrada por afirmación del informe, con su sección, su ficha y la huella
esperada de la entrega de la que deriva. Antes de que el tercero recorra, la herramienta
recalcula cada huella (FR-005): lo que no verifica queda marcado y debe resolverse —
corregir o declarar con motivo— antes de firmar. El RECORRIDO lo ejecuta un tercero
(persona que no estuvo en la sala) y su resultado se REGISTRA con `cierre registrar`:
la herramienta no simula el recorrido (FR-013). El auditor CORRIGE la redacción y la
agrupación de la tabla, REVISA y FIRMA (principio I). El cierre no dictamina: presenta
trabajo verificable; las conclusiones del auditor, si las hay, quedan como su texto
firmado, identificado como tal (FR-006). Publicar o entregar el informe es decisión del
dueño: el cierre lo deja listo, no lo ejecuta.

Archivos que produce (FR-011, solo archivos nuevos en 04_informe/):
  - 04_informe/cierre_s10.json        contenido canónico (lo que se firma)
  - 04_informe/cierre_s10.firma.json  firma: firmante, fecha, justificación y huella
  - 04_informe/informe-cierre.md      informe final legible, con la tabla de recorrido

Reglas de diseño (misma forma que S03–S09): el historial es la fuente, nada se borra
(FR-007), el resultado es determinista (FR-010) y firmar exige el recorrido sin enlaces
sin resolver (FR-008).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import alcance
from . import borrador
from . import cita
from . import enunciado
from . import lista
from . import perfil
from . import registro
from .util import now_iso, sha256_bytes, sha256_file, short_id

PRODUCTO = "S10 — El cierre"
VERSION_ESQUEMA = "1"

APROBACION = ("borrador", "revisado")
EVENTOS = ("propuesta", "correccion", "resolucion", "registro", "revision", "firma_anulada")

ENLACE_VERIFICA = "verifica"
ENLACE_NO_VERIFICA = "no-verifica"
ENLACE_ILEGIBLE = "ilegible"
ENLACE_PENDIENTE = "pendiente"
ENLACE_DECLARADO = "declarado"
ENLACES_ABIERTOS = (ENLACE_NO_VERIFICA, ENLACE_ILEGIBLE, ENLACE_PENDIENTE)

NOTA_FIRMA = ("Firmar el cierre no publica ni entrega el informe: eso es decisión del dueño. "
              "Y no abre la compuerta de autorización.")
NOTA_TERCERO = ("El recorrido lo ejecuta un tercero que no estuvo en la sala; este registro "
                "se completa con su identidad, fecha y observaciones.")

ARCHIVO_JSON = "04_informe/cierre_s10.json"
ARCHIVO_MD = "04_informe/informe-cierre.md"
ARCHIVO_FIRMA = "04_informe/cierre_s10.firma.json"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"


class CierreError(Exception):
    """Operación rechazada. 1 regla · 2 falta S09 · 4 origen cambió · 5 S09 sin firmar."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Rutas, lectura y escritura (FR-011) ------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "borrador": r / borrador.ARCHIVO_JSON}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise CierreError(f"no existe {ARCHIVO_JSON}: ejecute primero «cierre abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise CierreError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in registro._PROHIBIDOS:
        if patron.search(v):
            raise CierreError(f"{nombre} contiene {clase}: el cierre no lo admite (FR-016)")
    return alcance.limpiar(v)


def _enmascarar(texto: str) -> str:
    """Correos y teléfonos quedan enmascarados (FR-016, datos personales)."""
    t = re.sub(r"([A-Za-z0-9._%+-])([A-Za-z0-9._%+-]*)(@[A-Za-z0-9.-]+)", r"\1***\3", texto)
    return t


# --- Contexto de origen (FR-001) ---------------------------------------------

def _entrega_actual(raiz) -> Dict[str, Any]:
    return borrador.entregar(raiz)


def _contexto(raiz, previo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["borrador"].exists():
        raise CierreError(f"no existe {borrador.ARCHIVO_JSON}: falta el producto anterior de S09; "
                          "ejecute primero «borrador abrir»", 2)
    entrega = _entrega_actual(raiz)
    if not entrega["firmado"]:
        raise CierreError("el borrador de S09 no está firmado: el cierre exige un borrador "
                          "aprobado por el auditor", 5)
    return {"archivo": borrador.ARCHIVO_JSON,
            "sha256": sha256_file(p["borrador"]),
            "entrega_sha256": sha256_bytes(alcance.serializar(entrega)),
            "firmado": True, "estado": entrega["estado"],
            "cliente": entrega["cliente"],
            "cadena": {s: c for s, c in entrega["origen"]["cadena"].items()}}


def _origen_cambio(raiz, contenido: Dict[str, Any]) -> bool:
    p = _rutas(raiz)
    ctx = contenido["origen"]
    if not p["borrador"].exists():
        return True
    if sha256_file(p["borrador"]) != ctx["sha256"]:
        return True
    actual = _entrega_actual(raiz)
    return sha256_bytes(alcance.serializar(actual)) != ctx["entrega_sha256"]


def _cargar_vigente(raiz) -> Dict[str, Any]:
    contenido = cargar(raiz)
    if _origen_cambio(raiz, contenido):
        raise CierreError("el borrador de origen (S09) cambió desde que se abrió el cierre: "
                          "ejecute «cierre abrir» y revise antes de cambiar nada", 4)
    return contenido


# --- Tabla de recorrido (FR-004) ----------------------------------------------

def _tabla(raiz) -> List[Dict[str, Any]]:
    """Una entrada por ficha del trabajo, con la huella esperada de su entrega."""
    r = Path(raiz)
    filas: List[Dict[str, Any]] = []

    def añadir(afirmacion: str, seccion: str, ficha: str, json_origen: str) -> None:
        filas.append({"id": short_id("T", ficha, afirmacion[:60]), "afirmacion": afirmacion,
                      "seccion": seccion, "ficha": ficha, "json_origen": json_origen,
                      "huella_esperada": sha256_file(r / json_origen), "estado": ENLACE_PENDIENTE,
                      "motivo": None, "correcciones": []})

    for e in enunciado.cargar(raiz)["enunciados"]:
        añadir(f"El riesgo {e['id']} enuncia: {e['condicion'][:80]}", "desarrollo",
               f"03_hallazgos/enunciado-{e['id']}.md", enunciado.ARCHIVO_JSON)
    for x in cita.cargar(raiz)["citas"]:
        añadir(f"La cita {x['id']} ubica el riesgo en {x['marco']} {x['version']}", "desarrollo",
               f"03_hallazgos/cita-{x['id']}.md", cita.ARCHIVO_JSON)
    for s in perfil.cargar(raiz)["secciones"]:
        slug = perfil._slug(s["funcion"])
        añadir(f"La función {s['funcion']} del perfil recoge {len(s['riesgos'])} riesgo(s)",
               "desarrollo", f"03_hallazgos/perfil-{slug}.md", perfil.ARCHIVO_JSON)
    for f in lista.cargar(raiz)["filas"]:
        if f["estado_aplicabilidad"] == "descartado":
            continue
        añadir(f"El control {f['control']} aplica según su justificación", "desarrollo",
               f"03_hallazgos/lista-{f['id']}.md", lista.ARCHIVO_JSON)
    for json_origen in (alcance.ARCHIVO_JSON, registro.ARCHIVO_JSON, enunciado.ARCHIVO_JSON,
                        cita.ARCHIVO_JSON, perfil.ARCHIVO_JSON, lista.ARCHIVO_JSON,
                        "01_plan/encargo_s07.json", borrador.ARCHIVO_JSON, frases_archivo()):
        añadir(f"La entrega `{json_origen}` es la que cita este informe", "anexo",
               json_origen, json_origen)
    return filas


def frases_archivo() -> str:
    return "04_informe/frases_s08.json"


def _recalcular(raiz, tabla: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """FR-005: recalcula cada huella antes del recorrido y marca lo que no verifica."""
    r = Path(raiz)
    for e in tabla:
        if e["estado"] in (ENLACE_DECLARADO,):
            continue
        ficha = r / e["ficha"]
        if not ficha.is_file():
            e["estado"] = ENLACE_NO_VERIFICA
            e["motivo"] = "la ficha no existe"
            continue
        try:
            ficha.read_bytes()
        except OSError:
            e["estado"] = ENLACE_ILEGIBLE
            e["motivo"] = "la ficha no se puede leer"
            continue
        if not (r / e["json_origen"]).is_file():
            e["estado"] = ENLACE_NO_VERIFICA
            e["motivo"] = f"no existe {e['json_origen']}"
            continue
        if sha256_file(r / e["json_origen"]) != e["huella_esperada"]:
            e["estado"] = ENLACE_NO_VERIFICA
            e["motivo"] = f"la huella de {e['json_origen']} no corresponde"
            continue
        if e["estado"] in ENLACES_ABIERTOS:
            e["estado"] = ENLACE_VERIFICA
            e["motivo"] = None
    return tabla


def _derivar(raiz, historial: List[Dict[str, Any]]) -> Dict[str, Any]:
    tabla = _tabla(raiz)
    for ev in historial:
        if ev["tipo"] == "correccion":
            e = next((x for x in tabla if x["id"] == ev["entrada"]), None)
            if e is None:
                continue
            e["afirmacion"] = ev["nuevo"]
            e["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"],
                                      "anterior": ev["anterior"], "nuevo": ev["nuevo"],
                                      "motivo": ev["motivo"]})
        elif ev["tipo"] == "resolucion":
            e = next((x for x in tabla if x["id"] == ev["entrada"]), None)
            if e is None:
                continue
            e["estado"] = ENLACE_DECLARADO
            e["motivo"] = ev["motivo"]
            e["correcciones"].append({"autor": ev["autor"], "fecha": ev["fecha"],
                                      "anterior": "pendiente", "nuevo": ENLACE_DECLARADO,
                                      "motivo": ev["motivo"]})
    return {"tabla": tabla}


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] in ("correccion", "resolucion", "registro", "revision"):
            estado = "revisado"
    return estado


def _componer(origen, secciones, derivado, registro_tercero, historial, avisos) -> Dict[str, Any]:
    tabla = derivado["tabla"]
    conteos = {"entradas": len(tabla),
               "verifican": sum(1 for e in tabla if e["estado"] == ENLACE_VERIFICA),
               "no_verifican": sum(1 for e in tabla if e["estado"] == ENLACE_NO_VERIFICA),
               "ilegibles": sum(1 for e in tabla if e["estado"] == ENLACE_ILEGIBLE),
               "pendientes": sum(1 for e in tabla if e["estado"] == ENLACE_PENDIENTE),
               "declarados": sum(1 for e in tabla if e["estado"] == ENLACE_DECLARADO)}
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "origen": origen,
            "cliente": origen.get("cliente", ""), "secciones": secciones, "tabla": tabla,
            "conteos": conteos, "registro_tercero": registro_tercero,
            "estado_aprobacion": _estado(historial), "historial": historial, "avisos": avisos}


# --- Abrir (US1, FR-001, FR-003) ----------------------------------------------

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
    secciones = _entrega_actual(raiz)["secciones"]
    derivado = _derivar(raiz, historial)
    derivado["tabla"] = _recalcular(raiz, derivado["tabla"])
    reg = contenido.get("registro_tercero")
    nuevo = _componer(origen, secciones, derivado, reg, historial, contenido["avisos"])
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
            "motivo": "Informe de cierre a partir del borrador firmado de S09."}]
        reg = None
    else:
        historial = previo["historial"]
        reg = previo.get("registro_tercero")
        if _origen_cambio(raiz, previo):
            avisos.append("Cambió el borrador de origen (S09) desde la versión anterior del cierre.")
    secciones = _entrega_actual(raiz)["secciones"]
    derivado = _derivar(raiz, historial)
    derivado["tabla"] = _recalcular(raiz, derivado["tabla"])
    contenido = _componer(origen, secciones, derivado, reg, historial, avisos)
    _escribir(raiz, contenido)
    return contenido


# --- Corregir, resolver, registrar, revisar, firmar (US2, US3, FR-007/8/13) ----

def _entrada(contenido: Dict[str, Any], entrada: str) -> Dict[str, Any]:
    e = next((x for x in contenido["tabla"] if x["id"] == entrada), None)
    if e is None:
        raise CierreError(f"no existe la entrada {entrada}")
    return e


def corregir(raiz, entrada: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    nuevo_valor = _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    e = _entrada(contenido, entrada)
    # una corrección no puede contradecir el borrador firmado: la afirmación debe seguir
    # citando la ficha de su entrada
    if e["ficha"] not in nuevo_valor and e["json_origen"] not in nuevo_valor:
        raise CierreError("la corrección contradice el borrador firmado: la afirmación debe "
                          f"seguir citando {e['ficha']} o {e['json_origen']} "
                          f"(huella del origen {contenido['origen']['sha256'][:12]}…)")
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "entrada": entrada,
          "anterior": e["afirmacion"], "nuevo": nuevo_valor, "motivo": motivo}
    return _entrada(_guardar(raiz, contenido, ev), entrada)


def resolver(raiz, entrada: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Resuelve un enlace «no-verifica» o «ilegible» declarándolo con motivo."""
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    e = _entrada(contenido, entrada)
    if e["estado"] not in ENLACES_ABIERTOS:
        raise CierreError(f"la entrada {entrada} está «{e['estado']}»: no hay nada que resolver")
    ev = {"tipo": "resolucion", "autor": autor, "fecha": fecha or now_iso(), "entrada": entrada,
          "anterior": e["estado"], "nuevo": ENLACE_DECLARADO, "motivo": motivo}
    return _entrada(_guardar(raiz, contenido, ev), entrada)


def registrar(raiz, tercero: str, observaciones: str, autor: Optional[str] = None,
              fecha: Optional[str] = None) -> Dict[str, Any]:
    """Registra el recorrido del tercero (FR-013). La herramienta no lo simula: quien
    recorre declara su identidad y el resultado; los datos personales se enmascaran."""
    tercero_l = _enmascarar(alcance.limpiar(_exigir(tercero, "el nombre del tercero")))
    obs = _enmascarar(_texto_libre(observaciones, "las observaciones"))
    contenido = _cargar_vigente(raiz)
    conteos = contenido["conteos"]
    reg = {"tercero": tercero_l, "fecha": fecha or now_iso(),
           "conteos": dict(conteos), "observaciones": obs, "nota": NOTA_TERCERO}
    ev = {"tipo": "registro", "autor": autor or tercero_l, "fecha": fecha or now_iso(),
          "anterior": None, "nuevo": "recorrido registrado", "motivo": observaciones[:120]}
    nuevo = _guardar(raiz, contenido, ev)
    nuevo["registro_tercero"] = reg
    _escribir(raiz, nuevo)
    return reg


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor,
                                      "fecha": fecha or now_iso(), "motivo": motivo})


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-008). Exige el recorrido sin enlaces sin resolver."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise CierreError("solo se firma un cierre «revisado»: registre una corrección o una revisión")
    abiertos = [e["id"] for e in contenido["tabla"] if e["estado"] in ENLACES_ABIERTOS]
    if abiertos:
        raise CierreError("no se puede firmar con enlaces sin resolver: " + ", ".join(abiertos))
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "entradas_al_firmar": len(contenido["tabla"]), "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar (FR-009) --------------------------------------------------------

def verificar(raiz) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["json"].exists():
        raise CierreError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    ilegible = False
    try:
        contenido = cargar(raiz)
    except ValueError:
        contenido = {"tabla": [], "origen": {}}
        ilegible = True
    entrega_ok = True
    if contenido.get("origen"):
        try:
            entrega_ok = (sha256_file(p["borrador"]) == contenido["origen"]["sha256"]
                          and sha256_bytes(alcance.serializar(_entrega_actual(raiz)))
                          == contenido["origen"]["entrega_sha256"])
        except borrador.BorradorError:
            entrega_ok = False
    abiertos = [] if ilegible else [e["id"] for e in contenido["tabla"] if e["estado"] in ENLACES_ABIERTOS]
    anexo_rotos: List[str] = []
    if not ilegible:
        r_ = Path(raiz)
        try:
            anexo_borrador = next((s for s in borrador.cargar(raiz)["secciones"]
                                   if s["nombre"] == "anexo"), None)
            if anexo_borrador:
                for m in re.finditer(r"`([^`]+\.json)` · `([0-9a-f]{64})`",
                                     anexo_borrador["contenido"]):
                    archivo, huella = m.group(1), m.group(2)
                    if not (r_ / archivo).is_file() or sha256_file(r_ / archivo) != huella:
                        anexo_rotos.append(archivo)
        except borrador.BorradorError:
            entrega_ok = False
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "huella_ok": None,
                         "entrega_ok": entrega_ok, "enlaces_abiertos": abiertos,
                         "anexo_rotos": anexo_rotos}
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
    if r["estado"] == "firmado" and (abiertos or anexo_rotos or not entrega_ok):
        partes = []
        if abiertos:
            partes.append("enlaces sin resolver")
        if anexo_rotos:
            partes.append("anexo del borrador con enlaces rotos")
        if not entrega_ok:
            partes.append("origen cambiado")
        r["estado_informado"] = "firmado con " + " y con ".join(partes)
    else:
        r["estado_informado"] = r["estado"]
    r["integro"] = (not abiertos and not anexo_rotos and entrega_ok
                    and not r["estado"].startswith("revisado"))
    return r


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


# --- Vista legible (FR-012) -----------------------------------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    partes: List[str] = []
    for s in contenido["secciones"]:
        partes.append(s["contenido"])
    informe = "\n\n---\n\n".join(partes)
    cabecera = (f"# Informe de cierre — {contenido['cliente']}\n\n"
                f"> Producto de la herramienta C4A: propone; el auditor corrige y firma.\n"
                f"> Publicar o entregar este informe es decisión del dueño: el cierre lo deja "
                f"listo y firmado, no lo ejecuta.\n\n"
                f"- Estado: {estado} · huella `{v['sha256_actual']}`\n"
                f"- Origen: `{contenido['origen']['archivo']}` (huella "
                f"`{contenido['origen']['sha256']}`)\n\n---\n\n")
    tabla = ["## Anexo — Tabla de recorrido (afirmación → ficha → huella)", ""]
    conteos = contenido["conteos"]
    tabla.append(f"Estados: {conteos['verifican']} verifican · {conteos['declarados']} declarados · "
                 f"{conteos['no_verifican']} no verifican · {conteos['ilegibles']} ilegibles · "
                 f"{conteos['pendientes']} pendientes.")
    tabla += ["", "| Entrada | Afirmación | Sección | Ficha | Estado | Motivo |",
              "|---|---|---|---|---|---|"]
    for e in contenido["tabla"]:
        tabla.append(f"| `{e['id']}` | {_celda(e['afirmacion'][:80])} | {e['seccion']} | "
                     f"`{_celda(e['ficha'])}` | {e['estado']} | {_celda(e['motivo'])} |")
    reg = contenido.get("registro_tercero")
    tabla += ["", "## Registro del recorrido del tercero", ""]
    if reg:
        tabla.append(f"- Tercero: {reg['tercero']} · fecha: {reg['fecha']}")
        tabla.append(f"- Conteos al recorrer: {reg['conteos']}")
        tabla.append(f"- Observaciones: {reg['observaciones']}")
    else:
        tabla.append("Sin registrar: el recorrido lo ejecuta un tercero y se registra con "
                     "«cierre registrar» (la herramienta no lo simula).")
    return cabecera + informe + "\n\n---\n\n" + "\n".join(tabla) + "\n"


def escribir_vista(raiz) -> Path:
    p = _rutas(raiz)
    p["md"].write_bytes(vista(raiz).encode("utf-8"))
    return p["md"]
