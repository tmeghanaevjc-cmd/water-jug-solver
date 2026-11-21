"""Command-line interface:  python -m water_jug --a 4 --b 3 --target 2"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .solver import WaterJugProblem, bfs, dfs, replay
from .visualize import render_result, to_dot


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="water_jug",
        description="Solve the Water Jug Problem with state-space search.")
    p.add_argument("--a", type=int, default=4, help="capacity of jug A (default 4)")
    p.add_argument("--b", type=int, default=3, help="capacity of jug B (default 3)")
    p.add_argument("--target", type=int, default=2, help="target litres (default 2)")
    p.add_argument("--strategy", choices=["bfs", "dfs", "both"], default="both")
    p.add_argument("--dot", metavar="FILE", help="export state-space graph (Graphviz DOT)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        problem = WaterJugProblem(args.a, args.b, args.target)
    except (TypeError, ValueError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    banner = (f" WATER JUG PROBLEM  |  Jug A: {args.a} L  |  Jug B: {args.b} L"
              f"  |  Target: {args.target} L ")
    print("=" * len(banner), banner, "=" * len(banner), sep="\n")

    solvers = {"bfs": [bfs], "dfs": [dfs], "both": [bfs, dfs]}[args.strategy]
    results = [solve(problem) for solve in solvers]
    for res in results:
        print("\n" + render_result(problem, res))
        if res.solvable and not replay(problem, res.steps):
            print("Internal error: solution failed verification.", file=sys.stderr)
            return 3

    if len(results) == 2 and all(r.solvable for r in results):
        b, d = results
        print(f"\nComparison: BFS needed {b.moves} moves (optimal); "
              f"DFS needed {d.moves} moves.")

    if args.dot:
        best = next((r for r in results if r.solvable), None)
        Path(args.dot).write_text(to_dot(problem, best), encoding="utf-8")
        print(f"\nState-space graph written to {args.dot}")
    return 0 if any(r.solvable for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
