#!/usr/bin/env python3
"""Run preprocessing evaluation (Tables 2 and 6).

Measures the effect of reachability elimination on MaxSAT encoding size
and solver runtime for L({∃}) chains across multiple benchmarks.
"""

import argparse
import logging
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ontology import load_ontology, load_learning_problem, get_stats
from src.encoding import encode_chain_fitting
from src.reachability import reachability_elimination, get_unit_clauses
from src.solvers import solve
from src.utils import setup_logging, save_results, median_and_std

logger = logging.getLogger(__name__)

BENCHMARK_DIR = "data/ontologies"

BENCHMARKS = {
    "Family": "family.owl",
    "Mutagenesis": "mutagenesis.owl",
    "Carcinogenesis": "carcinogenesis.owl",
    "Semantic Bible": "semantic_bible.owl",
    "Vicodi": "vicodi.owl",
    "Hepatitis": "hepatitis.owl",
    "Mammographic": "mammographic.owl",
    "NCTRER": "nctrer.owl",
    "Premier League": "premier_league.owl",
    "Suramin": "suramin.owl",
}


def run_single(
    benchmark: str,
    k: int,
    t: int,
    solver_name: str,
    n_runs: int,
    timeout: int,
) -> dict:
    """Run preprocessing evaluation for a single configuration."""
    owl_path = os.path.join(BENCHMARK_DIR, BENCHMARKS[benchmark])
    lp_path = os.path.join(BENCHMARK_DIR, benchmark.lower().replace(" ", "_"), "lp.json")

    interp = load_ontology(owl_path)
    sample = load_learning_problem(interp, lp_path)
    stats = get_stats(interp)

    # Reachability elimination
    reach_result = reachability_elimination(sample, k)

    # Encode without reachability
    enc_generic = encode_chain_fitting(sample, k, t)

    # Encode with reachability
    unit_clauses = get_unit_clauses(
        reach_result["reachable_roles"],
        interp.sig_r,
        enc_generic.var_map,
    )
    enc_reach = encode_chain_fitting(sample, k, t, unit_clauses=unit_clauses)

    # Solve multiple runs
    gen_times = []
    reach_times = []
    for run in range(n_runs):
        logger.info(f"  Run {run+1}/{n_runs} (generic)...")
        r_gen = solve(enc_generic, solver_name, timeout)
        gen_times.append(r_gen["time"])

        logger.info(f"  Run {run+1}/{n_runs} (reachability)...")
        r_reach = solve(enc_reach, solver_name, timeout)
        reach_times.append(r_reach["time"])

    return {
        "benchmark": benchmark,
        "k": k,
        "t": t,
        "solver": solver_name,
        "stats": stats,
        "base_vars": reach_result["base_vars"],
        "reach_vars": reach_result["reach_vars"],
        "elimination_rate": reach_result["elimination_rate"],
        "prep_time_ms": reach_result["prep_time_ms"],
        "gen_time": median_and_std(gen_times),
        "reach_time": median_and_std(reach_times),
        "optimum_gen": r_gen["cost"],
        "optimum_reach": r_reach["cost"],
    }


def main():
    parser = argparse.ArgumentParser(description="Run preprocessing evaluation")
    parser.add_argument("--datasets", nargs="+", default=["Family", "Mutagenesis", "Carcinogenesis"])
    parser.add_argument("--k-values", nargs="+", type=int, default=[3, 5, 7])
    parser.add_argument("--t", type=int, default=0)
    parser.add_argument("--solvers", nargs="+", default=["rc2"])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=str, default="results/preprocessing.json")
    parser.add_argument("--log-level", type=str, default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    if args.datasets == ["all"]:
        args.datasets = list(BENCHMARKS.keys())

    results = []
    for benchmark in args.datasets:
        for k in args.k_values:
            for solver in args.solvers:
                logger.info(f"=== {benchmark} k={k} solver={solver} ===")
                result = run_single(
                    benchmark, k, args.t, solver, args.runs, args.timeout
                )
                results.append(result)

                # Verify optima match
                if result["optimum_gen"] != result["optimum_reach"]:
                    logger.warning(
                        f"OPTIMUM MISMATCH: gen={result['optimum_gen']}, "
                        f"reach={result['optimum_reach']}"
                    )

    save_results(results, args.output)
    logger.info(f"Done. {len(results)} configurations evaluated.")


if __name__ == "__main__":
    main()
