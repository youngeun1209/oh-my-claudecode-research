---
name: respond-reviewer-phase-02-classify
description: Dispatch `@supervisor` to label every parsed comment as exactly one of `prose | analysis | citation | clarification | structural`. Map labels to dispatched agents. `structural` is never dispatched — it routes to user-attention in phase 06.
---

# Phase 2 — Classify

Invoke `@supervisor` once with the full comments list and have it return a label per comment. Map labels onto dispatched-agent names. This is the only phase that calls the supervisor before the per-comment fan-out — the supervisor's role here is taxonomy, not response.

This phase composes [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md). The primitive owns the Agent-tool call; this phase owns the task brief and the label normalization.

## Inputs (from phase 01)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | phase 01 | UUID — flows into the dispatch's description and into `_run-log.jsonl`. |
| `review_letter_path` | phase 01 | Original input path; used in the brief for context. |
| `input_format` | phase 01 | `markdown | latex` — told to the supervisor so it knows how to read inline syntax. |
| `manuscript_root` | phase 01 | Surfaced to the supervisor so it can reason about which section a comment touches. |
| `comments` | phase 01 | List of `{comment_id, reviewer, text, raw_offset}` dicts. |
| `paper_state` | phase 01 | Parsed `paper.json` — gives the supervisor the section name → file path map. |

## Step 1 — Build the classification brief

Format the comments as a numbered block the supervisor can read top-to-bottom:

```
Comment R1.1: <text from comments[0]>
Comment R1.2: <text from comments[1]>
...
```

Include the full text of each comment, no truncation. If the letter is unusually long (total brief > 30K characters), warn but proceed — the supervisor's persona body + this brief together still fit comfortably in a model context.

Build the `task_brief`:

```
Classify each comment from the reviewer letter below into exactly one of these labels:

  prose         — reviewer wants the text reworded, hedged, or restructured.
                  The claim and the evidence stay the same; only the prose changes.
  analysis      — reviewer wants new analysis: a robustness check, additional test,
                  re-run with different parameters, or a figure redraw. Any comment
                  that requires running code or producing new numbers is `analysis`.
  citation      — reviewer wants a reference added, prior work covered, or a comparison
                  to a specific paper. The fix is in the bibliography, not the prose.
  clarification — reviewer is confused and wants a sentence or two added to clarify.
                  No new analysis, no new citation — just a brief textual addition.
  structural    — reviewer is asking for a framing change, scope decision, section
                  reorganization, or a methodological pivot. These are scientific
                  judgment calls that require a human decision. Default to `structural`
                  if you are uncertain between this label and any other.

Reviewer letter format: <input_format>
Manuscript root: <manuscript_root>
Sections available (from paper.json):
  <render sections as: "<name>: <path>" one per line, e.g. "results: manuscript/sections/results.tex">

Comments to classify:
<the numbered comments block from step 1>

For each comment, return one JSON object with this exact shape:

  {
    "comment_id":      "<the id from the comment above, e.g., R1.1>",
    "label":           "prose | analysis | citation | clarification | structural",
    "reason":          "<one-sentence justification for the label choice>",
    "target_section":  "<section name from paper.json.sections, or null if unclear>",
    "figure_id":       "<figure ID if the comment names one, or null>"
  }

Rules:
- Every parsed comment must appear in the output exactly once, in the same order.
- `label` must be one of the five above. Anything else fails the parse.
- `target_section` is best-effort — when the comment text or the reviewer's intent
  unambiguously points at one section, name it; otherwise null.
- `figure_id` is best-effort — when the comment names a figure (e.g., "Figure 3",
  "Fig. 2B"), record the ID; otherwise null. Comments that mention a figure should
  usually be labeled `analysis` (figure redraw is an analysis task) — but a comment
  whose only ask is "cite the original Figure 3 method" is `citation`.
- If you are uncertain between `structural` and another label, choose `structural`.
  Structural comments are not auto-dispatched; defaulting to `structural` keeps a
  human in the loop. This is the ethical guardrail.

Output: a JSON array of label objects only. No preamble, no explanation, no
trailing prose. The array length must equal the number of input comments.
```

