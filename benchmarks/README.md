# benchmarks/ — Cycle-level calibration

Measured (published) ARM Cortex-M4 cycle counts used to calibrate and cross-check the
analytical energy constants in `simulation_benchmarks.py` (Table 1 of the manuscript).

## Files
- `cycle_counts.csv` — raw cycle counts with implementation and source.
- `cycle_calibration.py` — converts cycles → time (at `--freq`, default 168 MHz) →
  energy (at `--p_cpu`, default 132 mW), and compares with the model's assumed `t_comp`.
- `calibration_report.csv` — generated comparison table (committed).

## Key results (168 MHz, 132 mW, 3.3 V × 40 mA)
| Model constant | Assumed `t_comp` | Measured source | Measured time | Verdict |
|---|---|---|---|---|
| Classical (ECDH) | 15.0 ms | X25519 const-time scalar mult, 1,816,351 cycles [1] | 10.81 ms | assumption conservative (0.72×) |
| PQC-Only (ML-KEM-768) | 3.5 ms | pqm4 m4fspeed encapsulation, 658,754 cycles [2] | 3.92 ms | assumption ≈ measured (1.12×) |
| PQC-Only, full leaf handshake | 3.5 ms | pqm4 keygen + decaps, 1,349,923 cycles [2] | 8.04 ms | real PQC cost 2.3× assumed → reported PQC penalty is conservative |
| QKD-Assisted endpoint | 0.8 ms | AES-256-GCM over 128 B, ~37,632 cycles [3] | 0.224 ms | assumption conservative (0.28×) |
| Hybrid QHSG endpoint | 0.9 ms | AES-256-GCM over 128 B, ~37,632 cycles [3] | 0.224 ms | assumption conservative (0.25×) |

## Sources
1. X25519 (Cortex-M4, constant-time): `dfaranha/x25519-cortexm4`;
   W. de Groot, "A performance study of X25519 on Cortex-M3 and M4", MSc thesis, TU/e (2019).
2. pqm4: J. M. B. Kannwischer, J. Rijneveld, P. Schwabe, K. Stoffelen, "PQM4: Post-quantum
   crypto library for the ARM Cortex-M4", https://eprint.iacr.org/2019/844; data from
   https://github.com/mupq/pqm4/blob/master/benchmarks.csv (m4fspeed, 10 executions, 24 MHz).
3. mbed TLS benchmark: AES-GCM-256 ≈ 294 cycles/byte on Cortex-M4 (NUCLEO_F303RE);
   published range 251–311 cyc/B (Mbed Crypto). 128-byte AEAD covers the 64-byte session
   ticket plus GCM tag/IV/header.

## How to re-run
```bash
python benchmarks/cycle_calibration.py                      # 168 MHz, 132 mW (paper defaults)
python benchmarks/cycle_calibration.py --freq 72e6 --p_cpu 0.050
```