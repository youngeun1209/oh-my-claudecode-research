# Phase 5 — Verify

Run every surviving entry from phase 04 through the standalone [`skills/verify-citation/`](../../verify-citation/SKILL.md) skill. The result determines whether the entry lands in `references.bib` (phase 06) or in `citations.json.last_sweep.rejected` (phase 06).

**This is the hard gate (Phase 2 decision §1).** Only `PASS` entries are added to `references.bib`. Everything else is preserved with a reason so the user can audit.

## Inputs (from phase 04)

| Name | Source | Purpose |
|---|---|---|
| `topic`, `n_requested`, `depth`, `parallel`, `bib_file`, `summary_file`, `citations_state`, `probe_failures`, `already_in_bib_count`, `merged_in_count`, `cross_batch_dups_count`, `trimmed_count`, `notes` | flows from phase 04 | Threaded through unchanged. |
| `survivors` | phase 04 | List of provisional records: `{doi, citekey, bibtex, csv_row, relevance_score, relevance_reason, previously_verified}`. |

## Step 1 — Empty-survivors short-circuit

If `survivors` is empty (phase 04 had nothing to pass through), produce empty result lists and hand off to phase 06:

- `verified_entries = []`
- `rejected_entries = []`

Phase 06 will produce a clean empty-result summary with the cause spelled out in `notes`. Skip the rest of this phase.

## Step 2 — Run `verify-citation` per survivor

For each entry in `survivors`, invoke the verify-citation skill via the Bash tool, in `--doi` mode with `--json` so the result is machine-readable.

Command shape:

```bash
python3 "$CODEX_PLUGIN_ROOT"/skills/verify-citation/verify_citation.py \
    --doi "<lowercase DOI>" \
    --json
```

If `CITATION_VERIFY_EMAIL` resolves (env var or AGENTS.md `## Research stack` field `CrossRef email`), set it in the environment for the subprocess — verify-citation reads it for the polite-pool header.

Concurrency: the calls are CPU-light but each is one or two HTTP roundtrips. Issue them **sequentially** even when the engine was launched with `--parallel > 1` — the `--parallel` flag governs the **curator dispatches in phase 03**, not the verify calls in phase 05. Verify is fast (a single shell-out per entry) and the runtime overhead of parallelizing here would not noticeably improve wall-clock time while it would multiply the risk of CrossRef / OpenAlex rate-limiting.

