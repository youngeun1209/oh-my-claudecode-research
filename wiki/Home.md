# oh-my-claudecode-research — Wiki

A Claude Code plugin that ships a **6-agent research team** + **13 slash commands** (7 setup/workflow/utility + 6 orchestration engines) + **18 skills** (1 primitive + 17 backing surfaces) + **4 lightweight hooks**, all tailored for producing research papers (or any structured-figure-and-outline document).

This wiki is the documentation deep dive. The [README](../README.md) is the quick overview.

## Navigation

### Getting started
- **[Getting Started](Getting-Started.md)** — Install, first session, common pitfalls
- **[Configuration](Configuration.md)** — The `## Research stack` block in your project's CLAUDE.md
- **[Standalone Usage](Standalone-Usage.md)** — Using OMCR alone (no OMC required)
- **[Using Orchestration](Using-Orchestration.md)** — how to use the 6 engines (Level 1/2/3 walkthrough)
- **[With OMC](With-OMC.md)** — Installing OMC alongside for richer features

### Reference
- **[Agents](Agents.md)** — The 6 core agents (supervisor / analysis-implementer / paper-writer / figure-descriptor / reviewer / literature-curator)
- **[Commands](Commands.md)** — all 13 slash commands (7 setup/workflow/utility + 6 orchestration engines) and the standalone skills
- **[Reading Library](Reading-Library.md)** — `paper-ingest`: file papers you read into a two-folder library (separate from the manuscript BibTeX)
- **[Hooks](Hooks.md)** — `pii-scrub`, `memory-load`, `citation-warn`, `setup-nudge`
- **[OMC Tool Reference](OMC-Tool-Reference.md)** — 47 OMC MCP tools mapped to research workflow stages
- **[Orchestration Comparison](Orchestration-Comparison.md)** — composition matrix: OMCR alone vs OMCR + OMC, decision tree, cost & complexity table
- **[Autonomous Drive](Autonomous-Drive.md)** — `/supervisor-drive` deep dive (modes, safety gates, priority ranker, cost model)

### Extending
- **[Specializing for Your Field](Specializing.md)** — How to author a field-specific preset (neuro-fmri, wet-lab, ML research, …)

## Quick decision tree

```
Are you writing a paper / structured outline doc with figures?
└── Yes
    │
    ├── Standalone (no OMC, minimal install) → see Standalone Usage
    │
    └── Want the full stack (OMC's wiki / python_repl / state machine / verifier / tracer)?
        └── See With-OMC for the companion install
```

## What OMCR is

OMCR is a **research-workflow orchestration plugin**. It coordinates a 6-specialist research team through the paper-writing lifecycle — from hypothesis interview to manuscript scaffold to figure-deck-vs-outline reconciliation. It does not bundle an execution runtime (no MCP server, no parallel/consensus engines); for those, pair with OMC. When loaded into Claude Code, you get 6 specialists you can `@`-mention:

- `@supervisor` — PI-level vision keeper + project orchestrator
- `@analysis-implementer` — analysis pipeline implementer (field-neutral; overlay a preset for domain flavor)
- `@paper-writer` — manuscript drafting & revision at high-impact-venue prose quality
- `@figure-descriptor` — figure design briefs (no images, just implementation-ready specs)
- `@reviewer` — adversarial pre-submission review at the target venue's level
- `@literature-curator` — BibTeX + summary-table owner; resolves `[CITE: ...]` placeholders and verifies every citation against CrossRef/OpenAlex

Plus the wiring:
- 4 hooks (PII guard, MEMORY auto-load, citation warning, setup nudge)
- 13 slash commands: 7 setup/workflow/utility (`/omcr-setup` installs infra; `/start-research` is the interview; `/todofig` and `/sync` cover figure-deck-vs-outline; `/session-start` orients read-only; `/save-session-log` journals a session; `/update-version` propagates artifact version bumps) + 6 orchestration engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` — see [Using-Orchestration](Using-Orchestration.md))
- 18 skills: the setup/workflow/utility commands are backed by matching skills; `cropfig` strips caption bands; `verify-citation` gates every citation; `manuscript-scaffold` lays down the LaTeX skeleton; `paper-ingest` files papers you read into a two-folder [Reading Library](Reading-Library.md). Plus 1 primitive (`orchestrate`) + 6 engine skills (`iterate-revision`, `literature-sweep`, `respond-reviewer`, `figure-bake`, `outline-expand`, `supervisor-drive`)

## What OMCR is NOT

- Not a runtime execution engine. OMCR orchestrates the *research workflow* (which specialist handles which stage of a paper, via `@supervisor` delegation and the `/start-research` → `/todofig` → `/sync` pipeline), but it does not ship parallel/consensus/loop execution engines like OMC's `ralph`, `team`, `autopilot`, `ultrawork`. For those, install [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) alongside — OMCR is designed to compose with OMC, not replace it.
- Not a runtime in the OMC sense. No MCP server, no Node bridge, no build chain. Just markdown + shell.
- Not a forked / vendored version of OMC. OMCR works alone or alongside OMC — your choice. See [With-OMC](With-OMC.md) for the companion setup.

## Versions

This wiki tracks `v0.1.x`. Breaking changes between minor versions are likely until `v1.0`. Each page notes the version it applies to at the top if behavior has changed.

## Where to file issues / contribute

GitHub issues + PRs on the main repo. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution contract (frontmatter / MEMORY schema / PII / commit conventions).
