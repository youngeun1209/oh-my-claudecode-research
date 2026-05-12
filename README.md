# oh-my-claudecode-research

A Claude Code plugin that ships a **6-agent research team** + **4 parameterized commands** + **3 skills** + **4 lightweight hooks**, all tailored for producing research papers (or any structured-figure-and-outline document).

This is the **research companion** to upstream [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode), not a fork. OMCR works standalone or alongside OMC — see [`wiki/With-OMC.md`](wiki/With-OMC.md) for the companion setup.

> **Status: v0.1.** Breaking changes are likely. Feedback and PRs welcome.

> **Full documentation:** [`wiki/Home.md`](wiki/Home.md)

## What you get

### 6 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI-level scientific vision keeper + project orchestrator. Owns the central hypothesis; delegates to subagents. |
| `@analysis-implementer` | Implements pipelines, statistical analyses, ML/sim models. Field-neutral by default. |
| `@paper-writer` | Drafts manuscript sections at high-impact-venue prose quality. |
| `@figure-descriptor` | Designs figures as implementation-ready briefs — no image generation. |
| `@reviewer` | Adversarial pre-submission review at the target venue's level. |
| `@literature-curator` | Owns the project BibTeX + literature summary table in lockstep. Resolves `[CITE: ...]` placeholders, verifies citations via the `verify-citation` skill, never fabricates. |

### 4 slash commands (parameterized via your project's CLAUDE.md)

| Command | What it does |
|---|---|
| `/omcr-setup` | Install-style: scaffold empty `CLAUDE.md` marker blocks, `.claude/agent-memory/` dirs, empty `references.bib`/`references.csv`, and a curated `.claude/settings.json` permission allowlist. **No questions about your research.** Run this once per project. |
| `/start-research [minimal\|neuro-fmri]` | Interview-driven: fill the `CLAUDE.md` placeholders (working title, hypothesis, target venue, datasets, narrative spine), optionally apply a preset to agent memory, scaffold the LaTeX manuscript dir (via the `manuscript-scaffold` skill, with optional journal template + Overleaf clone). Offers to run `/omcr-setup` first if not done. |
| `/todofig [Fig N]` | Compare a captured figure deck against an outline → prioritized P0/P1/P2 TODO. |
| `/sync` | Reconcile current state (deck) with goal (outline), refresh agent memories, optionally embed cropped figures into a target document. Status snapshot, not a TODO. |

### 3 skills

| Skill | What it does |
|---|---|
| `cropfig` | Three-step pipeline from a `.key`/`.pptx` deck to manuscript + outline artifacts: per-slide vector PDFs (cropped, manuscript-grade) + outline-grade PNGs. Invoked directly or by other commands; no slash. |
| `verify-citation` | Existence + metadata check via CrossRef/OpenAlex. Gates every entry `@literature-curator` adds, writes verification verdict into the project summary table. |
| `manuscript-scaffold` | Copy the bundled LaTeX skeleton into the user's manuscript dir, optionally apply a journal-specific `\documentclass` from the bundled registry, optionally clone an Overleaf project (token never persisted to tracked files), commit on the default branch, ask before pushing. Called by `/start-research` phase 5; also standalone-invocable. |

### 4 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Blocks writes containing PII (emails / SSNs / subject IDs by default; configurable). |
| `memory-load` | `SessionStart` | Auto-injects `.claude/agent-memory/*/MEMORY.md` into session context. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Heuristic non-blocking warning when manuscript markdown has uncited paragraphs. |
| `setup-nudge` | `SessionStart` | One-line non-blocking nudge to run `/omcr-setup` then `/start-research` if CLAUDE.md is missing the `## Project context` or `## Research stack` blocks. |

## Install

