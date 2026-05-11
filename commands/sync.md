---
description: Reconcile current state (captured figure deck) with final goal (outline document), refresh agent memories with drifts, optionally embed cropped figures into a target document. Produces a status snapshot — not a TODO (use /todofig for that).
argument-hint: [optional scope hint, e.g. "memory-heavy", "outline just changed", "no-embed", "embed only"]
---

# Project Sync

Goal: keep the project's **agent memories** and the team's mental model aligned with the **current state** (captured deck) and the **final goal** (outline). Optionally refresh figure embeds in a target document.

This command **does not** produce an actionable TODO — that's `/todofig`'s job. The output is a status snapshot and a list of drifts.

---

## Step 0 — Resolve project configuration

Read the project's `CLAUDE.md` for a `## Research stack` section. Required fields:

| Field | Purpose |
|---|---|
| `deck_export_dir` | Directory of captured figure PNGs (current state) |
| `outline_file` | Canonical outline file (final goal) |
| `figure_count` | Total figures expected |
| `report_lang` | Output language |
| `sync_report_dir` | Directory to save sync reports |

Optional fields (enable specific phases):

| Field | Enables | Default |
|---|---|---|
| `deck_export_script` | Phase 1.1 (idempotent re-export) | not set → skip |
| `tight_crop_dir` | Phase 4 (figure-only embeds) | `figures/tight/` |
| `embed_target` | Phase 4 (embed cropped figures into a docx / md) | not set → skip Phase 4 |
| `slide_to_figure_offset` | Slide-index → figure-number mapping | `0` (slide 1 = figure 1) |

If a required field is missing, ask the user once and offer to persist to the `## Research stack` section of `CLAUDE.md`. See `/todofig`'s Step 0 for the canonical block format.

---

## Authority hierarchy

| Question | Ground truth |
|---|---|
| What exists right now? | Captured PNGs in `deck_export_dir` (via `deck_export_script` if set) |
| Where are we heading? | `outline_file` |
| What has been done and decided? | Agent memories under `.claude/agent-memory/<agent>/MEMORY.md` |

When sources disagree:
- Agent memory vs. captured PNG → trust the PNG (current state); update the memory.
- Agent memory vs. outline → update the memory; flag the drift.
- Outline vs. captured PNG → note the gap; defer to `/todofig`.
- Agent memory references stale paths or filenames → normalize.

---

## Phase 1 — Read everything

### 1.1 Export the latest deck (if `deck_export_script` set)

```bash
${deck_export_script}
```

Idempotent. Note how many slides were exported (or "skipped — up to date").

**Guard:** if the script is missing or returns non-zero (headless environment, permission denied, missing tool), continue with outline-only analysis. State clearly in the report that figure snapshots are unavailable. Do not fail the whole sync.

### 1.2 Read the outline

Read `outline_file` in full. For each result/figure block, extract: figure number, panel list, key message, control conditions, method constraints. Use the project's `result_pattern` from `/todofig`'s config if defined; otherwise default to `^### Result (\d+)` or `^### Fig(?:ure)? (\d+)`.

### 1.3 Read the current state

Read PNGs in `deck_export_dir` (filename order). Determine which panels actually exist, which are placeholders, and which conditions are shown.

### 1.4 Read agent memories

For each agent under `.claude/agent-memory/`:
- `supervisor/MEMORY.md`
- `analysis-implementer/MEMORY.md`
- `paper-writer/MEMORY.md`
- `figure-descriptor/MEMORY.md`
- `reviewer/MEMORY.md`

Also read any linked topic files referenced inside each `MEMORY.md`. Note the last-synced date.

---

## Phase 2 — Reconcile memories

Each agent owns the structure of its own memory files. **`/sync` must not restructure or delete agent-authored content.** Allowed edits are strictly limited to:

1. Add or refresh the top-of-file sync marker: `**Last synced: YYYY-MM-DD**`.
2. Append a `## Drifts flagged at last sync` section (create if absent) listing factual mismatches found vs. captured deck / outline — one bullet per drift, no prose interpretation.
3. Correct factual fields that are **unambiguously** wrong by current ground truth (e.g., a memory says `outline_v3.md` → rename to `outline.md`; a memory says a hyperparameter that the outline now contradicts → note the drift but only change if the memory explicitly claims the outline states it).
4. If `outline_file` mtime is newer than an agent's `Last synced` marker, that agent's memory is potentially stale across the board — flag it, do **not** rewrite.

**Never do** any of the following in `/sync`:
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

For non-completed items, name the gap in one sentence. Do **not** author multi-step plans, priorities, or delegations — that's `/todofig`'s job.

### Phase 3.5 — Narrative-spine check (optional)

If the project's `CLAUDE.md` defines a narrative spine (multiple threads with load-bearing figures), explicitly verify each thread is still load-bearing in the current deck. Surface any weakened thread as a 🔴 item in the "Manual review needed" section with one sentence explaining why.

If `supervisor/MEMORY.md` flags specific contrasts as non-significant (overclaim risk), check that no current figure or memory has started asserting them as significant. Flag any overclaim.

---

