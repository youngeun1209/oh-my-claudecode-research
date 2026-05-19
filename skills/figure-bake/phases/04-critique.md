---
name: figure-bake-critique
description: Phase 4 of $figure-bake. Dispatch @reviewer to read the rendered figure (PNG preferred, PDF fallback) and return a structured JSON list of severity-tagged issues. Append the critique to figures.json.figures[<fig-id>].critiques.
---

# Phase 4 — Critique

Invoke `@reviewer` to critique the figure that phase 03 just rendered. The reviewer must **Read** the rendered artifact (Codex is multimodal — Read on a PNG or PDF surfaces the visual content to the model). Parse the reviewer's response into a structured `issues` list with the same severity taxonomy as `$iterate-revision` (`critical | major | minor | nit`), then append the iter's critique to `figures.json.figures[<fig-id>].critiques`.

This phase is the second half of the loop body (after design + implement). Phase 05 reads the `issues` list to decide the verdict.

## Inputs (from phase 03)

| Name | Source | Purpose |
|---|---|---|
| `fig_id` | phase 03 | Used in the reviewer brief + the critique entry. |
| `figures_state` | phase 03 | Parsed dict; `figures[fig_id]` is the entry this phase appends to. |
| `current_iter` | loop primitive | Iter being critiqued. |
| `max_iter` | phase 01 | Surfaced to the reviewer brief so it knows the budget. |
| `implementer_output` | phase 03 | Raw report from the implementer — included in the reviewer brief so the reviewer can cite the implementer's claims. |
| `implementer_status` | phase 03 | `"ok" | "failed" | "no-brief"`. Drives the short-circuit logic in step 1. |
| `render_pdf_path` | phase 03 | Absolute path to the PDF the reviewer should treat as canonical (cropped preferred; uncropped fallback). |
| `render_png_path` | phase 03 | Absolute path to the cropped PNG, or `null`. If non-null, the reviewer reads this directly. |
| `cropfig_status` | phase 03 | Mentioned in the brief so the reviewer doesn't flag a "weird border" when cropfig didn't run. |
| `brief_text` | phase 02 | Included in the reviewer brief — the reviewer evaluates the rendered figure *against* the brief. |
| `run_id` | loop primitive | UUID for the current run; appended into the critique entry for traceability. |
| `iter_started` | loop primitive | Start-of-iter UTC ISO-8601, for the `started` field on the critique entry. |
| `venue` | engine_args (optional, may be null) | If `paper.json.venue` is set, the reviewer applies that venue's strictness. |

## Step 1 — Short-circuit on implementer failure

If `implementer_status` is `"failed"` or `"no-brief"`:

- Skip the dispatch entirely. There is nothing visual to critique.
- Fabricate a single `issues` entry for phase 05:

  - For `implementer_status == "failed"`:
    ```jsonc
    {
      "severity": "critical",
      "text":     "Implementer reported Status: failed in iter <current_iter>. The PDF was not produced (or was empty). Last error from the implementer: <one-line summary extracted from the implementer's Reason field, truncated to 200 chars>. Without a usable render, the figure cannot be critiqued — fix the render error and re-run.",
      "location": "<render_pdf_path>"
    }
    ```
  - For `implementer_status == "no-brief"`:
    ```jsonc
    {
      "severity": "critical",
      "text":     "Phase 02 produced no brief this iter; phase 03 was skipped. Nothing to critique.",
      "location": "brief:<fig_id>"
    }
    ```

- Continue at step 5 (Append) with this synthetic issues list. Do not invoke the reviewer on a non-existent figure.

## Step 2 — Choose what the reviewer reads

Two cases:

1. **`render_png_path` is non-null AND the file exists on disk.** The reviewer reads the PNG directly. Most efficient — Codex Read on PNG surfaces the image multimodally with low token weight. This is the normal happy path (cropfig succeeded in phase 03).

2. **`render_png_path` is null or missing.** Fall back to reading the PDF at `render_pdf_path`. Codex Read on PDF also surfaces the page content multimodally, but at higher token weight. This branch happens when cropfig failed in phase 03 step 6.

