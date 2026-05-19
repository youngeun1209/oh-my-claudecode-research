---
description: Classify a reviewer letter into per-comment labels and dispatch each to the right specialist; assemble a rebuttal letter. Structural comments are routed to user attention, never auto-dispatched.
---

# /respond-reviewer

Dispatcher. Read [`skills/respond-reviewer/SKILL.md`](../skills/respond-reviewer/SKILL.md) and follow it exactly.

Arguments: `$ARGUMENTS`

## Signature

```
/respond-reviewer <review-letter-path> [--manuscript <root>] [--draft-only] [--format md|latex]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--manuscript` | `paper.json.manuscript_root` | Manuscript root the writer + analysis-implementer touch when applying changes. Falls back to `paper.json.manuscript_root`; if neither is set, phase 01 aborts. |
| `--draft-only` | `false` | Dispatch per-comment responses but skip all manuscript edits. The rebuttal letter is the only artifact written. Use when you want to read the rebuttal before deciding which fixes to merge. |
| `--format` | `latex` | Output format for the assembled rebuttal letter. `latex` writes `rebuttal-letter.tex`; `md` writes `rebuttal-letter.md`. Input format is auto-detected from the review-letter extension (`.md`/`.txt` → markdown, `.tex` → LaTeX) — this flag only controls **output** (Phase 2 decision §2). |

## Examples

```
/respond-reviewer reviews/r1-comments.md
/respond-reviewer reviews/r1-comments.tex --manuscript paper/
/respond-reviewer reviews/r2-comments.md --draft-only
/respond-reviewer reviews/r1-comments.txt --format md
```

## What this command guarantees

- **Comments labeled `structural` are never auto-dispatched.** They land in a user-attention list at the end of the run for explicit human decision (Phase 2 design constraint — ethical gate).
- **Engines are leaves.** If a comment requires a figure redraw, `/respond-reviewer` does NOT call `/figure-bake`. Instead, it routes the comment to `@analysis-implementer` with the figure ID in the brief and appends `suggested_next_steps: ["/figure-bake <fig-id>"]` to the rebuttal entry. The user runs the engine themselves (Phase 2 decision §5).
- **LaTeX out by default.** The manuscript scaffold is LaTeX; the rebuttal belongs in the same toolchain. `--format md` is the escape hatch for journals with markdown-only rebuttal forms (Phase 2 decision §2).
