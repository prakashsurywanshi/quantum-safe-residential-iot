# A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/prakashsurywanshi/quantum-safe-residential-iot/blob/main/Quantum_Safe_IoT_Simulation.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Under%20Review-orange.svg)](#status)

Simulation artifact accompanying the manuscript **"A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT"** (Manuscript No. **SUSCOM-D-26-04026**, under review at *Sustainable Computing: Informatics and Systems*, Elsevier).

This repository contains the benchmark-calibrated energy simulation, the parameterized command-line runner, the raw result tables, and the figure-generation routines used to evaluate four cryptographic configurations for residential smart-home networks.

> **Status:** Under review (single-blind peer review). The repository is public so reviewers and readers can reproduce the reported results and test their own parameters.

---

## Overview

The simulation quantifies the **security energy overhead** of key establishment on constrained ARM Cortex-M4 / ESP32-class IoT endpoints across four configurations:

1. **Classical Baseline** — Ephemeral ECDH (Curve25519) + AES-256-GCM.
2. **PQC-Only (Direct Leaf Node)** — Leaf-terminated ML-KEM-768 (FIPS 203) over 6LoWPAN/IEEE 802.15.4.
3. **QKD-Assisted** — Optical QKD buffer pool + AES-256-GCM.
4. **Hybrid QHSG (Proposed)** — Gateway-mediated HKDF fusion of ML-KEM-768 and QKD key pools, distributing a 64-byte symmetric session ticket to the leaf node.

The endpoint energy model combines MCU compute energy, radio transmission energy, and 6LoWPAN/IEEE 802.15.4 fragmentation overhead, then aggregates over fleet sizes `N`.

## Highlights

- Proposes a sustainable hybrid QKD–PQC framework for residential IoT.
- Edge gateway offloads lattice PQC handshakes from leaf nodes.
- Models 6LoWPAN packet fragmentation energy penalties on low-power radios.
- Reduces endpoint key-management energy by **96.8%** relative to direct PQC.
- Open-source simulation repository for empirical verification.

## Architecture at a glance

Constrained leaf endpoints (sensors, actuators, appliances, cameras) communicate over a low-power wireless link with a mains-powered **Quantum-Safe Home Security Gateway (QHSG)**. The QHSG terminates the bandwidth-heavy ML-KEM handshake, ingests last-mile optical QKD entropy, and delivers only compact symmetric session keys to endpoints over the local link. The complete architecture and session-key lifecycle are illustrated as Figure 1 of the manuscript.

## Repository structure

| Path | Description |
|------|-------------|
| `simulation_benchmarks.py` | Parameterized CLI simulation; generates the result table and figures |
| `requirements.txt` | Python dependencies (numpy, pandas, matplotlib) |
| `Quantum_Safe_IoT_Simulation.ipynb` | Original Colab notebook (linked by the badge above) |
| `A_Sustainable_Hybrid_QKD–PQC_..._IoT_.ipynb` | Polished notebook variant; writes to `paper_outputs/` |
| `Copy of A Sustainable Hybrid ... .ipynb` | Notebook variant that additionally draws the architecture diagrams |
| `data/Table_Energy_Results.csv` | Result table from the baseline run (reproduces manuscript Table 2) |
| `custom_results/Table_Energy_Results.csv` | Result table from a custom-parameter run |
| `figures/` | Generated scalability and workload-efficiency figures (PNG + PDF) |
| `benchmarks/` | Cycle-level crypto calibration data (pqm4) used in the model |
| `proverif/` | Formal security verification models and results |
| `cooja/` | Contiki-NG/COOJA fragmentation validation (executed headless; see `cooja/README.md`) |
| `PROJECT_NOTES.md` | Detailed technical and reproducibility notes |

## Requirements

- Python 3.9+
- `numpy`, `pandas`, `matplotlib` (see `requirements.txt`)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `venv` refuses to create an environment in a directory whose path contains a colon (`:`) or other PATH-separator characters. If your project path contains `:`, create the virtual environment elsewhere and use its interpreter directly, e.g. `python -m venv /tmp/qsiot-venv`.

## Quick start

Run the baseline simulation exactly as reported:

```bash
python simulation_benchmarks.py
```

This writes `data/Table_Energy_Results.csv` and figures under `figures/`.

