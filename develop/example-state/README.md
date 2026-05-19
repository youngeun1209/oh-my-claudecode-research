# `develop/example-state/`

Canonical empty-state JSONs for OMXR's orchestration state store. These are
the files `$omxr-setup` writes into the user's `.omx/state/omxr/` on first
run.

**Tracked, not gitignored** — the parent `.gitignore` has `!/develop/example-state/`
to keep these as committed reference material despite the rest of `develop/`
being local working docs.

## Files

| File | Purpose | Empty value |
|---|---|---|
| `paper.json` | Manuscript progress (sections, status, iter) | Title/venue/hypothesis `null`; 5 sections with `status: "empty"` |
| `reviews.json` | Append-only history of reviewer verdicts | `runs: []` |
| `citations.json` | BibTeX queue + verification states | `queue: []`, `verified: []`, `last_sweep: null` |
| `figures.json` | Per-figure design/impl/critique status | `figures: {}` |
| `rebuttals.json` | Append-only per-run rebuttal entries (one per `$respond-reviewer` invocation) | `rebuttals: []` |
| `_run-log.jsonl` | Append-only run log (one JSON per line) | Empty file |

## Schema reference

See [`../phase-0-primitives.md`](../phase-0-primitives.md) for full field
documentation and rationale. The examples below show the populated shape that
engines produce — the actual files in this directory contain only the empty
stub.

### `paper.json` — populated example

```json
{
  "schema_version": "1",
  "title": "Parametric working memory and frontoparietal connectivity",
  "venue": "NeuroImage",
  "hypothesis": "Load-dependent FC modulation predicts behavioral capacity",
  "manuscript_root": "manuscript/",
  "sections": {
    "results": {
      "path": "manuscript/sections/results.tex",
      "status": "revising",
      "iter": 2,
      "last_review_id": "a1b2c3d4-0001-...",
      "outline": null
    }
  },
  "figures": ["fig1", "fig2"],
  "submission_ready": false,
  "last_updated": "2026-05-11T14:32:00Z"
}
```

**Section `status` enum:** `empty | drafted | revising | approved | blocked | blocked-on-tbd`

**`outline` field semantics:** `null` → engine falls back to
`<manuscript_root>/outline.md`. Inline string → used directly.

### `reviews.json` — populated example entry

```json
{
  "schema_version": "1",
  "runs": [
    {
      "run_id": "a1b2c3d4-0001-...",
      "engine": "iterate-revision",
      "section": "results",
      "iter": 1,
      "venue": "NeuroImage",
      "started": "2026-05-11T14:00:00Z",
      "ended":   "2026-05-11T14:03:42Z",
      "issues": [
        { "severity": "major", "text": "Sample size justification missing", "location": "L34-38" }
      ],
      "verdict": "CONTINUE",
      "reason": "1 major remaining, iter < max_iter"
    }
  ]
}
```

**Severity enum:** `critical | major | minor | nit`
**Verdict enum:** `DONE | CONTINUE | BLOCKED | HALT`

### `citations.json` — populated example

```json
{
  "schema_version": "1",
  "queue": [
    {
      "placeholder_id": "CITE_001",
      "context": "the sentence the citation goes in",
      "status": "verified",
      "candidates": [{"doi": "10.xxxx/yyyy", "title": "...", "score": 0.92}],
      "chosen": "10.xxxx/yyyy"
    }
  ],
  "verified": [
    {
      "key": "smith2024deep",
      "doi": "10.xxxx/yyyy",
      "metadata_source": "crossref",
      "verified_at": "2026-05-11T14:32:00Z"
    }
  ],
  "last_sweep": {
    "topic": "frontoparietal working memory",
    "n_requested": 20,
    "n_returned": 17,
    "rejected": [{"doi": "10.aaaa/bbbb", "reason": "not peer-reviewed"}],
    "timestamp": "2026-05-11T14:32:00Z"
  }
}
```

**Queue status enum:** `pending | searching | verified | rejected`
**Metadata source enum:** `crossref | openalex`

### `figures.json` — populated example

