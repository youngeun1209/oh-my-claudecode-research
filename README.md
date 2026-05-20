English | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [Türkçe](README.tr.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md)

# oh-my-claudecode-research

**Multi-agent orchestration for Claude Code — the research edition. Zero learning curve.**

_Don't learn research tooling. Just use OMCR._

OMCR is a research workspace for Claude Code: six agents — `@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator` — you work alongside on hypothesis, analysis, writing, figures, citations, review. Six orchestration engines automate the common loops when you want it hands-off. Compose with [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) for generic orchestration on top (retries, parallelism, budget tracking).

A 6-agent research team + 6 orchestration engines + 4 setup/workflow commands + 14 skills + 4 lightweight hooks.

> **Status: v0.1.** Breaking changes are likely. Feedback and PRs welcome.

> **Full documentation:** [`wiki/Home.md`](wiki/Home.md)

## Quick start

**Step 0: Install OMC (optional, highly recommended)**

Not required, but highly recommended. OMCR works standalone, but pairing it with [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) unlocks generic orchestration.

Marketplace flow — open Claude Code in your terminal (`claude`), then enter these slash commands one at a time inside the session:

```
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
```

Then:

```
/plugin install oh-my-claudecode
```

Or **directly in your shell** (no Claude Code session needed) via npm:

```bash
npm i -g oh-my-claude-sisyphus@latest
```

Full mapping: [`wiki/With-OMC.md`](wiki/With-OMC.md).

**Step 1: Install**

**If you're installing OMCR for the first time** — marketplace flow (recommended). Open Claude Code in your terminal (`claude`), then enter these slash commands one at a time inside the session:

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

Then:

```
/plugin install oh-my-claudecode-research
```

