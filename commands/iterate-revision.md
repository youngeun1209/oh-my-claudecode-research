---
description: Revise one manuscript section against the reviewer team until DONE/BLOCKED/HALT. Writer ↔ reviewer loop driven by the orchestrate primitives.
---

# /iterate-revision

Dispatcher. Read [`skills/iterate-revision/SKILL.md`](../skills/iterate-revision/SKILL.md) and follow it exactly.

Arguments: `$ARGUMENTS`

## Signature

```
/iterate-revision <section-path> [--max-iter N] [--venue VENUE] [--force] [--allow-tbd]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--max-iter` | `3` | Hard cap on writer ↔ reviewer iterations. Reaching it without DONE/BLOCKED → HALT. Overrideable via `## Research stack` field `iterate_revision.max_iter`. |
| `--venue` | `paper.json.venue` | Target venue for reviewer strictness. Falls back to `paper.json.venue`; if neither is set, phase 01 aborts. |
| `--force` | `false` | Bypass the `status == approved` early-exit. Re-iterate an already-approved section. |
| `--allow-tbd` | `false` | Proceed even when the section file, the per-section outline, or `paper.json.hypothesis` contains `[TBD: ...]` markers (Phase 1 decision Q2). Off by default. |

## Examples

```
/iterate-revision sections/results.tex
/iterate-revision sections/intro.tex --max-iter 5 --venue Nature
/iterate-revision sections/abstract.tex --venue NeurIPS --force
/iterate-revision sections/discussion.tex --allow-tbd
```
