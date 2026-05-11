# Commands — reference

OMCR ships 2 slash commands and 1 invocable skill, all parameterized via the [Research stack block](Configuration.md) in your project's `CLAUDE.md`.

## `/todofig`

**Goal:** Compare a captured figure deck against an outline document; produce a prioritized TODO of gaps (P0/P1/P2).

**Inputs (from `## Research stack` block):**
- `deck_export_dir` — captured PNG source
- `outline_file` — canonical outline (markdown)
- `figure_count` — total figures expected
- `result_pattern` — regex to find figure blocks in outline
- `report_lang` — output language
- `report_output_dir` — where to save the TODO report
- `deck_export_script` (optional) — idempotent refresh script

**Argument:** `$ARGUMENTS` — optional figure identifier to focus on (e.g., `Fig4`, `R1`, `Figure 5`). Empty = full sweep.

**Output:**
1. Per-figure ✅ / ⚠️ / ❌ block + "next action"
2. Cross-cutting concerns (missing panels / orphan slides / stale figures / consistency issues)
3. Prioritized TODO (P0 / P1 / P2 / Later)

**Saved to:** `${report_output_dir}/todofig_YYYY-MM-DD.md`

**Priorities:**
- **P0** — blocks a main-text claim, or is an unresolved CRITICAL issue from supervisor memory
- **P1** — figure exists but does not convey the outline's key message
- **P2** — cosmetic / consistency issues
- **Later** — supplementary / replication panels

[Source: `commands/todofig.md`](../commands/todofig.md)

### Example session

```
/todofig
```

Output:
```
# Figure-Outline Gap Report — 2026-05-10

## Figure-by-figure

### Fig 1 — Conceptual schematic
- ✅ Pipeline overview present
- ⚠️ Color palette differs from rest of deck
- ❌ Step 3 ("traversal") panel missing
- **Next action:** Add Step 3 schematic; harmonize palette per color-system.md

### Fig 2 — R1 (rest scaffold)
...

## Prioritized TODO

1. [P0] Add Fig 1 Step 3 schematic — blocks the "Approach" narrative
2. [P0] R3 panel D — outline shows 4 conditions, slide has 3
3. [P1] Fig 5 caption mentions "87% of ceiling" but figure doesn't display the number
4. [P2] Harmonize Fig 1 palette
...
```

For a focused single-figure pass:

```
/todofig Fig5
```

Skips the cross-cutting section, produces only Fig 5's diff + focused TODO.

## `/sync`

**Goal:** Reconcile current state (captured deck) with final goal (outline), refresh agent memories with drifts, optionally embed cropped figures into a target document. Produces a status snapshot — **not a TODO**.

**Inputs (from `## Research stack` block):**
- All `/todofig` fields, plus:
- `sync_report_dir` — where to save status reports
- `tight_crop_dir` (optional) — for Phase 4 figure embedding
- `embed_target` (optional) — document (`.docx` / `.md`) to embed cropped figures into

**Argument:** `$ARGUMENTS` — optional scope hint:
- `memory-heavy` — deep memory reconciliation
- `outline just changed` — aggressive memory updates
- `figures only` — skip Phase 2 (memory)
- `no-embed` — skip Phase 4 (embed)
- `embed only` — run Phase 1.1 + Phase 4 only
- (empty) — default full pass

**Output (6 phases):**
1. Phase 1 — Read everything (export, outline, deck, memories)
2. Phase 2 — Reconcile memories (limited surgical edits only)
3. Phase 3 — Status snapshot (✅ / 🟡 / ⬜ / 🚧 per figure)
4. Phase 4 — Embed cropped figures into `embed_target` (optional)
5. Phase 5 — Report
6. Phase 6 — Persist report + update sync coordinator memory

**Saved to:** `${sync_report_dir}/sync_YYYY-MM-DD.md`

**Critical:** Phase 2 is **strictly limited** — no auto-rewriting of agent-authored interpretive content. Sync can only add/refresh sync markers and append drift entries.

[Source: `commands/sync.md`](../commands/sync.md)

### Authority hierarchy (sync's mental model)

| Question | Ground truth |
|---|---|
| What exists right now? | Captured PNGs in `deck_export_dir` |
| Where are we heading? | `outline_file` |
| What has been done / decided? | `.claude/agent-memory/<agent>/MEMORY.md` |

When sources disagree:
- Memory vs. PNG → trust PNG, update memory
- Memory vs. outline → update memory, flag drift
- Outline vs. PNG → flag gap (defer to `/todofig`)
- Memory references stale paths → normalize

### Example session

```
/sync
```

Output:
```
## Sync Report — 2026-05-10

### Current state
- Deck source: figures/captured/
- Latest export: 8 PNGs (refreshed)
- Per-figure summary: Fig 1 ✅, Fig 2 ✅, Fig 3 🟡, Fig 4 🚧, ...

### Goal alignment (vs. outline.md)
- ✅ Completed: Fig 1, Fig 2, Fig 6
- 🟡 In progress: Fig 3 (panel C placeholder), Fig 5 (stale)
- ⬜ Not started: Fig 8
- 🚧 Blocked: Fig 4 (waiting on R4 permutation test result)

### Embed updates (since embed_target = outline.docx)
- Refreshed: R1, R2, R3, R6
- Skipped: R4 (no PNG yet), R7 (no PNG yet)

### Agent memory updates
- supervisor: Last synced refreshed; 1 drift flagged
- analysis-implementer: no change
- paper-writer: no change
- figure-descriptor: 1 drift flagged (Fig 5 condition labels)
- reviewer: no change

### ⚠️ Manual review needed
- Fig 5 figure-descriptor memory says "Raw / Own / Other" but slide shows "Baseline / Treatment / Sham" — please reconcile.
```

## `cropfig` (skill, not a slash command)

**Goal:** Tight-crop captioned figure PNGs to figure-only content. Strips the top "Figure N. Title" label, removes trailing whitespace, adds uniform 10 px white padding.

**Invocation:** Not directly via `/`; agents and other commands invoke via the `Skill` tool with `skill="cropfig"`. Most commonly invoked by `/sync` Phase 4 to produce header-stripped PNGs for `.docx` embedding.

**Inputs:** `FIGURES_SRC`, `FIGURES_DST`, `EXPORT_SCRIPT` (env vars) or the corresponding Research-stack fields.

**Output contract:**

| Path | Owner | Top label | Bottom caption |
|---|---|---|---|
| `$FIGURES_SRC` | your export pipeline | KEPT | should be pre-stripped |
| `$FIGURES_DST` | this skill | **removed** | (pre-stripped) |

**Implementation:** Python (PIL + numpy) — see `skills/cropfig/crop_top_label.py` for the band-classification heuristic (color saturation + long-dark-run detection).

[Source: `skills/cropfig/SKILL.md`](../skills/cropfig/SKILL.md) and [`crop_top_label.py`](../skills/cropfig/crop_top_label.py)

### Direct CLI use

If you want to invoke `cropfig` outside of `/sync`:

```bash
# Defaults
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py

# Explicit paths
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py \
  path/to/captured/ \
  path/to/tight/

# Env vars
FIGURES_SRC=path/to/captured FIGURES_DST=path/to/tight \
  python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py
```

Or as a Python import:

```python
from skills.cropfig.crop_top_label import main
main(src="path/to/captured", dst="path/to/tight")
```

## See also

- [Configuration](Configuration.md) — `## Research stack` block schema
- [Agents](Agents.md) — agents that may invoke these commands
- [Hooks](Hooks.md) — `pii-scrub` runs before any write the commands produce
