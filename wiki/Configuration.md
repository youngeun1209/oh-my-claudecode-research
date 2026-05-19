# Configuration

OMXR is configured via three layers, in order of precedence:

1. **Environment variables** — highest priority, useful for one-off overrides
2. **Project `AGENTS.md` `## Research stack` block** — persistent project-level config
3. **Hardcoded defaults** in the command / skill / hook source

This page documents what each layer carries.

## Layer 2 — `## Research stack` block in AGENTS.md

Add a `## Research stack` section to your project's `AGENTS.md`. The skills (`$todofig`, `$sync`) and the `cropfig` skill read from it.

```markdown
## Research stack (used by $todofig, $sync, cropfig)

- **Deck file:** decks/main.key  (`.key` or `.pptx`; required by `cropfig`)
- **Figure PDF dir:** figures/pdf/   (cropped vector PDFs — manuscript artifact)
- **Figure PNG dir:** figures/png/   (cropped raster PNGs — outline artifact)
- **Outline file:** outline.md
- **Figure count:** 8
- **Result pattern:** `^### Result (\d+)`
- **Report language:** English
- **Report output dir:** .$todofig_reports/
- **Sync report dir:** .$sync_reports/
```

### Field reference

| Field | Used by | Type | Default | Purpose |
|---|---|---|---|---|
| `Deck file` | `cropfig`, `$sync`, `$todofig` | path | (required by `cropfig`) | Path to a `.key` or `.pptx` deck. `cropfig` exports it to per-slide vector PDFs and crops them; `$sync` and `$todofig` derive the PNG dir from it. |
| `Figure PDF dir` | `cropfig` func 3 | path | `<dirname(Deck file)>/pdf/` | Cropped per-slide vector PDFs (manuscript artifact). Default derived from `Deck file` — outputs land next to the deck. |
| `Figure PNG dir` | `cropfig` func 3, `$sync`, `$todofig` | path | `<dirname(Deck file)>/png/` | Cropped per-slide raster PNGs (outline artifact). Default derived from `Deck file`. `$sync` and `$todofig` inspect these to assess current figure state. |
| `Outline file` | `$todofig`, `$sync`, `cropfig` func 3 | path | `outline.md` | Markdown outline describing intended figure contents. `cropfig` func 3 inserts `![Figure N](figures/figureNN.png)` after each result heading. |
| `Figure count` | `$todofig`, `$sync` | integer | (required) | Total figures expected in the project. Used for the status table loop. |
| `Result pattern` | `$todofig`, `$sync`, `cropfig` func 3 | regex | `^### Result (\d+)` | Pattern used to find result/figure blocks in the outline. Capture group → figure number (1-indexed). |
| `Report language` | `$todofig`, `$sync` | string | `English` | Output language for the human-readable report. Manuscript content always stays English. |
| `Report output dir` | `$todofig` | path | `.$todofig_reports/` | Where `$todofig` saves its dated TODO report. |
| `Sync report dir` | `$sync` | path | `.$sync_reports/` | Where `$sync` saves its dated status snapshot. |
| `Manuscript dir` | `$start-research`, `@paper-writer` | path | `paper/` | Directory holding the LaTeX manuscript (`main.tex`, `sections/`, `references.bib`, `figures/`). Initialized by `$start-research` (via the `manuscript-scaffold` skill) from [`templates/manuscript-skeleton/`](../templates/manuscript-skeleton/). |
| `BibTeX file` | `@literature-curator`, `verify-citation` | path | `<Manuscript dir>/references.bib` | Canonical BibTeX file. Defaults inside the manuscript dir so it gets pushed to Overleaf when configured. |
| `Summary file` | `@literature-curator`, `verify-citation` | path | `references.csv` (project root) | Human-readable literature summary table. Lives **outside** the manuscript dir on purpose — it's project metadata, not part of the paper. |
| `CrossRef email` | `verify-citation` | email | (optional) | Polite-pool identifier for CrossRef. Recommended — higher rate limit and priority on the public API. Not used to send any mail. |
| `Overleaf git URL` | `$start-research` | URL | (optional) | If set, `$start-research` (via the `manuscript-scaffold` skill) clones the Overleaf project into `Manuscript dir` and scaffolds the skeleton there. Requires Overleaf paid plan with Git Integration. Authentication token is cached only in git's credential helper or `~/.netrc` — never written to AGENTS.md or any tracked file. |
| `Data root` | `$figure-bake` | path | `./data/` | Root directory for experimental data. `$figure-bake` resolves figure data references relative to this. Per-figure paths inside a figure brief reference paths under this root. |

### First-run wizard

On the first invocation of `$todofig` or `$sync` in a project without a `## Research stack` block:

1. The command notices the missing config.
2. It asks the user (via natural conversation) for the required fields.
3. It **offers to write** the block to `AGENTS.md` automatically.
4. Subsequent invocations use the stored values.

You can skip the wizard by adding the block manually before first invocation.

## Layer 1 — Environment variables

Use environment variables to override layer 2 for a single invocation or to pass values to the `cropfig` skill before the project AGENTS.md exists.

