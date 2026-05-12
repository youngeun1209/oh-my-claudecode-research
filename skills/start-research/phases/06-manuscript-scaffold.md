# Phase 5 — Manuscript scaffold (delegated)

This phase is **always run** unless the user explicitly opted out during phase 2 by setting `Manuscript dir` to an empty value. In that case, skip this phase entirely and continue to phase 6.

## Delegate to the `manuscript-scaffold` skill

Read [`../../manuscript-scaffold/SKILL.md`](../../manuscript-scaffold/SKILL.md) and follow its instructions, passing these inputs (resolved during phases 2 / 3):

| Skill input | Source |
|---|---|
| `MANUSCRIPT_DIR` | `## Research stack` → `Manuscript dir` |
| `TARGET_VENUE` | `## Project context` → `Target venue` (may be empty / `[TBD]`) |
| `OVERLEAF_GIT_URL` | `## Research stack` → `Overleaf git URL` (may be empty) |
| `WORKING_TITLE` | `## Project context` → `Working title` (may be empty / `[TBD]`) |

The skill runs four internal phases:

1. State check — decide whether the manuscript dir is safe to populate.
2. Journal template lookup — match `TARGET_VENUE` against the bundled registry, confirm before rewriting `\documentclass`.
3. Skeleton copy (with optional Overleaf clone + credential caching).
4. Commit on the default branch, then ask before pushing.

…and returns a structured summary. Fold that summary into phase 6's report under "Manuscript scaffold" / "Overleaf" / "Branch / commit" / "Deferred push command".

## On early stop from the skill

If the skill stops early (existing content in the manuscript dir, user declined Overleaf clone, etc.), continue to phase 6 and surface the stop reason in the report. **Do not retry the skill from `/start-research` without user direction** — re-running `/start-research` after the user manually resolves the blocker is the right path.