```json
{
  "schema_version": "1",
  "figures": {
    "fig1": {
      "title": "Behavioral results",
      "brief_status":    "approved",
      "impl_status":     "drafted",
      "critique_status": "pending",
      "iter": 1,
      "deck_path":   "decks/exported/fig1.png",
      "vector_path": "manuscript/figures/fig1.pdf"
    }
  }
}
```

**brief/impl status enum:** `missing | drafted | approved`
**critique_status enum:** `pending | done`

### `rebuttals.json` — populated example

Owned by the `$respond-reviewer` engine. One entry per engine run; entries are
append-only (a re-run of the same review letter creates a new entry, never
overwrites). Each entry records the full per-comment classification, dispatched
response, supervisor verdict, and the path to the assembled rebuttal letter.

```jsonc
{
  "schema_version": "1",
  "rebuttals": [
    {
      "run_id": "c3d4e5f6-0007-...",
      "review_letter": "reviews/r1-comments.md",
      "input_format":  "markdown",
      "output_format": "latex",
      "manuscript_root": "manuscript/",
      "draft_only": false,
      "started": "2026-05-11T15:00:00Z",
      "ended":   "2026-05-11T15:07:21Z",
      "letter_path":   "manuscript/rebuttal-letter.tex",
      "letter_backup": null,
      "verdict": "HALT",
      "reason":  "1 response disputed by supervisor; 1 structural comment requires human decision",
      "comments": [
        {
          "comment_id":     "R1.1",
          "reviewer":       "R1",
          "label":          "prose",
          "agent":          "paper-writer",
          "target_section": "discussion",
          "figure_id":      null,
          "classification_reason": "reviewer requests softer hedging on the causal claim",
          "response":       "We thank the reviewer. We have softened the claim by replacing 'demonstrates' with 'is consistent with' in L42.",
          "actions_taken":  ["edited manuscript/sections/discussion.tex L42"],
          "files_touched":  ["manuscript/sections/discussion.tex"],
          "citations_added": [],
          "next_steps":     [],
          "parse_error":    null,
          "dispatch_error": null,
          "verdict":        "addressed",
          "verdict_reason": "edit matches the prose response and file_touched is consistent"
        },
        {
          "comment_id":     "R1.2",
          "reviewer":       "R1",
          "label":          "analysis",
          "agent":          "analysis-implementer",
          "target_section": "results",
          "figure_id":      "fig3",
          "classification_reason": "reviewer asks for a redraw of Figure 3 with the additional control condition",
          "response":       "We agree that Figure 3 needs the additional control. The redraw should use the existing data slice at data/control_v2/; we suggest running $figure-bake fig3 to execute.",
          "actions_taken":  ["identified data slice for redraw at data/control_v2/"],
          "files_touched":  [],
          "citations_added": [],
          "next_steps":     ["$figure-bake fig3"],
          "parse_error":    null,
          "dispatch_error": null,
          "verdict":        "deferred",
          "verdict_reason": "redraw requires $figure-bake — engines do not auto-invoke other engines"
        },
        {
          "comment_id":     "R1.3",
          "reviewer":       "R1",
          "label":          "citation",
          "agent":          "literature-curator",
          "target_section": "introduction",
          "figure_id":      null,
          "classification_reason": "reviewer requests citation to Smith 2024 in the prior-work paragraph",
          "response":       "We have added the requested citation (smith2024deep, DOI 10.xxxx/yyyy).",
          "actions_taken":  ["verified DOI 10.xxxx/yyyy via CrossRef", "added citekey smith2024deep to references.bib"],
          "files_touched":  ["manuscript/references.bib"],
          "citations_added": [{ "citekey": "smith2024deep", "doi": "10.xxxx/yyyy", "title": "Deep learning in motor cortex" }],
          "next_steps":     [],
          "parse_error":    null,
          "dispatch_error": null,
          "verdict":        "addressed",
          "verdict_reason": "citation added and verified; response matches actions"
        },
        {
          "comment_id":     "R2.1",
          "reviewer":       "R2",
          "label":          "structural",
          "agent":          null,
          "target_section": "methods",
          "figure_id":      null,
          "classification_reason": "reviewer questions the central methodological framing; this is a scope decision",
          "response":       null,
          "actions_taken":  [],
          "files_touched":  [],
          "citations_added": [],
          "next_steps":     [],
          "parse_error":    null,
          "dispatch_error": null,
          "verdict":        "deferred",
          "verdict_reason": "structural — surfaced to user-attention; no auto-response generated"
        },
        {
          "comment_id":     "R2.2",
          "reviewer":       "R2",
          "label":          "prose",
          "agent":          "paper-writer",
          "target_section": "abstract",
          "figure_id":      null,
          "classification_reason": "reviewer wants the abstract tightened",
          "response":       "We have revised the abstract for clarity.",
          "actions_taken":  ["revised abstract"],
          "files_touched":  [],
          "citations_added": [],
          "next_steps":     [],
          "parse_error":    null,
          "dispatch_error": null,
          "verdict":        "disputed",
          "verdict_reason": "response claims revision but files_touched is empty and draft_only is false"
        }
      ],
      "user_attention_count": 1,
      "suggested_next_steps": ["$figure-bake fig3"],
      "summary": {
        "n_comments":       5,
        "n_dispatched":     4,
        "n_user_attention": 1,
        "by_label":         { "prose": 2, "analysis": 1, "citation": 1, "clarification": 0, "structural": 1 },
        "by_verdict":       { "addressed": 2, "deferred": 2, "disputed": 1 },
        "n_parse_failures":  0,
        "n_dispatch_errors": 0,
        "files_touched_all":  ["manuscript/sections/discussion.tex", "manuscript/references.bib"],
        "citations_added_all": [{ "citekey": "smith2024deep", "doi": "10.xxxx/yyyy", "title": "Deep learning in motor cortex" }]
      }
    }
  ]
}
```

