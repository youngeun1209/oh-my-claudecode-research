# Phase 3 — Confirm or auto

Branch by `mode`. The action plan from phase 02 is either user-acked (interactive), printed-and-skipped (plan-only), or passed straight to phase 04 (auto). Safety-gate pre-check is delegated to phase 04 — this phase only handles the user-facing branch.

## Inputs

From phase 02:

- `plan` — the structured action plan
- `current_picture`
- All carry-forward fields (run_id, mode, iter, max_iter, cumulative_tokens_used, no_commit, etc.)

## Steps

### 1. Branch by `mode`

#### 1a. `mode == "plan-only"`

Print the plan and a projection of the next 3 actions. Do not dispatch.

```
plan-only:
  Next action:
    engine:   <plan.next_action.engine>
    args:     <pretty-print args>
    reason:   <plan.next_action.reason>
    priority: <plan.next_action.priority>

  Alternatives (interactive-mode picker only):
    1. <alt.engine> <args> — <alt.reason>
    ...

  Projected next 3 actions (if next_action were to return DONE):
    iter <iter+1>: <projected engine> <projected args> (priority <P>)
    iter <iter+2>: <projected engine> <projected args> (priority <P>)
    iter <iter+3>: <projected engine> <projected args> (priority <P>)

  Cost projection:
    engine constant:     <cost_estimate_tokens from engine SKILL.md>
    rolling median:      <int or "(N<5 — using constant)">
    projected this iter: <projected_cost> × 1.25 padding = <padded>
    cumulative + padded: <cumulative_tokens_used + padded> / <budget_tokens>
    safety:              <"within budget" or "would trip BudgetExceeded gate">
```

The projection is computed by simulating: "if `next_action` returned DONE, what would phase 01 say next?" — concretely, mutate a deep copy of `current_picture` to reflect the post-DONE state (e.g., flip the section's status to `approved`), then re-run phase 02's priority rules on the copy. Repeat 3 times. If the simulation reaches priority 8 (submission ready) before 3 projections, stop and note `"submission ready after iter <i>"`.

After printing, jump directly to phase 07 (report). Do **not** call phase 04 (no dispatch). The drive ends cleanly in plan-only mode; no engine ran, no state changed.

#### 1b. `mode == "auto"`

Skip user confirmation. Pass the plan through to phase 04, which still runs the 6 safety-gate pre-check. Autonomous mode does not bypass gates (Phase 3 §5 + the spec §5 safety table).

If `plan.next_action.engine == null` (priority 1, 2, or 8 emitted a verdict directly): jump to phase 06 with the named verdict. Phase 06 will route HALT to phase 07 or DONE to phase 07 + submission_ready write.

Otherwise: call phase 04 with `plan` + carry-forward fields. Print one line:

```
auto: dispatching <engine> <args> (priority <P>) — safety-gate check in phase 04
```

#### 1c. `mode == "interactive"`

Print the plan and wait for the user's response.

```
[iter <iter>/<max_iter>] interactive
  Next action:
    engine:   <plan.next_action.engine>
    args:     <pretty-print args>
    reason:   <plan.next_action.reason>
    priority: <plan.next_action.priority>

  Alternatives:
    1. <alt.engine> <args> — <alt.reason>
    2. ...

  Respond:
    yes               → dispatch the planned action
    pick <num>        → dispatch alternative #<num>
    no                → skip this iter; loop back to phase 01 (re-survey state)
    halt              → exit cleanly via phase 07

  >
```

If `plan.next_action.engine == null` (priority 1, 2, or 8): the verdict is the action. Print the verdict reason and ask only `yes (proceed to phase 07)` / `halt (same — exit now)`. Both branches go to phase 07; the prompt is for the user's acknowledgment.

### 2. Parse the user response (interactive only)

Accept the following responses. Case-insensitive. Whitespace-trim.

| Response | Effect |
|---|---|
| `yes` / `y` | Dispatch the planned action via phase 04. |
| `pick <n>` | If `1 ≤ n ≤ len(alternatives)`: replace `plan.next_action` with `alternatives[n-1]` and dispatch. Else: re-prompt. |
| `no` / `skip` | Append a `phase: "skipped"` line to `_run-log.jsonl` recording the skipped plan, then jump back to phase 01 (re-survey). The user's manual edits between iters will surface via the next survey. |
| `halt` / `quit` / `exit` | Jump directly to phase 07 with `verdict: "HALT"` and `reason: "user halted at interactive prompt"`. |
| Anything else | Re-prompt with the same options. Do not crash; do not interpret as a free-form answer. |

The `no / skip` path is the user's "I disagree with this plan, but I am not halting the drive" escape. It costs one iter (the iter counter in phase 06 increments anyway) and lets the user do a manual edit between iters (e.g., they re-rank their own priorities by editing state directly). Phase 06's max-iter check still applies — skipping does not give infinite tries.

### 3. Record the user's choice

For audit, append a `phase: "user-choice"` line to `_run-log.jsonl` whenever interactive mode resolves:

```jsonc
{
  "run_id":  "<run-id>",
  "engine":  "supervisor-drive",
  "phase":   "user-choice",
  "iter":    <iter>,
  "choice":  "yes | pick-<n> | no | halt",
  "planned": { "engine": "<engine>", "args": {...}, "priority": <P> },
  "dispatched": { "engine": "<engine>", "args": {...} } | null,   // null on skip / halt
  "timestamp": "<UTC ISO-8601>"
}
```

This makes the interactive transcript replayable from the run log alone — useful for community pre-test bug reports.

### 4. Hand off

- `yes` / `pick` → phase 04 with the (possibly-overridden) plan.
- `no` → phase 06 (loop-back-or-finalize; if not at max-iter, phase 06 sends back to phase 01).
- `halt` → phase 07.
- Plan-only → phase 07.
- Auto with `engine == null` → phase 06 with the propagated verdict.

## Failure modes

| Condition | Behavior |
|---|---|
| User input is empty / EOF / Ctrl-C | Treat as `halt`. Phase 07 records `reason: "user interrupted at phase 03"`. |
| `pick <n>` with `n` out of range | Re-prompt. Do not crash. |
| Plan-only and `next_action.engine == null` (priority 1, 2, 8) | Print the verdict reason and the projection (if priority 8, projection is "submission ready now"; if priority 1 or 2, projection is "drive cannot proceed until the blocker is resolved"). Jump to phase 07. |
| Auto and `next_action.engine == null` with verdict DONE (priority 8) | Phase 06 writes `submission_ready = true` and routes to phase 07. |
| Auto and `next_action.engine == null` with verdict HALT (priority 1 or 2) | Phase 06 routes to phase 07. |

## What this phase does NOT do

- Does **not** apply safety gates. Phase 04 owns that — even in `--auto`. The split is deliberate: phase 03 is mode-routing, phase 04 is dispatch-protection. A `yes` from the user in interactive mode does NOT bypass phase 04's gate check; a HypothesisChange gate fires after the `yes` if the brief trips it.
- Does **not** dispatch any engine. Always delegates to phase 04 for the dispatch path.
- Does **not** read state files. Phase 01 already did.
- Does **not** project beyond 3 actions in plan-only mode. The simulation is a heuristic; deeper projection would invite the user to over-trust it.
- Does **not** show cost projection in interactive mode. The user sees it in phase 04 (the dispatch confirmation), where the projected number is accurate to the same iter; in interactive mode they have not yet committed to the dispatch when phase 03 prompts.
- Does **not** prompt for safety-gate confirmation phrases. Phase 04 handles those; the confirmation phrase is distinct from the interactive `yes`.
