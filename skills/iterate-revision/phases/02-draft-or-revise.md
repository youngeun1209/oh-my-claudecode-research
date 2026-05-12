# Phase 2 — Draft or revise

Invoke `@paper-writer` to produce or revise the section's prose. This phase runs once per loop iteration. The choice between DRAFT and REVISE mode is decided per-iter — phase 01 hands in the starting iter count, and the loop primitive bumps it for subsequent runs.

This phase is the first half of each loop iteration. The second half is phase 03 (review). The orchestrate `loop` primitive at [`../../orchestrate/phases/04-loop.md`](../../orchestrate/phases/04-loop.md) sequences them.

## Inputs (from phase 01 or the loop)

| Name | Source | Purpose |
|---|---|---|
| `section_name` | phase 01 | Key in `paper.json.sections`. |
| `section_path` | phase 01 | File on disk. |
| `section_ext` | phase 01 | `tex` / `md` / `txt`. |
| `venue` | phase 01 | Reviewer + writer use the same venue label. |
| `current_iter` | loop primitive | 0 for the very first dispatch; incremented by the loop after each phase 04. |
| `max_iter` | phase 01 | Surfaced to the writer brief so it knows the budget. |
| `paper_state` | phase 01 | Parsed `paper.json` dict (hypothesis, title, manuscript_root, other sections). |

## Step 1 — Mode selection

Read the section file's current content (just the bytes — don't try to parse LaTeX).

```
if current_iter == 0 AND section file content is empty (whitespace only, ignoring comments):
    mode = DRAFT
else:
    mode = REVISE
```

The "ignoring comments" rule:
- For `.tex`: strip lines whose first non-whitespace character is `%`.
- For `.md`: no comment stripping (markdown has no first-class comments).
- For `.txt`: no comment stripping.

If after stripping the file is empty, treat it as empty.

The iter-counter and the file-content check together prevent two failure modes:
- iter 0 on a non-empty file (writer would clobber existing content) → forces REVISE.
- iter ≥ 1 on a somehow-empty file (file deleted between runs) → still treated as REVISE, so the writer is told the file went empty as part of the brief.

Record `mode` for the dispatch step.

## Step 2 — Resolve the outline

The writer brief needs an outline. Resolution order (first non-null wins):

1. `paper_state.sections[section_name].outline` if non-null.
2. The file `<paper_state.manuscript_root>/outline.md` if it exists. Read its full content.
3. The literal string `"(no outline provided — infer from the hypothesis and surrounding sections)"`.

Resolution 2 is the fallback referenced by the schema's `outline: null` semantics. Do not invent an outline; use one of these three sources.

## Step 3 — Resolve the length target

Length guidance for the writer brief (in words unless noted):

| Section | Default | Venue note |
|---|---|---|
| `abstract` | 150–250 | Many venues cap at 150 (Nature) or 250 (NeurIPS); pass the venue-specific cap if known. |
| `introduction` | 600–900 | Longer for review-heavy venues, shorter for letters. |
| `methods` | 800–1500 | Some venues move detail to supplementary. |
| `results` | 700–1200 | Tracks the number of figures. |
| `discussion` | 600–1000 | Some venues merge with Results. |
| other | "match the section's role in the manuscript" | — |

If `## Research stack` defines per-section caps (future field, currently unused), prefer those. Phase 1 ships with the defaults above. Pass the range as a hint; do not enforce it post-hoc.

## Step 4a — Build the DRAFT brief

If `mode == DRAFT`:

Build a `task_brief` string with this shape (substitute the angle-bracketed variables):

```
Draft the <section_name> section for "<paper_state.title or 'untitled manuscript'>",
target venue <venue>.

Hypothesis: <paper_state.hypothesis or "(unspecified)">.

Outline / scope:
<resolved outline from step 2>

Length target: <range from step 3> words.

Already-drafted sections (read for cross-reference; do NOT edit):
  <list of paper_state.sections[k].path for k where status in {drafted, revising, approved} and k != section_name>

Conventions:
- Use \citep{...} placeholders for citations. If no citekey is known yet,
  write [CITE: <one-line claim>] — @literature-curator will resolve later.
- Use \ref{fig:<label>} for figure references. Do not invent figure files.
- Do not edit main.tex or any non-section file.

Output: the section prose only. No metadata, no commentary, no preamble.
Begin with the first sentence of the section body.
```

## Step 4b — Build the REVISE brief

If `mode == REVISE`:

