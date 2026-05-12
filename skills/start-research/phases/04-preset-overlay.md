# Phase 4 — Preset overlay (agent memory)

Apply the domain preset selected in phase 2's section C to agent memory templates. Manuscript-side preset hooks (e.g. journal documentclass) happen in phase 5 inside the `manuscript-scaffold` skill — not here.

## When to skip

- `preset_arg = minimal` or `preset_arg = no-overlay`: skip this phase entirely.
- No preset was selected during the interview (`Preset overlay: none`): skip.

## Apply preset to agent memory

For each of the 6 agents:

1. Check if `examples/<preset>/memory-templates/<agent>/MEMORY.md` exists in the plugin.
2. If yes, compare `.claude/agent-memory/<agent>/MEMORY.md` (the user's project) against the canonical template at `templates/MEMORY.template.md`:
   - **Byte-identical** (user hasn't started writing in it) → replace with the preset template. Report `replaced-from-canonical`.
   - **Different** (user has modified it) → leave untouched. Report `skipped-modified`.
3. If no preset template exists for that agent → leave untouched. Report `no-preset-template`.

## Optional agent body overlay

For `neuro-fmri`, the plugin ships an agent body overlay at `examples/neuro-fmri/agents/analysis-implementer.md`. When the plugin is installed via `/plugin install`, Claude Code loads the **plugin core** `agents/analysis-implementer.md`, not the preset overlay. The overlay is included in `examples/` as a reference for users who want to copy it manually into `.claude/agents/analysis-implementer.md` in their project, which overrides the plugin core.

Mention this in the phase 6 report:

> "Neuro-fMRI body overlay available at `examples/neuro-fmri/agents/analysis-implementer.md` if you want neuro-flavored agent behavior. Copy to `.claude/agents/analysis-implementer.md` to apply."

Do not auto-copy it — that's an explicit user action.

## Record for phase 6

Track per-agent outcome (`replaced-from-canonical` / `skipped-modified` / `no-preset-template`) so the report can summarize.
