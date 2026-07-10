# Standalone Usage (OMCR without OMC)

OMCR works fully standalone — no OMC required. This page walks through the canonical workflow with just OMCR installed.

If you also have OMC installed (or want to install it), see [With OMC](With-OMC.md) for the richer workflow.

## When standalone is enough

- You're early in a project and don't need a literature management database, an experiment-run registry, or a stateful Python REPL.
- You want the lightest possible install. OMCR is plain markdown + shell — no Node, no MCP, no Python beyond the cropfig skill.
- Your figure/outline workflow is straightforward (deck + outline + 6 agents covers it).

## What you get standalone

| Surface | Behavior |
|---|---|
| 6 `@`-mentionable agents | Full personas, English-by-default, configurable language |
| 7 setup/workflow/utility commands (`/omcr-setup`, `/start-research`, `/todofig`, `/sync`, `/session-start`, `/save-session-log`, `/update-version`) | Parameterized via `## Research stack` block in your CLAUDE.md |
| **6 orchestration engines** (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`) | Multi-step workflow drivers with `.claude/omcr-state/` persistence — see [Using-Orchestration](Using-Orchestration.md) |
| `cropfig` + `verify-citation` + `manuscript-scaffold` + `paper-ingest` skills | Figure crop pipeline + citation verification + LaTeX scaffold + reading library ([Reading-Library](Reading-Library.md)) |
| 4 hooks | PII guard + MEMORY auto-load + citation warning + setup nudge |
| `templates/MEMORY.template.md` | Canonical schema for per-agent memory |
| `examples/neuro-fmri/` | Overlay preset if you do neuroimaging (fMRI / EEG / MEG) work |

## Canonical session — paper-writing project

Suppose you're working on a paper. Here's a typical day-of-work session.

### Morning — orient and plan

```
@supervisor where are we?
```

Supervisor reads `CLAUDE.md` + `.claude/agent-memory/supervisor/MEMORY.md` and reports:
- Current phase (analysis / writing / revision)
- Most important unresolved question
- Concrete next action + which subagent should take it

### Implementation work

```
@analysis-implementer run the permutation test on the R3 contrast
```

Analysis-implementer:
- Reads its own MEMORY.md for parameter conventions, exclusion criteria, file paths
- Implements the analysis (modular Python with seeds, configs, logs)
- Saves outputs to disk + a sanity-check plot
- Reports: N units in, N excluded (and why), parameter values, output shape
- Updates its MEMORY.md if a new parameter choice or exclusion rule was settled

### Figure work

```
@figure-descriptor design Fig 5 — show the R3 contrast result alongside the null distribution
```

Figure-descriptor produces a complete brief:
- Single declarative claim for the figure
- Per-panel data, plot type, axes, color encoding, N
- Layout / hierarchy / consistency notes
- Caption text (bold finding title + per-panel description)
- Implementation notes (vector tool techniques, when to use Python export vs. native drawing)

You implement the figure in your tool of choice (Keynote, Illustrator, Inkscape).

### Gap check

```
/todofig
```

This compares your captured figure deck against your outline (paths from the `## Research stack` block) and produces a Korean / English TODO with P0/P1/P2 priorities. Save to `${report_output_dir}/`.

For a focused single-figure pass: `/todofig Fig5`.

### Writing

```
@paper-writer draft the Introduction
```

Paper-writer:
- Reads CLAUDE.md for the narrative spine
- Reads its own MEMORY.md for nomenclature decisions and hard-won phrasings
- Drafts the section following the section-by-section standards
- Flags any claim that needs a citation or `[STAT: ...]` placeholder
- Reports back: word count, flagged dependencies

### Quality gate

```
@reviewer review the Introduction draft
```

Reviewer applies the target-venue standards (configured in your CLAUDE.md). Returns:
- Verdict (Ready / Needs revision / Not ready)
- Major concerns (problem / why it matters / what is required)
- Minor concerns
- Optional suggestions

Major concerns flow back to supervisor → analysis-implementer or paper-writer for fixes.

### End of session

```
/sync
```

Sync:
- Reconciles each agent's MEMORY.md against current deck and outline (PNGs in `Figure PNG dir`)
- Reports drifts (no auto-resolution of judgment calls)

(Figure refresh and outline embedding now live in the `cropfig` skill — run `cropfig` separately before `/sync` if you need fresh figures.)

Sync is the "save state" command — run before closing the session so the next day picks up where you left off.

### Want more automation than @-mention?

The session above stays at **Level 1** (manual `@`-mention dispatching). OMCR also ships 6 **orchestration engines** that automate multi-step workflows (a whole section refinement, a literature scan, a rebuttal letter, etc.) and an **autonomous driver** that picks the right engine based on project state.

See [Using-Orchestration](Using-Orchestration.md) for the Level 2 (engine commands like `/iterate-revision`, `/literature-sweep`) and Level 3 (`/supervisor-drive --auto`) walkthroughs.

## Memory pattern in practice

OMCR's memory is just markdown files. Each agent has `.claude/agent-memory/<agent>/MEMORY.md` plus optional topic files (linked from MEMORY.md).

```
your-project/
├── CLAUDE.md                 ← your project context
└── .claude/
    └── agent-memory/
        ├── supervisor/
        │   ├── MEMORY.md     ← index + active state
        │   ├── hypothesis-log.md
        │   ├── literature-map.md
        │   └── objections-log.md
        ├── analysis-implementer/
        │   ├── MEMORY.md
        │   ├── pipeline-status.md
        │   └── bugs-log.md
        ├── paper-writer/
        │   ├── MEMORY.md
        │   ├── manuscript-status.md
        │   └── nomenclature.md
        ├── figure-descriptor/
        │   ├── MEMORY.md
        │   ├── color-system.md
        │   └── figure-status.md
        └── reviewer/
            ├── MEMORY.md
            └── open-concerns.md
```

The `memory-load` hook concatenates every `MEMORY.md` and injects it into session start. Topic files are loaded on-demand by the agent (it reads them when relevant).

Start with the schema at `templates/MEMORY.template.md` and the redacted neuro-fmri skeletons at `examples/neuro-fmri/memory-templates/`.

## Limits of standalone

Things you'll notice as gaps:

- **No literature management** — your supervisor maintains a literature-anchor list in MEMORY.md, but there's no searchable database. You manage citations in your reference manager (Zotero, EndNote, Paperpile).
- **No experiment-run registry** — analysis-implementer logs each run in its MEMORY.md or topic files, but there's no cross-run comparison surface. You roll your own (e.g., a CSV of run hashes + parameters + eval scores).
- **No stateful Python REPL** — analysis-implementer writes Python scripts that you run in your terminal or notebook. No interactive Python kernel in-session.
- **No automatic citation verification** — `citation-warn` heuristically flags uncited paragraphs but doesn't validate the URLs / cited papers actually exist.
- **No structured `verifier` agent** — `reviewer` covers manuscript readiness, but you don't get OMC's `verifier` (fresh-evidence completion checks against acceptance criteria).
- **No causal tracer** — `reviewer` raises objections but doesn't run OMC's tracer (evidence-driven competing-hypotheses ranking).

If any of these gaps matter to you, install OMC alongside — [With OMC](With-OMC.md).

## Quick reference

| You want to | Command |
|---|---|
| Orient on a project | `@supervisor where are we?` |
| Implement an analysis | `@analysis-implementer ...` |
| Design a figure | `@figure-descriptor design Fig N — ...` |
| Draft a section | `@paper-writer draft the [Intro/Methods/Results/Discussion]` |
| Adversarial review | `@reviewer review the [section / Fig N / full draft]` |
| Compare deck to outline | `/todofig` (full) or `/todofig FigN` (single) |
| Save state + reconcile memories | `/sync` |
| Deck → cropped figures (vector PDF + outline PNG) | `cropfig` skill (invoked manually or by other commands) |
