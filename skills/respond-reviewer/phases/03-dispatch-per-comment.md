---
name: respond-reviewer-phase-03-dispatch-per-comment
description: For each non-structural comment, dispatch the labelled agent with the comment text plus relevant manuscript context. Capture response + `actions_taken` list per comment. Collect `structural` comments into the user-attention list (never dispatched).
---

# Phase 3 — Dispatch per comment

For every comment whose `agent` is non-null (i.e., label is `prose`, `analysis`, `citation`, or `clarification`), dispatch that agent with the comment text and a tightly-scoped manuscript slice. `structural` comments collect into a user-attention list that phase 06 surfaces.

This phase is the **fan-out** of the classify-and-dispatch shape. Each non-structural comment is one independent Agent-tool call — the dispatches do not share context, do not see each other's outputs, and are sequenced serially (Phase 0 decision §4 — currently serial-only).

This phase composes [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) once per non-structural comment.

## Inputs (from phase 02)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | phase 01 | Recorded in per-comment metadata for `_run-log.jsonl`. |
| `comments` | phase 02 | Enriched list — each has `comment_id`, `text`, `label`, `agent`, `target_section`, `figure_id`. |
| `paper_state` | phase 01 | For resolving `target_section` → section file path. |
| `manuscript_root` | phase 01 | Surfaced to every dispatch's brief. |
| `draft_only` | phase 01 | If true, dispatches still run but agents are told **not** to edit manuscript files (the engine cannot enforce this; the brief instructs the agent). |

## Step 1 — Partition comments

Walk the comments list and split:

- `to_dispatch` — comments whose `agent` is one of `paper-writer`, `analysis-implementer`, `literature-curator`.
- `user_attention` — comments whose `agent` is `null` (label `structural`).

If `to_dispatch` is empty (e.g., every comment was structural), skip the dispatch loop entirely and hand off straight to phase 04 with the user-attention list populated and an empty response set. Phase 06 will surface the user-attention list and mark the run `HALT` (user action required).

## Step 2 — Load section context for each target_section

For each unique `target_section` referenced across `to_dispatch`:

- Look up `paper_state.sections[target_section].path`.
- Read that file from disk into a `section_content` dict keyed by section name.

If the section file does not exist on disk (e.g., the path in `paper.json` is stale), record `section_content[name] = null` and log a warning. The per-comment dispatch will fall back to "section content unavailable; reason from comment text only".

If a comment has `target_section: null` (the supervisor was unsure), no section is preloaded — the dispatch brief instructs the agent to identify the relevant section itself based on the comment text.

## Step 3 — Build per-comment briefs

For each comment in `to_dispatch` (preserve order — phase 04 aggregates by `comment_id` but a stable iteration order keeps the rebuttal letter readable):

Build the `task_brief` using the agent-specific template below. All four templates share a common header:

```
You are responding to one peer reviewer comment on the manuscript at <manuscript_root>.
Your output will be assembled into a rebuttal letter; another agent (the supervisor) will
re-read your response to confirm it matches the actions you claim to have taken.

Comment id:    <comment_id>
Reviewer:      <reviewer>
Label:         <label> (assigned by the supervisor)
Target section: <target_section or "(unspecified — infer from the comment text)">
Figure id:     <figure_id or "(none mentioned)">

Comment text (verbatim):
<text>

Surrounding manuscript context:
<section_content[target_section], full file — or "(section not preloaded)" if null>

<agent-specific instructions below>
```

Then append the agent-specific block:

### 3a — `paper-writer` brief (labels `prose` and `clarification`)

```
This is a <label> comment. Your job is to:

1. Quote the comment in your response (verbatim, preserving any LaTeX/markdown the reviewer used).
2. Briefly acknowledge what is valid in the critique.
3. Provide the scientific answer in 2–4 sentences.
4. Make the textual change in the target section file if the change is small and
   the comment is unambiguous. Otherwise, propose the change as a quoted edit
   ("we propose replacing L34–38 with: ...") for the user to apply.

<if draft_only is true:>
DRAFT-ONLY MODE: do NOT edit any manuscript file. Propose changes as quoted text
in your response. The user will apply edits manually.

Output a JSON object with this shape:

  {
    "comment_id":   "<echo the comment_id>",
    "response":     "<the full prose response to the reviewer — quote → acknowledge → answer → point-to-change>",
    "actions_taken": [
      "<one short string per concrete action, e.g., 'edited sections/results.tex L34-38' or 'proposed replacement quoted in response'>"
    ],
    "files_touched": ["<list of file paths actually edited, or [] if draft-only or nothing edited>"]
  }
```