Regenerate the sensitivity analysis and (optionally) the COOJA fragmentation validation:

```bash
python sensitivity_analysis.py
CONTIKI=/path/to/contiki-ng GRADLE_HOME=/path/to/.gradle \
  bash cooja/scripts/run_fragmentation.sh
```

## Command-line reference

| Flag | Default | Description |
|------|---------|-------------|
| `--scales` | `10 25 50 100 250 500` | List of fleet sizes `N` |
| `--outdir` | `data` | Output directory for the CSV and `summary.json` |
| `--figdir` | `figures` | Output directory for the figures |

Platform constants (`P_CPU`, `P_TX`, `P_RX`, `BITRATE`, and the fragmentation
geometry) are fixed in `simulation_benchmarks.py` at their externally grounded
values; see "Testing other parameters" to change them.

For advanced parameters not exposed as flags (per-scheme compute time and payload, 6LoWPAN fragment sizes, workload volumes, and the streaming baseline), see the "Testing other parameters" section below.

## Outputs

- `Table_Energy_Results.csv` in `--outdir`.
- `Fig_Energy_Scalability.{png,pdf}` — endpoint refresh energy vs. fleet size `N` (manuscript Figure 2).
- `Fig_Energy_Per_MB.{png,pdf}` — workload-normalized energy efficiency η_E (manuscript Figure 3), computed at `N = 100`.

> **Caveat:** figures are always written to `<outdir>/../figures`. Two runs sharing an output parent will overwrite each other's figure files (the CSV in each `--outdir` is preserved).

## For reviewers

1. Install dependencies (see [Requirements](#requirements)).
2. Run `python simulation_benchmarks.py`.
3. Confirm `data/Table_Energy_Results.csv` is generated, then compare against Table 2 and Figures 2–3 of the manuscript.

The default run reproduces the exact per-fleet values reported in Table 2 (e.g. Classical 157.63 mJ, PQC-Only 328.46 mJ, Hybrid QHSG 10.52 mJ at `N = 100`). Headline metrics: PQC vs. Classical **+108.4%**, Hybrid vs. PQC **−96.8%**, Hybrid vs. Classical **−93.3%**. The 6LoWPAN fragmentation penalty behind the PQC overhead is validated by the executed COOJA runs in [`cooja/`](cooja/) (the 2272-byte PQC handshake costs exactly 24 frames), and the security properties are machine-checked in [`proverif/`](proverif/).

All constants are externally grounded: datasheet radio currents, published Cortex-M4 cycle counts, and COOJA-measured 6LoWPAN fragmentation. Exact settings, calibration constants, and the model derivation are documented in [`PROJECT_NOTES.md`](PROJECT_NOTES.md).

### Testing other parameters

Only the CLI flags above are exposed for the runtime parameters. To change the cryptographic benchmarks, fragmentation model, workload volumes, or streaming baseline, edit the corresponding constants in `simulation_benchmarks.py`:

| Constant | Location | Purpose |
|----------|----------|---------|
| `P_CPU`, `P_TX`, `P_RX`, `BITRATE`, `ACK_BYTES` | `simulation_benchmarks.py:37-41` | Grounded platform constants |
| `MAC_MAX_PAYLOAD`, `COMP_HDR`, `FRAGN_DATA`, … | `simulation_benchmarks.py:44-49` | COOJA-validated 6LoWPAN fragmentation geometry |
| `PARAMS` (`t_comp`, `bytes`) | `simulation_benchmarks.py:52-57` | Per-scheme compute time and payload (Table 1) |

## Notebooks

The notebooks contain the same model expressed for Google Colab, plus manuscript figure styling and (in the `Copy of ...` variant) the matplotlib architecture diagrams. They were used for exploratory analysis; the standalone `simulation_benchmarks.py` is the canonical, reproducible entry point.

## Status

Under review at *Sustainable Computing: Informatics and Systems* (Elsevier). Manuscript No. SUSCOM-D-26-04026. Citation details and a `CITATION.cff` will be added upon acceptance/publication.

## License

Released under the [MIT License](LICENSE).

## Contact

**Prakash Suryawanshi**
Sinhgad Institute of Technology, Lonavala — Founder & Director, Qodeigence Infocircle Private Limited
Email: prakashsurywanshi1@live.com
