#!/usr/bin/env python3
"""Analisis estatico offline de un APK extraido (solo lectura, sin librerias de terceros).

Dos familias:
1. Firma del APK (esquemas v2/v3 del APK Signing Block): localiza el bloque,
   recalcula los digests de las tres secciones del ZIP y los compara con los
   embebidos; verifica la firma digital del signedData con la clave publica
   del firmante; describe los certificados (emisior, sujeto, vigencia, huella).
2. Manifiesto binario (AXML): parsea el arbol XML y extrae paquete, versiones,
   uses-permission, uses-feature, atributos de <application> y componentes
   (activity/activity-alias/service/receiver/provider) con exported efectivo.

Uso: python analisis_apk_propio.py <apk> <salida.json>
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"
VER_ID_V2 = 0x7109871A
VER_ID_V3 = 0xF05368C0
VER_ID_V31 = 0x1B93AD61

ALGOS = {
    0x0101: ("RSASSA-PSS", "SHA-256"),
    0x0102: ("RSASSA-PSS", "SHA-512"),
    0x0103: ("RSASSA-PKCS1-v1_5", "SHA-256"),
    0x0104: ("RSASSA-PKCS1-v1_5", "SHA-512"),
    0x0105: ("ECDSA", "SHA-256"),
    0x0106: ("ECDSA", "SHA-512"),
    0x0107: ("HMAC", "SHA-256"),
    0x0108: ("HMAC", "SHA-512"),
}
DIGEST_ALGOS = {
    0x0101: "sha256", 0x0102: "sha512", 0x0103: "sha256", 0x0104: "sha512",
    0x0105: "sha256", 0x0106: "sha512", 0x0107: "sha256", 0x0108: "sha512",
    0x0109: "sha256", 0x010A: "sha256", 0x010B: "sha256",
}

ANDROID_ATTRS = {
    0x01010001: "label", 0x01010002: "icon", 0x01010003: "name",
    0x01010006: "permission", 0x01010009: "protectionLevel",
    0x0101000E: "enabled", 0x0101000F: "debuggable", 0x01010010: "exported",
    0x01010011: "process", 0x01010018: "authorities",
    0x0101001B: "grantUriPermissions", 0x0101001C: "readPermission",
    0x0101001D: "writePermission",
    0x0101020C: "minSdkVersion", 0x0101021B: "versionCode",
    0x0101021C: "versionName", 0x01010270: "targetSdkVersion",
    0x01010280: "allowBackup", 0x0101035A: "largeHeap",
    0x0101046C: "appComponentFactory", 0x010104EA: "extractNativeLibs",
    0x010104EC: "usesCleartextTraffic", 0x01010527: "networkSecurityConfig",
    0x01010572: "compileSdkVersion", 0x01010573: "compileSdkVersionCodename",
}


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def read_lp(data, off):
    """Lee un campo length-prefixed: u32 len + bytes. Devuelve (bytes, nuevo_off)."""
    n = u32(data, off)
    return data[off + 4: off + 4 + n], off + 4 + n


def read_seq(data, off):
    """Lee una secuencia: u32 len total + elementos lp. Devuelve lista de bytes."""
    total = u32(data, off)
    end = off + 4 + total
    items = []
    p = off + 4
    while p < end:
        item, p = read_lp(data, p)
        items.append(item)
    return items


# --------------------------------------------------------------------------
# 1. APK Signing Block (v2/v3)
# --------------------------------------------------------------------------

def find_sig_block(apk: bytes):
    # End of Central Directory al final del fichero
    eocd = apk.rfind(b"PK\x05\x06")
    if eocd < 0:
        return None, "EOCD no encontrado"
    cd_offset = u32(apk, eocd + 16)
    if cd_offset == 0xFFFFFFFF:
        return None, "ZIP64 no soportado para localizar el bloque de firma"
    magic_pos = apk.rfind(APK_SIG_BLOCK_MAGIC, 0, cd_offset)
    if magic_pos < 0:
        return None, "bloque de firma no presente (APK solo v1 o sin firmar)"
    size2 = u64(apk, magic_pos - 8)
    block_start = magic_pos + 8 - size2  # size2 = pares + 24; el campo size1 inicia 16+pairs bytes antes del magic
    size1 = u64(apk, block_start)
    if size1 != size2 or apk[magic_pos: magic_pos + 16] != APK_SIG_BLOCK_MAGIC:
        return None, "magic del bloque de firma inconsistente"
    pairs_start = block_start + 8
    pairs_end = magic_pos - 8
    pairs = {}
    p = pairs_start
    while p < pairs_end:
        pid = u32(apk, p)
        (val,), _ = struct.unpack_from("<I", apk, p + 4), None
        n = u32(apk, p + 4)
        pairs[pid] = apk[p + 8: p + 8 + n]
        p += 8 + n
    return {"block_start": block_start, "block_size": size1 + 8,
            "cd_offset": cd_offset, "pairs": pairs}, None


def section_digests(apk: bytes, block_start: int, block_size: int, cd_offset: int, algo: str):
    """Calcula los digests de las 3 secciones. Prueba variantes de exclusion."""
    h = lambda: hashlib.new(algo)
    bs, be = block_start, block_start + block_size
    variantes = {
        "excluye_bloque_completo": [(0, bs), (be, cd_offset), (cd_offset, len(apk))],
        "incluye_size_inicial": [(0, bs + 8), (be, cd_offset), (cd_offset, len(apk))],
        "incluye_magic_en_s2": [(0, bs), (be - 16, cd_offset), (cd_offset, len(apk))],
        "incluye_size2_y_magic_en_s2": [(0, bs), (be - 8 - 16, cd_offset), (cd_offset, len(apk))],
        "excluye_size_inicial_y_s2_post_magic": [(0, bs + 8), (be - 16, cd_offset), (cd_offset, len(apk))],
    }
    out = {}
    for nombre, secciones in variantes.items():
        hh = h()
        for ini, fin in secciones:
            hh.update(apk[ini:fin])
        out[nombre] = hh.hexdigest()
    return out


def parse_signers(block: bytes, esquema: str):
    """Devuelve lista de firmantes con digests embebidos, certs y firmas."""
    signers = read_seq(block, 0)
    resultado = []
    for s in signers:
        signed_data, off = read_lp(s, 0)
        _, off = read_lp(s, off)  # signatures sequence
        pub_key, _ = read_lp(s, off)
        digests_seq = read_seq(signed_data, 0)
        certs_seq = read_seq(signed_data, u32(signed_data, 0) + 4)
        min_sdk = max_sdk = None
        resto = u32(signed_data, 0) + 4
        resto += u32(signed_data, resto) + 4
        if esquema == "v3" and resto + 8 <= len(signed_data):
            min_sdk = u32(signed_data, resto)
            max_sdk = u32(signed_data, resto + 4)
        digests = []
        p = 0
        for d in digests_seq:
            aid = u32(d, 0)
            dg, _ = read_lp(d, 4)
            digests.append({"algoritmo": ALGOS.get(aid, (hex(aid),))[0],
                            "algo_id": hex(aid),
                            "digest_alg": DIGEST_ALGOS.get(aid),
                            "digest": dg.hex()})
        certs = []
        for c in certs_seq:
            certs.append(c)
        # firmas
        sigs = read_seq(s, u32(s, 0) + 4)
        firmas = []
        for sg in sigs:
            aid = u32(sg, 0)
            valor, _ = read_lp(sg, 4)
            firmas.append({"algo_id": aid, "algoritmo": ALGOS.get(aid, (hex(aid),))[0],
                           "hash": ALGOS.get(aid, (None, ""))[1], "firma": valor})
        resultado.append({"digests_embebidos": digests, "certificados_der": certs,
                          "firmas": firmas, "public_key_der": pub_key,
                          "min_sdk": min_sdk, "max_sdk": max_sdk,
                          "signed_data": signed_data})
    return resultado


def describir_cert(der: bytes):
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        cert = x509.load_der_x509_certificate(der)
        fp = cert.fingerprint(hashes.SHA256()).hex()
        return {
            "sujeto": cert.subject.rfc4514_string(),
            "emisor": cert.issuer.rfc4514_string(),
            "serie": str(cert.serial_number),
            "vigente_desde": str(getattr(cert, "not_valid_before_utc", cert.not_valid_before)),
            "vigente_hasta": str(getattr(cert, "not_valid_after_utc", cert.not_valid_after)),
            "sha256": fp,
            "huella_colon": ":".join(fp[i:i + 2].upper() for i in range(0, len(fp), 2)),
            "auto_firmado": cert.subject == cert.issuer,
            "clave_publica": cert.public_key().__class__.__name__,
        }
    except Exception as e:  # noqa: BLE001
        return {"error": f"no parseable: {e}", "sha256": hashlib.sha256(der).hexdigest()}


def verificar_firma(firmante) -> dict:
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
        pub = serialization.load_der_public_key(firmante["public_key_der"])
        verificados = []
        for firma in firmante["firmas"]:
            aid = firma["algo_id"]
            datos = firmante["signed_data"]
            ok = False
            detalle = ""
            try:
                nombre = ALGOS.get(aid, (None,))[0]
                hash_name = ALGOS.get(aid, (None, None))[1]
                hh = {"SHA-256": hashes.SHA256(), "SHA-512": hashes.SHA512()}.get(hash_name)
                if nombre == "RSASSA-PKCS1-v1_5" and isinstance(pub, rsa.RSAPublicKey):
                    pub.verify(firma["firma"], datos, padding.PKCS1v15(), hh)
                    ok = True
                elif nombre == "RSASSA-PSS" and isinstance(pub, rsa.RSAPublicKey):
                    for salt in (hh.digest_size, padding.PSS.AUTO):
                        try:
                            pub.verify(firma["firma"], datos,
                                       padding.PSS(mgf=padding.MGF1(hh), salt_length=salt), hh)
                            ok = True
                            break
                        except Exception:  # noqa: BLE001, S110
                            continue
                elif nombre == "ECDSA" and isinstance(pub, ec.EllipticCurvePublicKey):
                    pub.verify(firma["firma"], datos, ec.ECDSA(hh))
                    ok = True
                else:
                    detalle = f"algoritmo {hex(aid)} no soportado para {type(pub).__name__}"
            except Exception as e:  # noqa: BLE001
                detalle = str(e)
            verificados.append({"algo_id": hex(aid), "algoritmo": firma["algoritmo"],
                                "verificada": ok, "detalle": detalle})
        return {"verificaciones": verificados}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def analizar_firma(apk_path: str):
    apk = Path(apk_path).read_bytes()
    info, err = find_sig_block(apk)
    if err:
        return {"error": err}
    salida = {"bloque": {"offset": info["block_start"], "tamanio": info["block_size"]},
              "esquemas": []}
    for pid, nombre in ((VER_ID_V2, "v2"), (VER_ID_V3, "v3"), (VER_ID_V31, "v3.1")):
        if pid not in info["pairs"]:
            continue
        for firmante in parse_signers(info["pairs"][pid], "v3" if pid != VER_ID_V2 else "v2"):
            digest_checks = []
            for d in firmante["digests_embebidos"]:
                if not d["digest_alg"]:
                    continue
                calculados = section_digests(apk, info["block_start"], info["block_size"],
                                             info["cd_offset"], d["digest_alg"])
                match = [k for k, v in calculados.items() if v == d["digest"]]
                digest_checks.append({
                    "digest_alg": d["digest_alg"], "coincide": bool(match),
                    "variante_que_coincidio": match[0] if match else None,
                    "digest_embebido": d["digest"],
                    "digests_calculados": calculados,
                })
            certs = [describir_cert(c) for c in firmante["certificados_der"]]
            verif = verificar_firma(firmante)
            salida["esquemas"].append({
                "esquema": nombre, "integridad_secciones": digest_checks,
                "firmas": verif, "certificados": certs,
                "min_sdk": firmante["min_sdk"], "max_sdk": firmante["max_sdk"],
            })
    salida["v1_presente"] = None
    try:
        import zipfile as zf
        with zf.ZipFile(apk_path) as z:
            v1 = [n for n in z.namelist()
                  if n.upper().startswith("META-INF/") and n.upper().endswith((".RSA", ".EC", ".DSA"))]
            salida["v1_presente"] = v1
    except Exception:  # noqa: BLE001, S110
        pass
    return salida


# --------------------------------------------------------------------------
# 2. Manifiesto AXML
# --------------------------------------------------------------------------

RES_STRING_POOL = 0x0001
RES_XML = 0x0003
RES_XML_RESOURCE_MAP = 0x0180
RES_XML_START_ELEMENT = 0x0102


class StringPool:
    def __init__(self, data: bytes, offset: int):
        assert u16(data, offset) == RES_STRING_POOL
        self.count = u32(data, offset + 8)
        self.flags = u32(data, offset + 16)
        self.strings_start = u32(data, offset + 20)
        self.base = offset
        base = offset + u16(data, offset + 2)
        self.data = data
        self.offsets = [u32(data, base + 4 * i) for i in range(self.count)]
        self.utf8 = bool(self.flags & 0x100)

    def get(self, idx: int) -> str:
        if idx < 0 or idx >= self.count:
            return f"@{idx}"
        o = self.base + self.strings_start + self.offsets[idx]
        if self.utf8:
            # AOSP: longitud en UTF-16 (1 o 2 bytes con bit 0x80), luego
            # longitud en UTF-8 (1 o 2 bytes con bit 0x80), luego los bytes.
            b0 = self.data[o]
            if b0 & 0x80:
                o += 2
            else:
                o += 1
            b1 = self.data[o]
            if b1 & 0x80:
                n = ((b1 & 0x7F) << 8) | self.data[o + 1]
                o += 2
            else:
                n = b1
                o += 1
            return self.data[o:o + n].decode("utf-8", "replace")
        n = u16(self.data, o)
        if n & 0x8000:
            n = ((n & 0x7FFF) << 16) | u16(self.data, o + 2)
            o += 4
        else:
            o += 2
        return self.data[o:o + 2 * n].decode("utf-16-le", "replace")


TIPOS = {0x00: "null", 0x01: "reference", 0x02: "attribute", 0x03: "string",
         0x04: "float", 0x05: "dimension", 0x06: "fraction", 0x10: "int_dec",
         0x11: "int_hex", 0x12: "boolean", 0x1C: "color_argb8", 0x1D: "color_rgb8",
         0x1E: "color_argb4", 0x1F: "color_rgb4"}


def parse_manifest(apk_path: str):
    import zipfile as zf
    with zf.ZipFile(apk_path) as z:
        data = z.read("AndroidManifest.xml")
    assert u16(data, 0) == RES_XML
    sp = StringPool(data, u16(data, 2))
    res_map = []
    off = u16(data, 2)
    off += u32(data, off + 4)
    if u16(data, off) == RES_XML_RESOURCE_MAP:
        n = u32(data, off + 4)
        res_map = [u32(data, off + 8 + 4 * i) for i in range((n - 8) // 4)]
        off += n
    raiz = {"tag": "manifest", "attrs": {}, "children": []}
    pila = [raiz]
    while off + 8 <= len(data):
        tipo = u16(data, off)
        tamanio = u32(data, off + 4)
        if tamanio <= 0:
            break
        if tipo == RES_XML_START_ELEMENT:
            ns = u32(data, off + 16)
            name_idx = u32(data, off + 20)
            attr_count = u16(data, off + 28)
            attrs = {}
            aoff = off + 36
            for i in range(attr_count):
                aname = u32(data, aoff + 4)
                raw = u32(data, aoff + 8)
                dtype = data[aoff + 15]
                dval = u32(data, aoff + 16)
                if aname == 0xFFFFFFFF and ns != 0xFFFFFFFF:
                    aname = ns
                nombre = sp.get(aname) if aname != 0xFFFFFFFF else None
                if nombre in (None, f"@{aname}"):
                    nombre = ANDROID_ATTRS.get(aname, f"res_{aname:08x}" if aname != 0xFFFFFFFF else "attr")
                if raw != 0xFFFFFFFF:
                    valor = sp.get(raw)
                elif dtype == 0x12:
                    valor = "true" if dval else "false"
                elif dtype in (0x10, 0x11):
                    valor = str(dval)
                elif dtype == 0x01:
                    valor = f"@ref_{dval:08x}"
                else:
                    valor = f"{TIPOS.get(dtype, hex(dtype))}:{dval}"
                attrs[nombre] = valor
                aoff += 20
            el = {"tag": sp.get(name_idx), "attrs": attrs, "children": []}
            pila[-1]["children"].append(el)
            pila.append(el)
        elif tipo == 0x0103:  # end element
            if len(pila) > 1:
                pila.pop()
        off += tamanio
    return sp, res_map, raiz


def analizar_manifest(apk_path: str):
    _, _, raiz = parse_manifest(apk_path)
    man = raiz["children"][0] if raiz["children"] else raiz
    usos_permiso, usos_feature = [], []
    usos_sdk = {}
    app_attrs = {}
    componentes = []
    for el in man["children"]:
        if el["tag"] == "uses-permission":
            usos_permiso.append(el["attrs"].get("name", "?"))
        elif el["tag"] == "uses-feature":
            usos_feature.append(el["attrs"].get("name", el["attrs"].get("glEsVersion", "?")))
        elif el["tag"] == "uses-sdk":
            usos_sdk = dict(el["attrs"])
        elif el["tag"] == "application":
            app_attrs = dict(el["attrs"])
            for c in el["children"]:
                if c["tag"] in ("activity", "activity-alias", "service", "receiver", "provider"):
                    comp = {"tipo": c["tag"], **c["attrs"]}
                    filtros = []
                    for f in c["children"]:
                        if f["tag"] == "intent-filter":
                            acciones = [h["attrs"].get("name") for h in f["children"] if h["tag"] == "action"]
                            cats = [h["attrs"].get("name") for h in f["children"] if h["tag"] == "category"]
                            datos = [h["attrs"] for h in f["children"] if h["tag"] == "data"]
                            filtros.append({"actions": acciones, "categories": cats, "data": datos})
                    comp["_intent_filters"] = filtros
                    componentes.append(comp)
    target_sdk = int(man["attrs"].get("targetSdkVersion", "0") or 0)

    def exported_efectivo(c):
        if "exported" in c:
            return c["exported"] == "true", "declarado"
        if c["tipo"] == "provider":
            return True, "por_defecto_provider"
        if c["_intent_filters"]:
            if target_sdk >= 31:
                return True, "por_defecto_target31_con_filter"
            return True, "por_defecto_pre31_con_filter"
        return False, "por_defecto_sin_filter"

    comps = []
    for c in componentes:
        exp, base = exported_efectivo(c)
        comps.append({**{k: v for k, v in c.items() if not k.startswith("_")},
                      "exported_efectivo": exp, "exported_base": base,
                      "intent_filters": c["_intent_filters"]})
    return {
        "paquete": man["attrs"].get("package"),
        "versionCode": man["attrs"].get("versionCode"),
        "versionName": man["attrs"].get("versionName"),
        "compileSdkVersion": man["attrs"].get("compileSdkVersion"),
        "uses_sdk": usos_sdk,
        "minSdkVersion": usos_sdk.get("minSdkVersion"),
        "targetSdkVersion": usos_sdk.get("targetSdkVersion"),
        "maxSdkVersion": usos_sdk.get("maxSdkVersion"),
        "uses_permission": sorted(set(usos_permiso)),
        "uses_feature": sorted(set(usos_feature)),
        "application_attrs": app_attrs,
        "componentes": comps,
        "conteo_componentes": {
            t: sum(1 for c in comps if c["tipo"] == t)
            for t in ("activity", "activity-alias", "service", "receiver", "provider")
        },
    }


def main():
    apk, salida = sys.argv[1], sys.argv[2]
    res = {
        "apk": str(apk),
        "sha256_apk": hashlib.sha256(Path(apk).read_bytes()).hexdigest(),
        "bytes": Path(apk).stat().st_size,
        "firma": analizar_firma(apk),
        "manifest": analizar_manifest(apk),
        "herramienta": "analisis_apk_propio.py (biblioteca estandar + cryptography 50)",
        "confianza": "observado",
    }
    Path(salida).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    m = res["manifest"]
    print("paquete:", m["paquete"], "| version:", m["versionName"], f"({m['versionCode']})")
    print("targetSdk:", m["targetSdkVersion"], "| permisos:", len(m["uses_permission"]),
          "| componentes:", sum(m["conteo_componentes"].values()))
    esquemas = [(e["esquema"], all(d["coincide"] for d in e["integridad_secciones"]))
                for e in res["firma"].get("esquemas", [])]
    print("firmas:", esquemas)


if __name__ == "__main__":
    main()
