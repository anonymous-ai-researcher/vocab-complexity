#!/bin/bash
# Run all experiments end-to-end.
# Usage: bash experiments/run_all.sh

set -e
mkdir -p results

echo "=== Table 2: Main preprocessing (3 benchmarks × 3 solvers) ==="
python experiments/run_preprocessing.py \
    --datasets Family Mutagenesis Carcinogenesis \
    --k-values 3 5 7 \
    --t 0 \
    --solvers open-wbo rc2 maxcdcl \
    --runs 5 \
    --timeout 600 \
    --output results/tab2.json

echo "=== Table 6: Full preprocessing (10 benchmarks) ==="
python experiments/run_preprocessing.py \
    --datasets all \
    --k-values 3 5 7 9 11 \
    --t 0 \
    --solvers open-wbo \
    --runs 5 \
    --timeout 600 \
    --output results/tab6.json

echo "=== Table 3: Union-of-chains + t-ablation ==="
python experiments/run_uoc.py \
    --datasets all \
    --k 5 \
    --t-values 0 2 5 10 \
    --output results/tab3.json

echo "=== Table 7: t-ablation (all benchmarks) ==="
python experiments/run_ablation_t.py \
    --datasets all \
    --k 5 \
    --t-values 0 2 5 10 \
    --output results/tab7.json

echo "=== Table 8: Depth-wise reachability ==="
python experiments/run_depthwise.py \
    --datasets all \
    --max-depth 6 \
    --output results/tab8.json

echo "=== Table 9: Scalability ==="
python experiments/run_scalability.py \
    --datasets all \
    --k 5 \
    --fractions 0.2 0.4 0.6 0.8 1.0 \
    --output results/tab9.json

echo "=== Tables 10-11: Baseline comparison ==="
python experiments/run_baselines.py \
    --datasets all \
    --k 7 \
    --t 0 \
    --timeout 300 \
    --output results/tab10_11.json

echo "=== Generating LaTeX tables ==="
python scripts/generate_tables.py --results-dir results/ --output-dir tables/

echo "=== Verifying cross-table consistency ==="
python scripts/verify_consistency.py --results-dir results/

echo "All experiments completed."
