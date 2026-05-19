---
name: iterate-revision
description: Revise one manuscript section against the reviewer team until DONE, BLOCKED, or HALT. Loops `@paper-writer` ↔ `@reviewer` with a venue-specific reviewer brief, recording every iteration's issues + verdict to `reviews.json` and updating `paper.json.sections[name]` status / iter. The first OMXR engine — a worked example of how to compose `skills/orchestrate/phases/*` primitives into a domain-specific loop. Safe to re-run; safe to resume after BLOCKED or HALT.
writes: [paper, reviews]
cost_estimate_tokens: 24000
---

# $iterate-revision

This engine runs the smallest viable orchestration shape: one section, one writer, one reviewer, looped until a verdict is reached. It is the proof the orchestration pattern works — Phase 2's four engines are mostly copy-and-vary on top of this one.

If you are reading this because Codex's skill auto-discovery surfaced it: invoke it via `$iterate-revision <section-path>`. Do not edit the manuscript or `.omx/state/omxr/` by hand while a run is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
$iterate-revision <section-path> [--max-iter N] [--venue VENUE] [--force] [--allow-tbd]
```

| Flag | Default | Purpose |
|---|---|---|
| `--max-iter` | `3` | Hard cap. Reaching it without DONE/BLOCKED → HALT. Override via CLI or via `## Research stack` field `iterate_revision.max_iter`. |
| `--venue` | `paper.json.venue` | Reviewer strictness target. CLI wins; falls back to state; if neither is set, abort. |
| `--force` | `false` | Bypass the `status == approved` early-exit. |
| `--allow-tbd` | `false` | Proceed despite `[TBD:` markers in the section file, the per-section outline, or `paper.json.hypothesis` (Phase 1 decision Q2). |

Examples:
- `$iterate-revision sections/results.tex` — defaults; venue from `paper.json`
- `$iterate-revision sections/intro.tex --max-iter 5 --venue Nature`
- `$iterate-revision sections/abstract.tex --venue NeurIPS --force`

## The loop

```
phase 01 — precheck (guards: file exists, venue resolvable, no [TBD: blockers, not approved)
phase 02 — draft-or-revise (@paper-writer)  ┐
phase 03 — review            (@reviewer)    │  repeated up to --max-iter
phase 04 — evaluate          (verdict rule) ┘
phase 05 — finalize (user summary + _run-log.jsonl append)
```

Loop body is phases 02 → 03 → 04. The loop itself is driven by `skills/orchestrate/phases/04-loop.md`; this engine just hands it a dispatch plan and a verdict rule.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — Precheck.** Read [`phases/01-precheck.md`](phases/01-precheck.md).
2. **Phase 2 — Draft or revise.** Read [`phases/02-draft-or-revise.md`](phases/02-draft-or-revise.md).
3. **Phase 3 — Review.** Read [`phases/03-review.md`](phases/03-review.md).
4. **Phase 4 — Evaluate.** Read [`phases/04-evaluate.md`](phases/04-evaluate.md).
5. **Phase 5 — Finalize.** Read [`phases/05-finalize.md`](phases/05-finalize.md).

Phases 02 → 03 → 04 form the loop body. The orchestrate `loop` primitive runs them up to `--max-iter` times.

## Composition

This engine imports the following primitives from `skills/orchestrate/`:

- [`phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — read `paper.json` (phase 01 of this engine) and `reviews.json` (phase 02 of this engine, for last-review lookup).
- [`phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — dispatch `@paper-writer` (phase 02) and `@reviewer` (phase 03) via the Agent tool with inlined persona bodies.
- [`phases/03-evaluate.md`](../orchestrate/phases/03-evaluate.md) — apply the verdict rule defined below; record the reviews.json entry verdict.
- [`phases/04-loop.md`](../orchestrate/phases/04-loop.md) — drive the writer + reviewer dispatch plan through up to `max_iter` iterations; own `_run-log.jsonl` writes; honor `budget_tokens` post-hoc.

This engine **does not** invent its own state-read, dispatch, or loop mechanics. If you find yourself replicating that logic inside a phase file, you're solving the wrong problem — fix the primitive, do not fork it.

## Verdict rule

The verdict is computed at the end of each iteration's reviewer dispatch. Canonical rule (passed as a `severity-threshold` rule spec to `orchestrate/phases/03-evaluate.md`):

| iter | critical | major | result |
|---|---|---|---|
| any   | ≥ 1 | any | **BLOCKED** — critical issue requires structural fix |
| < max | 0   | ≥ 1 | **CONTINUE** — loop another iteration |
| < max | 0   | 0   | **DONE** — section approved |
| = max | 0   | ≥ 1 | **HALT** — iterations exhausted, majors remain |
| = max | 0   | 0   | **DONE** — finished on the last allowed iter |

`minor` and `nit` issues never gate the verdict. They are logged to `reviews.json` and surfaced in the phase 05 summary.

The verdict drives `paper.json.sections[name].status`:

| Verdict | Status set |
|---|---|
| DONE | `approved` |
| BLOCKED | `blocked` |
| HALT | `revising` (left open so the user can resume) |
| CONTINUE | `revising` (loop continues) |

## Cost model

Each iteration is 2 Agent-tool dispatches (writer + reviewer). With `max_iter = 3`, a typical run is ≤ 6 subagent calls. The `cost_estimate_tokens: 24000` frontmatter field is a coarse upper-bound for `$supervisor-drive` budget gating (Phase 3 §6); actuals land in `_run-log.jsonl` post-hoc per Phase 0 decision §6.

Per-iter cost is dominated by the persona body inline (writer ~250 lines, reviewer ~200 lines) plus the section content. Long sections (>500 lines of LaTeX) compound this — the engine does not auto-trim; the user should split very long sections before running.

## What this engine does NOT do

- Does **not** track which issues were "already fixed" across iterations. Only the most recent review is passed to the writer (Phase 1 decision Q1). The reviewer's iter-N+1 read is what catches regressions.
- Does **not** auto-call `verify-citation` when the reviewer flags a missing citation. Citation flags land as ordinary `major`/`minor` issues; the writer addresses them next iter or leaves a `[CITE: ...]` placeholder for `@literature-curator`. (Phase 1 decision Q3 — deferred to Phase 2 `$respond-reviewer`.)
- Does **not** commit to git between iterations by default. Per-iter commit is an opt-in flag (passed to the loop primitive's `on_iter_end` slot); OMXR currently leaves it off.
- Does **not** call another engine. Engines are leaves; if you need to chain, that is `$supervisor-drive`'s job in Phase 3.
- Does **not** rewrite `main.tex` or any non-section file. The writer touches the section file only.

## Re-running policy

- Already-approved section + no `--force` → phase 01 exits cleanly, no agent calls.
- Already-approved section + `--force` → phase 01 flips status to `revising`, the loop runs normally.
- BLOCKED section → phase 01 lets the run proceed; the user is expected to have addressed the critical issue manually before re-running. Iter counter continues.
- HALT section → phase 01 lets the run proceed; iter counter continues from where it left off.
- `[TBD:` marker in the section / outline / hypothesis + no `--allow-tbd` → phase 01 sets `status = blocked-on-tbd` and exits, listing each marker's location.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine composes.
- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — public pattern doc.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — state-file schema reference.
- [`../../develop/phase-1-iterate-revision.md`](../../develop/phase-1-iterate-revision.md) — full design rationale + acceptance scenarios.
- [`../../develop/phase-1-decisions.md`](../../develop/phase-1-decisions.md) — the three locked Phase 1 decisions (Q1, Q2, Q3) with rationale.
