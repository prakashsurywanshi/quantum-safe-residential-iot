#!/usr/bin/env bash
# Re-run ALL ProVerif verification models for the QHSG security proof.
# Usage: ./run_all.sh [path-to-proverif-binary]
#
# Each model is run with ProVerif 2.05; the raw transcript is written to
# results_<tag>.txt next to the model, and the "Verification summary" block
# is echoed to stdout.
set -euo pipefail

PV="${1:-proverif}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# model:results-tag  (one entry per .pv file)
models=(
  "qhsg_key_lifecycle:results_lifecycle"
  "refresh_policy_stateless:results_stateless"
  "refresh_policy_eq10:results_eq10"
  "endpoint_isolation:results_isolation"
  "forward_secrecy:results_forward"
  "gateway_compromise_fs:results_gateway_fs"
  "key_independence:results_key_independence"
  "replay_packetloss_bound:results_replay_bound"
  "replay_packetloss_stateless:results_replay_stateless"
  "replay_reorder_window:results_replay_reorder"
  "impersonation_auth:results_impersonation_auth"
  "impersonation_noauth:results_impersonation_noauth"
)

status=0
for entry in "${models[@]}"; do
    name="${entry%%:*}"
    res="${entry##*:}"
    echo "== $name.pv =="
    if ! "$PV" "$HERE/$name.pv" > "$HERE/$res.txt" 2>&1; then
        status=1
    fi
    sed -n '/Verification summary:/,/^---/p' "$HERE/$res.txt"
done

echo "All models processed; raw transcripts in $HERE/results_*.txt."
exit "$status"
