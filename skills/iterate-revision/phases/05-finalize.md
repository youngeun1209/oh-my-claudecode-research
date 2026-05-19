# Phase 5 — Finalize

User-facing summary after the loop exits. Pulls the loop primitive's return value and renders it as a few lines the user can read in the Codex transcript. Appends one summary line to `_run-log.jsonl` (in addition to the start + end records the orchestrate loop primitive already wrote). No git commit, no push — those stay out by default.

## Inputs (from the loop primitive)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | loop primitive | UUID for the run; ties this summary to the `_run-log.jsonl` records. |
| `verdict` | loop primitive | `DONE | CONTINUE | BLOCKED | HALT`. The loop never returns `CONTINUE` at this point — `CONTINUE` is a mid-loop signal, not a final state. If it ever appears here, treat it as a bug and surface it as HALT with reason `"engine bug: CONTINUE returned to phase 05"`. |
| `reason` | loop primitive | Engine-specific string from phase 04 step 2. |
| `iter_count` | loop primitive | Total iterations that ran. |
| `tokens_used` | loop primitive | Cumulative token usage across the run (post-hoc per Phase 0 decision §6). |
| `iter_outputs` | loop primitive | List of per-iter dispatch result lists; phase 05 reads the **final** iter's issues count for the summary. |
| `started` / `ended` | loop primitive | Run start + end UTC ISO-8601 timestamps. |

Phase 05 also has access to the carried-forward `section_name`, `section_path`, `venue`, `max_iter`, and the latest `paper_state` (so it knows the final `status` that phase 04 wrote).

## Step 1 — Tally final-iter issues

From `iter_outputs[-1]` — the final iter's reviewer output — pull the `issues` list. Count by severity:

```
crit = #critical
maj  = #major
min  = #minor
nit  = #nit
```

If `iter_outputs` is empty (e.g., the loop aborted before completing iter 1), use zeros and add `(no iters completed)` to the issue-count line.

## Step 2 — Compute duration

`duration_sec = ended - started` in whole seconds. Format as:
- `< 60s` → `"<N>s"`
- `< 3600s` → `"<Nm <S>s"` (e.g., `2m 34s`)
- otherwise → `"<H>h <M>m"` (e.g., `1h 04m`)

## Step 3 — Render the user summary

Print this block to the transcript. The shape is the same for every verdict; only the trailing block varies.

```
Section:     <section_path>
Verdict:     <verdict>
Iterations:  <iter_count> / <max_iter>
Issues (final iter): <crit> critical, <maj> major, <min> minor, <nit> nit
Duration:    <formatted duration>
Tokens:      <tokens_used> (post-hoc; see _run-log.jsonl for per-iter detail)
Run id:      <run_id>

Reason: <reason from phase 04 / loop>
```

Then append one of these verdict-specific blocks:

### DONE

```
Section approved. paper.json: sections[<section_name>].status = "approved".

Suggested next:
  $iterate-revision <next unwritten or revising section>
  $todofig                       (check figure-vs-outline gap)
  $sync                          (snapshot project state)
```

The "next unwritten or revising section" hint should be filled in from `paper_state.sections` — pick the first key (in `sections` definition order) whose `status` is in `{empty, drafted, revising, blocked, blocked-on-tbd}`. If none exists, suggest `$sync` instead.

### BLOCKED

```
Section blocked. paper.json: sections[<section_name>].status = "blocked".

Critical issue (verbatim from the reviewer):
  <first critical issue's text, full — no truncation here>
  Location: <first critical issue's location>

This needs human action — new analysis, new data, or a framing decision.
The reviewer flagged it as structural; another writer iter will not resolve it.

Full review: .omx/state/omxr/reviews.json (run_id=<run_id>)
After addressing, re-run:
  $iterate-revision <section_path>
```

If there are multiple critical issues, list all of them (one per bullet line), then the "full review" hint.

### HALT

```
Iterations exhausted. paper.json: sections[<section_name>].status = "revising".

<maj> major issue(s) remain after <iter_count> iter — see reviews.json for the list.
The section made progress (each iter cleared some issues); the budget ran out.

Options:
  $iterate-revision <section_path> --max-iter <iter_count + 2>
                                  (bump the cap and continue)
  Address remaining issues by hand, then re-run $iterate-revision.

Full review: .omx/state/omxr/reviews.json (run_id=<run_id>)
```

### Fallthrough — `CONTINUE` (should not happen)

If phase 05 sees `verdict == CONTINUE`, render:
```
Engine bug: loop returned CONTINUE to phase 05. Treating as HALT.
Please file an issue against oh-my-codex-research with the run_id above.
```

Then fall through to the HALT block.

## Step 4 — Append a summary line to `_run-log.jsonl`

The orchestrate loop primitive already wrote a `phase: "start"` line and a `phase: "end"` line for this run. Phase 05 adds one more line, `phase: "summary"`, so a JSONL reader can grep `phase == "summary"` to get per-run user-facing summaries without parsing the full transcript.

Append (atomic append, never overwrite):

```jsonc
{
  "run_id":         "<run_id>",
  "engine":         "iterate-revision",
  "phase":          "summary",
  "section":        "<section_name>",
  "section_path":   "<section_path>",
  "venue":          "<venue>",
  "verdict":        "<verdict>",
  "reason":         "<reason>",
  "iter_count":     <iter_count>,
  "max_iter":       <max_iter>,
  "final_issues":   { "critical": <crit>, "major": <maj>, "minor": <min>, "nit": <nit> },
  "duration_sec":   <int>,
  "tokens_used":    <int>,
  "summary_at":     "<UTC ISO-8601 now>"
}
```

Use the same write semantics as the loop primitive's append:
- Open the file in append mode.
- Write one line of JSON followed by `\n`.
- `flush` + `fsync` if available.

If the append fails (disk full, permission denied), do **not** abort — the user has already seen the summary in the transcript. Log a warning:
```
iterate-revision: failed to append summary to _run-log.jsonl (<error>). Run output
above is the canonical record of this run; reviews.json + paper.json are durable.
```

## Step 5 — No git commit

OMXR does **not** commit on behalf of the user from this phase. If `on_iter_end == "git-commit"` was set on the loop primitive (currently never set by this engine), the loop already committed per-iter; phase 05 still does nothing.

Future versions may add a `--commit` flag that triggers a single final commit here with a message like `omxr: iterate-revision <section_name> <verdict> (<iter_count> iter)`. That is a future-version concern.

## Failure modes

| Condition | Behavior |
|---|---|
| `iter_outputs` empty or malformed | Use zeros in the issue tally; surface `(no iters completed)`. Continue rendering. |
| Phase 04 didn't write `paper.json.sections[name].status` | The summary's status reference is informational only; if state and summary disagree, the user reading the summary should trust `paper.json` on disk. |
| `_run-log.jsonl` append fails | Log a warning; do not abort. |
| First critical issue's `text` empty (malformed reviewer output that still parsed) | Render `"(no description)"` and append `Location: <location>` only. |

## What this phase does NOT do

- Does **not** invoke any subagent.
- Does **not** mutate `paper.json` or `reviews.json`. Phase 04 already did the durable writes.
- Does **not** commit to git by default.
- Does **not** push to Overleaf. Manuscript-scaffold owns push flows; iterate-revision is loop-internal.
- Does **not** retry on log-append failure.
- Does **not** decide DONE vs HALT. Phase 04 already did.
