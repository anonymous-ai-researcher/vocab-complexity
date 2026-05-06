"""Utility functions: logging, timing, I/O, statistics."""

import json
import logging
import os
import time
import numpy as np
from functools import wraps
from typing import Any, Dict, List


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logging.getLogger(func.__module__).info(
            f"{func.__name__} completed in {elapsed:.3f}s"
        )
        return result
    return wrapper


def save_results(results: Any, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logging.getLogger(__name__).info(f"Results saved to {path}")


def load_results(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def median_and_std(values: List[float]) -> Dict[str, float]:
    arr = np.array(values)
    return {
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "mean": float(np.mean(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def compute_speedup(gen_time: float, reach_time: float) -> float:
    if reach_time <= 0:
        return float("inf")
    return round(gen_time / reach_time, 2)


def compute_r_squared(x: List[float], y: List[float]) -> float:
    x, y = np.array(x), np.array(y)
    n = len(x)
    mx, my = x.mean(), y.mean()
    ss_xy = ((x - mx) * (y - my)).sum()
    ss_xx = ((x - mx) ** 2).sum()
    ss_yy = ((y - my) ** 2).sum()
    if ss_yy == 0 or ss_xx == 0:
        return 1.0
    return float((ss_xy ** 2) / (ss_xx * ss_yy))
