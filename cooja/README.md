# COOJA/Contiki-NG protocol-level simulations — Quantum-Resilient Residential IoT

This directory provides the protocol-level simulation environment for the
QHSG architecture under realistic 6LoWPAN/RPL conditions (RAM budget ≤ 2 GB
noted in the manuscript). The goal is to provide reproducible COOJA scenarios,
configuration files, and instructions to extract energest/packet-loss statistics
for N ∈ {10, 25, 50, 100} nodes with packet-loss profiles {0%, 5%, 20%}. The
results complement the analytical energy model (`simulation_benchmarks.py`,
`data/Table_Energy_Results.csv`) and the symbolic proofs (`proverif/`).

## Tools

- **Contiki-NG**: https://github.com/contiki-ng/contiki-ng
- **COOJA**: Java-based simulator bundled with Contiki-NG (run via Docker or
  native)

## Running with Docker

The project includes a publicly available Contiki-NG image (`contiker/contiki-ng`);
use `--mount` for host I/O (see below). On this host, RAM is ~7.7 GB with
limited free memory (~1.4 GB) — the `--memory=2g` flag was recommended in the
plan. Note that running COOJA GUI inside headless environments requires X11
forwarding.

### Minimal invocation
```bash
PROJ="/home/prakashsuryawanshi/Projects/Reserch Papaers/Journal/Sustainable Computing: Informatics and Systems/Paper/Project"
docker run --rm --memory=2g \
  --mount type=bind,source="$PROJ",target=/project \
  contiker/contiki-ng bash -lc 'cd /project/cooja && echo "COOJA setup ready"'
```

### Suggested scenarios
| Scenario | Nodes | Packet loss | Payload | Notes |
|----------|-------|-------------|---------|-------|
| s0-n10-p0 | 10 | 0% | 64/128/2272 B | baseline |
| s0-n25-p0 | 25 | 0% | 64/128/2272 B | scaling |
| s0-n50-p0 | 50 | 0% | 64/128/2272 B | scaling |
| s0-n100-p0 | 100 | 0% | 64/128/2272 B | largest |
| s1-n50-p5 | 50 | 5% | per workload | lossy |
| s1-n50-p20 | 50 | 20% | per workload | lossy |

## Data collection
COOJA logs and energest traces are written to `cooja/logs/`. Parse these to
produce CSVs:
- `cooja/results/energy_per_node.csv` — mean energy per node by scenario
- `cooja/results/packets.csv` — PDR, retransmissions
- `cooja/results/crosscheck_analytical_vs_cooja.csv` — sanity check against
  analytical model in `simulation_benchmarks.py`

## Cross-checking against analytical model
The analytical model (canonical) in `simulation_benchmarks.py` treats
endpoint energy as:
```
E_device = (t_comp * P_CPU * factor + (bytes*8/1e6) * P_TX) * 1000 [mJ/device]
```
with `factor=0.1` for gateway-mediated (QKD-Assisted/Hybrid QHSG) per the
reconciliation. COOJA energest measurements provide time/RTIMER counts; map
to energy using platform-specific current profiles (e.g. CC2538/STM32W or
generic Sky). Document the chosen motetype and power profile in `cooja/README.md`
along with any deviations.

## Reproducibility
- `cooja/config/` contains `.csc` COOJA simulation configuration templates.
- `cooja/apps/` contains the 6LoWPAN/UDP/RPL application skeleton (payload
  sizes 64/128/2272 B as specified).
- `cooja/scripts/` contains parsers (`parse_energest.py`, `parse_cooja.py`)
  to extract consistent CSVs.
- Do not commit large binary logs; commit only configs, scripts, and
  processed CSVs (≤ reasonable size). 

**Status:** scaffolding only (Phase 3 in progress). Actual `.csc` runs may
require GUI/X11 or headless mode (`COOJA_HEADLESS=1`); no simulations executed
here due to environment constraints.
