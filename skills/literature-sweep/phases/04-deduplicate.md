# Phase 4 — Deduplicate

Merge the per-batch curator outputs from phase 03, dedupe across batches by DOI, score-and-sort the merged list, and trim to `n_requested` survivors. The result is the list of entries phase 05 will verify and phase 06 will (for those that pass verification) write to disk.

## Inputs (from phase 03)

| Name | Source | Purpose |
|---|---|---|
| `topic`, `n_requested`, `depth`, `parallel`, `bib_file`, `summary_file`, `citations_state` | flows from phase 02/03 | Threaded through unchanged. |
| `batch_outputs` | phase 03 | List of dispatch-result dicts; `.parsed` is the curator's list of `{doi, citekey, bibtex, csv_row, relevance_score, relevance_reason}` objects. |
| `depth_outputs` | phase 03 (deep only) | List of `{doi, methodology, key_findings}` dicts, already merged into `csv_row` in phase 03 step 5. Re-checked here against the merged list. |
| `probe_failures`, `notes` | flows from phase 02/03 | Updated by this phase if dedupe rejects edge cases. |
| `already_in_bib_count` | phase 02 | Carried for the phase 06 summary. |

## Step 1 — Flatten `batch_outputs` into a single list

Concatenate all `.parsed` lists from `batch_outputs`. Drop any entry where:

- `.parsed` itself was null (the dispatch did not parse) — those batches were already counted in `notes` by phase 03.
- An individual entry within a `.parsed` list lacks both `doi` and `citekey` — un-anchorable, would only confuse downstream.
- An individual entry has an empty / null `bibtex` field — phase 06 cannot write nothing.

Each surviving entry is one **provisional record**:

```jsonc
{
  "doi":              "<lowercase DOI>",
  "citekey":          "<curator-assigned citekey>",
  "bibtex":           "@article{...}",
  "csv_row":          { ...curator-filled CSV row dict... },
  "relevance_score":  <float 0..1>,
  "relevance_reason": "<one sentence>"
}
```

Record the running total before any dedupe trim as `merged_in_count`. Phase 06 surfaces it in the user summary.

## Step 2 — Dedupe by DOI across batches

Within the flattened list, group entries by lowercase DOI. For each group of size ≥ 2:

1. Keep the entry with the highest `relevance_score`.
2. On ties: keep the one whose `csv_row.paper_says` is longest (proxy for "the curator wrote a richer summary for this one"). On ties there: keep the first by batch index.
3. Drop the rest. Increment `cross_batch_dups_count`.

This duplication can happen even though phase 02 deduped the candidate input list: when `--parallel > 1`, two curators may still produce slightly different citekeys for the same DOI if the input was *almost* duplicated (e.g., one source reported the DOI with case variation that slipped through phase 02). The DOI-grouping here is the authoritative dedupe.

If the surviving entry has a `citekey` that collides (case-insensitive) with another *kept* entry's citekey, append a single-letter suffix (`smith2024manifoldA`, then `smith2024manifoldB`, ...). The BibTeX entry's key inside the `bibtex` string must also be rewritten to match — search-and-replace the old citekey for the new one in the `bibtex` string.

## Step 3 — Cross-sweep dedupe against `citations.json.verified`

For each remaining entry, check whether its DOI is already in `citations_state.verified` (a list of `{key, doi, metadata_source, verified_at}` objects from prior sweeps).

If the DOI matches an existing `verified` record:

- The candidate is **not new**. It may still need to be written to `references.bib` if the user hand-deleted the BibTeX entry between sweeps, but phase 05 will discover that by re-running `verify-citation` and phase 06 will idempotent-append (no-op if the citekey already exists in `bib_file`).
- Keep the entry in the survivor list but flag it with `previously_verified: true`. Phase 06 will use this flag to mark `verify_status` as `PASS (re-verified)` for the CSV row and to avoid re-counting the entry as "new" in the run summary.

If the DOI does not match: leave the entry as-is (default `previously_verified: false`).

## Step 4 — Score and sort

The relevance score from the curator is the primary signal. Apply a few light tiebreakers:

- Primary key: `relevance_score` descending.
- Tiebreaker 1: `previously_verified == false` first (favor *new* entries when scores tie — re-adding already-known papers is lower marginal value).
- Tiebreaker 2: `csv_row.year` descending (favor recent).
- Tiebreaker 3: `csv_row.venue` non-empty before empty (proxy for "we know where it was published").
- Tiebreaker 4: stable original order (deterministic).

Apply the sort. The list is now in priority order for trimming.

## Step 5 — Trim to `n_requested`

If the sorted list has more than `n_requested` entries, keep the top `n_requested` and drop the rest. Record `trimmed_count = (merged_in_count - cross_batch_dups_count) - len(kept)` — the number of valid candidates dropped purely to hit the target N.

If the list has fewer than `n_requested` entries, keep all of them. Phase 06 will report the realized count as `n_returned` (possibly less than `n_requested`).

Important: this trim is **before verification**, so the engine still has the verify gate to absorb. Phase 05 may reject some of these survivors; the final `n_returned` may be smaller than the trimmed count. This is the locked behavior — we do not "top up" the list after verify failures. Per Phase 2 decision §1, the engine does not retry in any form within a run; the user re-runs if recall is too low.

## Step 6 — Hand off to phase 05

Pass forward to phase 05:

- All threaded fields from earlier phases (`topic`, `n_requested`, `depth`, `parallel`, `bib_file`, `summary_file`, `citations_state`, `probe_failures`, `already_in_bib_count`).
- `survivors` — the sorted, trimmed list of provisional records from step 5. Each has `previously_verified` set (true/false).
- `merged_in_count`, `cross_batch_dups_count`, `trimmed_count` — counters for the phase 06 summary.
- `notes` — updated with any per-record warnings emitted in this phase (rare).

## Failure modes

| Condition | Behavior |
|---|---|
| `batch_outputs` empty (phase 03 had no candidates) | `survivors = []`. Pass through. Phase 05 / 06 handle the empty case. |
| All batch outputs un-parseable | Same as above — empty survivor list. Phase 06 reports the cause from `notes`. |
| Two entries with identical DOI and identical relevance_score and identical `paper_says` length | Keep the first by batch index (deterministic). |
| Citekey collision after suffix exhausts A–Z (26 collisions) | Extremely unlikely; if hit, fall back to `<citekey>-<doi-tail-6-chars>`. Log a warning. |
| `citations.json.verified` malformed (e.g., entries missing `doi`) | Skip the malformed entries in the dedupe set; do not abort. Log: `"literature-sweep: citations.json.verified has <N> malformed entries — ignoring them for dedupe."` |
| Trim drops more than 60% of the merged input | Warn in `notes`: `"trim_high: <K> of <M> merged entries dropped to hit --n; consider re-running with a larger --n if recall matters more than precision."` |

## What this phase does NOT do

- Does **not** call any subagent. Pure in-memory list manipulation.
- Does **not** call `verify-citation`. The verify gate is phase 05.
- Does **not** write to disk. Phase 06 owns all writes.
- Does **not** consult `bib_file` again — phase 02 already pre-deduped against it. Re-reading here would duplicate effort and risk drift if the user hand-edited the file between phases.
- Does **not** rewrite the curator's `paper_says` / `bucket` / `our_use` columns. Curator output is authoritative; this phase only chooses *which* curator outputs survive.
- Does **not** preserve dropped entries for later recovery. Once trimmed, an entry is gone for the run. The user re-runs with a larger `--n` to see them.
