"""Cycle-level calibration of the QHSG energy model.

Converts published ARM Cortex-M4 cycle counts into execution time and
energy, then compares them with the analytical constants used in
simulation_benchmarks.py (Table 1 of the manuscript).

Methodology
-----------
Direct-execution schemes (Classical, PQC-Only):
  - Classical  (ECDH): one X25519 constant-time scalar multiplication.
  - PQC-Only   (ML-KEM-768): a leaf-terminated handshake = key generation
    + decapsulation (m4fspeed implementation). Single encapsulation is also
    reported because the analytical model's 3.5 ms corresponds to ~one
    encapsulation.
Gateway-mediated schemes (QKD-Assisted, Hybrid QHSG): the endpoint executes
  only symmetric AEAD (AES-256-GCM over the ~128-byte session block), which
  is what the "t_comp 0.8/0.9 ms" constants bound.

Sources
-------
- pqm4 (MUPQ): https://github.com/mupq/pqm4  (benchmarks.csv)
  Kannwischer, Rijneveld, Schwabe, Stoffelen, "PQMA4: Post-quantum crypto
  library for the ARM Cortex-M4", eprint 2019/844.
  Cycle counts obtained at 24 MHz to avoid memory wait states.
- X25519 (Cortex-M4): dfaranha/x25519-cortexm4; de Groot, W., "A performance
  study of X25519 on Cortex-M3 and M4", MSc thesis, TU/e, 2019.
  Constant-time scalar multiplication: 1,816,351 cycles.
- AES-256-GCM: mbed TLS benchmark, AES-GCM-256 ~= 294 cycles/byte on a
  Cortex-M4 (NUCLEO_F303RE @72 MHz); published range 251-311 cyc/B.

Usage
-----
    python -m benchmarks.cycle_calibration [--freq 168e6] [--p_cpu 0.132]
"""

import argparse
import os
import csv

HERE = os.path.dirname(os.path.abspath(__file__))

# Analytical constants from simulation_benchmarks.py (Table 1)
ASSUMED = {
    'Classical (ECDH)': 0.015,
    'PQC-Only (ML-KEM-768)': 0.0035,
    'QKD-Assisted': 0.0008,
    'Hybrid QHSG': 0.0009,
}


def load_counts():
    path = os.path.join(HERE, 'cycle_counts.csv')
    rows = {}
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows[(r['scheme'], r['operation'], r['implementation'])] = int(r['cycles_mean'])
    return rows


def op(counts, scheme, operation, impl):
    return counts[(scheme, operation, impl)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--freq', type=float, default=168e6, help='MCU clock (Hz); paper uses 168 MHz')
    ap.add_argument('--p_cpu', type=float, default=0.132, help='MCU active power (W)')
    args = ap.parse_args()

    counts = load_counts()

    x25519 = op(counts, 'ECDH-X25519', 'scalar_mult', 'deGroot-M4')
    kem_kg = op(counts, 'ML-KEM-768', 'keygen', 'm4fspeed')
    kem_enc = op(counts, 'ML-KEM-768', 'encaps', 'm4fspeed')
    kem_dec = op(counts, 'ML-KEM-768', 'decaps', 'm4fspeed')
    aes_gcm = op(counts, 'AES-256-GCM', 'aead_128B', 'mbedtls-m4')

    # (row, measured_cycles, notes)
    rows = [
        ('Classical (ECDH)', x25519, 'X25519 scalar mult (one side of ECDH)'),
        ('PQC-Only (ML-KEM-768) enclap only', kem_enc, 'single encapsulation'),
        ('PQC-Only (ML-KEM-768) full handshake', kem_kg + kem_dec, 'keygen + decaps (leaf-terminated)'),
        ('QKD-Assisted (endpoint bound)', aes_gcm, 'AES-256-GCM over 128 B session block'),
        ('Hybrid QHSG (endpoint bound)', aes_gcm, 'AES-256-GCM over 128 B session block'),
    ]

    out = []
    print(f'MCU clock   : {args.freq/1e6:.0f} MHz   P_CPU = {args.p_cpu*1e3:.0f} mW')
    print(f'{"Row":<38}{"cycles":>11}{"t_ms":>9}{"E_mJ":>9}{"t_ass":>9}{"ratio":>7}  note')
    for label, cycles, note in rows:
        t_ms = cycles / args.freq * 1e3
        e_mj = t_ms * 1e-3 * args.p_cpu * 1e3  # = t_ms * P_CPU
        idx = label.split(' [')[0]
        # map label to assumed constant
        base = 'PQC-Only (ML-KEM-768)' if 'PQC-Only' in label else (
            'QKD-Assisted' if 'QKD' in label else ('Hybrid QHSG' if 'Hybrid' in label else 'Classical (ECDH)'))
        t_ass = ASSUMED[base]
        out.append({'row': label, 'implementation': note, 'cycles': cycles,
                    't_measured_ms': round(t_ms, 4), 'e_measured_mJ': round(e_mj, 4),
                    't_assumed_ms': t_ass * 1e3, 'e_assumed_mJ': round(t_ass * args.p_cpu * 1e3, 4),
                    'ratio_measured_assumed': round(cycles / args.freq / t_ass, 3)})
        print(f'{label:<38}{cycles:>11,}{t_ms:>9.3f}{e_mj:>9.4f}{t_ass*1e3:>9.2f}'
              f'{cycles/args.freq/t_ass:>7.2f}  {note}')

    table = os.path.join(HERE, 'calibration_report.csv')
    with open(table, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f'\nReport written to {table}')


if __name__ == '__main__':
    main()