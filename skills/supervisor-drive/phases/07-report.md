# Phase 7 — Report

Comprehensive final report. Always runs — every drive ends here, clean or halted. Appends the canonical `phase: "supervisor-drive-final"` line to `_run-log.jsonl` so phase 00 of the next invocation can detect the close.

## Inputs

From phase 06 (normal halt path), phase 04 (exception path, skipping phase 05), or phase 03 (plan-only / user-halt path):

- `final_verdict` — `DONE | HALT | BLOCKED`
- `final_reason` — string
- `run_id` — supervisor's drive UUID
- `iter` — iter at which the drive halted (or the iter the plan-only run printed)
- `cumulative_tokens_used` — total
- `started_at` — from phase 00
- `mode` — interactive / auto / plan-only
- `resumed_from` — UUID or null
- All commit hashes captured by phase 05 (read from `_run-log.jsonl` `phase: "iter-summary"` records)
- All engine invocations and verdicts (same source)
- For exception path: the path to `run_error.json`
- For plan-only: the projected next 3 actions from phase 03

## Steps

### 1. Compute initial vs final state diff

- Re-read all 5 state files (via the state-read primitive — one call per file).
- Reconstruct the initial state from the first `phase: "start"` record's surrounding state snapshot if available. If no snapshot was captured (OMCR does not snapshot — the diff is computed against the engines' before-and-after writes recorded in `_run-log.jsonl`), use the `_run-log.jsonl` per-iter records to infer the changes.
- Build the diff:

  ```
  Sections approved:   <initial X>/<total> → <final Y>/<total>      (+<Y-X> newly approved)
  Sections drafted:    <initial X> → <final Y>
  Sections empty:      <initial X> → <final Y>
  Sections blocked:    <initial X> → <final Y>
  Citations verified:  <initial X> → <final Y>                       (+<Y-X> newly verified)
  Citations queue:     <initial X pending> → <final Y pending>
  Figures done:        <initial X>/<total> → <final Y>/<total>
  Rebuttals addressed: <initial X> → <final Y>
  submission_ready:    <initial false/true> → <final true/false>
  ```

  If the initial counts cannot be reconstructed (e.g., this is the first drive ever in the project and no prior `_run-log.jsonl` records exist), label them as `(unknown)` and only show the final.

### 2. Engine invocations log

From `_run-log.jsonl` filtered to `phase: "iter-summary"` AND `run_id == <supervisor run_id>`, build a per-iter table:

```
Engine invocations:
  iter 1: /iterate-revision sections/methods.tex      verdict=DONE   tokens=18400  commit=a1b2c3d
  iter 2: /iterate-revision sections/discussion.tex   verdict=DONE   tokens=24600  commit=e4f5g6h
  iter 3: /literature-sweep "neural manifolds"        verdict=DONE   tokens=42100  commit=i7j8k9l
  iter 4: /figure-bake fig3                            verdict=HALT   tokens=14500  commit=m0n1o2p
```

For exception-path drives, the last row shows `verdict=ERROR` instead.

For plan-only drives, this section says `Engine invocations: none — plan-only mode.` and the projection table from phase 03 is shown instead.

### 3. Totals

```
Totals:
  Iterations:    <iter completed> / <max_iter>
  Tokens used:   <cumulative> / <budget>           (<percent>%)
  Wall time:     <formatted duration>              (started <started_at>, ended <now>)
  Commits made:  <count>
  Run id:        <supervisor run_id>
  Resumed from:  <resumed_from or "(fresh drive)">
```

### 4. Verdict-specific tail

#### 4a. `final_verdict == "DONE"`

```
DRIVE COMPLETE.

paper.json: submission_ready = true.

All sections approved. All figures done. All citations verified. All rebuttals
addressed.

Suggested next:
  Review changes:    git log --grep="run=<supervisor run_id>"
  Build manuscript:  cd <manuscript_root> && latexmk -pdf main.tex   (if LaTeX)
  Push to remote:    /sync                                            (snapshot + optional push)
  Push to Overleaf:  use manuscript-scaffold's push flow

The supervisor will not auto-submit. You own the submission.
```

#### 4b. `final_verdict == "HALT"`

```
DRIVE HALTED.

Reason: <final_reason>

What's left (projection from current state):
  iter <iter+1>: <next projected engine> <args> — <reason>
  iter <iter+2>: <next projected engine> <args> — <reason>
  iter <iter+3>: <next projected engine> <args> — <reason>
  ...

The above projection uses phase 02's hardcoded priority rules. If the
projection looks wrong, the priority rules are wrong for your project — open
an issue or use --interactive next time to override step-by-step.

About to dispatch when halt fired:
  engine:     <engine of the iter that halted>
  args:       <args>
  trigger:    <which termination condition / gate fired>

State is durable. Resume with:
  /supervisor-drive --resume <supervisor run_id>     # continue the same trajectory
  /supervisor-drive --fresh                          # start over from current state

For the budget-related halts (conditions 3 / 4), bump the cap:
  /supervisor-drive --auto --budget-tokens <2× current> --resume <supervisor run_id>
```

