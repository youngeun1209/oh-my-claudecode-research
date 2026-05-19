# Phase 1 — State check

Inspect what already exists. Subsequent phases use this state to skip work that's already done.

Check and record:

1. **`CLAUDE.md`** at project root? If yes, scan for:
   - `## Project context` block (present? has content beyond `[TBD]` placeholders?)
   - `## Research stack` block (present? has content?)
   - `## Language preference` block (present? has content?)

2. **`.claude/agent-memory/`** directory? For each of the 6 agents (`supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`), does `MEMORY.md` exist?

3. **Bibliography files** at default paths?
   - `paper/references.bib`
   - `./references.csv` (project root)

4. **`.claude/settings.json`** — does it exist? Read and record:
   - Current `permissions.allow` array
   - Any broad wildcards (`"Bash"`, `"Write"`, `"Edit"` without parentheses) — these trigger a narrowing offer in phase 5
   - Any invalid entries (spaces in tool names like `"Web Fetch"` — these don't actually match any tool and should be removed)

5. **Hook registration** — the plugin manifest wires `hooks/hooks.json` automatically; just note in the report whether `.claude/agent-memory/` is reachable so `memory-load.sh` can find it on next session start.

Report this state to the user in 2–3 lines before running phase 2 — it sets expectations on what will be created vs. left alone. Record the gathered state so phases 2 / 3 / 4 / 5 can consult it.
