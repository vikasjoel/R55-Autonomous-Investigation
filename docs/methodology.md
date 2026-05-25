# Methodology: How the Agent Produced This Investigation

This document describes the **ThinkerWave** evolutionary agent framework that produced the empirical R(5,5) artifacts in this repository. It is provided for reproducibility and for reviewers evaluating the methodology claim.

## The Four-Persona Loop

Each generation of the agent runs four distinct LLM personas, each with a different model and temperature:

| Phase | Persona | Model | Temperature | Role |
|-------|---------|-------|-------------|------|
| 1. Strategize | Agent (evolving) | Sonnet 4.5 | 0.3 | Reads the current ACR identity, produces a strategy blueprint |
| 2. Execute | Agent (evolving) | Sonnet 4.5 | 0.5 | Executes the strategy with sandbox tools (Python + web search) |
| 3. Evaluate | Independent evaluator (fixed) | Opus 4.6 | 0.7 | Scores the output 1-10 against criteria, **never sees the agent's identity** |
| 3b. Calibrate | Independent evaluator (fixed) | Opus 4.6 | 0.7 | If criteria changed this gen, re-evaluates the best-config to produce a comparable baseline |
| 4. Transform | Transformation engine (fixed) | Opus 4.6 | 0.7 | Designs the **entire next-generation identity** from scratch based on the evaluation |

The transformer's output replaces the previous agent. There is no continuity of "self" across generations — only the accumulated `known_failures`, `learned_heuristics`, and `evaluation_criteria` carry forward inside the new Agent Configuration Record (ACR).

## The ACR (Agent Configuration Record)

Every generation begins with a complete ACR — a Pydantic model containing:
- `system_prompt`: The agent's full persona (500-2000 chars)
- `strategy`: The current approach (300-1000 chars)
- `evaluation_criteria`: 3-15 dimensions the work will be judged on
- `reasoning_approach`: How the agent structures its thinking
- `known_failures`: Up to 20 entries with relevance scores
- `learned_heuristics`: Up to 15 entries
- `knowledge_gaps`: What the agent admits it does not know
- `user_directive`: Optional mid-flight human steer (Mode 2 resumes only)

## Branching and Convergence

When the evaluator detects two viable but contradictory improvement directions in a generation, the transformer is allowed to **fork** — producing two parallel branches that explore independently for up to 5 generations each. The Convergence Engine (a fifth fixed persona, Opus 4.6 at temp 0.5) then synthesizes both branches into a single merged ACR. The merged ACR unions the discovered criteria, failures, and heuristics from both branches.

In the R(5,5) run, fork occurred at gen 6, and convergence merged at the appropriate point.

## Guardrails Enforced In Code

12 constraints are enforced as code-level validation:

1. Criteria rate limit: ±3 criteria per generation
2. Phase 3b calibration: triggered when criteria change
3. Best-config rollback: 3 consecutive regressions → revert
4. Failure deduplication: no duplicate entries
5. ACR token budget: 8000 max
6. Branch limit: max 4 parallel
7. Min fork interval: 3 generations
8. **Identity firewall:** new agent never sees predecessor's output
9. **Evaluator independence:** evaluator never sees `ACR.system_prompt`
10. Criteria substance seeding: seed includes domain-specific criterion
11. Phantom-verification cap: scores capped when over-claims detected (critical=4.0, major=6.0, minor=-0.5)
12. Token-aware budget tracking with per-model pricing

## The Phantom Verification Mechanism

A secondary evaluator pass scans every generation's output for unverified claims:

- **Critical:** unsupported claims about computational results that did not actually run (cap score at 4.0)
- **Major:** "appears to be" / "likely indicates" without supporting evidence (cap at 6.0)
- **Minor:** rhetorical inflation (e.g., "exceptional", "world-class") (-0.5)

The reported scores in this artifact are **calibrated** — they reflect what the agent could verify, not what it claimed.

For the R(5,5) run:
- Gen 22: raw 6.0, no phantom cap, final 6.0
- Gen 23: raw 5.0, no cap, final 5.0
- Gen 24: raw 7.0, **4 phantom claims caught**, capped to 6.0

## Mid-Flight Directives (Mode 2)

During the run, three human directives were injected via the Mode 2 Resume API. The directives were:

1. **Resume #3** (after gen 20): "Force a circulant SAT search on Z_43 (21 distance variables) and report SAT/UNSAT."
2. **Resume #4** (after gen 22): "Run a 2-block circulant SAT on Z_21 × Z_22 with clause deduplication."

A directive does NOT control the agent. It is injected into the strategize, execute, and transformer prompts; the agent reads it and decides whether and how to follow it. The evaluator never sees the directive (Guardrail #9) — it scores honestly against the criteria.

Both directives were followed substantively. The agent self-corrected mid-execution in gen 24 ("Timeout due to naive edge numbering. Switching to optimized circulant encoding") without further human input.

## Cost

- Gen 0–20 (linear + branched exploration): ~$13 USD in Anthropic API tokens
- Gen 21–22 (resume #3): ~$3.58 USD
- Gen 23–24 (resume #4): ~$3.84 USD
- **Total run cost: ~$20–22 USD**

## Honest Limitations

- The agent's "discovery" of the 2-block UNSAT verdict reproduces known structural barriers in cyclic Cayley-graph Ramsey searches. We did not perform a literature comparison; an expert combinatorialist may identify prior work that subsumes parts of this artifact.
- All numerical results are **single-run** — we did not run multiple seeds or repeat the full agent trajectory. SAT solve times are reproducible; the agent's exploration trajectory is partially stochastic (LLM sampling).
- The phantom-verification system catches over-claims but is itself an LLM. It is not a formal verifier. Treat all scoring as advisory.
- The agent was given web-search access. Some of its "knowledge" comes from Tavily search results, not from training data alone.

For reviewers: the full per-generation trace is in `logs/full_run_lineage.json` and the strategy / output / evaluation for the key gens (22, 23, 24) is in `logs/gen_22_output.md`, `gen_23_output.md`, `gen_24_output.md`.
