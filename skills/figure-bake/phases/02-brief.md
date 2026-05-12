---
name: figure-bake-brief
description: Phase 2 of /figure-bake. Dispatch @figure-descriptor to produce (or reuse) an implementation-ready design brief for this fig-id. Updates figures.json.figures[<fig-id>].brief + brief_status.
---

# Phase 2 — Brief

Invoke `@figure-descriptor` to produce a complete, unambiguous design brief for the figure: panel structure, color encoding, axes, layout, caption. This brief is **implementation-ready** — phase 03 hands it directly to `@analysis-implementer` and expects the implementer to be able to render code without further clarification.

This phase runs at most once per loop iteration. On iter 1 it always dispatches. On iter 2+ it may reuse the brief from iter 1, depending on the per-figure `brief_status` flag (which phase 05 may have flipped back to `"drafted"` if the previous reviewer flagged a brief-level concern).

## Inputs (from phase 01 or the loop)

| Name | Source | Purpose |
|---|---|---|
| `fig_id` | phase 01 | Key in `figures.json.figures`. |
| `figures_state` | phase 01 | Parsed dict; `figures[fig_id]` is the entry this phase mutates. |
| `paper_state.title` | phase 01 | Pass-through to the descriptor brief. |
| `paper_state.manuscript_root` | phase 01 | Context for the descriptor (so it can reference cross-figure consistency). |
| `data_root` | phase 01 | Pass-through (descriptor does not read data, but it influences what's plausible to ask of phase 03). |
| `current_iter` | loop primitive | 0 for the very first brief; incremented by the loop. |
| `max_iter` | phase 01 | Surfaced to the descriptor brief so it knows the budget. |

## Step 1 — Decide whether to dispatch this iter

Read the current `entry = figures_state.figures[fig_id]`. Apply this decision table:

| `current_iter` | `entry.brief_status` | `entry.brief` content | Action |
|---|---|---|---|
| 0 | any | any | **Dispatch.** First-iter always produces a fresh brief. |
| ≥ 1 | `"approved"` | non-empty string | **Skip dispatch.** Reuse `entry.brief` verbatim. Pass it forward to phase 03 as-is. |
| ≥ 1 | `"drafted"` | non-empty string | **Dispatch.** The previous reviewer flagged a brief-level concern (phase 05 set this); re-run the descriptor with the previous brief + the previous reviewer issues as context. |
| ≥ 1 | `"missing"` | null | **Dispatch.** Shouldn't normally happen (phase 02 always sets at least `"drafted"` on success), but treat as iter-1 — descriptor produces a fresh brief. |

When the action is `Skip dispatch`, jump to step 5 (hand off). The dispatch is the expensive step — skipping it on iter 2+ when the brief was approved is the whole reason we track `brief_status`.

## Step 2 — Build the descriptor task brief

Build the `task_brief` for `@figure-descriptor` with this shape (substitute the angle-bracketed variables):

```
Design figure "<fig_id>" for "<paper_state.title or 'untitled manuscript'>".

Current state:
  brief_status: <entry.brief_status>
  impl_status:  <entry.impl_status>
  iter:         <current_iter> of <max_iter>
  vector_path:  <entry.vector_path>     <-- the implementer will write the PDF here
  data_root:    <data_root>             <-- the implementer reads inputs from here

<if entry.brief is non-null:>
Previous brief (from iter <current_iter - 1>):
  <entry.brief>

<if the previous iter's reviewer flagged brief-level concerns — from entry.critiques[-1] when present:>
Previous reviewer concerns that target THIS brief, not just the rendering:
  <bulleted list of issues from entry.critiques[-1] with location starting with "brief:" or
   severity == "critical">

Produce an UPDATED brief that addresses these concerns. Preserve any design choices the
reviewer did not flag.

<else, first iter:>
This is iter 1. No prior brief or reviewer feedback exists. Produce a fresh brief.

Output requirements:

Your brief must be implementation-ready. The analysis-implementer agent will hand
your brief to a fresh dispatch and expect to produce working Python/matplotlib (or
equivalent) code without further clarification from you.

Cover, at minimum, all of these:
  1. Title — one-sentence finding the figure shows ("This figure shows that …").
  2. Panel structure — for each panel: data shown, plot type, axes with units, color
     encoding, N, statistical annotations. Number panels (a), (b), (c) …
  3. Layout — grid position of each panel, relative sizing, reading order.
  4. Visual system — color hex codes (colorblind-safe), font sizes, line weights,
     figure dimensions in mm matching the target venue's column width.
  5. Caption — bold title (a finding, not a label), per-panel descriptions, error-bar
     convention, significance thresholds, abbreviations.
  6. Data requirements — for each panel, name the input files / columns the
     implementer must read from <data_root>. Be specific: "panel (a) plots
     `subject_id, accuracy, condition` from data_root/behavior_summary.csv".
  7. Dependencies — Python libraries the implementer should use (matplotlib,
     seaborn, pandas, numpy, …). Flag any non-standard library.

Output: a single markdown document with the seven sections above, in that order. No
preamble, no commentary. Begin with the title section.
```

The `Previous brief` and `Previous reviewer concerns` blocks are omitted when there are no prior runs — on iter 1 the brief is built fresh from the seven requirement sections only.

## Step 3 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":     "figure-descriptor",
  "task_brief":  <the brief built in step 2>,
  "state_slice": {
    "fig_id":          <fig_id>,
    "title":           <paper_state.title>,
    "manuscript_root": <paper_state.manuscript_root>,
    "iter":            <current_iter>,
    "max_iter":        <max_iter>,
    "vector_path":     <entry.vector_path>,
    "data_root":       <data_root>,
    "previous_brief":  <entry.brief or null>,
    "previous_critiques_iter_n": <entry.critiques[-1] if present, else null>
  },
  "expected_output_schema": null
}
```

`expected_output_schema` is `null` — the descriptor returns a markdown document, not JSON. Phase 04 (reviewer) is where structured output matters.

The dispatch returns:
```jsonc
{
  "output":    "<the descriptor's markdown brief>",
  "persona":   "figure-descriptor",
  "timestamp": "..."
}
```

## Step 4 — Normalize and persist the brief

Apply in order:

1. **Empty-output guard.** If `output` is empty or whitespace-only:
   - Do **not** overwrite `entry.brief` (preserve any prior brief).
   - Set `entry.brief_status = "missing"`.
   - Persist `figures.json` atomically.
   - Hand off to phase 03 with a flag indicating the descriptor produced nothing. Phase 03 will surface this as BLOCKED.
   - Stop here.

2. **Length sanity-check.** Briefs shorter than ~400 chars are almost certainly truncated. If the output is shorter than 400 chars, log a warning to the run log but proceed:
   ```
   figure-bake brief: descriptor returned <N> chars — unusually short.
   Phase 03 may fail to produce code from it. Proceeding anyway.
   ```

3. **Title extraction.** If the descriptor's output starts with a `# `, `## Title`, or similar one-line title marker, extract the next non-empty text line as the figure's short title. Store into `entry.title`. If no title line is identifiable, leave `entry.title` at its current value (which may still be `null` from phase 01).

