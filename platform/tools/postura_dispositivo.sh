#!/usr/bin/env bash
# Postura de seguridad del dispositivo (solo lectura): bootloader, verified boot,
# cifrado y estado de Play Protect. Complementa RUN-20261029T003246Z-3802.
set -uo pipefail
ADB="${ADB:-C:/Users/herre/AppData/Local/Microsoft/WinGet/Packages/Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe/platform-tools/adb.exe}"
ESPERAR="${1:-1800}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_DIR="$RAIZ/evidence/RUN-20261029T003246Z-3802"
mkdir -p "$RUN_DIR/raw" "$RUN_DIR/reportes"
LOG="$RUN_DIR/reportes/postura.log"
log(){ printf '%s %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$LOG"; }

SERIAL="$("$ADB" devices | awk '$2=="device"{print $1}' | head -1)"
if [[ -z "$SERIAL" && "$ESPERAR" -gt 0 ]]; then
  log "sin dispositivo; esperando hasta ${ESPERAR}s..."
  fin=$((SECONDS + ESPERAR))
  while [[ $SECONDS -lt $fin ]]; do
    SERIAL="$("$ADB" devices | awk '$2=="device"{print $1}' | head -1)"
    [[ -n "$SERIAL" ]] && break
    sleep 5
  done
fi
[[ -z "$SERIAL" ]] && { log "no se conectó dispositivo; reintentar al conectarlo"; exit 3; }
log "dispositivo: $SERIAL"

OUT="$RUN_DIR/raw/postura_dispositivo.txt"
{
  echo "# postura de seguridad del dispositivo (solo lectura) - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# serial: $SERIAL"
  echo "## getprop seguridad"
  for prop in ro.boot.flash.locked ro.boot.verifiedbootstate ro.boot.veritymode \
              ro.crypto.state ro.crypto.type ro.debuggable ro.secure ro.build.type \
              ro.boot.warranty_bit ro.warranty_bit sys.oem_unlock_allowed \
              ro.build.version.security_patch; do
    echo "$prop=$("$ADB" -s "$SERIAL" shell getprop "$prop" 2>/dev/null | tr -d '\r')"
  done
  echo "## play protect / verificador de paquetes"
  for g in package_verifier_enable package_verifier_user_consent upload_apk_enable; do
    echo "settings global $g=$("$ADB" -s "$SERIAL" shell settings get global "$g" 2>/dev/null | tr -d '\r')"
  done
  echo "## gms (play services) instalado"
  "$ADB" -s "$SERIAL" shell pm list packages com.google.android.gms 2>/dev/null | tr -d '\r'
  echo "## vending (play store) instalado"
  "$ADB" -s "$SERIAL" shell pm list packages com.android.vending 2>/dev/null | tr -d '\r'
} > "$OUT"
log "capturado: $OUT ($(wc -l < "$OUT") lineas)"

(cd "$RUN_DIR" && find . -type f ! -name SHA256SUMS.txt ! -name MANIFEST.json ! -path "./reportes/*" -exec sha256sum {} + > SHA256SUMS.txt)
(cd "$RUN_DIR" && sha256sum -c SHA256SUMS.txt > reportes/verificacion_hashes.txt 2>&1) && log "custodia actualizada OK" || log "FALLO custodia"
exit 0
