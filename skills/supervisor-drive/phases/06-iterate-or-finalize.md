# Phase 6 — Iterate or finalize

Termination check. After phase 05 (or in the priority 8 / verdict-already-decided case from phase 04), decide whether to loop back to phase 01 (next iter) or fall through to phase 07 (final report).

The 6 termination conditions are evaluated in priority order. The **first** condition that triggers wins. Phase 3 §3 invariant: the supervisor always re-evaluates state from scratch on loop-back — phase 01 always runs, no shortcuts.

## Inputs

From phase 05 (clean path) or phase 04 (engine-null priority 1/2/8 path):

- The most recent `engine_verdict` (`DONE`, `BLOCKED`, `HALT`, or `null` for engine-null paths)
- `cumulative_tokens_used`
- `budget_tokens`
- `iter` — current iter that just completed
- `max_iter` — cap
- `budget_time` — int (minutes) or null
- `started_at` — drive start timestamp from phase 00
- `mode`
- All carry-forward fields

Plus a fresh read of state may be implicit via the loop back to phase 01.

## Termination conditions (in order)

### 1. `submission_ready == true` → DONE

If phase 04 already flipped `paper.json.submission_ready = true` (priority 8 path), or if the most recent engine completion brought every category to its terminal value: emit DONE.

Specifically, this condition fires if **either** of:

- Phase 04 set `submission_ready` directly (priority 8 from phase 02).
- A re-read of `paper.json` shows `submission_ready == true` (some engine the supervisor dispatched flipped it — unusual but possible currently+).

Verdict: `DONE`. Jump to phase 07 with `final_verdict: "DONE"`.

### 2. `iter >= max_iter` → HALT

If the iter that just completed equals `max_iter`: HALT.

```
final_verdict: "HALT"
final_reason:  "max_iter <max_iter> reached without submission_ready"
```

