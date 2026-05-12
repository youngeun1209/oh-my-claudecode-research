# Autonomous drive — `/supervisor-drive`

OMCR's autonomous orchestrator. Given the current project state, the supervisor surveys the 5 state files, applies a hardcoded bottleneck-ranker, dispatches the right engine, re-evaluates state from scratch, and loops — without per-step user prompting in `--auto` mode. The safety posture is conservative on purpose: 6 safety gates fire **even in `--auto`**, and after any halt the next invocation requires an explicit `--resume <run-id>` or `--fresh` flag.

If you have not yet read [Orchestration model](Orchestration-Model.md), do that first. This page assumes you understand engines-are-leaves and the 5 state files. Phase 3 of OMCR's roadmap is the spec backing this page; see [`develop/phase-3-autonomous-supervisor.md`](../develop/phase-3-autonomous-supervisor.md) and [`develop/phase-3-decisions.md`](../develop/phase-3-decisions.md) for the design source.

## What it does

`/supervisor-drive` is the **only** OMCR engine allowed to chain other engines, and it does so without violating engines-are-leaves: the supervisor re-reads all state from disk between every dispatch, so the priority ranker — not the prior engine — picks the next move. There are 3 modes (interactive, auto, plan-only), 6 safety gates, 8 priority rules in the ranker, and 6 termination conditions. The whole point is that everything is **bounded**: `--max-iter` caps engine invocations, `--budget-tokens` caps cumulative cost, every dispatch is gate-checked, and every halt writes durable state so the user can resume after addressing whatever stopped the drive.

The other OMCR engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`) are still leaves — they don't know `/supervisor-drive` exists. The supervisor invokes them the same way the user would.

## The 3 modes

### `--interactive` (default)

After every state survey, the supervisor prints its plan and waits for the user. Responses:

- `yes` — dispatch the planned engine.
- `pick <n>` — dispatch the n-th alternative instead.
- `no` — skip this iter; loop back to state-survey (handy if you want to edit state manually between iters).
- `halt` — exit cleanly.

```
$ /supervisor-drive

[iter 1/5] survey
  paper:      2/5 sections approved, 1 drafted, 2 empty
  citations:  8 verified, 0 pending, 3 [CITE:] placeholders in manuscript
  figures:    1/3 done, 1 diverged
  rebuttals:  0 pending
  prior:      (first iter)

[iter 1/5] plan
  next:    /literature-sweep "frontoparietal working memory"
  reason:  3 [CITE:] placeholders in manuscript. Dispatching /literature-sweep.
  priority: 3
  alts:    0 alternative(s)

Respond (yes / pick <n> / no / halt):
> yes
```

### `--auto`

The supervisor skips confirmation. The loop runs until any of the termination conditions fires. Safety gates still demand explicit confirmation phrases — autonomous mode does not silently change the hypothesis, add a citation, or commit budget you didn't approve.

```
$ /supervisor-drive --auto --max-iter 5 --budget-tokens 80000

[iter 1/5] survey  paper: 2/5 approved, 1 drafted, 2 empty | citations: 8 verified, 3 placeholders | figures: 1/3 | rebuttals: 0
[iter 1/5] plan    next: /literature-sweep "frontoparietal working memory" (priority 3)
auto: dispatching /literature-sweep — safety-gate check in phase 04

GATE: NewCitation
  Engine:   /literature-sweep
  Trigger:  literature-sweep first dispatch in drive

OMCR will not silently add references. Confirm by typing the exact phrase:

  confirm-new-citation

>
```

Autonomous mode pauses here. The user types the gate's confirmation phrase, the drive proceeds, and from this point the same gate does not re-fire in the same drive (the NewCitation gate is once-per-drive for the literature-sweep engine).

### `--plan-only`

State-survey + action-plan + report, no dispatch. Prints the next action and a projection of the next 3 actions. Use this to preview an `--auto` run before committing to it.

```
$ /supervisor-drive --plan-only

