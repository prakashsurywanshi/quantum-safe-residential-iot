#!/usr/bin/env python3
"""Parse COOJA QHSG fragmentation-probe logs and report link-layer frame counts.

Input: the per-message log file written by the COOJA ScriptRunner, one line per
mote log message, formatted as ``<mote_id>|<raw message>``.

The client firmware brackets every datagram with::

    PROBE begin seq=<n> len=<L>
    ...
    PROBE end   seq=<n> len=<L>

Between the two markers we count the 802.15.4 frames the client actually emits
at the MAC/framer layer (``Frame 15.4 ... Out: ...``).  The frame count is the
measured 6LoWPAN fragment count for that datagram and is compared against the
analytic value ``ceil((L + hdr) / frag_size)``.

Usage:
    parse_cooja_log.py results-64.txt [results-128.txt ...] [--csv out.csv]
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from pathlib import Path

BEGIN_RE = re.compile(r"QHSG_TX_BEGIN seq=(\d+) len=(\d+)")
END_RE = re.compile(r"QHSG_TX_END seq=(\d+) len=(\d+)")
# e.g. "Out:  1 0001.0001.0001.0001 21 102 (123)"
OUT_RE = re.compile(r"Out:\s+\d+\s+\S+\s+(\d+)\s+(\d+)\s+\((\d+)\)")
# authoritative 6LoWPAN fragment count logged by sicslowpan.c
FRAGCOUNT_RE = re.compile(r"fragmentation needed\. fragments: (\d+)")
LINE_RE = re.compile(r"^(\d+)\|(.*)$")

CLIENT_ID = 2

# COOJA-measured 6LoWPAN fragmentation parameters (client mote).
FRAGN_DATA = 96        # (NETSTACK_MAC.max_payload() - FRAGN_HDR) & ~7 = (104-5)&~7
COMP_HDR = 12          # compressed IPv6 + UDP header


def analytic_fragments(payload: int) -> int:
    """6LoWPAN fragmentation count, validated against COOJA."""
    return max(1, -(-(payload + COMP_HDR) // FRAGN_DATA))  # ceil division


def parse_file(path: Path) -> list[dict]:
    rows: list[dict] = []
    cur = None
    with path.open(errors="replace") as fh:
        for raw in fh:
            m = LINE_RE.match(raw.rstrip("\n"))
            if not m:
                continue
            mid = int(m.group(1))
            msg = m.group(2)

            if mid != CLIENT_ID:
                continue

            b = BEGIN_RE.search(msg)
            if b:
                cur = {"seq": int(b.group(1)), "len": int(b.group(2)),
                       "frames": 0, "bytes": 0, "frag_log": 0}
                continue
            e = END_RE.search(msg)
            if e and cur is not None:
                cur["measured_fragments"] = (cur["frag_log"]
                                             if cur["frag_log"] else cur["frames"])
                cur["analytic_fragments"] = analytic_fragments(cur["len"])
                rows.append(cur)
                cur = None
                continue
            if cur is not None:
                f = FRAGCOUNT_RE.search(msg)
                if f:
                    cur["frag_log"] = int(f.group(1))
                o = OUT_RE.search(msg)
                if o:
                    cur["frames"] += 1
                    cur["bytes"] += int(o.group(2))
    return rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--csv", type=Path, default=None)
    args = ap.parse_args(argv)

    all_rows: list[dict] = []
    for log in args.logs:
        rows = parse_file(log)
        if not rows:
            print(f"[warn] no PROBE windows found in {log}", file=sys.stderr)
            continue
        all_rows.extend(rows)
        print(f"\n== {log.name} ==")
        print(f"{'seq':>4} {'len':>6} {'frames':>7} {'bytes':>7} "
              f"{'analytic':>9}")
        for r in rows:
            print(f"{r['seq']:>4} {r['len']:>6} {r['measured_fragments']:>7} "
                  f"{r['bytes']:>7} {r['analytic_fragments']:>9}")

    if all_rows:
        print("\n== summary by payload size ==")
        print(f"{'len':>6} {'n':>3} {'frames(med)':>12} {'frames(min/max)':>16} "
              f"{'analytic':>9} {'match':>6}")
        for length in sorted({r["len"] for r in all_rows}):
            sub = [r for r in all_rows if r["len"] == length]
            med = statistics.median(r["measured_fragments"] for r in sub)
            lo = min(r["measured_fragments"] for r in sub)
            hi = max(r["measured_fragments"] for r in sub)
            ana = sub[0]["analytic_fragments"]
            match = "OK" if lo == hi == ana else "CHECK"
            print(f"{length:>6} {len(sub):>3} {med:>12g} "
                  f"{f'{lo}/{hi}':>16} {ana:>9} {match:>6}")

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["payload_bytes", "seq",
                                               "measured_fragments",
                                               "analytic_fragments",
                                               "on_air_bytes"])
            w.writeheader()
            for r in all_rows:
                w.writerow({"payload_bytes": r["len"], "seq": r["seq"],
                            "measured_fragments": r["measured_fragments"],
                            "analytic_fragments": r["analytic_fragments"],
                            "on_air_bytes": r["bytes"]})
        print(f"\nwrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
