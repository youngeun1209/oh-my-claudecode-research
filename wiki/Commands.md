# Commands — reference

OMCR ships **10 slash commands** (all thin dispatchers) and **14 invocable skills**, all parameterized via the [Project context + Research stack blocks](Configuration.md) in your project's `CLAUDE.md`. The 4 setup/workflow commands (`/omcr-setup`, `/start-research`, `/todofig`, `/sync`) are documented in detail below, followed by the 2 standalone skills (`cropfig`, `verify-citation`). The 6 orchestration engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`) are summarized at the bottom with links to deeper walkthroughs.

## `/omcr-setup`

**Goal:** Install OMCR's infrastructure in a project. **No questions about your research** — that lives in `/start-research`. Safe to re-run.

**Argument:** none.

**Phases (6):**

1. **State check** — inventory existing `CLAUDE.md` marker blocks, `.claude/agent-memory/`, bibliography files, `.claude/settings.json` (looking for broad wildcards or invalid entries).
2. **CLAUDE.md scaffold** — insert empty `## Project context` / `## Research stack` / `## Language preference` blocks with `[TBD]` placeholders. Existing blocks are left untouched.
3. **Agent memory** — `.claude/agent-memory/<agent>/MEMORY.md` from `templates/MEMORY.template.md` for any of the 6 agents missing it. Existing `MEMORY.md` is never overwritten.
4. **Bibliography** — create empty `paper/references.bib` (with header comment) and `./references.csv` (with canonical header row) if missing.
5. **Permissions** — interactive curated allowlist menu for `.claude/settings.json`. Categories (default ON unless noted): read-only git inspection, file search & exploration, edit code/text files, LaTeX build, citation API lookups (CrossRef / OpenAlex / doi.org), Python analysis scripts (⬜ opt-in), figure crop tool. Dangerous categories (git write, file deletion, wildcard `Bash`, unrestricted `curl`) are **never offered** — they always prompt. If a previous `.claude/settings.json` has broad wildcards or invalid entries, offers to narrow with backup to `.claude/settings.json.backup.YYYY-MM-DD`.
6. **Report** — concise summary; recommends `/start-research` next.

[Source: `commands/omcr-setup.md`](../commands/omcr-setup.md), [`skills/omcr-setup/`](../skills/omcr-setup/)

### Re-running `/omcr-setup`

Safe. State-check + skip semantics mean existing user content (filled `CLAUDE.md` fields, written `MEMORY.md`, your `references.bib` / `references.csv`) is never overwritten. The permissions phase asks before replacing broad wildcards. Use re-runs to refresh infrastructure after a plugin update.

## `/start-research`

**Goal:** Interview-driven first-research-project initialization. Fill the `CLAUDE.md` placeholders that `/omcr-setup` scaffolded — working title, hypothesis, target venue, datasets, narrative spine — optionally apply a domain preset to agent memory, scaffold the LaTeX manuscript directory. Safe to re-run.

**Argument:** `$ARGUMENTS` — optional preset hint:
- `minimal` / `no-overlay` — skip the preset-overlay prompt entirely
- `neuro-fmri` — pre-select the neuro-fMRI preset (still confirms before applying)
- (empty) — ask interactively

**Phases (6):**

1. **Precheck** — verifies `/omcr-setup` has run (`CLAUDE.md` marker blocks, `.claude/agent-memory/<agent>/`, bibliography files all present). If not, offers to invoke `/omcr-setup` automatically before continuing. User can decline and cancel.
2. **Interview** — asks only for fields that are missing or still `[TBD]`. Three policy bands:
   - *Scientific identity* (hypothesis / venue / topic / datasets / narrative spine) — push back **once** with the reason it matters; if user still skips, store as `[TBD: <one-line note>]`. **Never invent.**
   - *Infrastructure* (deck/outline paths, figure count, BibTeX/Summary paths, CrossRef email, Overleaf URL, language) — propose a sensible default; accept silently if user types `[skip]`.
   - *Preset overlay* — apply `neuro-fmri` (or another shipped preset) or stay field-neutral. Skip allowed.
3. **Fill CLAUDE.md** — write captured answers into the three marker blocks. Existing filled fields are preserved unless the user explicitly overrode them. If `BibTeX file` / `Summary file` paths differ from defaults, files are **moved** (not duplicated) with confirmation.
4. **Preset overlay (agent memory)** — if a preset was chosen, replace per-agent `MEMORY.md` files **only when byte-identical to the canonical template** (i.e. untouched). Modified memory is never overwritten.
5. **Manuscript scaffold** (delegated) — invokes the `manuscript-scaffold` skill with `Manuscript dir`, `Target venue`, `Overleaf git URL`, and `Working title`. The skill runs its own 4 phases: state check → journal template lookup (against `templates/journal-registry.json`) → skeleton copy (with optional Overleaf clone + credential caching) → commit and ask before push.
6. **Report** — summary block, TBD follow-up list, next steps. Ends by recommending `@supervisor where are we?`.

