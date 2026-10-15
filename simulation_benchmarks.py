"""Grounded endpoint key-refresh energy model for the QHSG architecture.

All constants are anchored to public datasheets / benchmark suites:
  - MCU      : ARM Cortex-M4F @ 168 MHz, active power 132 mW (40 mA @ 3.3 V).
  - Radio    : IEEE 802.15.4 transceiver, TX 22 mW (7.3 mA @ 3.0 V),
               RX 21 mW (6.9 mA @ 3.0 V)  [TI CC2652R datasheet].
  - PHY      : IEEE 802.15.4, 250 kbps, 127-byte PSDU (6LoWPAN fragmentation).
  - Compute  : pqm4 / x25519-cortexm4 measured cycle counts at 168 MHz
               (see benchmarks/cycle_calibration.py).

Endpoint energy per key-refresh cycle:
    E_end = P_CPU * t_comp + P_TX * t_data + P_RX * t_ack
    t_data = on_air_bytes(payload) * 8 / bitrate
    t_ack  = n_frag * ACK_BYTES * 8 / bitrate

Fragmentation is not modelled analytically from first principles but taken from
the Contiki-NG 6LoWPAN implementation and *validated with COOJA* (see
cooja/): for the client mote NETSTACK_MAC.max_payload() = 104 B, giving
96-byte middle fragments and a 12-byte compressed IPv6+UDP header, i.e.

    n_frag = ceil((payload + 12) / 96)

measured to hold exactly for payloads 64, 128, 256, 512, 1024, 1232 and
2272 B (cooja/results/fragmentation_results.csv).
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Grounded platform constants
# ---------------------------------------------------------------------------
P_CPU = 0.132          # W   Cortex-M4F @ 168 MHz active (40 mA @ 3.3 V)
P_TX = 0.022           # W   IEEE 802.15.4 TX (CC2652R, 7.3 mA @ 3.0 V)
P_RX = 0.021           # W   IEEE 802.15.4 RX (CC2652R, 6.9 mA @ 3.0 V)
BITRATE = 250_000      # bps IEEE 802.15.4 PHY
ACK_BYTES = 11         # 802.15.4 MAC ACK on air

# 6LoWPAN fragmentation parameters measured in Contiki-NG (COOJA).
MAC_MAX_PAYLOAD = 104  # NETSTACK_MAC.max_payload() for the client mote
MAC_HDR = 21           # PHY+MAC+FCS header bytes per 802.15.4 frame
FRAG1_HDR = 4          # 6LoWPAN first-fragment header
FRAGN_HDR = 5          # 6LoWPAN subsequent-fragment header
COMP_HDR = 12          # compressed IPv6 + UDP (HcUDP) header
FRAGN_DATA = 96        # (MAC_MAX_PAYLOAD - FRAGN_HDR) & ~7

# Measured compute times (s) at 168 MHz; see benchmarks/calibration_report.csv
PARAMS = {
    'Classical':    {'t_comp': 0.010811, 'bytes': 128,  'label': 'Classical (ECDH)'},
    'PQC-Only':     {'t_comp': 0.008035, 'bytes': 2272, 'label': 'PQC-Only (ML-KEM-768)'},
    'QKD-Assisted': {'t_comp': 0.000224, 'bytes': 64,   'label': 'QKD-Assisted'},
    'Hybrid QHSG':  {'t_comp': 0.000224, 'bytes': 64,   'label': 'Hybrid QHSG (Proposed)'},
}


def calc_fragments(payload_bytes):
    """6LoWPAN fragment count, validated against COOJA (see module docstring)."""
    if payload_bytes <= MAC_MAX_PAYLOAD - COMP_HDR:
        return 1
    return int(np.ceil((payload_bytes + COMP_HDR) / FRAGN_DATA))


def on_air_bytes(payload_bytes):
    """Total 802.15.4 on-air bytes for one datagram (data frames only)."""
    n = calc_fragments(payload_bytes)
    if n == 1:
        sixlowpan = payload_bytes + COMP_HDR
    else:
        sixlowpan = payload_bytes + COMP_HDR + FRAG1_HDR + FRAGN_HDR * (n - 1)
    return sixlowpan + MAC_HDR * n


def endpoint_energy_mj(scheme):
    p = PARAMS[scheme]
    n_frag = calc_fragments(p['bytes'])
    t_data = on_air_bytes(p['bytes']) * 8.0 / BITRATE
    t_ack = n_frag * ACK_BYTES * 8.0 / BITRATE
    e_j = P_CPU * p['t_comp'] + P_TX * t_data + P_RX * t_ack
    return e_j * 1000.0, n_frag


def parse_args():
    ap = argparse.ArgumentParser(description="QHSG grounded energy model")
    ap.add_argument("--scales", nargs="+", type=int, default=[10, 25, 50, 100, 250, 500])
    ap.add_argument("--outdir", type=str, default="data")
    ap.add_argument("--figdir", type=str, default="figures")
    return ap.parse_args()


def run(args):
    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(args.figdir, exist_ok=True)

    units = {}
    frags = {}
    for k in PARAMS:
        units[k], frags[k] = endpoint_energy_mj(k)

    df = pd.DataFrame({'Scale_N': args.scales})
    df['Classical_mJ'] = [n * units['Classical'] for n in args.scales]
    df['PQC_Only_mJ'] = [n * units['PQC-Only'] for n in args.scales]
    df['QKD_Assisted_mJ'] = [n * units['QKD-Assisted'] for n in args.scales]
    df['Hybrid_QHSG_mJ'] = [n * units['Hybrid QHSG'] for n in args.scales]
    for c in ['Classical_mJ', 'PQC_Only_mJ', 'QKD_Assisted_mJ', 'Hybrid_QHSG_mJ']:
        df[c] = df[c].round(2)
    df.to_csv(os.path.join(args.outdir, "Table_Energy_Results.csv"), index=False)

    i100 = args.scales.index(100) if 100 in args.scales else 0
    cl = df['Classical_mJ'].iloc[i100]
    pq = df['PQC_Only_mJ'].iloc[i100]
    hy = df['Hybrid_QHSG_mJ'].iloc[i100]
    summary = {
        'unit_mJ': {k: round(v, 6) for k, v in units.items()},
        'fragments': frags,
        'N100': {'Classical': cl, 'PQC': pq, 'QKD': df['QKD_Assisted_mJ'].iloc[i100], 'Hybrid': hy},
        'pct_PQC_vs_Classical': round((pq / cl - 1) * 100, 2),
        'pct_Hybrid_vs_PQC': round((1 - hy / pq) * 100, 2),
        'pct_Hybrid_vs_Classical': round((1 - hy / cl) * 100, 2),
    }
    with open(os.path.join(args.outdir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(df.to_string(index=False))
    print(json.dumps(summary, indent=2))

    # Figure: scalability
    plt.figure(figsize=(7, 4.5), dpi=300)
    plt.plot(df['Scale_N'], df['Classical_mJ'], 's--', label='Classical (ECDH)', color='#1f77b4', lw=1.5)
    plt.plot(df['Scale_N'], df['PQC_Only_mJ'], '^-.', label='PQC-Only (ML-KEM-768)', color='#d62728', lw=1.5)
    plt.plot(df['Scale_N'], df['QKD_Assisted_mJ'], 'd:', label='QKD-Assisted', color='#2ca02c', lw=1.5)
    plt.plot(df['Scale_N'], df['Hybrid_QHSG_mJ'], 'o-', label='Hybrid QHSG (Proposed)', color='#9467bd', lw=2.0)
    plt.xlabel('Number of IoT Endpoints ($N$)')
    plt.ylabel('Endpoint Refresh Energy (mJ)')
    plt.title('Endpoint Security Energy Overhead across Fleet Scales')
    plt.legend(frameon=True)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(args.figdir, "Fig_Energy_Scalability.png"), dpi=300)
    plt.savefig(os.path.join(args.figdir, "Fig_Energy_Scalability.pdf"))
    plt.close()

    # Figure: workload-normalized *security* overhead per protected MB
    workloads = np.array([50, 100, 200, 500, 1000])
    eta_pqc = pq / workloads
    eta_hybrid = hy / workloads
    eta_qkd = df['QKD_Assisted_mJ'].iloc[i100] / workloads

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    w = 0.25
    x = np.arange(len(workloads))
    ax.bar(x - w, eta_pqc, width=w, label='PQC-Only (Direct)', color='#d62728')
    ax.bar(x, eta_hybrid, width=w, label='Hybrid QHSG (Proposed)', color='#9467bd')
    ax.bar(x + w, eta_qkd, width=w, label='QKD-Assisted', color='#2ca02c')
    ax.set_xlabel('Application Payload Volume (MB)')
    ax.set_ylabel(r'Normalized Energy Efficiency $\eta_E$ (mJ/MB)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{v} MB' for v in workloads])
    ax.legend(frameon=True)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(args.figdir, "Fig_Energy_Per_MB.png"), dpi=300)
    plt.savefig(os.path.join(args.figdir, "Fig_Energy_Per_MB.pdf"))
    plt.close()

    print(f"[OK] eta_PQC@50={eta_pqc[0]:.2f} eta_Hybrid@50={eta_hybrid[0]:.2f}")
    print(f"[OK] eta_PQC@1000={eta_pqc[-1]:.3f} eta_Hybrid@1000={eta_hybrid[-1]:.3f}")


if __name__ == "__main__":
    run(parse_args())
