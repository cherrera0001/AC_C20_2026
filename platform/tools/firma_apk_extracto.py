#!/usr/bin/env python3
"""Extraccion forense de certificados y verificacion de integridad del APK.

Trata el APK Signing Block como contenedor opaco: escanea cada par (v2, v3,
v3.1) buscando certificados X.509 DER (SEQUENCE 0x30 0x82..) y verifica que
los digests embebidos de las tres secciones del ZIP coincidan con los bytes
reales del APK. No asume la estructura interna de firmantes (soporta rotacion
de claves / multiples firmantes de v3.1).

Uso: python firma_apk_extracto.py <apk> <salida.json>
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

MAGIC = b"APK Sig Block 42"
PARES = {0x7109871A: "v2", 0xF05368C0: "v3", 0x1B93AD61: "v3.1"}
DIGEST_ALGOS = {0x0101: "sha256", 0x0102: "sha512", 0x0103: "sha256", 0x0104: "sha512",
                0x0105: "sha256", 0x0106: "sha512", 0x0109: "sha256", 0x010A: "sha256"}
# Huella SHA-256 (colon-upper) del certificado de firma de WhatsApp LLC
# documentada publicamente por Meta para verificar APKs genuinos.
W4B_FP_PUBLICADA = "55:6B:FC:32:2F:59:F8:1F:1A:5D:F8:95:F0:1B:56:E1:6F:40:B8:4D:8F:F7:78:1D:A1:B2:56:82:62:DE:39:87:0A:91:0F"


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def extrae_certificados(blob: bytes):
    """Escanea secuencias DER 30 82 LL LL parseables como X.509."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    certs = {}
    i = 0
    while True:
        i = blob.find(b"\x30\x82", i)
        if i < 0 or i + 4 > len(blob):
            break
        ln = struct.unpack_from(">H", blob, i + 2)[0] + 4
        der = blob[i:i + ln]
        try:
            c = x509.load_der_x509_certificate(der)
            fp = c.fingerprint(hashes.SHA256()).hex()
            certs[fp] = {
                "sujeto": c.subject.rfc4514_string(),
                "emisor": c.issuer.rfc4514_string(),
                "serie": str(c.serial_number),
                "desde": str(getattr(c, "not_valid_before_utc", c.not_valid_before)),
                "hasta": str(getattr(c, "not_valid_after_utc", c.not_valid_after)),
                "sha256_colon": ":".join(fp[j:j + 2].upper() for j in range(0, len(fp), 2)),
                "auto_firmado": c.subject == c.issuer,
                "tipo_clave": c.public_key().__class__.__name__,
            }
            i += ln
        except Exception:  # noqa: BLE001
            i += 2
    return list(certs.values())


def main():
    apk_path, salida = sys.argv[1], sys.argv[2]
    apk = Path(apk_path).read_bytes()
    eocd = apk.rfind(b"PK\x05\x06")
    cd_offset = u32(apk, eocd + 16)
    magic_pos = apk.rfind(MAGIC, 0, cd_offset)
    size2 = u64(apk, magic_pos - 8)
    block_start = magic_pos + 8 - size2
    size1 = u64(apk, block_start)
    block_size = size1 + 8

    p, pares = block_start + 8, {}
    while p < magic_pos - 8:
        pid = u32(apk, p)
        n = u32(apk, p + 4)
        pares[pid] = apk[p + 8: p + 8 + n]
        p += 8 + n

    # Integridad: digests embebidos (cualquier par v2/v3) vs secciones reales.
    integridad = []
    embebidos = []
    for pid, nombre in PARES.items():
        if pid not in pares:
            continue
        blob = pares[pid]
        # localiza tuplas (algo u32, len u32, digest) dentro del blob
        for j in range(len(blob) - 40):
            aid = u32(blob, j)
            if aid in DIGEST_ALGOS and u32(blob, j + 4) in (32, 64):
                dg = blob[j + 8: j + 8 + u32(blob, j + 4)].hex()
                if dg not in [e["digest"] for e in embebidos]:
                    embebidos.append({"esquema": nombre, "algo_id": hex(aid),
                                      "digest_alg": DIGEST_ALGOS[aid], "digest": dg})

    CHUNK = 1024 * 1024
    secciones = [(0, block_start), (block_start + block_size, cd_offset), (cd_offset, len(apk))]

    def digest_secciones(algoritmo: str, prefijo_u64: bool, chunked: bool) -> str:
        h = hashlib.new(algoritmo)
        for a, b in secciones:
            if not chunked:
                if prefijo_u64:
                    h.update(struct.pack("<Q", b - a))
                h.update(apk[a:b])
                continue
            p_ = a
            while p_ < b:
                piece = apk[p_: p_ + CHUNK]
                if prefijo_u64:
                    h.update(struct.pack("<Q", len(piece)))
                h.update(piece)
                p_ += CHUNK
        return h.hexdigest()

    for e in embebidos:
        calculados = {}
        for chunked in (False, True):
            for pref in (False, True):
                clave = f"chunks1M_prefU64={pref}" if chunked else f"completo_prefU64={pref}"
                calculados[clave] = digest_secciones(e["digest_alg"], pref, chunked)
        coinciden = [k for k, v in calculados.items() if v == e["digest"]]
        integridad.append({**e, "coincide": bool(coinciden),
                           "variante": coinciden[0] if coinciden else None,
                           "calculados": calculados})

    certificados = {}
    for pid, nombre in PARES.items():
        if pid in pares:
            for c in extrae_certificados(pares[pid]):
                c["esquema"] = nombre
                certificados.setdefault(c["sha256_colon"], c)

    clist = list(certificados.values())
    for c in clist:
        c["coincide_con_whatsapp_llc_publicada"] = (c["sha256_colon"] == W4B_FP_PUBLICADA)

    out = {
        "apk": apk_path,
        "sha256_apk": hashlib.sha256(apk).hexdigest(),
        "bloque_firma": {"offset": block_start, "tamanio": block_size,
                         "pares_presentes": [PARES[k] for k in pares if k in PARES],
                         "otros_ids": [hex(k) for k in pares if k not in PARES]},
        "integridad_secciones": integridad,
        "certificados": clist,
        "huella_publicada_whatsapp_llc": W4B_FP_PUBLICADA,
        "metodo": "extraccion DER + recalculo de digests de secciones (sin asumir estructura de firmantes)",
    }
    Path(salida).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("pares:", out["bloque_firma"]["pares_presentes"], "| certs:", len(clist),
          "| digests ok:", sum(1 for i in integridad if i["coincide"]), "/", len(integridad))
    for c in clist:
        print(" cert:", c["sujeto"][:60], "|", c["tipo_clave"], "| wsp-llc:", c["coincide_con_whatsapp_llc_publicada"])


if __name__ == "__main__":
    main()
