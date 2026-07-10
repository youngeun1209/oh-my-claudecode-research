---
description: Read the project's Markdown corpus, build a genuine understanding of the study, and report a concise summary + honest current-status snapshot. The session-orientation command — read-only, no side effects. Light/full modes.
argument-hint: [light | full | a focus area e.g. "R3" or "figures"]
---

# /session-start

Thin dispatcher — the full read-and-report orientation workflow lives in the `session-start` skill so the slash-command surface stays small and the workflow can also be invoked outside `/session-start` (e.g. from a SessionStart hook in light mode).

## Dispatch

1. Read the bundled skill instructions: [`skills/session-start/SKILL.md`](../skills/session-start/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CLAUDE_PLUGIN_ROOT` and continue.
