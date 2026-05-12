# Phase 4 — Engine invoke

The safety-gate-protected dispatch. Before invoking the chosen engine, run the 6 safety gates (Phase 3 spec §5). On any gate trip: require user confirmation (typed phrase, not just "yes"), and pause autonomous mode. On engine **exception** (not BLOCKED): halt the drive without retry per Phase 3 §2, write `run_error.json`, jump to phase 07.

## Inputs

From phase 03:

- `plan` — with `next_action` resolved (possibly user-picked an alternative)
- `current_picture`
- `cumulative_tokens_used`
- `budget_tokens`
- `mode` (interactive / auto)
- All carry-forward fields

## The 6 safety gates (non-negotiable)

Every gate is **confirm-required even in `--auto`** except CriticalIssue, which never accepts confirmation. The user types the named confirmation phrase to proceed (not just "yes" — making the wrong action requires a deliberate keystroke). On decline / timeout / EOF: halt via phase 07.

| # | Gate name | Trigger | Confirmation phrase |
|---|---|---|---|
| 1 | HypothesisChange | Brief or args mention modifying `paper.json.hypothesis`. | `confirm-hypothesis-change` |
| 2 | NewCitation | Engine intends to add a `references.bib` entry not in `citations.json.verified`. | `confirm-new-citation` |
| 3 | NewExperiment | Brief contains: `"design a new experiment"`, `"collect more data"`, `"run a new analysis"`, `"acquire"`. | `confirm-new-experiment` |
| 4 | StructuralRewrite | Brief contains: `"restructure"`, `"reframe"`, `"change conclusion"`, `"pivot"`, `"flip the framing"`. | `confirm-structural-rewrite` |
| 5 | BudgetExceeded | `cumulative + projected × 1.25 > budget_tokens`. | `confirm-budget` |
| 6 | CriticalIssue | A prior engine in this drive returned BLOCKED with `severity: critical`. | (no override — always halt) |

Multiple gates can trip on one dispatch. Each is checked, each must be confirmed in sequence (the user might type all four phrases if the brief hits four gates). On the first CriticalIssue trip, the drive halts regardless of any other gate's status.

## Steps

Execute in order. Skip steps if `plan.next_action.engine == null` (verdict already decided — go directly to step 8 / phase 06).

### 1. Construct the engine call

The `plan.next_action` already has `engine` (kebab-case skill name) and `args` (dict). Build:

- `engine_slash_command` — `/<engine>` literal (e.g., `/iterate-revision`).
- `task_brief` — the engine's slash-command invocation as a single string, e.g. `/iterate-revision sections/methods.tex --venue NeurIPS`. This is what the gate scanners pattern-match against.
- `dispatch_target` — for logging: the engine name + the first positional arg.

Engines accept arguments via their slash command — supervisor-drive does not need to inline persona bodies (that's the engine's job through the dispatch primitive). What this skill **invokes** is the engine itself, by reading its SKILL.md and executing the workflow it documents.

### 2. Gate 1 — HypothesisChange

Scan `task_brief` AND any deeper engine_args fields for any of:

- `paper.json.hypothesis` (literal substring)
- `change the hypothesis`, `update the hypothesis`, `revise the hypothesis`, `new hypothesis`, `replace the hypothesis`
- `paper_state.hypothesis = `

If any match: the brief is asking to mutate `paper.json.hypothesis`. Trip the gate.

Print:

```
GATE: HypothesisChange
  Engine:   <engine> <args>
  Trigger:  <quoted match from brief>

The supervisor will not silently shift the central claim. Confirm by typing
the exact phrase below (no quotes):

  confirm-hypothesis-change

Anything else → drive halts with verdict HypothesisChange-declined.
```

Wait for input. If the user types `confirm-hypothesis-change` exactly (case-sensitive, no whitespace): proceed past the gate. Anything else: halt via phase 07 with `reason: "HypothesisChange gate declined"`.

This gate is confirm-required in **every** mode including `--auto`. Autonomous mode does not silently change the hypothesis.

### 3. Gate 2 — NewCitation

