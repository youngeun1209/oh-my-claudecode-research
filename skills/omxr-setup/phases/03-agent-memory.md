# Phase 3 — Agent Memory and Research State

Create durable project-local memory and state for the six research agents and orchestration engines.

## Part A — Agent memory

Create `.omx/omxr/agent-memory/<agent>/MEMORY.md` for:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

Rules:

- If the target `MEMORY.md` exists, skip it.
- If a legacy `.claude/agent-memory/<agent>/MEMORY.md` exists and the new target is missing, copy it once and add a short migration note header.
- Otherwise copy `templates/MEMORY.template.md` from the plugin root.
- Never overwrite user memory.

## Part B — Optional native agent templates

When project-scope native-agent delivery is selected, create `.codex/agents/omxr/<agent>.md` from tracked `agents/<agent>.md`.

Rules:

- Skip existing targets.
- Preserve tracked `agents/*.md` as source templates.
- User-scope delivery may instead target `${CODEX_HOME:-~/.codex}/agents/omxr/<agent>.md`.

## Part C — Research state

Create `.omx/state/omxr/` and seed:

- `paper.json`
- `reviews.json`
- `citations.json`
- `figures.json`
- `rebuttals.json`
- `_run-log.jsonl`

Rules:

- If `.omx/state/omxr/<name>.json` exists, skip it.
- Else if legacy `.claude/omcr-state/<name>.json` exists, copy it once.
- Else copy `develop/example-state/<name>.json` from the plugin root.
- Create `_run-log.jsonl` as an empty file if missing.
- Do not delete legacy state automatically.
