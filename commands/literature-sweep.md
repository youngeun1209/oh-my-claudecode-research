---
description: Find, summarize, and verify N papers on a topic. Parallel-dispatch engine across `@literature-curator` instances; only verified entries enter the BibTeX file.
---

# /literature-sweep

Dispatcher. Read [`skills/literature-sweep/SKILL.md`](../skills/literature-sweep/SKILL.md) and follow it exactly.

Arguments: `$ARGUMENTS`

## Signature

```
/literature-sweep <topic> [--n N] [--depth basic|deep] [--source crossref|openalex|both] [--parallel P]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--n` | `20` | Target number of verified entries. The engine pulls a candidate list of `3 * N` from the metadata sources, then dedupes and verifies down toward `N`. The final count may be less than `N` if verification rejects entries. |
| `--depth` | `basic` | `basic` extracts title/authors/year/venue/abstract per candidate. `deep` adds a second per-paper curator dispatch to extract methodology + key findings into the summary CSV (cost roughly doubles). |
| `--source` | `both` | Which metadata source to query. `crossref` = CrossRef only, `openalex` = OpenAlex only, `both` = union (deduped by DOI within the candidate list). |
| `--parallel` | `1` | Number of concurrent `@literature-curator` instances in phase 03. Clamped to `1 ≤ P ≤ 4` (Phase 2 decision §1). Values `> 4` are warned and clamped to `4`; values `< 1` abort. Default is sequential (`1`). |

## Examples

```
/literature-sweep "neural manifolds in motor cortex"
/literature-sweep "diffusion models for protein design" --n 30
/literature-sweep "frontoparietal working memory" --depth deep --parallel 4
/literature-sweep "transformer attention sparsity" --source crossref --n 15
```

## What this engine produces

- New verified entries appended to `references.bib` (path from `## Research stack` block or `paper.json`).
- New rows appended to the summary CSV (default `references.csv`) — `citekey | authors | year | title | venue | doi | bucket | our_use | paper_says | cited_sections | verified_on | verify_status`. Human-curated columns left blank for the curator to fill on a later pass.
- `citations.json.last_sweep` populated with `{topic, n_requested, n_returned, rejected, timestamp, notes}`.
- One `phase: "summary"` line appended to `.claude/omcr-state/_run-log.jsonl`.

## What this engine does NOT do

- Does not invent citations. Every entry passes the `verify-citation` skill before landing in `references.bib` — unverified candidates land in `citations.json.last_sweep.rejected` for user review.
- Does not call another slash command (engines are leaves — Phase 2 decision §5).
- Does not commit to git. Run `/sync` afterward if you want a snapshot commit.
- Does not write manuscript prose. The curator returns BibTeX + summary CSV rows only.
