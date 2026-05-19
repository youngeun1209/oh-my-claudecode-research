# `<agent-name>` agent — memory

<!--
  This file is auto-loaded into the session by the memory-load.sh hook
  at session start, so keep it concise — every line you write here ends
  up in the system prompt of every conversation that uses this agent.

  Schema:
  - Top-of-file metadata: agent name + last-synced marker.
  - Sections by topic, not by date. Update entries in place.
  - Linked topic files for detail that doesn't fit in 200 lines.
  - "What to save / NOT to save" rubric at the bottom.

  Rules:
  - Lines after ~200 may be truncated by the loader (depending on context budget).
    Keep this file as an INDEX. Push detail into linked topic files.
  - Organize by topic, not by date. If a fact changes, update in place;
    don't append a new entry that contradicts an old one.
  - Update or remove memories that turn out to be wrong or outdated.
  - Don't write duplicate memories — check before adding new ones.
-->

**Last synced:** [YYYY-MM-DD]
**Agent role:** [one line — what this agent owns in the project]

---

## Project state
<!-- What is the current shape of the project, from this agent's perspective? -->

- [Key fact 1, with date if it changes]
- [Key fact 2]
- ...

## Settled decisions
<!-- Things that are not up for re-discussion. Each entry should be terse. -->

- [Decision 1, on YYYY-MM-DD]
- [Decision 2]

## Open / unresolved
<!-- Things this agent is currently tracking but hasn't resolved. -->

- [ ] [Open item 1]
- [ ] [Open item 2]

## Linked topic files
<!--
  Detail that doesn't fit in 200 lines. Each topic file lives next to
  this MEMORY.md (e.g., `.claude/agent-memory/<agent>/<topic>.md`).
  Link them here so the agent knows where to look.
-->

- `<topic-1>.md` — [one-line description]
- `<topic-2>.md` — [one-line description]

## Drifts flagged at last sync
<!-- Auto-populated by /sync-style commands. Leave empty if not running such a command. -->

- [Drift 1]

---

## What to save here

- The current shape of decisions (hypothesis text, settled framings, locked nomenclature, hyperparameters, etc.)
- A pointer (filename) to detailed topic files
- Status of open items the agent is tracking
- Drifts flagged by sync commands

## What NOT to save here

- Raw data, results tables, or numbers — those live in the manuscript / analysis outputs
- In-progress drafts or session-specific task details
- Speculative items not yet decided
- Anything you can re-derive from the codebase by reading it
