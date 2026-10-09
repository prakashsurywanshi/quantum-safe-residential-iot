# PROJECT_NOTES — Technical & Reproducibility Notes

Companion notes for the simulation artifact of:

> **A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT**
> Prakash Suryawanshi — Manuscript No. **SUSCOM-D-26-04026**
> *Sustainable Computing: Informatics and Systems* (Elsevier), VSI: Sustainable Quantum Computing
> Repository: https://github.com/prakashsurywanshi/quantum-safe-residential-iot

These notes describe what the code computes, how to reproduce the results, and known differences between the code, the notebooks, and the manuscript. They are intended for reviewers and readers who want to verify the results or test their own parameters.

---

## 1. Purpose and scope

This artifact is an **analytical energy model**, not a packet-level network simulator and not a cryptographic implementation. It computes the per-session security energy of four key-establishment paradigms on constrained IoT endpoints using benchmark-calibrated constants, then aggregates over fleet size `N` and over protected application workload.

**What is modeled:** MCU compute energy, radio transmission energy, 6LoWPAN/IEEE 802.15.4 packet fragmentation overhead, and fleet-scale aggregation.

**What is NOT modeled:** actual ML-KEM/ECDH/AES execution, QKD protocol operation, packet-loss/retransmission dynamics, queuing, or real radio hardware. Battery lifetime and adaptive-refresh behavior are described mathematically in the manuscript but are not implemented as dynamic time-series in the code.

---

## 2. System architecture

Four operational domains (manuscript §5):

1. **IoT Leaf Endpoint Domain** — constrained sensors (PIR, temperature, environmental), actuators (smart locks), appliances, and multimedia devices (surveillance cameras) on ARM Cortex-M-class MCUs.
2. **Quantum-Safe Home Security Gateway (QHSG)** — mains-powered edge router with multi-core processing, crypto accelerators, and dual interfaces (local low-power wireless + wide-area fiber/broadband).
3. **Quantum Access Infrastructure Domain** — metro/ISP optical QKD distribution loops delivering symmetric key streams to the QHSG.
4. **Cloud and External Services Domain** — vendor platforms, encrypted archives, and remote mobile clients.

**Design principle:** concentrate bandwidth-heavy post-quantum handshakes and optical quantum-entropy negotiation at the gateway, and distribute only lightweight symmetric session keys to constrained endpoints.

### Security plane vs. data plane

- **Security plane (gateway):** device attestation, PQC key encapsulation, QKD key consumption, session-key rotation; shields the low-rate wireless subnet from public-key transmission overhead.
- **Data plane (endpoints):** telemetry, actuation, and video secured with hardware-accelerated symmetric primitives (AES-256-GCM or ChaCha20-Poly1305).

---

## 3. Hybrid key lifecycle (manuscript §8)

Let `Kq ∈ {0,1}^256` be QKD-derived key material and `Kp ∈ {0,1}^256` the ML-KEM-768 shared secret.

```
PRK = HMAC-SHA256(Salt, Kq || Kp)              (1)
Ks  = HKDF-Expand(PRK, C, L)                    (2)
C   = DevID || QHSG_ID || SeqNum || Version     (3)
Ci, Ti = AEAD_Ks(Pi, Ni, Ai)                    (4)
```

with output length `L = 32` bytes; `Ni` is a monotonic 96-bit nonce and `Ti` a 128-bit tag. If the QKD link degrades, the gateway sets `Kq = 0^256` and falls back to `Kp`.

---

## 4. Security–sustainability energy model (manuscript §9)

Total security energy over an observation period:

```
E_system = Σ_{i=1..N} E_end,i + E_gw + E_comm + E_qkd      (5)

E_end,i  = P_CPU · T_comp,i + P_TX · T_tx,i + P_RX · T_rx,i  (6)
E_comm   = Σ_m (N_frag,m · E_frame + E_oh)                  (7)
```

6LoWPAN fragmentation on IEEE 802.15.4 (physical MTU 127 bytes), with payload `Sm` bytes:

```
N_frag,m = 1 + ceil( max(0, Sm − S_first) / S_sub )          (8)
```

where `S_first ≈ 105` bytes and `S_sub ≈ 111` bytes reflect mesh-header overheads.

Normalized energy efficiency per protected data unit:

```
η_E = E_system / D_protected   [mJ/MB]                       (9)
```

### Adaptive key-refresh policy (manuscript §10)

