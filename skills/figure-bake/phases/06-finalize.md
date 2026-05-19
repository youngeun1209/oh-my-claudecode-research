---
name: figure-bake-finalize
description: Phase 6 of $figure-bake. Render the user-facing run summary, suggest an embedding follow-up (typically $sync), and append a phase:"summary" line to _run-log.jsonl. No git commit, no push.
---

# Phase 6 — Finalize

User-facing summary after the loop exits. Pulls the loop primitive's return value plus the latest `figures.json.figures[<fig-id>]` state, renders a readable block to the Codex transcript, and appends one summary line to `_run-log.jsonl` (in addition to the start + end records the orchestrate loop primitive already wrote). No git commit, no push — those stay out by default.

This phase mirrors `$iterate-revision/phases/05-finalize.md` in structure; the only differences are the state file (`figures.json` here vs. `paper.json + reviews.json` there) and the "suggested next" hints (figure-flavored, not section-flavored).

## Inputs (from the loop primitive)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | loop primitive | UUID for the run; ties this summary to the `_run-log.jsonl` records. |
| `verdict` | loop primitive | `DONE | CONTINUE | BLOCKED | HALT`. The loop never returns `CONTINUE` at this point — `CONTINUE` is a mid-loop signal. If it appears here, treat as a bug and render as HALT with reason `"engine bug: CONTINUE returned to phase 06"`. |
| `reason` | loop primitive | Engine-specific string from phase 05 step 2. |
| `iter_count` | loop primitive | Total iterations that ran. |
| `tokens_used` | loop primitive | Cumulative token usage across the run (post-hoc per Phase 0 decision §6). |
| `iter_outputs` | loop primitive | List of per-iter dispatch result lists. Phase 06 reads the final iter's reviewer output for the issue tally. |
| `started` / `ended` | loop primitive | Run start + end UTC ISO-8601 timestamps. |

Phase 06 also has access to the carried-forward `fig_id`, `max_iter`, `data_root`, and the latest `figures_state` (so it knows the final per-figure status fields phase 05 wrote).

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

## Step 3 — Pull artifact paths from the final state

Re-read `figures.json` via [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) (cheap; gives phase 06 the canonical post-phase-05 state). Pull:

- `entry.vector_path` — the implementer's raw PDF (uncropped).
- `entry.cropped_pdf_path` — set by phase 03 if cropfig succeeded; else null.
- `entry.cropped_png_path` — set by phase 03 if cropfig succeeded; else null.
- `entry.script_path` — implementer's renderer script path.
- `entry.brief_status`, `entry.impl_status`, `entry.critique_status`, `entry.iter`.
- `entry.title` — short label set by phase 02.

## Step 4 — Render the user summary

Print this block to the transcript. The shape is the same for every verdict; only the trailing block varies.

```
Figure:      <fig_id>  (title: <entry.title or "(untitled)">)
Verdict:     <verdict>
Iterations:  <iter_count> / <max_iter>
Issues (final iter): <crit> critical, <maj> major, <min> minor, <nit> nit
Duration:    <formatted duration>
Tokens:      <tokens_used> (post-hoc; see _run-log.jsonl for per-iter detail)
Run id:      <run_id>

Artifacts:
  Renderer:        <entry.script_path or "(not recorded)">
  Vector PDF:      <entry.vector_path>
  Cropped PDF:     <entry.cropped_pdf_path or "(cropfig did not run / failed)">
  Outline PNG:     <entry.cropped_png_path or "(cropfig did not run / failed)">

Reason: <reason from phase 05 / loop>
```

Then append one of these verdict-specific blocks:

### DONE

```
Figure approved. figures.json: figures[<fig_id>] all-approved.

Suggested next:
  $sync                          (embed the figure into the outline + commit a snapshot)
  $figure-bake <next fig-id>     (bake another figure)
  $iterate-revision <relevant section>
                                 (now that the figure is settled, iterate on the
                                  Results / Methods section it appears in)
```

The `$sync` hint is the manuscript-embedding follow-up — `$sync` uses cropfig func 3 internally, which is idempotent against the outline.md image-link block, so re-running it after each figure converges naturally. If `entry.cropped_png_path` is null (cropfig failed), surface a one-liner reminding the user to re-run `$figure-bake <fig_id>` (or fix the cropfig issue manually) before `$sync` will have a PNG to embed.

### BLOCKED

```
Figure blocked. figures.json: figures[<fig_id>].critique_status = "done",
impl_status = "<from entry>", brief_status = "<from entry>".

Critical issue (verbatim from the reviewer):
  <first critical issue's text, full — no truncation here>
  Location: <first critical issue's location>

<if the first critical's location starts with "brief:">
The reviewer flagged this as a brief-level problem. brief_status has been set back
to "drafted"; the next $figure-bake <fig_id> run will re-dispatch @figure-descriptor
to revise the design before the implementer renders again.
<else>
The reviewer flagged this at the rendering level. The next $figure-bake <fig_id> run
will reuse the approved brief; @analysis-implementer needs to fix the render to
address the critical issue.
</if>

Full critique trail: .omx/state/omxr/figures.json (figures[<fig_id>].critiques)
After addressing, re-run:
  $figure-bake <fig_id>
```

