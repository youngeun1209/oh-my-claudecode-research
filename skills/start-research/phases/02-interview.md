# Phase 2 — Interview

Ask the user **only for fields that are missing or still `[TBD]`** (consult the state recorded by phase 1). Two policies depending on field type:

## A. Infrastructure fields — propose a default, accept "skip"

For each field below, present the default and ask "use this, or override?". If the user types `[skip]` or hits enter without input, accept the default. No push-back.

| Field | Default | Goes into |
|---|---|---|
| `Deck file` | (ask user — `.key` or `.pptx` path; no default) | `## Research stack` |
| `Outline file` | `outline.md` | `## Research stack` |
| `Figure count` | `8` | `## Research stack` |
| `Result pattern` | `^### Result (\d+)` | `## Research stack` |
| `Report language` | `English` | `## Research stack` |
| `Report output dir` | `./todofig_reports/` | `## Research stack` |
| `Sync report dir` | `./sync_reports/` | `## Research stack` |
| `Figure PDF dir` | `<dirname(Deck file)>/pdf/` | `## Research stack` (optional override) |
| `Figure PNG dir` | `<dirname(Deck file)>/png/` | `## Research stack` (optional override) |
| `Manuscript dir` | `paper/` | `## Research stack` |
| `BibTeX file` | `<Manuscript dir>/references.bib` (i.e. `paper/references.bib`) | `## Research stack` |
| `Summary file` | `references.csv` (project root — kept OUT of the manuscript dir so it doesn't get pushed to Overleaf) | `## Research stack` |
| `CrossRef email` | (none) | `## Research stack` (optional — recommend the user provide it for verify-citation polite-pool access) |
| `Overleaf git URL` | (none) | `## Research stack` (optional — only if user has Overleaf with Git Integration enabled, which requires a paid plan) |
| `User-dialog language` | `English` | `## Language preference` (optional) |
| `Manuscript language` | `English` (do not let the user change this — keep manuscripts in English for venue compatibility) | `## Language preference` |

## B. Scientific identity fields — never invent, but push back once on `[skip]`

For each field below, ask plainly. If the user can answer, write it through. If the user says "skip" or "don't know yet", push back **exactly once** with the reason it matters, then accept `[TBD: <one-line note>]` if they still want to skip. Never invent content here.

| Field | Goes into | Push-back rationale (use when user skips) |
|---|---|---|
| `Working title` | `## Project context` | "Even a placeholder title gives `supervisor` something to anchor on — can be a rough one-liner." |
| `Field / sub-field` | `## Project context` | "Field determines which preset to suggest and how `figure-descriptor` defaults plot conventions — please name it even if narrow." |
| `First author` | `## Project context` | "Author identity is needed for the cover letter and the BibTeX self-citation later." |
| `PI / advisor` | `## Project context` | "PI name lets `supervisor` adjust framing tone and venue strategy." (Soft push-back — if the user genuinely has no PI, accept.) |
| `Target venue` | `## Project context` | "Venue determines word limits, figure budget, reviewer expectations, and `reviewer`'s severity bar. Even a top-2 short list is more useful than `[TBD]`." |
| `Backup venues (2–3)` | `## Project context` | "Helps `supervisor` keep a tier-list for framing pivots." (Skip allowed without push-back.) |
| `Central hypothesis` | `## Project context` | "Without a hypothesis, `supervisor` will ask every conversation. A rough one-sentence stake is far better than `[TBD]` — refine later." |
| `Research topic` | `## Project context` | "What's the **big-picture question**, distinct from the specific hypothesis? One or two sentences." |
| `Datasets` | `## Project context` | "Which dataset(s) are you using? Source, modality, approximate size, access status. If none decided yet, `[TBD]` is OK but flagged." |
| `Narrative spine — Gap` | `## Project context` | "What has the field NOT yet established that this study will?" |
| `Narrative spine — Question` | `## Project context` | "The specific testable question." |
| `Narrative spine — Approach` | `## Project context` | "One sentence of methodology." |
| `Narrative spine — Implication` | `## Project context` | "What this changes about how the field thinks. Often unknown early — `[TBD: filled as results emerge]` is the canonical placeholder." |

## C. Preset overlay (final step of the interview)

Consult `preset_arg` from the [SKILL.md](../SKILL.md) argument parsing:

- If `preset_arg ∈ {minimal, no-overlay}`: skip this section entirely.
- If `preset_arg = neuro-fmri`: confirm once with the user before applying. No need to re-list options.
- Otherwise (empty): ask: "Apply a domain preset? Available presets in this plugin: `neuro-fmri`. Or `none` to stay field-neutral."

If the user selects a preset, record the preset name. Phase 3 will write it as `Preset overlay: <name>` in the `## Project context` block; phase 4 will use it to pick the right memory template per agent.
