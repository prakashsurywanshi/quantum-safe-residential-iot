#!/usr/bin/env bash
#
# Reproduce the COOJA 6LoWPAN fragmentation validation of Section "Protocol-Level
# Validation in COOJA" in the manuscript.
#
# Requirements:
#   * a Contiki-NG checkout, built once with:
#       cd <CONTIKI>/tools/cooja && ./gradlew
#   * Docker with the contiker/contiki-ng image pulled
#   * a Gradle home directory containing the resolved dependencies (offline run)
#
# Usage:
#   CONTIKI=/path/to/contiki-ng \
#   GRADLE_HOME=/path/to/.gradle \
#   bash cooja/scripts/run_fragmentation.sh
#
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
CONTIKI="${CONTIKI:-/tmp/opencode/contiki-ng}"
GRADLE_HOME="${GRADLE_HOME:-/tmp/opencode/gradle-home}"
IMG="${COOJA_IMAGE:-contiker/contiki-ng:latest}"
LENGTHS=(64 128 256 512 1024 1232 2272)

echo "[run_fragmentation] repo   = $REPO"
echo "[run_fragmentation] contiki= $CONTIKI"
echo "[run_fragmentation] image  = $IMG"

APP_DST="$CONTIKI/examples/qhsg-udp"
echo "[run_fragmentation] installing app into $APP_DST"
rm -rf "$APP_DST"
mkdir -p "$APP_DST"
cp "$REPO"/cooja/apps/qhsg-udp/* "$APP_DST"/
python3 "$APP_DST/gen_probe.py"
cp "$APP_DST"/qhsg-frag-*.csc "$REPO"/cooja/config/

for L in "${LENGTHS[@]}"; do
  echo "[run_fragmentation] === payload $L bytes ==="
  docker run --rm --name "cooja-frag-$L" --memory=3g \
    --mount type=bind,source="$CONTIKI",target=/home/user/contiki-ng \
    --mount type=bind,source="$GRADLE_HOME",target=/home/user/.gradle \
    -w /home/user/contiki-ng/tools/cooja "$IMG" \
    bash -lc "./gradlew --offline run --args=\"--no-gui /home/user/contiki-ng/examples/qhsg-udp/qhsg-frag-$L.csc\""

  mkdir -p "$REPO/cooja/logs/run-frag-$L"
  cp "$APP_DST/results-$L.txt" "$REPO/cooja/logs/run-frag-$L/qhsg-full.log"
done

echo "[run_fragmentation] parsing logs -> cooja/results/fragmentation_results.csv"
python3 "$REPO/cooja/scripts/parse_cooja_log.py" \
  "$REPO"/cooja/logs/run-frag-*/qhsg-full.log \
  --csv "$REPO/cooja/results/fragmentation_results.csv"

echo "[run_fragmentation] done."
