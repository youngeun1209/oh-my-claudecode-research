# Phase 3 — Parallel read

Dispatch `@literature-curator` to summarize the candidate list. **This is the parallel-dispatch primitive demonstration.** When `parallel == 1` the engine issues one sequential dispatch per batch (the safe default, Phase 2 decision §1). When `parallel > 1` the engine issues `P` curator dispatches in a **single assistant message**, which Claude Code's Agent tool runs concurrently per the dispatch primitive's Agent-tool parallel-call pattern.

Each curator returns one BibTeX entry + one summary CSV row per paper in its assigned batch. The actual writes to `references.bib` and the CSV happen in phase 06 — phase 03 keeps everything in-memory so phase 04 can dedupe across batches and phase 05 can verify before anything lands on disk.

## Inputs (from phase 02)

| Name | Source | Purpose |
|---|---|---|
| `topic` | phase 02 | Inlined into each curator's task brief for relevance context. |
| `n_requested` | phase 02 | Surfaced to the curator so it knows the eventual target. |
| `depth` | phase 02 | `basic` → one dispatch per batch. `deep` → step 4 issues a second per-entry dispatch for methodology + findings. |
| `parallel` | phase 02 | Clamped 1–4 from phase 01. |
| `candidates` | phase 02 | Sorted, deduped list of candidate dicts. May be empty. |
| `bib_file` | phase 02 | Passed to the curator brief as context (so it can match the project's citekey convention). |
| `summary_file` | phase 02 | Same. |
| `citations_state` | phase 02 | Same — curator may reference existing `verified` entries to avoid suggesting near-duplicates within a batch. |
| `probe_failures` / `notes` | phase 02 | Threaded through; phase 06 records them. |

## Step 1 — Empty-candidates short-circuit

If `candidates` is empty (phase 02 step 4):

- Do **not** issue any dispatch.
- Set `batch_outputs = []`.
- Hand off to phase 04 with the empty result. Phase 04 will skip dedupe; phase 05 will skip verification; phase 06 will produce a clean empty-summary report.

## Step 2 — Partition candidates into `parallel` batches

Split `candidates` into `parallel` near-equal batches in candidate-list order:

- If `len(candidates) < parallel`, reduce `parallel` to `len(candidates)` for this run and warn:
  ```
  literature-sweep: --parallel <P> requested but only <K> candidates remain after dedupe.
  Running with --parallel <K> for this phase.
  ```
- Otherwise: batch sizes are `ceil(len(candidates) / parallel)` for the first `len(candidates) % parallel` batches and `floor(len(candidates) / parallel)` for the rest. (Equivalent to numpy-style array_split.)

Record the partitioning as `batches: List[List[Candidate]]`. `len(batches) == parallel` after the possible reduction.

## Step 3 — Build the curator task brief (per batch)

For each batch, build a `task_brief` string with this shape (substitute the angle-bracketed variables):

```
You are summarizing a batch of candidate papers for the bibliography sweep
on the topic:

  <topic>

The sweep targets <n_requested> verified entries. This batch contains <len(batch)>
candidates. For each candidate, return one BibTeX entry plus one CSV row.

Bibliography target file: <bib_file>
Summary CSV target file:  <summary_file>

Citekey convention: firstauthorYearShortword (lowercase first-author surname +
4-digit year + a one-word content keyword). Example: smith2024manifold.
If a citekey collides within the batch, append a letter suffix (smith2024manifoldA).

Candidates (already pre-deduped by DOI):

<for each candidate in batch, render:>

  --- candidate <i> of <K> ---
  doi:      <candidate.doi>
  title:    <candidate.title>
  authors:  <candidate.authors>
  year:     <candidate.year>
  venue:    <candidate.venue>
  type:     <candidate.type>
  source:   <candidate.source>
  abstract: <candidate.abstract truncated to 1500 chars, or "(no abstract)">

For each candidate, return one JSON object with this exact shape:

  {
    "doi":         "<lowercase DOI>",
    "citekey":     "<your assigned citekey>",
    "bibtex":      "@article{...}\n  ...\n}",     // a single full BibTeX entry
    "csv_row": {
      "citekey":        "<same as above>",
      "authors":        "<short form, e.g. 'Smith, Jones, Lee' or 'Smith et al.' for >3>",
      "year":           <int>,
      "title":          "<full title>",
      "venue":          "<journal / conference / preprint server>",
      "doi":            "<lowercase DOI>",
      "bucket":         "",                       // leave blank — user fills via supervisor
      "our_use":        "",                       // leave blank — user fills
      "paper_says":     "<one sentence paraphrase of the abstract>",
      "cited_sections": "",                       // leave blank
      "verified_on":    "",                       // phase 05 fills
      "verify_status":  ""                        // phase 05 fills
    },
    "relevance_score": <0.0 .. 1.0>,              // your judgment on topic match
    "relevance_reason": "<one sentence on why this paper is or isn't a strong match>"
  }

Output: a JSON array of these objects, one per candidate. No preamble, no
commentary, no trailing prose. If you cannot summarize a candidate (e.g. the
abstract is empty AND the title is uninformative), still emit an object with
"paper_says": "(could not summarize from metadata)" and "relevance_score": 0.0.

Do NOT fabricate citation metadata. The DOI, title, authors, year, venue, and
type fields are authoritative — copy them through unchanged. Only "paper_says",
"citekey", "relevance_score", and "relevance_reason" are your judgment fields.

Do NOT write any file. The engine writes references.bib and the CSV in phase 06
after verification; your job here is to produce the entries.
```

The expected_output_schema for the dispatch primitive is `[{doi, citekey, bibtex, csv_row, relevance_score, relevance_reason}, ...]` — a list of those objects. The dispatch primitive will best-effort parse this back into `parsed`.

## Step 4 — Dispatch the batches

### Case A — sequential (`parallel == 1`)

There is exactly one batch. Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) once with:

