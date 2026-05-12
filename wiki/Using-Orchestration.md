# Using Orchestration — practical walkthrough

How to actually USE OMCR's 6 orchestration engines after `/omcr-setup` and `/start-research` are done. This page is the "what do I type" reference; for internal mechanics see [Orchestration-Model](Orchestration-Model.md), for OMC composition see [Orchestration-Comparison](Orchestration-Comparison.md), and for the autonomous mode deep-dive see [Autonomous-Drive](Autonomous-Drive.md).

## 3 levels of automation

OMCR layers from manual to fully autonomous. Pick the level that matches what you want right now:

### Level 1 — Manual agent calls (most control)

The classic `@`-mention pattern. No orchestration; you drive every step.

```
@supervisor where are we?
@analysis-implementer run the permutation test on R3
@paper-writer draft the methods section
@reviewer review the Introduction at our target-venue bar
```

**When to use:** exploratory work, brainstorming, one-off questions, or when you want full control over each handoff.

### Level 2 — Engine invocation (most common day-to-day)

One engine drives one workflow to completion. You start it; the engine reads/writes state under `.claude/omcr-state/`, dispatches subagents, loops, and reports back with a DONE / CONTINUE / BLOCKED / HALT verdict.

```bash
# Iterate one section until the reviewer is satisfied
/iterate-revision sections/results.tex --max-iter 3 --venue Nature

# Find N papers on a topic; verify; drop into your BibTeX + summary CSV
/literature-sweep "frontoparietal working memory" --n 20

# Classify each reviewer comment, dispatch the right specialist, assemble rebuttal
/respond-reviewer reviewer-letter.md --format latex

# Drive one figure design→implementation→critique loop
/figure-bake fig1 --max-iter 3

# Take an outline; produce N parallel section drafts
/outline-expand outline.md
```

**When to use:** focused task, single deliverable, when you know exactly what you want next.

### Level 3 — Autonomous drive (least intervention)

`/supervisor-drive` reads project state, picks the highest-priority next engine, runs it, re-reads state, loops. Six hard safety gates protect against runaway behavior.

```bash
# Interactive: confirm each engine choice before running
/supervisor-drive

# Auto: bounded by max-iter, budget, and safety gates
/supervisor-drive --auto --max-iter 5 --budget-tokens 80000

# Preview only: see the plan; don't run anything
/supervisor-drive --plan-only

# Resume after a previous halt
/supervisor-drive --resume <run-id>

# Disable per-engine git commits if you want clean history
/supervisor-drive --auto --no-commit
```

**When to use:** long working session, end-of-day "drive everything forward", or when you want OMCR to find the bottleneck for you.

Deep dive: [Autonomous-Drive](Autonomous-Drive.md).

## End-to-end example

A week-long arc using all 6 engines, ending in autonomous submission-readiness.

### Day 0 — install + initialize (once per project)

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
/plugin install oh-my-claudecode-research
```

In your project root:

```
/omcr-setup        # scaffold CLAUDE.md blocks + agent-memory + .claude/omcr-state/
/start-research   # interview: hypothesis, venue, datasets, outline path
```

After this, `.claude/omcr-state/` exists with 5 empty state JSONs: `paper.json`, `reviews.json`, `citations.json`, `figures.json`, `rebuttals.json` (plus `_run-log.jsonl`).

### Day 1 — literature scan + outline expansion

Want a broad lit review and a first draft?

```
/literature-sweep "neural manifold motor cortex" --n 15
# → references.bib + references.csv populated with verified entries only
# → citations.json.last_sweep records what happened

/outline-expand outline.md
# → 5 sections drafted in parallel from outline + shared nomenclature
# → paper.json.sections[*].status = drafted
# → terminology-drift.md (non-blocking) flags inconsistent term usage across sections
```

### Day 2 — refine each section

```
/iterate-revision sections/methods.tex --max-iter 3
# Watch it loop writer → reviewer → writer → reviewer until 0 major issues
# → paper.json.sections.methods.status = approved when DONE
# → reviews.json gets one new entry per iteration

