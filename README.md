# A Sustainable Hybrid QKD–PQC Security Architecture for Quantum-Resilient Residential IoT

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/blob/main/Quantum_Safe_IoT_Simulation.ipynb)
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

## 🚀 Quick Start in Google Colab (One-Click)

Click the **Open in Colab** badge above to launch the simulation in an interactive notebook without installing any local packages.

---

## 💻 Local Installation & Usage

### 1. Prerequisites & Dependencies
Clone the repository and install required packages:
```bash
git clone [https://github.com/](https://github.com/)<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
cd <YOUR_REPO_NAME>
pip install -r requirements.txt
