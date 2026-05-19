# Phase 3 — Reduce (write + drift lint)

Walk the per-section `dispatch_results` from phase 02, write each successful section's prose to its `paper.json.sections[name].path`, update `paper.json` status to `drafted`, then run the post-merge terminology drift lint and emit `<manuscript_root>/terminology-drift.md`.

This phase is purely engine-specific logic — no orchestrate primitives are imported. Writes use the `Write` tool; state updates use the atomic tmp + rename pattern from [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) "Atomicity".

## Inputs (from phase 02)

| Name | Source | Purpose |
|---|---|---|
| `paper_state` | phase 02 | Parsed `paper.json`; this phase mutates and writes back. |
| `manuscript_root` | phase 02 | Drift artifact destination. |
| `section_plan` | phase 02 | Original plan; used for parent-directory checks. |
| `dispatch_results` | phase 02 | List of `{name, path, status, output, error, ...}` dicts. |
| `terminology_decisions` | phase 02 | List of writer-logged decisions; surfaced to phase 04. |
| `run_id`, `run_started_at` | phase 02 | Carried forward to phase 04. |

## Step 1 — Per-section write

For each entry `r` in `dispatch_results`:

### 1a. Skip failed dispatches

If `r.status == "failed"`:
- Do not touch the section file.
- Do not touch `paper_state.sections[r.name]`.
- Record into `write_results`:
  ```jsonc
  {
    "name":   "<r.name>",
    "path":   "<r.path>",
    "wrote":  false,
    "reason": "dispatch failed: <r.error>",
    "before_status": "<r.current_status>",
    "after_status":  "<r.current_status — unchanged>"
  }
  ```
- Continue to the next entry.

### 1b. Verify parent directory

For `r.path`, compute the parent directory. If it does not exist, create it (`mkdir -p`). If the create fails (permission denied, etc.), record a failed write:
```jsonc
{
  "name":   "<r.name>",
  "path":   "<r.path>",
  "wrote":  false,
  "reason": "parent directory could not be created: <OS error>",
  "before_status": "<r.current_status>",
  "after_status":  "<r.current_status — unchanged>"
}
```
and continue. Do not abort the whole phase.

### 1c. Write the prose

Use the `Write` tool to write `r.output` to `r.path`. The output has already had its trailing `TERMINOLOGY-DECISION` lines stripped in phase 02 step 7, so this is prose only.

**Overwrite vs. preserve framing:**

- If `r.path` ends in `.tex` AND the existing file on disk has a `\section{...}` or `\section*{...}` declaration that matches the section name, **preserve the framing**:
  1. Read the existing content.
  2. Identify the `\section{...}` / `\section*{...}` line. Keep it.
  3. Identify the end of the section body (one of: end-of-file, the next `\section{...}` at the same level, or a sentinel comment like `% end <name>`). Keep what comes after.
  4. Replace only the body between those markers with `r.output`.

  If the existing file has no recognisable `\section{...}` (e.g., it was an empty stub with `% TODO`), fall through to full-overwrite.

- Otherwise (`.md`, `.txt`, or `.tex` without recognisable framing), **full-overwrite** with `r.output`. The writer's prose is the new file content.

Record:
```jsonc
{
  "name":   "<r.name>",
  "path":   "<r.path>",
  "wrote":  true,
  "bytes":  <len(r.output)>,
  "before_status": "<r.current_status>",
  "after_status":  "drafted"
}
```

If the `Write` tool errors (PII-scrub hook block, OS error, etc.):
- Record `wrote: false`, `reason: "write failed: <error>"`.
- Do **not** mutate `paper_state.sections[r.name]`.
- Continue to the next entry. Partial success is the contract.

### 1d. Update `paper_state.sections[r.name]`

Only when `wrote: true`:
- `paper_state.sections[r.name].status = "drafted"` (regardless of the prior status — `revising`, `blocked`, `blocked-on-tbd` all collapse to `drafted` after a successful first-draft pass).
- `paper_state.sections[r.name].iter = 1` (this engine produces iter-1; subsequent `$iterate-revision` runs bump beyond).
- `paper_state.sections[r.name].last_review_id` is **not** cleared — it remains pointing to the prior review (if any). This is a quirk of the map-reduce shape: the section's prose just changed, so the prior review is stale, but we don't clear the pointer because the user may want to inspect the old review for context. `$iterate-revision`'s phase 02 already handles "no prior review for this iter" gracefully.

