"""Symmetry-restricted K_5-free SAT encodings for Ramsey R(5,5) investigation.

This module reproduces the encoding pipeline that the ThinkerWave agent
authored autonomously across gens 22-24. It is intentionally minimal and
matches the agent's own output as closely as possible.

Two encodings are provided:

  1. single_block_circulant(n) — Cayley graph of Z_n. Edge color depends
     only on |i - j| mod n. Yields floor(n/2) variables.

  2. two_block_circulant(n_a, n_b) — Block A is Z_{n_a}, Block B is
     Z_{n_b}, with asymmetric cross-edges. Yields
     floor(n_a/2) + floor(n_b/2) + n_b variables.

For each 5-subset of vertices, two clauses are added: one forbidding the
all-red K_5 and one forbidding the all-blue K_5. Clauses are deduplicated
via Python set() before being passed to the SAT solver — this is the
~89% reduction reported in the README.
"""
from __future__ import annotations

from itertools import combinations
from typing import Callable


def _orbit_single(n: int) -> Callable[[int, int], int]:
    """Edge → variable mapping for single-block circulant Z_n.

    Variables are 1..floor(n/2); variable k represents distance k mod n.
    """
    max_dist = n // 2

    def edge_var(i: int, j: int) -> int:
        d = abs(i - j) % n
        if d > max_dist:
            d = n - d
        return d  # 1..max_dist

    return edge_var


def _orbit_2block(n_a: int, n_b: int) -> Callable[[int, int], int]:
    """Edge → variable mapping for 2-block circulant (Z_{n_a} × Z_{n_b} + cross).

    Vertex layout: 0..n_a-1 = Block A, n_a..n_a+n_b-1 = Block B.

    Variables:
      1..floor(n_a/2)                                  — intra-A distances
      floor(n_a/2)+1..floor(n_a/2)+floor(n_b/2)        — intra-B distances
      floor(n_a/2)+floor(n_b/2)+1..+n_b                — cross-block (j - i_in_B) mod n_b
    """
    max_a = n_a // 2
    max_b = n_b // 2
    offset_b = max_a
    offset_x = max_a + max_b

    def edge_var(i: int, j: int) -> int:
        if i > j:
            i, j = j, i
        # both in A
        if j < n_a:
            d = (j - i) % n_a
            if d > max_a:
                d = n_a - d
            return d  # 1..max_a
        # both in B
        if i >= n_a:
            d = (j - i) % n_b
            if d > max_b:
                d = n_b - d
            return offset_b + d  # max_a+1..max_a+max_b
        # cross (i in A, j in B)
        d = (j - n_a - i) % n_b
        return offset_x + d + 1  # offset_x+1..offset_x+n_b

    return edge_var


def build_clauses(n: int, edge_var: Callable[[int, int], int]) -> set[tuple[int, ...]]:
    """Build deduplicated K_5-free clause set for n vertices.

    For each 5-subset S of vertices:
      - sort the 10 edge variable IDs, take the tuple
      - add (+v1,...,+v10): forbids all 10 edges being color RED
      - add (-v1,...,-v10): forbids all 10 edges being color BLUE

    The set() automatically deduplicates orbit-equivalent clauses.
    """
    clauses: set[tuple[int, ...]] = set()
    for subset in combinations(range(n), 5):
        edges = sorted({edge_var(i, j) for i, j in combinations(subset, 2)})
        # If <10 distinct variables, dedup already happened at the edge level
        # because the K_5 maps onto fewer than 10 orbits. Still emit both
        # polarity clauses on the orbit set.
        pos = tuple(edges)
        neg = tuple(-v for v in edges)
        clauses.add(pos)
        clauses.add(neg)
    return clauses


def num_variables_single(n: int) -> int:
    return n // 2


def num_variables_2block(n_a: int, n_b: int) -> int:
    return (n_a // 2) + (n_b // 2) + n_b
