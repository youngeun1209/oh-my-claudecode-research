---
name: verify-citation
description: Verify that academic citations exist and match the metadata claimed for them, and optionally write verification results into a project summary table. Looks up DOIs against CrossRef, fetches canonical authors/title/year/journal and the abstract via OpenAlex, and reports any mismatch against a BibTeX entry or a free-form DOI. Use to gate every citation `literature-curator` adds, to audit an existing BibTeX file for fabricated or wrong entries, or to retrieve an abstract so the calling agent can judge whether the paper actually supports a given claim.
---

<Purpose>
Provide a deterministic, network-based existence + metadata check on academic citations so that no fabricated or mis-cited reference makes it into the manuscript. Returns canonical metadata and the abstract so the calling agent (typically `literature-curator`) can assess claim-fit semantically. Optionally writes the verification verdict into the project's literature summary table so the audit trail lives next to the bibliography.
</Purpose>

<Use_When>
- `literature-curator` is about to add a new entry to the project BibTeX file.
- A reviewer / supervisor asks "is this citation real?" or "does this paper actually say X?".
- Auditing an existing BibTeX file (e.g. after a co-author imports references from another project).
- Resolving a `[CITE: ...]` placeholder — verify the candidate before committing.
- Refreshing the `verified_on` / `verify_status` columns of the project summary table.
</Use_When>

<Do_Not_Use_When>
- Only the citation **format** needs fixing (use a BibTeX prettifier, not this).
- The user wants to *find* a citation from scratch with no candidate yet — that is `literature-curator`'s WebSearch task; this skill verifies once a candidate exists.
- Offline-only environment with no network — skill requires CrossRef/OpenAlex.
</Do_Not_Use_When>

<Configuration>
This skill reads:

| Variable | Default | Purpose |
|---|---|---|
| `BIB_FILE` | `references.bib` | Path to project BibTeX. Used when verifying by citekey. |
| `SUMMARY_FILE` | `references.csv` | Project literature summary table. When `--summary-csv` is set (or this is configured in CLAUDE.md), `verified_on` / `verify_status` are written back per citekey. |
| `CITATION_VERIFY_EMAIL` | (unset) | Polite-pool email for CrossRef/OpenAlex. Strongly recommended — gives a higher rate limit and prioritizes your requests. |
| `CITATION_VERIFY_TIMEOUT` | `15` | Request timeout in seconds. |

Resolution order on each invocation:
1. **Command-line flags** (highest priority).
2. **Environment variables.**
3. **Project CLAUDE.md "Research stack" block** — fields `BibTeX file`, `Summary file`, `CrossRef email`.
4. **Defaults above.**

If `BIB_FILE` is not configured on first use, ask the user once and offer to persist it.
</Configuration>

<Steps>

### Step 1 — Pick the input mode

Four modes:

```bash
# Verify a single DOI
python3 verify_citation.py --doi 10.1038/s41586-023-XXXXX-X

# Verify one citekey from the BibTeX file
python3 verify_citation.py --bib references.bib --key smith2023connectome

# Audit the whole BibTeX file
python3 verify_citation.py --bib references.bib

# Audit and also update the project summary table in place
python3 verify_citation.py --bib references.bib --summary-csv references.csv
```

Optional flags:
- `--claim "<one-line claim>"` attaches the claim to the report so downstream logs show what was being supported. The skill does NOT decide whether the abstract supports it — that is the calling agent's call.
- `--json` emits structured JSON instead of the human report.

### Step 2 — Run the verifier

```bash
python3 "$CLAUDE_PLUGIN_ROOT"/skills/verify-citation/verify_citation.py \
    --bib "$BIB_FILE" \
    --summary-csv "$SUMMARY_FILE"
```

The script:
1. Parses the requested entry(ies) from the BibTeX file.
2. Hits CrossRef (`api.crossref.org/works/<DOI>`) for canonical metadata.
3. Falls back to a CrossRef title+author search if no DOI is present in the BibTeX.
4. Hits OpenAlex (`api.openalex.org/works/doi:<DOI>`) for the abstract.
5. Compares author / title / year between BibTeX and CrossRef; flags mismatches.
6. If `--summary-csv` is set, writes `verified_on` (today, YYYY-MM-DD) and `verify_status` to the matching `citekey` row. Other columns (`our_use`, `paper_says`, `bucket`, `cited_sections`) are **never** overwritten.

### Step 3 — Read the report

Human report (per entry):

```
[PASS|MISMATCH|NOT_FOUND] <citekey or DOI>
  DOI:        <doi>          → CrossRef: <found / not found>
  Title:      crossref="..."    match=<true/false>
  Author:     crossref="..." (+N more)   match=<true/false>
  Year:       crossref=YYYY   match=<true/false>
  Abstract (first 500 chars):
    "..."
  Claim:      <if --claim was provided>
  → Read the abstract above and confirm whether it supports the claim.
  Note:       <any flags>
```

Statuses:
- `PASS` — DOI resolves AND title/authors/year all match (case-insensitive, normalized).
- `MISMATCH` — found at CrossRef but at least one metadata field disagrees with the BibTeX entry.
- `NOT_FOUND` — DOI does not resolve and title+author search returns no plausible match.
- `NOT_VERIFIED` — network error, surfaced separately; not treated as a pass.

### Step 4 — Caller assesses claim-fit

The script does NOT decide whether the abstract supports the claim — that requires reading. The calling agent reads the abstract from the report and answers the claim-fit question. The skill provides the evidence; the agent provides the judgment.

</Steps>

<Output_Contract>

stdout: human-readable report (one block per entry) — or JSON if `--json` was passed.

Exit codes:
- `0` — all entries PASS.
- `1` — at least one entry MISMATCH or NOT_FOUND.
- `2` — script error (network down on every retry, malformed BibTeX, missing file, etc.).

When `--summary-csv` is set:
- Columns updated: `verified_on`, `verify_status` (per-citekey).
- Columns added if the citekey row does not exist: a new row with `citekey`, `verified_on`, `verify_status` filled and human-curated columns left blank for `literature-curator` to fill.
- Columns the skill never touches: `our_use`, `paper_says`, `bucket`, `cited_sections`, `authors`, `year`, `title`, `venue`, `doi`. These belong to the curator.

</Output_Contract>

<Failure_Modes>

| Symptom | Cause | Action |
|---|---|---|
| `urllib.error.URLError` / `timeout` | Network unreachable, CrossRef down | Retry once; if still failing, report affected entries as `NOT_VERIFIED (network)` and do NOT mark them PASS |
| `Title matches but DOI does not resolve` | BibTeX has a typo in DOI | Report as `MISMATCH`; the curator agent fixes the DOI |
| `Author count differs` | BibTeX truncates with "et al." | Soft `MISMATCH` — flagged in notes but does not necessarily fail (curator decides) |
| `Abstract empty in OpenAlex` | Publisher does not deposit abstracts | Skill still PASSes on metadata; caller must verify claim-fit via manuscript download |
| `Summary file does not exist` | First run, no summary table yet | Skill creates the file with the canonical header row |

</Failure_Modes>

<Files>
- `SKILL.md` — this file.
- `verify_citation.py` — the verifier. Stdlib-only (`urllib`, `json`, `csv`, `re`). Runnable as a script or importable.
</Files>
