"""Sensitivity and uncertainty analysis for the QHSG endpoint energy model.

Samples the platform parameters over their plausible physical ranges and
reports the distribution of the headline energy metrics at N = 100.

Parameters and ranges
---------------------
P_CPU : Uniform(0.066, 0.198)  W   (Cortex-M4 active, 0.5x-1.5x nominal 132 mW)
P_TX  : Uniform(0.010, 0.100)  W   (IEEE 802.15.4 / sub-GHz TX, 10-100 mW)
P_RX  : Uniform(0.010, 0.100)  W
t_comp: Lognormal, sigma = 0.20 (20% spread on measured cycle counts)
N     : fixed at 100 endpoints
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import simulation_benchmarks as sim

RNG = np.random.default_rng(20260114)
N_SAMPLES = 20000
N_ENDPOINTS = 100


def endpoint_energy(p_cpu, p_tx, p_rx, t_comp, bytes_):
    n_frag = sim.calc_fragments(bytes_)
    t_data = sim.on_air_bytes(bytes_) * 8.0 / sim.BITRATE
    t_ack = n_frag * sim.ACK_BYTES * 8.0 / sim.BITRATE
    return (p_cpu * t_comp + p_tx * t_data + p_rx * t_ack) * 1000.0


def metrics(p_cpu, p_tx, p_rx, jitter):
    cl = endpoint_energy(p_cpu, p_tx, p_rx, sim.PARAMS['Classical']['t_comp'] * jitter['Classical'],
                         sim.PARAMS['Classical']['bytes'])
    pq = endpoint_energy(p_cpu, p_tx, p_rx, sim.PARAMS['PQC-Only']['t_comp'] * jitter['PQC-Only'],
                         sim.PARAMS['PQC-Only']['bytes'])
    hy = endpoint_energy(p_cpu, p_tx, p_rx, sim.PARAMS['Hybrid QHSG']['t_comp'] * jitter['Hybrid QHSG'],
                         sim.PARAMS['Hybrid QHSG']['bytes'])
    return (pq / cl - 1) * 100, (1 - hy / pq) * 100, (1 - hy / cl) * 100


def main():
    outdir = "data"
    figdir = "figures"
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(figdir, exist_ok=True)

    p_cpu = sim.P_CPU * RNG.lognormal(0.0, 0.20, N_SAMPLES)
    p_tx = sim.P_TX * RNG.lognormal(0.0, 0.35, N_SAMPLES)
    p_rx = sim.P_RX * RNG.lognormal(0.0, 0.35, N_SAMPLES)
    # common multiplicative spread on the measured cycle-count-derived times
    common = RNG.lognormal(0.0, 0.15, N_SAMPLES)
    jit = {k: common for k in sim.PARAMS}

    a = np.array([metrics(p_cpu[i], p_tx[i], p_rx[i], {k: jit[k][i] for k in sim.PARAMS})
                  for i in range(N_SAMPLES)])

    labels = ['PQC vs Classical (+%)', 'Hybrid vs PQC (-%)', 'Hybrid vs Classical (-%)']
    rows = []
    for j, lab in enumerate(labels):
        col = a[:, j]
        rows.append({'metric': lab, 'median': round(np.median(col), 2),
                     'p05': round(np.percentile(col, 5), 2),
                     'p95': round(np.percentile(col, 95), 2)})
    tab = pd.DataFrame(rows)
    tab.to_csv(os.path.join(outdir, "sensitivity_results.csv"), index=False)
    print(tab.to_string(index=False))

    summary = {r['metric']: {'median': r['median'], 'p05': r['p05'], 'p95': r['p95']} for r in rows}
    with open(os.path.join(outdir, "sensitivity_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), dpi=300)
    for ax, j, lab in zip(axes, range(3), labels):
        ax.hist(a[:, j], bins=40, color='#9467bd', alpha=0.85)
        ax.axvline(np.mean(a[:, j]), color='k', lw=1.2)
        ax.set_title(lab, fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel('Samples')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "Fig_Sensitivity.png"), dpi=300)
    plt.savefig(os.path.join(figdir, "Fig_Sensitivity.pdf"))
    plt.close()
    print("[OK] wrote figures/Fig_Sensitivity.png and data/sensitivity_results.csv")


if __name__ == "__main__":
    main()
