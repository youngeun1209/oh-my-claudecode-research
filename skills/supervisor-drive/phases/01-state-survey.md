# Phase 1 — State survey

Read all 5 OMXR state files and build a `current_picture` dict that phase 02 (action-plan) consumes. This phase runs at the **start of every iteration**, not just at drive entry — the engines-are-leaves invariant (Phase 3 §3) requires re-reading state from scratch between every step.

## Inputs

From phase 00 (drive entry) or phase 06 (loop-back):

- `run_id` — UUID for this drive
- `mode` — interactive / auto / plan-only
- `iter` — current iter number (1 at drive entry, incremented by phase 06)
- `max_iter` — cap
- `cumulative_tokens_used` — running tally
- All other carry-forward fields from phase 00

## Steps

### 1. Read each of the 5 state files

Call [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) once per name. Each call bootstraps the file if missing — supervisor-drive may run before `$omxr-setup` has fully initialized state, and bootstrap is safe (Phase 0 §1).

- `state-read(paper)` → `paper_state`
- `state-read(reviews)` → `reviews_state`
- `state-read(citations)` → `citations_state`
- `state-read(figures)` → `figures_state`
- `state-read(rebuttals)` → `rebuttals_state`

If any read aborts with a parse error: propagate the abort. The drive cannot proceed with corrupted state. Phase 07 will be reached via the standard halt path.

### 2. Read `_run-log.jsonl` recent history

Open `.omx/state/omxr/_run-log.jsonl` and scan from the end. Build a `recent_runs` list of the last 20 records (or all if fewer), parsed as dicts. Skip malformed lines with a warning.

This list feeds:

- The cost-projection rolling-median calculation (phase 04 reads it).
- The prior-run trail in `current_picture` (phase 02 uses it to detect "we already tried this engine on this target and got BLOCKED").
- The phase 07 report.

### 3. Scan manuscript files for `[CITE: ...]` placeholders

For each `path` in `paper_state.sections[*]` whose file exists on disk, read it and count occurrences of the literal regex `\[CITE:\s*[^\]]+\]`. Record per-section counts.

This is the priority-3 trigger half — combined with `citations_state.queue` pending entries, it tells the ranker whether a `$literature-sweep` is overdue.

### 4. Build the `current_picture` dict

The structured snapshot phase 02 consumes:

```jsonc
{
  "iter":            <iter>,
  "run_id":          "<run-id>",
  "mode":            "<mode>",
  "paper": {
    "title":            "<paper_state.title or null>",
    "venue":            "<paper_state.venue or null>",
    "hypothesis":       "<paper_state.hypothesis or null>",
    "manuscript_root":  "<paper_state.manuscript_root>",
    "submission_ready": <bool>,
    "sections_by_status": {
      "approved":       [ "<name>", ... ],
      "drafted":        [ "<name>", ... ],
      "revising":       [ "<name>", ... ],
      "empty":          [ "<name>", ... ],
      "blocked":        [ "<name>", ... ],
      "blocked-on-tbd": [ "<name>", ... ]
    },
    "sections_detail": {
      "<name>": {
        "path":    "<path>",
        "status":  "<status>",
        "iter":    <int>,
        "outline": "<outline or null>",
        "cite_placeholder_count": <int>
      },
      ...
    }
  },
  "reviews": {
    "total_runs":            <int>,
    "last_run_id":           "<id or null>",
    "last_verdict":          "<verdict or null>",
    "last_section":          "<name or null>",
    "critical_open":         [ "<section name>", ... ]  // sections whose most recent review had critical issues
  },
  "citations": {
    "queue_pending":         <int>,        // count of citations_state.queue entries with status: pending
    "queue_verified":        <int>,
    "verified_total":        <int>,        // len(citations_state.verified)
    "last_sweep_topic":      "<str or null>",
    "last_sweep_at":         "<timestamp or null>",
    "cite_placeholder_total": <int>        // sum across all sections from step 3
  },
  "figures": {
    "all_done":              <bool>,       // every entry has brief_status=approved + impl_status=approved + critique_status=done
    "diverged":              [ "<fig-id>", ... ],   // entries where brief_status=approved but impl_status!=approved
    "blocked":               [ "<fig-id>", ... ],   // entries where the latest critique returned BLOCKED
    "missing":               [ "<fig-id>", ... ],   // entries with brief_status=missing
    "total":                 <int>
  },
  "rebuttals": {
    "unresolved":            [ "<letter-path>", ... ],   // rebuttals entries with verdict=HALT or any per-comment verdict in {deferred, disputed}
    "addressed":             <int>,
    "total":                 <int>,
    "user_attention_total":  <int>          // sum of user_attention_count across all entries
  },
  "prior_trail": {
    "last_engine":       "<engine name or null>",      // from last phase: "end" record in recent_runs
    "last_target":       "<args summary or null>",
    "last_verdict":      "<verdict or null>",
    "consecutive_blocked": <int>                       // run-length of trailing BLOCKED/HALT records on the same target
  },
  "recent_runs":       [ <up-to-20 parsed records> ]
}
```

The shape is deliberately verbose — phase 02's priority rules are easier to write when the survey has already done the bookkeeping.

### 5. Emit a structured summary

Print a short human-readable summary to the transcript (the user sees this every iter):

```
[iter <iter>/<max_iter>] survey
  paper:      <approved>/<total> sections approved, <drafted> drafted, <empty> empty<, N blocked>
  citations:  <verified_total> verified, <queue_pending> pending<, M [CITE:] placeholders in manuscript>
  figures:    <done>/<total> done<, K diverged>
  rebuttals:  <addressed>/<total> addressed<, U pending user attention>
  prior:      iter <iter-1> ran <last_engine> on <last_target> → <last_verdict>
```

Sections in parentheses are conditionally shown (e.g., the `, N blocked` only if `N > 0`).

If `submission_ready == true` and all categories are at their terminal counts, just print:

```
[iter <iter>/<max_iter>] survey: submission_ready=true. Handing off to phase 02 (will EXIT DONE).
```

### 6. Hand off to phase 02

Pass forward `current_picture` + all carry-forward fields from phase 00. Phase 02 owns the priority application — phase 01 is read-only.

## Failure modes

| Condition | Behavior |
|---|---|
| Any state-read aborts | Propagate the abort. Drive halts via phase 07 standard path. |
| `_run-log.jsonl` malformed lines | Skip each one with a warning. |
| Section `path` references a missing file | Record `cite_placeholder_count: 0` for that section and continue. Phase 02 may pick `$iterate-revision` which will fail the same precheck; that is the correct failure surface. |
| Outline file missing for an `empty` section that has `outline: null` | Record `outline: null` (the file-existence check happens in phase 02 when deciding outline-expand vs iterate-revision). |

## What this phase does NOT do

- Does **not** mutate any state file. Read-only.
- Does **not** apply priority rules. Phase 02 does that.
- Does **not** dispatch any engine.
- Does **not** check `submission_ready` itself — it surfaces the value to phase 02 which decides DONE.
- Does **not** trim `recent_runs` below 20 records — phase 04's rolling-median cost calculation may need more, and the cost is one read per iter (cheap).
- Does **not** detect engine-calls-engine violations. There are none by construction (engines are leaves); phase 01 does not need to verify.