[Source: `commands/start-research.md`](../commands/start-research.md), [`skills/start-research/`](../skills/start-research/), [`skills/manuscript-scaffold/`](../skills/manuscript-scaffold/)

### Journal template lookup (phase 5 details)

The `manuscript-scaffold` skill matches `Target venue` against [`templates/journal-registry.json`](../templates/journal-registry.json) — a curated registry of ~27 high-impact venues mapped to their **CTAN-distributed LaTeX classes** (revtex / aastex / elsarticle / IEEEtran / acmart / sn-jnl / mnras / amscls). On exact case-insensitive match (or alias match), the skill shows the registry entry and asks confirmation before rewriting `main.tex`'s `\documentclass{...}` line.

Safety:
- **Pointers only** — CTAN package names + `documentclass` strings + publisher guideline URLs. No `.cls` files bundled.
- **No fuzzy matching** — "PRX" matches "Physical Review X" only via registered alias.
- Each entry carries a `verified_on` timestamp; the skill always reminds the user to check publisher guidelines before submission.

For venues not in the registry, three options: keep generic `article`, specify a class name yourself, or paste a publisher URL for hash-display fetch before applying.

### Overleaf integration (phase 5 details)

If `Overleaf git URL` is set, the `manuscript-scaffold` skill clones the Overleaf project into `Manuscript dir` (requires paid Overleaf plan with Git Integration). Token cached **only** in git's credential helper or `~/.netrc`, scoped to `git.overleaf.com` — never written to any tracked file. Non-empty Overleaf projects stop and ask before clobbering. After scaffold, commits on the default branch **locally** and asks before pushing (default "no").

### Re-running `/start-research`

Safe. Existing values are surfaced as defaults; modified `MEMORY.md` is never overwritten; the `manuscript-scaffold` skill has its own existing-content guard. To reset an agent's memory, delete the specific `.claude/agent-memory/<agent>/MEMORY.md` and re-run.

## `/todofig`

**Goal:** Compare a captured figure deck against an outline document; produce a prioritized TODO of gaps (P0/P1/P2).

**Inputs (from `## Research stack` block):**
- `Deck file` — path to the `.key` / `.pptx` deck
- `Figure PNG dir` (optional, default `<dirname(Deck file)>/png/`) — cropped per-slide PNGs produced by `cropfig`
- `Outline file` — canonical outline (markdown)
- `Figure count` — total figures expected
- `Result pattern` — regex to find figure blocks in outline
- `Report language` — output language
- `Report output dir` — where to save the TODO report

**Argument:** `$ARGUMENTS` — optional figure identifier to focus on (e.g., `Fig4`, `R1`, `Figure 5`). Empty = full sweep.

**Output:**
1. Per-figure ✅ / ⚠️ / ❌ block + "next action"
2. Cross-cutting concerns (missing panels / orphan figures / stale figures / consistency issues)
3. Prioritized TODO (P0 / P1 / P2 / Later)

**Saved to:** `${Report output dir}/todofig_YYYY-MM-DD.md`

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
- ❌ Step 3 ("group comparison") panel missing
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

**Goal:** Reconcile current state (cropped figures + agent memories) with final goal (outline), refresh agent memories with drifts. Produces a status snapshot — **not a TODO**.

**Inputs (from `## Research stack` block):**
- All `/todofig` fields, plus:
- `Sync report dir` — where to save status reports

**Argument:** `$ARGUMENTS` — optional scope hint:
- `memory-heavy` — deep memory reconciliation
- `outline just changed` — aggressive memory updates
- `status only` — skip Phase 2 (memory)
- (empty) — default full pass

**Output (5 phases):**
1. Phase 1 — Read everything (outline, cropped PNGs, memories)
2. Phase 2 — Reconcile memories (limited surgical edits only)
3. Phase 3 — Status snapshot (✅ / 🟡 / ⬜ / 🚧 per figure)
4. Phase 4 — Report
5. Phase 5 — Persist report + update sync coordinator memory

(Figure refresh and outline embed live in the `cropfig` skill, not in `/sync`.)

**Saved to:** `${Sync report dir}/sync_YYYY-MM-DD.md`

**Critical:** Phase 2 is **strictly limited** — no auto-rewriting of agent-authored interpretive content. Sync can only add/refresh sync markers and append drift entries.

