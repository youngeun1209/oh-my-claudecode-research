# Phase 1 — State Check

Inspect project-local readiness and record what later phases should create or skip.

Check:

1. `AGENTS.md` at the project root:
   - Has `## Project context`?
   - Has `## Research stack`?
   - Has `## Language preference`?
   - Has marker-bounded OMXR content?

2. Base OMX runtime:
   - If available, run or reference `omx doctor` status.
   - If not available, warn that `$omxr-setup` assumes base `omx setup` has already prepared Codex/OMX runtime hooks and config.

3. Agent memory:
   - `.omx/omxr/agent-memory/<agent>/MEMORY.md` for each of:
     `supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`.

4. Research state:
   - `.omx/state/omxr/paper.json`
   - `.omx/state/omxr/reviews.json`
   - `.omx/state/omxr/citations.json`
   - `.omx/state/omxr/figures.json`
   - `.omx/state/omxr/rebuttals.json`
   - `.omx/state/omxr/_run-log.jsonl`

5. Optional native agents:
   - `.codex/agents/omxr/<agent>.md` when project-scope native-agent delivery is selected.

6. Bibliography files:
   - `paper/references.bib`
   - `references.csv`

7. Hook/check readiness:
   - Is `.codex/hooks.json` present?
   - Are OMXR hook wrappers installed or should the project rely on explicit checks?
   - Is `.omx/omxr/scrub-patterns.txt` present?

Report the state in 2-3 lines before phase 2. Preserve the gathered state for later phases.
