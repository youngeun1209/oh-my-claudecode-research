# Phase 4 — Bibliography

Initialize the two bibliography files at their **default paths**. `$start-research` may later relocate or rename them based on the user's `Manuscript dir` answer, but at install time the defaults are enough for `@literature-curator` and `verify-citation` to operate.

## `paper/references.bib`

If `paper/` does not exist, create it as an empty directory.

If `paper/references.bib` does not exist, create it with this one-line header:

```
% References for this project. Managed by @literature-curator. Do not hand-edit without coordinating with the agent.
```

If it exists, leave untouched. Do not overwrite.

## `./references.csv` (project root)

If `./references.csv` does not exist, create it with the canonical header row only:

```
citekey,authors,year,title,venue,doi,bucket,our_use,paper_says,cited_sections,verified_on,verify_status
```

If it exists, leave untouched. Do not overwrite or migrate.

The CSV stays in the **project root** (not inside `paper/`) so it does not get pushed to Overleaf — it is project metadata, not part of the manuscript.

## Path overrides

`$start-research` may ask the user to relocate `BibTeX file` or `Summary file` during its interview. If that happens, the start-research flow handles the relocation safely (move, not duplicate, with confirmation).