## Phase 4 — Embed cropped figures into `embed_target` (if configured)

Goal: at each result/figure heading in `embed_target`, embed the **figure-only** PNG (no top label, no caption) for the corresponding figure, replacing any previously sync-embedded image block. Keeps the user's editable working copy visually in sync with the captured deck. The prose inside `embed_target` is **never** touched.

This phase is **only** active when `embed_target` is configured. Otherwise, skip silently.

### Step 4.0 — Produce figure-only PNGs via the `cropfig` skill

Invoke the `cropfig` skill (`Skill` tool with `skill="cropfig"`). It refreshes the source PNGs (idempotent), strips the top "Figure N. Title" label, tight-bbox crops each slide, and writes to `tight_crop_dir`.

If cropfig fails (export unavailable, headless, PIL missing), skip Phase 4 entirely and flag in the report — do **not** fall back to embedding the captioned source PNGs (that would duplicate caption text inside the document).

### Step 4.1 — Prerequisites check

- `tight_crop_dir` must contain PNGs after Step 4.0. If empty, skip + flag.
- `embed_target` must not be locked by another process. For `.docx`, check `~$<filename>` lock file (`ls "$(dirname embed_target)/~\$(basename embed_target)" 2>/dev/null`). If locked, skip + surface "Close `embed_target` and rerun /sync".
- For `.docx` targets: `python-docx` must be importable (`python3 -c "import docx"`). If missing, skip + flag; do not auto-install.
- For `.md` targets: standard markdown image insertion — no extra dependency.

### Step 4.2 — Result → figure → slide mapping

For each result block in `outline_file`, parse the captured figure identifier. Map figure → slide using:

```
slide_index = figure_number + slide_to_figure_offset
source_png  = ${tight_crop_dir}/<sorted_filename_at_slide_index>
```

If a slide PNG is missing for a figure, skip that one embed and note it in the report.

### Step 4.3 — Embed (idempotent via sentinel)

Author a single-use script (do not commit it; run inline). For `.docx` use `python-docx`; for `.md` use plain text manipulation. Pattern:

1. Load `embed_target`.
2. Iterate sections / paragraphs. For each result/figure heading, record its position and the captured figure number.
3. For each matched heading, in order:
   a. Scan forward (until next heading) and **delete** any block bracketed by `<<sync-embedded-figure:N>>` sentinels. This removes stale embeds.
   b. Insert a new sentinel block: `<<sync-embedded-figure:N>>` paragraph, then the picture from `source_png`, then `<</sync-embedded-figure:N>>` paragraph.
4. Save back to `embed_target`.

Idempotency is enforced by the sentinels: re-running `/sync` always rewrites sync-owned blocks and never touches anything else.

### Failure modes (all → skip + surface in "Manual review needed")

- No PNGs in `deck_export_dir` (Phase 1.1 failed and dir was empty).
- `cropfig` skill failed → skip Phase 4 entirely; do not fall back to captioned PNGs.
- `embed_target` locked by another process.
- Required library missing (e.g., `python-docx` for `.docx`).
- Script exception: report the exception verbatim; do not attempt heuristic retries.

---

## Phase 5 — Report

Deliver in `report_lang` with this structure. Keep figure / panel / condition identifiers in English regardless of `report_lang`.

```
## Sync Report — YYYY-MM-DD

### Current state
- Deck source: ${deck_export_dir}
- Latest export: [N slides / skipped — up to date / unavailable: <reason>]
- Per-figure summary: [one-line status across all figures]

### Goal alignment (vs. ${outline_file})
- ✅ Completed: [figure list]
- 🟡 In progress: [figure + one-sentence gap]
- ⬜ Not started: [figure list]
- 🚧 Blocked: [figure + what blocks it]

### Embed updates (if embed_target configured)
- Refreshed: [figures whose embeds were updated]
- Skipped: [reasons — locked / missing PNG / lib missing]

### Agent memory updates
- supervisor: [one-line summary or "no change"]
- analysis-implementer: [...]
- paper-writer: [...]
- figure-descriptor: [...]
- reviewer: [...]

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

Save the full report to `${sync_report_dir}/sync_YYYY-MM-DD.md`. Create the directory if missing (`mkdir -p`). Do **not** overwrite any human-maintained TODO file.

Optionally update `.claude/agent-memory/sync-coordinator/MEMORY.md` (if the project tracks a sync coordinator memory) with:
- Sync date
- One-line summary of what changed since the last sync
- Current snapshot (N completed / in progress / not started / blocked)
- Flagged drifts the user still needs to resolve

---

## Argument handling

- `/sync memory-heavy` → spend extra effort on Phase 2 (deep memory reconciliation).
- `/sync outline just changed` → re-parse `outline_file` carefully; aggressively update memories that reference old terminology.
- `/sync figures only` → skip Phase 2; still run Phase 4 (embeds) and Phase 5 (status).
- `/sync no-embed` → skip Phase 4 even if `embed_target` is configured.
- `/sync embed only` → run Phase 1.1 + Phase 4 only (refresh embeds, no memory work, no full report).
- (empty) → default full pass (Phase 1 → 6).
