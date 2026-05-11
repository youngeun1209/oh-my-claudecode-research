# oh-my-claudecode-research

A Claude Code plugin that ships a **5-agent research team** + **2 parameterized commands** + **1 figure-cropping skill** + **3 lightweight hooks**, all tailored for producing research papers (or any structured-figure-and-outline document).

This is the **research companion** to upstream [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode), not a fork. OMCR works standalone or alongside OMC — see [`wiki/With-OMC.md`](wiki/With-OMC.md) for the companion setup.

> **Status: v0.1.** Breaking changes are likely. Feedback and PRs welcome.

> **Full documentation:** [`wiki/Home.md`](wiki/Home.md)

## What you get

### 5 agents (`@`-mention)

| Agent | Role |
|---|---|
| `@supervisor` | PI-level scientific vision keeper + project orchestrator. Owns the central hypothesis; delegates to subagents. |
| `@analysis-implementer` | Implements pipelines, statistical analyses, ML/sim models. Field-neutral by default. |
| `@paper-writer` | Drafts manuscript sections at high-impact-venue prose quality. |
| `@figure-descriptor` | Designs figures as implementation-ready briefs — no image generation. |
| `@reviewer` | Adversarial pre-submission review at the target venue's level. |

### 2 slash commands (parameterized via your project's CLAUDE.md)

| Command | What it does |
|---|---|
| `/todofig [Fig N]` | Compare a captured figure deck against an outline → prioritized P0/P1/P2 TODO. |
| `/sync` | Reconcile current state (deck) with goal (outline), refresh agent memories, optionally embed cropped figures into a target document. Status snapshot, not a TODO. |

### 1 skill

| Skill | What it does |
|---|---|
| `cropfig` | Tight-crop captioned figure PNGs to figure-only content. Used by `/sync` Phase 4 for `.docx` embedding without caption duplication. |

### 3 hooks

| Hook | Event | Behavior |
|---|---|---|
| `pii-scrub` | `PreToolUse:Write\|Edit` | Blocks writes containing PII (emails / SSNs / subject IDs by default; configurable). |
| `memory-load` | `SessionStart` | Auto-injects `.claude/agent-memory/*/MEMORY.md` into session context. |
| `citation-warn` | `PostToolUse:Write\|Edit` | Heuristic non-blocking warning when manuscript markdown has uncited paragraphs. |

## Install

**Recommended — Claude Code plugin:**

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Then in any project, open Claude Code and run `/plugin` to load it. After load:
- 5 agents appear in the `@`-mention picker
- `/todofig`, `/sync` appear in the slash-command picker
- 3 hooks register on session start

**Cherry-pick by file** (no plugin manager — copy agents into a specific project):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

This skips the commands, the skill, and the hooks. For full feature parity, use the plugin install.

## Quick start

After installing, open a research project and:

```
@supervisor where are we?
```

Supervisor reads the project's `CLAUDE.md` (and any `agent-memory/supervisor/MEMORY.md`) and orients you on status + next action. If `CLAUDE.md` is missing key fields (hypothesis / target venue / field), supervisor asks before assuming.

For the slash commands, add a `## Research stack` block to your `CLAUDE.md`:

```markdown
## Research stack (used by /todofig, /sync, /cropfig)

- **Deck export dir:** figures/captured/
- **Outline file:** outline.md
- **Figure count:** 8
- **Result pattern:** `^### Result (\d+)`
- **Report language:** English
- **Report output dir:** ./todofig_reports/
- **Sync report dir:** ./sync_reports/
```

Or just run `/todofig` once and it'll prompt for these fields, then offer to persist them automatically.

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

- **[`examples/neuro-fmri/`](examples/neuro-fmri/)** — Mapper-on-fMRI specialization. Provides a neuro-flavored `analysis-implementer` body + redacted MEMORY.md skeletons for all 5 agents.

Quick overlay:

```bash
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# In your project:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer; do
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
| `@document-specialist` agent | Literature research with citation verification (Context Hub). Fills our literature-anchoring gap. |
| `@verifier` agent | Evidence-based completion checks — rejects "should work" claims without fresh test output. |
| `@tracer` agent + `/oh-my-claudecode:trace` | Evidence-driven competing-hypotheses ranking with disconfirmation. Maps to methods/results validation. |
| `@writer` agent | Technical-documentation writer for lab protocols, methods appendices, reproducibility guides. |
| `@test-engineer` agent | TDD-discipline for analysis-script edge case coverage. |
| `@git-master` agent | Atomic-commit discipline — independently revertable analysis steps. |
| `/oh-my-claudecode:autoresearch` skill | Bounded evaluator-driven iteration loop with per-iteration JSON + decision logs. |
| `/oh-my-claudecode:deep-interview` skill | Socratic clarification of vague research goals into testable hypotheses. |
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
