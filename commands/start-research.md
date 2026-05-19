---
description: Interview-driven first-research-project initialization — fills the AGENTS.md placeholders that $omxr-setup scaffolded (working title, field, hypothesis, target venue, datasets, narrative spine), optionally applies a domain preset to agent memory, and scaffolds the LaTeX manuscript directory via the manuscript-scaffold skill. Requires $omxr-setup to have run first — will offer to run it if not. Safe to re-run; never overwrites your filled-in answers.
argument-hint: [optional: "minimal" | "neuro-fmri" | "no-overlay"]
---

# $start-research

Interview-style flow. Thin dispatcher — the full first-research-project initialization lives in the `start-research` skill so the skill surface stays small and the workflow can also be invoked outside of `$start-research`.

This is the "deep interview" complement to `$omxr-setup`'s "install" role. `$omxr-setup` lays down empty AGENTS.md marker blocks; `$start-research` walks the user through filling them.

## Dispatch

1. Read the bundled skill instructions: [`skills/start-research/SKILL.md`](../skills/start-research/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CODEX_PLUGIN_ROOT` and continue.