Triggers when the engine's args / brief indicate adding a citation key to `references.bib`. Heuristic match:

- Engine is `respond-reviewer` AND any per-comment label was `citation`.
- Engine is `literature-sweep` (always — the entire engine adds citations). For this engine, the gate is **modified**: it fires once per drive, not once per dispatch. If the supervisor has already dispatched `/literature-sweep` once in this drive and the user confirmed, subsequent `/literature-sweep` dispatches do not re-trip the gate.
- Brief contains: `"add citation"`, `"add reference"`, `"new citekey"`, `"insert references.bib"`.

For each candidate citekey discoverable from the args (the engine's own verification — `/literature-sweep`'s phase 05 hard-gate — covers most safety here, but the supervisor gate is the engine-author-leak catch):

- If the citekey is already in `current_picture.citations.queue` with `status: "verified"` OR in `citations_state.verified[*].key`: the gate **does not trip** for that citekey.
- If the citekey is novel: trip the gate.

Print:

```
GATE: NewCitation
  Engine:   <engine> <args>
  Trigger:  <reason — "literature-sweep first dispatch in drive" or specific citekey>

OMCR will not silently add references. Confirm by typing the exact phrase:

  confirm-new-citation

Anything else → drive halts with verdict NewCitation-declined.
```

Confirm path: proceed. Decline: halt.

The literature-sweep-once-per-drive simplification keeps the gate from firing 20 times in a 20-paper sweep. The engine's internal hard verify-gate (refusing entries that fail CrossRef/OpenAlex existence check) covers the per-entry fabrication risk.

### 4. Gate 3 — NewExperiment

Scan `task_brief` for any of:

- `design a new experiment`
- `collect more data`
- `run a new analysis` (vs. "re-run" / "re-analyze" — those are pre-existing)
- `acquire` (in the brief, e.g. `acquire more subjects`)
- `record` (when combined with data-collection context — heuristic: `record N` or `record more`)
- `pilot study`
- `new dataset`

If any match: trip the gate. Confirmation phrase: `confirm-new-experiment`.

Print:

```
GATE: NewExperiment
  Engine:   <engine> <args>
  Trigger:  <quoted match>

This brief implies a real-world action (data collection, new experiment).
OMCR engines are not authorized to commit you to real-world work.
Confirm by typing:

  confirm-new-experiment

Anything else → drive halts.
```

This gate is the most paranoid — false positives are acceptable. The user pays a typing cost; the cost of a misdirected experiment is much higher.

### 5. Gate 4 — StructuralRewrite

Scan `task_brief` for any of:

- `restructure`, `re-structure`
- `reframe`, `re-frame`
- `change conclusion`
- `pivot` (as a verb — heuristic: lowercase verb followed by `the framing` / `the story` / `the narrative`)
- `flip the framing`
- `rewrite from scratch`
- `change the central claim`

If any match: trip the gate. Confirmation phrase: `confirm-structural-rewrite`.

Print:

```
GATE: StructuralRewrite
  Engine:   <engine> <args>
  Trigger:  <quoted match>

This brief implies a scope or framing change. Structural rewrites need
human ownership — the supervisor will not delegate them autonomously.
Confirm by typing:

  confirm-structural-rewrite

Anything else → drive halts.
```

### 6. Gate 5 — BudgetExceeded

Compute the projected cost for this engine:

1. Read the engine's SKILL.md frontmatter `cost_estimate_tokens` (the declared constant).
2. Scan `current_picture.recent_runs` for `phase: "end"` records where `engine == plan.next_action.engine`. Collect the most recent 5 `tokens_used` values. If `N >= 5`, compute the median.
3. `projected_cost = (median if N>=5 else declared_constant) × 1.25`.

If `cumulative_tokens_used + projected_cost > budget_tokens`: trip the gate. Confirmation phrase: `confirm-budget`.

Print:

