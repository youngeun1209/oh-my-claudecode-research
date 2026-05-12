# Phase 3 — Agent memory

Create `.claude/agent-memory/<agent>/` for each of the 6 core agents and seed each with a `MEMORY.md` from the canonical template at `templates/MEMORY.template.md` (in the plugin root).

Agents to scaffold:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

For each agent:

- If `.claude/agent-memory/<agent>/MEMORY.md` already exists, **skip** — do not overwrite.
- Otherwise, copy `templates/MEMORY.template.md` (from the plugin root) to that path.

Always use the **canonical template** here. Preset-specific templates (e.g. `examples/neuro-fmri/memory-templates/<agent>/MEMORY.md`) are applied later by `/start-research`'s preset-overlay phase — only if the user selects a preset AND the existing `MEMORY.md` is still byte-identical to the canonical template (i.e. user hasn't started writing in it).

Record what was created vs. skipped so phase 6 can summarize.

## Why preset templates aren't applied here

`/omcr-setup` runs without knowing the user's domain. Applying a neuro-fMRI memory template to a project that turns out to be astrophysics would create misleading context. Canonical-template seeding is always safe; preset application is opt-in via `/start-research`.
