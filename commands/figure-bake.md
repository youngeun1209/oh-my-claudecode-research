---
description: Drive one figure from design brief to manuscript-ready PDF + outline PNG. Three-agent loop (@figure-descriptor → @analysis-implementer → @reviewer) wrapped around `cropfig` for the final artifact pass.
---

# /figure-bake

Dispatcher. Read [`skills/figure-bake/SKILL.md`](../skills/figure-bake/SKILL.md) and follow it exactly.

Arguments: `$ARGUMENTS`

## Signature

```
/figure-bake <fig-id> [--max-iter N] [--data <path>] [--code-dir <path>]
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--max-iter` | `3` | Hard cap on `descriptor → implementer → reviewer` iterations. Reaching it without DONE/BLOCKED → HALT. Each iter re-runs `@analysis-implementer` (real code execution), so the default is deliberately small. |
| `--data` | (resolved) | Dataset root for `@analysis-implementer` to read inputs from. Three-layer resolution (Phase 2 decision §3): CLI `--data` > env `CLAUDE_RESEARCH_DATA_ROOT` > CLAUDE.md `## Research stack` `data_root` field > hardcoded `./data/`. The first non-empty value wins; phase 01 aborts if the resolved path does not exist on disk. |
| `--code-dir` | `null` | Optional directory the implementer should write its rendering script(s) into (e.g. `code/figures/`). If unset, the implementer may write next to `vector_path` or under `<manuscript_root>/figures/code/`. The flag is a hint only; phase 03 does not enforce a layout. |

## Examples

```
/figure-bake fig1
/figure-bake fig2 --max-iter 5
/figure-bake fig3 --data ~/datasets/2026-cohort/
/figure-bake fig4 --code-dir code/figures/ --data ./preproc/
```

## What this engine produces

- A vector PDF at `figures.json.figures[<fig-id>].vector_path` — manuscript-grade, written by `@analysis-implementer`'s rendered code.
- A cropped PDF + outline PNG pair via `cropfig` (one-pass, auto-invoked at the end of each implement phase) — the same crop decision feeds both artifacts.
- A critique trail in `figures.json.figures[<fig-id>].critiques[]` — one entry per iter, with reviewer-issued severity-tagged issues.
- Updated per-figure status fields: `brief_status`, `impl_status`, `critique_status`, `iter`.
- One `phase: "summary"` line appended to `.claude/omcr-state/_run-log.jsonl`.

## What this engine does NOT do

- Does not insert the figure into a `.tex` file. Embedding is the user's call; phase 06 suggests `/sync` for that.
- Does not call another slash command. Engines are leaves (Phase 2 decision §5). It does call the `cropfig` skill — which is a skill, not an engine — so this is allowed.
- Does not commit to git. Run `/sync` afterward if you want a snapshot commit.
- Does not invent data. If the implementer cannot read the data root, phase 03 fails and the loop emits BLOCKED.

## See also

- [`skills/figure-bake/SKILL.md`](../skills/figure-bake/SKILL.md) — engine workflow + cost model.
- [`skills/cropfig/SKILL.md`](../skills/cropfig/SKILL.md) — the crop pipeline this engine wraps.
- [`develop/phase-2-additional-engines.md`](../develop/phase-2-additional-engines.md) — Engine 4 design doc.
- [`develop/phase-2-decisions.md`](../develop/phase-2-decisions.md) §3 — the `data_root` three-layer resolution.
