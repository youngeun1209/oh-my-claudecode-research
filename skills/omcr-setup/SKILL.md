---
name: omcr-setup
description: Install OMCR infrastructure in a project — scaffold empty CLAUDE.md marker blocks (`## Project context` / `## Research stack` / `## Language preference`), create `.claude/agent-memory/` for the 6 core agents with canonical-template MEMORY.md, initialize empty `references.bib` + `references.csv`, and install a curated permission allowlist in `.claude/settings.json`. Does NOT ask about the user's research project (no working title / hypothesis / venue / preset interview). For that, run `/start-research` after this completes. Safe to re-run — never overwrites existing user content.
---

# Setup

Install-style flow that lays down the **infrastructure** OMCR needs to operate in a project. This is OMCR's analog of OMC's `/omc-setup` — no research-interview questions, no preset selection, no manuscript scaffolding. Just makes the plugin work.

After `/omcr-setup` completes, the user should run `/start-research` for interview-style first-project initialization.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

Safe to re-run. Diffs against current state; only adds what is missing.

## What this installs

1. **CLAUDE.md infrastructure** — `## Project context`, `## Research stack`, `## Language preference` blocks with placeholder fields. (Filled in later by `/start-research`.)
2. **Agent memory directories** — `.claude/agent-memory/<agent>/MEMORY.md` for the 6 core agents, seeded from the canonical template. Existing files are never touched.
3. **Bibliography files** — empty `paper/references.bib` (with header comment) and `references.csv` (with header row) at default paths. Existing files are never touched.
4. **Permission allowlist** — curated `.claude/settings.json` so common research-flow tools (read-only git, file search, edits, LaTeX build, citation lookups, figure crop) don't prompt every time. Dangerous operations (git write, file deletion, wildcard bash) are intentionally excluded so they always prompt.

## What this explicitly does NOT do

- Ask about your project (working title, hypothesis, target venue, datasets, etc.)
- Pick or apply a domain preset (`neuro-fmri`, etc.)
- Scaffold the LaTeX manuscript directory
- Clone Overleaf or commit anything

All of those belong to `/start-research`.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — State check.** Read [`phases/01-state-check.md`](phases/01-state-check.md).
2. **Phase 2 — CLAUDE.md scaffold.** Read [`phases/02-claude-md-scaffold.md`](phases/02-claude-md-scaffold.md).
3. **Phase 3 — Agent memory.** Read [`phases/03-agent-memory.md`](phases/03-agent-memory.md).
4. **Phase 4 — Bibliography.** Read [`phases/04-bibliography.md`](phases/04-bibliography.md).
5. **Phase 5 — Permissions.** Read [`phases/05-permissions.md`](phases/05-permissions.md).
6. **Phase 6 — Report.** Read [`phases/06-report.md`](phases/06-report.md).

## Re-running policy

- `CLAUDE.md` marker blocks are inserted only if missing. Existing blocks are inspected but not overwritten.
- Existing `MEMORY.md` files are never overwritten (phase 3).
- Existing `references.bib` / `references.csv` are never overwritten (phase 4).
- Permission allowlist (phase 5) prompts the user before replacing or merging. Existing broad wildcards trigger a narrowing offer with backup to `.claude/settings.json.backup.YYYY-MM-DD`.

## Final recommendation

After phase 6's report, recommend the user run `/start-research` to fill in their project context and scaffold the manuscript.
