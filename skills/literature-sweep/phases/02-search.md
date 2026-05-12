# Phase 2 — Search

Query the metadata source(s) for the topic, build a deduped candidate list of up to `3 * n_requested` entries, and hand it to phase 03. No agent dispatch in this phase — the queries are direct HTTP calls via WebFetch.

## Inputs (from phase 01)

| Name | Source | Purpose |
|---|---|---|
| `topic` | phase 01 | The search query string. |
| `n_requested` | phase 01 | Target final count; this phase pulls `3 * n_requested` candidates. |
| `sources` | phase 01 | Filtered list — may be `["crossref"]`, `["openalex"]`, `["crossref", "openalex"]`, or empty if all probes failed. |
| `bib_file` | phase 01 | Read to dedupe candidates against existing entries (avoid re-adding what is already on disk). |
| `citations_state` | phase 01 | Parsed `citations.json`; the `verified` list is consulted for cross-sweep dedupe. |
| `probe_failures` | phase 01 | Pre-existing list of source names whose precheck failed; phase 02 may add more on a real-query failure. |

## Step 1 — Compute the candidate budget

`candidate_budget = 3 * n_requested`.

Rationale: empirically, dedupe + verify trims roughly 40–60% of the raw candidate list. Pulling `3 * N` gives the engine a buffer to still hit `N` survivors after phase 04 (dedupe) and phase 05 (verify).

