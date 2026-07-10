---
name: paper-ingest
description: Ingest a research paper into the project's two-folder reading library. Use when the user hands you a paper — a PDF path, a DOI, or a URL — and wants it read, summarized, and indexed. The skill writes a project-agnostic summary (with a cropped main figure) to the library's bibliographic-management/ folder, upserts a row in that folder's index.csv, judges whether the paper is relevant to the project's narrative (from CLAUDE.md ## Project context), and — only after reporting the relevance verdict and getting the user's go-ahead — writes a project-usage note. This is the reading/notes layer, separate from the manuscript's references.bib (owned by literature-curator). Triggers include "ingest this paper", "summarize and file this PDF", "add this DOI to the library".
---

# Paper Ingest

Turn a paper into a clean record in the project's reading library, and (if relevant) a
project-usage note. Reading is the notes layer — **separate** from the manuscript
`references.bib` that `literature-curator` owns; a paper can be recorded here without ever
being cited. Default to **English** for the written records and the user-facing status
report; override the language via the project `CLAUDE.md`.

## Configuration

Resolve config in priority order: env var → project `CLAUDE.md` `## Research stack` block → default.

| Setting | `## Research stack` key | Env var | Default |
|---|---|---|---|
| Library root | `Paper library dir` | `PAPER_LIBRARY_DIR` | `docs/papers/` |
| Bucket vocabulary | `Paper buckets` (comma-separated) | `PAPER_BUCKETS` | free-form (one-word tag) |

Paths below are written relative to the **library root**. On first run, if the library
root does not exist, scaffold it by copying the plugin template
[`templates/paper-library/`](../../templates/paper-library/) (its `bibliographic-management/`
with `_TEMPLATE.md`, `index.csv` header, `figs/.gitkeep`, and the root `_TEMPLATE.md` + `README.md`).

## The two-folder model (do not confuse)

| Folder | Role | Template |
|---|---|---|
| `<library root>/bibliographic-management/<file>.md` | **Paper record** — project-agnostic: what it is, claims, method, result, main figure | `bibliographic-management/_TEMPLATE.md` (A) |
| `<library root>/<file>.md` | **Project usage** — only for relevant papers: how we cite/use it, links back to the record | `<library root>/_TEMPLATE.md` (B) |
| `<library root>/bibliographic-management/index.csv` | flat index of **all** papers (relevant or not) | — |

The manuscript `BibTeX file` (`## Research stack`, default `<Manuscript dir>/references.bib`)
is a **separate** surface — do not write BibTeX here.

## Conventions

- **Filename:** `YYYY-firstauthor-keyword.md`, lowercase, hyphen (e.g. `2022-smith-graph-attention.md`). `bibkey = firstauthorYYYY` (e.g. `smith2022`).
- **Buckets:** a tag from the project's `Paper buckets` vocabulary; if none is configured, pick a short, distinctive one-word tag and reuse it consistently.
- **Status:** `to-read | skimmed | read`.
- **PDFs via poppler only** — the built-in Read tool can't see a brew-installed pdftoppm; use the bundled `pdf_to_assets.sh`.

## Procedure

### Step 1 — Resolve the input

- **PDF path**: run the extractor.
  ```bash
  bash skills/paper-ingest/pdf_to_assets.sh "<pdf-path>"
  ```
  It prints an `out_dir` holding `text.txt` (body text to read) and `page-NN.png` (low-res page renders for figure scouting). Read `text.txt` with the Read tool.
- **DOI or URL** (no PDF): fetch canonical metadata with the **`verify-citation`** skill (CrossRef + OpenAlex → authors, title, year, venue, abstract). Summarize from the abstract; skip the figure step.

**Guard:** if `pdf_to_assets.sh` reports poppler missing, surface the error and stop — do **not** fabricate a summary. If a DOI won't verify, write the summary but leave `doi` blank and flag it in the report.

### Step 2 — Derive identifiers

From the metadata: `bibkey = firstauthorYYYY`, filename `YYYY-firstauthor-keyword.md`. Pick a short, distinctive `keyword` from the title.

### Step 3 — Write the summary (Template A)

Copy the shape of `<library root>/bibliographic-management/_TEMPLATE.md`. Fill the top table, `## One-line`, `## Key claims`, `## Method`, `## Result`, `## Key terms`. Keep it tight — claims you'd actually use, not a full abstract dump. Write to `<library root>/bibliographic-management/<file>.md`.

### Step 4 — Crop one main figure (PDF inputs only)

Scout the `page-NN.png` renders, choose the single most representative figure, find its page + pixel region, then crop at higher resolution:
```bash
bash skills/paper-ingest/pdf_to_assets.sh --crop "<pdf>" <page> <x> <y> <W> <H> \
    "<library root>/bibliographic-management/figs/<bibkey>-figN.png" 200
```
Coords are pixels at the crop dpi (200). Embed it under `## Main figure` with a one-line *What it shows*. (Region-finding: render the page once at 200 dpi, read it, estimate the box; the `cropfig` band heuristic in [`skills/cropfig/crop_bounds.py`](../cropfig/crop_bounds.py) is available if a simple region crop isn't clean enough.)

### Step 5 — Upsert the index row

```bash
python3 skills/paper-ingest/update_index.py --csv "<library root>/bibliographic-management/index.csv" \
  --bibkey <bibkey> --year <YYYY> --first_author "<Lastname I>" \
  --title "<title>" --venue "<venue>" --doi <doi-or-blank> \
  --bucket <bucket> --status <status> --in_project no \
  --pdf "<pdf-path-or-—>" --figure "figs/<bibkey>-figN.png-or-—" \
  --added_on "$(date +%F)"
```
Idempotent on `bibkey` (re-running updates in place). Leave `relevance=—`, `in_project=no` for now.

### Step 6 — Judge relevance, then ASK before the usage note

Decide whether the paper bears on the project's narrative — read `CLAUDE.md` `## Project context` (hypothesis / topic / narrative spine). Assign a `bucket`. **Report the verdict + rationale to the user and ask** whether to create the `<library root>/` usage note. Do not create it unprompted.

On **yes**:
- Write `<library root>/<file>.md` from Template B — fill `## Why it's relevant`, `## How we cite & use it` (we-cite-for / position support|contrast / cited-in section / what-we-borrow-or-extend), `## Connections to our analyses`. Link the record in the top table.
- Re-run `update_index.py --bibkey <bibkey> --in_project yes --relevance "intro;R3" --status <status>`.

Never overwrite an existing `<library root>/<file>.md` without explicit confirmation.

### Step 7 — Report

State what was created/updated with paths, the relevance verdict, and the next-step prompt. Example shape:

```
📄 <Author YEAR> ingested
- record:  <library root>/bibliographic-management/<file>.md (+ figs/<bibkey>-figN.png)
- index.csv: <inserted|updated> (bibkey=<bibkey>, bucket=<bucket>)
- relevance: <relevant to intro/R3 because … | low direct relevance to this project>
- create project-usage note (<library root>/)? → (awaiting confirmation)
```

## Bundled files
- `pdf_to_assets.sh` — poppler wrapper: extract mode (text + page renders) and `--crop` mode (figure region → PNG).
- `update_index.py` — idempotent `bibkey` upsert into `index.csv` (pure stdlib; `--csv` required).