```
GATE: BudgetExceeded
  Engine:        <engine> <args>
  Cumulative:    <cumulative_tokens_used>
  Projected:     <projected_cost> (= <basis> × 1.25; basis: <"rolling median of last 5 same-engine runs" or "declared cost_estimate_tokens">)
  Budget:        <budget_tokens>
  Overrun if proceed: <cumulative + projected - budget> tokens

Per Phase 3 §6, the supervisor pauses before known-over-budget dispatches.
Confirm by typing:

  confirm-budget

Anything else → drive halts with verdict Budget-declined.
```

Note: this gate fires **before** dispatch. It is distinct from the orchestrate `loop` primitive's post-hoc `budget_tokens` HALT (which fires at the iteration boundary after the engine ran). The supervisor pre-empts the overrun; the loop primitive caps it after the fact. Both run in parallel — the supervisor's check is the conservative early-warning.

### 7. Gate 6 — CriticalIssue

Check `current_picture.recent_runs` for any record within the current drive (`run_id` field matches) where:

- The engine returned BLOCKED.
- The verdict reason mentions `severity=critical` OR the engine wrote to `reviews.json` with at least one issue of `severity: critical`.

If any such record exists: trip the gate. **There is no confirmation phrase.** The drive halts immediately.

Print:

```
GATE: CriticalIssue (no override)
  Prior engine:  <engine> <args>
  Critical issue: <first critical issue text from reviews.json>
  Location:       <location field>

Per Phase 3 §5, the supervisor cannot proceed past a critical-severity
issue. This needs structural action (new analysis, more data, or reframing).

Halting drive. State saved.
  Full review: .claude/omcr-state/reviews.json (run_id=<R>)
```

Jump directly to phase 07 with `verdict: "BLOCKED"` and `reason: "CriticalIssue gate (no override): <issue text>"`.

This is the strictest gate — it cannot be confirmed away, even by typing. The user must address the underlying issue (manually) before the supervisor can resume.

### 8. Dispatch the engine

If all gates passed (or were confirmed):

1. Append a `phase: "dispatch-start"` line to `_run-log.jsonl`:

   ```jsonc
   {
     "run_id":          "<supervisor run_id>",
     "engine":          "supervisor-drive",
     "phase":           "dispatch-start",
     "iter":            <iter>,
     "dispatched_engine": "<plan.next_action.engine>",
     "dispatched_args":   <plan.next_action.args>,
     "projected_cost":  <projected_cost>,
     "gates_tripped":   [ "<gate name>", ... ],   // empty list if none tripped
     "started":         "<UTC ISO-8601 now>"
   }
   ```

2. Invoke the engine. Read the engine's SKILL.md and execute the workflow it documents, passing `args` as the engine's CLI arguments. This is the same as the user typing the engine's slash command — the engine runs its own phases, dispatches its own personas via the orchestrate primitives, and returns its own verdict.

3. Capture the engine's return: `{ verdict, reason, iter_count, tokens_used, run_id_engine }`. The engine has its own `run_id` (it called the orchestrate `loop` primitive); record it alongside the supervisor's `run_id` so the two run logs are joinable.

### 9. Handle the engine's return

Three cases:

#### 9a. Clean return (verdict ∈ {DONE, BLOCKED, HALT})

Append a `phase: "dispatch-end"` line:

```jsonc
{
  "run_id":            "<supervisor run_id>",
  "engine":            "supervisor-drive",
  "phase":             "dispatch-end",
  "iter":              <iter>,
  "dispatched_engine": "<engine>",
  "engine_run_id":     "<run_id_engine>",
  "engine_verdict":    "<DONE | BLOCKED | HALT>",
  "engine_reason":     "<reason>",
  "engine_iter_count": <int>,
  "tokens_used_this_dispatch": <int>,
  "ended":             "<UTC ISO-8601 now>"
}
```

Update the running tally: `cumulative_tokens_used += tokens_used_this_dispatch`.

Hand off to phase 05 (checkpoint).

#### 9b. Engine exception (Phase 3 §2 — halt-on-exception)

If the engine threw any error (not a BLOCKED verdict — actual exception: missing file, parse error, tool failure, network drop, malformed state):