If there are multiple critical issues, list all of them (one per bullet line) before the "After addressing" hint.

### HALT

```
Iterations exhausted. figures.json: figures[<fig_id>].critique_status = "done",
impl_status = "drafted", brief_status = "<unchanged>".

<maj> major issue(s) remain after <iter_count> iter — see figures.json for the
full critique trail. The figure made progress (each iter cleared some issues); the
budget ran out.

Options:
  $figure-bake <fig_id> --max-iter <iter_count + 2>
                                  (bump the cap and continue — note each iter is
                                  expensive because it re-runs the implementer)
  Address the remaining major issues by hand-editing the renderer at
  <entry.script_path>, then re-run $figure-bake <fig_id>.

Full critique trail: .omx/state/omxr/figures.json (figures[<fig_id>].critiques)
```

### Fallthrough — `CONTINUE` (should not happen)

If phase 06 sees `verdict == CONTINUE`, render:
```
Engine bug: loop returned CONTINUE to phase 06. Treating as HALT.
Please file an issue against oh-my-codex-research with the run_id above.
```

Then fall through to the HALT block.

## Step 5 — Append a summary line to `_run-log.jsonl`

The orchestrate loop primitive already wrote a `phase: "start"` line and a `phase: "end"` line for this run. Phase 06 adds one more line, `phase: "summary"`, so a JSONL reader can grep `phase == "summary"` to get per-run user-facing summaries without parsing the full transcript.

Append (atomic append, never overwrite):

```jsonc
{
  "run_id":          "<run_id>",
  "engine":          "figure-bake",
  "phase":           "summary",
  "fig_id":          "<fig_id>",
  "title":           "<entry.title or null>",
  "verdict":         "<verdict>",
  "reason":          "<reason>",
  "iter_count":      <iter_count>,
  "max_iter":        <max_iter>,
  "final_issues":    { "critical": <crit>, "major": <maj>, "minor": <min>, "nit": <nit> },
  "vector_path":     "<entry.vector_path>",
  "cropped_pdf_path": "<entry.cropped_pdf_path or null>",
  "cropped_png_path": "<entry.cropped_png_path or null>",
  "script_path":     "<entry.script_path or null>",
  "data_root":       "<data_root from phase 01>",
  "duration_sec":    <int>,
  "tokens_used":     <int>,
  "summary_at":      "<UTC ISO-8601 now>"
}
```

Use the same write semantics as the loop primitive's append:
- Open the file in append mode.
- Write one line of JSON followed by `\n`.
- `flush` + `fsync` if available.

If the append fails (disk full, permission denied), do **not** abort — the user has already seen the summary in the transcript. Log a warning:
```
figure-bake: failed to append summary to _run-log.jsonl (<error>). Run output above
is the canonical record of this run; figures.json is durable.
```

## Step 6 — No git commit, no push

OMXR does **not** commit on behalf of the user from this phase. If `on_iter_end == "git-commit"` was set on the loop primitive (currently never set by this engine), the loop already committed per-iter; phase 06 still does nothing extra.

Embedding the figure into the manuscript is the user's call — phase 06's DONE block suggests `$sync`, which uses `cropfig` func 3 to insert `![Figure N](figures/<fig_id>.png)` links into the outline at each result heading. That side-effect-bearing step deserves user confirmation, not automation here.

Future versions may add a `--commit` flag that triggers a single final commit here with a message like `omxr: figure-bake <fig_id> <verdict> (<iter_count> iter)`. That is a future-version concern.

## Failure modes

| Condition | Behavior |
|---|---|
| `iter_outputs` empty or malformed | Use zeros in the issue tally; surface `(no iters completed)`. Continue rendering. |
| Phase 05 didn't write `figures.json.figures[<fig-id>]` status fields | The summary's status reference is informational only; if state and summary disagree, the user reading the summary should trust `figures.json` on disk. |
| `figures.json` re-read in step 3 fails | Render the summary with whatever the in-memory `figures_state` had at hand-off from phase 05. Log a warning. |
| `_run-log.jsonl` append fails | Log a warning; do not abort. |
| `entry.cropped_png_path` null AND verdict is DONE | Render the DONE block with the cropfig-failed hint about re-running before `$sync`. |
| First critical issue's `text` empty (malformed reviewer output that still parsed) | Render `"(no description)"` and append `Location: <location>` only. |

## What this phase does NOT do

- Does **not** invoke any subagent.
- Does **not** mutate `figures.json`. Phase 05 already did the durable writes.
- Does **not** commit to git by default.
- Does **not** push to Overleaf. Manuscript-scaffold owns push flows; figure-bake is loop-internal.
- Does **not** auto-invoke `$sync` to embed the figure. The DONE block *suggests* it; the user runs it explicitly.
- Does **not** auto-invoke `cropfig` again. Phase 03 already did. If `cropfig_status` was `failed`, the DONE block surfaces it and the user re-runs the engine (or the cropfig skill directly) to retry.
- Does **not** retry on log-append failure.
- Does **not** decide DONE vs HALT. Phase 05 already did.
- Does **not** invoke any other skill. Even the "Suggested next" hints are text, not auto-dispatched (Phase 2 decision §5).