**Recommended — Claude Code marketplace flow** (one slash command per line, enter them one at a time):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Alternative — manual checkout** (no plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Then open Claude Code and run `/plugin` to load it. After load (either path):
- 6 agents appear in the `@`-mention picker
- `/omcr-setup`, `/start-research`, `/todofig`, `/sync` appear in the slash-command picker
- 3 skills (`cropfig`, `verify-citation`, `manuscript-scaffold`) become invocable
- 4 hooks register on session start (PII guard, MEMORY auto-load, citation warning, setup nudge)

**Cherry-pick by file** (no plugin manager — copy agents into a specific project):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

This skips the commands, the skill, and the hooks. For full feature parity, use the plugin install.

## Quick start

After installing, open a research project and run these in order:

```
/omcr-setup
/start-research
```

**`/omcr-setup`** is install-style — no questions about your research. It just lays down infrastructure: empty `## Project context` / `## Research stack` / `## Language preference` blocks in `CLAUDE.md`, `.claude/agent-memory/<agent>/MEMORY.md` for all 6 agents (canonical template), empty `paper/references.bib` + `./references.csv` for the literature-curator, and a curated `.claude/settings.json` permission allowlist (read-only git, file search, LaTeX build, citation API, figure crop — opt-in for Python analysis; git write and file deletion stay manual).

**`/start-research`** is the interview. It walks you through filling those placeholders:
- **Project context** (working title, field, target venue, central hypothesis, research topic, datasets, narrative spine)
- **Research stack** (deck/outline paths, figure count, BibTeX + summary-table paths, optional CrossRef email)
- **Preset overlay** (optional — `examples/neuro-fmri/` etc. — only replaces agent `MEMORY.md` files that are still byte-identical to the canonical template)
- **Manuscript scaffold** (delegates to the `manuscript-scaffold` skill: LaTeX skeleton + journal template lookup + optional Overleaf clone)

If you run `/start-research` before `/omcr-setup`, it offers to run `/omcr-setup` first. Skipped scientific fields are saved as `[TBD: <short note>]` — never invented — so `@supervisor` knows to follow up.

If you skip both, the SessionStart `setup-nudge` hook prints a one-line reminder every session until you initialize. Suppress with `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

After both, start a real conversation:

```
@supervisor where are we?
```

Full walkthrough: [`wiki/Getting-Started.md`](wiki/Getting-Started.md)

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

| Component | Why for research |
|---|---|
| `@scientist` agent | Statistical-rigor enforcer (CIs / p-values / effect sizes / `[LIMITATION]` markers). Companion to `@analysis-implementer`. |
| `@document-specialist` agent | Heavier-weight literature research backed by OMC's Context Hub (cached fetches, structured notes). Use alongside `@literature-curator` when a survey-scale dive is needed; OMCR's curator handles per-claim citation resolution and BibTeX/summary-table bookkeeping on its own. |
| `@verifier` agent | Evidence-based completion checks — rejects "should work" claims without fresh test output. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Evidence-driven competing-hypotheses ranking with disconfirmation. Maps to methods/results validation. |
| `@writer` agent | Technical-documentation writer for lab protocols, methods appendices, reproducibility guides. |
| `@test-engineer` agent | TDD-discipline for analysis-script edge case coverage. |
| `@git-master` agent | Atomic-commit discipline — independently revertable analysis steps. |
| `/oh-my-claudecode:autoresearch` skill | Bounded evaluator-driven iteration loop with per-iteration JSON + decision logs. |
| `/oh-my-claudecode:deep-interview` skill | Socratic clarification of vague research goals into testable hypotheses. |
| OMC orchestration skills (`ralph`, `team`, `autopilot`, `ralplan`, `ultraqa`, `autoresearch`, …) | Multi-iteration / parallel / consensus orchestrators for analysis runs, literature scans, must-finish revisions. See [`wiki/With-OMC.md#recipes--pairing-omcr-with-omc`](wiki/With-OMC.md#recipes--pairing-omcr-with-omc) for 4 worked recipes. |
| `wiki_*` / `notepad_*` / `state_*` / `python_repl` MCP tools | Literature wiki / hypothesis register / experiment-run registry / stateful Python REPL. |

Install OMC alongside via the Claude Code marketplace, or `npm i -g oh-my-claude-sisyphus`. Full mapping: [`wiki/With-OMC.md`](wiki/With-OMC.md) + [`wiki/OMC-Tool-Reference.md`](wiki/OMC-Tool-Reference.md).

## Conventions (contributors)

- **kebab-case** filenames for agents, skills, commands
- **YAML frontmatter** required on every agent / skill / command (`name`, `description`, optional `model` / `color` / `memory`)
- **No PII** in `agents/`, `commands/`, `skills/`, `templates/`, `hooks/`, or top-level docs — institutions, advisors, real subject IDs, emails, target journal names, absolute paths. Domain-specific content lives only under `examples/<field>/`.
- **English-first** language directive on all agents (override-in-CLAUDE.md pattern)

Full contract: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
