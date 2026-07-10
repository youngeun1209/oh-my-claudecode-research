---
description: When the canonical outline or the figure deck is bumped to a new version, find every file that points to the OLD filename/version and update it to the NEW one. Reads the current values from CLAUDE.md ## Research stack (Deck file / Outline file); prompts for the new files if not @-mentioned. Also surfaces obsolete archive files as delete candidates (confirm-gated, never auto-deletes).
argument-hint: "@-mention the current outline + deck (e.g. @outline_v5.md @figures_v8.key), or run bare to be prompted"
---

# /update-version

Thin dispatcher — the full version-propagation workflow lives in the `update-version` skill so the slash-command surface stays small and the workflow can also be invoked outside `/update-version`.

## Dispatch

1. Read the bundled skill instructions: [`skills/update-version/SKILL.md`](../skills/update-version/SKILL.md).
2. Follow that `SKILL.md` exactly, treating the user's arguments as:

   ```text
   $ARGUMENTS
   ```

If the file is not directly readable from the current working directory, locate it under the active `CLAUDE_PLUGIN_ROOT` and continue.
