# Reproducibility (v2.0-rev2)

## Prerequisites
- Python 3.12.3 (use `/tmp/opencode/qsiot-venv` if the working path contains `:`)
- ProVerif 2.05 (binary available at `/path/to/proverif` or built as documented)
- Docker (for Contiki-NG/COOJA)

## Commands
- Analytical model (canonical): `python3 simulation_benchmarks.py --gateway-factor 0.1 --bitrate 1000000`
- Cycle calibration: `python3 benchmarks/cycle_calibration.py`
- ProVerif verification: `bash proverif/run_all.sh /path/to/proverif`
- COOJA/Contiki-NG: see `cooja/README.md` (Docker, scenarios N∈{10,25,50,100}, loss {0,5,20%}, energest parsing)

## Artifacts
- Corrected energy table: `data/Table_Energy_Results.csv` (Hybrid 13.99 mJ @ N=100)
- ProVerif models/results: `proverif/*.pv`, `proverif/results_*.txt`, `proverif/run_all.sh`
- Calibration: `benchmarks/cycle_counts.csv`, `benchmarks/calibration_report.csv`
- Reproducible harness: `cooja/` (configs/apps/scripts)
