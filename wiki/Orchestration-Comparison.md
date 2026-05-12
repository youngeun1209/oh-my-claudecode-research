# Orchestration comparison — OMCR alone vs OMCR + OMC

This page is the maturity-milestone reference for "which tool when?" when both OMCR and OMC are installed. OMCR v0.4 ships 6 engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`) on top of 4 orchestration primitives. Upstream OMC ships generic execution modes (`ralph`, `team`, `autopilot`, `ultrawork`, `ultraqa`, `ralplan`, `autoresearch`) plus specialist agents (`verifier`, `tracer`, `document-specialist`, `deep-interview`). The two stacks compose cleanly because they share no state — OMCR lives in `.claude/omcr-state/`, OMC lives in `.omc/`.

If you have not installed OMC alongside, none of the "+ OMC" cells in this page are available. Read [Standalone Usage](Standalone-Usage.md) instead. If you only want recipes (commands you can copy-paste), jump to [With-OMC § Recipes](With-OMC.md#recipes--pairing-omcr-with-omc).

This page answers three questions in three sections:

- **§A — task → tool matrix.** Given a research task, which OMCR engine / OMC skill / pairing should you reach for?
- **§B — decision tree.** A "are you in a single session / want N strategies / want a long-running drive" walk-through that lands you on a concrete command.
- **§C — cost & complexity table.** Per-tool cost ranges and setup cost so you know what you are signing up for before you type.

A short fourth section (§D) restates the architectural invariants that make the matrix legal: which tool owns what, what cannot be nested inside what, and why OMCR and OMC compose without surprises.

---

## A — task → tool matrix

The first column names a common research task. The second column shows what OMCR can do on its own (no OMC dependency — works with a plain `/plugin install oh-my-claudecode-research`). The third column shows the OMCR + OMC pairing that turns the same task into a longer-running, more parallel, or more cross-validated workflow.

| Research task | OMCR alone | OMCR + OMC |
|---|---|---|
| Draft one section to revision-ready | `/iterate-revision sections/methods.tex --max-iter 3 --venue Nature` — loops `@paper-writer` ↔ `@reviewer` until DONE / BLOCKED / HALT. | `/oh-my-claudecode:ralph "/iterate-revision sections/methods.tex --venue Nature" --max-iter 5 --verifier "@oh-my-claudecode:verifier"` — adds an independent second-opinion gate around OMCR's own verdict rule. |
| Bulk literature scan (≤20 papers, in-session) | `/literature-sweep "neural manifolds in motor cortex" --n 20 --parallel 4` — sequential default, opt-in 1≤N≤4 in-session parallel batches. | `omc team 5:literature-curator "sweep 'neural manifolds in motor cortex' in 5 batches; merge into references.bib"` — tmux-backed parallelism that survives session restart. Use when 50+ papers / week-long sweep. |
| Multi-strategy section revision (try N styles) | — (OMCR engines all converge on a single output by design). | `/oh-my-claudecode:ultraqa "/iterate-revision sections/discussion.tex" --strategies "concise,detailed,narrative" --selector reviewer-rating` — tries 3 styles, keeps the one OMCR's `@reviewer` scored highest. |
| Self-correcting iteration loop on a stubborn section | The engine's own `--max-iter` cap (built-in to every loop engine). | `/oh-my-claudecode:ralph "/iterate-revision sections/discussion.tex" --max-iter 5 --critic "@oh-my-claudecode:verifier"` — keeps retrying until a *different* verifier (not OMCR's `@reviewer`) confirms DONE. |
| Cross-check a critical claim against methods + results | `@reviewer` raises severity-flagged objections inside `/iterate-revision`. | `@oh-my-claudecode:verifier check the central claim in sections/discussion.tex against sections/methods.tex and sections/results.tex; flag any over-claims` — purpose-built for internal-consistency audits. |
| Parallel section drafting from an outline | `/outline-expand outline.md --sections introduction,methods,results,discussion` — map-reduce with N parallel `@paper-writer` dispatches in one Agent-tool message. | `/outline-expand` then `/oh-my-claudecode:ultraqa "/iterate-revision per section" --strategies "concise,detailed"` — draft in parallel, then explore styles per section. |
| Figure backlog burndown (5+ figures) | Sequential `/figure-bake fig-1`, `/figure-bake fig-2`, … (engines are leaves; no built-in fan-out). | `/oh-my-claudecode:ultrawork "for each id in [fig-1, fig-2, fig-3, fig-5]: /figure-bake <id> --max-iter 3"` — parallel burndown of independent figures. |
| Autonomous full-paper drive (greenfield → submission) | `/supervisor-drive --auto --max-iter 8 --budget-tokens 100000` — domain-aware ranker over the 5 state files, 6 safety gates. | `/oh-my-claudecode:autopilot "drive paper.json to submission_ready"` wrapping `/supervisor-drive --auto`, plus `--decision-log .omc/decisions.jsonl` for structured observability. |
| Long-running drive (week+, must survive session restart) | `/supervisor-drive --auto` halts when the session ends. | `omc team 1:supervisor "run /supervisor-drive --auto --budget-tokens 200000 to submission_ready"` — tmux pane keeps the drive alive across session restarts. |
| Reviewer-letter rebuttal | `/respond-reviewer reviews/r1-comments.md` — classifies, dispatches per-comment, assembles `rebuttal-letter.tex`. | `/oh-my-claudecode:ralph "/respond-reviewer reviews/r1-comments.md" --verifier "@oh-my-claudecode:verifier check rebuttal claims match manuscript"` — keeps iterating until the verifier confirms no over-claims. |
| Stuck-project triage (just back from conference) | `/sync` then `/todofig` to surface state drift + figure-deck gaps. | `/sync` then `/oh-my-claudecode:ralplan "given /sync output, what are the top 3 actions to reach submission_ready?"` — consensus replanner over the reconciled state. |
| Greenfield vague idea → first paper draft | `/start-research` (interview) then `/supervisor-drive --auto`. | `/oh-my-claudecode:deep-interview "<vague idea>"` → `/start-research` → `/oh-my-claudecode:autopilot --inner-engine /supervisor-drive --max-budget 100000`. Best-of-breed at each phase. |
| Diagnose a stuck `/iterate-revision` (looped 3× → HALT) | `@supervisor` reads `_run-log.jsonl` + `reviews.json` and summarizes. | `@oh-my-claudecode:tracer` instruments the next run with per-phase timing + dispatched-brief diffs; `@oh-my-claudecode:verifier` independently checks reviewer's "major" issues. |

### Reading the matrix

A few patterns recur:

- **"OMCR alone" is the right column for any in-session focused task** — single section, ≤20 papers, single figure, one rebuttal. OMCR engines are designed to do one thing well and exit. No OMC is needed; reach for it only when you cross one of the limits below.
- **"OMCR + OMC" earns its keep when** (a) you want a second opinion (`/ralph`, `@verifier`), (b) you want parallel/distributed work (`omc team`, `/ultrawork`), (c) you want multi-strategy exploration (`/ultraqa`), or (d) you want long-running budget-tracked drives (`/autopilot` wrapping `/supervisor-drive`).
- **One thing only OMC can do**: cross-session persistence. OMCR engines die with their Claude Code session. For week-long projects, OMC's tmux-backed `omc team` is the only viable runtime.
- **One thing only OMCR can do**: domain-aware bottleneck ranking. OMC's `/autopilot` doesn't know `paper.json` exists. `/supervisor-drive` does and uses its 8 hardcoded priority rules to pick the next engine. Pair them via "OMC wraps OMCR".

---

## B — decision tree

This walks you from the question to a concrete command. Read top-down; first branch that fits is the answer.

```
Q1: Is the task bounded by a single OMCR engine?
│
├── YES — one engine + one target is enough
│    │
│    ├── Q2a: Interactive (you'll watch each iter)?
│    │        → run the engine directly:
│    │          /iterate-revision sections/<x>.tex
│    │          /figure-bake <fig-id>
│    │          /literature-sweep "<topic>"
│    │          /respond-reviewer reviews/<letter>
│    │          /outline-expand outline.md
│    │
│    └── Q2b: Autonomous (walk away, come back to result)?
│             │
│             ├── Want to retry the same engine until verifier DONE?
│             │    → OMC /ralph wrapping the engine:
│             │      /oh-my-claudecode:ralph "/iterate-revision sections/x.tex" \
│             │        --max-iter 5 --verifier "@oh-my-claudecode:verifier"
│             │
│             ├── Want N independent strategies, pick best?
│             │    → OMC /ultraqa with --strategies:
│             │      /oh-my-claudecode:ultraqa "/iterate-revision sections/x.tex" \
│             │        --strategies "concise,detailed,narrative" \
│             │        --selector reviewer-rating
│             │
│             └── Want parallel burndown of independent items?
│                  → OMC /ultrawork with the engine:
│                    /oh-my-claudecode:ultrawork \
│                      "bake fig-1, fig-2, fig-3, fig-5 in parallel via /figure-bake"
│
└── NO — task crosses multiple engines, or you're not sure where to start
     │
     ├── Q3a: You have a state file (paper.json) and want auto-progress?
     │        → /supervisor-drive (default = --interactive, asks every step)
     │          /supervisor-drive --auto         (autonomous, bounded by --max-iter/--budget-tokens)
     │          /supervisor-drive --plan-only    (preview only, no dispatch)
     │
     ├── Q3b: Long-running (days), must survive session restart?
     │        → omc team 1:supervisor "run /supervisor-drive --auto --budget-tokens <N>"
     │          NOT bare /supervisor-drive — it dies with the session.
     │
     ├── Q3c: Greenfield, no paper.json yet, vague idea?
     │        → /oh-my-claudecode:deep-interview "<idea>"
     │          then /start-research          (lay down OMCR scaffold)
     │          then /supervisor-drive --auto (drive to first draft)
     │          optionally wrap in /oh-my-claudecode:autopilot for budget tracking
     │
     ├── Q3d: Stuck, don't know what's blocking submission?
     │        → /sync                                                 (reconcile state)
     │          /todofig                                              (deck-vs-outline gap)
     │          /oh-my-claudecode:ralplan "what to do next?"          (consensus replan)
     │
     └── Q3e: Suspicious of a verdict your own reviewer gave?
              → @oh-my-claudecode:verifier check <claim> against <evidence sources>
                (independent verdict, not bound by @reviewer's MEMORY.md)
```

Quick disambiguators when more than one branch fits:

- "I want it bounded and predictable" → OMCR direct or `/supervisor-drive`.
- "I want it stubborn (retry until it works)" → OMC `/ralph`.
- "I want it parallel" → OMC `/team` (across sessions), `omc team` (cross-process tmux), `/ultrawork` (in-session burst).
- "I want it explorative (try several ideas)" → OMC `/ultraqa`, `/autopilot`.
- "I want a second opinion" → OMC `@verifier`, `@tracer`.

---

## C — cost & complexity table

This table compares 6 OMCR engines plus 4 key OMC skills on three axes: a typical-run token estimate, the setup cost you have to pay once before the tool is usable, and the situation where it earns its keep. The OMCR estimates are from each engine's `cost_estimate_tokens` frontmatter (see [Orchestration-Model § cost model](Orchestration-Model.md#cost-model--post-hoc-only)); OMC estimates are from upstream guidance — they can run an order of magnitude higher than OMCR.

| Tool | Typical token cost | Setup complexity | When to reach for it |
|---|---|---|---|
| OMCR `/iterate-revision` | ~24k tokens (1 section, 3 iters) | none — works out of the box | Single section to revise. The smallest viable loop. |
| OMCR `/literature-sweep` | ~50k tokens (20 papers, basic depth, sequential) | needs CrossRef/OpenAlex reachable (no auth) + a writable `references.bib` | Topic-anchored bibliography build. Honors hard verify-gate. |
| OMCR `/respond-reviewer` | ~60k tokens (10-comment letter, ~7 dispatches) | needs `manuscript_root` set (or pass `--manuscript`) | Reviewer-letter rebuttal. Classify-and-dispatch per comment. |
| OMCR `/figure-bake` | ~45k tokens (1 figure, 3 iters, 3 agents per iter) | needs `data_root` resolvable + Python/matplotlib in env | One figure from concept to manuscript-grade PDF + outline-grade PNG. |
| OMCR `/outline-expand` | ~40k tokens (5 sections, ~8k each, single parallel dispatch) | needs an outline file + `paper.json` | First-draft expansion of an outline. Map-reduce, no loop. |
| OMCR `/supervisor-drive` | ~80k tokens / drive (4–8 engine invocations) | needs all 5 OMCR state files initialized (`/omcr-setup` + `/start-research`) | Autonomous orchestration over the whole paper. 6 safety gates. |
| OMC `/ralph` | high (engine cost × outer-loop iters) | requires OMC install (`/plugin install oh-my-claudecode` or `npm i -g oh-my-claude-sisyphus`) | Stubborn task needing retries until an independent verifier confirms DONE. |
| OMC `/team` (or `omc team`) | very high (N parallel workers × per-worker cost) | requires OMC install + tmux (for `omc team` CLI variant) | True parallel multi-agent work; tmux variant survives session restart. |
| OMC `/autopilot` | extreme (multi-stage exec with budget tracking) | requires OMC install + `--max-budget` or accept default | Greenfield exploration; wraps OMCR engines for cross-validated drives. |
| OMC `/ultraqa` | very high (N strategies × per-strategy cost) | requires OMC install | Multi-strategy "try N approaches and pick best" exploration. |

Some practical notes:

- **OMCR's `cost_estimate_tokens` is a coarse upper bound for `/supervisor-drive`'s budget gate.** The supervisor uses rolling-median actuals from `_run-log.jsonl` once N ≥ 5 same-engine runs exist; the frontmatter constant only matters for cold-start (Phase 3 §6). Real costs converge as you accumulate runs.
- **OMC-side estimates run an order of magnitude higher than OMCR.** A `/ralph` wrapping `/iterate-revision` is not "24k tokens" — it is "24k × (outer-retry count)" plus the verifier's own dispatches. Plan accordingly.
- **Setup complexity is once-per-project for OMCR, once-per-machine for OMC.** OMCR's setup is `/omcr-setup` (no questions) plus `/start-research` (interview). OMC's setup is `/plugin install oh-my-claudecode` plus `omc setup` plus optional MCP / tmux configuration depending on which features you intend to use.

---

## D — architectural invariants

Four one-liners explain why the matrix above is legal and what cannot be made to compose:

### 1. OMC orchestrates execution; OMCR orchestrates research workflow.

OMC's primitives (`ralph`, `team`, `autopilot`, `ultraqa`, `ultrawork`) are domain-neutral: they sequence tool calls, retry on verifier failure, parallelize across workers, explore multiple strategies. OMC does not know what `paper.json` is, what a reviewer comment looks like, or why a figure has both an outline-grade PNG and a manuscript-grade PDF. OMCR's engines (`/iterate-revision`, `/literature-sweep`, …) embed exactly that domain knowledge — they know the 5 state files, the section status taxonomy (`empty → drafted → revising → approved`), the BibTeX schema, the figure status triad (brief / impl / critique), and the 8-rule priority ranker. The clean line: OMC executes, OMCR knows what to execute.

### 2. OMCR engines are leaves — no engine-calls-engine.

A hard architectural rule from Phase 2 decision §5 and Phase 3 decision §3. `/iterate-revision` does not call `/literature-sweep`. `/figure-bake` does not call `/respond-reviewer`. The five Phase 1 / Phase 2 engines never invoke each other. Only `/supervisor-drive` may chain engines, and even it does so by **re-evaluating state between every step** — never by dispatching one engine from inside another's plan. This keeps each engine auditable from one place and makes `_run-log.jsonl` a flat sequence of records (no nested call stacks). See [Orchestration Model § Engines are leaves](Orchestration-Model.md#engines-are-leaves--no-engine-to-engine-calls).

### 3. OMC's `/autopilot` wraps OMCR's `/supervisor-drive` for cross-validated runs.

The recommended pattern when you want both OMCR's domain-aware ranker and OMC's budget tracking + structured decision logs. The composition is: outer `/autopilot` invocation, inner `/supervisor-drive --auto`, OMC's safety mechanisms (max-budget, decision-log, recovery) wrap OMCR's safety mechanisms (6 gates, single-target, halt-on-exception). Each layer's halts compose: an OMCR gate trip inside the supervisor surfaces back to autopilot as a paused engine; autopilot's budget cap fires before the next engine launches. See [Autonomous-Drive § Composability](Autonomous-Drive.md#composability-with-omcs-autopilot-and-ralph) for the recipe and [Recipe 4](With-OMC.md#recipe-4--autonomous-paper-drive-with-kill-switch) for the exact command.

### 4. The cost contract is post-hoc + pre-flight bracketed.

OMCR's orchestrate `loop` primitive records `tokens_used` **after** each iteration and halts at the iteration boundary if `budget_tokens` is exceeded (Phase 0 §6). `/supervisor-drive` adds **pre-dispatch** estimation on top using a rolling-median × 1.25 over the engine's last 5 actuals (Phase 3 §6). OMC adds its own outer-loop budget tracking when wrapping (e.g., `--max-budget` on `/autopilot`). Three layers — pre-flight estimate, in-loop post-hoc cap, outer-loop hard ceiling — protect against the most common autonomous-mode failure mode (silent runaway cost). No single layer alone is enough; the bracketing is the contract.

---

## See also

- [Orchestration Model](Orchestration-Model.md) — state store, 4 primitives, engines-are-leaves invariant.
- [Autonomous Drive](Autonomous-Drive.md) — `/supervisor-drive` deep dive (modes, gates, ranker, cost model).
- [With OMC](With-OMC.md) — companion install + 5 worked recipes pairing OMCR engines with OMC skills.
- [OMC Tool Reference](OMC-Tool-Reference.md) — 47 MCP tools mapped to research stages, plus the inverse-map of OMC tools per OMCR engine.
- [Commands](Commands.md) — `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` reference.
- [Standalone Usage](Standalone-Usage.md) — OMCR without OMC.
- `develop/decisions-summary.md` — all 21 locked orchestration decisions across Phase 0–3, plus user ACKs.
- `develop/phase-4-omc-integration.md` — the Phase 4 spec backing this page.
