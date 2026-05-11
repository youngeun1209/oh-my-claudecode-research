---
description: Compare a captured-figure deck against an outline document; produce a prioritized TODO of gaps (P0/P1/P2).
argument-hint: [optional figure identifier to focus on, e.g. "Fig4" or "R1"]
---

# Figure ↔ Outline Gap Analysis

Goal: compare what an exported figure deck **currently contains** against what an outline document **prescribes**, and produce a prioritized, actionable TODO so the user knows exactly what to fix.

This command is **status + gaps + prioritized actions**. For a status-only snapshot (no TODO), use `/sync`.

---

## Step 0 — Resolve project configuration

Read the project's `CLAUDE.md` for a `## Research stack` section. Required fields:

| Field | Purpose | Example |
|---|---|---|
| `deck_export_dir` | Directory of captured figure PNGs | `figures/captured/` |
| `outline_file` | Canonical outline (markdown) | `outline.md` |
| `figure_count` | Total figures expected | `8` |
| `result_pattern` | Regex to find result/figure blocks | `^### Result (\d+)` |
| `report_lang` | Output language | `English` |
| `report_output_dir` | Where to save the TODO report | `./todofig_reports/` |
| `deck_export_script` | (optional) Idempotent script to refresh the deck | `bash export.sh` |

If any **required** field is missing (the optional `deck_export_script` is allowed to be absent), **ask the user once** for the missing values, then **offer to write them** into the project's `CLAUDE.md` as a `## Research stack` section. Format:

```markdown
## Research stack (used by /todofig, /sync, /cropfig)

- **Deck export dir:** figures/captured/
- **Outline file:** outline.md
- **Figure count:** 8
- **Result pattern:** `^### Result (\d+)`
- **Report language:** English
- **Report output dir:** ./todofig_reports/
- **Deck export script:** bash export.sh  (optional)
- **Tight-crop output dir:** figures/tight/  (only if you use /sync embedding)
- **Embed target:** outline.docx  (only if you use /sync embedding)
- **Slide → figure offset:** 0  (offset to subtract from slide index → figure number; default 0)
```

Once persisted, subsequent invocations use the stored values without prompting.

---

## Step 1 — Export the latest deck (if configured)

If `deck_export_script` is set:

```bash
${deck_export_script}
```

It should be idempotent (skip if no source change). Note how many slides were exported (or "skipped — up to date").

**Guard:** if the script is missing, fails, or returns non-zero (e.g., headless environment, missing dependency), continue with outline-only analysis. State clearly in the final report that figure snapshots were unavailable, and skip Step 3 PNG inspection. Do not fabricate panel contents.

If no `deck_export_script` configured, assume the user has already populated `deck_export_dir` with current PNGs.

---

## Step 2 — Load the outline

Read `outline_file` in full. For every block matching `result_pattern`, extract:

- The intended figure number / identifier (capture group from the regex)
- The panel list (sub-bullets, A/B/C/D/...)
- The **key message** sentence — what the figure must visually communicate
- Methods / conditions / controls / hyperparameters specific to this figure

### Step 2.5 — Pull supervisor's unresolved CRITICAL issues (optional)

If `.claude/agent-memory/supervisor/MEMORY.md` exists, read it for unresolved CRITICAL issues. Each unresolved CRITICAL issue that blocks a figure or a main-text claim auto-injects as a P0 item in Step 5, even if the figure looks superficially complete.

---

## Step 3 — Inspect each captured PNG

List `deck_export_dir/*.png` in filename order. Each PNG ≈ one slide. **Slide index ≠ figure number** in general — the deck may contain dividers, title slides, or supplementary slides.

Determine the **slide → figure offset** on the first run (`slide N = figure (N - offset)`) and record it in the project's `CLAUDE.md` `## Research stack` block so later runs don't re-discover it. Default offset is `0` (slide 1 = figure 1).

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

**Budget note:** reading every PNG is token-heavy. If the deck has more than 12 slides and `$ARGUMENTS` is non-empty, inspect only the slides for the focused figure + immediate neighbors; defer the rest unless the gap analysis demands them.

---

## Step 4 — Build the diff

For each figure, build the diff: outline-prescribed contents **vs.** captured PNG contents.

Categories to check:

1. **Missing panels** — outline calls for panel X, slide does not show it.
2. **Placeholder content** — panel is present but shows preliminary data, wrong subject/condition, stale version.
3. **Orphan slides** — a slide exists that the outline does not describe.
4. **Cross-figure consistency** — palette, label conventions, identifier choices match across all figures.
5. **Replication / supplementary completeness** — if the outline calls for replication or supplementary panels, are they present? (Often incomplete; flag explicitly.)
6. **Key-message visibility** — if the outline states a specific quantitative claim ("X reduces Y by 40%"), does the figure actually communicate that number?
7. **Staleness** — if `outline_file` mtime is newer than the deck source mtime (or the latest PNG mtime), the outline has probably drifted ahead of the figures. Flag which figures look stale.

---

## Step 5 — Produce the TODO

Deliver the result in `report_lang` using the structure below. Keep figure / panel / condition identifiers in English regardless of `report_lang`.

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
- **P0** — blocks a main-text claim, or is an unresolved CRITICAL issue carried from `supervisor/MEMORY.md` (Step 2.5).
- **P1** — figure exists but does not clearly convey the outline's key message.
- **P2** — cosmetic / consistency issues (palette, labels, ID matching, color-system violations).
- **Later** — supplementary / replication panels not load-bearing for the core narrative.

**Narrative-half balance check (when applicable):** after ranking, if the outline structures the project into multiple narrative threads (e.g., two halves of a paper title), check whether P0/P1 items cluster in one thread. If so, flag at the top that the other thread is under-resourced.

---

## Step 6 — Persist the report

Save the full report to `${report_output_dir}/todofig_YYYY-MM-DD.md`. Create the directory if it doesn't exist (`mkdir -p`). Do **not** overwrite any human-maintained TODO file (e.g., a project-level `TODO.md`).

---

## Argument handling

If `$ARGUMENTS` matches a figure identifier (e.g., `Fig4`, `R1`, `Figure 5`, `5`), **restrict the analysis to that single figure**. Skip the cross-cutting and multi-figure sections; produce only the focused figure's ✅ / ⚠️ / ❌ block and a focused TODO.

If `$ARGUMENTS` is empty, run the full sweep over all `figure_count` figures.