1. Write `.claude/omcr-state/run_error.json` (atomic write — tmp + rename):

   ```jsonc
   {
     "schema_version":    "1",
     "supervisor_run_id": "<supervisor run_id>",
     "engine":            "<dispatched engine name>",
     "args":              <plan.next_action.args>,
     "iter":              <iter>,
     "exception_type":    "<error class or category>",
     "exception_text":    "<full error message + stack trace summary>",
     "occurred_at":       "<UTC ISO-8601 now>",
     "cumulative_tokens": <cumulative_tokens_used at exception time>
   }
   ```

2. Append a `phase: "dispatch-error"` line to `_run-log.jsonl`:

   ```jsonc
   {
     "run_id":            "<supervisor run_id>",
     "engine":            "supervisor-drive",
     "phase":             "dispatch-error",
     "iter":              <iter>,
     "dispatched_engine": "<engine>",
     "exception_type":    "<type>",
     "exception_excerpt": "<first 200 chars of exception_text>",
     "error_file":        ".claude/omcr-state/run_error.json",
     "occurred_at":       "<UTC ISO-8601 now>"
   }
   ```

3. **Skip phase 05** (checkpoint). There is nothing meaningful to commit on a partial dispatch — the engine may have left state in an inconsistent shape. Phase 07 will surface the error to the user and instruct them to inspect.

4. Jump directly to phase 07 with `verdict: "BLOCKED"`, `reason: "engine exception: <type>"`.

No retry. No fallback engine. No "try a different target." Per Phase 3 §2 (locked).

#### 9c. `plan.next_action.engine == null` (verdict already decided)

This is the priority 1, 2, or 8 case from phase 02. The "dispatch" is the supervisor itself writing state:

- Priority 8 (DONE): the supervisor reads `paper_state` directly (via the state-read primitive), sets `submission_ready = true`, writes back atomically. Log `phase: "submission-ready-set"` to `_run-log.jsonl`.
- Priority 1 / 2 (HALT): no state mutation. Just log the planned halt.

Then jump to phase 06 (which routes to phase 07 since verdict ∈ {DONE, HALT}).

### 10. Hand off

- Clean dispatch → phase 05 (checkpoint).
- Exception → phase 07 (skip 05).
- Null engine with verdict → phase 06 (which routes to 07).

## Failure modes

| Condition | Behavior |
|---|---|
| Any gate's confirmation phrase fails (typo, empty, EOF) | Halt via phase 07 with `reason: "<gate> gate declined"`. |
| CriticalIssue gate trips | Always halt. No override. |
| Engine exception during dispatch | Write `run_error.json`, log `phase: "dispatch-error"`, jump to phase 07 (skip phase 05). |
| Engine returns a verdict not in `{DONE, BLOCKED, HALT}` (e.g. `CONTINUE`) | Treat as exception. `CONTINUE` is an engine-internal mid-loop signal and should never escape; if it does, the engine has a bug. Write `run_error.json` with `exception_type: "engine-bug-continue-escaped"`. |
| `_run-log.jsonl` append fails mid-dispatch | Bubble the OS error and halt via phase 07. Without a log trail the drive is unsafe to continue. |
| Multiple gates trip on one dispatch | Confirm them in order (1 → 6). Any decline halts immediately. CriticalIssue (gate 6) is checked first if its trigger fires regardless of other gates' state. |

## What this phase does NOT do

- Does **not** retry on exception. Halt-on-exception, no retry (Phase 3 §2).
- Does **not** dispatch a different engine if the chosen one fails. No fallback engine.
- Does **not** bypass any gate based on mode. Every gate is confirm-required even in `--auto`.
- Does **not** commit to git. Phase 05 owns commits.
- Does **not** read state files directly except for the priority-8 `submission_ready` write. Phase 01 reads; phase 04 dispatches.
- Does **not** modify the gate trigger keyword lists at runtime. Adding gates / triggers is a v0.5+ refinement; v0.4 lists are locked above.
- Does **not** time-out user confirmation in `--auto`. If the user walks away from the terminal during a safety-gate prompt, the drive simply waits. This is the right tradeoff: a misclick on a 30-second timeout could ship a fabricated citation.
