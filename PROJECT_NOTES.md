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
| 7–15 | `parse_args()` | CLI definition (6 flags) |
| 18–23 | `calc_fragments()` | 6LoWPAN fragment count (`105`/`111` byte thresholds) |
| 25–60 | `run_simulation()` | Energy model, CSV export |
| 31–36 | `params` dict | Per-scheme `t_comp` and `bytes` |
| 38–45 | `calc_energy_endpoint()` | Compute + TX + per-fragment overhead energy |
| 49–58 | `results` / DataFrame | Fleet aggregation and `data/Table_Energy_Results.csv` |
| 62–76 | Figure 1 block | Scalability plot |
| 78–103 | Figure 2 block | Workload-normalized efficiency, at the `N = 100` index |

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

The script, the notebooks, and the manuscript are **not numerically identical**. Reviewers should be aware of the following.

| # | Item | Script (`simulation_benchmarks.py`) | Notebook | Manuscript |
|---|------|-------------------------------------|----------|------------|
| 1 | Default bitrate | `250000` bps | `1e6` bps | Text says 250 kbps, but Table 2 numbers correspond to 1 Mbps |
| 2 | Per-fragment overhead | Adds `n_frag × 0.0005 × P_TX` (`:44`) | Not modeled | Term absent from Table 2 |
| 3 | Gateway compute factor | QKD/Hybrid use small `t_comp` as-is (no ×0.1) | Multiplies compute by ×0.1 for gateway-mediated schemes | Matches notebook for QKD/Hybrid |
| 4 | Hybrid payload | 64 B (`:34-35`) | 2272 + 64 = 2336 B | Table 1: 64 B |
| 5 | Hybrid `t_comp` | 0.9 ms | 4.2 ms | Table 1: 0.9 ms |
| 6 | Figures output path | `<outdir>/../figures` — runs share and overwrite figure files | Written to CWD / `paper_outputs/` | — |

**Consequence:** the default script run does **not** reproduce manuscript Table 2 exactly. For example, at `N = 100` the committed baseline CSV reports Classical 325.40 mJ, PQC-Only 2126.30 mJ, QKD-Assisted 74.26 mJ, and Hybrid QHSG 75.58 mJ. Reconstructing Table 2 requires 1 Mbps and removal of the per-fragment overhead term, plus the gateway compute factor. The manuscript's Hybrid value (0.269 mJ/device) does not precisely match any committed configuration; this should be reconciled before any camera-ready/artifact-release update.

**Other caveats:**

- `--p_rx` is parsed but never used in the energy computation (line 6 of the CLI is effectively dead).
- The committed `figures/` currently reflect the **custom-parameter** run (the second invocation overwrote the baseline figures because of caveat #6); `data/` holds the baseline CSV and `custom_results/` the custom CSV.
- `venv` cannot be created inside a directory path containing `:` (the workspace path does); create the environment elsewhere.

---

## 9. Testing other parameters

Vary the exposed flags directly (`--bitrate`, `--p_cpu`, `--p_tx`, `--p_rx`, `--scales`, `--outdir`). To change the hardcoded benchmarks, edit:

| Constant | Location |
|----------|----------|
| `params` (`t_comp`, `bytes`) | `simulation_benchmarks.py:31-36` |
| `s_first`, `s_sub` | `simulation_benchmarks.py:19-20` |
| per-fragment overhead `0.0005` | `simulation_benchmarks.py:44` |
| `workloads`, `base_stream_mj` (`×12.0`) | `simulation_benchmarks.py:79-80` |

The current artifact intentionally exposes only these six CLI parameters; parameterizing the remaining constants (e.g., `--scheme-tcomp`, `--scheme-bytes`, `--frag-first`, `--stream-mj-per-mb`) is a natural future enhancement but was left out of the reviewed snapshot to avoid changing default results.

---

## 10. Links

- Repository: https://github.com/prakashsurywanshi/quantum-safe-residential-iot
- Journal: *Sustainable Computing: Informatics and Systems* — https://www.sciencedirect.com/journal/sustainable-computing-informatics-and-systems
- Manuscript No.: SUSCOM-D-26-04026 (under review)