[Source: `commands/sync.md`](../commands/sync.md)

### Authority hierarchy (sync's mental model)

| Question | Ground truth |
|---|---|
| What exists right now? | Cropped PNGs in `Figure PNG dir` (produced by `cropfig`) |
| Where are we heading? | `Outline file` |
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
- Figure source: decks/main.pptx → /…/png/
- Snapshot status: 8 cropped PNGs available
- Per-figure summary: Fig 1 ✅, Fig 2 ✅, Fig 3 🟡, Fig 4 🚧, ...

### Goal alignment (vs. outline.md)
- ✅ Completed: Fig 1, Fig 2, Fig 6
- 🟡 In progress: Fig 3 (panel C placeholder), Fig 5 (stale)
- ⬜ Not started: Fig 8
- 🚧 Blocked: Fig 4 (waiting on R4 permutation test result)

### Agent memory updates
- supervisor: Last synced refreshed; 1 drift flagged
- analysis-implementer: no change
- paper-writer: no change
- figure-descriptor: 1 drift flagged (Fig 5 condition labels)
- reviewer: no change

### ⚠️ Manual review needed
- Fig 5 figure-descriptor memory says "Raw / Own / Other" but slide shows "Baseline / Treatment / Sham" — please reconcile.
```

## Orchestration engines (v0.2–v0.4)

Six engine commands automate multi-step research workflows. Each engine reads/writes state in `.claude/omcr-state/`, dispatches one or more agent personas via the [`orchestrate`](../skills/orchestrate/SKILL.md) primitive skill, and reports a DONE / CONTINUE / BLOCKED / HALT verdict. Engines are **leaves** — they never call other slash-command engines; cross-engine coordination is the autonomous `/supervisor-drive`'s job.

| Engine | Pattern | What it drives |
|---|---|---|
| `/iterate-revision <path>` | writer ↔ reviewer loop | Polish one manuscript section until reviewer is satisfied |
| `/literature-sweep <topic>` | N parallel curators (1–4) | Find + verify N papers; drop into BibTeX + summary CSV (hard verify-gate) |
| `/respond-reviewer <letter>` | classify & dispatch | Per-comment rebuttal letter; structural comments are human-gated |
| `/figure-bake <fig-id>` | 3-agent loop | Design → implement → critique loop with `cropfig` integration |
| `/outline-expand <outline>` | map-reduce | Outline → N parallel section drafts + terminology-drift lint |
| `/supervisor-drive [--auto]` | autonomous driver | Bottleneck-ranker dispatches the right engine; 6 safety gates |

**Full daily-workflow walkthrough:** [Using-Orchestration](Using-Orchestration.md)
**Autonomous mode deep dive:** [Autonomous-Drive](Autonomous-Drive.md) (6 safety gates, priority rules, modes)
**Internal mechanics (state store + 4 primitives):** [Orchestration-Model](Orchestration-Model.md)
**Composition with OMC (5 worked recipes):** [Orchestration-Comparison](Orchestration-Comparison.md) and [With-OMC](With-OMC.md)

Source files: [`commands/iterate-revision.md`](../commands/iterate-revision.md), [`commands/literature-sweep.md`](../commands/literature-sweep.md), [`commands/respond-reviewer.md`](../commands/respond-reviewer.md), [`commands/figure-bake.md`](../commands/figure-bake.md), [`commands/outline-expand.md`](../commands/outline-expand.md), [`commands/supervisor-drive.md`](../commands/supervisor-drive.md). Each engine's skill lives at `skills/<name>/` with phase files documenting per-step behavior.

## `cropfig` (skill, not a slash command)

**Goal:** Three-step pipeline from a `.key` / `.pptx` deck to manuscript + outline. Produces vector PDFs (for `\includegraphics` in the .tex) and outline-grade PNGs (for `![Figure N](...)` in the outline.md) — both derived from the same cropped artifact so they cannot drift.

**Invocation:** Not directly via `/`; agents and other commands invoke via the `Skill` tool with `skill="cropfig"`, or run the three scripts directly.

**Inputs:** `DECK_FILE` (required) + optional `MANUSCRIPT_DIR`, `OUTLINE_FILE`, `RESULT_PATTERN`, `CROPFIG_PROBE_DPI`, `CROPFIG_PNG_DPI` env vars (or the corresponding Research-stack fields). Defaults derive output paths from `dirname($DECK_FILE)`.

**Output contract:**

| Path | Owner | Content |
|---|---|---|
| `<dirname($DECK_FILE)>/pdf/figureNN.pdf` | func 2 | cropped vector PDF, manuscript-grade |
| `<dirname($DECK_FILE)>/png/figureNN.png` | func 2 | rasterized view of the cropped PDF, outline-grade |
| `$MANUSCRIPT_DIR/figures/figureNN.pdf` | func 3 (copy) | identical to the source PDF — used by the .tex |
| `<dirname($OUTLINE_FILE)>/figures/figureNN.png` | func 3 (copy) | identical to the source PNG — referenced by the outline |
| `$OUTLINE_FILE` | func 3 (modifies) | `![Figure N](figures/figureNN.png)` inserted after each result heading |

**Implementation:** PyMuPDF (vector PDF CropBox + per-slide split) + a band-classification heuristic in `crop_bounds.py` (color saturation + long-dark-run detection on a probe rasterization).

[Source: `skills/cropfig/SKILL.md`](../skills/cropfig/SKILL.md)

### Direct CLI use

```bash
# Required: point at the deck
export DECK_FILE=decks/main.pptx

