# COOJA / Contiki-NG protocol-level validation — Quantum-Resilient Residential IoT

This directory contains the protocol-level validation of the 6LoWPAN
fragmentation model used in the manuscript's energy analysis (the subsection
*Protocol-Level Validation in COOJA*). Its purpose is narrow and fully
reproducible: it measures how many IEEE 802.15.4 frames the Contiki-NG 6LoWPAN
layer actually emits for a single UDP datagram of a given payload size, and
checks that measurement against the closed form used by the analytical model,

```
N_frag = ceil((payload + 12) / 96)
```

where 12 bytes is the compressed IPv6/UDP header and 96 bytes
(`(104 - 5) & ~7`) is the usable payload per fragment. These constants come from
the Contiki-NG implementation and are **not** assumptions of the analytical
model.

## Tools

- **Contiki-NG**: https://github.com/contiki-ng/contiki-ng
- **COOJA**: Java-based simulator bundled with Contiki-NG (run headless via
  Docker; no X11 required)
- **Docker image**: `contiker/contiki-ng`

## Layout

```
cooja/
  apps/qhsg-udp/       probe + server motes, Makefile, project-conf.h, generator
  config/              generated .csc scenarios (one per payload size) [after run]
  logs/run-frag-<L>/   raw COOJA logs, one directory per payload size
  results/             fragmentation_results.csv (machine-readable outcome)
  scripts/             run_fragmentation.sh, parse_cooja_log.py
  patch/               contiki-ng-ipv6-mtu.patch (required UIP_LINK_MTU raise)
```

## What the scenarios do

Each scenario adds two motes: mote 1 is the RPL root / UDP server
(`qhsg-server.c`), mote 2 is the probe client (`qhsg-probe-<L>.c`). The client
sends five UDP datagrams of `L` bytes and brackets each send with
`QHSG_TX_BEGIN`/`QHSG_TX_END` log markers. Two independent signals are recorded:

1. **Authoritative:** the 6LoWPAN layer logs
   `output: fragmentation needed. fragments: N`
   (`LOG_CONF_LEVEL_6LOWPAN = LOG_LEVEL_INFO`).
2. **Cross-check:** the framer logs one `Frame 15.4 ... Out: ...` line per
   emitted IEEE 802.15.4 frame (`LOG_CONF_LEVEL_FRAMER = LOG_LEVEL_INFO`).

`parse_cooja_log.py` counts the `Out:` frames between each BEGIN/END pair and, if
present, prefers the 6LoWPAN fragment count; the two always agree.

## Prerequisite: raise `UIP_LINK_MTU`

Stock Contiki-NG hard-codes `UIP_LINK_MTU` to 1280 bytes, so the 2272-byte
ML-KEM-768 handshake payload is silently dropped by `tcpip_ipv6_output()`
("output: Packet too big"). Apply the supplied patch:

```bash
cd <CONTIKI>
git apply /path/to/repo/cooja/patch/contiki-ng-ipv6-mtu.patch
```

and set `UIP_LINK_MTU 3000` in `cooja/apps/qhsg-udp/project-conf.h` (already
done). This is the only change required to the Contiki-NG tree.

## Running (headless)

```bash
CONTIKI=/path/to/contiki-ng \
GRADLE_HOME=/path/to/.gradle \
bash cooja/scripts/run_fragmentation.sh
```

The script installs `apps/qhsg-udp` into `<CONTIKI>/examples/qhsg-udp`,
generates the per-size sources and `.csc` files, runs each scenario headless
(`contiker/contiki-ng`, `--no-gui`), copies the raw logs into
`cooja/logs/run-frag-<L>/`, and regenerates
`cooja/results/fragmentation_results.csv`. Each scenario takes well under a
minute once the Contiki-NG image and the Gradle cache are warm.

## Measured result

| Payload (B) | Frames | Predicted | Match |
|-------------|--------|-----------|-------|
| 64          | 1      | 1         | yes   |
| 128         | 2      | 2         | yes   |
| 256         | 3      | 3         | yes   |
| 512         | 6      | 6         | yes   |
| 1024        | 11     | 11        | yes   |
| 1232        | 13     | 13        | yes   |
| 2272        | 24     | 24        | yes   |

The 2272-byte PQC handshake therefore costs 24 link-layer frames, which is the
transmission cost that dominates the direct-PQC energy penalty reported in the
manuscript (Table 2 and Figure `Fig_Energy_Scalability`).

## Notes / scope

- **Energest is intentionally not used.** Energest counters reported
  implausible (underflow/garbage) values under COOJA and did not scale with
  payload, so they are unsuitable as an energy source here. The validated
  quantity is the *frame/fragment count*; the frame count is combined with the
  datasheet radio constants inside `simulation_benchmarks.py`.
- This directory validates link-layer fragmentation only. It does **not**
  re-derive the gateway/broadband side of the architecture, which is modeled
  analytically.