```
Tr = min( V_max / R_data ,  T_base · (E_rem / E_initial) / (α·Rd + β·Sc) )   (10)
```

`V_max` is the nonce-reuse data threshold, `R_data` the active bitrate, `E_rem/E_initial` the residual battery fraction, `Rd ∈ [0.1, 1.0]` a device vulnerability score, and `Sc ∈ {1,2}` environmental occupancy.

---

## 5. Parameters and reference results

### Table 1 — Cryptographic parameters and leaf-node baselines

| Configuration | T_comp | Payload | 6LoWPAN fragments | Security basis |
|---------------|--------|---------|-------------------|----------------|
| Classical (ECDH) | 15.0 ms | 128 B | 2 | Computational (DLP) |
| PQC (ML-KEM-768) | 3.5 ms | 2272 B | 21 | Computational (lattice) |
| QKD-Assisted | 0.8 ms | 64 B | 1 | Physical (quantum) |
| Hybrid QHSG (proposed) | 0.9 ms | 64 B | 1 | Hybrid (PQC + QKD) |

Calibration: ARM Cortex-M4 @ 168 MHz, `P_CPU = 132 mW` (3.3 V × 40 mA), IEEE 802.15.4 transceiver `P_TX = 250 mW`, `P_RX = 180 mW`.

### Table 2 — Cumulative endpoint key-refresh energy across fleet scales (manuscript)

| Scale (N) | Classical (mJ) | PQC-Only (mJ) | QKD-Assisted (mJ) | Hybrid QHSG (mJ) |
|-----------|----------------|---------------|-------------------|------------------|
| 10 | 22.36 | 50.06 | 1.39 | 2.69 |
| 25 | 55.90 | 125.15 | 3.46 | 6.73 |
| 50 | 111.80 | 250.30 | 6.93 | 13.45 |
| 100 | 223.60 | 500.60 | 13.86 | 26.90 |
| 250 | 559.00 | 1251.50 | 34.64 | 67.25 |
| 500 | 1118.00 | 2503.00 | 69.28 | 134.50 |

Headline comparisons: direct ML-KEM-768 on leaf endpoints = **+123.9%** energy vs. classical ECDH; proposed QHSG = **−94.6%** vs. direct PQC and **−88.0%** vs. classical ECDH. At 1000 MB the workload-normalized efficiency converges to ≈ 12.03 mJ/MB as handshake cost is amortized.

---

## 6. Code map

### `simulation_benchmarks.py` (canonical entry point)

| Lines | Function / block | Role |
|-------|------------------|------|
| 7–30 | CLI args + `calc_fragments()` | Flag definitions; 6LoWPAN fragment count (`105`/`111` byte thresholds) |
| 31–44 | `run_simulation()` setup | Output dirs; `params` (Table 1) and `gateway_mediated` scheme set |
| 46–55 | `calc_energy_endpoint()` | Compute (+ gateway factor) + TX (+ optional per-fragment overhead) energy |
| 57–70 | `results` / DataFrame | Fleet aggregation, 2-decimal rounding, `data/Table_Energy_Results.csv` |
| 74–88 | Figure 1 block | Scalability plot |
| 90–... | Figure 2 block | Workload-normalized efficiency, at the `N = 100` index |

### Notebooks

| Notebook | Notes |
|----------|-------|
| `Quantum_Safe_IoT_Simulation.ipynb` | 2 cells; Colab badge target; writes figures to the working directory |
| `A_Sustainable_Hybrid_QKD–PQC_..._IoT_.ipynb` | Serif publication styling; writes to `paper_outputs/`; auto-downloads in Colab |
| `Copy of A Sustainable Hybrid ... .ipynb` | As above, plus two matplotlib architecture-diagram cells |

All three share an identical first code cell (the core energy model, `BITRATE = 1e6`, no fragmentation-overhead term, gateway ×0.1 compute factor).

---

## 7. Reproduction steps

```bash
# Environment (avoid a path containing ':' — venv refuses such paths)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Baseline
python simulation_benchmarks.py

# Custom parameters (README example)
python simulation_benchmarks.py \
  --bitrate 250000 --p_cpu 0.150 --p_tx 0.280 \
  --scales 10 50 100 200 500 1000 --outdir custom_results/
```

Environment used for the committed results: Python 3.12, numpy 2.5.3, pandas 3.0.6, matplotlib 3.11.2.

---

## 8. Known discrepancies and caveats

The script now reproduces the manuscript's Table 2 exactly for the Classical, PQC-Only, and QKD-Assisted rows, and for the corrected Hybrid row (see column 10 below). Remaining items:

