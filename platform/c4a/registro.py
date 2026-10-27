"""S02 — El registro: hechos con su evidencia y su huella, y lo que no consta.

La herramienta ABRE el registro a partir del alcance de S01 (una entrada «no consta»
por el activo y por cada dominio dentro o pendiente), PROPONE una entrada cuando el
auditor aporta una evidencia y RECHAZA la que no acredita esta auditoría. El auditor
CORRIGE, DESCARTA, RESTABLECE, REVISA y FIRMA (constitución, principio I). Nada de
este módulo abre la compuerta de autorización, ejecuta pruebas ni escribe en `scope/`.

Archivos que produce (ver specs/002-registro-hechos/data-model.md):
  - 02_evidencia/registro_s02.json        contenido canónico (lo que se firma)
  - 02_evidencia/registro_s02.firma.json  firma: firmante, fecha, justificación y huella
  - 02_evidencia/registro_s02.md          vista legible para un tercero
  - evidence/registro_s02/<E-…>.<ext>     copia de cada evidencia aportada (fuera de git)

Reglas de diseño (research D1–D10):
  - El historial es la fuente: las entradas se derivan del alcance más el historial
    reaplicado en orden. Nada se borra (FR-013) y el resultado es determinista (FR-018).
  - La huella guardada se calcula sobre la copia ya escrita; la del original, aparte
    (principio III).
  - El registro nunca copia contenido de la evidencia: cita tipo, origen, ubicación y
    huella (FR-012).
  - El registro no dictamina: no hay estados de cumplimiento (FR-011).
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alcance
from .util import now_iso, sha256_file, short_id

PRODUCTO = "S02 — El registro"
VERSION_ESQUEMA = "1"

RESULTADOS = ("positivo", "negativo", "inconcluso", "no-ejecutado")
RESULTADOS_EVIDENCIA = ("positivo", "negativo", "inconcluso")
TIPOS_EVIDENCIA = ("documental", "tecnica")
APROBACION = ("borrador", "revisado")  # «firmado» se deriva de una firma válida
CAMPOS_CORREGIBLES = ("afirmacion", "resultado", "motivo")
EVENTOS = ("aporte", "rechazo", "correccion", "descarte", "restablecimiento", "revision", "firma_anulada")

HECHO = "hecho"
NO_CONSTA = "no consta"

MARCA_DESCARTADA = "descartada"
MARCA_SUPERADA = "superada por "  # + id del hecho
MARCA_FUERA = "fuera del alcance vigente"
MARCA_PENDIENTE = "alcance pendiente"
MARCA_ALTERADA = "evidencia alterada"  # se calcula al verificar; no se persiste
MARCAS = (MARCA_DESCARTADA, MARCA_SUPERADA + "H-…", MARCA_FUERA, MARCA_PENDIENTE, MARCA_ALTERADA)

MOTIVO_COMPUERTA = "compuerta cerrada"
MOTIVO_DOCUMENTAL = "requiere solicitud documental"
MOTIVO_SIN_EVIDENCIA = "sin evidencia"
MOTIVOS_NO_CONSTA = (MOTIVO_COMPUERTA, MOTIVO_DOCUMENTAL, MOTIVO_SIN_EVIDENCIA)

RECHAZO_ACTIVO = "otro activo"
RECHAZO_DOMINIO = "dominio fuera del alcance"
RECHAZO_OBJETIVO = "otro objetivo"
RECHAZO_AUTORIZACION = "sin autorización vigente"
RECHAZO_ORIGEN = "origen no declarado"

ARCHIVO_JSON = "02_evidencia/registro_s02.json"
ARCHIVO_MD = "02_evidencia/registro_s02.md"
ARCHIVO_FIRMA = "02_evidencia/registro_s02.firma.json"
CARPETA_COPIAS = "evidence/registro_s02"
LEDGER = ".c4a/runs.jsonl"

DOMINIO_ACTIVO = "(el activo como un todo)"
RESPONSABLE_HERRAMIENTA = "C4A (propuesta de la herramienta)"
NOTA_FIRMA = "Firmar el registro no abre la compuerta de autorización."
NOTA_NO_CONSTA = ("«No consta» quiere decir que no se miró o que falta evidencia admisible: no es una "
                  "ausencia de hallazgos ni un dictamen de cumplimiento.")
_OBS_DOCUMENTAL = "no se acredita con una prueba técnica"

# Textos libres que no pueden entrar al registro (FR-011, FR-012).
_PROHIBIDOS = (
    ("un estado de cumplimiento", re.compile(r"(?i)\b(cumple|parcial|no-cumple|no-evaluado|no-aplica)\b")),
    ("un número de puerto", re.compile(r"(?i)\bpuertos?\s*:?\s*\d{1,5}\b|:\d{2,5}\b")),
    ("una forma de comando", re.compile(r"(?m)^\s*[$#]\s|(?:^|\s)--[a-z]|\bsudo\b")),
    ("una forma de credencial", re.compile(r"(?i)\b(password|passwd|contraseña|clave|token|secret)\s*[=:]")),
)


class RegistroError(Exception):
    """Operación rechazada. `codigo` sigue contracts/cli-registro.md."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Rutas, lectura y escritura (FR-017, FR-018) ---------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "md": r / ARCHIVO_MD, "firma": r / ARCHIVO_FIRMA,
            "copias": r / CARPETA_COPIAS, "ledger": r / LEDGER,
            "alcance": r / alcance.ARCHIVO_JSON, "autorizacion": r / alcance.INSUMO_AUTORIZACION}


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise RegistroError(f"no existe {ARCHIVO_JSON}: ejecute primero «registro abrir»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _exigir(valor: Optional[str], nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise RegistroError(f"falta {nombre}: es obligatorio")
    return v


def _texto_libre(valor: Optional[str], nombre: str, obligatorio: bool = True) -> str:
    """Texto escrito por el auditor: sin estados de cumplimiento, puertos, comandos ni
    credenciales (FR-011, FR-012); las direcciones de red se reemplazan con `limpiar`."""
    v = _exigir(valor, nombre) if obligatorio else (valor or "").strip()
    for clase, patron in _PROHIBIDOS:
        if patron.search(v):
            raise RegistroError(f"{nombre} contiene {clase}: el registro no lo admite (FR-011, FR-012)")
    return alcance.limpiar(v)


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "").strip().lower())


