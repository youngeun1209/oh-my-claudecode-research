# Phase 0 — Resume check

Entry guard. Detects any halted prior drive in `_run-log.jsonl` and refuses to proceed unless the user explicitly passes `--resume <run-id>` or `--fresh`. Implements Phase 3 §1 (strict, user ACK).

## Inputs

From the skill:

- `--auto` / `--interactive` / `--plan-only` — mode (mutually exclusive). Default `--interactive` if none passed.
- `--max-iter N` — default `5`.
- `--budget-tokens N` — default `50000`.
- `--budget-time MIN` — default null.
- `--resume <run-id>` — optional.
- `--fresh` — optional flag.
- `--no-commit` — optional flag.

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate mode flags

The mode flags `--interactive`, `--auto`, `--plan-only` are mutually exclusive. If more than one is set, abort:

```
supervisor-drive: --interactive, --auto, --plan-only are mutually exclusive.
Pick exactly one (or omit all three; default is --interactive).
```

`--resume <run-id>` and `--fresh` are also mutually exclusive. If both are set, abort:

```
supervisor-drive: --resume <run-id> and --fresh are mutually exclusive.
Pick one based on phase 00's halt-summary, or omit both if no prior halt.
```

Record the resolved mode as `mode ∈ {interactive, auto, plan-only}` for forward phases.

### 2. Read `_run-log.jsonl`

Open `.omx/state/omxr/_run-log.jsonl` for reading.

- **File missing** → no prior drives exist. Skip to step 6 (initialize new drive). Note in the run-start log: `first_drive_in_project: true`.
- **File present but empty** → same as missing. Skip to step 6.
- **File present and non-empty** → parse each line as JSON. Lines that fail to parse: log a warning to the user (`supervisor-drive: skipping malformed line in _run-log.jsonl`) and skip them. Continue with the parsed entries.

The supervisor reads `_run-log.jsonl` with normal file I/O — this file is append-only and is not read via the `state-read` primitive.

### 3. Detect halted prior drives

Scan the parsed entries for any `engine: "supervisor-drive"` records. A drive is **clean** if both of these are true:

- There is a `phase: "start"` record with run_id R.
- There is a corresponding `phase: "supervisor-drive-final"` record with the same run_id R **and** `verdict: "DONE"`.

A drive is **halted** if either of:

- The `phase: "start"` record exists with run_id R, but no matching `phase: "supervisor-drive-final"` record for R is present.
- The `phase: "supervisor-drive-final"` record exists for R but `verdict ∈ {HALT, BLOCKED}`.

A drive is **errored** if `.omx/state/omxr/run_error.json` exists and its `run_id` matches a recent (non-clean) drive in `_run-log.jsonl`.

Build a list of recent drives (last 5) with their `run_id`, `started`, `verdict` (or `(open)` if no final record), and the engine name from the last per-iter summary record for that drive. Most recent first.

### 4. Branch on detected state

Apply in order:

#### 4a. No prior drive

(File missing / empty.) Skip to step 6.

#### 4b. Errored prior drive

`run_error.json` exists for a recent halted drive.

- If `--fresh` was passed: archive `run_error.json` to `run_error.json.<timestamp>.bak` (rename in place) and proceed to step 6 with a new run.
- If `--fresh` was **not** passed: print the contents of `run_error.json` plus a one-paragraph explainer and exit non-zero:

  ```
  supervisor-drive: prior drive (run_id=<R>) errored. Errors are not auto-recoverable.
  Inspect the error below, then re-invoke with --fresh once the underlying cause is resolved.

  <pretty-printed contents of run_error.json>

  Re-invoke:
    $supervisor-drive --fresh [other flags]
  ```

  `--resume <run-id>` is **rejected** for errored drives. The user must inspect the error first.

#### 4c. Halted prior drive (no error)

A halted drive exists, no `run_error.json`.

- If `--resume <run-id>` was passed and `<run-id>` matches a halted drive: record `resumed_from: <run-id>` for the new run, copy any safety-gate confirmation state from the halted drive's `phase: "supervisor-drive-final"` record (if present — it carries the halted action context), and proceed to step 6.
- If `--resume <run-id>` was passed but `<run-id>` does not match a recent halted drive: abort.
  ```
  supervisor-drive: --resume <run-id> does not match any recent halted drive.
  Recent drives:
    <run_id> started <ts> verdict <v>
    ...
  Use --fresh to start a new drive instead.
  ```