**Label enum:** `prose | analysis | citation | clarification | structural`
**Per-comment verdict enum:** `addressed | deferred | disputed`
**Run-level verdict enum:** `DONE | HALT | BLOCKED` (no `CONTINUE` — `$respond-reviewer` is single-pass)

**`agent` semantics:** maps from `label` per the engine's classification taxonomy.
`structural` always has `agent: null` — these comments are routed to the
user-attention list and never auto-dispatched (Phase 2 ethical gate). Figure
redraws are labeled `analysis` and routed to `@analysis-implementer` with the
figure id; the response typically includes `$figure-bake <id>` in `next_steps`
because engines do not call other engines (Phase 2 decision §5).

**`letter_path` format:** the path extension records the chosen output format
(`.tex` for LaTeX, `.md` for markdown). LaTeX is the default (Phase 2
decision §2); markdown is the `--format md` escape for journals with web-form
rebuttal submissions.

### `_run-log.jsonl` — example line

JSONL = one JSON object per line. Append-only; never overwritten.

```jsonl
{"run_id": "a1b2c3d4-0001-...", "engine": "iterate-revision", "args": {"section": "sections/results.tex", "max_iter": 3, "venue": "NeuroImage"}, "started": "2026-05-11T14:00:00Z", "ended": "2026-05-11T14:03:42Z", "iter_count": 1, "verdict": "CONTINUE", "tokens_used": 8400, "section_path": "sections/results.tex"}
```

## How `$omxr-setup` uses these

`$omxr-setup` reads each file in this directory and writes its content into
the user's `.omx/state/omxr/<file>` only if the target doesn't already
exist. Existing state is never overwritten — `$omxr-setup` is idempotent.

## Schema version migration

`schema_version` is a JSON string (`"1"`, not int — see Phase 0 decision §2).
Future bumps follow semver-lite:

- `"1.1"` — additive (new optional fields; old readers ignore)
- `"2"` — breaking (will require a migration runner; deferred+)

In the current lifecycle, all files declare `"1"`. A mismatch causes a warn-and-proceed
in `skills/orchestrate/phases/01-state-read.md`.
