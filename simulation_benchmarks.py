import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="Quantum-Safe Residential IoT Simulation")
    parser.add_argument("--bitrate", type=float, default=250000, help="Wireless bitrate in bps (default: 250 kbps)")
    parser.add_argument("--p_cpu", type=float, default=0.132, help="MCU CPU Active Power in Watts (default: 0.132 W)")
    parser.add_argument("--p_tx", type=float, default=0.250, help="Transceiver TX Power in Watts (default: 0.250 W)")
    parser.add_argument("--p_rx", type=float, default=0.180, help="Transceiver RX Power in Watts (default: 0.180 W)")
    parser.add_argument("--scales", nargs="+", type=int, default=[10, 25, 50, 100, 250, 500], help="List of fleet sizes N")
    parser.add_argument("--outdir", type=str, default="data", help="Output directory")
    return parser.parse_args()

# 6LoWPAN Fragmentation calculation over IEEE 802.15.4 (MTU: 127 Bytes)
def calc_fragments(payload_bytes):
    s_first = 105
    s_sub = 111
    if payload_bytes <= s_first:
        return 1
    return 1 + int(np.ceil((payload_bytes - s_first) / s_sub))

def run_simulation(args):
    os.makedirs(args.outdir, exist_ok=True)
    fig_dir = os.path.join(args.outdir, "../figures")
    os.makedirs(fig_dir, exist_ok=True)

    # Benchmarks (Time in seconds, Payload in bytes)
    params = {
        'Classical': {'t_comp': 0.015, 'bytes': 128},
        'PQC-Only': {'t_comp': 0.0035, 'bytes': 2272},
        'QKD-Assisted': {'t_comp': 0.0008, 'bytes': 64},
        'Hybrid QHSG': {'t_comp': 0.0009, 'bytes': 64}
    }

    def calc_energy_endpoint(scheme):
        p = params[scheme]
        e_comp = p['t_comp'] * args.p_cpu
        n_frag = calc_fragments(p['bytes'])
        t_tx = (p['bytes'] * 8) / args.bitrate
        # Overhead per fragment accounts for MAC preambles & inter-frame spacing
        e_comm = (t_tx * args.p_tx) + (n_frag * 0.0005 * args.p_tx)
        return (e_comp + e_comm) * 1000.0  # in mJ

    e_unit = {k: calc_energy_endpoint(k) for k in params}

    results = {
        'Scale_N': args.scales,
        'Classical_mJ': [n * e_unit['Classical'] for n in args.scales],
        'PQC_Only_mJ': [n * e_unit['PQC-Only'] for n in args.scales],
        'QKD_Assisted_mJ': [n * e_unit['QKD-Assisted'] for n in args.scales],
        'Hybrid_QHSG_mJ': [n * e_unit['Hybrid QHSG'] for n in args.scales]
    }
    df = pd.DataFrame(results)
    csv_file = os.path.join(args.outdir, "Table_Energy_Results.csv")
    df.to_csv(csv_file, index=False)
    print(f"[✓] Generated dataset saved to {csv_file}")
    print(df.to_string(index=False))

    # Figure 1: Scalability
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
    plt.savefig(os.path.join(fig_dir, "Fig_Energy_Scalability.png"), dpi=300)
    plt.savefig(os.path.join(fig_dir, "Fig_Energy_Scalability.pdf"))
    plt.close()

    # Figure 2: Normalized Workload
    workloads = np.array([50, 100, 200, 500, 1000])
    base_stream_mj = workloads * 12.0
    idx_100 = args.scales.index(100) if 100 in args.scales else 0

    eta_pqc = (base_stream_mj + df['PQC_Only_mJ'].iloc[idx_100]) / workloads
    eta_hybrid = (base_stream_mj + df['Hybrid_QHSG_mJ'].iloc[idx_100]) / workloads
    eta_qkd = (base_stream_mj + df['QKD_Assisted_mJ'].iloc[idx_100]) / workloads

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
    plt.savefig(os.path.join(fig_dir, "Fig_Energy_Per_MB.png"), dpi=300)
    plt.savefig(os.path.join(fig_dir, "Fig_Energy_Per_MB.pdf"))
    plt.close()
    print(f"[✓] Figures exported to {fig_dir}")

if __name__ == "__main__":
    args = parse_args()
    run_simulation(args)