4. **Write back.** Set:
   - `entry.brief = <output>` (the full markdown document)
   - `entry.brief_status = "drafted"` (always — phase 05 may flip it to `"approved"` later)

   Persist `figures.json` atomically (tmp + rename) per the orchestrate state-read primitive convention.

The descriptor's brief is **not** written to a separate file on disk. It lives inside `figures.json.figures[<fig-id>].brief` as a string. This keeps the state self-contained and avoids drift between the in-state brief and an on-disk copy.

## Step 5 — Hand off to phase 03

Pass forward to phase 03:

- `fig_id`
- `figures_state` (with the updated entry)
- `paper_state` (unchanged)
- `data_root`, `code_dir`, `vector_path` (unchanged from phase 01)
- `current_iter`, `max_iter`
- `brief_text` — the full string the implementer will receive. This is either:
  - the freshly-dispatched output from step 4, or
  - the previously-approved brief from `entry.brief` if step 1 chose "Skip dispatch".
- `brief_dispatched` (bool) — `true` if step 3 ran, `false` if step 1 short-circuited. Phase 03 uses this for run-log attribution; the loop primitive uses it to count dispatches against `budget_tokens`.
- `dispatch_meta` — timestamp + any empty-output flag from step 4. `null` if `brief_dispatched` is false.

## Failure modes

| Condition | Behavior |
|---|---|
| Descriptor dispatch errors out | Loop primitive catches in its step 3b (loop primitive) and emits BLOCKED. The `entry.brief_status` is left at its prior value; the previous brief is preserved. |
| Descriptor returns empty output | Step 4 case 1 — preserve prior brief, set `brief_status = "missing"`, flag phase 03 to BLOCKED. |
| Descriptor returns malformed output that lacks the seven required sections | Not detected here — phase 03 (implementer) will struggle and likely produce a render failure, which phase 04 (reviewer) will flag as `critical` (brief insufficient). The loop's natural feedback cycle handles this. |
| `figures.json` write fails | Bubble the OS error; loop primitive emits BLOCKED. The prior on-disk brief is unchanged because the write was atomic. |

## What this phase does NOT do

- Does **not** generate images. The descriptor designs; phase 03 implements; cropfig handles artifacts. (This is the persona contract baked into `agents/figure-descriptor.md` — see "What You Do NOT Do" in that file.)
- Does **not** call `@analysis-implementer`. That is phase 03's job.
- Does **not** mutate `entry.impl_status` or `entry.critique_status`. Only `brief_status` (and `brief`, `title`) are owned by this phase.
- Does **not** read the data at `data_root`. The descriptor never reads data — it designs from the hypothesis + the user's research stack. Phase 03's implementer is the only agent that touches data files.
- Does **not** crop or render. Phase 03 owns the render call; cropfig owns the crop pass.
- Does **not** retry on a short / partial brief. The brief is fed to phase 03 as-is; if it's insufficient, the reviewer in phase 04 flags it and phase 05 sets `brief_status = "drafted"` so the next iter re-runs this phase.
- Does **not** edit any persona file under `agents/` or any file outside `figures.json`.
