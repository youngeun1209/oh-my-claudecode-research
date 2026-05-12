# oh-my-claudecode-research — Wiki

A small Claude Code plugin that ships a **6-agent research team** + **4 lightweight hooks** + **4 parameterized commands** + **3 skills**, all tailored for producing research papers (or any structured-figure-and-outline document).

This wiki is the documentation deep dive. The [README](../README.md) is the quick overview.

## Navigation

### Getting started
- **[Getting Started](Getting-Started.md)** — Install, first session, common pitfalls
- **[Configuration](Configuration.md)** — The `## Research stack` block in your project's CLAUDE.md
- **[Standalone Usage](Standalone-Usage.md)** — Using OMCR alone (no OMC required)
- **[With OMC](With-OMC.md)** — Installing OMC alongside for richer features

### Reference
- **[Agents](Agents.md)** — The 6 core agents (supervisor / analysis-implementer / paper-writer / figure-descriptor / reviewer / literature-curator)
- **[Commands](Commands.md)** — `/omcr-setup`, `/start-research`, `/todofig`, `/sync`, plus the `cropfig`, `verify-citation`, and `manuscript-scaffold` skills
- **[Hooks](Hooks.md)** — `pii-scrub`, `memory-load`, `citation-warn`
- **[OMC Tool Reference](OMC-Tool-Reference.md)** — 47 OMC MCP tools mapped to research workflow stages

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

OMCR is a **research-team persona pack**. It does not orchestrate analyses, run code, or call MCPs. It ships agent prompts and conventions that, when loaded into Claude Code, give you 6 specialists you can `@`-mention:

- `@supervisor` — PI-level vision keeper + project orchestrator
- `@analysis-implementer` — analysis pipeline implementer (field-neutral; overlay a preset for domain flavor)
- `@paper-writer` — manuscript drafting & revision at high-impact-venue prose quality
- `@figure-descriptor` — figure design briefs (no images, just implementation-ready specs)
- `@reviewer` — adversarial pre-submission review at the target venue's level
- `@literature-curator` — BibTeX + summary-table owner; resolves `[CITE: ...]` placeholders and verifies every citation against CrossRef/OpenAlex

Plus the harness:
- 4 hooks (PII guard, MEMORY auto-load, citation warning, setup nudge)
- 4 slash commands (`/omcr-setup` installs OMCR infrastructure; `/start-research` runs the interview-driven first-project init; `/todofig` and `/sync` cover figure-deck-vs-outline workflows)
- 3 skills (`cropfig` strips caption bands from exported figure PNGs; `verify-citation` gates every citation added to the bibliography; `manuscript-scaffold` lays down the LaTeX skeleton + optional journal template + optional Overleaf clone)

## What OMCR is NOT

- Not an orchestration framework. For that, see [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) (the parent project this one builds on).
- Not a runtime. No MCP server, no Node bridge, no build chain. Just markdown + shell.
- Not a forked / vendored version of OMC. OMCR works alone or alongside OMC — your choice. See [With-OMC](With-OMC.md) for the companion setup.

## Versions

This wiki tracks `v0.1.x`. Breaking changes between minor versions are likely until `v1.0`. Each page notes the version it applies to at the top if behavior has changed.

## Where to file issues / contribute

GitHub issues + PRs on the main repo. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution contract (frontmatter / MEMORY schema / PII / commit conventions).
