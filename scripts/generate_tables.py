#!/usr/bin/env python3
"""Generate LaTeX tables from experiment results."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def generate_tab2(data, output_dir):
    """Generate Table 2 (main text preprocessing)."""
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "tab2.tex"), "w") as f:
        f.write("% Table 2: Reachability preprocessing (auto-generated)\n")
        for entry in data:
            f.write(
                f"{entry['benchmark']} & {entry['k']} & "
                f"{entry['base_vars']} & ... \\\\\n"
            )
    print(f"Generated {output_dir}/tab2.tex")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results/")
    parser.add_argument("--output-dir", default="tables/")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for tab_file in os.listdir(args.results_dir):
        if tab_file.endswith(".json"):
            data = load_json(os.path.join(args.results_dir, tab_file))
            tab_name = tab_file.replace(".json", "")
            print(f"Processing {tab_name}...")

    print(f"All tables generated in {args.output_dir}/")


if __name__ == "__main__":
    main()
