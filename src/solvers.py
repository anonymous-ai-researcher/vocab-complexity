"""Interface to MaxSAT solvers: Open-WBO, RC2, MaxCDCL."""

import os
import subprocess
import tempfile
import time
import logging
from typing import Dict, Optional, Tuple

from src.encoding import MaxSATEncoding

logger = logging.getLogger(__name__)

SOLVER_PATHS = {
    "open-wbo": os.environ.get("OPENWBO_PATH", "solvers/open-wbo"),
    "maxcdcl": os.environ.get("MAXCDCL_PATH", "solvers/maxcdcl"),
}


def solve_rc2(encoding: MaxSATEncoding, timeout: int = 600) -> Dict:
    """Solve using RC2 (PySAT built-in)."""
    from pysat.examples.rc2 import RC2

    wcnf = encoding.to_wcnf()
    start = time.perf_counter()
    with RC2(wcnf) as solver:
        model = solver.compute()
        cost = solver.cost
    elapsed = time.perf_counter() - start

    return {
        "solver": "rc2",
        "model": model,
        "cost": cost,
        "time": round(elapsed, 3),
        "status": "OPTIMUM" if model else "UNSATISFIABLE",
    }


def solve_external(
    encoding: MaxSATEncoding,
    solver_name: str,
    timeout: int = 600,
) -> Dict:
    """Solve using an external MaxSAT solver binary."""
    solver_path = SOLVER_PATHS.get(solver_name)
    if not solver_path or not os.path.exists(solver_path):
        raise FileNotFoundError(
            f"Solver binary not found: {solver_path}. "
            f"Set {solver_name.upper().replace('-','')}_PATH or place binary in solvers/"
        )

    with tempfile.NamedTemporaryFile(suffix=".wcnf", delete=False, mode="w") as f:
        wcnf_path = f.name
        encoding.to_wcnf_file(wcnf_path)

    try:
        start = time.perf_counter()
        result = subprocess.run(
            [solver_path, wcnf_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - start

        cost = None
        model = None
        status = "UNKNOWN"

        for line in result.stdout.split("\n"):
            if line.startswith("o "):
                cost = int(line.split()[1])
            elif line.startswith("s "):
                status = line.split()[1]
            elif line.startswith("v "):
                model = list(map(int, line.split()[1:]))

        return {
            "solver": solver_name,
            "model": model,
            "cost": cost,
            "time": round(elapsed, 3),
            "status": status,
        }

    except subprocess.TimeoutExpired:
        return {
            "solver": solver_name,
            "model": None,
            "cost": None,
            "time": timeout,
            "status": "TIMEOUT",
        }
    finally:
        os.unlink(wcnf_path)


def solve(
    encoding: MaxSATEncoding,
    solver_name: str = "rc2",
    timeout: int = 600,
) -> Dict:
    """Solve a MaxSAT encoding using the specified solver.

    Args:
        encoding: The MaxSATEncoding instance.
        solver_name: One of "open-wbo", "rc2", "maxcdcl".
        timeout: Timeout in seconds.

    Returns:
        Dictionary with solver, model, cost, time, status.
    """
    if solver_name == "rc2":
        return solve_rc2(encoding, timeout)
    else:
        return solve_external(encoding, solver_name, timeout)