Parse the JSON output. The shape (per verify-citation's contract):

```jsonc
{
  "status":   "PASS | MISMATCH | NOT_FOUND | NOT_VERIFIED",
  "doi":      "<lowercase DOI>",
  "crossref": { "title": "...", "authors": [...], "year": <int>, "journal": "...", "found": true|false },
  "openalex": { "abstract": "...", "found": true|false },
  "matches":  { "title": true|false, "authors": true|false, "year": true|false },
  "notes":    [ "<any flag strings>" ]
}
```

Exit codes also matter:

- `0` — PASS.
- `1` — MISMATCH or NOT_FOUND.
- `2` — script error (verifier crashed, both APIs down, malformed input).

Use the JSON `status` as the canonical signal; the exit code is a redundancy check.

## Step 3 — Classify each result

For each entry, decide based on `status` and the JSON payload:

### `PASS`

The DOI resolved at CrossRef and the title / authors / year matched the BibTeX entry's claims.

- Stamp `verified_at = <UTC ISO-8601 now>` on the in-memory record.
- Update `csv_row.verify_status = "PASS"` and `csv_row.verified_on = <YYYY-MM-DD>`.
- If `entry.previously_verified == true`, override `csv_row.verify_status = "PASS (re-verified)"` so the summary CSV row shows continuity.
- Optionally: if the curator's `csv_row.paper_says` was `"(could not summarize from metadata)"` and `verify-citation` returned a non-empty `openalex.abstract`, append a one-line fallback summary built from the first sentence of the abstract. This rescues entries whose CrossRef record was thin but whose OpenAlex abstract is rich. Mark the rescued row with a note (`csv_row` gains no extra column; the rescue is silent — the summary table reader sees a real one-liner instead of the apology string).
- Append the record to `verified_entries`.

### `MISMATCH`

The DOI resolved but at least one of title / authors / year disagreed with what the curator produced.

- Build a rejection reason summarizing the mismatched fields. Example:
  ```
  MISMATCH: CrossRef title differs ("Neural manifolds in primate motor cortex"
  vs curator's "Neural manifolds in motor cortex") and year differs (2024 vs 2023).
  ```
- Append `{doi, citekey, bibtex, csv_row, reason, status: "MISMATCH"}` to `rejected_entries`.
- Do **not** add to `references.bib`.

A `MISMATCH` is most often a typo the curator introduced or a CrossRef ahead-of-print update; the user reviewing `rejected` decides whether to manually rescue.

### `NOT_FOUND`

The DOI did not resolve and the title-author fallback search returned no plausible match.

- Build a rejection reason:
  ```
  NOT_FOUND: DOI <doi> did not resolve at CrossRef; title+author fallback returned no match.
  Possible causes: typo in DOI, withdrawn preprint, paper from a venue not indexed by CrossRef.
  ```
- Append to `rejected_entries`.
- Do **not** add to `references.bib`.

### `NOT_VERIFIED`

Network error, timeout, or the verifier script crashed. The entry could not be checked.

- Build a rejection reason from the script's `notes` field:
  ```
  NOT_VERIFIED (network): <reason from verify-citation notes>
  Re-run $literature-sweep when the network is back, or pass --source <other> if
  one API is specifically unreachable.
  ```
- Append to `rejected_entries`.
- Do **not** add to `references.bib`.

Per the locked invariant: an unverified entry is never written to the bibliography, regardless of how it failed. Anything other than `PASS` is rejected, full stop.

## Step 4 — Track running counts

While iterating, maintain three counters for phase 06's user summary:

- `verify_pass_count` — entries where `status == PASS`.
- `verify_reject_count` — `MISMATCH` + `NOT_FOUND` + `NOT_VERIFIED` combined.
- Per-status breakdown: `verify_status_counts = {"PASS": ..., "MISMATCH": ..., "NOT_FOUND": ..., "NOT_VERIFIED": ...}`.

If the verifier crashed (exit code 2) on a specific entry, also record an entry-level note in `notes`:

```
literature-sweep: verify-citation crashed on <doi> (<reason>) — treating as NOT_VERIFIED.
```

If the verifier crashes on every entry (e.g., the script file is missing or Python is unavailable), record once in `notes`:

```
literature-sweep: verify-citation is non-functional on this machine (<reason>).
All <K> survivors recorded as NOT_VERIFIED. Fix the verifier (run $omxr-setup
to re-check infrastructure) and re-run.
```

Continue to phase 06 anyway — the user needs to see a clean summary with the diagnosis, not a stack trace.

## Step 5 — Hand off to phase 06

Pass forward to phase 06:

- All threaded fields from phase 04
- `verified_entries` — list of records with `verified_at` stamps; ready for `references.bib` and CSV append.
- `rejected_entries` — list of records with `reason` and `status`; ready for `citations.json.last_sweep.rejected`.
- `verify_pass_count`, `verify_reject_count`, `verify_status_counts` — for the run summary.
- `notes` — updated with any verifier-level diagnostics.

## Failure modes

| Condition | Behavior |
|---|---|
| Empty `survivors` | Skip dispatch. Empty `verified_entries` and `rejected_entries`. Phase 06 reports the cause from earlier `notes`. |
| verify-citation script missing at `$CODEX_PLUGIN_ROOT/skills/verify-citation/verify_citation.py` | All survivors classified as `NOT_VERIFIED` with reason `"verify-citation script not found at plugin root"`. Add one engine-level note. Continue. |
| verify-citation timeout for one entry | That entry classified `NOT_VERIFIED`. Continue with the rest. |
| verify-citation timeout for many entries (rate-limited) | Each classified `NOT_VERIFIED`. Record one engine-level note suggesting `CITATION_VERIFY_EMAIL` (polite pool) or a re-run later. |
| Malformed JSON from verify-citation | Treat the entry as `NOT_VERIFIED` with reason `"verify-citation output not parseable as JSON"`. Continue. |
| Exit code 2 (script error) but JSON still parses | Trust the JSON `status` field; record the script error in the entry's notes for telemetry. |
| User Ctrl-C mid-verify | The engine exits without a phase 06 write. The state on disk is unchanged (no partial bib writes). Re-running starts from phase 01. |

## What this phase does NOT do

- Does **not** invoke any subagent. The verify-citation skill is a pure Python script, not an Agent dispatch.
- Does **not** retry failed verifications. One shot per entry per run; the user re-runs the whole engine for a fresh attempt.
- Does **not** parallelize the verify calls — even when `--parallel > 1` was passed for phase 03. Phase 03's `--parallel` flag governs **curator dispatches only**.
- Does **not** write to `references.bib`, the CSV, or `citations.json`. Phase 06 owns all writes.
- Does **not** re-judge claim-fit. The curator already decided `paper_says` in phase 03 based on the same abstract data; this phase only checks that the candidate exists and the metadata is what the curator said it was.
- Does **not** read the manuscript. Cited-section attribution (`cited_sections`) stays empty for sweep-added entries; the user (or a later targeted curator pass) fills it.
