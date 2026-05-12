---
name: supervisor-drive
description: Autonomous OMCR orchestrator. Surveys state across the 5 OMCR state files (paper, reviews, citations, figures, rebuttals), picks the highest-priority engine from a hardcoded bottleneck-ranker, runs it through one of the 5 OMCR engines, then re-evaluates state from scratch and loops. Three modes — interactive (default), auto, plan-only. Six safety gates (HypothesisChange, NewCitation, NewExperiment, StructuralRewrite, BudgetExceeded, CriticalIssue) fire even in --auto. Single-target only currently. Halt-on-exception, no retry. Resume after halt is strict — requires explicit --resume <run-id> or --fresh.
writes: [paper, reviews, citations, figures, rebuttals]
cost_estimate_tokens: 80000
---

# /supervisor-drive

This engine sits at the top of OMCR's orchestration tree. Unlike the five Phase 1 / Phase 2 engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`), `/supervisor-drive` does not itself dispatch personas. Instead it dispatches **other engines** — and only the supervisor is allowed to do that. The whole point of this skill is to be the one place where engine sequencing lives so the engines themselves can stay simple leaves.

If you are reading this because Claude Code's skill auto-discovery surfaced it: invoke it via `/supervisor-drive` (the slash command — defaults to `--interactive`). Do not edit `.claude/omcr-state/` by hand while a drive is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
/supervisor-drive [--auto] [--interactive] [--plan-only]
                  [--max-iter N] [--budget-tokens N] [--budget-time MIN]
                  [--resume <run-id>] [--fresh] [--no-commit]