1. Look up the last review for this section. Read `reviews.json` via [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = reviews`. Filter `runs` by `section == section_name`. Sort descending by `ended` (or `started` if `ended` is missing). Take the first entry.

   If no prior review exists (e.g., iter 0 on a non-empty file → mode is REVISE but no review history yet), build the brief without an issues list (see "no-prior-review subcase" below).

2. Build the issues block from the last review's `issues` array. List only `critical | major | minor | nit` (no other severities exist). Render each as:
   ```
   [<severity>] <location>: <text>
   ```
   Sort `critical` first, then `major`, then `minor`, then `nit`.

3. Read the current section file's full content into `current_content`.

4. Build the `task_brief`:

   ```
   Revise the <section_name> section of "<paper_state.title or 'untitled manuscript'>"
   for target venue <venue>.

   Hypothesis: <paper_state.hypothesis or "(unspecified)">.

   Issues raised by the reviewer in iter <last_review.iter>:
   <issues block from step 2>

   Revision rules:
   - Fix every critical and major issue. Address minors where doing so does not
     require disproportionate rewrites; ignore nits unless trivially addressable.
   - Keep changes minimal. Do not rewrite text that the reviewer did not flag.
   - Do not introduce new citations beyond resolving [CITE:] placeholders for
     flagged missing-citation issues.
   - Preserve the section's LaTeX framing (\section{...}, \label{...}, \ref{...},
     environment blocks). Only the prose body changes.

   Current section content:
   <current_content>

   Output: the full revised section prose. No commentary, no diff markers,
   no preamble — return the section as it should appear on disk.
   ```

**No-prior-review subcase.** If REVISE mode was selected but no prior review exists for this section (the file had content but was never reviewed), omit the issues block and the `Revision rules` first bullet about "fix every critical/major"; otherwise the brief is the same shape. The writer effectively does a clean-up pass.

## Step 5 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":     "paper-writer",
  "task_brief":  <the brief built in step 4a or 4b>,
  "state_slice": {
    "title":        <paper_state.title>,
    "venue":        <venue>,
    "hypothesis":   <paper_state.hypothesis>,
    "section":      {
      "name":   <section_name>,
      "path":   <section_path>,
      "status": <paper_state.sections[section_name].status>,
      "iter":   <current_iter>,
      "outline": <resolved outline from step 2 — string, not the field value>
    },
    "manuscript_root": <paper_state.manuscript_root>
  },
  "expected_output_schema": null
}
```

Note: `expected_output_schema` is `null` — the writer returns free prose, not JSON. Phase 03 (reviewer) is where structured output matters.

The dispatch returns:
```jsonc
{
  "output":    "<the writer's prose>",
  "persona":   "paper-writer",
  "timestamp": "..."
}
```

## Step 6 — Write the prose to disk

Decide the write strategy:

- **DRAFT mode AND file is empty** (step 1 saw zero non-comment content) → use the `Write` tool with the dispatch output as the full file content. If the file had comment-only framing (e.g., a `% TODO` header in a `.tex` stub), preserve it by prepending those lines before the new prose.
- **REVISE mode, OR DRAFT mode with non-empty framing** → use the `Edit` tool to replace the prose body. The body is everything between the section's framing (e.g., between `\section{Results}` and the end-of-section marker for `.tex`; for `.md`, between the `# Heading` line and the next sibling heading; for `.txt`, the full content).

If you cannot identify the framing boundary unambiguously (e.g., the section has no `\section{...}` or heading), fall back to `Write` on the full file, but log a warning:
```
iterate-revision: <section_path> has no clear section framing. Overwriting the full file.
This is safe for sections in their own files, but verify nothing important was lost.
```

**Empty-output handling.** If the writer's `output` is empty or whitespace-only:
- Do **not** clobber the file. Leave the previous content on disk.
- Record an `iter_outputs` entry with `parse_error: "writer returned empty prose"` so phase 03 can decide whether to skip its dispatch.
- Phase 04's verdict rule will see the empty-output flag through phase 03's issues list (phase 03 fabricates a single `major` issue in this case — see phase 03 step "Empty input from phase 02").

## Step 7 — Update `paper.json`

After a successful write:

- `paper_state.sections[section_name].iter = current_iter + 1`
- `paper_state.sections[section_name].status = "revising"` (always — both DRAFT and REVISE end in `revising` until phase 04 decides otherwise)
- `paper_state.last_updated = <UTC ISO-8601 now>`

Write `paper.json` back atomically (tmp + rename) per [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) "Atomicity".

## Output to phase 03

Pass forward:
- `section_name`, `section_path`, `venue` (unchanged)
- `new_iter` (the value just written; `current_iter + 1`)
- `writer_output` (the raw prose returned by the dispatch, for logging only — phase 03 reads the file from disk to ensure on-disk + in-memory parity)
- `dispatch_meta` (the timestamp + any parse-error flag from step 6)

## Failure modes

| Condition | Behavior |
|---|---|
| Outline resolution all three sources empty | Use the literal-string fallback (step 2, option 3). Do not abort — the writer can sometimes infer. |
| `reviews.json` read fails in REVISE mode | Bubble the orchestrate state-read error. The loop primitive will catch and BLOCKED. |
| Dispatch returns empty prose | See "Empty-output handling" in step 6. Do not write; let phase 03 catch it. |
| Edit-tool framing-boundary ambiguous | Fall back to Write on the full file; log a warning. Continue. |
| Filesystem write fails | Bubble the OS error; loop primitive emits BLOCKED. |

## What this phase does NOT do

- Does **not** invoke `@reviewer`. That is phase 03's job.
- Does **not** compute a verdict. Phase 04 does that based on phase 03's issues list.
- Does **not** pass prior-iteration history to the writer beyond "the most recent review" (Phase 1 decision Q1).
- Does **not** edit `main.tex`, `references.bib`, or any non-section file.
- Does **not** insert `[TBD: ...]` markers. Phase 01 already refused to run if they were present.
