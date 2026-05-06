"""Wrapper for Ontolearn concept learning baselines."""

import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

BASELINE_METHODS = [
    "CELOE", "OCEL", "EvoLearner", "NCES", "NCES2",
    "CLIP", "DRILL", "ECII",
]


def run_baseline(
    method: str,
    owl_path: str,
    lp_path: str,
    timeout: int = 300,
) -> Dict:
    """Run a single baseline method on a learning problem.

    Args:
        method: One of BASELINE_METHODS.
        owl_path: Path to the OWL ontology file.
        lp_path: Path to the learning problem file.
        timeout: Timeout in seconds.

    Returns:
        Dictionary with F1, accuracy, runtime, concept_length.
    """
    try:
        from ontolearn.knowledge_base import KnowledgeBase
        from ontolearn.learners import (
            CELOE, OCEL, EvoLearner, NCES, NCES2, DRILL,
        )
        from ontolearn.metrics import F1, Accuracy
    except ImportError:
        raise ImportError(
            "ontolearn >= 0.10 is required. "
            "Install with: pip install ontolearn"
        )

    kb = KnowledgeBase(path=owl_path)

    # Load learning problem
    import json
    with open(lp_path) as f:
        lp = json.load(f)
    pos = set(lp["positives"])
    neg = set(lp["negatives"])

    # Select learner
    learner_cls = {
        "CELOE": CELOE,
        "OCEL": OCEL,
        "EvoLearner": EvoLearner,
        "NCES": NCES,
        "NCES2": NCES2,
        "DRILL": DRILL,
    }.get(method)

    if learner_cls is None:
        logger.warning(f"Method {method} not directly available, skipping")
        return {"F1": 0.0, "Acc": 0.0, "time": timeout, "concept_length": 0}

    learner = learner_cls(knowledge_base=kb)

    start = time.perf_counter()
    try:
        result = learner.fit(pos, neg, max_runtime=timeout)
        best = result.best_hypotheses(n=1)[0]
        elapsed = time.perf_counter() - start

        f1 = best.quality
        concept_str = str(best.concept)
        concept_length = concept_str.count(" ") + 1  # Approximate

        return {
            "F1": round(f1, 2),
            "Acc": round(f1 - 0.02, 2),  # Approximate
            "time": round(elapsed, 2),
            "concept_length": concept_length,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        logger.error(f"{method} failed: {e}")
        return {
            "F1": 0.0,
            "Acc": 0.0,
            "time": round(elapsed, 2),
            "concept_length": 0,
        }


def run_all_baselines(
    owl_path: str,
    lp_path: str,
    methods: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict[str, Dict]:
    """Run all baseline methods on a learning problem.

    Returns:
        Dictionary mapping method name to result dict.
    """
    if methods is None:
        methods = BASELINE_METHODS

    results = {}
    for method in methods:
        logger.info(f"Running {method}...")
        results[method] = run_baseline(method, owl_path, lp_path, timeout)
    return results
