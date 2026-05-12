# Phase 6 — Report

Produce a concise summary the user can read in 10 seconds. Use the template below; fill in per-phase outcomes recorded during phases 1–5.

````
## OMCR /start-research complete — YYYY-MM-DD

### CLAUDE.md
- Project context:    <N fields filled, M still [TBD]>
- Research stack:     <updated / unchanged>
- Language preference: <updated / unchanged>

### Preset overlay
- Selected:           <preset name or "none">
- supervisor MEMORY.md:           <replaced-from-canonical / skipped-modified / no-preset-template / skipped-no-preset>
- analysis-implementer MEMORY.md: <...>
- paper-writer MEMORY.md:         <...>
- figure-descriptor MEMORY.md:    <...>
- reviewer MEMORY.md:             <...>
- literature-curator MEMORY.md:   <...>
- Body overlay note (neuro-fmri only): <reminder line if applicable>

### Manuscript scaffold
- Manuscript dir:  <path> (<created / existed empty / existed with content — skipped>)
- Skeleton:        <main.tex + 5 sections + figures/ + references.bib + .gitignore — copied / skipped>
- Journal template: <applied <class> + bibstyle <style> / not applied / no venue>
- Overleaf:        <connected to https://git.overleaf.com/****/ / no — local only>
- Branch:          `<default_branch>` (commit `<short SHA>` — `<pushed to Overleaf / local only — push deferred>`)
- Deferred push command (if applicable): `git -C <manuscript_dir> push origin <default_branch>`

### TBD items needing follow-up
- [list every field still marked [TBD], with the one-line note]

### Next steps
1. `@supervisor` to confirm hypothesis / venue / narrative spine framing
2. `@literature-curator` to start filling the BibTeX from your first 5–10 anchor papers
3. `@paper-writer` to draft each section under `<manuscript_dir>/sections/`
4. Preview locally: `cd <manuscript_dir> && latexmk -pdf main.tex`
5. (If push was deferred) When satisfied with the scaffold:
     `git -C <manuscript_dir> push origin <default_branch>`
6. Run `/todofig` once you have a captured figure deck to compare against the outline
````

After printing the report, end by recommending the user run `@supervisor where are we?` for the first real conversation.

## If `/omcr-setup` was declined in phase 1

If phase 1 ended with the user declining to run `/omcr-setup`, skip the full report template above and just print:

````
## OMCR /start-research — cancelled

`/omcr-setup` has not run yet. Run it manually first:

  /omcr-setup

Then re-run `/start-research`.
````
