# Manuscript skeleton

This directory is the canonical LaTeX manuscript scaffold that `/omcr-setup` copies into a project's `Manuscript dir` (default `paper/`).

## What's here

```
main.tex                       # Document root — \input{}'s the section files
sections/
  abstract.tex                 # 5 stubs, one per section
  introduction.tex
  methods.tex
  results.tex
  discussion.tex
figures/                       # Place .pdf / .png figures here
  .gitkeep
references.bib                 # Empty — managed by @literature-curator
.gitignore                     # Strips LaTeX build artifacts
```

## Conventions (enforced via `@paper-writer`)

- **One section per file.** Edit `sections/<name>.tex`; `main.tex` rarely needs touching.
- **Citations** via `\citep{citekey}` against `references.bib`. Citekeys must already exist in the bib — request new ones from `@literature-curator` by leaving `[CITE: <one-line claim>]` placeholders.
- **Figures** live in `figures/`. Include via `\includegraphics{<filename>}` (the `\graphicspath{{figures/}}` directive in `main.tex` resolves the path).
- **`references.bib` is read-only for `@paper-writer`** — only `@literature-curator` writes to it (each entry verified by the `verify-citation` skill).

## Bibliography summary table

The companion to `references.bib` is `references.csv` (or whatever `Summary file` is set to in `## Research stack`). That CSV lives at the **project root**, NOT inside this directory — so it is not pushed to Overleaf when this directory is a clone of an Overleaf project. The CSV is project metadata (`our_use`, `bucket`, `verified_on`); it is not part of the manuscript.

## Local preview

```bash
cd paper/
latexmk -pdf main.tex
```

The `.gitignore` already excludes LaTeX build artifacts (`*.aux`, `*.log`, `*.bbl`, etc.).

## Overleaf workflow

If `/omcr-setup` configured an Overleaf Git Bridge URL, this directory is a clone of your Overleaf project. `/omcr-setup` commits the scaffold on the default branch (`main` or `master` — whatever Overleaf set) but **does not push automatically**. You'll be asked explicitly whether to push when `/omcr-setup` runs.

If you said "no" at the prompt (or want to push later edits):

```bash
git -C paper/ push origin main          # or `master` for older Overleaf projects
```

The Overleaf web view updates within seconds.

To undo a local commit before you've pushed:

```bash
git -C paper/ reset --hard HEAD~1
```