Do **not** write `paper.json` back to disk after each section — accumulate the mutations in memory and write once at the end of step 1, to keep the on-disk file consistent (either all-or-nothing visible).

### 1e. Write `paper.json` back atomically

After all entries in `dispatch_results` are processed:

1. Set `paper_state.last_updated = <UTC ISO-8601 now>`.
2. Write `paper.json` back via the tmp + rename pattern from [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) Atomicity section.

If the write fails, log an error to the run log and continue — the prose is already on disk, and re-running the engine will reconcile. Do **not** roll back the section file writes.

## Step 2 — Build the candidate-term set

Across all sections where `wrote == true`, scan the prose for candidate-jargon terms. The scan is regex-light — three families, applied in order:

### Family A — All-caps tokens (acronyms)

Match `\b[A-Z][A-Z0-9-]{1,}\b` against each section's prose. Filter out:
- Common English short caps that are noise: `I`, `OK`, `USA`, `UK`, `EU`, `PhD`, `et`, `al` — extend the deny-list conservatively. (`et al` and `PhD` won't match the `[A-Z][A-Z0-9-]+` pattern anyway, listed for clarity.)
- Single-letter tokens (the leading-class already constrains to ≥2 chars).
- Roman-numeral-only tokens of length ≤4 (`II`, `III`, `IV`, `XII`).

Record each surviving token with its surface form and the section name.

### Family B — Hyphenated compounds (2+ words)

Match `\b[a-z][a-z]+-[a-z][a-z]+(?:-[a-z][a-z]+)*\b` against each section's prose. Examples: `working-memory`, `top-down`, `frontal-parietal`.

Filter out compounds that are common English (`well-known`, `up-to-date`, `state-of-the-art`) — keep the deny-list short; over-filtering is worse than under-filtering for a lint artifact the user will read.

Record each surviving compound with its surface form and the section name.

### Family C — Defined-once-then-reused phrases (cross-section signal)

For each section, extract every distinct 2- and 3-gram of capitalized words (heuristic: phrases like `Working Memory`, `Frontoparietal Network`). For each n-gram:
- Count occurrences in its own section. Skip if count < 2 (need "defined-once-then-reused" inside the section to count as a candidate).
- Look for the same n-gram (case-insensitive exact match) in any other written section. If found anywhere else with count ≥ 1, the n-gram is a candidate.

Record candidates with the surface form (preserving the case from the first occurrence) and the sections they appear in.

This family is the heuristic that catches phrases like `Working Memory` vs `working memory` vs `WM` — though family C alone won't detect the WM <-> Working Memory synonymy (the engine doesn't know they're the same concept). The drift report is "things that look like jargon and disagree in surface form across sections", which the user reads and decides.

## Step 3 — Cluster variants

Group candidates by a normalized form (lowercase, hyphens → spaces, plural-stripping). Within each cluster, list the distinct surface forms observed and the sections each form appears in.

For each cluster:
- If only one distinct surface form across all sections → no drift; skip from the report.
- If two or more distinct surface forms → drift candidate. Record:
  ```jsonc
  {
    "normalized":     "<lowercase normalized form>",
    "variants":       [
      { "form": "<surface>", "sections": ["<name1>", "<name2>"], "count": <total occurrences> },
      ...
    ],
    "suggested":      "<the variant with the highest total count; ties broken by first appearance order in section_plan>"
  }
  ```

## Step 4 — Emit `terminology-drift.md`

Write `<manuscript_root>/terminology-drift.md`. Use the `Write` tool. The file is **always** written, even when no drift is detected (so the user has a consistent place to look).

### Header

```
# Terminology drift report

Generated: <UTC ISO-8601>
Run id: <run_id>
Engine: outline-expand
Sections drafted this run: <comma-separated names of write_results entries with wrote=true>

This file is a non-blocking lint artifact. The engine completed normally; this
report lists candidate-jargon terms whose surface form disagrees across two or
more sections drafted in this run. Read the entries below, decide which form is
canonical, and either:

- Edit the sections by hand to converge on one form, OR
- Run $iterate-revision <section-path> per section — the reviewer will catch
  the same inconsistencies through prose review, OR
- Update .omx/omxr/agent-memory/paper-writer/nomenclature.md so future runs
  anchor on the canonical form.

This file is regenerated on every $outline-expand run. Gitignore it if you
do not want it tracked.
```

### Drift entries

For each cluster from step 3, render:

```
## <normalized form>

Variants observed in this run:
- "<variant 1 form>" — <count> occurrence(s) in: <section names>
- "<variant 2 form>" — <count> occurrence(s) in: <section names>
- ...

Suggested canonical: "<variant with highest count>"
```

Sort clusters by total occurrence count, descending. Truncate to the top 50 clusters if the run produced more (likely indicates the heuristic is over-firing on a noisy field; user can re-run with manual cleanup).

### Writer-logged terminology decisions

If `terminology_decisions` (from phase 02 step 7) is non-empty, append:

```
## Writer-logged terminology decisions

The writers explicitly logged the following decisions during this run. Consider
adopting them into .omx/omxr/agent-memory/paper-writer/nomenclature.md:

- (in <section>) <term> = <chosen-form>  — reason: <reason>
- ...
```

These are decisions the writers made consciously. The drift heuristic above is mechanical; this section is what the writer flagged on its own.

### No-drift case

If both the drift cluster list and `terminology_decisions` are empty, the file contains only the header plus:

```
No drift detected.

All scanned candidate-jargon terms used a single surface form across the
sections drafted in this run. No writer-logged terminology decisions either.
```

## Step 5 — Hand off to phase 04

Pass forward to phase 04:
- `paper_state` (post-write, post-status-update)
- `manuscript_root`
- `write_results` (list of per-section write outcomes from step 1)
- `drift_clusters` (list from step 3 — may be empty)
- `terminology_decisions` (from phase 02, unchanged)
- `drift_artifact_path` (`<manuscript_root>/terminology-drift.md`)
- `run_id`, `run_started_at`

Phase 04 uses these to render the user summary and append the `_run-log.jsonl` close + summary records.

## Failure modes

| Condition | Behavior |
|---|---|
| Parent directory of a section path cannot be created | Record write failure for that section; continue. |
| `Write` tool errors on a section file (e.g., PII-scrub block) | Record write failure for that section; do not abort. |
| `paper.json` write-back fails | Log error to run log; do not roll back section file writes. State on disk is now "prose updated, paper.json stale" — the user re-running `$sync` or `$outline-expand` reconciles. |
| `terminology-drift.md` write fails | Log warning; do not abort. Phase 04 still surfaces drift count from the in-memory list. |
| Zero sections succeeded in phase 02 | Phase 03 walks an all-failed `dispatch_results`; writes zero files; `paper_state` is untouched; `terminology-drift.md` contains the no-drift header (no sections to scan). Phase 04 reports the all-fail case. |
| Section file already contains `\section{...}` framing but framing-detection picks the wrong boundary | Fall back to full-overwrite; log a one-line warning into `write_results[i].framing_warning`. Phase 04 surfaces it. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure writes + lint.
- Does **not** call `$iterate-revision`. The drift artifact is the only output that ties to refinement; the user decides whether to iterate.
- Does **not** edit `nomenclature.md`. Writer-logged decisions are surfaced in the drift report, not auto-merged.
- Does **not** commit to git. No git operations from this engine, ever.
- Does **not** update `last_review_id`. Stale prior reviews are tolerated; the next `$iterate-revision` reviews fresh.
- Does **not** update `paper_state.figures` or trigger figure work. Figure design is `$figure-bake`'s engine.
- Does **not** clear failed-write entries from `paper.json` (e.g., revert a status). Failed writes leave `paper_state.sections[name]` exactly as it was before the run.
