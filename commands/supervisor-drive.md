---
description: Autonomous orchestrator — survey state, pick the right OMCR engine, run it, re-evaluate, loop. Interactive by default. Safety-gated. Supports --auto, --plan-only, --resume, and budget caps.
argument-hint: [--auto | --interactive | --plan-only] [--max-iter N] [--budget-tokens N] [--budget-time MIN] [--resume <run-id>] [--fresh] [--no-commit]
---

# /supervisor-drive

Thin dispatcher — the full autonomous orchestration workflow lives in the `supervisor-drive` skill so the slash-command surface stays small and the workflow can also be invoked outside `/supervisor-drive`.

This is OMCR's most-watched feature: an orchestrator that, given the current project state, picks the right engine, runs it, re-evaluates state, and loops — without per-step user prompting in `--auto` mode. **Safety is the priority** — every dispatch is guarded by 6 confirmation gates that fire even in `--auto`.

## Dispatch

1. Read the bundled skill instructions: [`skills/supervisor-drive/SKILL.md`](../skills/supervisor-drive/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CLAUDE_PLUGIN_ROOT` and continue.

## Signature

```
/supervisor-drive [--auto] [--interactive] [--plan-only]
                  [--max-iter N] [--budget-tokens N] [--budget-time MIN]
                  [--resume <run-id>] [--fresh] [--no-commit]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--interactive` | **on** (default mode) | Confirm each engine dispatch with the user. `yes / pick <alt-num> / no / halt`. Cannot be combined with `--auto` or `--plan-only`. |
| `--auto` | off | Skip per-step confirmation. Safety gates still fire (see SKILL.md §6 / wiki page). Bounded by `--max-iter`, `--budget-tokens`, `--budget-time`. |
| `--plan-only` | off | Run state-survey + action-plan + report. Print the next action and the projected next 3 actions. Do **not** dispatch any engine. Use to preview what `--auto` would do. |
| `--max-iter` | `5` | Total engine invocations across this drive. Reaching it halts cleanly with a "what's left" report. |
| `--budget-tokens` | `50000` | Cumulative token cap. Pre-dispatch check fires `BudgetExceeded` confirm-gate at `cumulative + projected > budget`. Per Phase 3 §6. |
| `--budget-time` | `null` (no cap) | Wall-clock minutes cap. Optional. Halts at next phase boundary if exceeded. |
| `--resume <run-id>` | — | Explicitly continue a halted prior run. Required (along with `--fresh`) when phase 00 detects an open halt; no auto-resume per Phase 3 §1. |
| `--fresh` | off | Explicitly start a new drive from current state, ignoring any halted prior run. Required (along with `--resume`) when phase 00 detects an open halt. |
| `--no-commit` | off | Skip the per-engine git commit normally made in phase 05. Default is commit-on so runs are easy to roll back. |

## Usage examples

### Interactive mode (default)

```
/supervisor-drive
```

The skill surveys state, prints the next planned action, and waits for `yes / pick <alt-num> / no / halt`. Repeats after every engine completes. This is the safe default — every dispatch is user-acked.

### Autonomous mode

```
/supervisor-drive --auto --max-iter 5 --budget-tokens 80000
```

Runs without per-step confirmation, bounded by `--max-iter` and `--budget-tokens`. Halts cleanly on:
- `submission_ready == true`
- iter cap reached
- budget exhausted
- any safety gate tripped without user confirmation
- engine BLOCKED or exception

### Plan-only mode

```
/supervisor-drive --plan-only
```

Prints the next-action plan and projected next 3 actions. Dispatches nothing. Use to preview an `--auto` run before committing to it.

### Resuming a halted run

If a prior drive halted (engine returned BLOCKED, safety gate tripped, or user-interrupted), the next `/supervisor-drive` invocation prints a halt-summary and exits unless you pass one of:

```
/supervisor-drive --resume a1b2c3d4-0001-...   # continue the same trajectory
/supervisor-drive --fresh                       # start a new drive, ignore the prior halt
```

This is strict on purpose — see Phase 3 §1 in [`develop/phase-3-decisions.md`](../develop/phase-3-decisions.md). Auto-resume is a foot-gun under common scenarios (manual edits, branch switches, hand-run engines between drives).

## Mode exclusivity

- `--interactive`, `--auto`, `--plan-only` are mutually exclusive. The skill aborts in phase 00 if more than one is set.
- `--resume <run-id>` and `--fresh` are mutually exclusive.

## What this command does NOT do

- Does **not** call engines directly. Engines are leaves; only the supervisor-drive skill chains them, and even then by re-evaluating state from scratch between every step (Phase 3 §3).
- Does **not** dispatch multiple engines in parallel. Single-target only currently (Phase 3 §4). Parallel batch is a future backlog item.
- Does **not** override the bottleneck-ranker via CLAUDE.md. Hardcoded currently (Phase 3 §5). Escape hatches: `--interactive` (pick an alternative each step) and `--plan-only` (inspect without running).
- Does **not** retry engine exceptions. Halt-on-exception, no retry (Phase 3 §2). A `run_error.json` is written next to `_run-log.jsonl` and the loop jumps to the final report.
- Does **not** push to a remote. Per-engine commits are local. If you want to push afterward, run `/sync` or use the manuscript-scaffold push flow.

## See also

- [`skills/supervisor-drive/SKILL.md`](../skills/supervisor-drive/SKILL.md) — the workflow this command dispatches.
- [`wiki/Autonomous-Drive.md`](../wiki/Autonomous-Drive.md) — public deep dive on the 3 modes, 6 safety gates, priority rules, and cost model.
- [`wiki/Orchestration-Model.md`](../wiki/Orchestration-Model.md) — state store + 4 primitives + engines-are-leaves invariant.
- [`develop/phase-3-autonomous-supervisor.md`](../develop/phase-3-autonomous-supervisor.md) — design spec.
- [`develop/phase-3-decisions.md`](../develop/phase-3-decisions.md) — locked decisions §1–§6.