- If `--fresh` was passed: proceed to step 6 with a new run. No `resumed_from` marker.
- If **neither** was passed: print the one-screen halt summary and exit non-zero:

  ```
  supervisor-drive: prior drive halted. Choose how to proceed.

  Most recent halt:
    run_id:       <run-id of most recent halted drive>
    started:      <UTC ISO-8601>
    halt verdict: <HALT | BLOCKED | (open — no final record)>
    last engine:  <engine name from last per-iter summary record>
    last args:    <engine args from same record>
    reason:       <reason string from final record, or "no final record (drive was interrupted)">
    last commit:  <git log -1 --format='%h %s' or "(no commits in this drive)">

  Resume options:
    $supervisor-drive --resume <run-id>     # continue the same trajectory
    $supervisor-drive --fresh               # start a new drive from current state

  See develop/phase-3-decisions.md §1 for why this requires an explicit flag.
  ```

  Exit non-zero. Do not proceed.

#### 4d. Clean prior drive (or all prior drives clean)

Most recent drive is clean. Print a one-line acknowledgment and proceed to step 6:

```
supervisor-drive: prior drive run_id=<R> completed cleanly (verdict=DONE). Starting new drive.
```

`--resume <run-id>` against a clean drive is allowed but discouraged — it starts a new run with `resumed_from` set, but the prior run had nothing to resume from. Phase 00 emits a warning and proceeds.

### 5. (reserved for future deferral logic)

No-op currently. The decision tree above covers every Phase 3 §1 case.

### 6. Initialize the new drive

Generate a fresh `run_id` (UUID v4). Append a `phase: "start"` record to `_run-log.jsonl`:

```jsonc
{
  "run_id":       "<uuid>",
  "engine":       "supervisor-drive",
  "args":         { "mode": "<mode>",
                    "max_iter": <int>,
                    "budget_tokens": <int>,
                    "budget_time": <int or null>,
                    "no_commit": <bool> },
  "resumed_from": "<prior-run-id or null>",
  "started":      "<UTC ISO-8601 now>",
  "phase":        "start"
}
```

Use atomic append (`open(..., "a")` + flush + fsync), per the orchestrate `loop` primitive's pattern.

### 7. Hand off to phase 01

Pass forward to phase 01:

- `run_id` — UUID
- `mode` — one of `interactive`, `auto`, `plan-only`
- `max_iter` — int (loop cap)
- `budget_tokens` — int
- `budget_time` — int or null
- `no_commit` — bool
- `resumed_from` — UUID or null
- `cumulative_tokens_used` — int, starts at 0 (or restored from prior drive's last summary if `--resume`)
- `iter` — int, starts at 1 (or restored from prior drive's last summary `iter + 1` if `--resume`)
- `started_at` — UTC ISO-8601 from step 6

## Failure modes

| Condition | Behavior |
|---|---|
| Mode flags conflict | Abort with the mutex message. |
| `--resume` + `--fresh` together | Abort with the mutex message. |
| `_run-log.jsonl` malformed lines | Skip each one with a warning. Do not abort. |
| `_run-log.jsonl` entirely unreadable (permission denied) | Abort with the OS error and the path. |
| `--resume <run-id>` matches nothing | Abort with the recent-drives list. |
| `--resume` against an errored drive | Reject; require `--fresh`. |
| `run_error.json` exists but corrupt | Warn, treat as if absent (the halted-drive branch handles the rest). |
| Append to `_run-log.jsonl` fails | Bubble the OS error and abort — running a drive without a log trail is unsafe. |

## What this phase does NOT do

- Does **not** read any of the 5 state JSON files. Phase 01 does that.
- Does **not** dispatch any engine. Zero dispatches in phase 00.
- Does **not** auto-resume. The whole point of this phase is to refuse auto-resume per Phase 3 §1.
- Does **not** clear `run_error.json` except in the `--fresh` branch (and even then, it renames it to a `.bak` rather than deleting it).
- Does **not** commit to git. Phase 05 handles per-engine commits; phase 00 only initializes the run log.
- Does **not** validate the user's `--max-iter` / `--budget-tokens` flags beyond accepting them. Phase 06 enforces them at the iteration boundary.
