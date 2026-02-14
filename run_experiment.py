#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from src.simulation import run_monte_carlo


def main() -> None:
    parser = argparse.ArgumentParser(description="Stochastic transit simulation demo")
    parser.add_argument("--runs", type=int, default=300)
    parser.add_argument("--dist", type=str, default="exp", choices=["exp", "normal"])
    parser.add_argument("--out", type=str, default="docs/results.json")
    args = parser.parse_args()

    result = run_monte_carlo(n=args.runs, dist=args.dist)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"wrote: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
