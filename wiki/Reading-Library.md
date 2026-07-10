# Reading Library — `paper-ingest`

The **reading library** is where papers you *read* are recorded — summaries, main figures, an
index — as distinct from the manuscript bibliography you *cite*. The `paper-ingest` skill
populates it; the scaffold ships in [`templates/paper-library/`](../templates/paper-library/).

> **Reading vs. citing.** `@literature-curator` owns the manuscript's `references.bib` +
> summary table (`verify-citation`-gated) — that is the *citation* layer. `paper-ingest` owns
> the *reading* layer: a paper can be read, summarized, and filed here without ever being cited,
> and most of your reading never makes it into the paper. Two surfaces, on purpose.

## Two-folder model

| Path (under `Paper library dir`) | Role | Written for | Template |
|---|---|---|---|
| `bibliographic-management/<file>.md` | **Paper record** — project-agnostic summary: what it is, claims, method, result, main figure | **every** paper you ingest | Template A |
| `<file>.md` (library root) | **Project usage** — how *your* project cites/uses it; links back to the record | **relevant** papers only | Template B |
| `bibliographic-management/index.csv` | flat index of **all** ingested papers | — | — |
| `bibliographic-management/figs/` | cropped main figures embedded in records | — | — |

The record answers "what is this paper?"; the usage note answers "why do *we* care?". Keeping
them apart means the record stays reusable across projects while the usage note carries your
argument-specific framing.

## Conventions

- **Filename:** `YYYY-firstauthor-keyword.md` (lowercase, hyphenated) — e.g. `2022-smith-graph-attention.md`.
- **bibkey:** `firstauthorYYYY` (e.g. `smith2022`) — the join key across both files + `index.csv`.
- **Status:** `to-read | skimmed | read`.
- **Buckets:** a small tag vocabulary grouping your reading by theme. Set `Paper buckets` in the
  `## Research stack` block (comma-separated) — e.g. `core-method, baselines, datasets`. If unset,
  `paper-ingest` uses a free-form one-word tag. **No default vocabulary ships** — buckets are a
  project choice (unlike the neuro preset's fixed set, the core is field-neutral).

## Configuration

Resolve order: env var → `## Research stack` block → default. See [Configuration](Configuration.md).

| Setting | `## Research stack` key | Env var | Default |
|---|---|---|---|
| Library root | `Paper library dir` | `PAPER_LIBRARY_DIR` | `docs/papers/` |
| Bucket vocabulary | `Paper buckets` | `PAPER_BUCKETS` | free-form |

## What `paper-ingest` does

1. **Resolve the input** — a PDF (poppler wrapper `pdf_to_assets.sh` extracts text + page renders), or a DOI/URL (metadata via the `verify-citation` skill — CrossRef + OpenAlex, no fabrication).
2. **Derive identifiers** — `bibkey`, filename, keyword.
3. **Write the record** (Template A) — one-line, key claims, method, result, key terms.
4. **Crop one main figure** (PDF only) — scout page renders, `--crop` the chosen region, embed under `## Main figure`. Reuses `cropfig`'s band heuristic when a plain region crop isn't clean.
5. **Upsert `index.csv`** — idempotent on `bibkey` via `update_index.py` (re-running updates in place).
6. **Judge relevance, then ask** — decide whether the paper bears on the project's narrative (from `CLAUDE.md` `## Project context`); report the verdict and **ask before** writing the project-usage note. Never created unprompted.
7. **Report** — paths created/updated, the relevance verdict, the next-step prompt.

**Guards:** if poppler is missing, it stops rather than fabricating a summary; if a DOI won't
verify, it writes the record with `doi` blank and flags it; it never overwrites an existing
project-usage note without confirmation.

## First-run scaffold

On the first ingest, if the `Paper library dir` doesn't exist, `paper-ingest` copies the plugin
template ([`templates/paper-library/`](../templates/paper-library/)) — the two `_TEMPLATE.md`
files, the `index.csv` header, `figs/.gitkeep`, and a `README.md` describing the model.

## Related

- [Commands](Commands.md#paper-ingest-skill-not-a-slash-command) — skill reference
- [Configuration](Configuration.md) — the `## Research stack` keys
- [Agents](Agents.md) — `@literature-curator` owns the complementary *citation* layer
