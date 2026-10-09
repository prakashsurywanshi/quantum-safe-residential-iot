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
- Reduces endpoint key-management energy by **94.6%** relative to direct PQC.
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
| `data/Table_Energy_Results.csv` | Result table from the baseline run |
| `custom_results/Table_Energy_Results.csv` | Result table from a custom-parameter run |
| `figures/` | Generated scalability and workload-efficiency figures (PNG + PDF) |
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

Test custom hardware, transceiver, and network-scale parameters:

```bash
python simulation_benchmarks.py \
  --bitrate 250000 \
  --p_cpu 0.150 \
  --p_tx 0.280 \
  --scales 10 50 100 200 500 1000 \
  --outdir custom_results/
```

## Command-line reference

| Flag | Default | Description |
|------|---------|-------------|
| `--bitrate` | `250000` | Wireless bitrate in bps |
| `--p_cpu` | `0.132` | MCU CPU active power in Watts |
| `--p_tx` | `0.250` | Transceiver TX power in Watts |
| `--p_rx` | `0.180` | Transceiver RX power in Watts *(parsed but reserved/unused in the current energy model)* |
| `--scales` | `10 25 50 100 250 500` | List of fleet sizes `N` |
| `--outdir` | `data` | Output directory for the CSV |

For advanced parameters not exposed as flags (per-scheme compute time and payload, 6LoWPAN fragment sizes, per-frame overhead, workload volumes, and the streaming baseline), see the "Testing other parameters" section below.

## Outputs

- `Table_Energy_Results.csv` in `--outdir`.
- `Fig_Energy_Scalability.{png,pdf}` — endpoint refresh energy vs. fleet size `N` (manuscript Figure 2).
- `Fig_Energy_Per_MB.{png,pdf}` — workload-normalized energy efficiency η_E (manuscript Figure 3), computed at `N = 100`.

> **Caveat:** figures are always written to `<outdir>/../figures`. Two runs sharing an output parent will overwrite each other's figure files (the CSV in each `--outdir` is preserved).

## For reviewers

1. Install dependencies (see [Requirements](#requirements)).
2. Run `python simulation_benchmarks.py`.
3. Confirm `data/Table_Energy_Results.csv` is generated, then compare against Table 2 and Figures 2–3 of the manuscript.

The default run reproduces the qualitative ordering and the reported energy trends (PQC-Only incurs a large fragmentation/transmission penalty; the proposed Hybrid QHSG tracks QKD-Assisted at a fraction of the PQC cost). Exact numeric settings, calibration constants, and known differences between the script, the notebooks, and the manuscript table are documented in [`PROJECT_NOTES.md`](PROJECT_NOTES.md).

### Testing other parameters

Only six flags are exposed by the CLI. To change the cryptographic benchmarks, fragmentation model, workload volumes, or streaming baseline, edit the corresponding constants in `simulation_benchmarks.py`:

| Constant | Location | Purpose |
|----------|----------|---------|
| `params` (`t_comp`, `bytes`) | `simulation_benchmarks.py:31-36` | Per-scheme compute time and payload |
| `s_first`, `s_sub` | `simulation_benchmarks.py:19-20` | 6LoWPAN fragment sizes (105 / 111 bytes) |
| per-fragment overhead `0.0005` | `simulation_benchmarks.py:44` | MAC preamble / inter-frame spacing per fragment |
| `workloads`, `base_stream_mj = workloads * 12.0` | `simulation_benchmarks.py:79-80` | Workload-normalized efficiency inputs |

## Notebooks

The notebooks contain the same model expressed for Google Colab, plus manuscript figure styling and (in the `Copy of ...` variant) the matplotlib architecture diagrams. They were used for exploratory analysis; the standalone `simulation_benchmarks.py` is the canonical, reproducible entry point.

## Status

Under review at *Sustainable Computing: Informatics and Systems* (Elsevier). Manuscript No. SUSCOM-D-26-04026. Citation details and a `CITATION.cff` will be added upon acceptance/publication.

## License

Released under the [MIT License](LICENSE).

## Contact

**Prakash Suryawanshi**
Sinhgad Institute of Technology, Lonavala — Founder & Director, Qodeigence Infocircle Private Limited
Email: prakashsuryawanshi1@live.com
