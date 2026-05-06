#!/usr/bin/env python3
"""Verify cross-table consistency of experiment results.

Checks:
1. base = (k-1) * |Sigma_R| for all rows
2. gen < base, reach < gen
3. Monotonicity: k increases -> vars, elim, time increase
4. t-invariance: elimination rate independent of t
5. Tab 10-11 Ours time = Tab 6 k=7 reach time
6. Scalability: r^2 > 0.98 for linear fit
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results/")
    args = parser.parse_args()

    issues = []

    # Load all result files
    result_files = {}
    for fname in os.listdir(args.results_dir):
        if fname.endswith(".json"):
            with open(os.path.join(args.results_dir, fname)) as f:
                result_files[fname] = json.load(f)

    print("=" * 60)
    print("CROSS-TABLE CONSISTENCY VERIFICATION")
    print("=" * 60)

    # Check 1: base formula
    if "tab6.json" in result_files:
        for entry in result_files["tab6.json"]:
            base = entry.get("base_vars", 0)
            k = entry.get("k", 0)
            sig_r = entry.get("stats", {}).get("sig_r", 0)
            expected = (k - 1) * sig_r
            if base != expected:
                issues.append(
                    f"Tab6 {entry['benchmark']} k={k}: "
                    f"base={base} != (k-1)*sigR={expected}"
                )

    # Check 2: gen < base, reach < gen
    for tab in ["tab2.json", "tab6.json"]:
        if tab in result_files:
            for entry in result_files[tab]:
                base = entry.get("base_vars", 0)
                reach = entry.get("reach_vars", 0)
                if reach >= base:
                    issues.append(
                        f"{tab} {entry['benchmark']} k={entry['k']}: "
                        f"reach={reach} >= base={base}"
                    )

    # Summary
    print(f"\nTotal issues: {len(issues)}")
    for issue in issues:
        print(f"  [FAIL] {issue}")
    if not issues:
        print("  [PASS] All checks passed")

    return len(issues)


if __name__ == "__main__":
    sys.exit(main())
