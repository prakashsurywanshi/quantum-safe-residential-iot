#!/usr/bin/env python3
"""Generate the graphical abstract for the QHSG manuscript.

Left panel : the architecture in one glance (constrained endpoints <-> QHSG,
             fed by metro QKD and offloaded ML-KEM-768).
Right panel: endpoint key-refresh energy at N=100 for the four schemes, with the
             headline reductions annotated.

Output: figures/Graphical_Abstract.png (and .pdf for vector reproduction).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
with open(os.path.join(ROOT, "data", "summary.json")) as f:
    S = json.load(f)

N100 = S["N100"]  # mJ at N=100
pct_pqc = S["pct_PQC_vs_Classical"]
pct_hyb = S["pct_Hybrid_vs_PQC"]
pct_hyb_cl = S["pct_Hybrid_vs_Classical"]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=200,
                               gridspec_kw={"width_ratios": [1.15, 1.0]})

# ---------------------------------------------------------------- left panel
axL.set_xlim(0, 10)
axL.set_ylim(0, 10)
axL.axis("off")


def box(x, y, w, h, text, fc, ec="#333333", fs=9, weight="normal"):
    axL.add_patch(FancyBboxPatch((x, y), w, h,
                                 boxstyle="round,pad=0.12,rounding_size=0.25",
                                 linewidth=1.3, edgecolor=ec, facecolor=fc))
    axL.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fs, weight=weight)


def arrow(x1, y1, x2, y2, text="", color="#333333", fs=8, style="-|>",
          rad=0.0):
    axL.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=13, linewidth=1.4,
                                 color=color,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        axL.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.28, text, ha="center",
                 va="bottom", fontsize=fs, color=color)


box(0.2, 3.6, 3.0, 2.6,
    "IoT Leaf Endpoints\n(Cortex-M4, 802.15.4)\nsensors - locks - cameras",
    "#e8f0fe", fs=9, weight="bold")
box(6.6, 3.6, 3.2, 2.6,
    "Quantum-Safe Home\nGateway (QHSG)\nmains-powered edge",
    "#e6f4ea", fs=9, weight="bold")
box(6.6, 7.0, 3.2, 1.9,
    "Metro QKD\noptical key distribution",
    "#f3e8fd", fs=9)
box(2.3, 7.0, 3.2, 1.9,
    "Offloaded ML-KEM-768\nPQC handshake",
    "#fde8e8", fs=9)

arrow(3.2, 4.9, 6.6, 4.9, "64 B symmetric ticket\n(AES-256-GCM)", color="#1a73e8")
arrow(8.2, 7.0, 8.2, 6.2, "", color="#8e24aa")
arrow(5.5, 7.0, 7.0, 6.2, "", color="#d93025", rad=-0.2)
axL.text(5.0, 9.4, "Security plane (gateway)", ha="center", fontsize=9,
         style="italic", color="#444444")
axL.text(5.0, 1.9, "Data plane (endpoints): lightweight symmetric crypto",
         ha="center", fontsize=9, style="italic", color="#444444")

# ---------------------------------------------------------------- right panel
schemes = ["Classical\n(ECDH)", "PQC-Only\n(ML-KEM-768)", "QKD-Assisted",
           "Hybrid QHSG\n(proposed)"]
vals = [N100["Classical"], N100["PQC"], N100["QKD"], N100["Hybrid"]]
colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
y = range(len(schemes))[::-1]
bars = axR.barh(list(y), vals, color=colors, height=0.6)
axR.set_yticks(list(y))
axR.set_yticklabels(schemes, fontsize=9)
axR.set_xlabel("Endpoint key-refresh energy at $N=100$ (mJ)", fontsize=9)
axR.set_title("Endpoint energy: offloading beats direct PQC", fontsize=10,
              weight="bold")
for b, v in zip(bars, vals):
    axR.text(v + 6, b.get_y() + b.get_height() / 2, f"{v:.2f}",
             va="center", fontsize=8.5)
axR.set_xlim(0, max(vals) * 1.22)
axR.grid(axis="x", alpha=0.25)
for s in ["top", "right"]:
    axR.spines[s].set_visible(False)
axR.annotate(f"$-${pct_hyb:.1f}% vs direct PQC\n$-${pct_hyb_cl:.1f}% vs ECDH",
             xy=(N100["Hybrid"], 0), xytext=(max(vals) * 0.42, 0.7),
             fontsize=8.5, color="#6a1b9a",
             arrowprops=dict(arrowstyle="->", color="#6a1b9a", lw=1.2))

fig.suptitle("Sustainable Hybrid QKD-PQC Security for Quantum-Resilient IoT",
             fontsize=11.5, weight="bold", y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.95])
out_png = os.path.join(HERE, "Graphical_Abstract.png")
out_pdf = os.path.join(HERE, "Graphical_Abstract.pdf")
fig.savefig(out_png, dpi=300, bbox_inches="tight")
fig.savefig(out_pdf, bbox_inches="tight")
print("wrote", out_png, "and", out_pdf)
print(f"headline: PQC {pct_pqc:+.1f}% vs Classical; Hybrid {pct_hyb:.1f}% vs PQC; "
      f"{pct_hyb_cl:.1f}% vs Classical")