/iterate-revision sections/results.tex --venue Nature
# Same pattern, different section
# Will refuse if section contains [TBD:...] markers; pass --allow-tbd to override
```

### Day 3 — figures

```
/figure-bake fig1 --max-iter 3
# figure-descriptor produces brief → analysis-implementer runs code → reviewer critiques
# → cropfig auto-runs to produce manuscript-grade PDF + outline PNG
# → figures.json.fig1.{brief,impl,critique}_status updated each iter
```

### Day 4 — reviewer letter

```
/respond-reviewer received-review.md --manuscript paper/
# parses 12 comments → @supervisor classifies each (prose / analysis / citation / clarif / structural)
# → routes prose-fixes to @paper-writer, new analyses to @analysis-implementer, citations to @literature-curator
# → assembles rebuttal-letter.tex
# Structural comments are flagged for YOU — never auto-fixed (ethical gate)
```

### Day 5 — drive everything to submission

```
/supervisor-drive --auto --budget-tokens 100000
```

Internally:
- Reads all 5 state files; picks the highest-priority bottleneck
- Runs that engine; re-evaluates state from scratch (engines never chain directly)
- Loops until `paper.json.submission_ready == true` OR max_iter OR budget OR safety gate trip
- Per-engine git commits along the way (use `--no-commit` to disable)
- Halts immediately on any of the 6 safety gates

## Engine selector — at a glance

| Situation | Engine |
|---|---|
| Polish one section until reviewer-ready | `/iterate-revision <path>` |
| Find papers on a topic, verify, add to bib | `/literature-sweep <topic>` |
| Reviewer letter arrived, need rebuttal | `/respond-reviewer <letter-path>` |
| Drive one figure design→impl→critique | `/figure-bake <fig-id>` |
| Outline → N parallel section drafts | `/outline-expand <outline-path>` |
| Drive the whole paper forward unattended | `/supervisor-drive --auto` |
| Preview what supervisor would do | `/supervisor-drive --plan-only` |
| Read current state in plain English | `@supervisor where are we?` |

## Bottleneck-ranker (how `/supervisor-drive` decides)

The autonomous mode applies these hardcoded priority rules in order (no config knob; override via `--interactive` or `--plan-only`):

1. **Blocked sections** (`status: blocked`) → human action required, halt
2. **TBD-blocked sections** (`status: blocked-on-tbd`) → halt, ask user to resolve markers or pass `--allow-tbd`
3. **Critical citations missing** → `/literature-sweep` or `@literature-curator` dispatch
4. **Unwritten sections** (`status: empty`) → `/outline-expand` or `/iterate-revision`
5. **Drafted-but-unreviewed sections** (`status: drafted`) → `/iterate-revision`
6. **Pending reviewer comments** → `/respond-reviewer`
7. **Figures with mismatched briefs** → `/figure-bake`
8. **Everything approved + verified** → `submission_ready = true`, exit DONE

Only one engine + one target per iteration (no parallel dispatch at v0.4).

## Where state lives

All orchestration state lives under `.claude/omcr-state/` in your project (gitignored):

| File | What it tracks |
|---|---|
| `paper.json` | Manuscript progress per section (`status` / `iter` / `last_review_id` / `outline` / `hypothesis`) |
| `reviews.json` | Append-only history of every reviewer verdict (one entry per iteration) |
| `citations.json` | BibTeX queue + verification states + last sweep summary |
| `figures.json` | Per-figure brief / impl / critique status |
| `rebuttals.json` | Append-only rebuttal entries from `/respond-reviewer` |
| `_run-log.jsonl` | Every engine invocation logged (run_id / engine / tokens_used / verdict) |

Canonical schemas: [`develop/example-state/`](../develop/example-state/) (tracked as reference; copied into your project by `/omcr-setup`). Engines never overwrite human-curated fields; they only add/append.

`schema_version` is a JSON string (`"1"`). Additive bumps (`"1.1"`) require no migration; breaking bumps (`"2"`) will (deferred to v0.5+).

## Safety in autonomous mode

`/supervisor-drive --auto` has 6 hard safety gates. Every gate **requires explicit user confirmation** (a typed phrase, not just "yes") to proceed even in `--auto`:

| Gate | What it catches | Override |
|---|---|---|
| **HypothesisChange** | Engine arg or brief modifies `paper.json.hypothesis` | typed `confirm-hypothesis-change` |
| **NewCitation** | Engine wants to add a citation outside the verified queue | typed confirmation |
| **NewExperiment** | Brief contains "design new experiment" / "collect more data" | typed confirmation |
| **StructuralRewrite** | Brief contains "restructure" / "reframe" / "change conclusion" | typed confirmation |
| **BudgetExceeded** | Projected cumulative tokens > `--budget-tokens` (× 1.25 padded) | typed confirmation |
| **CriticalIssue** | Prior engine returned BLOCKED with critical severity | **no override — always halts** |

Plus checkpointing: a git commit fires after every successful engine completion (unless `--no-commit`), so any drift is bisectable. Engine exceptions trigger immediate halt-with-error-report — no retry, no fallback engine.

## Read-only intent

If you just want to KNOW state without changing anything:

```
@supervisor where are we?
/supervisor-drive --plan-only
```

Both are non-destructive. Neither dispatches an engine. `@supervisor` is **advisory** under the v0.4 split — it reads state and recommends. The actual driving happens via `/supervisor-drive`.

## When to compose with OMC

OMCR's engines compose with upstream OMC's generic orchestrators when you want extra power:

| Need | Composition |
|---|---|
| Retry an engine with a verifier | `/oh-my-claudecode:ralph` wrapping OMCR engine |
| True parallel literature scan at scale | `omc team N:literature-curator` instead of `/literature-sweep --parallel` |
| Try N different writing styles | `/oh-my-claudecode:ultraqa` over `/iterate-revision` |
| Budget-tracked autonomous drive with decision log | `/oh-my-claudecode:autopilot` wrapping `/supervisor-drive --auto` |
| Cross-check a critical claim | `@oh-my-claudecode:verifier` after `/iterate-revision` DONE |

Full matrix + 5 worked recipes: [Orchestration-Comparison](Orchestration-Comparison.md) and [With-OMC](With-OMC.md).

## See also

- [Orchestration-Model](Orchestration-Model.md) — internal mechanics (state primitives, dispatch, evaluate, loop)
- [Autonomous-Drive](Autonomous-Drive.md) — `/supervisor-drive` deep dive with example sessions
- [Orchestration-Comparison](Orchestration-Comparison.md) — OMCR alone vs OMCR + OMC, decision tree, cost table
- [Commands](Commands.md) — full slash-command reference
- [Agents](Agents.md) — the 6 personas the engines dispatch
- [Configuration](Configuration.md) — `## Research stack` block + `data_root` for `/figure-bake`
