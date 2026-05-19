# Phase 6 — Finalize

Write the verified entries to `references.bib` and the summary CSV. Populate the `citations.json.last_sweep` block with topic, counts, rejected list, timestamp, and any notes. Append one `phase: "summary"` line to `.omx/state/omxr/_run-log.jsonl`. Render the user-facing summary.

This phase is the only phase that mutates files on disk. Everything from phase 01 through phase 05 was assembled in-memory.

## Inputs (from phase 05)

| Name | Source | Purpose |
|---|---|---|
| `topic`, `n_requested`, `depth`, `parallel`, `bib_file`, `summary_file`, `citations_state`, `probe_failures`, `already_in_bib_count`, `merged_in_count`, `cross_batch_dups_count`, `trimmed_count`, `notes` | flows through phases 01–05 | Carried for the summary block and on-disk record. |
| `verified_entries` | phase 05 | Records that passed verify-citation; will be appended to `references.bib` + CSV. Includes `verified_at` stamps. |
| `rejected_entries` | phase 05 | Records that failed verification; will be recorded in `citations.json.last_sweep.rejected`. |
| `verify_pass_count`, `verify_reject_count`, `verify_status_counts` | phase 05 | For the user summary. |

The loop primitive's `run_id`, `started`, and `ended` (UTC ISO-8601) are also available from the trivial loop invocation set up in the engine SKILL.md `## Composition` section.

## Step 1 — Append verified entries to `references.bib`

If `bib_file` does not exist, create it with a single trailing newline. If it exists, read its content into memory to:

- Detect the file's existing trailing-whitespace pattern (one newline, two newlines, none) — preserve it before appending.
- Build a set of citekeys already present (regex on `@\w+\s*\{\s*([^,]+),`) so an idempotent re-run does not double-add.

For each entry in `verified_entries`:

- If the entry's `citekey` is already in the existing-citekeys set: skip the BibTeX append for that entry. (It will still get its CSV row updated in step 2 — `verify_status` and `verified_on` are useful to refresh.)
- Otherwise: append the `bibtex` string to the file, preceded by one blank line. The `bibtex` string from the curator already contains the trailing `}` and a newline.

Use the standard atomic write pattern (write to `bib_file.tmp`, fsync, rename to `bib_file`) for the bibliography. The bib file is the single most important durable artifact of the run; never leave a half-written copy.

Track `bib_appended_count` (how many new entries were actually written) and `bib_skipped_count` (how many were skipped due to citekey-already-present).

## Step 2 — Append summary CSV rows

If `summary_file` does not exist:

- Create it with the canonical RFC 4180 header row. Use the column list from the curator's `csv_row` keys, with the canonical order from [`agents/literature-curator.md`](../../../agents/literature-curator.md):

  ```
  citekey,authors,year,title,venue,doi,bucket,our_use,paper_says,cited_sections,verified_on,verify_status
  ```

  If `depth == "deep"`, append two extra columns at the end: `methodology,key_findings`.

If it exists:

- Read the header row. Use that column list for new appends; do not rewrite the header. If a row's `csv_row` is missing a column (e.g., it was a basic-mode entry but the CSV file has the `deep`-extension columns from a prior run), emit empty strings for the missing columns. Conversely, if the row has extra columns the file doesn't have, drop the extras silently — the user can run an audit pass later to widen the header.
- Read every existing row's `citekey` into a set, similar to step 1, so the engine can refresh the row in place for `previously_verified` entries.

For each entry in `verified_entries`:

- If the entry's `citekey` already has a row in the CSV: **update** that row's `verified_on` and `verify_status` columns in place (matches what verify-citation does in audit mode). Do not overwrite `bucket`, `our_use`, `paper_says`, or `cited_sections` — those are user-curated. The summary table's 1:1 correspondence with the BibTeX file is owned by `@literature-curator`; this engine only refreshes the verification fields on re-encounter.
- Otherwise: append a new row built from `csv_row`, with values RFC-4180-quoted (wrap in `"..."` and escape inner `"` as `""` if the value contains `,`, `"`, or `\n`).

Use the same atomic write pattern (`summary_file.tmp` → rename).

Track `csv_appended_count` and `csv_refreshed_count`.

## Step 3 — Update `citations.json`

