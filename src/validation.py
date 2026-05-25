"""Sanity-check the encoding pipeline against known Ramsey numbers R(3,3) and R(4,4).

If these checks pass, the encoding is structurally sound.

Note: This file uses K_3-free and K_4-free SAT (NOT K_5-free), since the
known thresholds are R(3,3)=6 (smallest n where K_3-free coloring is
impossible) and R(4,4)=18.
"""
from __future__ import annotations

import sys
import time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from encoder import _orbit_single

try:
    from pysat.solvers import Glucose3
except ImportError:
    print("ERROR: install python-sat first:  pip install python-sat", file=sys.stderr)
    sys.exit(1)


def k_clique_free_sat(n: int, k: int) -> tuple[str, float]:
    """Build a K_k-free SAT instance under single-block circulant symmetry."""
    edge_var = _orbit_single(n)
    clauses: set[tuple[int, ...]] = set()
    for subset in combinations(range(n), k):
        edges = sorted({edge_var(i, j) for i, j in combinations(subset, 2)})
        clauses.add(tuple(edges))
        clauses.add(tuple(-v for v in edges))

    t_start = time.perf_counter()
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(list(cl))
    is_sat = solver.solve()
    elapsed = time.perf_counter() - t_start
    solver.delete()
    return ("SAT" if is_sat else "UNSAT"), elapsed


def main() -> None:
    print("=== R(3,3) = 6  ===")
    for n in [5, 6]:
        status, t = k_clique_free_sat(n, k=3)
        expected = "SAT" if n < 6 else "UNSAT"
        ok = "OK" if status == expected else "FAIL"
        print(f"  n={n}: {status} in {t*1000:.2f}ms (expected {expected}) {ok}")

    print()
    print("=== R(4,4) = 18 ===")
    for n in [17, 18]:
        status, t = k_clique_free_sat(n, k=4)
        expected = "SAT" if n < 18 else "UNSAT"
        ok = "OK" if status == expected else "FAIL"
        print(f"  n={n}: {status} in {t*1000:.2f}ms (expected {expected}) {ok}")


if __name__ == "__main__":
    main()
