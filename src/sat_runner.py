"""PySAT Glucose3 driver for symmetry-restricted K_5-free Ramsey searches.

Reproduces the agent's gen 22 and gen 24 main results from the command line.

Examples:
    # Single-block circulant Z_43 (gen 22 main result)
    python src/sat_runner.py --n 43 --mode single

    # 2-block circulant Z_21 x Z_22 on N=43 (gen 24 main result)
    python src/sat_runner.py --n 43 --mode 2block --block-a 21 --block-b 22

    # Full scaling ladder
    python src/sat_runner.py --scaling-ladder
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow `python src/sat_runner.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from encoder import (
    _orbit_single,
    _orbit_2block,
    build_clauses,
    num_variables_single,
    num_variables_2block,
)

try:
    from pysat.solvers import Glucose3
except ImportError:
    print("ERROR: install python-sat first:  pip install python-sat", file=sys.stderr)
    sys.exit(1)


def solve(n: int, mode: str, n_a: int = 21, n_b: int = 22) -> dict:
    """Solve K_5-free SAT for given n and symmetry mode. Returns result dict."""
    naive_clauses = 2 * (n * (n - 1) * (n - 2) * (n - 3) * (n - 4) // 120)

    if mode == "single":
        edge_var = _orbit_single(n)
        num_vars = num_variables_single(n)
        arch = f"Single-block Z_{n}"
    elif mode == "2block":
        if n_a + n_b != n:
            raise ValueError(f"block sizes {n_a}+{n_b} != n={n}")
        edge_var = _orbit_2block(n_a, n_b)
        num_vars = num_variables_2block(n_a, n_b)
        arch = f"2-block Z_{n_a} x Z_{n_b}"
    else:
        raise ValueError(f"unknown mode: {mode}")

    t_encode_start = time.perf_counter()
    clauses = build_clauses(n, edge_var)
    t_encode = time.perf_counter() - t_encode_start

    dedup_pct = 100.0 * (1.0 - len(clauses) / naive_clauses) if naive_clauses else 0.0

    t_solve_start = time.perf_counter()
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(list(cl))
    is_sat = solver.solve()
    model = solver.get_model() if is_sat else None
    t_solve = time.perf_counter() - t_solve_start
    solver.delete()

    return {
        "n": n,
        "architecture": arch,
        "variables": num_vars,
        "naive_clauses": naive_clauses,
        "unique_clauses": len(clauses),
        "dedup_pct": dedup_pct,
        "status": "SAT" if is_sat else "UNSAT",
        "model": model,
        "encode_time": t_encode,
        "solve_time": t_solve,
    }


def print_result(r: dict) -> None:
    print(f"[{r['architecture']}] N={r['n']}: {r['variables']} vars, "
          f"{r['unique_clauses']:,} unique clauses "
          f"(naive {r['naive_clauses']:,}, {r['dedup_pct']:.1f}% dedup)")
    print(f"[Glucose3] {r['status']} — encode {r['encode_time']:.2f}s, "
          f"solve {r['solve_time']:.2f}s")
    if r["status"] == "SAT" and r["model"] is not None:
        print(f"[Model] {r['model']}")
    print()


def scaling_ladder() -> None:
    """Reproduce the full scaling-ladder table from the README."""
    print("=== Single-block circulant scaling ladder ===")
    for n in [6, 18, 30, 35, 37, 39, 41, 42, 43]:
        r = solve(n, mode="single")
        print_result(r)

    print("=== 2-block Z_21 x Z_22 on N=43 (gen 24 main result) ===")
    r = solve(43, mode="2block", n_a=21, n_b=22)
    print_result(r)


def main() -> None:
    p = argparse.ArgumentParser(
        description="K_5-free Ramsey SAT under symmetry restriction"
    )
    p.add_argument("--n", type=int, help="Vertex count (e.g., 43)")
    p.add_argument(
        "--mode", choices=["single", "2block"],
        help="Symmetry restriction mode"
    )
    p.add_argument("--block-a", type=int, default=21, help="Block A size (2block mode)")
    p.add_argument("--block-b", type=int, default=22, help="Block B size (2block mode)")
    p.add_argument(
        "--scaling-ladder", action="store_true",
        help="Reproduce the full scaling ladder from the README"
    )

    args = p.parse_args()

    if args.scaling_ladder:
        scaling_ladder()
        return

    if not args.n or not args.mode:
        p.print_help()
        sys.exit(1)

    r = solve(args.n, args.mode, args.block_a, args.block_b)
    print_result(r)


if __name__ == "__main__":
    main()