plan-only:
  Next action:
    engine:   /literature-sweep
    args:     { "topic": "frontoparietal working memory" }
    reason:   3 [CITE:] placeholders + 0 pending citations.json.queue entries
    priority: 3

  Projected next 3 actions (if next_action returned DONE):
    iter 2: /iterate-revision sections/discussion.tex (priority 5)
    iter 3: /iterate-revision sections/methods.tex (priority 5)
    iter 4: /figure-bake fig3 (priority 7)

  Cost projection:
    iter 1: 50000 × 1.25 = 62500 tokens
    iter 2: 24000 × 1.25 = 30000 tokens
    iter 3: 24000 × 1.25 = 30000 tokens
    iter 4: 45000 × 1.25 = 56250 tokens
    total:  178750 tokens (vs --budget-tokens 50000)
```

Nothing is dispatched. Nothing is committed. The drive ends with a clean DONE record so the next invocation does not detect an "open" halt.

## The 6 safety gates

Every dispatch passes through 6 pre-dispatch gates. **Every gate is confirm-required even in `--auto` mode** — except CriticalIssue, which has no override.

| # | Gate | Trigger | Confirmation phrase | Notes |
|---|---|---|---|---|
| 1 | **HypothesisChange** | Brief or args mention modifying `paper.json.hypothesis`. | `confirm-hypothesis-change` | Research integrity. Autonomous mode does not shift the central claim. |
| 2 | **NewCitation** | Engine intends to add a `references.bib` entry not already in `citations.json.verified`. | `confirm-new-citation` | `/literature-sweep`'s own hard verify-gate covers most fabrication risk; this gate catches engine-author leaks. Fires once per drive for `/literature-sweep`, per dispatch for `/respond-reviewer` citation comments. |
| 3 | **NewExperiment** | Brief contains `"design a new experiment"`, `"collect more data"`, `"run a new analysis"`, `"acquire"`, etc. | `confirm-new-experiment` | Real-world action, not a model output. False positives are acceptable. |
| 4 | **StructuralRewrite** | Brief contains `"restructure"`, `"reframe"`, `"change conclusion"`, `"pivot"`, `"flip the framing"`, etc. | `confirm-structural-rewrite` | Scope-change risk; needs human ownership. |
| 5 | **BudgetExceeded** | `cumulative + projected × 1.25 > budget_tokens`. | `confirm-budget` | Pre-dispatch check. See cost model below. |
| 6 | **CriticalIssue** | A prior engine in this drive returned BLOCKED with `severity: critical`. | (no override — always halt) | The strictest gate. Can't be confirmed away. |

Multiple gates can trip on one dispatch — each must be confirmed in order. A typed `yes` is **not** acceptable for a gate; the confirmation phrase is distinct on purpose. Making the wrong choice should require a deliberate keystroke.

The full implementation lives in [`skills/supervisor-drive/phases/04-engine-invoke.md`](../skills/supervisor-drive/phases/04-engine-invoke.md). The trigger keyword lists are locked at v0.4 — adding gates or changing triggers is a v0.5+ refinement.

## The hardcoded priority rules

The bottleneck-ranker. Phase 02 of the skill applies these in order; first match wins. Hardcoded at v0.4 per Phase 3 decision §5 — no CLAUDE.md-driven override.

| # | Trigger | Engine / response |
|---|---|---|
| 1 | Any section `status: blocked` | **HALT.** Human action required (a prior `/iterate-revision` returned BLOCKED with a critical issue). |
| 2 | Any section `status: blocked-on-tbd` | **HALT.** Resolve `[TBD: ...]` markers or re-invoke with `--allow-tbd`. |
| 3 | `[CITE: ...]` placeholders in manuscript OR `citations.json.queue` has `pending` entries | `/literature-sweep <topic>` |
| 4 | Empty sections (`status: empty`) | `/outline-expand <outline-path>` if outline exists; else `/iterate-revision <section>` single-section |
| 5 | Drafted-but-unreviewed (`status: drafted`) | `/iterate-revision <section>` |
| 6 | Pending rebuttals (`rebuttals.json` has entries with HALT verdict or per-comment `deferred` / `disputed`) | `/respond-reviewer <letter>` |
| 7 | Figures with brief-vs-impl divergence | `/figure-bake <fig-id>` |
| 8 | All approved + figures done + citations verified + rebuttals resolved | `submission_ready = true`. **EXIT DONE.** |

Two practical notes:

- Priorities 1 and 2 are halt states, not engine dispatches. The supervisor cannot auto-clear them — they need human action.
- An **anti-loop guard** sits on top of the rules: if the prior iter returned BLOCKED on the same engine + same target, the supervisor flags it; if two consecutive iters return BLOCKED on the same target, the supervisor halts. No silent retries, no fallback engine.

If you disagree with the ranking for a specific run, two escape hatches exist:

- `--interactive` — the user picks an `alternative` each step.
- `--plan-only` — inspect the plan, then stop and run the engine you actually want manually.

User-configurable priority overrides are a v0.5 backlog item. v0.4 ships with hardcoded rules so the v0.5 design has a clean baseline.

## `--resume <run-id>` and `--fresh`

Per Phase 3 decision §1 (locked, user ACK strict): after any halt, the next `/supervisor-drive` invocation does **not** auto-resume. It prints a one-screen halt-summary and exits unless the user explicitly picks one of:

- `--resume <run-id>` — continue the prior trajectory. Records `resumed_from: <run-id>` in the new run's start entry for clean audit.
- `--fresh` — start a new drive from current state, ignoring the prior halt.

```
$ /supervisor-drive