Verify the chosen path exists and is non-empty (size > 1 KB). If both are missing / empty, treat as `implementer_status == "failed"` per step 1 (this should be caught upstream by phase 03's verification; the guard is cheap).

Record `reader_path` = the chosen path. The reviewer brief tells the reviewer exactly which file to Read.

## Step 3 — Build the reviewer brief

Venue-specific strictness is conveyed in one line, like `$iterate-revision` phase 03 does. Build the `task_brief`:

```
You are reviewing figure "<fig_id>" rendered for the manuscript as a peer reviewer
for <venue or "the project's target venue">. Apply that venue's standards — strict
but specific. Do not redesign or rewrite; flag issues only.

Iter <current_iter> of <max_iter>. The descriptor designed this figure; the
implementer rendered it; you are the gate.

Design brief (what the descriptor specified):
<brief_text>

Implementer's render report:
<implementer_output>

<if cropfig_status == "failed":>
Note: the `cropfig` post-processing pipeline failed in this iter (typically a tooling
issue with margins / crop bounds — not a brief-level problem). You are looking at the
UNCROPPED render. Disregard outer whitespace, slide-title remnants, or stray captions
that look like they belong to a deck label — those are cropfig's responsibility, not
the figure's.

Render to review:
  Path: <reader_path>
  Read it directly with the Read tool. The figure is visual; you must see it to
  critique it. Do NOT critique solely from the brief or the implementer's report.

Critique dimensions (apply each to the rendered figure you just read):

  1. Does the figure deliver the brief's stated finding? (Title check — the brief's
     "This figure shows that X" must be obvious from the visual.)
  2. Panel structure — every panel from the brief present? Each panel labeled (a),
     (b), …? Reading order matches the argument?
  3. Visual system — colors match brief's hex codes? Colorblind-safe? Font sizes
     legible at print width? Line weights consistent?
  4. Data display — axes labeled with units? Tick density appropriate? Error bars or
     CIs shown where the brief calls for them?
  5. Caption alignment — does the rendered figure match what the brief's caption
     describes? (Especially: caption title vs. visual finding.)
  6. Implementation quality — vector preserved (text sharp)? No 3D effects, gradients,
     or rainbow palettes? Aspect ratio sensible for the venue's column width?

For each issue, return one JSON object with this exact shape:
  {
    "severity": "critical" | "major" | "minor" | "nit",
    "text":     "<one-to-three sentence description of the problem and what is required>",
    "location": "<panel label like 'panel (a)' or 'caption' or 'overall' or 'brief:N'>"
  }

Severity definitions (use them strictly):

  critical — fundamental flaw that blocks the figure entering the manuscript.
             Examples: rendered figure does not show what the brief claims; data is
             clearly fabricated or impossible; figure is unreadable (corrupted PDF
             rendering, blank page); colorblind conflict (red/green) used to encode
             meaning. A `critical` cannot be fixed by the implementer in a single
             code edit — it usually points back at the brief.

             If the issue is brief-level (the descriptor specified something the
             implementer cannot deliver, or the design is fundamentally wrong),
             prefix the `location` field with "brief:" so the next iter knows to
             re-run the descriptor. Example: "location": "brief:panel-b" means
             "the brief's panel-b spec is the problem, not the rendering of it."

  major    — significant concern fixable in a revision-pass of the implementer's
             code: a missing axis label, a font size below legibility, a missing
             error bar, a misaligned panel grid, wrong color from the brief's
             palette. Must be addressed before submission.

  minor    — small improvement: a tick density tweak, an annotation that helps but
             isn't required, a hint of clipping that doesn't impair the message.

  nit      — typography or stylistic: a stray comma in the caption, a panel-label
             font that's bold-italic where the brief said bold-only.

Output: a JSON array of issue objects only. No preamble, no explanation, no trailing
prose. If the figure has no issues at all, return an empty array [].
```

## Step 4 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":     "reviewer",
  "task_brief":  <the brief built in step 3>,
  "state_slice": {
    "fig_id":          <fig_id>,
    "iter":            <current_iter>,
    "max_iter":        <max_iter>,
    "reader_path":     <reader_path>,
    "cropfig_status":  <cropfig_status>,
    "venue":           <venue or null>
  },
  "expected_output_schema": [
    { "severity": "critical|major|minor|nit", "text": "<string>", "location": "<string>" }
  ]
}
```

The dispatch primitive will try to parse a JSON array out of the agent response and return it as `parsed`. Capture both `output` (raw) and `parsed` (best-effort).

## Step 5 — Normalize the issues list

Apply in order (mirrors `$iterate-revision/phases/03-review.md` step 4):

1. **Parse-success case.** If `parsed` is a non-null list:
   - Drop any entry that isn't an object with at least a `severity` field.
   - For each remaining entry, normalize:
     - `severity` → lowercase. If not in `{critical, major, minor, nit}`, coerce to `major` and append `[severity-coerced from <original>]` to the `text`.
     - `text` → string. If missing, use `(no description)`.
     - `location` → string. If missing, use `(unspecified)`.
   - Result: a cleaned list of `{severity, text, location}` dicts.

2. **Parse-failure case.** If `parsed` is null OR not a list:
   - Treat the entire raw `output` as one `major` issue:
     ```jsonc
     {
       "severity": "major",
       "text":     "Reviewer output did not parse as a JSON array. Raw output preserved here for the next iter's implementer/descriptor: <output truncated to 1500 chars>",
       "location": "(unparseable)"
     }
     ```
   - Do **not** abort. Phase 05 will see one `major` and most likely emit `CONTINUE` (or `HALT` at max_iter).

3. **Short-circuit case.** If step 1 of this phase produced the synthetic implementer-failure issue, skip this step entirely — that issues list is already canonical.

## Step 6 — Append to `figures.json.figures[<fig-id>].critiques`

Read `figures.json` via [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = figures` (re-read to capture any concurrent writes between phase 03 and phase 04 — there shouldn't be any, but the cost is one read).

Append one new entry to `figures.json.figures[<fig_id>].critiques`:

```jsonc
{
  "run_id":      "<run_id from the loop primitive>",
  "engine":      "figure-bake",
  "iter":        <current_iter>,
  "venue":       "<venue or null>",
  "started":    "<iter_started>",
  "ended":      "<UTC ISO-8601 now>",
  "reader_path": "<reader_path or null if synthetic>",
  "issues":      <normalized list from step 5>,
  "verdict":     null,
  "reason":      null
}
```

`verdict` and `reason` are **null at this point** — phase 05 fills them in. The append still happens here so the issues land on disk even if the user Ctrl-Cs between phase 04 and phase 05.

Also set `figures_state.figures[fig_id].critique_status = "done"` (always — the critique itself happened, regardless of severity counts).

Write `figures.json` back atomically (tmp + rename).

## Step 7 — Hand off to phase 05

Pass forward to phase 05:

- `fig_id`
- `figures_state` (with the new critique appended)
- `current_iter`, `max_iter`
- `run_id`, the entry index in `figures.json.figures[fig_id].critiques` (so phase 05 can update `verdict` / `reason` in place)
- The normalized `issues` list
- The `last_output` dict shaped as `{parsed: {issues: [...]}, output: <raw>, ...}` so the orchestrate `evaluate` primitive can read `last_output.parsed.issues` per its dotted-path contract.
- `implementer_status` (so phase 05 knows whether to flip `impl_status` to `"approved"` on DONE).

## Failure modes

| Condition | Behavior |
|---|---|
| `render_pdf_path` and `render_png_path` both missing on disk | Treat as `implementer_status == "failed"` per step 1; synthesize a `critical` issue; skip the dispatch. |
| Reviewer dispatch errors out (Agent tool error) | Loop primitive catches in its step 3b and emits BLOCKED. The critique entry was not appended; `critique_status` is unchanged. |
| Reviewer returns empty string | Treat as one `major` "Reviewer returned empty response" issue; proceed to phase 05 (likely CONTINUE / HALT). |
| Reviewer JSON parse fails | Step 5 case 2 — treat raw output as one `major` issue. Continue. |
| Reviewer "Read" tool fails on the chosen artifact | The reviewer should report the failure as a `critical` issue ("could not read figure file"). Phase 05 routes to BLOCKED. |
| `figures.json` write fails in step 6 | Bubble the OS error. The loop primitive will catch and BLOCKED — but the critique entry was the only durable record of this iter's issues, so the run's effective state is "iter ran, results lost". Phase 06 should surface this. |

## What this phase does NOT do

- Does **not** compute the verdict. Phase 05 does that.
- Does **not** mutate `entry.brief_status` or `entry.impl_status`. Phase 05 owns those based on the verdict.
- Does **not** invent severities. Only the four-level enum is allowed; the reviewer brief enforces it; step 5 coerces unknown values to `major`.
- Does **not** retry on parse failure. One dispatch per iter. Bad parses become `major` issues; the next iter re-critiques.
- Does **not** show the reviewer prior iterations' critiques. The reviewer reads the figure fresh every iter, to prevent "you already fixed this" bias (same constraint as `$iterate-revision` phase 03).
- Does **not** auto-resolve a render that looks broken by re-rendering. Re-render is the implementer's job in the next iter (CONTINUE) or the user's job before re-running (BLOCKED).
- Does **not** modify `_run-log.jsonl`. The loop primitive owns that file.
- Does **not** call `cropfig`. Phase 03 owns the crop pass; phase 04 only reads what's already on disk.
