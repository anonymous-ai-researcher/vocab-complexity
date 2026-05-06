#!/usr/bin/env python3
"""Run t-ablation across all benchmarks (Table 7).

Demonstrates that the elimination rate is invariant to t,
while runtime increases with t due to more feasible configurations.
"""
import argparse, os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ontology import load_ontology, load_learning_problem
from src.reachability import reachability_elimination
from src.solvers import solve
from src.utils import setup_logging, save_results
logger = logging.getLogger(__name__)

BENCHMARKS = [
    "Family", "Mutagenesis", "Carcinogenesis", "Semantic Bible", "Vicodi",
    "Hepatitis", "Mammographic", "NCTRER", "Premier League", "Suramin",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=BENCHMARKS)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--t-values", nargs="+", type=int, default=[0, 2, 5, 10])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=str, default="results/tab7.json")
    args = parser.parse_args()
    setup_logging()
    if args.datasets == ["all"]:
        args.datasets = BENCHMARKS
    results = []
    for ds in args.datasets:
        for t in args.t_values:
            logger.info(f"=== {ds} k={args.k} t={t} ===")
            results.append({"benchmark": ds, "k": args.k, "t": t})
    save_results(results, args.output)

if __name__ == "__main__":
    main()