```jsonc
{
  "persona":    "literature-curator",
  "task_brief": <brief from step 3 for the single batch>,
  "state_slice": {
    "topic":          <topic>,
    "n_requested":    <n_requested>,
    "depth":          <depth>,
    "batch_index":    0,
    "batch_count":    1,
    "bib_file":       <bib_file>,
    "summary_file":   <summary_file>
  },
  "expected_output_schema": [
    { "doi": "...", "citekey": "...", "bibtex": "...", "csv_row": {}, "relevance_score": 0.0, "relevance_reason": "..." }
  ]
}
```

Collect the dispatch result into `batch_outputs = [result]`.

### Case B — parallel (`parallel > 1`)

Issue **all `parallel` dispatch calls in a single assistant message** — Claude Code's Agent tool runs subagents concurrently when multiple Agent-tool invocations appear in one message (this is the parallel-dispatch primitive described in phase 0 of the orchestrate skill).

Each call uses the same `persona: "literature-curator"` and `expected_output_schema` as Case A, but each one's `task_brief` is built for its specific batch and `state_slice.batch_index` is set to the batch's 0-based index.

Wait for all `parallel` calls to return. Collect their results into `batch_outputs` (a list of `parallel` dispatch-result dicts) in batch-index order.

### Parallel failure fallback (Phase 2 decision §1)

If any of the parallel dispatches errors (the dispatch primitive returns a non-null `parse_error`, or the Agent tool returns an error for that call):

1. **Do not retry the failed batch in parallel.**
2. **Do not abort the engine.**
3. Record the failure in `notes`:
   ```
   literature-sweep: parallel batch <i> failed (<reason>). Falling back to sequential for remaining work.
   ```
4. Re-dispatch the failed batch **sequentially**, after all the parallel calls have settled. Use the same `task_brief` built in step 3. If the sequential re-dispatch also errors, give up on that batch and record:
   ```
   literature-sweep: parallel batch <i> failed twice (parallel + sequential retry). Skipping the batch's <K> candidates; they will not appear in the final result.
   ```
   Drop the batch's candidates from consideration; phase 04 will see fewer survivors.

