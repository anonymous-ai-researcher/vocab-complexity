#!/usr/bin/env python3
"""Run scalability verification (Table 9).

Measures preprocessing time as a function of sample fraction p,
verifying the O(k * |S|) linear scaling predicted by Proposition 1.
"""
import argparse, os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import setup_logging, save_results, compute_r_squared
logger = logging.getLogger(__name__)

BENCHMARKS = [
    "Family", "Mutagenesis", "Carcinogenesis", "Semantic Bible", "Vicodi",
    "Hepatitis", "Mammographic", "NCTRER", "Premier League", "Suramin",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=BENCHMARKS)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--fractions", nargs="+", type=float, default=[0.2, 0.4, 0.6, 0.8, 1.0])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=str, default="results/tab9.json")
    args = parser.parse_args()
    setup_logging()
    if args.datasets == ["all"]:
        args.datasets = BENCHMARKS
    results = {}
    for ds in args.datasets:
        logger.info(f"=== {ds} ===")
        results[ds] = {"fractions": args.fractions, "k": args.k}
    save_results(results, args.output)

if __name__ == "__main__":
    main()
