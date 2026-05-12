# Phase 3 — Fill CLAUDE.md

Write the fields gathered in phase 2 into the project's `CLAUDE.md`, replacing `[TBD]` placeholders inside the three marker blocks. Preserve everything else in the file.

Use this canonical layout for the three blocks — substitute interview answers for `<...>` and leave `[TBD: <reason>]` for fields the user genuinely skipped.

````markdown
## Project context

- **Working title:** <title or [TBD]>
- **Field:** <field>
- **First author / PI:** <first author> / <PI>
- **Target venue:** <venue or [TBD: short note]>
- **Backup venues:** <comma-separated or [TBD]>
- **Central hypothesis:** <one sentence or [TBD: short note]>
- **Research topic:** <one-two sentences or [TBD]>
- **Datasets:** <name, source, modality, status — or [TBD: short note]>
- **Narrative spine:**
  1. *Gap:* <...>
  2. *Question:* <...>
  3. *Approach:* <...>
  4. *Finding:* [filled as results emerge]
  5. *Implication:* <... or [TBD]>
- **Preset overlay:** <name or none>

## Research stack (used by /todofig, /sync, /start-research, and the verify-citation + cropfig skills)

- **Deck file:** <path to .key or .pptx>
- **Outline file:** <path>
- **Figure count:** <N>
- **Result pattern:** `<regex>`
- **Report language:** <lang>
- **Report output dir:** <path>
- **Sync report dir:** <path>
- **Figure PDF dir:** <path or omit — defaults to <dirname(Deck file)>/pdf/>
- **Figure PNG dir:** <path or omit — defaults to <dirname(Deck file)>/png/>
- **Manuscript dir:** <path>
- **BibTeX file:** <path>
- **Summary file:** <path>
- **CrossRef email:** <email or omit>

## Language preference

- **User-dialog language:** <lang>  (manuscripts always stay in English)
````

## Write policy

- **Block exists, fields all `[TBD]`** → safe to fully replace with new content.
- **Block exists, some fields already filled** → only update fields where phase 2 captured a new value. Leave previously-filled fields alone unless the user explicitly chose to override during phase 2.
- **Block missing** → this shouldn't happen post-`/omcr-setup`, but if it does, insert the full filled-in block.

Show the resulting block(s) to the user before writing, and confirm. After confirmation, write `CLAUDE.md` and report the diff so the user can see exactly what changed.

## Path relocations

If the user's `BibTeX file` or `Summary file` answer differs from the defaults (`paper/references.bib`, `./references.csv`) that `/omcr-setup` created, **move** the existing file to the new path (don't duplicate). Show the move and confirm before executing. If a file at the new path already exists, stop and ask the user.
