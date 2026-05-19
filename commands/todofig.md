---
description: Compare a captured-figure deck against an outline document; produce a prioritized TODO of gaps (P0/P1/P2).
argument-hint: [optional figure identifier to focus on, e.g. "Fig4" or "R1"]
---

# /todofig

Thin dispatcher — the full figure-vs-outline gap analysis lives in the `todofig` skill so the slash-command surface stays small and the workflow can also be invoked outside `/todofig`.

## Dispatch

1. Read the bundled skill instructions: [`skills/todofig/SKILL.md`](../skills/todofig/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CLAUDE_PLUGIN_ROOT` and continue.