# --- Identificadores (FR-020, research D4 y D5) ----------------------------

def id_hecho(activo: str, fila_dominio: Optional[str], afirmacion: str) -> str:
    return short_id("H", activo, fila_dominio or "activo", _normalizar(afirmacion))


def id_no_consta(activo: str, fila_dominio: Optional[str]) -> str:
    return short_id("N", activo, fila_dominio or "activo")


def id_evidencia(sha256_original: str, tipo: str) -> str:
    return short_id("E", sha256_original, tipo)


# --- Lectura del alcance de S01 (contrato con S01, FR-001) ----------------

def _clasificar(fila: Dict[str, Any]) -> str:
    """Misma regla que `alcance.consultar` para una fila ya ubicada."""
    if alcance.es_pendiente(fila):
        return "pendiente"
    if fila["decision"] == "excluido":
        return "fuera"
    return "dentro"


def _nombre_activo(fila: Dict[str, Any]) -> str:
    return fila["valor"].split(" (")[0].strip()


def _filas_alcance(raiz) -> Tuple[List[Dict[str, Any]], bool]:
    """Filas del alcance de S01. Sin `alcance_s01.json`, se derivan en memoria (mínimo de
    referencia) sin escribir nada en `scope/`."""
    p = _rutas(raiz)
    if p["alcance"].exists():
        return alcance.cargar(raiz)["filas"], False
    _insumos, filas, _avisos = alcance.derivar(raiz)
    return filas, True


def _contexto(raiz, previo: Optional[Dict[str, Any]], fecha_referencia: Optional[date]) -> Dict[str, Any]:
    """Bloque `alcance` del registro. La compuerta se evalúa una vez y se guarda: así la misma
    entrada produce los mismos bytes (FR-018, análisis I2)."""
    p = _rutas(raiz)
    minimo = not p["alcance"].exists()
    aut_sha = sha256_file(p["autorizacion"]) if p["autorizacion"].exists() else None
    ant = (previo or {}).get("alcance") or {}
    if fecha_referencia is None and ant.get("autorizacion_sha256") == aut_sha and ant.get("compuerta"):
        compuerta, fecha = ant["compuerta"], ant["compuerta_fecha"]
    else:
        c = alcance.evaluar_compuerta(raiz, fecha_referencia)
        compuerta, fecha = c["resultado"], c["fecha_referencia"]
    return {
        "archivo": alcance.ARCHIVO_JSON if not minimo else alcance.INSUMO_ALCANCE,
        "sha256": None if minimo else sha256_file(p["alcance"]),
        "firmado": False if minimo else alcance.estado_efectivo(raiz) == "firmado",
        "minimo_de_referencia": minimo,
        "autorizacion_sha256": aut_sha,
        "compuerta": compuerta,
        "compuerta_fecha": fecha,
    }


# --- Derivación: alcance + historial → entradas (research D1) -------------