Re-read `citations.json` via [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = citations`. (Re-reading rather than using the in-memory `citations_state` from phase 01 guards against the unlikely case that a concurrent process touched the file — even though serial execution is the current assumption, the atomic pattern costs almost nothing.)

Apply two updates:

### 3a — Append to `citations.json.verified`

For each entry in `verified_entries` that is *not* `previously_verified`, append one record to the `verified` array:

```jsonc
{
  "key":              "<citekey>",
  "doi":              "<lowercase DOI>",
  "metadata_source":  "<crossref | openalex | both>",
  "verified_at":      "<verified_at from phase 05>"
}
```

`metadata_source` is the curator's `csv_row` source attribution if present, else `"crossref"` if verify-citation's `crossref.found` was true, else `"openalex"` if `openalex.found` was true, else `"both"` as a generic fallback.

If `previously_verified == true`, do not append a new record — but update the existing record's `verified_at` to the new timestamp.

### 3b — Set `citations.json.last_sweep`

Overwrite the `last_sweep` field with the new run's summary:

```jsonc
{
  "topic":        "<topic>",
  "n_requested":  <n_requested>,
  "n_returned":   <verify_pass_count>,
  "rejected": [
    {
      "doi":    "<doi>",
      "reason": "<reason from phase 05>"
    },
    ...
  ],
  "timestamp":    "<UTC ISO-8601 now>",
  "notes":        [ <any strings accumulated in notes across phases> ]
}
```

Each `rejected` record collapses the phase 05 `rejected_entries` list to just `{doi, reason}` — the user can read the reason and rescue manually if they want.

`notes` includes every warning the engine accumulated:

- `probe_failures` rendered as `"<source> probe failed (<reason>)"` for each.
- Parallel-failure warnings from phase 03 (`"parallel batch <i> failed; fell back to sequential"`).
- Verifier-level warnings from phase 05 (`"verify-citation crashed on <doi>; treated as NOT_VERIFIED"`).
- Any miscellaneous warnings (high trim rate from phase 04, citekey-suffix-exhausted, etc.).

If `notes` is empty, write an empty array `[]`, not `null` — keeps the schema shape uniform for tooling.

Write `citations.json` back atomically. Same `*.tmp` + rename pattern.

## Step 4 — Append run summary to `_run-log.jsonl`

The orchestrate loop primitive already wrote `phase: "start"` and `phase: "end"` records for this run (via the trivial loop wrapping established in `SKILL.md`). Phase 06 adds one more line, `phase: "summary"`, so a JSONL reader can grep `phase == "summary" && engine == "literature-sweep"` to get a per-run summary table.

Append (atomic append, never overwrite):

```jsonc
{
  "run_id":              "<run_id>",
  "engine":              "literature-sweep",
  "phase":               "summary",
  "topic":               "<topic>",
  "n_requested":         <n_requested>,
  "n_returned":          <verify_pass_count>,
  "depth":               "<depth>",
  "parallel":            <parallel>,
  "sources":             [ <sources actually queried after phase 01/02 drops> ],
  "candidates_searched": <candidate_budget from phase 02>,
  "candidates_merged":   <merged_in_count>,
  "cross_batch_dups":    <cross_batch_dups_count>,
  "trimmed_to_n":        <trimmed_count>,
  "already_in_bib":      <already_in_bib_count>,
  "verify_pass":         <verify_pass_count>,
  "verify_reject":       <verify_reject_count>,
  "verify_breakdown":    <verify_status_counts dict>,
  "bib_appended":        <bib_appended_count>,
  "bib_skipped":         <bib_skipped_count>,
  "csv_appended":        <csv_appended_count>,
  "csv_refreshed":       <csv_refreshed_count>,
  "notes_count":         <len(notes)>,
  "summary_at":          "<UTC ISO-8601 now>"
}
```

Use the same write semantics as the orchestrate loop primitive's append (open in append mode, write one line + `\n`, flush + fsync). If the append fails, log a warning and continue — the user already has the summary in the transcript and `citations.json.last_sweep` on disk is the canonical durable record.

## Step 5 — Render the user-facing summary

Print this block to the transcript:

```
Topic:              <topic>
Requested:          <n_requested>   |   Returned: <verify_pass_count>
Depth:              <depth>         |   Parallel: <parallel>
Sources:            <comma-joined sources actually queried>
Candidates pulled:  <candidate_budget>     (3 * n_requested)
After dedupe:       <merged_in_count>      (cross-batch dups: <cross_batch_dups_count>)
After trim:         <merged_in_count - cross_batch_dups_count - trimmed_count>
Verify breakdown:   PASS=<...>  MISMATCH=<...>  NOT_FOUND=<...>  NOT_VERIFIED=<...>
references.bib:     +<bib_appended_count> new, <bib_skipped_count> already present
<summary CSV>:      +<csv_appended_count> new, <csv_refreshed_count> refreshed
Already in bib:     <already_in_bib_count>      (skipped at search-time)
Run id:             <run_id>
```

Then a verdict block:

### When `verify_pass_count >= n_requested * 0.7` (good return)

```
Sweep complete. <verify_pass_count> verified entries added to <bib_file>.

Suggested next:
  Review the rejected list (citations.json.last_sweep.rejected) for any
  recoverable entries (typos, transient network failures).
  Open <summary_file> and fill the `bucket` / `our_use` columns where supervisor
  has decided how each paper fits the manuscript.
  $sync                          (snapshot project state)
```

### When `0 < verify_pass_count < n_requested * 0.7` (low return)

```
Sweep complete with low recall: <verify_pass_count> / <n_requested> verified.

This usually means:
  - The topic phrasing was too narrow — try a broader query.
  - One metadata source was rate-limiting — re-run with --source <other>.
  - The field genuinely doesn't have <n_requested> indexed papers — adjust --n.

Review citations.json.last_sweep.rejected for entries to rescue manually.
Consider re-running with --parallel 1 if you used --parallel > 1.
```

### When `verify_pass_count == 0`

```
Sweep produced no verified entries.

Cause (from notes):
  <bulleted list of the strings in `notes`>

No writes were made to <bib_file> or <summary_file>. The empty result is
recorded in citations.json.last_sweep for telemetry.

To debug:
  - Re-run with --parallel 1 if parallel was used.
  - Confirm network reachability: try $literature-sweep with --source crossref
    only, then with --source openalex only.
  - Confirm the topic resolves something on https://search.crossref.org manually.
```

If `notes` is non-empty in any verdict branch, render the notes list under a `Notes:` heading at the end of the block. One bullet per note.

## Step 6 — No git commit, no push

OMXR does **not** commit or push on behalf of the user from this phase. The bibliography is durable, citations.json is durable, the CSV is durable — those writes are the deliverable. If the user wants a snapshot commit, they run `$sync` next.

A future flag (`--commit` or `--push`) is a future-version concern. The pattern matches `iterate-revision` phase 05 step 5 and `manuscript-scaffold` phase 04 prompt-to-push convention.

## Failure modes

| Condition | Behavior |
|---|---|
| `bib_file` write fails mid-append | Atomic pattern means either the old file or the new file is on disk — never a half-written copy. Surface the OS error; the user re-runs after fixing permissions. |
| `summary_file` write fails | Same atomic guarantee. The bibliography may have been written successfully in step 1; this is acceptable — the user re-runs and step 2's idempotent header check + citekey-row check will not duplicate. |
| `citations.json` write fails | The on-disk citations.json reflects the pre-phase-06 state (verified array may be missing this run's additions; last_sweep may be stale). Surface the OS error; the user re-runs. |
| `_run-log.jsonl` append fails | Log a warning. Do not abort. The user has already seen the transcript summary; citations.json.last_sweep is the canonical record. |
| `verified_entries` empty AND `rejected_entries` empty AND `notes` empty | Should not happen; either the sources were unreachable (notes populated) or there were no candidates (notes populated by phase 02 step 4). If it does happen, render: `"Sweep complete with zero candidates and zero notes — please file an issue against oh-my-codex-research with the run_id above."` |
| Disk full on any write | All atomic writes will fail their rename step; the file content stays at the previous version. Surface the OS error and continue with the remaining writes. The user re-runs after freeing space. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure I/O + summary rendering.
- Does **not** re-verify any entry. Phase 05 already gated.
- Does **not** rewrite the user-curated CSV columns (`bucket`, `our_use`, `paper_says` on existing rows, `cited_sections`). Only verification columns are touched on refresh.
- Does **not** trim or re-score. Phase 04 already did.
- Does **not** commit to git or push to a remote.
- Does **not** retry on write failure. One shot per file per run.
- Does **not** clear or rewrite older entries in `citations.json.verified`. Only appends new ones (and updates `verified_at` on previously_verified matches).