If `sources` is empty (phase 01's probes all failed), skip steps 2 and 3 and produce an empty candidate list. Phase 03 will handle the empty input gracefully — it will not dispatch — and phase 06 will record the outage in `last_sweep.notes`.

Otherwise, split the budget across the active sources:

- One source active → that source gets the full `candidate_budget`.
- Two sources active → each source gets `candidate_budget / 2`, rounded up so the total ≥ `candidate_budget`. Slight over-pull is fine; phase 04 dedupes the merged list.

Record `per_source_budget` as an int per source.

## Step 2 — Query each source

For each source in `sources`, issue one search query using WebFetch. URL shapes:

### CrossRef

```
https://api.crossref.org/works?query=<URL-encoded topic>&rows=<per_source_budget>&select=DOI,title,author,issued,container-title,abstract,type
```

Optional polite-pool header: `User-Agent: omcr-literature-sweep/0.2 (mailto:<CITATION_VERIFY_EMAIL>)`. Email source: env var `CITATION_VERIFY_EMAIL`, else CLAUDE.md `## Research stack` field `CrossRef email`, else omit the parenthetical. Unset is acceptable; CrossRef still answers, just at the public rate.

Parse the JSON response. The candidate list is at `message.items`. Per item:

| Candidate field | Source path |
|---|---|
| `doi` | `DOI` (lowercase) |
| `title` | `title[0]` if list, else `title` as string. Strip LaTeX-escape artifacts (`\textit{...}` → `...`). |
| `authors` | join `author[].family + ", " + author[].given` (drop entries lacking `family`). |
| `year` | `issued.date-parts[0][0]` as int. |
| `venue` | `container-title[0]` if list, else `container-title`. |
| `abstract` | `abstract` if present; strip JATS-XML tags (`<jats:p>...</jats:p>` → `...`); else empty string. |
| `type` | `type` (used in scoring — `journal-article` preferred over `posted-content` / `proceedings-article`). |
| `source` | literal `"crossref"`. |

### OpenAlex

```
https://api.openalex.org/works?search=<URL-encoded topic>&per_page=<per_source_budget>&select=doi,title,authorships,publication_year,host_venue,abstract_inverted_index,type
```

OpenAlex returns abstracts as an inverted index (`{"word": [positions]}`); reconstruct the abstract by sorting positions and joining words, or leave as the inverted form if reconstruction is non-trivial — phase 03's curator can handle either, but reconstructed prose is preferred.

Parse the JSON response. The candidate list is at `results`. Per item:

| Candidate field | Source path |
|---|---|
| `doi` | `doi` — strip the `https://doi.org/` prefix if present, lowercase. |
| `title` | `title`. |
| `authors` | join `authorships[].author.display_name`. |
| `year` | `publication_year` as int. |
| `venue` | `host_venue.display_name` if present. |
| `abstract` | reconstruct from `abstract_inverted_index`; fall back to empty if reconstruction errors. |
| `type` | `type` (e.g., `journal-article`, `posted-content`). |
| `source` | literal `"openalex"`. |

### On query failure

If a single source's query errors (timeout, 5xx, malformed JSON, etc.):

1. Add the source to `probe_failures` with a one-line reason.
2. Log:
   ```
   literature-sweep: <source> query failed (<reason>) — proceeding with remaining sources.
   ```
3. Continue with the other sources.

If **all** active sources error, do not abort — produce an empty candidate list and let phase 06 record the outage in `last_sweep.notes`. The user sees a clean failure summary instead of a stack trace.

Do **not** retry inside the phase. The user can re-run.

## Step 3 — Merge and dedupe by DOI within the candidate list

Concatenate the per-source candidate lists. Dedupe by DOI (case-insensitive):

- For each DOI, prefer the first occurrence. Note in the dropped entries' record which source had it (for telemetry only; not surfaced unless the run later goes wrong).
- Drop entries missing a DOI entirely — without a DOI, phase 05 cannot verify them; including them would only waste curator + verify cycles.

Optionally also dedupe against entries already in `bib_file` and `citations_state.verified`:

- Parse `bib_file` (if it exists) for `doi = {...}` fields. Build a set of lowercase DOIs.
- Pull `doi` fields from `citations_state.verified[].doi` into the same set.
- Drop any candidate whose DOI is in this set. Increment a `already_in_bib_count` for the phase 06 summary.

Sort the surviving candidates by a coarse relevance score (used as a tiebreaker in phase 04):

- `+3` if `type == "journal-article"`.
- `+1` if `year >= current_year - 5` (recency bias for active topics; harmless for foundational ones because phase 04 keeps high-cite anchors via topic matching).
- `+2` if `abstract` is non-empty (lets the curator extract `paper_says` without a follow-up fetch).
- `+1` if `venue` is non-empty.
- `+0` otherwise.

Record this sorted list as `candidates`. Length is at most `candidate_budget`, may be far less if the queries returned little or if dedupe trimmed aggressively.

## Step 4 — Empty-list short-circuit

If `candidates` is empty after step 3:

- Do **not** abort. Hand the empty list to phase 03, which will skip its dispatch.
- Record the cause in a `notes` list (in-memory; phase 06 writes it to `last_sweep.notes`):
  - `"all sources unreachable"` if `probe_failures` covers every source.
  - `"no candidates returned after dedupe"` otherwise (the queries succeeded but matched only papers already in the bib).
- Continue.

This is the graceful empty-return path. Phase 06 will produce a clean summary (`n_returned: 0`) with the cause spelled out.

## Step 5 — Hand off to phase 03

Pass forward to phase 03:

- `topic`, `n_requested`, `depth`, `parallel`, `bib_file`, `summary_file`, `citations_state` (all unchanged from phase 01)
- `candidates` (the sorted, deduped list from step 3; may be empty)
- `probe_failures` (updated list from this phase)
- `already_in_bib_count` (int — for phase 06 telemetry)
- `notes` (list of warnings to surface in `last_sweep.notes` later)

## Failure modes

| Condition | Behavior |
|---|---|
| All sources unreachable (phase 01 reported empty `sources`, or all queries errored) | Empty candidate list. Continue. Phase 06 logs the outage. |
| One source unreachable | Drop that source. Continue with the others. Log to `notes`. |
| Source returns malformed JSON | Treat as a query failure for that source. Log. Continue. |
| Source returns valid but empty results (`message.items: []` / `results: []`) | Continue with whatever the other source returned. If both sources returned nothing, fall through to step 4. |
| `bib_file` exists but cannot be parsed | Warn (`bib_file unparseable — skipping pre-dedupe; phase 05 will still gate via DOI lookup`) and continue without the pre-dedupe. Do not abort. |
| Candidate count after dedupe < `n_requested` | Continue — the candidate list may still be enough after phase 05 verifies. Phase 06 reports the realized count. |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero `@literature-curator` dispatches in phase 02.
- Does **not** call the `verify-citation` skill. Verification is phase 05's job; phase 02 only assembles a candidate pool.
- Does **not** write to disk. All state is in-memory until phase 06.
- Does **not** fetch full PDFs. Metadata + abstract only.
- Does **not** rank candidates by anything beyond the coarse score above. Real relevance judgment lives in the curator's read in phase 03.
- Does **not** retry failed queries. One shot per source; the user re-runs.