**If you prefer manual checkout** (no plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

**If OMCR is already installed and you want to update it** — run these two slash commands one at a time:

```
/plugin marketplace update omcr
```

Then:

```
/plugin update oh-my-claudecode-research
```

The first refreshes marketplace metadata; the second actually pulls the new plugin files. OMCR tracks `main`, so every new commit is treated as a new version. Your project state (CLAUDE.md, agent memory, settings) is not touched — no need to re-run Step 2.

**Step 2: Setup**

**Only needed once per project.** Inside a Claude Code session in your research project, run these slash commands **one at a time**:

```
/omcr-setup
```

Then:

```
/start-research
```

`/omcr-setup` lays down infrastructure — empty `## Project context` / `## Research stack` / `## Language preference` blocks in `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` for all 6 agents, empty `paper/references.bib` + `./references.csv` for the literature-curator, and a curated `.claude/settings.json` permission allowlist. **No questions about your research.**

`/start-research` is the interview. It walks you through filling those placeholders:

- **Project context** (working title, field, target venue, central hypothesis, research topic, datasets, narrative spine)
- **Research stack** (deck/outline paths, figure count, BibTeX + summary-table paths, optional CrossRef email)
- **Preset overlay** (optional — `examples/neuro-fmri/` etc. — only replaces agent `MEMORY.md` files still byte-identical to the canonical template)
- **Manuscript scaffold** (delegates to the `manuscript-scaffold` skill: LaTeX skeleton + journal template lookup + optional Overleaf clone)

If you run `/start-research` before `/omcr-setup`, it offers to run `/omcr-setup` first. Skipped scientific fields are saved as `[TBD: <short note>]` — never invented — so `@supervisor` knows to follow up. If you skip both, the SessionStart `setup-nudge` hook prints a one-line reminder every session until you initialize (suppress with `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`).

**Step 3: Start working**

```
@supervisor where are we?
```

Full walkthrough: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

## What you get

### 6 agents (`@`-mention)

| Agent                     | Role                                                                                                                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `@supervisor`           | PI-level scientific vision keeper + project orchestrator. Owns the central hypothesis; delegates to subagents.                                                                 |
| `@analysis-implementer` | Implements pipelines, statistical analyses, ML/sim models. Field-neutral by default.                                                                                           |
| `@paper-writer`         | Drafts manuscript sections at high-impact-venue prose quality.                                                                                                                 |
| `@figure-descriptor`    | Designs figures as implementation-ready briefs — no image generation.                                                                                                         |
| `@reviewer`             | Adversarial pre-submission review at the target venue's level.                                                                                                                 |
| `@literature-curator`   | Owns the project BibTeX + literature summary table in lockstep. Resolves `[CITE: ...]` placeholders, verifies citations via the `verify-citation` skill, never fabricates. |

### 4 slash commands (parameterized via your project's CLAUDE.md)

| Command                                  | What it does                                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/omcr-setup`                          | Install-style: scaffold empty `CLAUDE.md` marker blocks, `.claude/agent-memory/` dirs, empty `references.bib`/`references.csv`, and a curated `.claude/settings.json` permission allowlist. **No questions about your research.** Run this once per project.                                                                        |
| `/start-research [minimal\|neuro-fmri]` | Interview-driven: fill the `CLAUDE.md` placeholders (working title, hypothesis, target venue, datasets, narrative spine), optionally apply a preset to agent memory, scaffold the LaTeX manuscript dir (via the `manuscript-scaffold` skill, with optional journal template + Overleaf clone). Offers to run `/omcr-setup` first if not done. |
| `/todofig [Fig N]`                     | Compare a captured figure deck against an outline → prioritized P0/P1/P2 TODO.                                                                                                                                                                                                                                                                     |
| `/sync`                                | Reconcile current state (deck) with goal (outline), refresh agent memories, optionally embed cropped figures into a target document. Status snapshot, not a TODO.                                                                                                                                                                                   |

### 14 skills

The 4 setup/workflow slash commands are thin dispatchers — each forwards `$ARGUMENTS` to a matching skill. `cropfig`, `verify-citation`, `manuscript-scaffold` are standalone-invocable. **Plus** 1 primitive (`orchestrate` — internal, composes via 4 phases) + 6 engine skills backing the 6 orchestration commands; full walkthrough at [`wiki/Using-Orchestration.md`](wiki/Using-Orchestration.md). The table below covers the 7 setup/workflow skills.

| Skill                   | What it does                                                                                                                                                                                                                                                                                                                                         |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `omcr-setup`          | Backs `/omcr-setup`. Install-style: scaffold `CLAUDE.md` marker blocks, agent-memory dirs, bibliography files, curated permission allowlist.                                                                                                                                                                                                     |
| `start-research`      | Backs `/start-research`. Interview-driven first-project init: fills the scaffolded `CLAUDE.md` placeholders, optionally applies a preset overlay, delegates manuscript scaffold to `manuscript-scaffold`.                                                                                                                                      |
| `sync`                | Backs `/sync`. Reconcile current state (captured figure deck) with the outline; refresh agent memories with factual drifts; status snapshot only (no TODO).                                                                                                                                                                                        |
| `todofig`             | Backs `/todofig`. Compare a captured figure deck against the outline; produce a prioritized P0/P1/P2 TODO of gaps.                                                                                                                                                                                                                                 |
| `cropfig`             | Three-step pipeline from a `.key`/`.pptx` deck to manuscript + outline artifacts: per-slide vector PDFs (cropped, manuscript-grade) + outline-grade PNGs. Invoked directly or by other commands; no slash.                                                                                                                                       |
| `verify-citation`     | Existence + metadata check via CrossRef/OpenAlex. Gates every entry `@literature-curator` adds, writes verification verdict into the project summary table.                                                                                                                                                                                        |
| `manuscript-scaffold` | Copy the bundled LaTeX skeleton into the user's manuscript dir, optionally apply a journal-specific `\documentclass` from the bundled registry, optionally clone an Overleaf project (token never persisted to tracked files), commit on the default branch, ask before pushing. Called by `/start-research` phase 6; also standalone-invocable. |

### 4 hooks

| Hook              | Event                      | Behavior                                                                                                                                                        |
| ----------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pii-scrub`     | `PreToolUse:Write\|Edit`  | Blocks writes containing PII (emails / SSNs / subject IDs by default; configurable).                                                                            |
| `memory-load`   | `SessionStart`           | Auto-injects `.claude/agent-memory/*/MEMORY.md` into session context.                                                                                         |
| `citation-warn` | `PostToolUse:Write\|Edit` | Heuristic non-blocking warning when manuscript markdown has uncited paragraphs.                                                                                 |
| `setup-nudge`   | `SessionStart`           | One-line non-blocking nudge to run `/omcr-setup` then `/start-research` if CLAUDE.md is missing the `## Project context` or `## Research stack` blocks. |

## Documentation

- **[Wiki home](wiki/Home.md)** — navigation hub
- **[Getting Started](wiki/Getting-Started.md)** — install + first session
- **[Configuration](wiki/Configuration.md)** — Research stack block, env vars, PII patterns
- **[Standalone Usage](wiki/Standalone-Usage.md)** — using OMCR alone, full walkthrough
- **[With OMC](wiki/With-OMC.md)** — full stack: OMCR + OMC companion install
- **[Agents](wiki/Agents.md)** | **[Commands](wiki/Commands.md)** | **[Hooks](wiki/Hooks.md)** — references
- **[OMC Tool Reference](wiki/OMC-Tool-Reference.md)** — 47 OMC MCP tools mapped to research stages
- **[Specializing](wiki/Specializing.md)** — author a field-specific preset

## Specializing for your field

Core agents and commands are field-neutral. For domain-specific flavor (e.g., neuroscience methodology, wet-lab conventions, ML evaluation idioms), overlay a preset from `examples/<field>/`. Currently shipped:

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — generic neuro-fMRI specialization. Provides a neuro-flavored `analysis-implementer` body (preprocessing / parcellation / connectivity / ISC / spin tests) + redacted MEMORY.md skeletons for all 6 agents.

Quick overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer literature-curator; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md \
     .claude/agent-memory/$agent/MEMORY.md
done
```

To author your own preset: see [`wiki/Specializing.md`](wiki/Specializing.md). PRs adding new presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) welcome.

## OMC companion (recommended)

OMCR treats [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) as a *companion*, not a dependency. With OMC installed alongside, the following components fit naturally into research workflows. Pick the ones relevant to your project — you don't have to use all of them.

| Component                                                                                                     | Why for research                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@scientist` agent                                                                                          | Statistical-rigor enforcer (CIs / p-values / effect sizes /`[LIMITATION]` markers). Companion to `@analysis-implementer`.                                                                                                                                                      |
| `@document-specialist` agent                                                                                | Heavier-weight literature research backed by OMC's Context Hub (cached fetches, structured notes). Use alongside `@literature-curator` when a survey-scale dive is needed; OMCR's curator handles per-claim citation resolution and BibTeX/summary-table bookkeeping on its own. |
| `@verifier` agent                                                                                           | Evidence-based completion checks — rejects "should work" claims without fresh test output.                                                                                                                                                                                        |
| `@tracer` agent + `/oh-my-claudecode:trace`                                                               | Evidence-driven competing-hypotheses ranking with disconfirmation. Maps to methods/results validation.                                                                                                                                                                             |
| `@writer` agent                                                                                             | Technical-documentation writer for lab protocols, methods appendices, reproducibility guides.                                                                                                                                                                                      |
| `@test-engineer` agent                                                                                      | TDD-discipline for analysis-script edge case coverage.                                                                                                                                                                                                                             |
| `@git-master` agent                                                                                         | Atomic-commit discipline — independently revertable analysis steps.                                                                                                                                                                                                               |
| `/oh-my-claudecode:autoresearch` skill                                                                      | Bounded evaluator-driven iteration loop with per-iteration JSON + decision logs.                                                                                                                                                                                                   |
| `/oh-my-claudecode:deep-interview` skill                                                                    | Socratic clarification of vague research goals into testable hypotheses.                                                                                                                                                                                                           |
| OMC orchestration skills (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Multi-iteration / parallel / consensus orchestrators for analysis runs, literature scans, must-finish revisions. See[`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) for 5 worked recipes.                                      |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP tools                                          | Literature wiki / hypothesis register / experiment-run registry / stateful Python REPL.                                                                                                                                                                                            |

Install OMC alongside via the Claude Code marketplace, or `npm i -g oh-my-claude-sisyphus`. Full mapping: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md).

## Conventions (contributors)

- **kebab-case** filenames for agents, skills, commands
- **YAML frontmatter** required on every agent / skill / command (`name`, `description`, optional `model` / `color` / `memory`)
- **No PII** in `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, or top-level docs — institutions, advisors, real subject IDs, emails, target journal names, absolute paths. Domain-specific content lives only under `examples/<field>/`.
- **English-first** language directive on all agents (override-in-CLAUDE.md pattern)

Full contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