def _motivo_no_consta(fila: Optional[Dict[str, Any]], compuerta: str) -> str:
    if fila is None:
        return MOTIVO_SIN_EVIDENCIA
    if _OBS_DOCUMENTAL in (fila.get("observacion") or ""):
        return MOTIVO_DOCUMENTAL
    if fila["clave"].startswith("tecnico:") and compuerta != "abierta":
        return MOTIVO_COMPUERTA
    return MOTIVO_SIN_EVIDENCIA


def _base(filas: List[Dict[str, Any]], compuerta: str) -> Tuple[Dict[str, Dict], Dict[Tuple, str]]:
    """Entradas «no consta» del alcance vigente y la clasificación de cada (activo, fila)."""
    entradas: Dict[str, Dict] = {}
    clase: Dict[Tuple, str] = {}
    activos = [f for f in filas if f["tipo"] == "activo" and f["valor"]]
    dominios = [f for f in filas if f["tipo"] == "dominio" and f["valor"]]
    for fa in activos:
        nombre = _nombre_activo(fa)
        c_act = _clasificar(fa)
        clase[(nombre, None)] = c_act
        objetivos = [(None, DOMINIO_ACTIVO, c_act, None)]
        for fd in dominios:
            c_dom = _clasificar(fd)
            c = "fuera" if "fuera" in (c_act, c_dom) else ("pendiente" if "pendiente" in (c_act, c_dom) else "dentro")
            clase[(nombre, fd["id"])] = c
            objetivos.append((fd["id"], fd["valor"], c, fd))
        for fila_id, valor, c, fd in objetivos:
            if c == "fuera":
                continue
            eid = id_no_consta(nombre, fila_id)
            entradas[eid] = {
                "id": eid, "clase": NO_CONSTA, "activo": nombre,
                "dominio": {"fila": fila_id, "valor": valor},
                "afirmacion": NO_CONSTA, "resultado": "no-ejecutado",
                "motivo": _motivo_no_consta(fd, compuerta), "evidencias": [],
                "responsable": RESPONSABLE_HERRAMIENTA, "estado_aprobacion": "borrador",
                "marcas": [MARCA_PENDIENTE] if c == "pendiente" else [],
            }
    return entradas, clase


def _resultado_de(evidencias: List[Dict[str, Any]]) -> str:
    vistos = {e["resultado"] for e in evidencias}
    return vistos.pop() if len(vistos) == 1 else "inconcluso"


def _derivar(filas: List[Dict[str, Any]], compuerta: str, historial: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    entradas, clase = _base(filas, compuerta)
    corregido_resultado = set()
    for ev in historial:
        t = ev["tipo"]
        if t == "aporte":
            e = entradas.get(ev["entrada"])
            if e is None:
                e = entradas[ev["entrada"]] = {
                    "id": ev["entrada"], "clase": HECHO, "activo": ev["activo"], "dominio": dict(ev["dominio"]),
                    "afirmacion": ev["afirmacion"], "resultado": ev["evidencia"]["resultado"], "motivo": "",
                    "evidencias": [], "responsable": ev["autor"], "estado_aprobacion": "borrador", "marcas": [],
                }
            if all(x["id"] != ev["evidencia"]["id"] for x in e["evidencias"]):
                e["evidencias"].append(dict(ev["evidencia"]))
                e["evidencias"].sort(key=lambda x: x["id"])
            if e["id"] not in corregido_resultado:
                e["resultado"] = _resultado_de(e["evidencias"])
        elif t in ("correccion", "descarte", "restablecimiento"):
            e = entradas.get(ev["entrada"])
            if e is None:
                continue
            if t == "correccion":
                e[ev["campo"]] = ev["nuevo"]
                if ev["campo"] == "resultado":
                    corregido_resultado.add(e["id"])
            elif t == "descarte":
                if MARCA_DESCARTADA not in e["marcas"]:
                    e["marcas"].append(MARCA_DESCARTADA)
            else:
                e["marcas"] = [m for m in e["marcas"] if m != MARCA_DESCARTADA]
            e["estado_aprobacion"] = "revisado"
    # Marcas derivadas del alcance vigente y de los hechos vigentes (FR-015, FR-021, análisis U3).
    vigentes_por_objetivo: Dict[Tuple, List[str]] = {}
    for e in entradas.values():
        if e["clase"] != HECHO:
            continue
        c = clase.get((e["activo"], e["dominio"]["fila"]), "fuera")
        e["marcas"] = [m for m in e["marcas"] if m not in (MARCA_FUERA, MARCA_PENDIENTE)]
        if c == "fuera":
            e["marcas"].append(MARCA_FUERA)
        elif c == "pendiente":
            e["marcas"].append(MARCA_PENDIENTE)
        if MARCA_DESCARTADA not in e["marcas"] and c != "fuera":
            vigentes_por_objetivo.setdefault((e["activo"], e["dominio"]["fila"]), []).append(e["id"])
    for e in entradas.values():
        if e["clase"] == NO_CONSTA:
            hechos = sorted(vigentes_por_objetivo.get((e["activo"], e["dominio"]["fila"]), []))
            if hechos:
                e["marcas"].append(MARCA_SUPERADA + hechos[0])
        e["marcas"] = sorted(e["marcas"])
    return sorted(entradas.values(),
                  key=lambda e: (e["activo"], e["dominio"]["fila"] or "", e["clase"] != NO_CONSTA, e["id"]))


def _estado(historial: List[Dict[str, Any]]) -> str:
    estado = "borrador"
    for ev in historial:
        if ev["tipo"] == "aporte":
            estado = "borrador"  # un aporte tras la revisión exige revisar de nuevo (análisis U4)
        elif ev["tipo"] in ("correccion", "descarte", "restablecimiento", "revision"):
            estado = "revisado"
    return estado


def _rechazos(historial: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: v for k, v in ev.items() if k != "tipo"} for ev in historial if ev["tipo"] == "rechazo"]


