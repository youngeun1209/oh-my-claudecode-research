---
name: sync
description: Reconcile current state (captured figure deck) with final goal (outline document), refresh agent memories with factual drifts, and produce a dated status snapshot. Reads `## Research stack` config from the user's CLAUDE.md (Deck file / Outline file / Figure count / Report language / Sync report dir). Status-only output — never produces a TODO (that is the `todofig` skill's job). Called by the `/sync` slash command but also standalone-invocable.
---

# Sync

Goal: keep the project's **agent memories** and the team's mental model aligned with the **current state** (captured deck) and the **final goal** (outline). Optionally refresh figure embeds in a target document.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

This skill **does not** produce an actionable TODO — that's the `todofig` skill's job (called by `/todofig`). The output is a status snapshot and a list of drifts.

---

## Step 0 — Resolve project configuration

Read the project's `CLAUDE.md` for a `## Research stack` section. Required fields:

| Field | Purpose |
|---|---|
| `Deck file` | Path to the `.key` / `.pptx` deck (current state derives from this) |
| `Outline file` | Canonical outline file (final goal) |
| `Figure count` | Total figures expected |
| `Report language` | Output language |
| `Sync report dir` | Directory to save sync reports |

Optional fields:

| Field | Default | Purpose |
|---|---|---|
| `Figure PNG dir` | `<dirname(Deck file)>/png/` | Cropped per-slide raster PNGs. This skill reads these to assess current figure state. Populated by the `cropfig` skill. |

If a required field is missing, ask the user once and offer to persist to the `## Research stack` section of `CLAUDE.md`. See [`wiki/Configuration.md`](../../wiki/Configuration.md) for the canonical block format.

Figure refresh and outline embedding are owned by the `cropfig` skill (`export_deck.py` + `crop_figures.py` + `upload_figures.py`), not by this skill. Run `cropfig` separately when you need to refresh the deck.

---

## Authority hierarchy

| Question | Ground truth |
|---|---|
| What exists right now? | Cropped PNGs in `Figure PNG dir` (produced by `cropfig`) |
| Where are we heading? | `Outline file` |
| What has been done and decided? | Agent memories under `.claude/agent-memory/<agent>/MEMORY.md` |

When sources disagree:
- Agent memory vs. cropped PNG → trust the PNG (current state); update the memory.
- Agent memory vs. outline → update the memory; flag the drift.
- Outline vs. cropped PNG → note the gap; defer to `/todofig`.
- Agent memory references stale paths or filenames → normalize.

---

## Phase 1 — Read everything

### 1.1 Read the outline

Read `Outline file` in full. For each result/figure block, extract: figure number, panel list, key message, control conditions, method constraints. Use the project's `Result pattern` from the `todofig` skill's config if defined; otherwise default to `^### Result (\d+)`.

### 1.2 Read the current state

Read PNGs in `Figure PNG dir` (filename order: `figure01.png`, `figure02.png`, …). Each `figureNN.png` corresponds 1-to-1 with the figure block numbered `N` in the outline. Determine which panels actually exist, which are placeholders, and which conditions are shown.

**Guard:** if `Figure PNG dir` is missing or empty (`cropfig` hasn't run yet, or the deck hasn't been re-exported since the last memory sync), continue with outline-only analysis and state clearly in the report that figure snapshots are unavailable.

### 1.3 Read agent memories

For each agent under `.claude/agent-memory/`:
- `supervisor/MEMORY.md`
- `analysis-implementer/MEMORY.md`
- `paper-writer/MEMORY.md`
- `figure-descriptor/MEMORY.md`
- `reviewer/MEMORY.md`
- `literature-curator/MEMORY.md`

Also read any linked topic files referenced inside each `MEMORY.md`. Note the last-synced date.

---

## Phase 2 — Reconcile memories

Each agent owns the structure of its own memory files. **This skill must not restructure or delete agent-authored content.** Allowed edits are strictly limited to:

1. Add or refresh the top-of-file sync marker: `**Last synced: YYYY-MM-DD**`.
2. Append a `## Drifts flagged at last sync` section (create if absent) listing factual mismatches found vs. captured deck / outline — one bullet per drift, no prose interpretation.
3. Correct factual fields that are **unambiguously** wrong by current ground truth (e.g., a memory says `outline_v3.md` → rename to `outline.md`; a memory says a hyperparameter that the outline now contradicts → note the drift but only change if the memory explicitly claims the outline states it).
4. If `outline_file` mtime is newer than an agent's `Last synced` marker, that agent's memory is potentially stale across the board — flag it, do **not** rewrite.

**Never do** any of the following:
- Add new interpretive claims, design decisions, or narrative framings.
- Invent new TODO items.
- Remove an agent's topic files or flatten its internal schema.
- Write to agent-owned specification files (e.g., `figure-descriptor/color-system.md`).

