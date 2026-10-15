# Reproducibility

## Prerequisites
- Python 3.12.3 (use `/tmp/opencode/qsiot-venv` if the working path contains `:`; needs numpy/pandas/matplotlib)
- ProVerif 2.05 (binary at `/tmp/proverif/bin/proverif` or built as documented)
- Docker with the `contiker/contiki-ng` image and a Contiki-NG checkout (for COOJA)

## Commands
- Analytical model (canonical): `python3 simulation_benchmarks.py --scales 10 25 50 100 250 500`
  - writes `data/Table_Energy_Results.csv`, `data/summary.json`, and `figures/Fig_Energy_*`
  - the 6LoWPAN fragmentation constants are those validated in COOJA (see `cooja/`)
- Sensitivity analysis: `python3 sensitivity_analysis.py`
  - writes `data/sensitivity_results.csv`, `data/sensitivity_summary.json`, `figures/Fig_Sensitivity.png`
- Cycle calibration: `python3 benchmarks/cycle_calibration.py`
  - writes `benchmarks/cycle_counts.csv`, `benchmarks/calibration_report.csv`
- ProVerif verification: `bash proverif/run_all.sh /path/to/proverif`
  - writes `proverif/results_*.txt`; summary in `proverif/results_table.md`
- COOJA/Contiki-NG fragmentation validation: `bash cooja/scripts/run_fragmentation.sh`
  - see `cooja/README.md`; requires the `UIP_LINK_MTU` patch in `cooja/patch/`
  - writes `cooja/results/fragmentation_results.csv` and `cooja/logs/run-frag-*/`

## Artifacts
- Energy table: `data/Table_Energy_Results.csv` (endpoint units: Classical 1.5763, PQC 3.2846, QKD/Hybrid 0.105248 mJ; Hybrid 10.52 mJ @ N=100)
- Headline metrics: PQC vs. Classical +108.4%; Hybrid vs. PQC −96.8%; Hybrid vs. Classical −93.3%
- Sensitivity: `data/sensitivity_summary.json` (PQC vs. Classical 108.6 [46.3, 217.4]; Hybrid vs. PQC 96.8; Hybrid vs. Classical 93.3)
- ProVerif models/results: `proverif/*.pv`, `proverif/results_*.txt`, `proverif/results_table.md`, `proverif/run_all.sh`
- Calibration: `benchmarks/cycle_counts.csv`, `benchmarks/calibration_report.csv`
- COOJA validation: `cooja/apps/qhsg-udp/`, `cooja/scripts/`, `cooja/results/fragmentation_results.csv`, `cooja/patch/contiki-ng-ipv6-mtu.patch`

## Notes
- The COOJA validation measures 6LoWPAN **frame/fragment counts** (not energy).
  Energest counters were found unreliable under COOJA and are not used; energy is
  computed in `simulation_benchmarks.py` from the validated frame counts and
  datasheet radio constants.
