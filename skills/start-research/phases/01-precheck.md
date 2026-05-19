# Phase 1 — Precheck

Verify that `$omxr-setup` has run. If not, offer to run it first.

## Detect `$omxr-setup` state

Check:

1. Does `AGENTS.md` exist at project root?
2. Does it contain all three marker blocks: `## Project context`, `## Research stack`, `## Language preference`?
3. Does `.omx/omxr/agent-memory/` exist with subdirectories for all 6 agents (`supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`)?
4. Does `./references.csv` exist? Does `paper/references.bib` exist?

If all four checks pass, set `SETUP_DONE = true`. If any fail, set `SETUP_DONE = false`.

## If `SETUP_DONE = false`

Use AskUserQuestion:

**Question:** "`$omxr-setup` hasn't installed the OMXR infrastructure on this project yet. `$omxr-setup` lays down the empty `AGENTS.md` blocks, agent-memory directories, research state files, bibliography files, and hook/check readiness that `$start-research` then fills in. Run `$omxr-setup` now and continue?"

**Options:**
1. **Yes — run `$omxr-setup` now, then continue (Recommended)** — invokes `$omxr-setup` automatically, then returns here for the interview.
2. **No — cancel** — exits. The user can run `$omxr-setup` manually later, then `$start-research`.

If user chooses **Yes**:
- Invoke the `omxr-setup` skill (read [`../../omxr-setup/SKILL.md`](../../omxr-setup/SKILL.md) and execute its 6 phases).
- When `$omxr-setup` reports complete, return here and continue to phase 2.

If user chooses **No**:
- Stop the flow. Print: "Cancelled. Run `$omxr-setup` first, then `$start-research`."
- Phase 7 will still run to produce a one-line report noting the cancellation.

## Record state for phase 2

If `SETUP_DONE = true` (or just made true by running setup), record:

- For each `AGENTS.md` placeholder field: current value or `[TBD]`.
- Existing `Preset overlay` value in `## Project context` (so phase 4 can skip re-applying).
- Existence of `Manuscript dir` content (so phase 6 can decide whether to invoke `manuscript-scaffold`).

Phase 2 uses this to ask **only about fields that are missing or still `[TBD]`**.
