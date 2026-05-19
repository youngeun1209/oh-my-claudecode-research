# oh-my-codex-research (OMXR)

This repository is the research edition of `oh-my-codex`: a Codex/OMX workflow bundle for academic research projects.

## Operating Contract
- Use `oh-my-codex/` as the upstream runtime reference; do not rewrite it for research-edition changes unless an explicit integration requirement proves the need.
- Codex plugin discovery lives in `.codex-plugin/plugin.json`.
- Base runtime setup belongs to `omx setup`.
- Research-project scaffolding belongs to `$omxr-setup`.
- Project guidance lives in `AGENTS.md`, with OMXR sections inserted or refreshed without overwriting unrelated user guidance.
- Generated project state is local and must not be committed when it contains real research details or PII.

## Research Stack
`$omxr-setup` creates or refreshes these project-local surfaces:

- `.omx/state/omxr/{paper,reviews,citations,figures,rebuttals}.json`
- `.omx/state/omxr/_run-log.jsonl`
- `.omx/omxr/agent-memory/<agent>/MEMORY.md`
- `.codex/agents/omxr/<agent>.md` when project-scope native agent installation is selected

The six research agents are:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

## Language Preference
Scientific artifacts default to academic English. User-facing status may follow the user's language preference for the current project.

## Safety
- PII and unpublished project details belong only in local generated state, never tracked source files.
- Hook behavior must be verified against Codex/OMX support. If a native hook cannot provide exact behavior, ship an explicit skill/check fallback and document the boundary.
- Remaining legacy references are allowed only in migration notes, compatibility aliases, or historical context.
