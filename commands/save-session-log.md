---
description: Save a structured record of the current session — what was discussed, what was analyzed/built, where files were saved, decisions made, open next steps — to the session-logs dir. Writes one dated Markdown file per invocation and propagates durable results/decisions into the wiki knowledge vault.
argument-hint: "[optional: short slug for the filename, e.g. 'fig4-bottleneck' — auto-derived from the session if omitted]"
---

# /save-session-log

Thin dispatcher — the full session-journaling workflow lives in the `save-session-log` skill so the slash-command surface stays small and the workflow can also be invoked outside `/save-session-log`.

## Dispatch

1. Read the bundled skill instructions: [`skills/save-session-log/SKILL.md`](../skills/save-session-log/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CLAUDE_PLUGIN_ROOT` and continue.