def _componer(ctx, entradas, historial, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "alcance": ctx, "entradas": entradas,
            "rechazos": _rechazos(historial), "estado_aprobacion": _estado(historial),
            "historial": historial, "avisos": avisos}


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
    """Único punto de escritura de las acciones del auditor: agrega el evento, anula una firma
    previa (análisis I1) y recompone las entradas."""
    filas, _minimo = _filas_alcance(raiz)
    historial = contenido["historial"] + [evento]
    _anular_firma(raiz, historial, evento["autor"], evento["fecha"])
    nuevo = _componer(contenido["alcance"], _derivar(filas, contenido["alcance"]["compuerta"], historial),
                      historial, contenido["avisos"])
    _escribir(raiz, nuevo)
    return nuevo


def _cargar_vigente(raiz) -> Dict[str, Any]:
    """Carga el registro y exige que el alcance no haya cambiado desde `abrir`."""
    contenido = cargar(raiz)
    p = _rutas(raiz)
    actual = sha256_file(p["alcance"]) if p["alcance"].exists() else None
    if actual != contenido["alcance"]["sha256"]:
        raise RegistroError("el alcance de S01 cambió desde que se abrió el registro: ejecute «registro abrir»")
    return contenido


# --- Abrir (US1, FR-001 a FR-003, FR-015) -----------------------------------

