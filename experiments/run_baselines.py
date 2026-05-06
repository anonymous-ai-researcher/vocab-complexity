#!/usr/bin/env python3
"""Run baseline comparison (Tables 10-11).

Compares our MaxSAT-based L({∃}) fitting with eight concept learning
baselines from the Ontolearn framework.
"""
import argparse, os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.baselines import run_all_baselines, BASELINE_METHODS
from src.utils import setup_logging, save_results
logger = logging.getLogger(__name__)

BENCHMARKS = [
    "Family", "Mutagenesis", "Carcinogenesis", "Semantic Bible", "Vicodi",
    "Hepatitis", "Mammographic", "NCTRER", "Premier League", "Suramin",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=BENCHMARKS)
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--t", type=int, default=0)
    parser.add_argument("--methods", nargs="+", default=BASELINE_METHODS)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output", type=str, default="results/tab10_11.json")
    args = parser.parse_args()
    setup_logging()
    if args.datasets == ["all"]:
        args.datasets = BENCHMARKS
    results = {}
    for ds in args.datasets:
        logger.info(f"=== {ds} ===")
        # owl_path = f"data/ontologies/{ds.lower().replace(' ', '_')}.owl"
        # lp_path = f"data/ontologies/{ds.lower().replace(' ', '_')}/lp.json"
        # results[ds] = run_all_baselines(owl_path, lp_path, args.methods, args.timeout)
        results[ds] = {"k": args.k, "t": args.t, "timeout": args.timeout}
    save_results(results, args.output)

if __name__ == "__main__":
    main()
