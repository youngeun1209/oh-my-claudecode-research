---
name: figure-bake
description: Drive one figure from design idea to manuscript-ready vector PDF + outline-ready PNG. Loops `@figure-descriptor` → `@analysis-implementer` → `@reviewer` against a single fig-id in `figures.json`, with the `cropfig` skill auto-invoked at the end of each implement phase to keep manuscript + outline artifacts in lockstep. The third Phase 2 engine — a 3-agent loop, more complex than `/iterate-revision`'s 2-agent loop, and the only Phase 2 engine that executes real code per iteration. Safe to re-run; safe to resume after BLOCKED or HALT.
writes: [figures, paper]
cost_estimate_tokens: 45000
---

# /figure-bake

This engine bakes a single figure from a one-line concept to a manuscript-grade artifact. It is the **3-agent loop** demonstration of the orchestration pattern: each iteration runs design (`@figure-descriptor`) → implementation (`@analysis-implementer`, which actually executes Python/matplotlib code via Bash) → critique (`@reviewer`, which reads the rendered PNG/PDF multimodally), with a verdict at the end of every iter.

If you are reading this because Claude Code's skill auto-discovery surfaced it: invoke it via `/figure-bake <fig-id>`. Do not edit `figures.json`, the rendered figure files, or the per-figure script directory by hand while a run is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
/figure-bake <fig-id> [--max-iter N] [--data <path>] [--code-dir <path>]
```

| Flag | Default | Purpose |
|---|---|---|
| `--max-iter` | `3` | Hard cap. Reaching it without DONE/BLOCKED → HALT. Override via CLI or via `## Research stack` field `figure_bake.max_iter`. |
| `--data` | (resolved) | Dataset root. Three-layer resolution: CLI `--data` > env `CLAUDE_RESEARCH_DATA_ROOT` > CLAUDE.md `## Research stack` `data_root` > hardcoded `./data/` (Phase 2 decision §3). |
| `--code-dir` | `null` | Optional script directory the implementer writes its renderer(s) into. If unset, the implementer chooses (typically `<manuscript_root>/figures/code/` or alongside `vector_path`). |

Examples:
- `/figure-bake fig1` — defaults; data resolves from env / CLAUDE.md
- `/figure-bake fig2 --max-iter 5 --data ~/datasets/2026-cohort/`
- `/figure-bake fig3 --code-dir code/figures/`

## The loop

```
phase 01 — precheck (resolve fig-id, resolve data_root, validate path)
phase 02 — brief      (@figure-descriptor → design brief, no images)  ┐
phase 03 — implement  (@analysis-implementer → render code + cropfig) │  repeated up to --max-iter
phase 04 — critique   (@reviewer reads the rendered figure)            │
phase 05 — evaluate   (verdict rule on critique severity list)         ┘
phase 06 — finalize (user summary + _run-log.jsonl append + embed hint)
```

Loop body is phases 02 → 03 → 04 → 05. The brief produced in phase 02 of iter 1 is reused in iter 2+ unless `@reviewer` flags a structural design issue that bumps `brief_status` back to `"drafted"`; that triggers a fresh brief on the next iter (see phase 02 step 4 for the rule).

The loop is driven by [`../orchestrate/phases/04-loop.md`](../orchestrate/phases/04-loop.md); this engine hands it a dispatch plan + a verdict rule and lets the primitive run them.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — Precheck.** Read [`phases/01-precheck.md`](phases/01-precheck.md).
2. **Phase 2 — Brief.** Read [`phases/02-brief.md`](phases/02-brief.md).
3. **Phase 3 — Implement.** Read [`phases/03-implement.md`](phases/03-implement.md).
4. **Phase 4 — Critique.** Read [`phases/04-critique.md`](phases/04-critique.md).
5. **Phase 5 — Evaluate.** Read [`phases/05-evaluate.md`](phases/05-evaluate.md).
6. **Phase 6 — Finalize.** Read [`phases/06-finalize.md`](phases/06-finalize.md).

