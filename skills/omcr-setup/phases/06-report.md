# Phase 6 — Report

Print a concise summary the user can read in 10 seconds. Fill the template with outcomes recorded during phases 1–5.

````
## OMCR /omcr-setup complete — YYYY-MM-DD

### CLAUDE.md infrastructure
- Project context block:    <added with [TBD] placeholders / already present — left alone>
- Research stack block:     <added / already present>
- Language preference block: <added / already present>

### Agent memory (`.claude/agent-memory/<agent>/MEMORY.md`)
- supervisor:           <created from canonical / already exists — skipped>
- analysis-implementer: <...>
- paper-writer:         <...>
- figure-descriptor:    <...>
- reviewer:             <...>
- literature-curator:   <...>

### Bibliography
- paper/references.bib:    <created with header / already exists>
- references.csv (root):   <created with header row / already exists>

### Permissions (`.claude/settings.json`)
- Strategy:           <narrow / merge / skip>
- Categories enabled: <list of ① ② ③ ④ ⑤ ⑥ ⑦ that user selected>
- Patterns count:     N
- Backup:             <.claude/settings.json.backup.YYYY-MM-DD / no prior file>

### Next step
Run `/start-research` next — it walks you through filling the `[TBD]` placeholders in `CLAUDE.md` (working title, field, hypothesis, target venue, datasets, narrative spine), optionally applies a domain preset (e.g. `neuro-fmri`), and scaffolds the LaTeX manuscript directory.
````

End by recommending `/start-research`.
