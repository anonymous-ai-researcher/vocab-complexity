# Not the Formula, Not the Data: Vocabulary Controls the Complexity of Concept Learning

This repository contains the code and experiment pipeline for reproducing the results in our NeurIPS 2026 submission.

## Overview

We study the parameterized complexity of concept fitting in the description logic ALC. The main contributions are:

1. **FPT tractability** (Theorem 1): Both BndFit and ApxFit are FPT by concept size k for every fixed vocabulary and every ALC fragment.
2. **W[2]-hardness** (Theorem 3): When the vocabulary is part of the input, fitting becomes W[2]-hard by k, even for L({∃}) chains at t=0.
3. **Kernel lower bound** (Theorem 4): No polynomial kernel exists even over a fixed two-role vocabulary, unless NP ⊆ coNP/poly.
4. **Reachability elimination** (Proposition 1): A preprocessing rule that removes 41–70% of role-selection variables from MaxSAT encodings with negligible overhead.

## Requirements

- Python ≥ 3.9
- Java ≥ 11 (for Ontolearn/OWL API)
- PySAT (for RC2 solver)
- Open-WBO (binary, see installation below)
- MaxCDCL (binary, see installation below)

```bash
pip install -r requirements.txt
```

### Solver Installation

**Open-WBO** (v2.1):
```bash
git clone https://github.com/sat-group/open-wbo.git
cd open-wbo && make rs
cp open-wbo_release ../solvers/open-wbo
```

**MaxCDCL** (v2023):
```bash
# Download from https://maxsat-evaluations.github.io/
# Place binary at solvers/maxcdcl
```

**RC2** is included via PySAT (`pip install python-sat`).

### Dataset Download

```bash
bash data/download_datasets.sh
```

This downloads the 10 benchmark ontologies from SML-Bench and the NCES suite.

## Project Structure

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── configs/
│   └── experiments.yaml          # All experiment configurations
├── data/
│   ├── download_datasets.sh      # Dataset download script
│   └── benchmarks.yaml           # Dataset metadata
├── src/
│   ├── __init__.py
│   ├── ontology.py               # OWL ontology loading and statistics
│   ├── encoding.py               # MaxSAT encoding for L({∃}) chains
│   ├── reachability.py           # Reachability elimination (Algorithm 1)
│   ├── solvers.py                # Solver interface (Open-WBO, RC2, MaxCDCL)
│   ├── baselines.py              # Ontolearn baseline wrapper
│   └── utils.py                  # Logging, timing, I/O utilities
├── experiments/
│   ├── run_preprocessing.py      # Tables 2, 6: preprocessing evaluation
│   ├── run_uoc.py                # Table 3: union-of-chains + t-ablation
│   ├── run_ablation_t.py         # Table 7: t-ablation across all benchmarks
│   ├── run_depthwise.py          # Table 8: depth-wise reachability rates
│   ├── run_scalability.py        # Table 9: linear scalability verification
│   ├── run_baselines.py          # Tables 10, 11: baseline comparison
│   └── run_all.sh                # Run all experiments end-to-end
├── scripts/
│   ├── generate_tables.py        # Generate LaTeX tables from results
│   └── verify_consistency.py     # Cross-table consistency verification
├── results/                      # Output directory (auto-created)
└── solvers/                      # Solver binaries (user-provided)
```

## Quick Start

### 1. Download data and install dependencies

```bash
pip install -r requirements.txt
bash data/download_datasets.sh
```

### 2. Run all experiments

```bash
bash experiments/run_all.sh
```

This runs all experiments sequentially and saves results to `results/`.

### 3. Generate LaTeX tables

```bash
python scripts/generate_tables.py --results-dir results/ --output-dir tables/
```

### 4. Verify cross-table consistency

```bash
python scripts/verify_consistency.py --results-dir results/
```

## Individual Experiments

### Table 2/6: Preprocessing Evaluation

```bash
python experiments/run_preprocessing.py \
    --datasets Family Mutagenesis Carcinogenesis \
    --k-values 3 5 7 \
    --t 0 \
    --solvers open-wbo rc2 maxcdcl \
    --runs 5 \
    --timeout 600 \
    --output results/tab2.json
```

For full 10-benchmark evaluation (Table 6):

```bash
python experiments/run_preprocessing.py \
    --datasets all \
    --k-values 3 5 7 9 11 \
    --t 0 \
    --solvers open-wbo \
    --runs 5 \
    --timeout 600 \
    --output results/tab6.json
```

### Table 7: t-Ablation

```bash
python experiments/run_ablation_t.py \
    --datasets all \
    --k 5 \
    --t-values 0 2 5 10 \
    --output results/tab7.json
```

### Table 8: Depth-wise Reachability

```bash
python experiments/run_depthwise.py \
    --datasets all \
    --max-depth 6 \
    --output results/tab8.json
```

### Table 9: Scalability

```bash
python experiments/run_scalability.py \
    --datasets all \
    --k 5 \
    --fractions 0.2 0.4 0.6 0.8 1.0 \
    --output results/tab9.json
```

### Tables 10-11: Baseline Comparison

```bash
python experiments/run_baselines.py \
    --datasets all \
    --k 7 \
    --t 0 \
    --timeout 300 \
    --output results/tab10_11.json
```

## Benchmarks

| Dataset | |Δ| | |P| | |N| | m | |Σ_R| | |Σ_C| | Source |
|---------|-----|-----|-----|---|-------|-------|--------|
| Family | 202 | 42 | 39 | 81 | 6 | 19 | SML-Bench |
| Mutagenesis | 5,631 | 125 | 63 | 188 | 12 | 38 | Srinivasan et al. 1996 |
| Carcinogenesis | 22,372 | 182 | 116 | 298 | 18 | 52 | SML-Bench |
| Semantic Bible | 733 | 56 | 44 | 100 | 29 | 48 | NCES suite |
| Vicodi | 28,654 | 112 | 88 | 200 | 10 | 194 | NCES suite |
| Hepatitis | 592 | 250 | 250 | 500 | 5 | 14 | SML-Bench |
| Mammographic | 961 | 481 | 480 | 961 | 3 | 19 | SML-Bench |
| NCTRER | 7,413 | 78 | 72 | 150 | 9 | 37 | SML-Bench |
| Premier League | 12,895 | 160 | 140 | 300 | 13 | 10 | SML-Bench |
| Suramin | 482 | 11 | 5 | 16 | 3 | 46 | SML-Bench |

## Hardware

All experiments were run on Intel Xeon Gold 6248R (3.0 GHz), 256 GB RAM, Ubuntu 22.04. The solver timeout is 600 seconds. Reachability preprocessing adds at most 14 ms overhead.

## License

This code is released under the MIT License. See `LICENSE` for details.