def abrir(raiz, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
    p = _rutas(raiz)
    previo = cargar(raiz) if p["json"].exists() else None
    filas, minimo = _filas_alcance(raiz)
    ctx = _contexto(raiz, previo, fecha_referencia)
    historial = previo["historial"] if previo else []
    entradas = _derivar(filas, ctx["compuerta"], historial)
    avisos: List[str] = []
    if minimo:
        avisos.append(f"Falta el producto anterior (S01, {alcance.ARCHIVO_JSON}): se usa "
                      f"{alcance.INSUMO_ALCANCE} como mínimo de referencia; no se admiten aportes.")
    if not ctx["firmado"]:
        avisos.append("El registro se basa en un alcance no firmado.")
    if previo:
        ant = previo["alcance"]
        cambios = [n for n, k in (("el alcance", "sha256"), ("la autorización", "autorizacion_sha256"),
                                  ("el estado de la compuerta", "compuerta"),
                                  ("la firma del alcance", "firmado")) if ant.get(k) != ctx[k]]
        if cambios:
            afectadas = [e["id"] for e in entradas if MARCA_FUERA in e["marcas"]]
            avisos.append(f"Cambió {', '.join(cambios)} desde la versión anterior del registro; entradas "
                          f"afectadas: {', '.join(afectadas) or 'ninguna fuera del alcance vigente'}.")
    contenido = _componer(ctx, entradas, historial, avisos)
    nuevos = alcance.serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        raise RegistroError("El registro está firmado y el alcance, la autorización o la compuerta cambiaron. "
                            "No se actualiza solo: revise y vuelva a firmar a partir de un cambio explícito.", 4)
    _escribir(raiz, contenido)
    return contenido


# --- Aportar y rechazar (US2, US4, FR-005 a FR-007, FR-020, FR-021) --------

def _ubicacion(raiz, ruta: Path) -> str:
    try:
        return ruta.resolve().relative_to(Path(raiz).resolve()).as_posix()
    except ValueError:
        return ruta.name


def _objetivo_corrida(raiz, corrida: str) -> Optional[str]:
    """`target` de una corrida del ledger, en solo lectura. No se instancia `Ledger`: su
    constructor crea la carpeta."""
    ruta = _rutas(raiz)["ledger"]
    if not ruta.exists():
        return None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea:
            r = json.loads(linea)
            if r.get("run_id") == corrida:
                return r.get("target") or ""
    return None


def _ubicar_dominio(raiz, filas, dominio: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """→ (fila de dominio o None, clasificación). `activo` designa la entrada del activo."""
    if dominio.strip().lower() == "activo":
        return None, "activo"
    if re.match(r"^A-[0-9a-f]{10}$", dominio.strip()):
        fila = next((f for f in filas if f["id"] == dominio.strip() and f["tipo"] == "dominio"), None)
        return (fila, _clasificar(fila)) if fila else (None, "fuera")
    r = alcance.consultar(raiz, "dominio", dominio)
    if r["fila"] is None:
        return None, "fuera"
    fila = next(f for f in filas if f["id"] == r["fila"]["id"])
    return fila, r["respuesta"]


def _admisible(raiz, *, act: Dict[str, Any], fila_act, fila_dom, c_dom: str, tipo: str, origen: str,
               corrida: Optional[str], fecha_recoleccion: date) -> Optional[Tuple[str, str, Optional[str]]]:
    """Primer motivo de rechazo, en el orden de research D3 → (motivo, regla, fila), o None."""
    if act["respuesta"] == "fuera":
        return RECHAZO_ACTIVO, act["motivo"] or "el activo no es el del alcance", fila_act
    if c_dom == "fuera":
        return (RECHAZO_DOMINIO, "el dominio no figura en el alcance o está excluido",
                fila_dom["id"] if fila_dom else None)
    if corrida:
        objetivo = _objetivo_corrida(raiz, corrida)
        nombre = _nombre_activo({"valor": act.get("valor", "")}) if act.get("valor") else ""
        if objetivo is None or alcance._norm(objetivo) != alcance._norm(nombre):
            return (RECHAZO_OBJETIVO, "la corrida no figura en el ledger o su objetivo registrado no es el activo",
                    fila_act)
    if tipo == "tecnica":
        c = alcance.evaluar_compuerta(raiz, fecha_recoleccion)
        if c["resultado"] != "abierta":
            return (RECHAZO_AUTORIZACION, "compuerta " + c["resultado"] + " en la fecha de recolección: "
                    + "; ".join(c["motivos"]), None)
    if tipo == "documental" and not origen:
        return RECHAZO_ORIGEN, "la evidencia documental exige origen declarado", None
    return None


def aportar(raiz, activo: str, dominio: str, afirmacion: str, resultado: str, evidencia, tipo: str,
            fecha_recoleccion: str, autor: str, origen: Optional[str] = None, corrida: Optional[str] = None,
            sin_copia: bool = False, fecha: Optional[str] = None) -> Dict[str, Any]:
    p = _rutas(raiz)
    if not p["alcance"].exists():
        raise RegistroError(f"falta el alcance de S01 ({alcance.ARCHIVO_JSON}): sin él no se admiten hechos", 2)
    contenido = _cargar_vigente(raiz)
    ruta = Path(evidencia)
    if not ruta.is_file():
        raise RegistroError(f"no existe o no se puede leer el archivo de evidencia: {ruta.name}", 2)
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    afirmacion = _texto_libre(afirmacion, "la afirmación")
    origen = _texto_libre(origen, "el origen", obligatorio=False)
    if resultado not in RESULTADOS_EVIDENCIA:
        raise RegistroError(f"resultado no válido: {resultado} (use {', '.join(RESULTADOS_EVIDENCIA)})")
    if tipo not in TIPOS_EVIDENCIA:
        raise RegistroError(f"tipo no válido: {tipo} (use {', '.join(TIPOS_EVIDENCIA)})")
    try:
        f_rec = date.fromisoformat(fecha_recoleccion)
    except (TypeError, ValueError):
        raise RegistroError("fecha de recolección no válida: use AAAA-MM-DD")
    fecha = fecha or now_iso()
    sha_original = sha256_file(ruta)
    filas, _minimo = _filas_alcance(raiz)
    act = alcance.consultar(raiz, "activo", activo)
    fila_act = act["fila"]["id"] if act["fila"] else None
    if fila_act:
        act["valor"] = next(f["valor"] for f in filas if f["id"] == fila_act)
    fila_dom, c_dom = _ubicar_dominio(raiz, filas, dominio)
    if c_dom == "activo":
        c_dom = act["respuesta"]
    rechazo = _admisible(raiz, act=act, fila_act=fila_act, fila_dom=fila_dom, c_dom=c_dom, tipo=tipo,
                         origen=origen, corrida=corrida, fecha_recoleccion=f_rec)
    ubicacion = _ubicacion(raiz, ruta)
    if rechazo:
        motivo, regla, fila = rechazo
        ev = {"tipo": "rechazo", "autor": autor, "fecha": fecha,
              "evidencia": {"tipo": tipo, "ubicacion": ubicacion, "sha256": sha_original},
              "activo": alcance.limpiar(activo), "dominio": alcance.limpiar(dominio), "motivo": motivo,
              "regla": alcance.limpiar(regla), "fila_alcance": fila}
        _guardar(raiz, contenido, ev)
        return {"aceptada": False, "motivo": motivo, "regla": ev["regla"], "fila_alcance": fila}
    nombre = _nombre_activo({"valor": act["valor"]})
    eid = id_evidencia(sha_original, tipo)
    copia, sha_guardado = None, None
    if not sin_copia:
        destino = p["copias"] / f"{eid}{ruta.suffix.lower()}"
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists() and sha256_file(destino) != sha_original:
            raise RegistroError(f"la copia guardada {destino.name} no coincide con el original: "
                                "evidencia alterada; no se reutiliza (principio III)", 3)
        if not destino.exists():
            shutil.copyfile(ruta, destino)
        copia = destino.relative_to(p["raiz"]).as_posix()
        sha_guardado = sha256_file(destino)  # huella de los bytes ya escritos (principio III)
    dom = {"fila": fila_dom["id"], "valor": fila_dom["valor"]} if fila_dom else {"fila": None, "valor": DOMINIO_ACTIVO}
    entrada = id_hecho(nombre, dom["fila"], afirmacion)
    ev = {"tipo": "aporte", "autor": autor, "fecha": fecha, "entrada": entrada, "activo": nombre,
          "dominio": dom, "afirmacion": afirmacion,
          "evidencia": {"id": eid, "tipo": tipo, "origen": origen, "ubicacion_original": ubicacion,
                        "copia": copia, "sin_copia": bool(sin_copia), "sha256_original": sha_original,
                        "sha256_guardado": sha_guardado, "fecha_recoleccion": f_rec.isoformat(),
                        "responsable": autor, "resultado": resultado, "corrida": corrida or None}}
    _guardar(raiz, contenido, ev)
    return {"aceptada": True, "entrada": entrada, "evidencia": eid}


# --- Corregir, descartar, restablecer, revisar, firmar (US2, FR-013, FR-014) --

def _entrada(contenido: Dict[str, Any], entrada: str) -> Dict[str, Any]:
    e = next((x for x in contenido["entradas"] if x["id"] == entrada), None)
    if e is None:
        raise RegistroError(f"no existe la entrada {entrada}")
    return e


def corregir(raiz, entrada: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise RegistroError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    if campo == "resultado" and valor not in RESULTADOS:
        raise RegistroError(f"resultado no válido: {valor} (use {', '.join(RESULTADOS)})")
    nuevo_valor = valor if campo == "resultado" else _texto_libre(valor, "el valor nuevo")
    contenido = _cargar_vigente(raiz)
    e = _entrada(contenido, entrada)
    if not e["evidencias"] and ((campo == "resultado" and nuevo_valor != "no-ejecutado")
                                or (campo == "afirmacion" and _normalizar(nuevo_valor) != NO_CONSTA)):
        raise RegistroError(f"la entrada {entrada} no cita evidencia: no puede afirmar un hecho; aporte una "
                            "evidencia admisible (FR-006)")
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha or now_iso(), "entrada": entrada,
          "campo": campo, "anterior": e[campo], "nuevo": nuevo_valor, "motivo": motivo}
    nuevo = _guardar(raiz, contenido, ev)
    return _entrada(nuevo, entrada)


def _marcar(raiz, tipo: str, entrada: str, motivo: str, autor: str, fecha: Optional[str]) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    e = _entrada(contenido, entrada)
    descartada = MARCA_DESCARTADA in e["marcas"]
    if tipo == "descarte" and descartada:
        raise RegistroError(f"la entrada {entrada} ya está descartada")
    if tipo == "restablecimiento" and not descartada:
        raise RegistroError(f"la entrada {entrada} no está descartada: no hay nada que restablecer")
    ev = {"tipo": tipo, "autor": autor, "fecha": fecha or now_iso(), "entrada": entrada,
          "anterior": "descartada" if descartada else "vigente",
          "nuevo": "vigente" if descartada else "descartada", "motivo": motivo}
    return _entrada(_guardar(raiz, contenido, ev), entrada)


def descartar(raiz, entrada: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "descarte", entrada, motivo, autor, fecha)


def restablecer(raiz, entrada: str, motivo: str, autor: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    return _marcar(raiz, "restablecimiento", entrada, motivo, autor, fecha)


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = _texto_libre(motivo, "el motivo")
    autor = alcance.limpiar(_exigir(autor, "el autor"))
    contenido = _cargar_vigente(raiz)
    return _guardar(raiz, contenido, {"tipo": "revision", "autor": autor, "fecha": fecha or now_iso(),
                                      "motivo": motivo})


def no_consta_vigentes(contenido: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [e for e in contenido["entradas"] if e["clase"] == NO_CONSTA
            and not any(m.startswith(MARCA_SUPERADA) or m in (MARCA_FUERA, MARCA_DESCARTADA)
                        for m in e["marcas"])]


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-014). Registra quién, cuándo y con qué justificación
    (principio I). La huella es de los bytes ya guardados (principio III)."""
    firmante = alcance.limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = _texto_libre(motivo, "la justificación de la firma")
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise RegistroError("solo se firma un registro «revisado»: registre una corrección o una revisión")
    p = _rutas(raiz)
    firma = {"archivo": Path(ARCHIVO_JSON).name, "sha256": sha256_file(p["json"]), "firmante": firmante,
             "fecha": fecha or now_iso(), "motivo": motivo,
             "no_consta_al_firmar": len(no_consta_vigentes(contenido)), "nota": NOTA_FIRMA}
    p["firma"].write_bytes(alcance.serializar(firma))
    escribir_vista(raiz)
    return firma


# --- Verificar y entregar (FR-008, FR-019) ---------------------------------

def _evidencias_alteradas(raiz, contenido: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    r = Path(raiz)
    entradas, evidencias = [], []
    for e in contenido["entradas"]:
        for ev in e["evidencias"]:
            if ev["copia"]:
                ruta, esperado = r / ev["copia"], ev["sha256_guardado"]
            else:
                ruta, esperado = r / ev["ubicacion_original"], ev["sha256_original"]
                if not ruta.is_file():
                    continue  # referencia sin copia fuera de alcance: no verificable, no alterada
            if not ruta.is_file() or sha256_file(ruta) != esperado:
                evidencias.append(ev["id"])
                if e["id"] not in entradas:
                    entradas.append(e["id"])
    return entradas, sorted(set(evidencias))


def verificar(raiz) -> Dict[str, Any]:
    """Recalcula la huella del registro guardado y de cada evidencia, sin regenerar nada."""
    p = _rutas(raiz)
    if not p["json"].exists():
        raise RegistroError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    try:
        contenido = cargar(raiz)
    except ValueError:  # bytes alterados hasta volverlo ilegible: la huella ya lo delata
        contenido = {"entradas": []}
    alteradas, evidencias = _evidencias_alteradas(raiz, contenido)
    r: Dict[str, Any] = {"sha256_actual": actual, "sha256_firmado": None, "entradas_alteradas": alteradas,
                         "evidencias_alteradas": evidencias}
    if not p["firma"].exists():
        r["estado"] = "sin firma"
    else:
        firma = json.loads(p["firma"].read_bytes().decode("utf-8"))
        r["sha256_firmado"] = firma.get("sha256")
        if firma.get("sha256") == actual:
            r.update(estado="firmado", firmante=firma.get("firmante"), fecha=firma.get("fecha"),
                     motivo=firma.get("motivo"), no_consta_al_firmar=firma.get("no_consta_al_firmar"))
        else:
            r["estado"] = "revisado (firma no aplica)"
    r["estado_informado"] = ("firmado con evidencia alterada" if r["estado"] == "firmado" and alteradas
                             else r["estado"])
    r["integro"] = not alteradas and not r["estado"].startswith("revisado")
    return r


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


def entregar(raiz) -> Dict[str, Any]:
    """Lo que recibe S03: solo las entradas vigentes (FR-019)."""
    contenido = cargar(raiz)
    v = verificar(raiz)
    alteradas = set(v["entradas_alteradas"])
    salida = []
    for e in contenido["entradas"]:
        if e["clase"] == HECHO:
            if MARCA_DESCARTADA in e["marcas"] or MARCA_FUERA in e["marcas"] or e["id"] in alteradas:
                continue
        elif e not in no_consta_vigentes(contenido):
            continue
        salida.append({"id": e["id"], "clase": e["clase"], "activo": e["activo"], "dominio": e["dominio"],
                       "afirmacion": e["afirmacion"], "resultado": e["resultado"], "motivo": e["motivo"],
                       "marcas": e["marcas"],
                       "evidencias": [{k: x[k] for k in ("id", "tipo", "ubicacion_original", "copia",
                                                         "sha256_original", "sha256_guardado")}
                                      for x in e["evidencias"]]})
    return {"producto": PRODUCTO, "firmado": v["estado"] == "firmado", "estado": v["estado_informado"],
            "alcance": contenido["alcance"], "entradas": salida}


# --- Vista legible (FR-016, principio VIII) --------------------------------

def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


def vista(raiz) -> str:
    contenido = cargar(raiz)
    v = verificar(raiz)
    estado = estado_efectivo(raiz)
    ctx = contenido["alcance"]
    alteradas = set(v["entradas_alteradas"])
    nc = no_consta_vigentes(contenido)
    hechos = [e for e in contenido["entradas"] if e["clase"] == HECHO]
    otras = [e for e in contenido["entradas"] if e["clase"] == NO_CONSTA and e not in nc]
    L = [f"# El registro (S02) — {v['estado_informado'] if estado == 'firmado' else estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         "> El registro anota hechos y vacíos: no contiene conclusiones sobre controles.", "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{v['sha256_actual']}`"]
    if v["estado"] == "firmado":
        L.append(f"- **Firma**: {v['firmante']}, {v['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {v.get('motivo') or '—'}")
    elif v["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += [f"- **Alcance de origen**: `{ctx['archivo']}` · huella {_celda(ctx['sha256'])} · "
          + ("firmado" if ctx["firmado"] else "**alcance no firmado**")
          + (" · mínimo de referencia" if ctx["minimo_de_referencia"] else ""),
          f"- **Compuerta de autorización**: {ctx['compuerta']} (evaluada el {ctx['compuerta_fecha']}); "
          "la herramienta solo la lee.",
          f"- **Resumen**: {len(nc)} entradas no constan · {len(hechos)} hechos · "
          f"{len(contenido['rechazos'])} rechazos.", "", NOTA_NO_CONSTA, "",
          f"## No consta ({len(nc)})", ""]
    if nc:
        L += ["| Id | Activo | Dominio | Resultado | Motivo | Marcas |", "|---|---|---|---|---|---|"]
        for e in nc:
            L.append(f"| `{e['id']}` | {_celda(e['activo'])} | {_celda(e['dominio']['valor'])} | {e['resultado']} | "
                     f"{_celda(e['motivo'])} | {_celda(', '.join(e['marcas']))} |")
    else:
        L.append("Ninguna.")
    L += ["", f"## Hechos ({len(hechos)})", ""]
    if hechos:
        L += ["| Id | Activo | Dominio | Afirmación | Resultado | Evidencias (id · tipo · ubicación · huella) | Marcas | Aprobación |",
              "|---|---|---|---|---|---|---|---|"]
        for e in hechos:
            marcas = e["marcas"] + ([MARCA_ALTERADA] if e["id"] in alteradas else [])
            evs = "<br>".join(f"`{x['id']}` · {x['tipo']} · {_celda(x['copia'] or x['ubicacion_original'] + ' (sin copia)')}"
                              f" · `{x['sha256_guardado'] or x['sha256_original']}`" for x in e["evidencias"])
            aprob = "firmado" if estado == "firmado" else e["estado_aprobacion"]
            L.append(f"| `{e['id']}` | {_celda(e['activo'])} | {_celda(e['dominio']['valor'])} | {_celda(e['afirmacion'])} | "
                     f"{e['resultado']} | {evs} | {_celda(', '.join(marcas))} | {aprob} |")
    else:
        L.append("Ninguno.")
    if otras:
        L += ["", f"## Entradas no consta superadas o fuera del alcance vigente ({len(otras)})", "",
              "| Id | Dominio | Marcas |", "|---|---|---|"]
        for e in otras:
            L.append(f"| `{e['id']}` | {_celda(e['dominio']['valor'])} | {_celda(', '.join(e['marcas']))} |")
    L += ["", f"## Rechazos ({len(contenido['rechazos'])})", ""]
    if contenido["rechazos"]:
        L += ["| Fecha | Evidencia (tipo · ubicación) | Activo | Dominio | Motivo | Regla | Fila del alcance |",
              "|---|---|---|---|---|---|---|"]
        for r in contenido["rechazos"]:
            L.append(f"| {r['fecha']} | {r['evidencia']['tipo']} · {_celda(r['evidencia']['ubicacion'])} | "
                     f"{_celda(r['activo'])} | {_celda(r['dominio'])} | {r['motivo']} | {_celda(r['regla'])} | "
                     f"{_celda(r['fila_alcance'])} |")
    else:
        L.append("Ninguno.")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Entrada | Campo | Anterior | Nuevo | Motivo |", "|---|---|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('entrada'))} | "
                     f"{_celda(e.get('campo'))} | {_celda(e.get('anterior'))} | {_celda(e.get('nuevo'))} | "
                     f"{_celda(e.get('motivo'))} |")
    else:
        L.append("Sin eventos.")
    if contenido["avisos"]:
        L += ["", "## Avisos", ""] + [f"- {a}" for a in contenido["avisos"]]
    L += ["", NOTA_FIRMA]
    return "\n".join(L) + "\n"


def escribir_vista(raiz) -> Path:
    ruta = _rutas(raiz)["md"]
    ruta.write_bytes(vista(raiz).encode("utf-8"))
    return ruta
