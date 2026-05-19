---
name: respond-reviewer-phase-05-evaluate
description: Dispatch `@supervisor` to re-read the assembled rebuttal letter and flag weak responses (e.g., "we have added X" without X actually appearing). Emit one verdict per comment from `addressed | deferred | disputed`. Failures stay in the rebuttal entry with a reason.
---

# Phase 5 — Evaluate

Hand the assembled rebuttal letter and the per-comment `actions_taken` list back to `@supervisor`. The supervisor's job here is **adversarial** — it looks for responses that claim actions without performing them, or responses that materially fail to engage the reviewer's concern. The output is a verdict per comment.

This phase composes [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) once (one supervisor dispatch with all comments at once — same shape as phase 02's classification dispatch, just adversarial instead of taxonomic) and [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md) with the `engine-supplied` rule family (the per-comment verdict shape does not fit `severity-threshold`).

## Inputs (from phase 04)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | phase 01 | Recorded in the dispatch description. |
| `letter_content` | phase 04 | The assembled rebuttal letter, in-memory. The supervisor reads this. |
| `letter_filename` | phase 04 | Surfaced to the supervisor in the brief as context. |
| `output_format` | phase 01 | `latex | md` — told to the supervisor so it can read LaTeX commands literally if present. |
| `comments` | phase 02 | The enriched comments list (label, target_section, agent, reason). |
| `responses` | phase 03 | Per-comment response dicts with `response`, `actions_taken`, etc. |
| `user_attention` | phase 03 | Structural comments — surfaced to the supervisor as the "deferred" set so it does not flag them as missing. |
| `paper_state` | phase 01 | The supervisor may want to verify a section's current content matches what the response claims to have changed. |
| `draft_only` | phase 01 | Surfaced — the supervisor should be lenient on "did not edit" claims if draft-only is set. |

## Step 1 — Build the adversarial brief

Format the per-comment payload as a numbered block (similar to phase 02, but each entry now has the response and actions, not just the comment text):

```
For each comment below, decide one verdict:

  addressed — the response materially answers the reviewer's concern AND the
              actions taken (if any) are consistent with the response prose.
              "Material" means the response engages the substance of the comment,
              not just acknowledges it.

  deferred  — the response is reasonable but points to a follow-up the user must
              run (e.g., /figure-bake, manual --allow-tbd clearance, a structural
              decision the supervisor must make). The work is NOT complete; the
              user will see this and continue manually. Comments labeled
              `structural` in phase 02 do NOT appear in this list — they are
              already in the user-attention section and need no verdict from you.

  disputed  — the response is weak or misleading. Examples:
              - claims to have added a reference but no citation_added is reported
              - claims an edit ("we revised L34-38") but no files_touched is reported
              - claims a new analysis but actions_taken is empty
              - response is generic and does not engage the comment's substance
              - response contradicts the manuscript content
              Defaulting to `disputed` on borderline cases is correct — the user
              must intervene rather than accept a weak rebuttal silently.

Reviewer letter (rebuttal draft, format=<output_format>):
<letter_content>

Per-comment metadata:
<for each comment in `comments` whose label != "structural":>
  Comment <comment_id>:
    label:           <label>
    target_section:  <target_section or null>
    figure_id:       <figure_id or null>
    response prose:  <response_by_id[comment_id].response, full>
    actions_taken:   <response_by_id[comment_id].actions_taken, as a JSON array>
    files_touched:   <response_by_id[comment_id].files_touched or []>
    next_steps:      <response_by_id[comment_id].next_steps or []>
    parse_error:     <response_by_id[comment_id].parse_error or null>
    dispatch_error:  <response_by_id[comment_id].dispatch_error or null>

<if draft_only is true:>
NOTE: this run was --draft-only. The agents were told not to edit files. An empty
files_touched is therefore expected; do NOT downgrade a response to `disputed`
solely because no file was edited. Continue to flag responses that contradict the
manuscript or fail to engage the comment.

For each comment, return one JSON object:

  {
    "comment_id": "<the id>",
    "verdict":    "addressed | deferred | disputed",
    "reason":     "<one-to-three sentences explaining why this verdict>"
  }

Rules:
- Every non-structural comment must appear exactly once, in input order.
- If `parse_error` or `dispatch_error` is set on a response, the verdict is
  almost always `disputed` — the response literally did not arrive intact.
- If the response references a section edit but `files_touched` is empty AND
  draft_only is false, the verdict is `disputed`.
- If the response references a citation but `citations_added` is empty (or
  missing) AND draft_only is false, the verdict is `disputed`.
- If the response is a description of a follow-up the user must run (with a
  non-empty `next_steps`), the verdict is `deferred`, NOT `disputed`.
- `addressed` is the default for clean, complete responses with consistent
  actions.

Output: a JSON array of verdict objects only. No preamble, no explanation, no
trailing prose. Array length must equal the number of non-structural comments.
```

## Step 2 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":    "supervisor",
  "task_brief": <the brief built in step 1>,
  "state_slice": {
    "run_id":          <run_id>,
    "letter_filename": <letter_filename>,
    "output_format":   <output_format>,
    "draft_only":      <draft_only>,
    "n_responses":     <len(responses)>
  },
  "expected_output_schema": [
    {
      "comment_id": "<string>",
      "verdict":    "addressed|deferred|disputed",
      "reason":     "<string>"
    }
  ]
}
```

Capture both `output` (raw) and `parsed` (best-effort).

## Step 3 — Normalize the verdict list

Apply in order:

1. **Parse-success case.** If `parsed` is a non-null list:
   - For each entry, normalize:
     - `comment_id` → string. Must match one of the non-structural comments. If not, attempt alignment by ordinal; if still no match, log a warning and skip.
     - `verdict` → lowercase. Must be in `{addressed, deferred, disputed}`. If not, coerce to `disputed` and append `[verdict-coerced from <original>]` to `reason`. (Coerce to `disputed` rather than `addressed` to preserve the user-attention default.)
     - `reason` → string. If missing, use `(no reason given)`.

2. **Parse-failure case.** If `parsed` is null or not a list:
   - Synthesize a fallback verdict list: assign **every** non-structural comment `verdict = disputed` with `reason = "supervisor re-evaluation failed; defaulting to disputed pending human review"`. The user will see every comment flagged and can re-run after fixing whatever caused the supervisor to fail.
   - Continue to step 4.

3. **Missing-comment_id case.** Some non-structural comments did not get a verdict back:
   - For each missing comment, synthesize `verdict = disputed`, `reason = "no verdict returned by supervisor; defaulted to disputed"`.
   - Log warnings naming the missing ids.

## Step 4 — Apply the orchestrate evaluate primitive (per-run verdict)

Call [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md) with the **engine-supplied** rule family — the per-comment shape does not fit `severity-threshold`, so the engine computes its own run-level verdict and hands it to the primitive for logging only:

Compute the run-level verdict from the per-comment verdict distribution:

| Distribution | Run verdict | Reason template |
|---|---|---|
| Any per-comment `disputed` | `HALT` | `<N> response(s) disputed by supervisor — user must address` |
| ≥1 structural comment present (regardless of others) | `HALT` | `<M> structural comment(s) require human decision (plus <D> disputed if any)` |
| Any `deferred`, none `disputed`, no structural | `HALT` | `<K> response(s) deferred to user follow-up — see suggested next steps` |
| All `addressed`, no structural, no deferred, no disputed | `DONE` | `all <N> non-structural comment(s) addressed; no follow-up required` |
| Any phase 03 dispatch error or parse failure that wasn't already overridden by a later success | `BLOCKED` | `<N> dispatch error(s) during phase 03 — partial rebuttal preserved` |

Note that `CONTINUE` never appears — this engine is single-pass.

Call the primitive:

```jsonc
{
  "engine_name":       "respond-reviewer",
  "state_after":       <paper_state — unchanged from phase 01 unless phase 03 edits flipped a section status; pass current>,
  "last_output":       <the supervisor dispatch result from step 2>,
  "iter":              1,
  "max_iter":          1,
  "verdict_rule_spec": {
    "kind":    "engine-supplied",
    "verdict": "<the run-level verdict computed above>",
    "reason":  "<the run-level reason computed above>"
  },
  "run_id":            <run_id>,
  "section":           null,
  "venue":             null
}
```

The primitive will record the verdict to `reviews.json.runs` under `engine: "respond-reviewer"`. The per-comment verdicts do NOT go into `reviews.json` — they live in `rebuttals.json` only (phase 06 writes them). `reviews.json` records the run-level verdict for orchestration-level state tracking; the rich per-comment detail belongs in `rebuttals.json`.

## Step 5 — Attach verdicts to the comments-in-memory

For each non-structural comment, find its verdict in the normalized list (or the synthesized fallback) and attach it as `comment.verdict` and `comment.verdict_reason`. Phase 06 reads these when writing `rebuttals.json`.

For each structural comment in `user_attention`, attach the synthetic verdict `comment.verdict = "deferred"` and `comment.verdict_reason = "structural — surfaced to user-attention; no auto-response generated"`. This makes the `rebuttals.json` entry uniform: every comment has a verdict, even if the structural ones were never dispatched.

## Step 6 — Hand off to phase 06

Pass forward (everything from phase 04 plus):
- `run_verdict` (one of `DONE | HALT | BLOCKED`).
- `run_reason` (the run-level reason string).
- `comments` (now enriched with per-comment `verdict` + `verdict_reason`).
- `responses` (unchanged).
- `user_attention` (unchanged from phase 03, but each entry has `verdict = deferred`).
- `eval_dispatch_meta` (timestamp + parse-error flag from step 2, for the `_run-log.jsonl` summary).

## Failure modes

| Condition | Behavior |
|---|---|
| Supervisor dispatch errors out | The run-level verdict is `BLOCKED`. Per-comment verdicts default to `disputed` (the synthetic fallback in step 3 case 2). Phase 06 still writes `rebuttals.json` with the partial state. |
| Supervisor returns empty response | Same as parse-failure; every non-structural comment defaults to `disputed`. Run-level `HALT`. |
| Supervisor returns wrong-length list | Synthesize verdicts for missing comments; run-level computed from the partial set with the missing-comment count contributing to `disputed`. |
| `reviews.json` write inside the primitive fails | Bubble the OS error; phase 06 still attempts the `rebuttals.json` write since that is the engine's primary durable artifact. |

## What this phase does NOT do

- Does **not** modify the assembled letter. `letter_content` is read-only here. (If the supervisor's re-evaluation suggests rewrites, those land in `verdict_reason` for the user to address on the next run; the engine does not auto-rewrite.)
- Does **not** re-dispatch weak responses. One supervisor pass per run. The user re-runs after acting on `disputed` verdicts.
- Does **not** edit the manuscript. Phase 03 dispatches may have; this phase is read-only against the manuscript.
- Does **not** write to `rebuttals.json`. Phase 06 owns that. The verdicts flow through in-memory.
- Does **not** call other engines. Engine-leaves invariant (Phase 2 decision §5).
- Does **not** invent verdict values. Per-comment verdicts are exactly `{addressed, deferred, disputed}`; run-level verdicts are `{DONE, HALT, BLOCKED}`. No `CONTINUE` (single-pass), no `addressed` at run-level.
- Does **not** retry on parse failure. The synthetic `disputed`-everywhere fallback is the recovery path. The user re-runs.
