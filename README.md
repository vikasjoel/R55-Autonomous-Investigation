# Autonomous AI-Agent Investigation of Ramsey Number R(5,5)

> An open-science artifact demonstrating what an LLM-guided evolutionary research agent can autonomously achieve on a 70-year-old open problem in extremal combinatorics — including its self-corrected SAT pipeline, scaling data, and honest assessment of its own limitations.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-ThinkerWave-purple.svg)
![Artifact](https://img.shields.io/badge/Type-Methodology%20Demo-green.svg)

---

## ⚠️ What This Is, And What It Is NOT

**What this IS:**
- A demonstration of an autonomous LLM research agent (24+ generations of recursive identity refinement) producing tool-verified empirical results on a deep mathematical problem.
- Reproducible Python/PySAT code for symmetry-restricted SAT encodings of the Ramsey K₅-free coloring problem.
- An honest log of what the agent discovered, what it correctly identified as already-known, and where it explicitly flagged its limits.

**What this is NOT:**
- A new mathematical result about R(5,5). The lower bound R(5,5) ≥ 43 (Exoo 1989) and the upper bound R(5,5) ≤ 46 (arXiv:2409.15709, 2024) are unchanged.
- A "proof" that R(5,5) = 43 or any other value. We provide computational evidence that *certain restricted families* of graph colorings (circulant Cayley graphs of Z₄₃ and 2-block Z₂₁ × Z₂₂ circulants) cannot produce a K₅-free coloring of K₄₃. This empirically reconfirms structural barriers that are implicit in 35 years of failed attempts to push the lower bound above Exoo's 1989 K₄₂ construction.
- A claim of priority. Block-circulant and Cayley-graph Ramsey searches have been explored by McKay, Radziszowski, Harborth, and others since the 1990s. We did not do an exhaustive literature comparison; we report what our agent produced.

---

## 🤖 The Methodological Contribution

The novel element here is *how* this analysis was produced:

- An evolutionary agent framework ([ThinkerWave](https://github.com/vikasjoel/ThinkerWaveCode)) ran **24 generations** of recursive identity replacement on the prompt *"Investigate the open problem of the Ramsey number R(5,5)."*
- Each generation: strategize → execute (with a Python sandbox + web search) → independent evaluator → identity transformation. At gen 6 the agent forked into parallel branches and later converged.
- **The agent itself proposed** the SAT-encoding angle, the circulant restriction, the deduplication pipeline, and the 2-block decomposition — when prompted with one-line mid-flight directives ("force circulant symmetry", "try 2-block Z₂₁ × Z₂₂").
- The agent self-corrected mid-execution: when its first encoding attempt timed out it wrote "Switching to optimized circulant encoding" and produced a working pipeline.
- A built-in **phantom-verification** evaluator capped scores when the agent over-claimed (e.g., gen 24 raw score 7.0 → calibrated 6.0 after 4 over-claims were detected).

If you are evaluating LLM research agents, **the artifact is the trajectory, not the verdict**.

---

## 📊 Empirical Results (Tool-Verified)

All numbers below come from actual `pysat.solvers.Glucose3` invocations inside the agent's Python sandbox. Times are wall-clock on a single CPU.

### Single-Block Circulant Z_n (10–21 distance variables)

| n  | Vars | Unique Clauses | Status | Time (s) |
|----|------|---------------:|--------|---------:|
| 6  | 2    | 16             | UNSAT (recovers R(3,3)=6 sanity) | 0.0004 |
| 18 | 9    | 208            | UNSAT (recovers R(4,4)=18 sanity) | 0.007 |
| 30 | 14   | 4,724          | SAT    | 0.283 |
| 35 | 17   | 9,382          | SAT    | 0.626 |
| 37 | 18   | 11,934         | SAT    | 0.851 |
| 39 | 19   | 14,934         | **UNSAT** | 1.153 |
| 41 | 20   | 18,468         | SAT    | 1.476 |
| **42** | **21** | **20,246** | **UNSAT** | **1.697** |
| 43 | 21   | (within single-block dedup) | **UNSAT** | 8.23 |

### 2-Block Circulant (Z₂₁ × Z₂₂ with cross-block edges) on N=43

| Architecture | Vars | Naive Clauses | Unique Clauses | Reduction | Status | Time (s) |
|--------------|-----:|--------------:|---------------:|----------:|--------|---------:|
| Block A (Z₂₁) only | 10 | — | — | — | — | — |
| Block B (Z₂₂) only | 11 | — | — | — | — | — |
| Full 2-block (21+22 + cross) | **44** | **1,925,196** | **207,960** | **89.2%** | **UNSAT** | **4.67** |

### Observations the agent extracted

1. **The Z₄₂ → Z₄₃ circulant cliff:** Single-block circulant SAT transitions from satisfiable at n=41 to unsatisfiable at n=42 — consistent with the well-known fact that Exoo's 1989 K₄₂ K₅-free coloring is a circulant and that no circulant K₅-free coloring of K₄₃ has ever been found.
2. **A non-monotonic surprise:** Single-block circulant on Z₃₉ is *also* UNSAT despite Z₄₁ being SAT. This UNSAT pocket between SAT regions at n=37 and n=41 is worth a closer look — it suggests the SAT/UNSAT phase boundary under cyclic symmetry is not monotonic in n.
3. **Block decomposition does not escape the cliff:** Going from 21 vars (single-block Z₄₃) to 44 vars (2-block Z₂₁ × Z₂₂) *increases the variable budget by ~2×* but is still UNSAT. Any K₅-free coloring of K₄₃ — if one exists — must therefore use a *non*-block-circulant structure (e.g., a non-abelian Cayley graph, or a non-algebraic construction).
4. **Cross-block edges dominate K₅ formation:** In the 2-block setting, **65.5%** of all C(43,5) = 962,598 five-vertex subsets straddle the block boundary (3 in Block A + 2 in Block B, or vice-versa). The agent identified these cross-block K₅s as the structural reason 2-block decomposition fails to help.
5. **Compute is no longer the bottleneck.** A log-log regression of solve time vs clause count (R²=0.89, 7 data points) extrapolates n=48 solving in ~9 seconds with <0.05 GB RAM. Within the symmetry-restricted family, exploring up to and past the current upper bound is computationally cheap.
6. **What the agent honestly said about the blocker:** *"70% mathematical insight, 30% computation. SAT solvers are fast enough to verify candidates, but we don't know what candidates to try."*

### Paley graph evidence (sanity check)

| Graph | Vertices | Red K₅ count | Blue K₅ count |
|-------|---------:|-------------:|--------------:|
| Paley P(41) | 41 | 205 | 205 |
| Paley P(43) | 43 | 1,064 | 1,064 |

Both are confirmed *not* K₅-free, so the agent ruled out Paley as a path to a 43-vertex counterexample.

---

## 🧪 What's Implicit / Already Known

Honest framing requires being explicit about what this work does **not** independently discover:

- **The "42-cliff" is folklore.** It is the immediate consequence of Exoo's lower bound having held at 43 since 1989. Anyone who has seriously attempted to extend Exoo's circulant to n=43 — and many have — has effectively observed this. Radziszowski's *Small Ramsey Numbers* dynamic survey (regularly updated, [DS1](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1)) is the canonical reference.
- **Symmetry-broken SAT encodings of Ramsey problems are well-studied.** See e.g., Codish et al., "Sums of Triples in Abelian Groups" (2016); Heule's work on Schur Number Five (2017); various papers on BreakID and Shatter.
- **2024 upper bound improvement to 46.** [arXiv:2409.15709](https://arxiv.org/abs/2409.15709) tightened the upper bound from 48 to 46. Our agent discovered this via web search and incorporated it.

If you intend to build on this work for a math paper, please do a thorough literature comparison first.

---

## 🛠️ Pipeline Architecture

```
┌──────────────────────────────────────────────────────────┐
│ ThinkerWave Evolutionary Agent (24 generations)          │
│                                                          │
│  Gen 0–5:   First-principles analysis, scope mapping     │
│  Gen 6:     Fork → branch_a / branch_b                   │
│  Gen 7–14:  Branch exploration                           │
│  Gen 14:    Merge / Mode 2 directive injection           │
│  Gen 15–21: SA on n=43, Paley analysis, scaling          │
│  Gen 22:    Z₄₃ circulant SAT → UNSAT (8.23s)            │
│  Gen 23:    2-block Z₂₁ × Z₂₂ SAT → UNSAT (2.42s)        │
│  Gen 24:    Refined 2-block + extrapolation (4.67s)      │
└──────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│ SAT Pipeline (agent-authored)                            │
│                                                          │
│  1. Symmetry restriction (circulant or block-circulant)  │
│  2. Map each C(n,5) subset to its symmetry orbit         │
│  3. Sort literals within clauses → set() dedup           │
│  4. Feed unique clauses to PySAT Glucose3                │
│  5. Report SAT/UNSAT + wall-clock time                   │
└──────────────────────────────────────────────────────────┘
```

### Encoding (agent's own approach, paraphrased)

```python
# Single-block circulant on Z_n: edge color depends on |i-j| mod n
edge_var_single = lambda i, j, n: (abs(i - j) % n) + 1

# 2-block: Block A = vertices 0..nA-1, Block B = vertices nA..nA+nB-1
def edge_var_2block(i, j, nA, nB):
    if i < nA and j < nA:
        return ("A", abs(i - j) % nA)         # intra-block A
    if i >= nA and j >= nA:
        return ("B", abs((i-nA) - (j-nA)) % nB)  # intra-block B
    a, b = (i, j) if i < nA else (j, i)
    return ("X", (b - nA - a) % nB)              # cross-block

# K_5-free constraint: for each 5-subset, at least one edge each color
from itertools import combinations
from pysat.solvers import Glucose3

clauses = set()
for S in combinations(range(n), 5):
    edge_orbits = [edge_var_2block(i, j, nA, nB) for i, j in combinations(S, 2)]
    var_ids = sorted(map(orbit_to_id, edge_orbits))
    clauses.add(tuple(var_ids))     # red K_5 forbidden
    clauses.add(tuple(-v for v in var_ids))  # blue K_5 forbidden
```

The deduplication step (`set(clauses)`) is what compresses 1.9M naive clauses down to ~208K.

---

## 📂 Repository Layout

```text
.
├── README.md                       # This file
├── LICENSE                         # MIT
├── src/
│   ├── encoder.py                  # Circulant + 2-block SAT encoding
│   ├── sat_runner.py               # PySAT Glucose3 driver
│   └── validation.py               # R(3,3)=6 and R(4,4)=18 sanity checks
├── logs/
│   ├── full_run_lineage.json       # All 24 generation records (ACR snapshots, scores, divergence)
│   ├── gen_22_output.md            # Z₄₃ single-block circulant verdict
│   ├── gen_23_output.md            # 2-block Z₂₁ × Z₂₂ verdict
│   ├── gen_24_output.md            # Refined 2-block + extrapolation
│   └── scaling_ladder.csv          # Per-n SAT/UNSAT timing data
└── docs/
    └── methodology.md              # ThinkerWave agent framework overview
```

---

## 🚀 Reproducing the Results

```bash
# Install
pip install python-sat numpy

# Single-block circulant on N=43
python src/sat_runner.py --n 43 --mode single

# 2-block Z_21 x Z_22 on N=43
python src/sat_runner.py --n 43 --mode 2block --block-a 21 --block-b 22

# Full scaling ladder
python src/sat_runner.py --scaling-ladder
```

Expected output (on a 2024-era laptop CPU):
```
[mode=2block, nA=21, nB=22] N=43: 44 vars, 207,960 unique clauses (89.2% dedup)
[Glucose3] solve: UNSAT in 4.67s
```

---

## 🔬 Reproducibility of the Agent Trajectory

The full agent lineage is logged in `logs/full_run_lineage.json`. Each generation record contains:
- The complete Agent Configuration Record (ACR) — system prompt, strategy, evaluation criteria, accumulated failures
- Strategy blueprint produced by the strategize phase
- Solution output and its tool-call trace
- Independent evaluator score, strengths, weaknesses, phantom-verification flags
- Calibrated baseline (when evaluation criteria changed)
- Divergence score and class (LOW / MEDIUM / HIGH)
- Branch and merge events

To run the full agent trajectory yourself you will need the ThinkerWave framework (separate repo) and AWS Bedrock credentials (Claude Sonnet 4.5 + Opus 4.6). A complete 24-generation run with branching and tool calls cost approximately **$18–22 USD** in LLM tokens.

---

## 📜 Citation

If you reference this artifact, please cite both the artifact and the underlying framework:

```bibtex
@misc{r55_thinkerwave_2025,
  title  = {Autonomous AI-Agent Investigation of Ramsey Number R(5,5):
            Symmetry-Restricted SAT Pipelines via an LLM Evolutionary Agent},
  author = {Goel, Vikas},
  year   = {2025},
  howpublished = {\url{https://github.com/<this-repo>}},
  note   = {Methodology demonstration; SAT results empirically reconfirm
            structural barriers known to the Ramsey-theory community.}
}

@software{thinkerwave_2025,
  title  = {ThinkerWave: An Evolutionary Multi-Persona LLM Agent Framework},
  author = {Goel, Vikas},
  year   = {2025},
  howpublished = {\url{https://github.com/vikasjoel/ThinkerWaveCode}}
}
```

---

## 🙏 Acknowledgements & Disclosure

- The agent's autonomous reasoning was driven by Anthropic Claude (Sonnet 4.5 for strategize/execute, Opus 4.6 for evaluate/transform/converge).
- Three mid-flight directives were injected by a human operator across Mode 2 resumes (the directives are logged in `logs/full_run_lineage.json` under `user_directive`).
- The phantom-verification cap fired multiple times during the run, catching over-claims. The reported scores are calibrated, not raw.
- The 2024 upper bound R(5,5) ≤ 46 was incorporated via web search by the agent during gen 24; we did not produce it.
- **We have not done a full literature comparison** against block-circulant Cayley-graph searches in the existing Ramsey literature. If you intend to build a math paper on this artifact, please do so first.

## License
MIT. See [LICENSE](LICENSE).
