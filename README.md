# A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/prakashsurywanshi/quantum-safe-residential-iot/blob/main/Quantum_Safe_IoT_Simulation.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the simulation source code, empirical baseline datasets, and figure generation routines for the paper:

> **"A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT"**  
> *Author:* Prakash Surywanshi  
> *Submitted to:* Sustainable Computing: Informatics and Systems (Elsevier)

---

## 📌 Overview

This artifact evaluates the energy consumption, communication overhead, and scalability trade-offs of four cryptographic configurations for residential smart home networks:
1. **Classical Baseline:** Ephemeral ECDH (Curve25519) + AES-256-GCM.
2. **PQC-Only (Direct Leaf Node):** Leaf-terminated ML-KEM-768 (FIPS 203) with 6LoWPAN packet fragmentation.
3. **QKD-Assisted:** Optical QKD buffer pool + AES-256-GCM.
4. **Hybrid QHSG (Proposed):** Gateway-mediated HKDF fusion of ML-KEM-768 and QKD key pools + 64-byte symmetric session distribution.

---

## Run Baseline Simulation
To reproduce the exact figures and CSV tables presented in the paper:

python simulation_benchmarks.py


## Experiment with Custom Parameters
The simulation supports custom command-line arguments to test different hardware, transceivers, and network scales:

python simulation_benchmarks.py \
  --bitrate 250000 \
  --p_cpu 0.150 \
  --p_tx 0.280 \
  --scales 10 50 100 200 500 1000 \
  --outdir custom_results/
