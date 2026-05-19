---
name: literature-sweep
description: Find, summarize, and verify N papers on a topic, then drop verified entries into `references.bib` and the literature summary CSV. Dispatches `@literature-curator` (one or many instances) over a CrossRef/OpenAlex candidate list, runs every survivor through the `verify-citation` skill, and writes the run summary to `citations.json.last_sweep`. Sequential by default; opt-in `--parallel N` (1 ≤ N ≤ 4) fan-out for speed. Safe to re-run; idempotent against duplicate DOIs (existing BibTeX entries are skipped, not double-added).
writes: [citations]
cost_estimate_tokens: 50000
---

# $literature-sweep

This engine is the parallel-dispatch worked example: the first OMXR engine that fans out across several `@literature-curator` instances in a single message and then re-collects their work. The other Phase 2 engines (`$respond-reviewer`, `$figure-bake`, `$outline-expand`) all reference this skill's phase 03 for the parallel-dispatch pattern.

If you are reading this because Codex's skill auto-discovery surfaced it: invoke it via `$literature-sweep <topic>`. Do not hand-edit `references.bib`, the summary CSV, or `.omx/state/omxr/citations.json` while a run is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
$literature-sweep <topic> [--n N] [--depth basic|deep] [--source crossref|openalex|both] [--parallel P]
```

| Flag | Default | Purpose |
|---|---|---|
| `--n` | `20` | Target number of verified entries (final). Phase 02 pulls `3 * N` candidates; phase 04 dedupes and trims; phase 05 verifies. |
| `--depth` | `basic` | `basic` extracts title/authors/year/venue/abstract. `deep` adds a per-entry curator dispatch for methodology + key findings. |
| `--source` | `both` | `crossref` \| `openalex` \| `both`. `both` queries each source and merges. |
| `--parallel` | `1` | Phase 03 concurrent curator instances. Clamped to `1 ≤ P ≤ 4` (Phase 2 decision §1). Phase 01 warns and clamps values `> 4`; aborts on `< 1`. |

Examples:

- `$literature-sweep "neural manifolds in motor cortex"` — defaults: 20 entries, basic depth, both sources, sequential.
- `$literature-sweep "diffusion models for protein design" --n 30 --parallel 4` — 30 entries, four curator instances in parallel.
- `$literature-sweep "transformer attention sparsity" --depth deep --source crossref` — deeper extraction, CrossRef only, sequential.

## The pipeline

```
phase 01 — precheck         (validate topic, ping APIs, resolve bib + CSV paths, clamp --parallel)
phase 02 — search           (CrossRef and/or OpenAlex → 3N candidates, dedupe by DOI)
phase 03 — parallel-read    (@literature-curator × P, each handles a batch — BibTeX + CSV row per paper)
phase 04 — deduplicate      (merge batches, dedupe by DOI, score, trim to N)
phase 05 — verify           (verify-citation skill per survivor — HARD GATE)
phase 06 — finalize         (append to references.bib + CSV; write citations.json.last_sweep; append to _run-log.jsonl)
```

Phases 02–05 form the read-then-verify pipeline. Unlike `$iterate-revision`, there is no inner loop — each phase runs once. The parallel concurrency lives entirely in phase 03 and is transparent to phases 04 and 05.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — Precheck.** Read [`phases/01-precheck.md`](phases/01-precheck.md).
2. **Phase 2 — Search.** Read [`phases/02-search.md`](phases/02-search.md).
3. **Phase 3 — Parallel read.** Read [`phases/03-parallel-read.md`](phases/03-parallel-read.md).
4. **Phase 4 — Deduplicate.** Read [`phases/04-deduplicate.md`](phases/04-deduplicate.md).
5. **Phase 5 — Verify.** Read [`phases/05-verify.md`](phases/05-verify.md).
6. **Phase 6 — Finalize.** Read [`phases/06-finalize.md`](phases/06-finalize.md).

## Composition

This engine imports the following primitives from `skills/orchestrate/`:

- [`phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — read `citations.json` in phase 01 (bootstrap if missing) and re-read in phase 06 for the durable `last_sweep` write.
- [`phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — dispatch `@literature-curator`. Phase 03 uses it in two shapes: a single sequential call per batch when `--parallel 1`, or multiple concurrent calls in one assistant message when `--parallel > 1` (Codex Agent-tool parallel invocation).
- [`phases/04-loop.md`](../orchestrate/phases/04-loop.md) — used only for the `_run-log.jsonl` `phase: "start"` + `phase: "end"` records and `run_id` generation. There is **no inner iteration loop in this engine** (one shot, not iterative), so phase 04 of orchestrate is invoked with `max_iter = 1` and a trivial `always-after-n` verdict rule that emits `DONE` immediately. The real engine logic lives in phases 02–06 here, not inside the loop body.

This engine **does not** import `orchestrate/phases/03-evaluate.md` — there is no severity-threshold verdict to compute. The verification gate in phase 05 is a hard pass/fail per entry, not an aggregate verdict over the run.

## Integration with `verify-citation`

Phase 05 calls the standalone [`skills/verify-citation/SKILL.md`](../verify-citation/SKILL.md) skill **once per surviving entry** (after phase 04's dedupe), via its `--doi <doi>` mode (we have a DOI by then; we are not auditing an existing BibTeX file). The skill returns one of `PASS | MISMATCH | NOT_FOUND | NOT_VERIFIED` per entry.

The hard gate (Phase 2 decision §1, locked):

- `PASS` → entry is added to `references.bib` and to the summary CSV; recorded in `citations.json.verified`.
- `MISMATCH` / `NOT_FOUND` / `NOT_VERIFIED` → entry is rejected; recorded in `citations.json.last_sweep.rejected` with reason. **Never written to `references.bib`.**

The user reviews `citations.json.last_sweep.rejected` after the run and decides whether to manually rescue any rejected entries (typo in DOI, network outage, etc.).

## Cost model

Per-entry cost is dominated by:

- One `@literature-curator` dispatch per `--parallel`-batch in phase 03 (handles up to `3N / P` candidates per dispatch).
- One `verify-citation` call per surviving entry in phase 05 (cheap; a single HTTP roundtrip per source, stdlib-only Python).
- An optional second curator dispatch per survivor when `--depth deep` (rough cost doubling for the dispatch portion).

With `--n 20 --parallel 1 --depth basic`: ~1 curator dispatch over 60 candidates + 20 verify-citation calls. The frontmatter `cost_estimate_tokens: 50000` is the coarse upper bound for `$supervisor-drive` budget gating (Phase 3 §6); actuals land in `_run-log.jsonl` post-hoc per Phase 0 decision §6.

`--parallel 4` does not multiply token cost — the work is sharded, not duplicated — but it does multiply *concurrent* token throughput, which is the relevant constraint for the runtime's rate limiter.

## Locked decisions honored

From [`develop/phase-2-decisions.md`](../../develop/phase-2-decisions.md) §1:

- **Sequential default.** `--parallel` defaults to `1`. Power users opt in.
- **Clamp 1 ≤ N ≤ 4.** Phase 01 warns and clamps `> 4`; aborts on `< 1`.
- **Parallel failure mode.** If one batch errors during the parallel dispatch, the engine falls back to sequential for the remaining batches and records a one-line warning in `citations.json.last_sweep.notes`. No in-loop retry; the user can re-run with `--parallel 1` if they want a clean sequential pass.
- **Hard verify-gate.** Unverified entries never enter `references.bib`. Always recorded in `citations.json.last_sweep.rejected` with a reason so the user can audit.

## What this engine does NOT do

- Does **not** fabricate references. Every entry survives `verify-citation` before being added — by construction, fabricated DOIs cannot pass.
- Does **not** decide `bucket`, `our_use`, or `cited_sections` columns in the summary CSV. Those are human-curated columns that the `literature-curator` agent leaves blank in a sweep; the user (or a later curator pass keyed to a specific manuscript section) fills them.
- Does **not** invoke `$iterate-revision`, `$respond-reviewer`, `$figure-bake`, or `$outline-expand`. Engines are leaves (Phase 2 decision §5).
- Does **not** auto-resolve `[CITE: ...]` placeholders inside the manuscript. That is the standalone `@literature-curator` agent's day-job. `$literature-sweep` is about building a *bibliography*, not patching a specific placeholder.
- Does **not** commit to git or push to a remote. Run `$sync` afterward if you want a commit-and-push snapshot.
- Does **not** re-fetch full PDFs. Abstract-level metadata only. Deeper claim-fit checks need a human (or a dedicated future engine) to read the paper.

## Re-running policy

- Topic already in `citations.json.last_sweep.topic` and the user re-runs the same topic → the engine still runs. Newer candidates may exist on CrossRef/OpenAlex since the last sweep; dedupe against the BibTeX file (not against last sweep) ensures no double-adds.
- A DOI already in `references.bib` (case-insensitive) → phase 03 / 04 skip it, count it toward the `--n` target, and the curator dispatch never re-extracts it. The summary CSV row is left as-is.
- A DOI already in `citations.json.verified` (from a prior sweep) but missing from `references.bib` (e.g., user hand-edited the bib) → treated as new; re-verified; re-added.
- Network outage during phase 02 or phase 05 → engine emits a partial result with `notes: "API <name> unreachable; partial result"` in `last_sweep`. Any entries that *did* verify are still added.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine composes.
- [`../verify-citation/SKILL.md`](../verify-citation/SKILL.md) — the standalone verifier called from phase 05.
- [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) — pattern reference; voice and structure of this skill mirror it.
- [`../../agents/literature-curator.md`](../../agents/literature-curator.md) — the primary dispatched persona; phase 03 inlines its body via `orchestrate/phases/02-dispatch.md`.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — `citations.json` schema reference, including the `last_sweep` block this engine writes.
- [`../../develop/phase-2-additional-engines.md`](../../develop/phase-2-additional-engines.md) — full design rationale (Engine 2).
- [`../../develop/phase-2-decisions.md`](../../develop/phase-2-decisions.md) — locked decisions §1 (concurrency).
