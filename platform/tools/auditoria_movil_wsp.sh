#!/usr/bin/env bash
# Auditoría móvil C4A — dispositivo personal del auditor + WhatsApp.
# Contrato: scope/alcance_movil.md (borrador 2026-10-28). SOLO LECTURA:
# inventario del dispositivo, dumpsys del paquete, extracción del APK base
# y análisis estático con REA. Sin tráfico de red, sin ejecutar la app,
# sin leer chats/bases de datos/cuentas/medisos, sin modificar el dispositivo.
#
# Uso:
#   bash platform/tools/auditoria_movil_wsp.sh [--esperar <segundos>] [--serial <dispositivo>] [--paquete <nombre>]
#
# Salida: evidence/RUN-<utc>-<hex>/ con resultados REA (json), crudos,
# APK extraído, SHA256SUMS.txt, MANIFEST.json y reportes/pasos.log.
set -uo pipefail

ESPERAR=0
SERIAL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --esperar) ESPERAR="${2:-900}"; shift 2 ;;
    --serial)  SERIAL="${2:-}";     shift 2 ;;
    --paquete) PKG_ARG="${2:-}";    shift 2 ;;
    *) echo "Uso: $0 [--esperar <seg>] [--serial <dispositivo>] [--paquete <nombre>]" >&2; exit 2 ;;
  esac
done

ADB="${ADB:-C:/Users/herre/AppData/Local/Microsoft/WinGet/Packages/Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe/platform-tools/adb.exe}"
export REA_ADB_PATH="$ADB"
REA_PKG="rea-agents@6.8.0"
PKG="${PKG_ARG:-com.whatsapp}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_ID="RUN-$(date -u +%Y%m%dT%H%M%SZ)-$(od -An -tx1 -N2 /dev/urandom | tr -d ' \n')"
RUN_DIR="$RAIZ/evidence/$RUN_ID"
mkdir -p "$RUN_DIR"/{rea,raw,apk,reportes}
LOG="$RUN_DIR/reportes/pasos.log"
STATUS=0

log(){ printf '%s %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$LOG"; }

rea_run(){ # <nombre_salida> <comando_rea...>
  local out="$1"; shift
  if npx -y "$REA_PKG" "$@" --format json > "$RUN_DIR/rea/$out.json" 2> "$RUN_DIR/rea/$out.stderr.log"; then
    log "OK   rea $out"
  else
    log "FALLO rea $out (ver rea/$out.stderr.log)"; STATUS=1
  fi
}

serial_detectado(){
  "$ADB" devices | awk '$2=="device"{print $1}' | head -1
}

if [[ -z "$SERIAL" ]]; then
  SERIAL="$(serial_detectado)"
  if [[ -z "$SERIAL" && "$ESPERAR" -gt 0 ]]; then
    log "Sin dispositivo; esperando hasta ${ESPERAR}s (pendiente P2 de alcance_movil)..."
    fin=$((SECONDS + ESPERAR))
    while [[ $SECONDS -lt $fin ]]; do
      SERIAL="$(serial_detectado)"
      [[ -n "$SERIAL" ]] && break
      sleep 5
    done
  fi
fi

if [[ -z "$SERIAL" ]]; then
  log "NO HAY DISPOSITIVO CONECTADO."
  log "Requerido (P2): cable USB, 'Depuración USB' activa y aceptar la huella RSA en el teléfono."
  exit 3
fi
if "$ADB" devices | grep -q "^${SERIAL}.*unauthorized"; then
  log "DISPOSITIVO SIN AUTORIZAR ($SERIAL): acepta la huella RSA en la pantalla del teléfono."
  exit 4
fi
log "RUN_DIR=$RUN_DIR"
log "Dispositivo detectado: $SERIAL"

rea_run "00_list_adb_devices"  list-adb-devices
rea_run "01_inspect_adb_device" inspect-adb-device "$SERIAL"
rea_run "02_resolve_whatsapp"  resolve-adb-packages "$SERIAL" whatsapp
rea_run "03_inspect_whatsapp"  inspect-adb-package "$SERIAL" "$PKG"

if "$ADB" -s "$SERIAL" shell dumpsys package "$PKG" > "$RUN_DIR/raw/dumpsys_${PKG}.txt" 2>> "$LOG"; then
  log "OK   dumpsys package $PKG (permisos y componentes declarados/concedidos)"
else
  log "FALLO dumpsys package $PKG"; STATUS=1
fi

rea_run "04_pull_whatsapp" pull-adb-package "$SERIAL" "$PKG" --output-directory "$RUN_DIR/apk"

BASE_APK="$RUN_DIR/apk/$PKG/base.apk"
if [[ -f "$BASE_APK" ]]; then
  rea_run "05_inspect_apk" inspect-android-package "$BASE_APK"
  (cd "$RUN_DIR" && find . -type f ! -name SHA256SUMS.txt ! -name MANIFEST.json ! -path "./reportes/*" -exec sha256sum {} + > SHA256SUMS.txt)
  log "OK   SHA256SUMS.txt"
  if (cd "$RUN_DIR" && sha256sum -c SHA256SUMS.txt > reportes/verificacion_hashes.txt 2>&1); then
    log "OK   verificación de hashes"
  else
    log "FALLO verificación de hashes"; STATUS=1
  fi
else
  log "FALLO: no se obtuvo $BASE_APK; se omite análisis estático del APK"; STATUS=1
fi

python - "$RUN_DIR" "$SERIAL" "$PKG" > "$RUN_DIR/MANIFEST.json" <<'PY'
import hashlib, json, os, sys
run_dir, serial, pkg = sys.argv[1], sys.argv[2], sys.argv[3]
files = []
for base, _dirs, names in os.walk(run_dir):
    for n in sorted(names):
        p = os.path.join(base, n)
        rel = os.path.relpath(p, run_dir).replace(os.sep, "/")
        if rel in ("MANIFEST.json",):
            continue
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        files.append({"path": rel, "sha256": h.hexdigest(), "bytes": os.path.getsize(p)})
json.dump({
    "run_id": os.path.basename(run_dir),
    "alcance": "scope/alcance_movil.md",
    "metodo": "solo-lectura ADB + analisis estatico REA (rea-agents@6.8.0)",
    "serial_dispositivo": serial,
    "paquete": pkg,
    "colectado_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    "archivos": files,
}, sys.stdout, indent=2, ensure_ascii=False)
PY

log "Terminado STATUS=$STATUS RUN_DIR=$RUN_DIR"
exit $STATUS
