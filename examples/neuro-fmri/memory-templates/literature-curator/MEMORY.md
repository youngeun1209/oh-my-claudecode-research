# literature-curator agent — memory (redacted skeleton)

> **Skeleton only.** Concrete BibTeX paths, citekeys, anchor papers, and venue
> names have been stripped. Copy this file into your own project's
> `.claude/agent-memory/literature-curator/MEMORY.md` and fill in.
>
> Domain flavor: neuro-fMRI. Preferred sources, bucket conventions, and
> example citekey patterns reflect typical neuroimaging studies (preprocessing,
> parcellation, connectivity, ISC, spin tests). Adapt for other neuro flavors
> (EEG/MEG, behavior-only, lesion studies) by editing the **Preferred sources**
> and **Bucket conventions** sections.

**Last synced:** [YYYY-MM-DD]

---

## File paths (this project)

- **BibTeX file:** `[references.bib]`
- **Summary table:** `[references.csv]`
- **Citekey convention:** `[firstauthorYearShortword]` (lowercase first-author surname + 4-digit year + short content keyword, e.g. `power2011functional`, `yeo2011organization`, `nastase2019measuring`)

## Preferred sources (in search order)

1. **PubMed** — biomedical/clinical neuroimaging, especially patient-cohort work
2. **bioRxiv / medRxiv** — recent neuroimaging preprints (always check for the published version before citing the preprint)
3. **Google Scholar (via WebSearch)** — coverage for methods papers that PubMed under-indexes (e.g., older MATLAB-toolbox papers, theoretical/computational pieces)
4. **arXiv (cs.LG / stat.ML / q-bio.NC)** — for ML/computational-neuroscience adjacent claims
5. **CrossRef** (via `verify-citation` skill) — final canonical metadata + DOI verification
6. **OpenAlex** (via skill) — abstract retrieval for claim-fit checks

Avoid citing **review papers** for primary claims unless the project explicitly wants a review citation; walk back to the primary source.

## Bucket conventions

The four buckets used in `references.csv`'s `bucket` column (matches `supervisor`'s anchor-list rubric):

| Bucket | What goes here (neuro-fMRI flavor) |
|---|---|
| `foundational` | Field-standard works the manuscript cites without argument. Common patterns: parcellation atlas papers (e.g., the atlas you use), the canonical preprocessing-pipeline paper, the seminal paper introducing your primary analysis (e.g. ISC, dynamic FC, gradient methods). |
| `competing` | Papers whose claim our study extends, refines, or directly challenges. Engaged in **Discussion**. |
| `contextual` | Methodological / statistical citations that justify a parameter choice but are not the subject of engagement (e.g., the spin-test paper, the cluster-correction paper, the GLM software citation). Cite once; do not over-engage. |
| `open-question` | Papers that explicitly call for the work this study is doing. Strong rhetorical anchors for the **Introduction**. |

## Anchor list (4-bucket summary)

The full anchor list lives in `references.csv` (filter by `bucket` column). The most rhetorically load-bearing entries (kept here for quick recall):

### Foundational
- `[citekey]` — [one-sentence role, e.g., "Parcellation atlas; defines our 400-parcel ROI scheme."]
- `[citekey]` — [...]

### Competing / closest prior
- `[citekey]` — [one-sentence role, e.g., "Reports the X→Y effect we generalize to condition Z."]
- `[citekey]` — [...]

### Contextual / methodological
- `[citekey]` — [e.g., "Spin-test null model — cited in Methods for spatial autocorrelation."]
- `[citekey]` — [...]

### Open-question
- `[citekey]` — [e.g., "Explicitly calls for tests of our specific hypothesis in clinical populations."]
- `[citekey]` — [...]

## Open `[CITE: ...]` placeholders

Track unresolved placeholders here so they do not get lost between sessions. Remove an entry once `references.bib` has a verified entry for it.

| Placeholder text | Section | Raised on | Status |
|---|---|---|---|
| `[CITE: ...]` | [Intro / Methods / Discussion] | [YYYY-MM-DD] | open / resolved / NOT_FOUND |
| `[CITE: ...]` | ... | ... | ... |

## Failed searches (do not retry without a new lead)

Claims for which a satisfactory citation could not be found. Re-attempt only if the user provides a new starting reference.

- [YYYY-MM-DD] [Claim] — searched [sources]; no primary source. Best near-miss: `[citekey or DOI]`.

## Last audit

- **Date:** [YYYY-MM-DD]
- **Total entries:** [N]
- **PASS / MISMATCH / NOT_FOUND / NOT_VERIFIED:** [n / n / n / n]
- **Action items from the audit:** [list any DOIs needing manual fix, retracted papers, etc.]

## Settled bibliographic conventions

- Reference style: `[author-year / numeric]` (matches `paper-writer/MEMORY.md`'s **Target venue** entry)
- BibLaTeX vs BibTeX: `[BibTeX]` (or `BibLaTeX` if using `biblatex` package in LaTeX)
- Preprint handling: `[cite published version when available; preprint only when no published version exists]`
- "et al." threshold for `references.csv`'s `authors` column: `[>3 authors → "First et al."]`

## Linked topic files

- `failed-searches.md` — long-form notes on unsuccessful citation hunts (when this section grows past ~10 entries)
- `style-decisions.md` — non-trivial BibTeX styling choices (e.g., how to cite preregistration documents, datasets, software, conference abstracts)
- `summary-table-schema.md` — if this project diverges from the canonical 12-column schema, document the divergence here

## Drifts flagged at last sync

- [Auto-populated by `/sync` if running that command; otherwise leave empty.]