### 3b — `analysis-implementer` brief (label `analysis`)

```
This is an `analysis` comment. Your job is to:

1. Quote the comment in your response.
2. Identify what new analysis or robustness check is required.
3. Either (a) run the analysis if it is bounded and the data path is configured,
   or (b) describe the analysis precisely enough that the user can run it themselves.

<if figure_id is non-null:>
The comment requests a figure redraw of "<figure_id>". Do NOT redraw the figure
yourself in this dispatch. Identify the data/code paths and the redraw scope,
and note that the user should run `/figure-bake <figure_id>` as a follow-up.
Engines do not call other engines (Phase 2 decision §5).

<if draft_only is true:>
DRAFT-ONLY MODE: do NOT modify any code, data, or manuscript file. Describe the
analysis in the response only.

Output a JSON object with this shape:

  {
    "comment_id":      "<echo the comment_id>",
    "response":        "<the full prose response — quote → acknowledge → describe analysis + result-or-plan>",
    "actions_taken":   [
      "<one short string per action, e.g., 'ran sensitivity analysis varying k=3..7' or 'identified data slice for redraw'>"
    ],
    "files_touched":   ["<list of files actually written, or []>"],
    "next_steps":      ["<optional list of follow-up commands the user should run, e.g., '/figure-bake fig3'>"]
  }
```

### 3c — `literature-curator` brief (label `citation`)

```
This is a `citation` comment. Your job is to:

1. Quote the comment in your response.
2. Identify the specific reference(s) the reviewer is asking for.
3. Use the `verify-citation` skill if available to confirm each candidate exists
   (CrossRef / OpenAlex). Do NOT add unverified entries to `references.bib`.
4. If a verified citation is found, add it to `references.bib` and the summary
   table per your normal workflow. Quote the new citekey in your response.

<if draft_only is true:>
DRAFT-ONLY MODE: do NOT modify references.bib or any summary table. Describe the
proposed citation in the response only (full bibliographic record + DOI), so the
user can paste it in.

Output a JSON object with this shape:

  {
    "comment_id":      "<echo the comment_id>",
    "response":        "<the full prose response — quote → acknowledge → name the citation + how it answers the comment>",
    "actions_taken":   [
      "<e.g., 'verified DOI 10.xxxx/yyyy via CrossRef' or 'added citekey smith2024foo to references.bib'>"
    ],
    "files_touched":   ["<list of files actually written, or []>"],
    "citations_added": [
      { "citekey": "<key>", "doi": "<doi>", "title": "<title>" }
    ]
  }
```

### 3d — Common output schema notes

Every per-comment dispatch returns at minimum:

```jsonc
{
  "comment_id":   "<string>",
  "response":     "<string — the prose for the rebuttal letter>",
  "actions_taken": ["<string>", ...]
}
```

`files_touched`, `next_steps`, `citations_added` are agent-specific optional fields. Phase 04 reads only `comment_id`, `response`, `actions_taken`, and the optional `next_steps`. Phase 06 reads `files_touched` and `citations_added` for the user summary.

## Step 4 — Dispatch each non-structural comment