| # | Item | Script (`simulation_benchmarks.py`) | Notebook | Manuscript / status |
|---|------|-------------------------------------|----------|---------------------|
| 1 | Default bitrate | `1e6` bps (was `250000`) | `1e6` bps | **Resolved** — 1 Mbps adopted as canonical; manuscript §14 text corrected from "250 kbps" |
| 2 | Per-fragment overhead | Opt-in via `--frag-overhead` (default off; previously always on) | Not modeled | **Resolved** — excluded from the canonical model, matching Table 2 |
| 3 | Gateway compute factor | `--gateway-factor 0.1` for QKD/Hybrid (`:48-49`); previously none | ×0.1 for gateway-mediated | **Resolved** — script and notebook now agree |
| 4 | Hybrid payload | 64 B (`:41`) | 2272 + 64 = 2336 B | Script follows Table 1 (64 B); notebook is exploratory and not canonical |
| 5 | Hybrid `t_comp` | 0.9 ms | 4.2 ms | Script follows Table 1 (0.9 ms) |
| 6 | Legacy row values | Old default run (250 kbps + overhead) reported Classical 325.40 mJ, PQC 2126.30 mJ @ N=100 | — | Superseded; recreated with `--bitrate 250000 --frag-overhead` only for historical comparison |
| 7 | Hybrid Table-2 value | **13.99 mJ @ N=100** (reproducible) | — | Original draft printed 26.90 mJ, which **cannot be reconstructed** from any clean decomposition of Table 1 parameters; corrected to the reproducible value in the revision |

**Reconciliation note (item 7):** the per-device curve that reproduces Table 2 for Classical (2.236 mJ), PQC-Only (5.006 mJ), and QKD-Assisted (0.13856 mJ) is

```
E_device(scheme) = ( t_comp · P_CPU · factor + (bytes · 8 / 1e6) · P_TX ) × 1000   [mJ/device]
factor = 0.1 for QKD-Assisted and Hybrid QHSG, else 1.0
```

with Table 1 parameters (Classical 15 ms/128 B, PQC 3.5 ms/2272 B, QKD 0.8 ms/64 B, Hybrid 0.9 ms/64 B). This yields Hybrid = 0.13988 mJ/device → **13.99 mJ @ N=100**. Headline percentages under the reconciled model: PQC-Only vs. Classical **+123.9%** (unchanged); Hybrid QHSG vs. PQC-Only **−97.2%** and vs. Classical **−93.7%** (slightly stronger than the draft's 94.6%/88.0%, which were anchored to the unreproducible 26.90 mJ value). The revision must carry these corrected figures.

**Other caveats:**

- `--p_rx` is parsed but never used in the endpoint energy computation.
- The committed `figures/` reflect the current (canonical) baseline run; because figures are written to `<outdir>/../figures`, any later run sharing the parent overwrites them (the CSV in each `--outdir` is preserved).
- `venv` cannot be created inside a directory path containing `:`; create the environment elsewhere.

---

## 9. Testing other parameters

Vary the exposed flags directly (`--bitrate`, `--p_cpu`, `--p_tx`, `--p_rx`, `--scales`, `--outdir`, `--gateway-factor`, `--frag-overhead`, `--frag-overhead-cost`). To change the hardcoded benchmarks, edit:

| Constant | Location |
|----------|----------|
| `params` (`t_comp`, `bytes`) | `simulation_benchmarks.py:37-41` |
| `gateway_mediated` | `simulation_benchmarks.py:44` |
| `s_first`, `s_sub` | `simulation_benchmarks.py:25-26` |
| per-fragment overhead | `simulation_benchmarks.py:52-54` (with `--frag-overhead`) |
| `workloads`, `base_stream_mj` (`×12.0`) | `simulation_benchmarks.py:91-92` |

The artifact intentionally keeps the exposed CLI surface small so the canonical defaults are the paper-accurate model; parameterizing the remaining constants (e.g., `--scheme-tcomp`, `--scheme-bytes`) is a natural future enhancement that was left out of the reviewed snapshot to avoid changing default results.

---

## 10. Links

- Repository: https://github.com/prakashsurywanshi/quantum-safe-residential-iot
- Journal: *Sustainable Computing: Informatics and Systems* — https://www.sciencedirect.com/journal/sustainable-computing-informatics-and-systems
- Manuscript No.: SUSCOM-D-26-04026 (under review)
