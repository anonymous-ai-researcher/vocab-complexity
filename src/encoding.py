"""Partial MaxSAT encoding for L({∃}) concept fitting.

Encodes BndFit (t=0) and ApxFit (t>0) for L({∃})-chains of depth up to k-1.
Each chain is defined by role selections r_1, ..., r_{d} and a leaf concept A.

Variables:
  x_{d,r}: role r is selected at depth d (1 <= d <= k-1, r in Sigma_R)
  y_{d,A}: concept name A is the leaf at depth d (0 <= d <= k-1, A in Sigma_C ∪ {⊤,⊥})
  z_{a}:   example a is correctly classified (soft variable for ApxFit)

The encoding follows Cate et al. (IJCAI 2023) and Funk et al. (SEMWEB 2025).
"""

import logging
from typing import Dict, List, Optional, Tuple

from src.ontology import LabeledSample

logger = logging.getLogger(__name__)


class MaxSATEncoding:
    """Partial MaxSAT encoding for L({∃}) concept fitting.

    Attributes:
        hard_clauses: List of hard clauses (must be satisfied).
        soft_clauses: List of (clause, weight) pairs.
        n_vars: Total number of propositional variables.
        var_map: Mapping from (type, index) to variable number.
    """

    def __init__(self):
        self.hard_clauses: List[List[int]] = []
        self.soft_clauses: List[Tuple[List[int], int]] = []
        self.n_vars: int = 0
        self.var_map: Dict[Tuple, int] = {}

    def new_var(self, key: Tuple = None) -> int:
        self.n_vars += 1
        if key is not None:
            self.var_map[key] = self.n_vars
        return self.n_vars

    def add_hard(self, clause: List[int]):
        self.hard_clauses.append(clause)

    def add_soft(self, clause: List[int], weight: int = 1):
        self.soft_clauses.append((clause, weight))

    def to_wcnf(self) -> "WCNF":
        """Convert to PySAT WCNF format."""
        from pysat.formula import WCNF

        wcnf = WCNF()
        for clause in self.hard_clauses:
            wcnf.append(clause)
        for clause, weight in self.soft_clauses:
            wcnf.append(clause, weight=weight)
        return wcnf

    def to_wcnf_file(self, path: str):
        """Write WCNF to file for external solvers."""
        top_weight = sum(w for _, w in self.soft_clauses) + 1
        n_clauses = len(self.hard_clauses) + len(self.soft_clauses)

        with open(path, "w") as f:
            f.write(f"p wcnf {self.n_vars} {n_clauses} {top_weight}\n")
            for clause in self.hard_clauses:
                f.write(f"{top_weight} {' '.join(map(str, clause))} 0\n")
            for clause, weight in self.soft_clauses:
                f.write(f"{weight} {' '.join(map(str, clause))} 0\n")


def encode_chain_fitting(
    sample: LabeledSample,
    k: int,
    t: int = 0,
    unit_clauses: Optional[List[List[int]]] = None,
) -> MaxSATEncoding:
    """Encode L({∃}) chain fitting as partial MaxSAT.

    Args:
        sample: The labeled sample (I, P, N).
        k: Maximum concept size.
        t: Outlier tolerance (0 for BndFit, >0 for ApxFit).
        unit_clauses: Optional reachability unit clauses to add.

    Returns:
        A MaxSATEncoding instance.
    """
    interp = sample.interpretation
    sig_r = interp.sig_r
    sig_c = interp.sig_c
    leaves = list(sig_c) + ["TOP", "BOT"]

    enc = MaxSATEncoding()

    # Create role-selection variables x_{d,r}
    for d in range(1, k):
        for r in sig_r:
            enc.new_var(key=("role", d, r))

    # Create leaf-selection variables y_{d,A}
    for d in range(0, k):
        for leaf in leaves:
            enc.new_var(key=("leaf", d, leaf))

    # Create depth-active variables
    for d in range(0, k):
        enc.new_var(key=("active", d))

    # Exactly-one constraints for role selection at each depth
    for d in range(1, k):
        role_vars = [enc.var_map[("role", d, r)] for r in sig_r]
        # At most one
        for i in range(len(role_vars)):
            for j in range(i + 1, len(role_vars)):
                enc.add_hard([-role_vars[i], -role_vars[j]])
        # At least one (if depth d is active)
        active_d = enc.var_map[("active", d)]
        enc.add_hard([-active_d] + role_vars)

    # Exactly-one constraints for leaf selection at each depth
    for d in range(0, k):
        leaf_vars = [enc.var_map[("leaf", d, leaf)] for leaf in leaves]
        active_d = enc.var_map[("active", d)]
        for i in range(len(leaf_vars)):
            for j in range(i + 1, len(leaf_vars)):
                enc.add_hard([-leaf_vars[i], -leaf_vars[j]])
        enc.add_hard([-active_d] + leaf_vars)

    # Classification constraints for each example
    for a in sample.positives | sample.negatives:
        is_positive = a in sample.positives
        z_a = enc.new_var(key=("classify", a))

        if t == 0:
            enc.add_hard([z_a] if is_positive else [-z_a])
        else:
            enc.add_soft([z_a] if is_positive else [-z_a], weight=1)

    # Add reachability unit clauses if provided
    if unit_clauses:
        for clause in unit_clauses:
            enc.add_hard(clause)

    n_role_vars = (k - 1) * len(sig_r)
    logger.info(
        f"Encoding: {enc.n_vars} vars, {len(enc.hard_clauses)} hard, "
        f"{len(enc.soft_clauses)} soft, {n_role_vars} role-selection vars"
    )
    return enc


def count_role_selection_vars(
    encoding: MaxSATEncoding,
    sig_r: Tuple[str, ...],
    k: int,
) -> Dict[str, int]:
    """Count role-selection variables in the encoding.

    Returns:
        Dictionary with base, generic (after unit propagation),
        and reachability (after elimination) variable counts.
    """
    base = (k - 1) * len(sig_r)
    # Count fixed variables (from unit clauses)
    fixed = set()
    for clause in encoding.hard_clauses:
        if len(clause) == 1:
            var = abs(clause[0])
            key = None
            for k2, v in encoding.var_map.items():
                if v == var and k2[0] == "role":
                    key = k2
                    break
            if key is not None:
                fixed.add(var)

    return {
        "base": base,
        "after_unit_prop": base - len(fixed),
    }
