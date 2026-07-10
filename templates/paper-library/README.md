# Paper library — reading & reference notes

The reading library the [`paper-ingest`](../../skills/paper-ingest/) skill writes into.
This is the **reading/notes layer** — distinct from the manuscript's `references.bib`
([`literature-curator`](../../agents/literature-curator.md) owns that). A paper can be
read and recorded here without ever being cited in the manuscript.

`/start-research` and `paper-ingest` copy this scaffold into your project's
**Paper library dir** (`## Research stack` key `Paper library dir`, env
`PAPER_LIBRARY_DIR`, default `docs/papers/`).

## Two-folder model (do not confuse the two)

| Path | Role | Written for |
|---|---|---|
| `bibliographic-management/<file>.md` | **Paper record** — project-agnostic summary: what it is, claims, method, result, main figure | **every** paper you ingest |
| `<library root>/<file>.md` | **Project usage** — how *your* project cites/uses it; links back to the record | **relevant** papers only |
| `bibliographic-management/index.csv` | flat index of **all** ingested papers | — |
| `bibliographic-management/figs/` | cropped main figures embedded in records | — |

The manuscript `references.bib` is a **separate** surface — do not write BibTeX here.

## Conventions

- **Filename:** `YYYY-firstauthor-keyword.md`, lowercase, hyphen (e.g. `2022-smith-graph-attention.md`).
- **bibkey:** `firstauthorYYYY` (e.g. `smith2022`) — the join key across both files + `index.csv`.
- **Status:** `to-read | skimmed | read`.
- **Buckets:** a small tag vocabulary that groups your reading by theme. Define your own
  in the project `## Research stack` block under `Paper buckets:` (comma-separated), e.g.
  `Paper buckets: core-method, baselines, datasets, related-theory`. If unset, `paper-ingest`
  uses a free-form one-word tag. Buckets are a project choice — no default vocabulary ships here.

## index.csv columns

`bibkey, year, first_author, title, venue, doi, bucket, status, relevance, in_project, pdf, figure, added_on`

Managed idempotently by `paper-ingest`'s `update_index.py` (keyed on `bibkey`; re-running
updates the row in place). Missing fields are stored as `—`.