supervisor-drive: prior drive halted. Choose how to proceed.

Most recent halt:
  run_id:       a1b2c3d4-0001-...
  started:      2026-05-11T14:00:00Z
  halt verdict: HALT
  last engine:  /iterate-revision sections/methods.tex
  last args:    section_path=sections/methods.tex venue=NeurIPS
  reason:       1 major issue remaining, iter 3/3
  last commit:  e4f5g6h omcr supervisor-drive: iterate-revision sections/methods.tex verdict=HALT run=a1b2c3d4-0001-

Resume options:
  /supervisor-drive --resume a1b2c3d4-0001-...     # continue the same trajectory
  /supervisor-drive --fresh                          # start a new drive from current state
```

Auto-resume is a foot-gun: the user may have manually edited a section, switched branches, hand-run an engine between drives, or forgotten the prior drive existed. Explicit resume costs one flag and forces conscious "yes, continue."

**Errored drives** (engine threw an exception, `run_error.json` exists) are stricter: `--resume <run-id>` is rejected. The user must inspect the error and pass `--fresh` once the underlying cause is resolved.

## Cost model

Phase 3 decision §6 (locked): each engine declares `cost_estimate_tokens` in its SKILL.md frontmatter. The supervisor's pre-dispatch budget check uses:

1. **Rolling median** of the last 5 `tokens_used` values for the same engine in `_run-log.jsonl`. If N ≥ 5, use the median.
2. **Declared constant** from the engine's frontmatter. If N < 5, use the constant.
3. **Multiply by 1.25** as conservative padding.

The `BudgetExceeded` gate fires when `cumulative + projected × 1.25 > budget_tokens`. Wrong-by-25% is fine; wrong-by-2x is the failure mode this guards against.

This is distinct from the orchestrate `loop` primitive's post-hoc `budget_tokens` cap (which fires at the iteration boundary after the engine ran). The supervisor pre-empts the overrun; the loop primitive caps it after the fact. Both run.

Default `--budget-tokens` is `50000`. Typical full-drive runs estimate at ~80000 tokens (see the supervisor's own `cost_estimate_tokens: 80000` frontmatter). Bump the budget if your drives keep tripping the gate — but a tripped gate is sometimes the right signal that the project's scope is wider than the cap.

## Composability with OMC's `/autopilot` and `/ralph`

OMCR's `/supervisor-drive` is research-paper-shaped: its priority ranker knows about sections, citations, figures, rebuttals. OMC's `/autopilot` and `/ralph` (from upstream `oh-my-claudecode`) are general-purpose autonomous loops with broader scope (code, infra, general agents). The two compose well:

- Use `/autopilot` for project-level orchestration that spans more than just paper-writing (e.g. "set up the repo + run the analysis + draft the paper").
- Use `/supervisor-drive` for the paper-writing portion specifically, with OMCR's domain-aware safety gates.

The recommended pattern: a top-level `/autopilot` invocation that, when it reaches the manuscript phase, dispatches `/supervisor-drive --auto --budget-tokens <X>` as a single bounded sub-task. The supervisor's `--auto` then runs to either DONE or HALT, and `/autopilot` continues with whatever comes next.

See [With OMC](With-OMC.md) for concrete recipes once the OMC companion install is in place.

## The engine-leaves invariant — restated

`/supervisor-drive` is the only OMCR engine allowed to chain others. Even it does so by re-evaluating state from scratch between every step (Phase 3 decision §3). The five Phase 1 / Phase 2 engines never call each other and never call the supervisor.

This makes the loop fully described by `loop { survey → plan → confirm → dispatch → checkpoint → iterate }` with no special cases:

- Every transition between engines is a fresh state-read + ranker pass.
- Safety gates fire at every transition, not only at the top level.
- `_run-log.jsonl` reads as a flat sequence — no nested call stacks.

This invariant is what makes the supervisor auditable. The full pattern is documented in [Orchestration model](Orchestration-Model.md); see also Phase 2 decision §5 (engines are leaves) and Phase 3 decision §3 (no inter-engine chaining).

## Why single-target only at v0.4

Phase 3 decision §4 (locked, user ACK): `next_action` is always exactly one engine + one target per iter. No parallel dispatch.

Parallel dispatch multiplies every Phase 3 risk by N:

- Budget overruns scale linearly.
- Safety-gate evaluation has to handle concurrent partial results.
- "Halt" gets ambiguous when one of three parallel engines errored.
- `_run-log.jsonl` needs a new schema for grouped runs.

Each is a v0.5+ problem. Single-target also keeps the example-session traces readable. Researchers iterating on a paper rarely need true parallelism — sequential runs are bounded by user attention anyway. Users who want parallelism today can run two Claude Code sessions side-by-side at their own risk.

## What the supervisor does NOT do

- Does not retry on engine exception. Halt-on-exception, no retry — `run_error.json` is written and the drive halts. The user inspects and re-invokes with `--fresh`.
- Does not call personas directly. Only engines. (Personas are inside engines.)
- Does not override safety gates in `--auto`. Every gate is confirm-required.
- Does not push to a remote. Per-engine commits are local. Run `/sync` afterward to push.
- Does not rewrite `main.tex`, `references.bib`, or any non-state file directly. All edits go through engines.
- Does not modify other engines' SKILL.md or phase files at runtime. Engine logic is static markdown.
- Does not auto-submit a paper when `submission_ready = true`. Submission is the user's call.

## See also

- [`commands/supervisor-drive.md`](../commands/supervisor-drive.md) — the slash command (thin dispatcher).
- [`skills/supervisor-drive/SKILL.md`](../skills/supervisor-drive/SKILL.md) — the engine skill body.
- [`skills/supervisor-drive/phases/`](../skills/supervisor-drive/phases/) — the 8 phase files (00-resume-check, 01-state-survey, 02-action-plan, 03-confirm-or-auto, 04-engine-invoke, 05-checkpoint, 06-iterate-or-finalize, 07-report).
- [`agents/supervisor.md`](../agents/supervisor.md) — the advisory persona (read-only).
- [Orchestration model](Orchestration-Model.md) — state store, 4 primitives, engines-are-leaves invariant.
- [Agents](Agents.md) — `@supervisor` and the other 5 OMCR agents.
- [Commands](Commands.md) — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand` (the engines the supervisor dispatches).
- [Configuration](Configuration.md) — the `## Research stack` block and env vars.
- [`develop/phase-3-autonomous-supervisor.md`](../develop/phase-3-autonomous-supervisor.md) — full design spec.
- [`develop/phase-3-decisions.md`](../develop/phase-3-decisions.md) — locked decisions §1–§6.
