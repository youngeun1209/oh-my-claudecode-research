---
name: todofig
description: Compare a captured-figure deck against an outline document and produce a prioritized TODO of gaps (P0/P1/P2). Reads `## Research stack` config from the user's CLAUDE.md (Deck file / Outline file / Figure count / Result pattern / Report language / Report output dir). Accepts an optional figure identifier in `$ARGUMENTS` (e.g. "Fig4") to restrict the analysis to a single figure. Called by the `/todofig` slash command but also standalone-invocable.
---

# Figure ↔ Outline Gap Analysis

Goal: compare what an exported figure deck **currently contains** against what an outline document **prescribes**, and produce a prioritized, actionable TODO so the user knows exactly what to fix.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

This skill is **status + gaps + prioritized actions**. For a status-only snapshot (no TODO), use the `sync` skill (called by `/sync`).

---

## Step 0 — Resolve project configuration

Read the project's `CLAUDE.md` for a `## Research stack` section. Required fields:

| Field | Purpose | Example |
|---|---|---|
| `Deck file` | Path to the `.key` / `.pptx` deck (drives figure refresh via `cropfig`) | `decks/main.key` |
| `Outline file` | Canonical outline (markdown) | `outline.md` |
| `Figure count` | Total figures expected | `8` |
| `Result pattern` | Regex to find result/figure blocks | `^### Result (\d+)` |
| `Report language` | Output language | `English` |
| `Report output dir` | Where to save the TODO report | `./todofig_reports/` |

Optional field:

| Field | Default | Purpose |
|---|---|---|
| `Figure PNG dir` | `<dirname(Deck file)>/png/` | Where the cropped per-slide PNGs live. This skill reads these to inspect figure state. Populated by the `cropfig` skill. |

If any required field is missing, **ask the user once** for the missing values, then **offer to write them** into the project's `CLAUDE.md` as a `## Research stack` section. See [`wiki/Configuration.md`](../../wiki/Configuration.md) for the canonical block format.

Figure refresh is owned by the `cropfig` skill, not this skill. Run `cropfig` separately if the PNG dir is stale or empty.

---

## Step 1 — Load the outline

Read `Outline file` in full. For every block matching `Result pattern`, extract:

- The intended figure number / identifier (capture group from the regex)
- The panel list (sub-bullets, A/B/C/D/...)
- The **key message** sentence — what the figure must visually communicate
- Methods / conditions / controls / hyperparameters specific to this figure

### Step 1.5 — Pull supervisor's unresolved CRITICAL issues (optional)

If `.claude/agent-memory/supervisor/MEMORY.md` exists, read it for unresolved CRITICAL issues. Each unresolved CRITICAL issue that blocks a figure or a main-text claim auto-injects as a P0 item in Step 5, even if the figure looks superficially complete.

---

## Step 2 — Inspect each cropped figure PNG

List `Figure PNG dir`/figure*.png in filename order. Each `figureNN.png` corresponds 1-to-1 with the figure block numbered `N` in the outline (no slide-to-figure offset — `cropfig` writes figure-numbered filenames directly).

If `Figure PNG dir` is empty, `cropfig` has not been run yet — say so in the report and skip the inspection rather than fabricating panel contents.

For every figure, note:
- Which panels are drawn vs. missing
- Whether axes / legends / typography are submission-ready (legible at print width)
- Whether the figure's **key message** reads off the panels without the caption
- Whether all required conditions / controls / contrasts are present
- Cross-figure consistency: palette, condition naming, axis conventions

### Visual-language checklist (when applicable)

If `.claude/agent-memory/figure-descriptor/color-system.md` exists, load it and check every figure against:
- **Palette conformance** — do condition colors match the locked hex codes? Flag any inline-invented color.
- **Plot-type conformance** — does the outline-prescribed plot type match what's shown?
- **Typography** — axis labels, panel labels, tick labels at the venue's print-size thresholds
- **Visual hierarchy** — is the figure's primary contrast the most prominent element?
- **Overclaim check** — if `supervisor/MEMORY.md` flags any contrast as non-significant, ensure no figure asserts it visually as significant

**Budget note:** reading every PNG is token-heavy. If `Figure count` > 12 and `$ARGUMENTS` is non-empty, inspect only the focused figure + immediate neighbors; defer the rest unless the gap analysis demands them.

---

## Step 3 — Build the diff

For each figure, build the diff: outline-prescribed contents **vs.** cropped PNG contents.

Categories to check:

1. **Missing panels** — outline calls for panel X, slide does not show it.
2. **Placeholder content** — panel is present but shows preliminary data, wrong subject/condition, stale version.
3. **Orphan figures** — a `figureNN.png` exists that the outline does not describe.
4. **Cross-figure consistency** — palette, label conventions, identifier choices match across all figures.
5. **Replication / supplementary completeness** — if the outline calls for replication or supplementary panels, are they present? (Often incomplete; flag explicitly.)
6. **Key-message visibility** — if the outline states a specific quantitative claim ("X reduces Y by 40%"), does the figure actually communicate that number?
7. **Staleness** — if `Outline file` mtime is newer than the deck file mtime (or the latest `Figure PNG dir` PNG mtime), the outline has probably drifted ahead of the figures. Flag which figures look stale.

---

## Step 4 — Produce the TODO

Deliver the result in `Report language` using the structure below. Keep figure / panel / condition identifiers in English regardless of `Report language`.

```
# Figure-Outline Gap Report — YYYY-MM-DD

## Figure-by-figure

### Fig 1 — [title from outline]
- ✅ ...
- ⚠️ ...
- ❌ ...
- **Next action:** ...

### Fig 2 — [title]
- ✅ ...
- ⚠️ ...
- ❌ ...
- **Next action:** ...

... (through Fig <figure_count>)

## Cross-cutting

- **Missing figures/panels:** ...
- **Orphan slides:** ...
- **Stale (outline newer than deck):** ...
- **Consistency issues:** ...

## Prioritized TODO (this iteration)

1. [P0] ...
2. [P0] ...
3. [P1] ...
4. [P2] ...

## Prioritized TODO (later, before submission)

- ...
```

Priority rules:
- **P0** — blocks a main-text claim, or is an unresolved CRITICAL issue carried from `supervisor/MEMORY.md` (Step 1.5).
- **P1** — figure exists but does not clearly convey the outline's key message.
- **P2** — cosmetic / consistency issues (palette, labels, ID matching, color-system violations).
- **Later** — supplementary / replication panels not load-bearing for the core narrative.

**Narrative-half balance check (when applicable):** after ranking, if the outline structures the project into multiple narrative threads (e.g., two halves of a paper title), check whether P0/P1 items cluster in one thread. If so, flag at the top that the other thread is under-resourced.

---

## Step 5 — Persist the report

Save the full report to `${Report output dir}/todofig_YYYY-MM-DD.md`. Create the directory if it doesn't exist (`mkdir -p`). Do **not** overwrite any human-maintained TODO file (e.g., a project-level `TODO.md`).

---

## Argument parsing

Inspect `$ARGUMENTS` (passed through by [`commands/todofig.md`](../../commands/todofig.md)).

If `$ARGUMENTS` matches a figure identifier (e.g., `Fig4`, `R1`, `Figure 5`, `5`), **restrict the analysis to that single figure**. Skip the cross-cutting and multi-figure sections; produce only the focused figure's ✅ / ⚠️ / ❌ block and a focused TODO.

If `$ARGUMENTS` is empty, run the full sweep over all `Figure count` figures.
