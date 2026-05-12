---
description: Map-reduce engine — take an outline, dispatch @paper-writer in parallel, one per section, produce first drafts. Refinement is the user's call via /iterate-revision.
---

# /outline-expand

Dispatcher. Read [`skills/outline-expand/SKILL.md`](../skills/outline-expand/SKILL.md) and follow it exactly.

Arguments: `$ARGUMENTS`

## Signature

```
/outline-expand <outline-path> [--sections <list>] [--max-iter-per-section N]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--sections` | all sections discovered in the outline that match a `paper.json.sections[*]` key and are not already `approved` | Comma-separated subset of section names to draft this run. When set, **only** these are drafted; existing-status guards still apply unless an explicit name is listed (an explicit name in `--sections` skips the "already drafted" early-skip). |
| `--max-iter-per-section` | `1` | Unused for v0.2. Accepted on the CLI for forward compatibility with the v0.3 `--auto-iterate` flag (Phase 2 §5, Phase 5 deferred). This engine produces first drafts only — it does **not** invoke `/iterate-revision` internally. |

## Examples

```
/outline-expand outline.md
/outline-expand manuscript/outline.md --sections introduction,methods
/outline-expand outline.tex --sections results
```

## What this engine does NOT do

- Does **not** call `/iterate-revision`. Engines are leaves (Phase 2 decision §5). After this engine returns DONE, run `/iterate-revision <section-path>` on each newly-written section to refine.
- Does **not** retry failed paper-writer dispatches. A partial-failure run reports `N drafted, M failed`; the user re-runs with `--sections` listing the failed names.
- Does **not** mutate already-`approved` sections unless they are named explicitly in `--sections`.
- Does **not** edit `main.tex`, `references.bib`, or any non-section file. Writes only the section files declared in `paper.json.sections[*].path`.

## See also

- [`skills/outline-expand/SKILL.md`](../skills/outline-expand/SKILL.md) — the engine body.
- [`develop/phase-2-additional-engines.md`](../develop/phase-2-additional-engines.md) — engine 5 design doc.
- [`develop/phase-2-decisions.md`](../develop/phase-2-decisions.md) §4 — shared `nomenclature.md` payload + post-merge drift lint decision.