| Variable | Used by | Maps to layer 2 field |
|---|---|---|
| `DECK_FILE` | `cropfig` (all 3 funcs) | `Deck file` |
| `MANUSCRIPT_DIR` | `cropfig` func 3 | `Manuscript dir` |
| `OUTLINE_FILE` | `cropfig` func 3 | `Outline file` |
| `RESULT_PATTERN` | `cropfig` func 3 | `Result pattern` |
| `CROPFIG_PROBE_DPI` | `cropfig` func 2 | (no layer-2 field; tunable knob) |
| `CROPFIG_PNG_DPI` | `cropfig` func 2 | (no layer-2 field; tunable knob) |
| `CODEX_RESEARCH_DATA_ROOT` | `$figure-bake` | `Data root` |
| `CODEX_RESEARCH_DISABLE_PII_SCRUB` | `pii-scrub` hook | (n/a — disables) |
| `CODEX_RESEARCH_DISABLE_MEMORY_LOAD` | `memory-load` hook | (n/a — disables) |
| `CODEX_RESEARCH_DISABLE_CITATION_WARN` | `citation-warn` hook | (n/a — disables) |

Set environment variables in `.codex/hooks.json` (per-project) or your shell profile (global).

Example `.codex/hooks.json` snippet:

```json
{
  "env": {
    "DECK_FILE": "decks/main.key",
    "MANUSCRIPT_DIR": "paper",
    "OUTLINE_FILE": "outline.md"
  }
}
```

`DECK_FILE` is the only field `cropfig` strictly needs — the pdf/png output dirs default to `<dirname(DECK_FILE)>/pdf/` and `<dirname(DECK_FILE)>/png/`. `MANUSCRIPT_DIR` and `OUTLINE_FILE` are only consulted by `cropfig` func 3 (upload step).

## PII scrub patterns

The `pii-scrub` hook looks for patterns in this order:

1. **`.omx/omxr/scrub-patterns.txt`** in the current project (wins entirely if present).
2. **`hooks/default-scrub-patterns.txt`** shipped with OMXR (fallback defaults).

The project-level file is gitignored (covered by `.codex/`), so your actual sensitive patterns (advisor names, internal subject-ID formats) never get committed.

Format: one extended regex per line. Lines starting with `#` and blank lines ignored.

Example project override (`.omx/omxr/scrub-patterns.txt`):

```
# Standard contact info
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}

# This project's internal subject ID format (5-digit prefix HCP-#####)
\bHCP-[0-9]{5}\b

# Lab / advisor names you don't want leaking
(?i)\b(your-lab-name|advisor-name)\b
```

Test before committing:

```bash
echo '{"tool_input":{"file_path":"foo.md","content":"contact me at alice@example.com"}}' \
  | bash ~/.codex/plugins/oh-my-codex-research/hooks/pii-scrub.sh
echo "exit code: $?"   # expect 2 (blocked)
```

## AGENTS.md project-context section

Beyond the `## Research stack` block, your project's `AGENTS.md` should also have a `## Project context` block that the 6 agents read for scientific identity (hypothesis / venue / topic / datasets / narrative). The canonical schema:

```markdown
## Project context

- **Working title:** [your project name or [TBD]]
- **Field:** [your field / sub-field]
- **Target venue:** [target journal / conference, or [TBD: short note]]
- **Backup venues:** [comma-separated top 2–3, or [TBD]]
- **Central hypothesis:** [one sentence, or [TBD: short note]]
- **Research topic:** [the big-picture question — broader than the specific hypothesis; 1–2 sentences]
- **Datasets:** [name, source, modality, size, access status — or [TBD]]
- **Narrative spine:**
  1. *Gap:* [what the field has not established]
  2. *Question:* [the specific testable question]
  3. *Approach:* [methodology in one sentence]
  4. *Finding:* [filled as results emerge]
  5. *Implication:* [what this changes — or [TBD]]
- **Preset overlay:** [neuro-fmri / none]
```

`$omxr-setup` scaffolds these fields as `[TBD]` placeholders. `$start-research` then interviews you to fill them in. The interview **never invents** scientific identity — if you skip a scientific field, it stores `[TBD: <one-line note>]` so `@supervisor` knows to surface the gap later.

### Field semantics

- **Research topic vs. Central hypothesis.** The topic is the big-picture question your study sits inside (e.g. "How does network reconfiguration support flexible cognition?"); the hypothesis is the specific testable claim (e.g. "Network X shows greater state-dependent reconfiguration than Y during task Z."). Both matter — the topic anchors framing, the hypothesis anchors design.
- **Datasets.** What `@analysis-implementer` builds against and what `paper-writer` describes in Methods. Include enough detail to be unambiguous: name, modality, sample size if known, public/restricted/private access status, ethics approval status.
- **Target venue + Backup venues.** Drives reviewer expectations, word limits, figure budget, and `@reviewer`'s severity bar. Even a "top-1 choice + 2 backups" short list is far more useful than a single fixed venue, because `@supervisor` can advise framing pivots when results come in stronger or weaker than expected.

## Language preference

```markdown
## Language preference

- **User-dialog language:** Korean  (default is English)
- **Manuscript language:** English  (default — do not change)
```

The 6 agents are coded to default to English. If you want user-facing reports in another language, set `User-dialog language` here and the agents will adapt. Manuscript text stays in English regardless, for venue compatibility.

## See also

- [Standalone Usage](Standalone-Usage.md) — using OMXR's commands with this config
- [Commands](Commands.md) — full reference for `$omxr-setup`, `$start-research`, `$todofig`, `$sync`, plus the `cropfig`, `verify-citation`, and `manuscript-scaffold` skills
- [Hooks](Hooks.md) — full reference for the 4 hooks