```

| Flag | Default | Purpose |
|---|---|---|
| `--interactive` | on | Confirm each engine dispatch with the user. Default mode if none of `--auto`/`--plan-only` is passed. |
| `--auto` | off | Skip per-step confirmation. Safety gates still fire. Bounded by `--max-iter`, `--budget-tokens`, `--budget-time`. |
| `--plan-only` | off | Run phases 00 + 01 + 02 + 07. Print the next action + projected next 3 actions. Dispatch nothing. |
| `--max-iter` | `5` | Total engine invocations across this drive. Hit it → HALT with "what's left" report. |
| `--budget-tokens` | `50000` | Cumulative token cap. Pre-dispatch `BudgetExceeded` gate fires when `cumulative + projected > budget`. |
| `--budget-time` | `null` | Wall-clock minutes cap. Optional. Halts at phase boundary if exceeded. |
| `--resume <run-id>` | — | Explicit continuation of a halted prior run. Required (with `--fresh`) when phase 00 detects an open halt. |
| `--fresh` | off | Explicit fresh drive ignoring any halted prior run. Required (with `--resume`) when phase 00 detects an open halt. |
| `--no-commit` | off | Skip the per-engine git commit in phase 05. Default is commit-on (autonomous mode without commits = chaos to roll back). |

Mode flags (`--interactive`, `--auto`, `--plan-only`) are mutually exclusive. `--resume` and `--fresh` are mutually exclusive.

## The 3 modes

### `--interactive` (default)

Phase 03 prints the planned next action and waits for the user. Acceptable responses:

- `yes` — dispatch the planned engine.
- `pick <n>` — dispatch the n-th alternative instead.
- `no` — skip this iter; loop back to phase 01 (which may pick the same plan again or, if the user manually changed state, a different one).
- `halt` — exit cleanly via phase 07.

After every engine completes (success, BLOCKED, or safety-gate trip with user-decline), the cycle repeats. The user can interrupt at any phase boundary (Ctrl-C / typed halt).

### `--auto`

Phase 03 skips confirmation. The loop runs until any of the 6 termination conditions in phase 06 triggers. Safety gates (phase 04) still require explicit confirmation phrases even in `--auto` — they are the one place autonomous mode pauses.

### `--plan-only`

Phases 00 + 01 + 02 + 07 run. Phase 03 is skipped (no confirmation, no dispatch). Phase 07 prints:
- the current `next_action` plan,
- a projection of the next 3 actions (by simulating "what would phase 01 say if the planned engine had returned DONE?"),
- the same initial-state-vs-final-state diff phase 07 always emits (in plan-only mode the diff is empty by construction).

Use this to preview what `--auto` would do. Nothing is written to disk except the standard `_run-log.jsonl` start + end + summary records that mark the plan-only run.

## The 8 phases

```
phase 00 — resume-check       (halt detection + --resume / --fresh handling)  [skip-if: no prior halt]
phase 01 — state-survey       (read all 5 state files, build current_picture)
phase 02 — action-plan        (apply hardcoded priority rules → next_action + alternatives)
phase 03 — confirm-or-auto    (branch by mode; safety-gate pre-check delegated to phase 04)
phase 04 — engine-invoke      (safety-gate-protected dispatch; halt-on-exception)
phase 05 — checkpoint         (git commit, _run-log.jsonl summary, budget tally)
phase 06 — iterate-or-finalize (termination check; loop back to phase 01 or fall through to 07)
phase 07 — report             (final report; _run-log.jsonl phase: "supervisor-drive-final")
```

The loop body is phases 01 → 02 → 03 → 04 → 05 → 06. Phase 00 runs once at entry. Phase 07 runs once at exit (clean or halt).

## Phase execution

Execute phases in order. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 0 — Resume check.** Read [`phases/00-resume-check.md`](phases/00-resume-check.md).
2. **Phase 1 — State survey.** Read [`phases/01-state-survey.md`](phases/01-state-survey.md).
3. **Phase 2 — Action plan.** Read [`phases/02-action-plan.md`](phases/02-action-plan.md).
4. **Phase 3 — Confirm or auto.** Read [`phases/03-confirm-or-auto.md`](phases/03-confirm-or-auto.md).
5. **Phase 4 — Engine invoke.** Read [`phases/04-engine-invoke.md`](phases/04-engine-invoke.md).
6. **Phase 5 — Checkpoint.** Read [`phases/05-checkpoint.md`](phases/05-checkpoint.md).
7. **Phase 6 — Iterate or finalize.** Read [`phases/06-iterate-or-finalize.md`](phases/06-iterate-or-finalize.md).
8. **Phase 7 — Report.** Read [`phases/07-report.md`](phases/07-report.md).

Phases 01 → 06 are the loop. The orchestrate `loop` primitive is **not** used here — this skill is itself a higher-order loop that dispatches engines rather than persona subagents, so the primitive's dispatch-plan shape does not fit. The skill writes `_run-log.jsonl` start + end + summary records directly, mirroring the primitive's pattern.

## Composition

This engine reads, but does not directly invoke, the four orchestrate primitives. It dispatches **engines**, which in turn compose those primitives.

- [`../orchestrate/phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — used in phase 01 to read each of the 5 state files (one call per file: `paper`, `reviews`, `citations`, `figures`, `rebuttals`). Phase 00 also tails `_run-log.jsonl` directly (not via this primitive — it is append-only and read with normal file I/O).
- [`../orchestrate/phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — **not** invoked by this engine. The supervisor does not dispatch personas; it dispatches engines. The engines themselves use this primitive.
- [`../orchestrate/phases/03-evaluate.md`](../orchestrate/phases/03-evaluate.md) — not invoked. There is no severity-threshold verdict at the supervisor level; the verdicts come from each engine's own evaluator.
- [`../orchestrate/phases/04-loop.md`](../orchestrate/phases/04-loop.md) — not invoked as a primitive. This engine's loop body is phase 01 → 06; the `_run-log.jsonl` start + end + summary writes follow the primitive's record shape (with an additional `phase: "supervisor-drive-final"` line per phase 07) so a JSONL reader sees consistent records across all engines.

### Engine compositions

The supervisor dispatches engines as if invoking their slash commands. Each engine returns a verdict (`DONE | BLOCKED | HALT` — `CONTINUE` is engine-internal). The supervisor uses the verdict + the freshly re-read state to plan the next iter.

| Engine | Slash command | When the ranker picks it |
|---|---|---|
| [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) | `/iterate-revision <section-path>` | Priorities 4, 5 — unwritten sections (no outline) or drafted-but-unreviewed sections. |
| [`../literature-sweep/SKILL.md`](../literature-sweep/SKILL.md) | `/literature-sweep <topic>` | Priority 3 — citations queue has pending entries or text has `[CITE: ...]` placeholders. |
| [`../respond-reviewer/SKILL.md`](../respond-reviewer/SKILL.md) | `/respond-reviewer <letter>` | Priority 6 — `rebuttals.json` has unresolved entries. |
| [`../figure-bake/SKILL.md`](../figure-bake/SKILL.md) | `/figure-bake <fig-id>` | Priority 7 — figures with brief-vs-impl status divergence. |
| [`../outline-expand/SKILL.md`](../outline-expand/SKILL.md) | `/outline-expand <outline-path>` | Priority 4 — unwritten sections **and** an outline exists. |

The supervisor never bypasses an engine's own precheck phase. If `/iterate-revision`'s phase 01 sees `[TBD: ...]` markers, it sets the section to `blocked-on-tbd` and exits with BLOCKED; the supervisor sees BLOCKED on return and lets the priority ranker handle it on the next iter (priority 2 — halts with `blocked-on-tbd` advisory).

## The bottleneck-ranker — hardcoded priority rules

Phase 02 applies these rules in order. The **first match wins** — no weighted scoring currently. See [`phases/02-action-plan.md`](phases/02-action-plan.md) for the full implementation; the summary table:

| # | Trigger | Engine / response |
|---|---|---|
| 1 | Any section `status: blocked` | **HALT** with bottleneck report. Human action required. |
| 2 | Any section `status: blocked-on-tbd` | **HALT** asking user to resolve TBDs or pass `--allow-tbd` to the engine on the next manual invocation. |
| 3 | Critical citations missing (manuscript text has `[CITE: ...]` placeholders OR `citations.json.queue` has `pending` entries) | `/literature-sweep <topic>` (or `@literature-curator` per phase 02 step 3). |
| 4 | Unwritten sections (`status: empty`) | `/outline-expand <outline-path>` if an outline exists; else `/iterate-revision <section-path>` single-section. |
| 5 | Drafted-but-unreviewed sections (`status: drafted`) | `/iterate-revision <section-path>`. |
| 6 | Pending reviewer rebuttals (`rebuttals.json` has entries with run-level `HALT` OR per-comment `deferred` / `disputed`) | `/respond-reviewer <letter>`. |
| 7 | Figures with brief-vs-impl divergence (`figures.json` entry where `brief_status == approved` but `impl_status != approved`, or `critique_status == done` and the latest verdict was BLOCKED/HALT) | `/figure-bake <fig-id>`. |
| 8 | All approved + all figures done + all citations verified | `submission_ready = true`. **EXIT DONE.** |

Priority rules are **hardcoded** currently per Phase 3 §5. No `CLAUDE.md`-driven override, no JSON knob, no flag. Users who disagree on a specific run use `--interactive` (pick an alternative) or `--plan-only` (inspect and stop).

## The 6 safety gates

Every dispatch is guarded by 6 pre-dispatch gates. **Every gate is confirm-required even in `--auto` mode.** The user must type the named confirmation phrase — not just "yes" — to proceed. This is uncomfortable on purpose.

| # | Gate | Trigger | Confirmation phrase | Notes |
|---|---|---|---|---|
| 1 | **HypothesisChange** | Engine args or task brief mentions any change to `paper.json.hypothesis`. | `confirm-hypothesis-change` | Research integrity — the supervisor must not silently shift the central claim. |
| 2 | **NewCitation** | Engine intends to add a `references.bib` entry that is not already in `citations.json.verified` queue. | `confirm-new-citation` | Prevents hallucinated references. `/literature-sweep`'s hard verify-gate covers most cases; this gate catches engine-author leaks. |
| 3 | **NewExperiment** | Brief contains keywords: `"design a new experiment"`, `"collect more data"`, `"run a new analysis"`, `"acquire"`. | `confirm-new-experiment` | Real-world action, not a model output. |
| 4 | **StructuralRewrite** | Brief contains keywords: `"restructure"`, `"reframe"`, `"change conclusion"`, `"pivot"`, `"flip the framing"`. | `confirm-structural-rewrite` | Likely needs human ownership; scope-change risk. |
| 5 | **BudgetExceeded** | `cumulative_tokens_used + projected_cost > budget_tokens`. Projected cost = engine's `cost_estimate_tokens` × 1.25, OR rolling median of last 5 same-engine entries in `_run-log.jsonl` × 1.25 if N≥5. | `confirm-budget` | Fires before dispatch, not after. Cost containment per Phase 3 §6. |
| 6 | **CriticalIssue** | A prior engine in the same drive returned BLOCKED with `severity: critical` (e.g. a `@reviewer` flagged a power/methodology issue the writer cannot fix). | (no override — always halt) | The only gate with no confirmation phrase. Always halts the drive. Phase 07 surfaces the full review. |

Gates 1–4 scan the engine's planned `task_brief` and `engine_args` for the trigger keywords. Gate 5 is numerical. Gate 6 is verdict-based.

On gate trip in `--interactive`: phase 04 prints the gate name + trigger evidence + projected cost (for gate 5) and waits for the named confirmation phrase. On gate trip in `--auto`: phase 04 emits `awaiting confirmation` + the full dump and waits for user input — autonomous mode **pauses** here. Gate 6 never accepts confirmation; the drive halts and phase 07 reports.

## The invariants (non-negotiable)

These are the rules every phase enforces:

### Engine-calls-engine invariant

Engines never invoke other engines (Phase 2 §5, Phase 3 §3). The supervisor is the **only** thing that may chain engines, and even it does so by **re-evaluating state from scratch between every step** — phase 01 always runs after phase 06 says "loop again". No engine's dispatch plan calls another engine. No engine's output triggers another engine directly. The supervisor sees the verdict + the freshly-read state, and the priority ranker picks the next move.

This makes the loop fully described by `loop { survey → plan → confirm → dispatch → checkpoint → iterate }` with no special cases. It also means **safety gates fire at every transition**, not only at the top level — every dispatch is a fresh phase 04 evaluation.

### Single-target invariant

`next_action` is always exactly one engine + one target (Phase 3 §4). No "iterate-revision on methods AND discussion simultaneously." No parallel dispatch. `alternatives` in the action plan is for the interactive-mode picker only, never for parallel execution. Batch / parallel modes are deferred.

### Explicit-resume invariant

Per Phase 3 §1. After any halt, the next `/supervisor-drive` invocation does not auto-resume. Phase 00 surveys `_run-log.jsonl`, detects any prior run without a clean `verdict: "DONE"` close, and exits non-zero with a one-screen summary unless the user passes `--resume <run-id>` or `--fresh`. Resumed runs record `resumed_from: <run-id>` in their start entry for audit.

### Halt-on-exception invariant

Per Phase 3 §2. Engine exceptions (not BLOCKED — actual errors: missing file, tool failure, malformed state, parse error, network drop) halt the drive immediately. No retry. No fallback engine. No alternative dispatch. Phase 04 writes `run_error.json` next to `_run-log.jsonl` with engine name, args, exception text, and timestamp. Control jumps directly to phase 07 (skipping phase 05's commit — there is nothing meaningful to commit on a partial dispatch).

## Cost model

`cost_estimate_tokens: 80000` is the frontmatter declaration for a typical full drive run (≈4 engine dispatches × ~20k tokens each, with overhead). It is a coarse upper-bound for nested invocations of this skill (e.g., a meta-orchestrator that called `/supervisor-drive` itself).

Within a drive, phase 04 estimates per-engine cost using:

1. **Rolling median** of the last 5 same-engine `phase: "end"` records in `_run-log.jsonl` (i.e., the last 5 `tokens_used` values for that engine). If N ≥ 5, use the median.
2. **Declared `cost_estimate_tokens`** from the engine's SKILL.md frontmatter. If N < 5, use the declared constant.
3. **Multiply by 1.25** as conservative padding (Phase 3 §6).

The `BudgetExceeded` gate fires when `cumulative_tokens_used + projected_cost × 1.25 > budget_tokens`. Wrong-by-25% is fine; wrong-by-2x is the failure mode this guards against.

## Checkpointing

After every engine completes (phase 05), unless `--no-commit` was passed:

```
git add -A
git commit -m "omcr supervisor-drive: <engine> <args> verdict=<v> run=<run-id>"
```

The commit message includes the engine name, the first 60 chars of the args, the engine's returned verdict (`DONE | BLOCKED | HALT`), and the supervisor's `run_id`. This is the same `run_id` the `_run-log.jsonl` start / end records use, so commit-history and run-log are joinable.

If the commit fails (e.g. nothing to commit — engine was read-only, or `--draft-only` mode), phase 05 logs a warning and continues. It does not abort the drive.

Per-engine commits are **on by default** for supervisor-drive (unlike `/iterate-revision` which is off-by-default). Reason: autonomous mode without commits = chaos to roll back if it goes wrong. Users who want quiet history pass `--no-commit`.

## State files this engine reads / writes

| File | R/W | Purpose |
|---|---|---|
| `paper.json` | read | All sections, hypothesis, submission_ready. |
| `reviews.json` | read | Prior reviewer verdicts. |
| `citations.json` | read | `queue` (pending placeholders) + `verified` (audit gate 2). |
| `figures.json` | read | Per-figure brief/impl/critique status. |
| `rebuttals.json` | read | Pending reviewer rebuttals (priority 6 trigger). |
| `_run-log.jsonl` | append | Start + end + per-iter summary + final report records. |
| `run_error.json` | conditional write | Only on engine exception (Phase 3 §2). One per halt. Sibling of `_run-log.jsonl`. |

The supervisor **declares `writes: [paper, reviews, citations, figures, rebuttals]`** because the engines it dispatches collectively mutate all 5. This is the broadest `writes:` declaration in OMCR — and the only engine that touches every state file — by design. Reviewers grepping `writes:` see at a glance that supervisor-drive is the one place every state file is in scope.

## What this engine does NOT do

- Does **not** call personas directly. Only engines. (Personas are inside engines.)
- Does **not** dispatch engines in parallel. Single-target only currently (Phase 3 §4).
- Does **not** retry on engine exception. Halt-on-exception, no retry (Phase 3 §2).
- Does **not** auto-resume after a halt. Explicit `--resume <run-id>` or `--fresh` required (Phase 3 §1).
- Does **not** override safety gates in `--auto` mode. Every gate is confirm-required; autonomous mode pauses at the gate.
- Does **not** read a `CLAUDE.md` priority-override block. Hardcoded ranker currently (Phase 3 §5).
- Does **not** push to a remote. Per-engine commits are local. Run `/sync` afterward to push.
- Does **not** rewrite `main.tex`, `references.bib`, or any non-state file directly. All file edits are mediated through the engine the supervisor invoked.
- Does **not** modify other engines' SKILL.md or phase files at runtime. Engine logic is static markdown; the supervisor reads it.

## Re-running policy

- **Clean prior run** (last entry in `_run-log.jsonl` has `verdict: "DONE"` and `phase: "supervisor-drive-final"`) → new drive starts immediately. Phase 00 prints a one-line "prior run completed cleanly" and proceeds.
- **Halted prior run** (start record without matching `phase: "supervisor-drive-final"`, or final record verdict was HALT / BLOCKED with safety gate trip) → phase 00 exits non-zero unless `--resume <run-id>` or `--fresh` is passed.
- **Errored prior run** (`run_error.json` exists for a recent run) → phase 00 surfaces the error file's contents and refuses to proceed without `--fresh`. Resume after exception is not allowed — the user must inspect the error.
- **`--resume <run-id>`** → phase 00 records `resumed_from: <run-id>` in the new run's start entry. The new drive's iter counter starts at 1; engines have their own internal iter counters.
- **`--fresh`** → phase 00 starts a new drive ignoring all prior halts. No resumption marker. Useful when the user has manually fixed state between drives.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine delegates to via the engines it dispatches.
- [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) — Phase 1 engine, primary dispatch target for sections.
- [`../literature-sweep/SKILL.md`](../literature-sweep/SKILL.md) — Phase 2 engine, dispatched on citation gaps.
- [`../respond-reviewer/SKILL.md`](../respond-reviewer/SKILL.md) — Phase 2 engine, dispatched on rebuttals.
- [`../figure-bake/SKILL.md`](../figure-bake/SKILL.md) — Phase 2 engine, dispatched on figure divergence.
- [`../outline-expand/SKILL.md`](../outline-expand/SKILL.md) — Phase 2 engine, dispatched on empty sections with an outline.
- [`../../agents/supervisor.md`](../../agents/supervisor.md) — the advisory persona that pairs with this skill. `@supervisor` is read-only; `/supervisor-drive` is the executor.
- [`../../wiki/Autonomous-Drive.md`](../../wiki/Autonomous-Drive.md) — public deep dive on modes, gates, ranker, cost model, and OMC composability.
- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — state store + engines-are-leaves invariant.
- [`../../develop/phase-3-autonomous-supervisor.md`](../../develop/phase-3-autonomous-supervisor.md) — design spec.
- [`../../develop/phase-3-decisions.md`](../../develop/phase-3-decisions.md) — locked decisions §1–§6.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — state-file schema reference.
