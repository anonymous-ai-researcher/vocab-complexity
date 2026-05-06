"""Reachability elimination for L({∃}) chain encodings (Algorithm 1).

Implements the preprocessing rule from Proposition 1:
  For each depth d, compute the set R_d of reachable roles.
  Role-selection variables x_{d,r} with r ∉ R_d can be safely
  fixed to false without affecting the optimum value.
"""

import time
import logging
from typing import Dict, FrozenSet, List, Set, Tuple

from src.ontology import Interpretation, LabeledSample

logger = logging.getLogger(__name__)


def compute_reachable_layers(
    sample: LabeledSample,
    k: int,
) -> List[Set[str]]:
    """Compute reachable role sets R_1, ..., R_{k-1}.

    Algorithm 1 from the paper:
      V_0 = P  (positive examples)
      For d = 1, ..., k-1:
        For each r in Sigma_R:
          V_d^r = { b in Delta : exists a in V_{d-1} with (a,b) in r^I }
        R_d = { r in Sigma_R : V_d^r ≠ ∅ }
        V_d = ∪_r V_d^r

    Args:
        sample: The labeled sample (I, P, N).
        k: Concept size bound.

    Returns:
        List of sets [R_1, R_2, ..., R_{k-1}], where each R_d ⊆ Sigma_R.
    """
    interp = sample.interpretation
    sig_r = interp.sig_r

    # Precompute forward adjacency: for each role r, map a -> {b : (a,b) in r^I}
    fwd = {}
    for r in sig_r:
        adj = {}
        for a, b in interp.role_ext.get(r, frozenset()):
            if a not in adj:
                adj[a] = set()
            adj[a].add(b)
        fwd[r] = adj

    current_layer = set(sample.positives)  # V_0 = P
    reachable_roles = []

    for d in range(1, k):
        R_d = set()
        next_layer = set()

        for r in sig_r:
            adj = fwd[r]
            successors = set()
            for a in current_layer:
                if a in adj:
                    successors.update(adj[a])
            if successors:
                R_d.add(r)
                next_layer.update(successors)

        reachable_roles.append(R_d)
        current_layer = next_layer

        if not current_layer:
            # No more reachable elements; remaining layers are empty
            for _ in range(d, k - 1):
                reachable_roles.append(set())
            break

    return reachable_roles


def reachability_elimination(
    sample: LabeledSample,
    k: int,
) -> Dict:
    """Run reachability elimination and return statistics.

    Args:
        sample: The labeled sample.
        k: Concept size bound.

    Returns:
        Dictionary with keys:
          - reachable_roles: List[Set[str]], R_1 through R_{k-1}
          - base_vars: int, (k-1) * |Sigma_R|
          - reach_vars: int, sum of |R_d| for d = 1..k-1
          - eliminated_vars: int, base_vars - reach_vars
          - elimination_rate: float, eliminated_vars / base_vars
          - prep_time_ms: float, preprocessing time in milliseconds
    """
    sig_r = sample.interpretation.sig_r
    base_vars = (k - 1) * len(sig_r)

    start = time.perf_counter()
    reachable = compute_reachable_layers(sample, k)
    elapsed_ms = (time.perf_counter() - start) * 1000

    reach_vars = sum(len(R_d) for R_d in reachable)
    eliminated = base_vars - reach_vars

    result = {
        "reachable_roles": reachable,
        "base_vars": base_vars,
        "reach_vars": reach_vars,
        "eliminated_vars": eliminated,
        "elimination_rate": eliminated / base_vars if base_vars > 0 else 0.0,
        "prep_time_ms": round(elapsed_ms, 2),
    }

    logger.info(
        f"Reachability elimination: {base_vars} -> {reach_vars} vars "
        f"({result['elimination_rate']:.1%} eliminated, {elapsed_ms:.1f} ms)"
    )
    return result


def get_unit_clauses(
    reachable_roles: List[Set[str]],
    sig_r: Tuple[str, ...],
    var_map: Dict[Tuple[int, str], int],
) -> List[List[int]]:
    """Generate unit hard clauses for unreachable role-selection variables.

    For each depth d and role r ∉ R_d, add the unit clause [-x_{d,r}].

    Args:
        reachable_roles: R_1, ..., R_{k-1} from compute_reachable_layers.
        sig_r: Tuple of role names.
        var_map: Mapping (d, r) -> propositional variable index.

    Returns:
        List of unit clauses (each a singleton list [-var]).
    """
    clauses = []
    for d, R_d in enumerate(reachable_roles, start=1):
        for r in sig_r:
            if r not in R_d:
                var = var_map.get((d, r))
                if var is not None:
                    clauses.append([-var])
    return clauses


def depthwise_rates(
    sample: LabeledSample,
    max_depth: int = 6,
) -> List[float]:
    """Compute |R_d| / |Sigma_R| for d = 1, ..., max_depth.

    Used for Table 8 (depth-wise reachability analysis).

    Args:
        sample: The labeled sample.
        max_depth: Maximum depth to compute.

    Returns:
        List of rates [|R_1|/|Σ_R|, ..., |R_{max_depth}|/|Σ_R|].
    """
    sig_r = sample.interpretation.sig_r
    n_roles = len(sig_r)
    if n_roles == 0:
        return [0.0] * max_depth

    reachable = compute_reachable_layers(sample, max_depth + 1)
    rates = [len(R_d) / n_roles for R_d in reachable[:max_depth]]
    return rates