For each comment in `to_dispatch`, in order:

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":     "<comment.agent>",                 // paper-writer | analysis-implementer | literature-curator
  "task_brief":  <the brief built in step 3>,
  "state_slice": {
    "comment_id":      <comment.comment_id>,
    "label":           <comment.label>,
    "target_section":  <comment.target_section>,
    "figure_id":       <comment.figure_id>,
    "manuscript_root": <manuscript_root>,
    "draft_only":      <draft_only>
  },
  "expected_output_schema": {
    "comment_id":     "<string>",
    "response":       "<string>",
    "actions_taken":  ["<string>"]
  }
}
```

The dispatch primitive will try to parse a JSON object from the agent response. Capture both `output` (raw) and `parsed` (best-effort).

**Per-dispatch normalization:**

1. **Parse-success case.** If `parsed` is a non-null object with at least `comment_id`, `response`, `actions_taken`:
   - Verify `comment_id` matches the dispatched comment's id. If mismatch, log a warning and overwrite with the dispatched id (the agent is allowed to be sloppy here; we use the dispatch context as the source of truth).
   - Normalize `actions_taken` to a list of strings. If a string, wrap it as `[string]`. If null, empty list.
   - Carry through `files_touched`, `next_steps`, `citations_added` if present; treat missing as null / empty list.

2. **Parse-failure case.** If `parsed` is null or malformed:
   - Synthesize a response object:
     ```jsonc
     {
       "comment_id":    "<dispatched id>",
       "response":      "<raw output, truncated to 4000 chars if longer, with a note: '[response did not parse as JSON — raw text preserved here]'>",
       "actions_taken": ["dispatch parse failed; raw response preserved"],
       "parse_error":   "<reason>"
     }
     ```
   - Continue to the next comment. Do NOT abort the run — the user gets the raw text and phase 05 will likely mark this comment `disputed`.

3. **Dispatch-error case.** If the Agent tool itself errors:
   - Record the error on the comment:
     ```jsonc
     {
       "comment_id":     "<dispatched id>",
       "response":       "(dispatch failed — see error)",
       "actions_taken":  [],
       "dispatch_error": "<error message>"
     }
     ```
   - **Decision point:** if more than 25% of `to_dispatch` comments have errored so far, abort the run with `BLOCKED` — the manuscript / agent stack is in a bad state and continuing wastes tokens. Phase 06 records the partial state. Otherwise, continue.

## Step 5 — Collect responses

Build a `responses` list — one entry per comment in `to_dispatch`, in the same order. Each entry has the shape from step 4. Order matters because phase 04 assembles the rebuttal letter section-by-section in `comments` order, and the comment iteration order from phase 01's parser preserves the reviewer's intended sequence.

Also build a `user_attention` list — the `structural` comments from step 1. Phase 06 surfaces this verbatim. Each entry retains its full original shape (`comment_id`, `reviewer`, `text`, `label`, `reason`, `target_section`, `figure_id`, `agent: null`).

## Step 6 — Per-comment side-effect summary

Tally for phase 06's user summary:

- `n_dispatched` — `len(to_dispatch)`.
- `n_user_attention` — `len(user_attention)`.
- `n_parse_failures` — count of `responses` entries with `parse_error`.
- `n_dispatch_errors` — count of `responses` entries with `dispatch_error`.
- `files_touched_all` — union of `files_touched` across all `responses` (deduplicated).
- `citations_added_all` — concatenated `citations_added` across all `responses`.
- `next_steps_all` — concatenated `next_steps` across all `responses` (the suggested follow-up commands).

These are not written to `rebuttals.json` directly — phase 06 maps them into the rebuttal entry. They flow forward in-memory.

## Step 7 — Hand off to phase 04

Pass forward (everything from phase 02 plus):
- `responses` (list of per-comment response dicts).
- `user_attention` (list of structural comments).
- Per-comment side-effect tallies from step 6.

## Failure modes

| Condition | Behavior |
|---|---|
| Empty `to_dispatch` (every comment was `structural`) | Skip the dispatch loop; pass empty `responses` to phase 04. Phase 06 will mark the run `HALT`. |
| One dispatch parse-fails | Synthesize a `parse_error` response; continue. Likely → `disputed` in phase 05. |
| One dispatch errors | Synthesize a `dispatch_error` response; continue **unless** >25% of remaining comments have already errored, in which case abort `BLOCKED`. |
| Target section file missing on disk | `section_content[name] = null`; brief tells the agent to infer from the comment alone. |
| Agent returns the wrong `comment_id` | Override with the dispatched id; log warning. |
| `--draft-only` with an agent that edits anyway | The engine cannot enforce — agents read the brief and self-regulate. Phase 05 evaluation may catch (e.g., the supervisor flags "claims to have edited but mode was draft-only"). |

## What this phase does NOT do

- Does **not** dispatch `structural` comments. Ever. They collect into `user_attention` for phase 06.
- Does **not** call another engine. If a comment requests a figure redraw, the `@analysis-implementer` dispatch may include `/figure-bake <fig-id>` in its `next_steps` list, but **this engine** does not run it. Engines are leaves (Phase 2 decision §5).
- Does **not** loop on weak responses. One dispatch per comment. If phase 05 marks a response `disputed`, the user decides whether to re-run.
- Does **not** commit to git between dispatches. There is no `on_iter_end` hook in this engine.
- Does **not** evaluate responses for quality. That is phase 05's job (supervisor re-read).
- Does **not** assemble the rebuttal letter. That is phase 04.
- Does **not** read or write `rebuttals.json`. Phase 06 owns the state write.
- Does **not** retry failed dispatches. One shot per comment.
