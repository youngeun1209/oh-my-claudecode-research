# Phase 2 — CLAUDE.md scaffold

Insert empty marker blocks into the project's `CLAUDE.md`. **Do not** ask the user about their research — that is `/start-research`'s job. Just install the structure with `[TBD]` placeholders so `/start-research` has somewhere to write.

## If `CLAUDE.md` does not exist

Create it with the canonical layout below as the entire file.

## If `CLAUDE.md` exists

Preserve all existing content (e.g. an existing `# <repo name>` heading, a "Repository status" section). For each of the three blocks below:

- If the `## <Block name>` heading is already present, **leave the block untouched** — even if its fields are all `[TBD]`. (The user may be in the middle of filling them, or a previous `/start-research` may have populated some.)
- If absent, append the empty block to the end of the file.

## Canonical block layout

````markdown
## Project context

- **Working title:** [TBD]
- **Field:** [TBD]
- **Target venue:** [TBD]
- **Backup venues:** [TBD]
- **Central hypothesis:** [TBD]
- **Research topic:** [TBD]
- **Datasets:** [TBD]
- **Narrative spine:**
  1. *Gap:* [TBD]
  2. *Question:* [TBD]
  3. *Approach:* [TBD]
  4. *Finding:* [filled as results emerge]
  5. *Implication:* [TBD]
- **Preset overlay:** none

## Research stack (used by /todofig, /sync, /start-research, and the verify-citation + cropfig skills)

- **Deck file:** [TBD — path to .key or .pptx]
- **Outline file:** outline.md
- **Figure count:** 8
- **Result pattern:** `^### Result (\d+)`
- **Report language:** English
- **Report output dir:** ./todofig_reports/
- **Sync report dir:** ./sync_reports/
- **Figure PDF dir:** [defaults to <dirname(Deck file)>/pdf/]
- **Figure PNG dir:** [defaults to <dirname(Deck file)>/png/]
- **Manuscript dir:** paper/
- **BibTeX file:** paper/references.bib
- **Summary file:** references.csv
- **CrossRef email:** [optional — recommended for verify-citation polite-pool access]
- **Overleaf git URL:** [optional — only if Overleaf Git Integration is enabled (paid plan)]

## Language preference

- **User-dialog language:** English
- **Manuscript language:** English  (do not change — manuscripts stay in English for venue compatibility)
````

Show the resulting block(s) to the user before writing. After writing, report:

- which blocks were added,
- which were already present (and left alone).

## Why placeholders, not interview answers

`/omcr-setup` is install-style — it lays down the structure quickly so the plugin (hooks, agents, commands) works. `/start-research` is the interview-style flow that walks the user through filling these `[TBD]` placeholders. Splitting them lets users re-run `/omcr-setup` to refresh infrastructure without re-doing the interview, and lets users re-run `/start-research` to revise their project framing without re-installing infrastructure.
