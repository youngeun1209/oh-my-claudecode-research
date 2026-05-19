# Phase 2 — AGENTS.md Scaffold

Ensure the project has research guidance without overwriting unrelated user guidance.

## Behavior

1. If `AGENTS.md` is missing, create it with:
   - `# Project Guidance`
   - `## Project context`
   - `## Research stack`
   - `## Language preference`
   - marker-bounded OMXR section:
     `<!-- OMXR:RESEARCH:START -->` / `<!-- OMXR:RESEARCH:END -->`

2. If `AGENTS.md` exists, insert missing blocks only. Do not remove user text.

3. Refresh only content inside the OMXR markers. The marker section should state:
   - this project uses `oh-my-codex-research`
   - research state is under `.omx/state/omxr/`
   - research agent memory is under `.omx/omxr/agent-memory/`
   - optional project-scope agents are under `.codex/agents/omxr/`
   - `$start-research` fills project-specific research fields after `$omxr-setup`

4. If old Codex-specific legacy guidance exists in another file, do not delete it automatically. Mention migration in the final report.

## Placeholder blocks

Use concise placeholders:

```markdown
## Project context
- Working title: [TBD]
- Field: [TBD]
- Target venue: [TBD]
- Central hypothesis: [TBD]
- Narrative spine: [TBD]

## Research stack
- Manuscript root: manuscript/
- Outline path: manuscript/outline.md
- Figure deck: [TBD]
- BibTeX file: paper/references.bib
- Literature summary: references.csv
- Data root: ./data/

## Language preference
- Manuscript language: English
- User-facing status language: [TBD]
```