Phase 07 will append a "what's left" projection (using the same simulator from phase 03's plan-only branch — projecting next 3 actions from current state).

### 3. Budget exhausted → HALT

If `cumulative_tokens_used >= budget_tokens`: HALT.

```
final_verdict: "HALT"
final_reason:  "cumulative_tokens_used <X> >= budget_tokens <Y>"
```

This is the **post-hoc** budget cap — distinct from phase 04's pre-dispatch `BudgetExceeded` safety gate. The pre-dispatch gate fires before known-overrun dispatches; the post-hoc cap fires if the engine spent more than projected. Both can fire; this is the second-to-last safety net.

### 4. Wall-clock budget exhausted → HALT (optional)

If `budget_time != null`:

- `elapsed_minutes = (now - started_at) / 60`
- If `elapsed_minutes >= budget_time`: HALT.

```
final_verdict: "HALT"
final_reason:  "wall-clock <elapsed>min >= budget_time <budget_time>min"
```

The check runs at phase-boundary granularity — a single engine that takes 30 minutes will not be interrupted mid-run, but the next iter will not start.

### 5. Safety gate tripped and not confirmed → HALT (already routed)

This condition is normally **handled in phase 04** — a declined gate confirmation halts immediately via phase 07 without returning to phase 06. The condition is listed here for completeness: if phase 06 sees a `gate_declined` marker in the iter-summary (e.g., the gate was tripped, the user declined, phase 04 still routed back to phase 06 by mistake): re-route to phase 07 with `final_verdict: "HALT"`, `final_reason: "<gate> declined; supervisor cannot proceed"`.

In normal operation, phase 04 already jumps to phase 07 on gate decline, and this condition is unreachable. The defensive check is here so that any future refactor of phase 04 cannot silently bypass the gate.

### 6. Engine returned BLOCKED with no auto-recovery → HALT

If the most recent engine completion returned `BLOCKED`:

- The supervisor does NOT auto-retry (Phase 3 §2).
- The supervisor does NOT pick a different engine for the same target (would violate the engine-calls-engine invariant's spirit and break the priority ranker's authority).
- Phase 02's anti-loop guard (step 2) already would have caught a same-target retry. The BLOCKED path here is the first BLOCKED on a target.

For the first BLOCKED:

- If the BLOCKED was a critical-severity issue (the engine surfaced one): phase 04's CriticalIssue gate (gate 6) already halted; phase 06 cannot see this case.
- If the BLOCKED was non-critical (e.g. `[TBD: ...]` markers found, dispatch error inside the engine, file-not-found in precheck): treat as a halt-with-recovery-advice case.

```
final_verdict: "HALT"
final_reason:  "engine <engine> returned BLOCKED: <engine_reason>"
```

Phase 07 will include the engine's `reason` verbatim plus a one-line "how to recover" hint based on the engine name.

Subtle distinction: a BLOCKED return is treated as a halt at the supervisor level. The user re-invokes after addressing the blocker. This is consistent with the per-engine BLOCKED semantics — `$iterate-revision` BLOCKED means "human action required," and the supervisor honors that.

### 7. User interrupted at phase boundary → HALT

If a phase-boundary signal indicates user interruption (Ctrl-C, typed `halt` in phase 03, EOF on stdin):

- The phase that detected the interrupt already jumped to phase 07.
- Phase 06 cannot reach this condition in normal operation; it is here for defensive completeness.

`final_verdict: "HALT"`, `final_reason: "user interrupted at <phase>"`.

### Loop back

If **none** of the above conditions fire (the most recent verdict was a clean `DONE` for the current iter's engine target, iter < max_iter, budget OK, no BLOCKED):

- Increment `iter` by 1.
- Pass control back to phase 01 (state-survey) with the incremented iter and updated `cumulative_tokens_used`.
- Phase 01 re-reads all 5 state files from disk — Phase 3 §3 invariant. The supervisor does NOT carry the prior iter's `paper_state` / `reviews_state` / etc. into the next iter; the new survey is from scratch.

This is the **only** loop-back path in the drive. There are no shortcuts (e.g. "engine returned DONE quickly, skip the next survey") — the re-evaluate-between-every-step invariant is binding.

## Steps

### 1. Evaluate conditions 1–7 in order

First match wins. Each condition computes a `(final_verdict, final_reason)` pair.

### 2. If a condition fires

- Append a `phase: "termination-decision"` line to `_run-log.jsonl`:

  ```jsonc
  {
    "run_id":          "<supervisor run_id>",
    "engine":          "supervisor-drive",
    "phase":           "termination-decision",
    "iter":            <iter>,
    "condition":       "<1-7>",
    "final_verdict":   "<DONE | HALT | BLOCKED>",
    "final_reason":    "<reason>",
    "decided_at":      "<UTC ISO-8601 now>"
  }
  ```

- Jump to phase 07. Pass `final_verdict`, `final_reason`, and all carry-forward fields.

### 3. If no condition fires → loop back

- `iter += 1`.
- Print one line: `[iter <iter>/<max_iter>] looping back to state-survey`.
- Jump to phase 01.

## Failure modes

| Condition | Behavior |
|---|---|
| `_run-log.jsonl` append fails | Bubble OS error; jump to phase 07 with reason `"log append failed"`. |
| `iter` somehow exceeds `max_iter` (off-by-one in a future refactor) | Treat as condition 2 — HALT. Defensive. |
| Engine returned `CONTINUE` (should have been caught in phase 04) | Treat as condition 6 BLOCKED with reason `"engine bug: CONTINUE escaped to phase 06"`. |
| State re-read on loop-back fails | Phase 01 will raise; that abort routes through phase 07's standard halt path. |
| Phase 06 reached with `final_verdict` already set (engine-null path from phase 02) | Honor the already-decided verdict; skip the condition table; jump to phase 07. |

## What this phase does NOT do

- Does **not** dispatch any engine.
- Does **not** mutate any state file (other than the audit-line append to `_run-log.jsonl`).
- Does **not** decide whether to commit (phase 05 did that, before phase 06 ran).
- Does **not** skip phase 01 on loop-back. Re-evaluating state from scratch is the Phase 3 §3 invariant.
- Does **not** carry the prior `paper_state` / `reviews_state` into the next iter. Phase 01 reads fresh state every time.
- Does **not** auto-retry BLOCKED. The user re-invokes the supervisor (or addresses the blocker manually) — `--resume <run-id>` is the path back in.
- Does **not** suggest a "next supervisor run" — that's phase 07's job (the final report).
