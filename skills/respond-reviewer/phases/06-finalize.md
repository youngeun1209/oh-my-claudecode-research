---
name: respond-reviewer-phase-06-finalize
description: Write the assembled rebuttal letter to disk, append the rebuttal entry to `rebuttals.json`, append start + summary records to `_run-log.jsonl`, and print the user-facing summary (including the user-attention list for any structural comments).
---

# Phase 6 — Finalize

The terminal phase. Three durable writes (rebuttal letter file, `rebuttals.json` entry, `_run-log.jsonl` summary line) plus the user transcript summary. No subagent dispatch — pure state + I/O.

## Inputs (from phase 05)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | phase 01 | UUID — ties the durable records together. |
| `started_at` | phase 01 | Run-start timestamp; copied into the rebuttal entry. |
| `review_letter_path` | phase 01 | Recorded in the rebuttal entry. |
| `input_format`, `output_format` | phase 01 | Recorded for cross-reference. |
| `manuscript_root` | phase 01 | Letter write target directory. |
| `draft_only` | phase 01 | Recorded in the entry and surfaced in the summary. |
| `letter_content` | phase 04 | The assembled rebuttal — written to disk in step 1. |
| `letter_filename` | phase 04 | `rebuttal-letter.tex` or `rebuttal-letter.md`. |
| `letter_target_path` | phase 04 | Planned absolute path. |
| `comments` | phase 05 | Enriched with per-comment `verdict` + `verdict_reason`. |
| `responses` | phase 03 | Per-comment dispatch results. |
| `user_attention` | phase 05 | Structural comments (each carries the synthetic `deferred` verdict). |
| `run_verdict` | phase 05 | `DONE | HALT | BLOCKED`. |
| `run_reason` | phase 05 | Run-level reason string. |
| `paper_state`, `rebuttals_state` | phase 01 | The latter is appended to. |
| Tallies from phase 03 step 6 | phase 03 | `files_touched_all`, `citations_added_all`, `next_steps_all`, error counts. |

## Step 1 — Write the rebuttal letter to disk

Target path: `letter_target_path` (`<manuscript_root>/rebuttal-letter.<ext>`).

If `<manuscript_root>` does not exist or is not writable:
- Log a warning naming the path.
- Fall back to `./rebuttal-letter.<ext>` (the project root).
- Record the fallback path as the canonical `letter_path` going into `rebuttals.json`.

Use the `Write` tool with `letter_content` as the file body. If the target file already exists (a prior run wrote to it), back up the existing file to `<target>.<timestamp>.bak` before overwriting. Do not silently lose a prior rebuttal — the user may want to compare drafts.