Drifts that require human judgment (narrative direction changes, contradictions across documents, decisions affecting multiple agents) are **surfaced only in the report's "Manual review needed" section**, not auto-resolved.

---

## Phase 3 — Status snapshot

For each figure (1 through `figure_count`), classify into exactly one status (no prescriptive next steps — this is status only):

- **✅ Completed** — outline panels match the captured deck, and the key message reads off the figure.
- **🟡 In progress** — data or code exists, but the figure is incomplete, placeholder, or shows a stale version.
- **⬜ Not started** — no data, code, or panel exists yet.
- **🚧 Blocked** — cannot proceed without a decision or prerequisite (specify what).

For non-completed items, name the gap in one sentence. Do **not** author multi-step plans, priorities, or delegations — that's the `todofig` skill's job.

### Phase 3.5 — Narrative-spine check (optional)

If the project's `CLAUDE.md` defines a narrative spine (multiple threads with load-bearing figures), explicitly verify each thread is still load-bearing in the current deck. Surface any weakened thread as a 🔴 item in the "Manual review needed" section with one sentence explaining why.

If `supervisor/MEMORY.md` flags specific contrasts as non-significant (overclaim risk), check that no current figure or memory has started asserting them as significant. Flag any overclaim.

---

## Phase 4 — (figure embedding moved to `cropfig`)

Figure refreshing (deck → per-slide PDF → cropped PDF + low-DPI PNG) and outline embedding (`![Figure N](figures/figureNN.png)` after each result heading) are owned by the `cropfig` skill, not by this skill. To refresh figures alongside a sync:

```bash
DECK_FILE=<path> python3 "$CLAUDE_PLUGIN_ROOT"/skills/cropfig/export_deck.py   "$DECK_FILE" "$STAGE"
DECK_FILE=<path> python3 "$CLAUDE_PLUGIN_ROOT"/skills/cropfig/crop_figures.py  "$STAGE"
DECK_FILE=<path> python3 "$CLAUDE_PLUGIN_ROOT"/skills/cropfig/upload_figures.py
```

Or invoke the `cropfig` skill directly. This skill should not duplicate that work — if the outline appears out of date and `cropfig` has not been run, surface that as a "Manual review needed" item rather than running embed logic here.

---

## Phase 5 — Report

Deliver in `Report language` with this structure. Keep figure / panel / condition identifiers in English regardless of `Report language`.

```
## Sync Report — YYYY-MM-DD

### Current state
- Figure source: ${Figure PNG dir}
- Snapshot status: [N figures / unavailable: <reason — cropfig not run yet, etc.>]
- Per-figure summary: [one-line status across all figures]

### Goal alignment (vs. ${Outline file})
- ✅ Completed: [figure list]
- 🟡 In progress: [figure + one-sentence gap]
- ⬜ Not started: [figure list]
- 🚧 Blocked: [figure + what blocks it]

### Agent memory updates
- supervisor: [one-line summary or "no change"]
- analysis-implementer: [...]
- paper-writer: [...]
- figure-descriptor: [...]
- reviewer: [...]
- literature-curator: [...]

### Narrative-spine check (if applicable)
- [Thread 1]: [carrying / weakened — reason]
- [Thread 2]: [carrying / weakened — reason]
- Headline quantitative claim: [still valid / re-examine]
- Overclaim detection: [if any, location + content]

### ⚠️ Manual review needed
- [Items requiring user decision — narrative direction, document contradictions, outline-vs-deck conflicts, 🔴 narrative weakening, etc.]
```

---

## Phase 6 — Persist

Save the full report to `${Sync report dir}/sync_YYYY-MM-DD.md`. Create the directory if missing (`mkdir -p`). Do **not** overwrite any human-maintained TODO file.

Optionally update `.claude/agent-memory/sync-coordinator/MEMORY.md` (if the project tracks a sync coordinator memory) with:
- Sync date
- One-line summary of what changed since the last sync
- Current snapshot (N completed / in progress / not started / blocked)
- Flagged drifts the user still needs to resolve

---

## Argument parsing

Inspect `$ARGUMENTS` (passed through by [`commands/sync.md`](../../commands/sync.md)):

- `$ARGUMENTS` contains `memory-heavy` → spend extra effort on Phase 2 (deep memory reconciliation).
- `$ARGUMENTS` contains `outline just changed` → re-parse `Outline file` carefully; aggressively update memories that reference old terminology.
- `$ARGUMENTS` contains `status only` → skip Phase 2; produce status snapshot only.
- empty → default full pass (Phase 1 → 6, excluding Phase 4 which now lives in `cropfig`).
