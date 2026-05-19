---
name: omxr-setup
description: Setup oh-my-codex-research project infrastructure: AGENTS.md research blocks, .omx/state/omxr schemas, .omx/omxr agent memory, optional .codex/agents/omxr native-agent templates, bibliography files, and hook/fallback readiness checks. Requires base oh-my-codex runtime setup.
---

# OMXR Setup

Install-style flow that lays down the **project-local research infrastructure** OMXR needs. This is the research-edition companion to base `omx setup`: base `omx setup` owns Codex/OMX runtime readiness, while `$omxr-setup` owns research project scaffolding.

After `$omxr-setup` completes, run `$start-research` for interview-style first-project initialization.

**When invoked, execute the workflow below. Do not only summarize these instructions.**

Safe to re-run. Only create missing files or refresh marker-bounded OMXR sections.

## What this installs

1. **AGENTS.md research blocks** — `## Project context`, `## Research stack`, and `## Language preference` placeholders.
2. **Research agent memory** — `.omx/omxr/agent-memory/<agent>/MEMORY.md` for the six core agents, seeded from `templates/MEMORY.template.md`.
3. **Research state** — `.omx/state/omxr/{paper,reviews,citations,figures,rebuttals}.json` and `.omx/state/omxr/_run-log.jsonl`.
4. **Optional native agent templates** — `.codex/agents/omxr/<agent>.md` for project-scope agent delivery when selected.
5. **Bibliography files** — `paper/references.bib` and `references.csv`.
6. **Hook/check readiness** — report whether memory load, setup nudge, PII scrub, and citation warning are native hooks, runtime fallbacks, or explicit checks for this project.

## What this explicitly does NOT do

- Install the base OMX runtime. Run `omx setup` first when `omx doctor` reports missing setup.
- Ask about the research content itself.
- Pick or apply a domain preset.
- Scaffold the manuscript directory.
- Clone Overleaf or commit anything.
- Delete legacy `.codex/` or `.omx/` state automatically.

## Phase execution

Execute phases sequentially:

1. **Phase 1 — State check.** Read [`phases/01-state-check.md`](phases/01-state-check.md).
2. **Phase 2 — AGENTS.md scaffold.** Read [`phases/02-agents-md-scaffold.md`](phases/02-agents-md-scaffold.md).
3. **Phase 3 — Agent memory and state.** Read [`phases/03-agent-memory.md`](phases/03-agent-memory.md).
4. **Phase 4 — Bibliography.** Read [`phases/04-bibliography.md`](phases/04-bibliography.md).
5. **Phase 5 — Hook/check readiness.** Read [`phases/05-permissions.md`](phases/05-permissions.md).
6. **Phase 6 — Report.** Read [`phases/06-report.md`](phases/06-report.md).

## Re-running policy

- `AGENTS.md` marker blocks are inserted only if missing or refreshed inside OMXR-owned markers.
- Existing `MEMORY.md` files are never overwritten.
- Existing state JSON files are never overwritten.
- Existing bibliography files are never overwritten.
- Hook/check readiness is reported, not force-rewired, unless an OMXR-owned wrapper is explicitly missing and safe to create.

## Legacy migration

If an old research project contains `.claude/agent-memory/<agent>/MEMORY.md` or `.claude/omcr-state/<name>.json`, surface it to the user and copy it only when the new `.omx/...` target is missing. Do not remove the old directory automatically.