Phases 02 → 03 → 04 → 05 form the loop body. The orchestrate `loop` primitive runs them up to `--max-iter` times.

## Composition

This engine imports the following primitives from [`../orchestrate/`](../orchestrate/):

- [`phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — read `figures.json` in phase 01 (and re-read in phases 03, 04, 05 when status updates land back on disk) and `paper.json` in phase 01 (`manuscript_root` field is needed to resolve relative `vector_path` defaults).
- [`phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — dispatch `@figure-descriptor` (phase 02), `@analysis-implementer` (phase 03), and `@reviewer` (phase 04) via the Agent tool with inlined persona bodies.
- [`phases/03-evaluate.md`](../orchestrate/phases/03-evaluate.md) — apply the `severity-threshold` verdict rule defined in [`phases/05-evaluate.md`](phases/05-evaluate.md) of this engine.
- [`phases/04-loop.md`](../orchestrate/phases/04-loop.md) — drive the 3-step dispatch plan through up to `max_iter` iterations; own `_run-log.jsonl` writes; honor `budget_tokens` post-hoc.

In addition, this engine **calls one non-engine skill**: [`../cropfig/SKILL.md`](../cropfig/SKILL.md). `cropfig` is invoked from phase 03 (after the implementer succeeds) to produce the manuscript-grade vector PDF and outline-grade raster PNG from one cropped source. This is allowed under Phase 2 decision §5 — engines may invoke skills; they may not invoke other engines.

This engine **does not** invent its own state-read, dispatch, or loop mechanics. If you find yourself replicating that logic inside a phase file, you're solving the wrong problem — fix the primitive, do not fork it.

## Three-layer `data_root` resolution

Phase 01 resolves `data_root` in this order (first non-empty wins):

1. **CLI `--data <path>`** — one-off override for this invocation.
2. **Env `CLAUDE_RESEARCH_DATA_ROOT`** — useful for CI / batch runs.
3. **CLAUDE.md `## Research stack` block, field `data_root`** — the project-default. Set once during `/start-research` or hand-edited.
4. **Hardcoded fallback `./data/`** — last-resort relative path.

The resolved path is then validated: phase 01 aborts if the path does not exist on disk. `--data` is the only layer that overrides the validation order; an env or CLAUDE.md value that doesn't exist still aborts (the user must fix their config). See Phase 2 decision §3 for the rationale (mirrors the env → CLAUDE.md → default pattern already used elsewhere in the plugin).

## Verdict rule

The verdict is computed at the end of each iteration's `@reviewer` critique. Canonical rule (passed as a `severity-threshold` rule spec to [`../orchestrate/phases/03-evaluate.md`](../orchestrate/phases/03-evaluate.md)):

| iter | critical | major | result |
|---|---|---|---|
| any   | ≥ 1 | any | **BLOCKED** — critical issue requires structural redesign |
| < max | 0   | ≥ 1 | **CONTINUE** — loop another iteration |
| < max | 0   | 0   | **DONE** — figure approved |
| = max | 0   | ≥ 1 | **HALT** — iterations exhausted, majors remain |
| = max | 0   | 0   | **DONE** — finished on the last allowed iter |

`minor` and `nit` issues never gate the verdict. They are logged to `figures.json.figures[<fig-id>].critiques[]` and surfaced in the phase 06 summary.

The verdict drives the per-figure status fields in `figures.json.figures[<fig-id>]`:

| Verdict | `critique_status` | `impl_status` | `brief_status` |
|---|---|---|---|
| DONE     | `done`    | `approved` | `approved` |
| BLOCKED  | `done`    | `drafted`  | unchanged (typically `drafted` — the reviewer's critical flag may target the brief; if so, set `drafted` so phase 02 re-runs on resume) |
| HALT     | `done`    | `drafted`  | unchanged |
| CONTINUE | `done`    | `drafted`  | unchanged (or `drafted` if the reviewer flagged a brief-level issue — see phase 05 step 4) |

Phase 05 owns these writes. Phase 06 only reads them.

## Cost model

Each iteration is **3 Agent-tool dispatches** (descriptor + implementer + reviewer) plus one `cropfig` invocation. With `max_iter = 3`, a typical run is ≤ 9 subagent calls + 3 cropfig passes. The `cost_estimate_tokens: 45000` frontmatter field is a coarse upper-bound for `/supervisor-drive` budget gating (Phase 3 §6); actuals land in `_run-log.jsonl` post-hoc per Phase 0 decision §6.

Per-iter cost is dominated by:
- the persona bodies (descriptor ~200 lines, implementer ~170 lines, reviewer ~200 lines) inlined into each dispatch (Phase 0 decision §5),
- the rendered figure's bytes when `@reviewer` reads the PNG via the Read tool (multimodal — non-trivial token weight),
- the implementer's actual code-execution tokens (Bash output, error tracebacks, plotting library prints).

Why the default `max_iter = 3` is deliberately small: each iter triggers real code execution by `@analysis-implementer`, which is the most expensive operation in the engine and the slowest. Bumping `max_iter` higher than 3 should be a conscious call, not an accident — pass it explicitly.

## What this engine does NOT do

- Does **not** insert `\includegraphics{...}` into any `.tex` file. The implementer writes the rendering script + the PDF; embedding the PDF into the manuscript is the user's call. Phase 06 suggests `/sync` as the right tool for that, because `/sync` already understands the outline-side embed pattern through `cropfig` func 3.
- Does **not** crop manually. The crop pass is one call to the `cropfig` skill, which owns the band-classification heuristic + the dual PDF/PNG output. This engine doesn't duplicate that logic.
- Does **not** mutate any other figure's entry in `figures.json`. One run = one fig-id.
- Does **not** call `/iterate-revision`, `/respond-reviewer`, `/outline-expand`, or `/literature-sweep`. Engines are leaves (Phase 2 decision §5). If a reviewer comment says "this figure proves nothing about the methods section," that's a hint to run `/iterate-revision sections/methods.tex` afterward — the user, not this engine, makes that call.
- Does **not** commit to git between iterations by default. `on_iter_end` is left unset on the loop primitive.
- Does **not** retry the implementer on a Python traceback inside the same iter. A failed render becomes a BLOCKED verdict and the user fixes the data / script before re-running.
- Does **not** auto-resolve the dataset path against a default if the user-configured path is missing. Phase 01 aborts; the user must fix the CLAUDE.md / env / `--data` value.

## Re-running policy

- Already-DONE figure (status fields all `approved` / `done`) + first invocation in a fresh session → phase 01 lets the run proceed (the user re-invoked for a reason — perhaps the data changed). Iter counter continues; no early-exit flag in v0.2.
- BLOCKED figure → phase 01 lets the run proceed; the user is expected to have addressed the critical issue (revised the brief, fixed the data, or moved to a different `vector_path`) before re-running. Iter counter continues.
- HALT figure → phase 01 lets the run proceed; iter counter continues from where it left off.
- Missing fig-id in `figures.json` → phase 01 creates the entry (with `brief_status: "missing"`, `impl_status: "missing"`, `critique_status: "pending"`, `iter: 0`, and a templated `vector_path` of `<manuscript_root>/figures/<fig-id>.pdf`) and proceeds into phase 02.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine composes.
- [`../cropfig/SKILL.md`](../cropfig/SKILL.md) — the crop pipeline this engine auto-invokes from phase 03.
- [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) — pattern reference (2-agent loop; this engine is the 3-agent loop variant).
- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — public pattern doc.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — `figures.json` schema reference.
- [`../../develop/phase-2-additional-engines.md`](../../develop/phase-2-additional-engines.md) — Engine 4 design rationale.
- [`../../develop/phase-2-decisions.md`](../../develop/phase-2-decisions.md) §3 — the `data_root` three-layer resolution.
