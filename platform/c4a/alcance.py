"""S01 — El alcance: propuesta, corrección, firma y consulta.

La herramienta PROPONE el alcance a partir de `scope/alcance.md` y
`scope/autorizacion.md`; el auditor lo CORRIGE y lo FIRMA (constitución,
principio I). Nada de lo que hace este módulo abre la compuerta de
autorización ni escribe en esos dos documentos de origen.

Archivos que produce, todos nuevos dentro de `scope/`:
  - alcance_s01.json        contenido canónico (lo que se firma)
  - alcance_s01.firma.json  registro de firma: firmante, fecha y huella
  - alcance_s01.md          vista legible para un tercero

Reglas de diseño (ver specs/001-alcance-auditoria/research.md):
  - La huella firmada se calcula sobre los bytes ya guardados (principio III).
  - El contenido canónico no lleva hora de generación: mismos insumos y mismas
    correcciones producen los mismos bytes (FR-018).
  - Lo que no consta no se inventa: queda «pendiente de confirmar» o «VALIDAR».
  - Ninguna dirección de red pasa del insumo al producto (FR-004).
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .util import now_iso, sha256_file, sha256_text, short_id

PRODUCTO = "S01 — El alcance"
VERSION_ESQUEMA = "1"

TIPOS = ("activo", "parte", "marco", "obligacion", "dominio", "exclusion", "regla", "compuerta")
PENDIENTE = "pendiente de confirmar"
DECISIONES = ("incluido", "excluido", PENDIENTE)
APROBACION = ("borrador", "revisado")  # «firmado» se deriva de una firma válida
VALIDAR = "VALIDAR"
CAMPOS_CORREGIBLES = ("decision", "valor", "motivo", "version")

INSUMO_ALCANCE = "scope/alcance.md"
INSUMO_AUTORIZACION = "scope/autorizacion.md"
CONSTITUCION = ".specify/memory/constitution.md"
ARCHIVO_JSON = "scope/alcance_s01.json"
ARCHIVO_FIRMA = "scope/alcance_s01.firma.json"
ARCHIVO_MD = "scope/alcance_s01.md"

REMISION_RED = "[detalle de red en scope/autorizacion.md]"
NOTA_FIRMA = "Firmar el alcance no abre la compuerta de autorización."

# Marcos de referencia de la constitución (principio IV).
MARCOS_REFERENCIA = (
    ("iso-27001", "ISO/IEC 27001", "2022"),
    ("nist-csf", "NIST CSF", "2.0"),
    ("cis-controls", "CIS Controls", "v8.1"),
)

_KNOWLEDGE = Path(__file__).resolve().parent / "knowledge"

_RE_IP = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2})?\b")
_RE_SECCION = re.compile(r"^## (\d+)\.\s+(.+?)\s*$")
_RE_PLACEHOLDER = re.compile(r"^_\(.*\)_$")
_RE_ESTADO = re.compile(r"ESTADO:\s*(NO FIRMADA|FIRMADA)", re.IGNORECASE)
_RE_PALABRAS_POLITICA = re.compile(r"(?i)pol[ií]tica|persona|proveedor|proceso|organizacional")


class AlcanceError(Exception):
    """Operación rechazada. `codigo` sigue contracts/cli-alcance.md."""

    def __init__(self, mensaje: str, codigo: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo


# --- Lectura de insumos (research D5) ------------------------------------

def _texto(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def secciones(texto: str) -> Dict[str, Dict[str, str]]:
    """Secciones `## N. Título` → {n: {titulo, texto, huella}}. La «0» es el encabezado."""
    out: Dict[str, Dict[str, Any]] = {"0": {"titulo": "encabezado", "lineas": []}}
    actual = "0"
    for linea in texto.split("\n"):
        m = _RE_SECCION.match(linea)
        if m:
            actual = m.group(1)
            out[actual] = {"titulo": m.group(2), "lineas": []}
            continue
        out[actual]["lineas"].append(linea)
    res = {}
    for n, s in out.items():
        cuerpo = "\n".join(s["lineas"]).strip("\n")
        res[n] = {"titulo": s["titulo"], "texto": cuerpo, "huella": sha256_text(cuerpo)}
    return res


def tabla(texto: str) -> List[List[str]]:
    """Filas de las tablas markdown del texto, sin la fila separadora."""
    filas = []
    for linea in texto.split("\n"):
        s = linea.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        celdas = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in celdas if c):
            continue
        filas.append(celdas)
    return filas


def campos(texto: str) -> List[Tuple[str, str]]:
    """Pares (campo, valor) de tablas `| Campo | Valor |`."""
    return [(f[0], f[1]) for f in tabla(texto) if len(f) >= 2 and f[0] != "Campo"]


def bloques(texto: str) -> List[Tuple[str, List[str]]]:
    """Listas agrupadas bajo rótulos en negrita (`**Rótulo:**`). Sin rótulo → ''."""
    out: List[Tuple[str, List[str]]] = [("", [])]
    for linea in texto.split("\n"):
        s = linea.strip()
        if s.startswith("**") and s.endswith(":**"):
            out.append((s.strip("*").rstrip(":"), []))
            continue
        m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", s)
        if m:
            out[-1][1].append(m.group(1).strip())
    return [b for b in out if b[1]]


def es_placeholder(valor: str) -> bool:
    v = (valor or "").strip()
    return v == "" or bool(_RE_PLACEHOLDER.match(v)) or "por completar" in v.lower()


def limpiar(texto: str) -> str:
    """Quita marcas de markdown y reemplaza direcciones de red (FR-004)."""
    t = _RE_IP.sub(REMISION_RED, texto or "")
    t = t.replace("**", "").replace("`", "").strip()
    t = re.sub(r"\s+", " ", t)
    return t.rstrip(".").strip()


def _slug(texto: str, largo: int = 40) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:largo].strip("-")


def _norm(texto: str) -> str:
    return _slug(texto, 400).replace("-", " ")


# --- Constructor de filas -------------------------------------------------

def _fila(tipo: str, clave: str, valor: str, decision: str, fuente: str, *,
          motivo: str = "", declarado: Optional[str] = None, huella: Optional[str] = None,
          marca: Optional[str] = None, atributos: Optional[Dict[str, Any]] = None,
          observacion: str = "") -> Dict[str, Any]:
    assert tipo in TIPOS and decision in DECISIONES
    return {
        "id": short_id("A", tipo, clave),
        "orden": 0,
        "tipo": tipo,
        "clave": clave,
        "valor": limpiar(valor),
        "decision": decision,
        "declarado": declarado,
        "motivo": limpiar(motivo),
        "fuente": fuente,
        "huella_fuente": huella,
        "estado_aprobacion": "borrador",
        "marca_legal": marca,
        "atributos": atributos or {},
        "observacion": observacion,
        "insumo_cambio": False,
    }


def es_pendiente(fila: Dict[str, Any]) -> bool:
    return fila["decision"] == PENDIENTE or fila.get("marca_legal") == VALIDAR


# --- Derivación desde scope/alcance.md -----------------------------------

def _cobertura_iso() -> Tuple[int, bool]:
    try:
        data = json.loads((_KNOWLEDGE / "controls_iso27001.json").read_text(encoding="utf-8"))
        return len([k for k in data if not k.startswith("_")]), True
    except OSError:
        return 0, False


def _en_catalogo_normativas(clave: str) -> bool:
    try:
        data = json.loads((_KNOWLEDGE / "normativas.json").read_text(encoding="utf-8"))
    except OSError:
        return False
    return clave in data


def _derivar_activo(sec: Dict[str, Dict[str, str]], aut: Optional[Dict[str, Dict[str, str]]]) -> List[Dict]:
    s4 = sec.get("4")
    fuente = f"{INSUMO_ALCANCE} §4"
    if not s4:
        return [_fila("activo", "activo", "", PENDIENTE, "sin fuente",
                      observacion="El alcance no declara activos.")]
    hosts: List[str] = []
    rotulo_lab = ""
    hay_red = False
    for rotulo, items in bloques(s4["texto"]):
        if not rotulo.lower().startswith("activos"):
            continue
        rotulo_lab = rotulo
        for it in items:
            if re.search(r"(?i)\bhost\b", it):
                m = re.search(r"\(([^)]+)\)", it)
                hosts.append(m.group(1).strip() if m else "")
            elif _RE_IP.search(it) or re.search(r"(?i)segmento|rango", it):
                hay_red = True
    filas = []
    if len(hosts) == 1 and hosts[0]:
        lab = re.search(r"\(([^)]*laboratorio[^)]*)\)", rotulo_lab)
        rol = "objetivo del " + (lab.group(1).split(",")[-1].strip() if lab else "ejercicio")
        valor = f"{hosts[0]} (tipo: host; rol: {rol})"
        obs = ""
        decision = "incluido"
        if aut and "2" in aut:
            hosts_aut = [v for c, v in campos(aut["2"]["texto"]) if c.lower().startswith("host")]
            nombres = [m.group(1).strip() for v in hosts_aut for m in [re.search(r"\(([^)]+)\)", v)] if m]
            if nombres and nombres != [hosts[0]]:
                decision = PENDIENTE
                obs = "El activo de la autorización no coincide con el del alcance."
        filas.append(_fila("activo", "activo", valor, decision, fuente, huella=s4["huella"],
                           observacion=obs))
    else:
        filas.append(_fila(
            "activo", "activo", "", PENDIENTE, fuente, huella=s4["huella"],
            declarado=f"{len(hosts)} activos",
            observacion="El ejercicio admite un solo activo; los insumos declaran "
                        f"{len(hosts)}."))
    if hay_red:
        filas.append(_fila(
            "regla", "detalle-red",
            "El rango y el host objetivo constan en scope/autorizacion.md §2; no se copian aquí",
            "incluido", fuente, huella=s4["huella"]))
    return filas


def _derivar_marcos_y_obligaciones(sec: Dict[str, Dict[str, str]]) -> List[Dict]:
    s3 = sec.get("3")
    filas: List[Dict] = []
    declarados: Dict[str, Tuple[str, Optional[str], str]] = {}
    leyes: List[Tuple[str, str, str, str]] = []
    encabezado_estado = "Estado"
    if s3:
        t = tabla(s3["texto"])
        if t:
            encabezado_estado = t[0][-1] if len(t[0]) >= 3 else encabezado_estado
        for celdas in t[1:]:
            if len(celdas) < 2:
                continue
            nombre = limpiar(celdas[0])
            cubre = limpiar(celdas[1])
            estado = limpiar(celdas[2]) if len(celdas) > 2 else ""
            if nombre.lower().startswith("ley"):
                leyes.append((nombre, cubre, estado, s3["huella"]))
                continue
            for clave, base, _ref in MARCOS_REFERENCIA:
                if nombre.lower().startswith(base.lower()):
                    m = re.match(re.escape(base) + r"\s*[: ]\s*(\S+)", nombre, re.IGNORECASE)
                    declarados[clave] = (nombre, m.group(1) if m else None, cubre)
    for clave, base, ref in MARCOS_REFERENCIA:
        if clave == "iso-27001":
            n, ok = _cobertura_iso()
            estado_h = "implementado parcialmente" if ok and n else "mencionado"
            total = None
            if clave in declarados:
                m = re.search(r"(\d+)\s+controles", declarados[clave][2])
                total = m.group(1) if m else None
            cobertura = (f"{n} de {total} controles del Anexo A en el catálogo de la herramienta"
                         if total else f"{n} controles del Anexo A en el catálogo; total no declarado")
        elif clave == "nist-csf":
            estado_h = "mencionado"
            cobertura = ("el catálogo trae las seis funciones, sin categorías ni subcategorías"
                         if _en_catalogo_normativas("NIST-CSF") else "sin catálogo en la herramienta")
        else:
            estado_h = "mencionado"
            cobertura = "sin catálogo en la herramienta"
        if clave in declarados:
            nombre, version, _cubre = declarados[clave]
            atributos = {"version": version or PENDIENTE, "version_referencia": ref,
                         "estado_herramienta": estado_h, "cobertura": cobertura}
            obs = ""
            decision = "incluido"
            if not version:
                decision = PENDIENTE
                obs = "El alcance cita el marco sin versión; no se completa con la de referencia."
            elif version.lstrip("v") != ref.lstrip("v"):
                obs = f"Versión declarada {version} distinta de la de referencia {ref}: decide el auditor."
            filas.append(_fila("marco", clave, nombre, decision, f"{INSUMO_ALCANCE} §3",
                               huella=s3["huella"] if s3 else None, atributos=atributos,
                               observacion=obs))
        else:
            filas.append(_fila(
                "marco", clave, f"{base} {ref}", PENDIENTE, f"{CONSTITUCION} §IV",
                atributos={"version": ref, "version_referencia": ref,
                           "estado_herramienta": estado_h, "cobertura": cobertura},
                observacion="Marco de referencia de la constitución; no está declarado en el alcance."))
    s9 = sec.get("9", {}).get("texto", "")
    for nombre, cubre, estado, huella in leyes:
        m = re.search(r"\d{2}\.\d{3}", nombre)
        clave = "ley-" + (m.group(0) if m else _slug(nombre))
        no_audita = re.match(r"(?i)no se audita[:.]?\s*(.*)", cubre)
        fundamento = None
        if "21.663" in nombre:
            obs_ap = ("La aplicabilidad depende de la clasificación OIV / servicio esencial, que no "
                      "consta (scope/alcance.md §9).") if re.search(r"OIV", s9) else ""
        else:
            obs_ap = ""
        atributos = {"fuente_oficial": None, "fecha_consulta": None, "articulo": None,
                     "fundamento": fundamento,
                     "antecedente": f"{estado} (anotado en {INSUMO_ALCANCE} §3, columna «{limpiar(encabezado_estado)}»)"
                     if estado else None}
        faltan = [k for k in ("fuente_oficial", "fecha_consulta", "articulo", "fundamento") if not atributos[k]]
        obs = "Obligación candidata. Falta: " + ", ".join(
            nombre for k, nombre in _ATRIBUTOS_LEGALES if k in faltan) + "."
        if obs_ap:
            obs += " " + obs_ap
        if no_audita:
            filas.append(_fila("obligacion", clave, f"{nombre}: {cubre}", "excluido",
                               f"{INSUMO_ALCANCE} §3", motivo=cubre, huella=huella,
                               marca=VALIDAR if faltan else None, atributos=atributos,
                               observacion=obs))
        else:
            filas.append(_fila("obligacion", clave, f"{nombre}: {cubre}", "incluido",
                               f"{INSUMO_ALCANCE} §3", huella=huella,
                               marca=VALIDAR if faltan else None, atributos=atributos,
                               observacion=obs))
    return filas


def _derivar_dominios(sec: Dict[str, Dict[str, str]]) -> List[Dict]:
    filas: List[Dict] = []
    s4 = sec.get("4")
    if s4:
        for rotulo, items in bloques(s4["texto"]):
            r = rotulo.lower()
            if r.startswith("dominios t"):
                pref = "tecnico"
            elif r.startswith("dominios de control"):
                pref = "control"
            else:
                continue
            for i, it in enumerate(items, 1):
                obs = ""
                if pref == "control" and _RE_PALABRAS_POLITICA.search(it):
                    obs = "Requiere políticas, personas o procesos: no se acredita con una prueba técnica."
                filas.append(_fila(
                    "dominio", f"{pref}:{i}:{_slug(it)}", it, PENDIENTE, f"{INSUMO_ALCANCE} §4",
                    declarado="incluido", huella=s4["huella"],
                    observacion=(obs + " " if obs else "") + "Declarado incluido, sin motivo en el ítem."))
    else:
        filas.append(_fila("dominio", "dominios", "", PENDIENTE, "sin fuente",
                           observacion="El alcance no declara dominios."))
    s5 = sec.get("5")
    if s5:
        for i, (_r, items) in enumerate(bloques(s5["texto"])):
            for j, it in enumerate(items, 1):
                filas.append(_fila(
                    "exclusion", f"alcance:{j}:{_slug(it)}", it, PENDIENTE, f"{INSUMO_ALCANCE} §5",
                    declarado="excluido", huella=s5["huella"],
                    observacion="Declarado fuera de alcance, sin motivo en el ítem."))
    else:
        filas.append(_fila("exclusion", "exclusiones", "", PENDIENTE, "sin fuente",
                           observacion="El alcance no declara exclusiones."))
    s6 = sec.get("6")
    if s6:
        for _r, items in bloques(s6["texto"]):
            for j, it in enumerate(items, 1):
                if re.search(r"(?i)cifrad", it):
                    filas.append(_fila(
                        "regla", f"rde:{j}", it, PENDIENTE, f"{INSUMO_ALCANCE} §6",
                        declarado="incluido", huella=s6["huella"],
                        observacion="Requisito declarado que el sistema no garantiza hoy: "
                                    "tener huellas de integridad no equivale a cifrado."))
                else:
                    filas.append(_fila("regla", f"rde:{j}", it, "incluido", f"{INSUMO_ALCANCE} §6",
                                       huella=s6["huella"]))
    return filas


# --- Derivación desde scope/autorizacion.md ------------------------------

_FORMATOS_FECHA = ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d", "%d-%m-%Y %H:%M",
                   "%d-%m-%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y")


def _leer_fecha(valor: str) -> Tuple[str, Optional[str]]:
    """→ ('informada', iso) | ('no informada', None) | ('ilegible', None)."""
    if es_placeholder(valor):
        return "no informada", None
    v = limpiar(valor)
    for fmt in _FORMATOS_FECHA:
        try:
            return "informada", datetime.strptime(v, fmt).isoformat()
        except ValueError:
            continue
    return "ilegible", None


def _derivar_autorizacion(aut: Optional[Dict[str, Dict[str, str]]]) -> List[Dict]:
    if aut is None:
        obs = "Falta el insumo scope/autorizacion.md."
        return [
            _fila("parte", "organizacion", "", PENDIENTE, "sin fuente", observacion=obs),
            _fila("exclusion", "activos-no-listados", "", PENDIENTE, "sin fuente", observacion=obs),
            _fila("compuerta", "firma", "no firmada", PENDIENTE, "sin fuente", observacion=obs),
            _fila("compuerta", "completitud", "incompleta", PENDIENTE, "sin fuente", observacion=obs),
            _fila("compuerta", "ventana", "no informada", PENDIENTE, "sin fuente", observacion=obs),
        ]
    filas: List[Dict] = []
    todos: List[Tuple[str, str, str]] = []
    for n, s in aut.items():
        for c, v in campos(s["texto"]):
            todos.append((n, c, v))

    def buscar(prefijo: str) -> Tuple[Optional[str], Optional[str]]:
        for n, c, v in todos:
            if c.lower().startswith(prefijo.lower()):
                return n, v
        return None, None

    n, org = buscar("Organización")
    if org is not None and not es_placeholder(org):
        filas.append(_fila("parte", "organizacion", org, "incluido", f"{INSUMO_AUTORIZACION} §{n}",
                           huella=aut[n]["huella"],
                           observacion="Consta en la autorización; la firma del representante es aparte."))
    else:
        filas.append(_fila("parte", "organizacion", "", PENDIENTE,
                           f"{INSUMO_AUTORIZACION} §{n}" if n else "sin fuente",
                           observacion="Organización auditada por completar."))

    n, excl = buscar("Exclusiones")
    if excl is not None and not es_placeholder(excl):
        filas.append(_fila("exclusion", "activos-no-listados", excl, PENDIENTE,
                           f"{INSUMO_AUTORIZACION} §{n}", declarado="excluido", huella=aut[n]["huella"],
                           observacion="Declarado fuera de alcance, sin motivo en el ítem."))
    else:
        filas.append(_fila("exclusion", "activos-no-listados", "", PENDIENTE,
                           f"{INSUMO_AUTORIZACION} §{n}" if n else "sin fuente",
                           observacion="Exclusiones de activos por completar."))

    encabezado = aut.get("0", {}).get("texto", "")
    m = _RE_ESTADO.search(encabezado)
    estado_decl = m.group(1).upper() if m else None
    sec_firma = next((k for k, s in aut.items() if s["titulo"].lower().startswith("firma")), None)
    firma_campos = campos(aut[sec_firma]["texto"]) if sec_firma else []
    firma_completa = bool(firma_campos) and not any(es_placeholder(v) for _c, v in firma_campos)
    firmada = estado_decl == "FIRMADA" and firma_completa
    filas.append(_fila(
        "compuerta", "firma", "firmada" if firmada else "no firmada",
        "incluido" if firmada else PENDIENTE, f"{INSUMO_AUTORIZACION} encabezado y §{sec_firma or '?'}",
        huella=sha256_text(encabezado + (aut[sec_firma]["texto"] if sec_firma else "")),
        atributos={"estado_declarado": estado_decl, "firma_completa": firma_completa}))

    faltantes = [c for _n, c, v in todos if es_placeholder(v)]
    filas.append(_fila(
        "compuerta", "completitud", "completa" if not faltantes else "incompleta",
        "incluido" if not faltantes else PENDIENTE, f"{INSUMO_AUTORIZACION} §1–§6",
        huella=sha256_text("\n".join(f"{c}={v}" for _n, c, v in todos)),
        atributos={"campos_faltantes": faltantes}))

    n_ini, v_ini = buscar("Inicio")
    _n_fin, v_fin = buscar("Fin")
    l_ini, iso_ini = _leer_fecha(v_ini or "")
    l_fin, iso_fin = _leer_fecha(v_fin or "")
    informada = l_ini == "informada" and l_fin == "informada"
    lectura = "informada" if informada else ("ilegible" if "ilegible" in (l_ini, l_fin) else "no informada")
    filas.append(_fila(
        "compuerta", "ventana", f"{iso_ini} a {iso_fin}" if informada else "no informada",
        "incluido" if informada else PENDIENTE,
        f"{INSUMO_AUTORIZACION} §{n_ini}" if n_ini else "sin fuente",
        huella=aut[n_ini]["huella"] if n_ini else None,
        atributos={"inicio": iso_ini, "fin": iso_fin, "lectura": lectura},
        observacion="Fecha ilegible: se trata como no informada." if lectura == "ilegible" else ""))
    return filas


# --- Proponer ------------------------------------------------------------

def _rutas(raiz) -> Dict[str, Path]:
    r = Path(raiz)
    return {"raiz": r, "json": r / ARCHIVO_JSON, "firma": r / ARCHIVO_FIRMA, "md": r / ARCHIVO_MD,
            "alcance": r / INSUMO_ALCANCE, "autorizacion": r / INSUMO_AUTORIZACION}


def derivar(raiz) -> Tuple[List[Dict], List[Dict], List[str]]:
    """Filas del borrador a partir de los insumos. → (insumos, filas, avisos)."""
    p = _rutas(raiz)
    t_alc = _texto(p["alcance"])
    t_aut = _texto(p["autorizacion"])
    avisos = []
    insumos = []
    for rel, ruta, t in ((INSUMO_ALCANCE, p["alcance"], t_alc), (INSUMO_AUTORIZACION, p["autorizacion"], t_aut)):
        insumos.append({"archivo": rel, "existe": t is not None,
                        "sha256": sha256_file(ruta) if t is not None else None})
        if t is None:
            avisos.append(f"Falta el insumo {rel}: sus filas quedan «{PENDIENTE}».")
    sec = secciones(t_alc) if t_alc is not None else {}
    aut = secciones(t_aut) if t_aut is not None else None
    filas: List[Dict] = []
    filas += _derivar_activo(sec, aut)
    filas += _derivar_autorizacion(aut)
    filas += _derivar_marcos_y_obligaciones(sec)
    filas += _derivar_dominios(sec)
    orden_tipo = {t: i for i, t in enumerate(TIPOS)}
    filas = sorted(enumerate(filas), key=lambda x: (orden_tipo[x[1]["tipo"]], x[0]))
    filas = [f for _i, f in filas]
    vistos = set()
    for i, f in enumerate(filas, 1):
        f["orden"] = i
        if f["id"] in vistos:
            raise AlcanceError(f"id de fila duplicado: {f['id']} ({f['clave']})")
        vistos.add(f["id"])
    return insumos, filas, avisos


def serializar(contenido: Dict[str, Any]) -> bytes:
    """Serialización determinista del contenido canónico (FR-018)."""
    return (json.dumps(contenido, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def cargar(raiz) -> Dict[str, Any]:
    ruta = _rutas(raiz)["json"]
    if not ruta.exists():
        raise AlcanceError(f"no existe {ARCHIVO_JSON}: ejecute primero «alcance proponer»", 2)
    return json.loads(ruta.read_bytes().decode("utf-8"))


def _aplicar(filas_por_id: Dict[str, Dict], ev: Dict[str, Any]) -> bool:
    f = filas_por_id.get(ev.get("fila"))
    if f is None:
        return False
    campo, nuevo = ev["campo"], ev["nuevo"]
    if campo == "version":
        f["atributos"]["version"] = nuevo
    elif campo == "decision":
        f["decision"] = nuevo
        f["motivo"] = ev["motivo"]
    else:
        f[campo] = nuevo
    f["estado_aprobacion"] = "revisado"
    return True


def _componer(insumos, filas, historial, estado, avisos) -> Dict[str, Any]:
    return {"producto": PRODUCTO, "version_esquema": VERSION_ESQUEMA, "insumos": insumos,
            "filas": filas, "estado_aprobacion": estado, "historial": historial, "avisos": avisos}


def proponer(raiz, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
    """Genera o regenera el borrador; conserva las correcciones del auditor (FR-013)."""
    p = _rutas(raiz)
    insumos, filas, avisos = derivar(raiz)
    historial: List[Dict] = []
    estado = "borrador"
    previo = None
    if p["json"].exists():
        previo = cargar(raiz)
        historial = previo["historial"]
        estado = previo["estado_aprobacion"]
        por_id = {f["id"]: f for f in filas}
        for ev in historial:
            if ev["tipo"] != "correccion":
                continue
            if not _aplicar(por_id, ev):
                avisos.append(f"La corrección sobre {ev['fila']} ya no tiene fila: revisar.")
                continue
            f = por_id[ev["fila"]]
            if ev.get("huella_fuente") != f["huella_fuente"]:
                f["insumo_cambio"] = True
                avisos.append(f"El insumo de la fila {f['id']} cambió después de corregirla: "
                              "se conserva la corrección; revisar.")
    contenido = _componer(insumos, filas, historial, estado, sorted(set(avisos), key=avisos.index))
    nuevos = serializar(contenido)
    if previo is not None and estado_efectivo(raiz) == "firmado" and nuevos != p["json"].read_bytes():
        cambiados = [a["archivo"] for a, b in zip(insumos, previo["insumos"]) if a["sha256"] != b["sha256"]]
        raise AlcanceError(
            "El alcance está firmado y se basó en otra versión de los insumos "
            f"({', '.join(cambiados) or 'insumos'}). No se actualiza solo: corrija o vuelva a "
            "firmar a partir de una revisión explícita.", 4)
    p["json"].parent.mkdir(parents=True, exist_ok=True)
    p["json"].write_bytes(nuevos)
    escribir_vista(raiz, fecha_referencia)
    return contenido


# --- Corregir, revisar, firmar, verificar --------------------------------

def _guardar(raiz, contenido, fecha_referencia=None) -> None:
    _rutas(raiz)["json"].write_bytes(serializar(contenido))
    escribir_vista(raiz, fecha_referencia)


def _anular_firma(raiz, contenido, autor, fecha) -> None:
    ruta = _rutas(raiz)["firma"]
    if ruta.exists():
        ruta.unlink()
        contenido["historial"].append({"tipo": "firma_anulada", "autor": autor, "fecha": fecha,
                                       "fila": None,
                                       "motivo": "Cambio posterior a la firma: se exige una nueva firma."})


def _exigir(valor: str, nombre: str) -> str:
    v = (valor or "").strip()
    if not v:
        raise AlcanceError(f"falta {nombre}: es obligatorio")
    return v


def corregir(raiz, fila: str, campo: str, valor: str, motivo: str, autor: str,
             fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = limpiar(_exigir(motivo, "el motivo"))
    autor = limpiar(_exigir(autor, "el autor"))
    if campo not in CAMPOS_CORREGIBLES:
        raise AlcanceError(f"campo no corregible: {campo} (use {', '.join(CAMPOS_CORREGIBLES)})")
    if campo == "decision" and valor not in DECISIONES:
        raise AlcanceError(f"decisión no válida: {valor} (use {', '.join(DECISIONES)})")
    contenido = cargar(raiz)
    por_id = {f["id"]: f for f in contenido["filas"]}
    if fila not in por_id:
        raise AlcanceError(f"no existe la fila {fila}")
    f = por_id[fila]
    anterior = f["atributos"].get("version", "") if campo == "version" else f[campo]
    fecha = fecha or now_iso()
    ev = {"tipo": "correccion", "autor": autor, "fecha": fecha, "fila": fila, "campo": campo,
          "anterior": "" if anterior is None else str(anterior), "nuevo": limpiar(valor),
          "motivo": motivo, "huella_fuente": f["huella_fuente"]}
    _aplicar(por_id, ev)
    contenido["historial"].append(ev)
    contenido["estado_aprobacion"] = "revisado"
    _anular_firma(raiz, contenido, autor, fecha)
    _guardar(raiz, contenido)
    return f


def revisar(raiz, autor: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    motivo = limpiar(_exigir(motivo, "el motivo"))
    autor = limpiar(_exigir(autor, "el autor"))
    contenido = cargar(raiz)
    fecha = fecha or now_iso()
    contenido["historial"].append({"tipo": "revision", "autor": autor, "fecha": fecha,
                                   "fila": None, "motivo": motivo})
    contenido["estado_aprobacion"] = "revisado"
    _anular_firma(raiz, contenido, autor, fecha)
    _guardar(raiz, contenido)
    return contenido


def firmar(raiz, firmante: str, motivo: str, fecha: Optional[str] = None) -> Dict[str, Any]:
    """Única vía a «firmado» (FR-012). Registra quién, cuándo y con qué justificación
    (principio I). La huella es de los bytes ya guardados (principio III)."""
    firmante = limpiar(_exigir(firmante, "el nombre del firmante"))
    motivo = limpiar(_exigir(motivo, "la justificación de la firma"))
    contenido = cargar(raiz)
    if contenido["estado_aprobacion"] != "revisado":
        raise AlcanceError("solo se firma un alcance «revisado»: registre una corrección o una revisión")
    p = _rutas(raiz)
    registro = {
        "archivo": Path(ARCHIVO_JSON).name,
        "sha256": sha256_file(p["json"]),
        "firmante": firmante,
        "fecha": fecha or now_iso(),
        "motivo": motivo,
        "pendientes_al_firmar": sum(1 for f in contenido["filas"] if es_pendiente(f)),
        "nota": NOTA_FIRMA,
    }
    p["firma"].write_bytes(serializar(registro))
    escribir_vista(raiz)
    return registro


def verificar(raiz) -> Dict[str, Any]:
    """Recalcula la huella del archivo guardado sin regenerarlo y la compara con la firma."""
    p = _rutas(raiz)
    if not p["json"].exists():
        raise AlcanceError(f"no existe {ARCHIVO_JSON}", 2)
    actual = sha256_file(p["json"])
    if not p["firma"].exists():
        return {"estado": "sin firma", "sha256_actual": actual, "sha256_firmado": None}
    reg = json.loads(p["firma"].read_bytes().decode("utf-8"))
    if reg.get("sha256") == actual:
        return {"estado": "firmado", "sha256_actual": actual, "sha256_firmado": reg["sha256"],
                "firmante": reg.get("firmante"), "fecha": reg.get("fecha"), "motivo": reg.get("motivo")}
    return {"estado": "revisado (firma no aplica)", "sha256_actual": actual,
            "sha256_firmado": reg.get("sha256")}


def estado_efectivo(raiz) -> str:
    v = verificar(raiz)
    if v["estado"] == "firmado":
        return "firmado"
    if v["estado"].startswith("revisado"):
        return "revisado"
    return cargar(raiz)["estado_aprobacion"]


# --- Compuerta (solo lectura, research D4) -------------------------------

def evaluar_compuerta(raiz, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
    """Firma, completitud y ventana de scope/autorizacion.md. Nunca la abre ni la modifica."""
    ref = fecha_referencia or date.today()
    t = _texto(_rutas(raiz)["autorizacion"])
    filas = {f["clave"]: f for f in _derivar_autorizacion(secciones(t) if t is not None else None)
             if f["tipo"] == "compuerta"}
    firma = filas["firma"]["valor"]
    faltan = filas["completitud"]["atributos"].get("campos_faltantes", [])
    completitud = filas["completitud"]["valor"]
    at = filas["ventana"]["atributos"]
    motivos = []
    if t is None:
        motivos.append("falta scope/autorizacion.md")
    if firma != "firmada":
        motivos.append("no firmada")
    if completitud != "completa":
        motivos.append("incompleta: " + ", ".join(faltan) if faltan else "incompleta")
    if not at.get("inicio") or not at.get("fin"):
        ventana = "no informada"
        motivos.append("ventana no informada" + (" (fecha ilegible)" if at.get("lectura") == "ilegible" else ""))
    else:
        ini = datetime.fromisoformat(at["inicio"]).date()
        fin = datetime.fromisoformat(at["fin"]).date()
        if ref > fin:
            ventana = "vencida"
            motivos.append("ventana vencida")
        elif ref < ini:
            ventana = "no vigente (aún no comienza)"
            motivos.append("ventana aún no comienza")
        else:
            ventana = "vigente"
    return {"firma": firma, "completitud": completitud, "ventana": ventana,
            "resultado": "abierta" if not motivos else "cerrada", "motivos": motivos,
            "fecha_referencia": ref.isoformat(), "nota": NOTA_FIRMA}


# --- Consulta para S02 (FR-016) ------------------------------------------

def consultar(raiz, tipo: str, valor: str) -> Dict[str, Any]:
    contenido = cargar(raiz)
    firmado = estado_efectivo(raiz) == "firmado"
    q = _norm(valor)
    for f in contenido["filas"]:
        if f["tipo"] != tipo or not q:
            continue
        v = _norm(f["valor"])
        if tipo == "activo":
            coincide = bool(v) and _norm(f["valor"].split(" (")[0]) == q
        else:
            coincide = q in v or q == _norm(f["clave"])
        if coincide:
            if es_pendiente(f):
                resp = "pendiente"
            elif f["decision"] == "excluido":
                resp = "fuera"
            else:
                resp = "dentro"
            return {"respuesta": resp, "fila": {"id": f["id"], "fuente": f["fuente"]},
                    "motivo": f["motivo"] or f["observacion"], "firmado": firmado}
    return {"respuesta": "fuera", "fila": None,
            "motivo": "No figura en el alcance: lo no listado queda fuera.", "firmado": firmado}


def evidencia_admisible(raiz, activo: str) -> bool:
    """¿Un hecho sobre este activo puede ser evidencia de esta auditoría? Solo si está «dentro»."""
    return consultar(raiz, "activo", activo)["respuesta"] == "dentro"


# --- Vista legible (FR-017, FR-019) --------------------------------------

_TITULOS = {"activo": "Activo", "parte": "Organización auditada", "marco": "Marcos de referencia",
            "obligacion": "Obligaciones candidatas", "dominio": "Dominios",
            "exclusion": "Exclusiones", "regla": "Reglas de enganche", "compuerta": "Compuerta de autorización (declarado)"}


def _celda(t: Any) -> str:
    return str(t if t not in (None, "") else "—").replace("|", "\\|")


_ATRIBUTOS_LEGALES = (("fuente_oficial", "fuente oficial"), ("fecha_consulta", "fecha de consulta"),
                      ("articulo", "artículo"), ("fundamento", "fundamento de aplicabilidad"))


def _que_falta(f: Dict[str, Any]) -> str:
    partes = []
    if f["decision"] == PENDIENTE:
        partes.append(f"decisión ({'declarado: ' + f['declarado'] if f['declarado'] else 'no consta'})")
    if f.get("marca_legal") == VALIDAR:
        partes.append("VALIDAR: " + ", ".join(nombre for k, nombre in _ATRIBUTOS_LEGALES
                                               if not f["atributos"].get(k)))
    return "; ".join(partes)


def vista(raiz, fecha_referencia: Optional[date] = None) -> str:
    contenido = cargar(raiz)
    p = _rutas(raiz)
    ver = verificar(raiz)
    estado = estado_efectivo(raiz)
    comp = evaluar_compuerta(raiz, fecha_referencia)
    pend = [f for f in contenido["filas"] if es_pendiente(f)]
    L = [f"# El alcance (S01) — {estado}", "",
         "> Producto de la herramienta C4A. La herramienta propone; el auditor corrige y firma.",
         "> Este alcance delimita qué se audita y qué no: no contiene conclusiones sobre controles.",
         "",
         f"- **Estado de aprobación**: {estado}",
         f"- **Huella SHA-256 de `{ARCHIVO_JSON}`**: `{ver['sha256_actual']}`"]
    if ver["estado"] == "firmado":
        L.append(f"- **Firma**: {ver['firmante']}, {ver['fecha']} (verificada contra los bytes guardados). "
                 f"Justificación: {ver.get('motivo') or '—'}")
    elif ver["sha256_firmado"]:
        L.append("- **Firma**: no aplica: la huella firmada no coincide con el archivo guardado")
    else:
        L.append("- **Firma**: sin firma")
    L += ["", "## Insumos", "", "| Archivo | Existe | SHA-256 |", "|---|---|---|"]
    for i in contenido["insumos"]:
        L.append(f"| `{i['archivo']}` | {'sí' if i['existe'] else 'no'} | {_celda(i['sha256'])} |")
    L += ["", f"## Compuerta de autorización (fecha de referencia {comp['fecha_referencia']})", "",
          "| Firma | Completitud | Ventana | Resultado |", "|---|---|---|---|",
          f"| {comp['firma']} | {comp['completitud']} | {comp['ventana']} | **{comp['resultado']}** |", ""]
    if comp["motivos"]:
        L.append("Motivos: " + "; ".join(comp["motivos"]) + ".")
        L.append("")
    L += [f"{NOTA_FIRMA} La herramienta solo lee `scope/autorizacion.md`.", "",
          f"## Pendientes ({len(pend)})", ""]
    if pend:
        L += ["| Id | Tipo | Valor | Qué falta | Fuente |", "|---|---|---|---|---|"]
        for f in pend:
            L.append(f"| `{f['id']}` | {f['tipo']} | {_celda(f['valor'])} | {_celda(_que_falta(f))} | {_celda(f['fuente'])} |")
    else:
        L.append("Sin pendientes.")
    for t in TIPOS:
        filas = [f for f in contenido["filas"] if f["tipo"] == t]
        if not filas:
            continue
        L += ["", f"## {_TITULOS[t]}", "",
              "| Id | Valor | Decisión | Motivo | Fuente | Aprobación | Observación |",
              "|---|---|---|---|---|---|---|"]
        for f in filas:
            extra = ""
            if t == "marco":
                a = f["atributos"]
                extra = f"Versión {a.get('version')}; {a.get('estado_herramienta')}; {a.get('cobertura')}. "
            if f["insumo_cambio"]:
                extra += "El insumo cambió después de la corrección. "
            aprob = "firmado" if estado == "firmado" else f["estado_aprobacion"]
            L.append(f"| `{f['id']}` | {_celda(f['valor'])} | {f['decision']} | {_celda(f['motivo'])} | "
                     f"{_celda(f['fuente'])} | {aprob} | {_celda((extra + f['observacion']).strip())} |")
    L += ["", f"## Historial ({len(contenido['historial'])})", ""]
    if contenido["historial"]:
        L += ["| Fecha | Tipo | Autor | Fila | Campo | Anterior | Nuevo | Motivo |", "|---|---|---|---|---|---|---|---|"]
        for e in contenido["historial"]:
            L.append(f"| {e['fecha']} | {e['tipo']} | {_celda(e['autor'])} | {_celda(e.get('fila'))} | "
                     f"{_celda(e.get('campo'))} | {_celda(e.get('anterior'))} | {_celda(e.get('nuevo'))} | {_celda(e['motivo'])} |")
    else:
        L.append("Sin correcciones.")
    if contenido["avisos"]:
        L += ["", "## Avisos", ""] + [f"- {a}" for a in contenido["avisos"]]
    return "\n".join(L) + "\n"


def escribir_vista(raiz, fecha_referencia: Optional[date] = None) -> Path:
    ruta = _rutas(raiz)["md"]
    ruta.write_bytes(vista(raiz, fecha_referencia).encode("utf-8"))
    return ruta
