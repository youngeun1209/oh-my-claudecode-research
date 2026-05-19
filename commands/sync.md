---
description: Reconcile current state (captured figure deck) with final goal (outline document), refresh agent memories with drifts, optionally embed cropped figures into a target document. Produces a status snapshot — not a TODO (use $todofig for that).
argument-hint: [optional scope hint, e.g. "memory-heavy", "outline just changed", "status only"]
---

# $sync

Thin dispatcher — the full status-reconciliation workflow lives in the `sync` skill so the skill surface stays small and the workflow can also be invoked outside `$sync`.

## Dispatch

1. Read the bundled skill instructions: [`skills/sync/SKILL.md`](../skills/sync/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CODEX_PLUGIN_ROOT` and continue.
