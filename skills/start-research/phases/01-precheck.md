# Phase 1 — Precheck

Verify that `/omcr-setup` has run. If not, offer to run it first.

## Detect `/omcr-setup` state

Check:

1. Does `CLAUDE.md` exist at project root?
2. Does it contain all three marker blocks: `## Project context`, `## Research stack`, `## Language preference`?
3. Does `.claude/agent-memory/` exist with subdirectories for all 6 agents (`supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`)?
4. Does `./references.csv` exist? Does `paper/references.bib` exist?

If all four checks pass, set `SETUP_DONE = true`. If any fail, set `SETUP_DONE = false`.

## If `SETUP_DONE = false`

Use AskUserQuestion:

**Question:** "`/omcr-setup` hasn't installed the OMCR infrastructure on this project yet. `/omcr-setup` lays down the empty `CLAUDE.md` blocks, agent-memory directories, bibliography files, and permission allowlist that `/start-research` then fills in. Run `/omcr-setup` now and continue?"

**Options:**
1. **Yes — run `/omcr-setup` now, then continue (Recommended)** — invokes `/omcr-setup` automatically, then returns here for the interview.
2. **No — cancel** — exits. The user can run `/omcr-setup` manually later, then `/start-research`.

If user chooses **Yes**:
- Invoke the `omcr-setup` skill (read [`../../omcr-setup/SKILL.md`](../../omcr-setup/SKILL.md) and execute its 6 phases).
- When `/omcr-setup` reports complete, return here and continue to phase 2.

If user chooses **No**:
- Stop the flow. Print: "Cancelled. Run `/omcr-setup` first, then `/start-research`."
- Phase 6 will still run to produce a one-line report noting the cancellation.

## Record state for phase 2

If `SETUP_DONE = true` (or just made true by running setup), record:

- For each `CLAUDE.md` placeholder field: current value or `[TBD]`.
- Existing `Preset overlay` value in `## Project context` (so phase 4 can skip re-applying).
- Existence of `Manuscript dir` content (so phase 5 can decide whether to invoke `manuscript-scaffold`).

Phase 2 uses this to ask **only about fields that are missing or still `[TBD]`**.