The "what's left" projection uses the same simulator from phase 03's plan-only branch — project the next 3 actions by simulating successful completions of the current plan.

For safety-gate-declined halts: include the specific gate name and the trigger evidence from phase 04. For BLOCKED-engine halts: include the engine's `reason` verbatim. For max-iter halts: the projection is the most useful section.

#### 4c. `final_verdict == "BLOCKED"`

This is the engine-exception path (phase 04 step 9b — `run_error.json` was written).

```
DRIVE HALTED (engine exception).

A dispatched engine raised an exception. Per Phase 3 §2, the supervisor
halted immediately without retry.

Error details:
  engine:          <engine>
  args:            <args>
  iter:            <iter>
  exception_type:  <type>
  exception_text:  <first 500 chars>
  occurred_at:     <ts>
  error_file:      .claude/omcr-state/run_error.json

Per Phase 3 §2, --resume <run-id> is REJECTED for errored drives. After
addressing the underlying cause, use:
  /supervisor-drive --fresh [other flags]

If the error is reproducible, please file an issue with the contents of
run_error.json.
```

Also applies to `CriticalIssue` gate (gate 6) halts — same shape, but the trigger is the review's critical issue rather than an exception. Output the issue's text verbatim instead of `exception_text`.

#### 4d. Plan-only

```
PLAN-ONLY RUN.

No engines dispatched. No state changed.

Plan that would have run at iter 1:
  <plan dump from phase 02>

Projected next 3 actions:
  iter 1: <engine> <args> — <reason>
  iter 2: <engine> <args> — <reason>
  iter 3: <engine> <args> — <reason>

Cost projection (if you ran --auto with this plan):
  iter 1:  <projected cost> tokens
  iter 2:  <projected cost> tokens
  iter 3:  <projected cost> tokens
  total:   <sum> tokens (vs --budget-tokens <budget>)

Re-run without --plan-only to dispatch:
  /supervisor-drive            (interactive — recommended)
  /supervisor-drive --auto     (autonomous — safety gates still apply)
```

### 5. Append the canonical close to `_run-log.jsonl`

This is the line phase 00 of the **next** invocation looks for to detect a clean close.

```jsonc
{
  "run_id":       "<supervisor run_id>",
  "engine":       "supervisor-drive",
  "phase":        "supervisor-drive-final",
  "mode":         "<mode>",
  "resumed_from": "<resumed_from or null>",
  "started":      "<started_at>",
  "ended":        "<UTC ISO-8601 now>",
  "iter_count":   <iter>,
  "max_iter":     <max_iter>,
  "verdict":      "<DONE | HALT | BLOCKED>",
  "reason":       "<final_reason>",
  "tokens_used":  <cumulative_tokens_used>,
  "budget_tokens": <budget_tokens>,
  "commits_made": <count from iter-summary records>,
  "engines_dispatched": [
    { "iter": 1, "engine": "<name>", "verdict": "<v>" },
    ...
  ]
}
```

Atomic append. If the append fails: log a warning to the transcript (the user has already seen the report above; the missing log line just means phase 00 of the next invocation may see an "open" record and refuse to auto-proceed — which is the safe behavior anyway).

### 6. (Plan-only only) Do not append `supervisor-drive-final`

Wait — plan-only DOES append the final line. The whole point of phase 00 is to detect open drives; a plan-only run that does not close itself would falsely look like a halt on the next invocation.

Plan-only's final line has `verdict: "DONE"` and `reason: "plan-only run completed; no dispatches"`. This way phase 00 sees a clean close.

### 7. (No-op step)

Reserved for future per-phase hooks (e.g., webhook integration as a future addition). This step currently does nothing.

## Failure modes

| Condition | Behavior |
|---|---|
| State re-read fails during diff computation | Skip the diff; show only "(state files unreadable at report time)". Continue rendering the rest of the report. |
| `_run-log.jsonl` append fails for the final close | Log a warning; do not abort (the report has already been printed). The next invocation may see an "open" record and refuse to proceed without `--resume` or `--fresh` — that is the safe default. |
| Projected next 3 actions can't be computed (e.g. priority 1 blocking) | Print only `(projection: drive cannot proceed until blocker resolved)`. |
| Initial state cannot be reconstructed | Show `(unknown)` in the initial column of the diff. |

## What this phase does NOT do

- Does **not** dispatch any engine.
- Does **not** make a final git commit. Phase 05 already committed after each engine; the final report is read-only.
- Does **not** push to a remote. Local state only — pushing is the user's call (or `/sync`'s).
- Does **not** clear `run_error.json` on the exception path. The file stays until the user inspects and re-invokes with `--fresh`.
- Does **not** propose user-visible "what-to-do-next" for `DONE` beyond the bullets above. Submission lives outside OMCR's scope.
- Does **not** suggest a specific value for `--budget-tokens` on resume. The "2× current" hint in the HALT block is a rough rule; the user picks.
- Does **not** suppress its output in `--auto` mode. The final report is the one place autonomous mode always speaks — without it the user has no idea what happened.