Atomic write pattern (per the orchestrate primitive's "Atomicity" convention):

1. `Write` to `<target>.tmp`.
2. Rename `<target>` (if it exists) to `<target>.<UTC-ISO-8601>.bak`.
3. Rename `<target>.tmp` to `<target>`.

If any step fails, log the OS error and continue — `rebuttals.json` is still written in step 2 with the in-memory `letter_content`, so the rebuttal is recoverable. The user gets a warning in the summary.

Record `letter_path_final` (the path actually written) and `backup_path` (if a backup was made; else null).

## Step 2 — Append the run entry to `rebuttals.json`

Build the entry:

```jsonc
{
  "run_id":         <run_id>,
  "review_letter":  <review_letter_path>,
  "input_format":   <input_format>,
  "output_format":  <output_format>,
  "manuscript_root": <manuscript_root>,
  "draft_only":     <draft_only>,
  "started":        <started_at>,
  "ended":          <UTC ISO-8601 now>,
  "letter_path":    <letter_path_final>,
  "letter_backup":  <backup_path or null>,
  "verdict":        <run_verdict>,
  "reason":         <run_reason>,
  "comments":       [
    <for each comment in `comments`, in input order:>
    {
      "comment_id":     <comment.comment_id>,
      "reviewer":       <comment.reviewer>,
      "label":          <comment.label>,
      "agent":          <comment.agent or null>,
      "target_section": <comment.target_section>,
      "figure_id":      <comment.figure_id>,
      "classification_reason": <comment.reason>,
      "response":       <responses-by-id.get(comment.comment_id, {}).get("response") or null>,
      "actions_taken":  <responses-by-id.get(comment.comment_id, {}).get("actions_taken") or []>,
      "files_touched":  <responses-by-id.get(comment.comment_id, {}).get("files_touched") or []>,
      "citations_added": <responses-by-id.get(comment.comment_id, {}).get("citations_added") or []>,
      "next_steps":     <responses-by-id.get(comment.comment_id, {}).get("next_steps") or []>,
      "parse_error":    <responses-by-id.get(comment.comment_id, {}).get("parse_error") or null>,
      "dispatch_error": <responses-by-id.get(comment.comment_id, {}).get("dispatch_error") or null>,
      "verdict":        <comment.verdict>,
      "verdict_reason": <comment.verdict_reason>
    }
  ],
  "user_attention_count": <len(user_attention)>,
  "suggested_next_steps": [
    <for each step in next_steps_all (deduplicated, preserve first-seen order):>
    <step>
  ],
  "summary": {
    "n_comments":         <len(comments)>,
    "n_dispatched":       <count of non-structural comments>,
    "n_user_attention":   <len(user_attention)>,
    "by_label":           { "prose": <int>, "analysis": <int>, "citation": <int>, "clarification": <int>, "structural": <int> },
    "by_verdict":         { "addressed": <int>, "deferred": <int>, "disputed": <int> },
    "n_parse_failures":   <int from phase 03>,
    "n_dispatch_errors":  <int from phase 03>,
    "files_touched_all":  <deduplicated list>,
    "citations_added_all": <list>
  }
}
```

Note: structural comments retain `agent: null`, `response: null`, `actions_taken: []`, `verdict: "deferred"`, `verdict_reason: "structural — surfaced to user-attention; no auto-response generated"`. They are not omitted — the user gets the full per-comment record in one place.

Append the entry to `rebuttals_state.rebuttals` and write the file back atomically (tmp + rename) per the orchestrate state-read primitive's "Atomicity" section.

If the write fails:
- Log the OS error.
- Print the rebuttal entry as JSON to the transcript so the user has a copy.
- Continue to step 3 — the letter file is already on disk, the transcript has the entry, the only loss is the durable state record.

## Step 3 — Update `paper.json` if any sections changed

If `responses` reported `files_touched` that include any `paper_state.sections[*].path`, the affected sections may have been modified. The engine does not automatically flip their `status` (e.g., to `revising`) — that is `/iterate-revision`'s job and would be premature here. But:

- For each section path that appears in `files_touched_all` AND matches a `paper_state.sections[name].path`:
  - Log to the transcript: `respond-reviewer: section <name> was edited by a dispatched agent — consider running /iterate-revision <path> to re-review.`
- Update `paper_state.last_updated = <UTC ISO-8601 now>`.
- Write `paper.json` back atomically.

If `--draft-only` was set, this step is a no-op — no sections were edited.

## Step 4 — Append run records to `_run-log.jsonl`

The orchestrate `loop` primitive normally writes the start + end records, but `/respond-reviewer` does not use the loop primitive as its driver (single-pass engine). This phase writes the equivalent records directly.

Append three lines (atomic-append, never overwrite):

```jsonc
// 1. Start record (written here at finalization, after the fact — the start_at timestamp from phase 01 preserves the actual run-start time):
{
  "run_id":   <run_id>,
  "engine":   "respond-reviewer",
  "args":     {
    "review_letter":  <review_letter_path>,
    "manuscript":     <manuscript_root>,
    "draft_only":     <draft_only>,
    "format":         <output_format>
  },
  "started":  <started_at>,
  "phase":    "start"
}

// 2. End record:
{
  "run_id":       <run_id>,
  "engine":       "respond-reviewer",
  "args":         <same args dict>,
  "started":      <started_at>,
  "ended":        <UTC ISO-8601 now>,
  "iter_count":   1,
  "verdict":      <run_verdict>,
  "reason":       <run_reason>,
  "tokens_used":  <cumulative across phase 02 + phase 03 + phase 05 dispatches; post-hoc per Phase 0 decision §6>,
  "phase":        "end"
}

// 3. Summary record (engine-specific user-facing payload, same convention as iterate-revision phase 05):
{
  "run_id":          <run_id>,
  "engine":          "respond-reviewer",
  "phase":           "summary",
  "review_letter":   <review_letter_path>,
  "letter_path":     <letter_path_final>,
  "verdict":         <run_verdict>,
  "reason":          <run_reason>,
  "n_comments":      <len(comments)>,
  "n_dispatched":    <count of non-structural>,
  "n_user_attention": <len(user_attention)>,
  "by_label":        <same dict from step 2>,
  "by_verdict":      <same dict from step 2>,
  "summary_at":      <UTC ISO-8601 now>
}
```

Use the same atomic-append semantics as the orchestrate loop primitive: open in append mode, write one line + `\n`, `flush` + `fsync`.

If the append fails (disk full, permission denied), do **not** abort — the rebuttal letter and `rebuttals.json` are already durable. Log a warning.

## Step 5 — Print the user summary

Compute `duration_sec = ended - started` and format per the iterate-revision convention:
- `< 60s` → `"<N>s"`
- `< 3600s` → `"<Nm <S>s"`
- otherwise → `"<H>h <M>m"`

Print this block to the transcript:

```
Review letter: <review_letter_path>
Rebuttal:      <letter_path_final>
Verdict:       <run_verdict>
Comments:      <n_dispatched> dispatched, <n_user_attention> need human decision
By label:      prose=<n>, analysis=<n>, citation=<n>, clarification=<n>, structural=<n>
By verdict:    addressed=<n>, deferred=<n>, disputed=<n>
Duration:      <formatted>
Tokens:        <tokens_used> (post-hoc; see _run-log.jsonl for detail)
Run id:        <run_id>

Reason: <run_reason>
```

Then append the verdict-specific block:

### DONE

```
All non-structural comments addressed. Rebuttal letter written to:
  <letter_path_final>

Suggested next:
  - Read the rebuttal letter and verify each response matches the manuscript.
  - Compile: cd <manuscript_root> && latexmk -pdf rebuttal-letter.tex
                (if --format latex)
  - Re-run /iterate-revision on any section that was edited (see paper.json updates above).
```

### HALT

If `len(user_attention) > 0`, render the user-attention block first:

```
USER ATTENTION REQUIRED — <N> structural comment(s) need human decision:

  [<comment_id>] <reviewer>:
    <comment.text, truncated to 200 chars with "…" if longer>
    Classification reason: <comment.reason>
    Target section (best guess): <comment.target_section or "(unspecified)">

  [<next structural comment>]
    ...

These comments were not auto-dispatched (engines do not make framing or scope
decisions). Address them in the rebuttal letter manually, or revise the
manuscript and re-run /respond-reviewer with the updated letter.
```

Then, regardless of whether `user_attention` is empty:

```
<count of disputed> response(s) flagged DISPUTED by the supervisor:

  [<comment_id>] <verdict_reason from the disputed comment>
  ...

<count of deferred + non-structural> response(s) DEFERRED to user follow-up:

  [<comment_id>] <verdict_reason>
  ...

Suggested next:
  - Read the rebuttal letter: <letter_path_final>
  - Address disputed responses (rewrite or accept manually).
  - Run any of the suggested follow-up commands (engines do not auto-invoke):
      <render `suggested_next_steps` list from step 2, one per line>
  - Re-run /respond-reviewer with an updated letter once decisions are made.

Full state: .claude/omcr-state/rebuttals.json (run_id=<run_id>)
```

### BLOCKED

```
Run BLOCKED — partial rebuttal preserved. Cause:
  <run_reason>

Dispatch errors (<count>):
  [<comment_id>] <dispatch_error from the comment>
  ...

What was preserved:
  - Rebuttal letter (partial): <letter_path_final>
  - rebuttals.json entry with verdict=BLOCKED and all per-comment state recorded.
  - _run-log.jsonl start + end + summary records.

After addressing the cause, re-run /respond-reviewer with the same letter. The
new run is a fresh entry; the BLOCKED entry stays for audit.
```

## Step 6 — Surface render warnings

If phase 04 emitted any warnings (sanity-check failures or `--draft-only` mismatch), print them after the verdict-specific block:

```
Warnings:
  - <warning 1>
  - <warning 2>
```

These do not change the verdict; they alert the user to inspect specific artifacts.

## Failure modes

| Condition | Behavior |
|---|---|
| Letter write fails | Fall back to project root; if that also fails, log the OS error and continue — `rebuttals.json` still holds the in-memory letter as a recovery path (write the `letter_content` into the entry as a `letter_inline` fallback field). |
| `rebuttals.json` write fails | Print the entry JSON to the transcript so the user can recover. Continue. |
| `_run-log.jsonl` append fails | Log a warning; do not abort. The summary in the transcript and `rebuttals.json` together are the canonical record. |
| `paper.json` write in step 3 fails | Log a warning; the section-edit suggestions in the summary are still printed. |
| `letter_target_path` collides with an existing file | Back up with `<target>.<timestamp>.bak` before overwriting. Never silently lose a prior letter. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure state writes + transcript output.
- Does **not** commit to git. OMCR leaves git out of the rebuttal flow. Future versions may add a `--commit` flag.
- Does **not** push to Overleaf or any remote. Manuscript-scaffold owns push flows.
- Does **not** re-dispatch any comment. The user re-runs the engine after acting on the summary.
- Does **not** auto-run `/iterate-revision` on edited sections. It only **suggests** the user run it. Engines are leaves (Phase 2 decision §5).
- Does **not** modify the rebuttal letter content. Whatever phase 04 rendered is what gets written.
- Does **not** retry on durable-write failure. One shot per artifact. The fallbacks (transcript print, project-root letter) preserve the work but the user must move them into place manually if the primary write failed.
