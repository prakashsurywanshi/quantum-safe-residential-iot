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

6LoWPAN fragmentation on IEEE 802.15.4, with payload `Sm` bytes (COOJA-validated; see `cooja/`):

```
N_frag,m = ceil( (Sm + C_hdr) / S_sub )                      (8)
```

where the compressed IPv6/UDP header is `C_hdr = 12` bytes and the usable payload per
fragment is `S_sub = 96` bytes (`(104 − 5) & ~7`). These are measured values from the
Contiki-NG 6LoWPAN implementation, confirmed to reproduce the COOJA frame counts exactly.

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
| Classical (ECDH) | 10.81 ms | 128 B | 2 | Computational (DLP) |
| PQC (ML-KEM-768) | 8.04 ms | 2272 B | 24 | Computational (lattice) |
| QKD-Assisted | 0.22 ms | 64 B | 1 | Physical (quantum) |
| Hybrid QHSG (proposed) | 0.22 ms | 64 B | 1 | Hybrid (PQC + QKD) |

Calibration: ARM Cortex-M4F @ 168 MHz, `P_CPU = 132 mW` (3.3 V × 40 mA); IEEE 802.15.4 transceiver `P_TX = 22 mW` (7.3 mA @ 3.0 V), `P_RX = 21 mW` (6.9 mA @ 3.0 V) [TI CC2652R datasheet]; PHY rate 250 kbps. Compute times are measured cycle counts (`benchmarks/`).

### Table 2 — Cumulative endpoint key-refresh energy across fleet scales (manuscript)

| Scale (N) | Classical (mJ) | PQC-Only (mJ) | QKD-Assisted (mJ) | Hybrid QHSG (mJ) |
|-----------|----------------|---------------|-------------------|------------------|
| 10 | 15.76 | 32.85 | 1.05 | 1.05 |
| 25 | 39.41 | 82.11 | 2.63 | 2.63 |
| 50 | 78.82 | 164.23 | 5.26 | 5.26 |
| 100 | 157.63 | 328.46 | 10.52 | 10.52 |
| 250 | 394.08 | 821.14 | 26.31 | 26.31 |
| 500 | 788.15 | 1642.28 | 52.62 | 52.62 |

Endpoint units: Classical 1.5763 mJ, PQC-Only 3.2846 mJ, QKD-Assisted/Hybrid 0.105248 mJ per device.

Headline comparisons: direct ML-KEM-768 on leaf endpoints = **+108.4%** energy vs. classical ECDH; proposed QHSG = **−96.8%** vs. direct PQC and **−93.3%** vs. classical ECDH. The QKD-Assisted and Hybrid rows are identical because both leave the endpoint with only symmetric AEAD. A 20,000-sample Monte-Carlo sensitivity analysis confirms the conclusions hold across the plausible parameter range.

---

---

## 6. Code map

### `simulation_benchmarks.py` (canonical entry point)

| Lines | Function / block | Role |
|-------|------------------|------|
| 1–25 | module docstring | Documents grounded constants and COOJA-validated fragmentation |
| 37–41 | platform constants | `P_CPU`, `P_TX`, `P_RX`, `BITRATE`, `ACK_BYTES` |
| 44–49 | fragmentation constants | `MAC_MAX_PAYLOAD`, `COMP_HDR`, `FRAGN_DATA`, … |
| 52–57 | `PARAMS` | measured `t_comp` and payload per scheme (Table 1) |
| 60–64 | `calc_fragments()` | `ceil((payload+12)/96)`, COOJA-validated |
| 67–74 | `on_air_bytes()` | total 802.15.4 bytes incl. per-frame MAC header |
| 77–83 | `endpoint_energy_mj()` | `P_CPU·t_comp + P_TX·t_data + P_RX·t_ack`, returns (mJ, n_frag) |
| 94–128 | `run()` | fleet aggregation → `data/Table_Energy_Results.csv`, `data/summary.json` |
| 130–144 | scalability figure | `figures/Fig_Energy_Scalability.*` |
| 146–167 | workload-efficiency figure | `figures/Fig_Energy_Per_MB.*` |

### `sensitivity_analysis.py`

20,000-sample Monte-Carlo over log-normal radio powers (20%/35% CV) and a common
15% perturbation on measured compute times, reusing `sim.calc_fragments()` and
`sim.on_air_bytes()`; writes `data/sensitivity_results.csv`,
`data/sensitivity_summary.json`, `figures/Fig_Sensitivity.png`.

### `cooja/`

Headless Contiki-NG/COOJA fragmentation validation; see `cooja/README.md`.

### Notebooks

The Colab notebooks are exploratory and are **not** part of the canonical artifact;
do not use them to reproduce Table 2.

---

## 7. Reproduction steps

```bash
# Environment (avoid a path containing ':' — venv refuses such paths)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Canonical model
python simulation_benchmarks.py --scales 10 25 50 100 250 500

# Sensitivity analysis
python sensitivity_analysis.py

# Cycle calibration
python benchmarks/cycle_calibration.py

# ProVerif (formal verification)
bash proverif/run_all.sh /path/to/proverif

# COOJA fragmentation validation (requires Contiki-NG + Docker)
CONTIKI=/path/to/contiki-ng GRADLE_HOME=/path/to/.gradle \
  bash cooja/scripts/run_fragmentation.sh
```

Environment used for the committed results: Python 3.12, numpy 2.5.3, pandas 3.0.6, matplotlib 3.11.2.

---

## 8. Known caveats

The canonical script reproduces the manuscript's Table 2 and `data/summary.json`
exactly. Caveats:

| # | Item | Status |
|---|------|--------|
| 1 | Energest under COOJA | **Not used** — counters were implausible and did not scale with payload; the validated quantity is the frame/fragment count, combined with datasheet radio constants in the model |
| 2 | Gateway-side energy (`E_gw`, `E_qkd`) | Modelled analytically only; the endpoint model does not simulate the broadband/QKD side |
| 3 | Packet loss / retransmissions | Not simulated; `cooja/` uses an ideal link (success ratios 1.0) |
| 4 | Notebooks | Exploratory Colab notebooks; not part of the canonical artifact |

---

## 9. Testing other parameters

The canonical model exposes only `--scales`, `--outdir`, `--figdir`. To change the
model constants, edit:

| Constant | Location |
|----------|----------|
| `P_CPU`, `P_TX`, `P_RX`, `BITRATE`, `ACK_BYTES` | `simulation_benchmarks.py:37-41` |
| `MAC_MAX_PAYLOAD`, `COMP_HDR`, `FRAGN_DATA` | `simulation_benchmarks.py:44-49` |
| `PARAMS` (`t_comp`, `bytes`) | `simulation_benchmarks.py:52-57` |

Parameterization of schemes via CLI is a natural future enhancement.

---

## 10. Links

- Repository: https://github.com/prakashsurywanshi/quantum-safe-residential-iot
- Journal: *Sustainable Computing: Informatics and Systems* — https://www.sciencedirect.com/journal/sustainable-computing-informatics-and-systems
- Manuscript No.: SUSCOM-D-26-04026 (under review)
