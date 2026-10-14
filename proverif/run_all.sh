#!/usr/bin/env bash
# Re-run all ProVerif verification models for the QHSG security proof.
# Usage: ./run_all.sh [path-to-proverif-binary]
set -euo pipefail

PV="${1:-proverif}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for name in qhsg_key_lifecycle refresh_policy_stateless refresh_policy_eq10 \
            endpoint_isolation forward_secrecy; do
    echo "== $name.pv =="
    "$PV" "$HERE/$name.pv" | sed -n '/Verification summary:/,/^---/p'
done