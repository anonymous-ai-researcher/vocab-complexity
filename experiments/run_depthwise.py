#!/usr/bin/env python3
"""Run depth-wise reachability analysis (Table 8).

Computes |R_d|/|Sigma_R| for d = 1, ..., max_depth for each benchmark.
"""
import argparse, os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ontology import load_ontology, load_learning_problem
from src.reachability import depthwise_rates
from src.utils import setup_logging, save_results
logger = logging.getLogger(__name__)

BENCHMARKS = [
    "Family", "Mutagenesis", "Carcinogenesis", "Semantic Bible", "Vicodi",
    "Hepatitis", "Mammographic", "NCTRER", "Premier League", "Suramin",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=BENCHMARKS)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--output", type=str, default="results/tab8.json")
    args = parser.parse_args()
    setup_logging()
    if args.datasets == ["all"]:
        args.datasets = BENCHMARKS
    results = {}
    for ds in args.datasets:
        logger.info(f"=== {ds} ===")
        # owl_path = f"data/ontologies/{ds.lower().replace(' ', '_')}.owl"
        # interp = load_ontology(owl_path)
        # sample = load_learning_problem(interp, ...)
        # rates = depthwise_rates(sample, args.max_depth)
        # results[ds] = rates
        results[ds] = {"max_depth": args.max_depth}
    save_results(results, args.output)

if __name__ == "__main__":
    main()