# Func 1 — deck → per-slide vector PDFs (staging dir is ephemeral)
STAGE=$(mktemp -d)
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/export_deck.py "$DECK_FILE" "$STAGE"

# Func 2 — crop each PDF, emit cropped PDF + outline PNG next to the deck
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_figures.py "$STAGE"
rm -rf "$STAGE"

# Func 3 — copy artifacts into the manuscript + outline trees
MANUSCRIPT_DIR=paper OUTLINE_FILE=outline.md \
  python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/upload_figures.py
```

`crop_figures.py` accepts optional positional output dirs (`<staging> <pdf_out> <png_out>`); `upload_figures.py` reads from `<dirname($DECK_FILE)>/pdf` and `<dirname($DECK_FILE)>/png` and copies into the manuscript + outline trees. Func 3 is idempotent — re-running replaces the outline embed links rather than duplicating them.

## `verify-citation` (skill, not a slash command)

**Goal:** Verify that an academic citation exists and that its metadata matches what is claimed for it. Hits CrossRef for canonical metadata, OpenAlex for the abstract, and optionally writes the verdict into the project's literature summary table (`references.csv` by default) without clobbering human-curated columns.

**Invocation:** Used primarily by `@literature-curator` as a gate on every citation added to the bibliography. Can also be invoked directly for one-off audits.

**Inputs:** `BIB_FILE`, `SUMMARY_FILE`, `CITATION_VERIFY_EMAIL` (env vars) or the corresponding Research-stack fields.

**Modes:**

```bash
# Verify a single DOI (existence check + fetch metadata + fetch abstract)
python3 .../verify_citation.py --doi 10.1038/nature14236

# Verify one citekey from the project BibTeX
python3 .../verify_citation.py --bib references.bib --key smith2023connectome

# Full audit of the BibTeX
python3 .../verify_citation.py --bib references.bib

# Full audit AND write verified_on/verify_status into the summary table
python3 .../verify_citation.py --bib references.bib --summary-csv references.csv

# Attach a one-line claim for downstream logging (skill does NOT judge claim-fit — the agent reads the abstract and decides)
python3 .../verify_citation.py --doi 10.1038/nature14236 \
        --claim "DQN reaches human-level performance on Atari"
```

**Statuses:**

| Status | Meaning |
|---|---|
| `PASS` | DOI resolves AND title/authors/year all match (case-insensitive, normalized) |
| `MISMATCH` | Found at CrossRef but at least one metadata field disagrees with the BibTeX entry |
| `NOT_FOUND` | DOI does not resolve and title+author search returns no plausible match |
| `NOT_VERIFIED` | Network error — not treated as a pass |

**Exit codes:** `0` = all PASS; `1` = at least one MISMATCH/NOT_FOUND/NOT_VERIFIED; `2` = script error (missing file, malformed BibTeX, persistent network failure).

**Summary-table columns the skill writes:** `verified_on` (YYYY-MM-DD), `verify_status`. Plus bibliographic defaults (`authors`, `year`, `title`, `venue`, `doi`) **only when the row is blank** — never overwrites curator-curated columns (`bucket`, `our_use`, `paper_says`, `cited_sections`).

**Implementation:** Pure Python stdlib (urllib + csv + json + re) — no external dependencies.

[Source: `skills/verify-citation/SKILL.md`](../skills/verify-citation/SKILL.md) and [`verify_citation.py`](../skills/verify-citation/verify_citation.py)

## See also

- [Configuration](Configuration.md) — `## Research stack` block schema
- [Agents](Agents.md) — agents that may invoke these commands
- [Hooks](Hooks.md) — `pii-scrub` runs before any write the commands produce