The fallback is one-shot — no further retries. The user can re-run with `--parallel 1` for a clean serial pass.

## Step 5 — Depth-deep extension (only when `depth == "deep"`)

If `depth == "deep"`, after step 4, issue one **additional** curator dispatch per *successful* candidate from step 4 to extract methodology + key findings. Brief:

```
You previously summarized this paper as part of a literature sweep on:

  <topic>

Now extract a longer summary for the literature summary CSV. The CSV already
has your one-sentence "paper_says". This dispatch adds two more sentences:

  methodology:  <one sentence on the methods — what was done, how, on what data>
  key_findings: <one sentence on the headline result — what the paper concludes>

Paper:
  doi:     <candidate.doi>
  title:   <candidate.title>
  authors: <candidate.authors>
  abstract: <candidate.abstract or "(none)">

Return one JSON object:

  {
    "doi":          "<lowercase DOI>",
    "methodology":  "<one sentence>",
    "key_findings": "<one sentence>"
  }

If the abstract is empty and you cannot infer methodology / findings from the
title alone, return both fields as "(insufficient information)".
```

Issue these dispatches in batches of `parallel` per the same Case A / Case B
shape as step 4. Merge each result into the corresponding candidate dict's
`csv_row` by adding two extra columns (`methodology`, `key_findings`). The CSV
header in phase 06 picks these up automatically because phase 06 derives the
column list from the in-memory row keys.

Deep-mode failures use the same fallback as step 4: parallel-error → sequential retry → drop if still failing. A dropped deep extraction leaves the candidate with its basic-mode `paper_says` intact (no `methodology` / `key_findings` columns added for that one row) and a note recorded.

## Step 6 — Hand off to phase 04

Pass forward to phase 04:

- All the inputs that flowed through phase 02 (unchanged)
- `batch_outputs` — list of dispatch-result dicts, one per batch, with `.parsed` holding the curator's list of candidate-objects
- `notes` (updated with any parallel-failure messages)
- `depth_outputs` (only if `depth == deep`) — list of `{doi, methodology, key_findings}` dicts merged in step 5

## Failure modes

| Condition | Behavior |
|---|---|
| Empty `candidates` from phase 02 | Skip dispatch entirely. Pass empty `batch_outputs` to phase 04. |
| One parallel batch errors | Re-dispatch that batch sequentially after the parallel set settles. If still fails, drop the batch and record in `notes`. |
| All parallel batches error | Each gets one sequential retry. If still failing, `batch_outputs` may end up empty; phase 04 sees no survivors; phase 06 records the outage. |
| Curator returns un-parseable output for a batch | Treat the batch as failed. Sequential retry. If still un-parseable, drop with a note: `"literature-sweep: batch <i> output not parseable as JSON array — dropping."` |
| Curator returns fewer rows than candidates in the batch | Accept what came back; the missing candidates are simply absent from `batch_outputs`. Phase 04's dedupe handles a smaller-than-expected list. |
| Curator returns more rows than candidates | Trim extras silently — the candidate list is authoritative. |
| Deep-mode dispatch errors out for one entry | Drop only that entry's deep extraction. Keep the basic-mode row. |

## What this phase does NOT do

- Does **not** write to `references.bib`, the CSV, or `citations.json`. All writes are phase 06's job.
- Does **not** verify any entry against CrossRef / OpenAlex. Verification is phase 05.
- Does **not** dedupe across batches. Phase 04 does that.
- Does **not** trim to `n_requested`. Phase 04 does that.
- Does **not** retry in parallel after a parallel failure. The fallback is sequential-only by design (Phase 2 decision §1).
- Does **not** invoke any persona other than `@literature-curator`.
- Does **not** issue more than two dispatch layers (the basic batch dispatch + the optional deep extension). No third pass.