## Step 2 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":    "supervisor",
  "task_brief": <the brief built in step 1>,
  "state_slice": {
    "review_letter":   <review_letter_path>,
    "input_format":    <input_format>,
    "manuscript_root": <manuscript_root>,
    "n_comments":      <len(comments)>,
    "sections":        <object: { name: path } for each section in paper_state.sections>
  },
  "expected_output_schema": [
    {
      "comment_id":     "<string>",
      "label":          "prose|analysis|citation|clarification|structural",
      "reason":         "<string>",
      "target_section": "<string|null>",
      "figure_id":      "<string|null>"
    }
  ]
}
```

The dispatch primitive will try to parse a JSON array out of the supervisor's response and return it as `parsed`. Capture both `output` (raw) and `parsed` (best-effort).

## Step 3 — Normalize the label list

Apply in order:

1. **Parse-success case.** If `parsed` is a non-null list with length equal to `len(comments)`:
   - For each entry, normalize:
     - `comment_id` → string. Must match a parsed comment_id; if not, attempt to align by index (parsed list ordinal matches comments list ordinal). If still no match, log a warning and use the comments-list-ordinal id.
     - `label` → lowercase. Must be in `{prose, analysis, citation, clarification, structural}`. If not, coerce to `structural` and append `[label-coerced from <original>]` to `reason`. (Coercing to `structural` rather than `prose` preserves the ethical-gate default — anything weird stays in user hands.)
     - `reason` → string. If missing, use `(no reason given)`.
     - `target_section` → string or null. If a string, verify it exists in `paper_state.sections`; if not, set to null and log a warning.
     - `figure_id` → string or null. No verification (figures.json is not read by this engine for label-time validation).

2. **Parse-failure / length-mismatch case.** If `parsed` is null, not a list, OR has wrong length:
   - Log a warning with the parse problem.
   - Synthesize a fallback labels list: assign **every** comment `label = structural` with `reason = "supervisor classification failed; defaulted to structural pending human review"`. This preserves the ethical-gate default and ensures phase 03 dispatches nothing (every comment is human-only). The user sees the full letter routed to user-attention in phase 06 and can re-run after fixing the classification step.
   - Continue to step 4.

3. **Missing-comment_id case.** If some comments have no corresponding label entry after step 1:
   - For each missing comment, synthesize `label = structural`, `reason = "no label returned by supervisor; defaulted to structural"`.
   - Log warnings naming the missing ids.

## Step 4 — Map labels to dispatched agents

For each labelled comment, attach `agent` based on the label:

| Label | `agent` field |
|---|---|
| `prose` | `paper-writer` |
| `analysis` | `analysis-implementer` |
| `citation` | `literature-curator` |
| `clarification` | `paper-writer` |
| `structural` | `null` |

`structural` comments get `agent: null` — they are surfaced to the user, not dispatched. Phase 03 explicitly skips any comment whose `agent` is null.

## Step 5 — Annotate the comments list in-place

Merge the labels back onto the parsed comments list from phase 01. Each comment dict now has:

```jsonc
{
  "comment_id":     "R1.1",
  "reviewer":       "R1",
  "text":           "<full body>",
  "raw_offset":     <int>,
  "label":          "<one of the five>",
  "reason":         "<supervisor's justification>",
  "target_section": "<name | null>",
  "figure_id":      "<id | null>",
  "agent":          "<persona name | null>"
}
```

Phase 03 reads this enriched list and dispatches per-comment.

## Step 6 — Hand off to phase 03

Pass forward:
- `run_id`, `started_at` (unchanged from phase 01).
- `review_letter_path`, `review_letter_abs`, `input_format`, `output_format` (unchanged).
- `manuscript_root`, `draft_only` (unchanged).
- `comments` (enriched with label, agent, reason, target_section, figure_id).
- `paper_state`, `rebuttals_state` (unchanged — phases 03 and 06 will mutate).
- `classification_dispatch_meta` (the dispatch's timestamp + any parse-error flag, for the `_run-log.jsonl` summary in phase 06).

Also compute a quick count for the user transcript (printed at the end of this phase):

```
respond-reviewer phase 02 — classified <N> comments:
  prose:         <count>
  analysis:      <count>
  citation:      <count>
  clarification: <count>
  structural:    <count> (will be routed to user-attention)
```

This is a status line, not the final summary — phase 06 prints the user-facing summary.

## Failure modes

| Condition | Behavior |
|---|---|
| Supervisor dispatch errors out | Loop primitive's dispatch-error semantics apply: this phase emits a synthetic-fail signal so phase 06 records `BLOCKED` for the run. No comments labelled; phase 03 skipped entirely. |
| Supervisor returns empty response | Treated as parse-failure; step 3 case 2 applies (default every comment to `structural`). User sees the full letter in user-attention. |
| Supervisor returns wrong-length list | Same as parse-failure; default to `structural`. |
| One comment's label coerced from invalid → `structural` | Logged with the original value preserved in `reason`. Proceeds. |
| `target_section` references a section not in `paper.json` | Set to null; log warning; proceed. The per-comment dispatch in phase 03 will reason without a definite target section. |

## What this phase does NOT do

- Does **not** read the manuscript content. The supervisor classifies on the comment text alone (plus the section name → path map for context). Reading section content is phase 03's job per-comment.
- Does **not** dispatch any specialist agents. That is phase 03 — this phase only labels.
- Does **not** answer or partially answer comments. The supervisor here is a taxonomist, not a respondent. (The supervisor will re-appear in phase 05 as an evaluator of the assembled rebuttal.)
- Does **not** write to `rebuttals.json`. Phase 06 owns that file.
- Does **not** mutate `paper.json`. The labels live in-memory until phase 06 records them.
- Does **not** validate the figure_id against `figures.json`. The figure-redraw routing is best-effort — phase 03 will surface "figure not found" if the dispatched `@analysis-implementer` flags it.
- Does **not** retry on parse failure. The synthetic `structural`-everywhere fallback is the recovery path. The user re-runs after addressing whatever caused the supervisor to fail.
