# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

v0.1.x of a Claude Code plugin that ships:
- 6 research-team agents (`agents/`)
- 4 parameterized slash commands (`commands/`)
- 5 skills (`skills/omcr-setup/`, `skills/start-research/`, `skills/cropfig/`, `skills/verify-citation/`, `skills/manuscript-scaffold/`)
- 4 lightweight hooks (`hooks/`)
- a canonical memory schema (`templates/MEMORY.template.md`)
- the plugin manifest (`.claude-plugin/plugin.json`)
- one worked example preset (`examples/neuro-fmri/` — neuro-flavored analysis-implementer body + redacted MEMORY.md skeletons)
- wiki documentation (`wiki/`) — 11 markdown pages, mirrors to GitHub Wiki via `wiki/README.md` instructions

MIT licensed (`LICENSE`, 2026 Young-Eun Lee). No build chain, no npm — plain markdown plus shell scripts loaded directly by Claude Code.

## Project intent

Public release on GitHub as the **research companion** to the upstream `oh-my-claudecode` project. The "research" framing means curated agents and conventions tailored to producing papers — not a runnable application. Treat additions through that lens; if a new asset is general-purpose orchestration, it likely belongs in upstream OMC instead.

## Conventions baked into the repo

- `.gitignore` excludes `.claude/` and `.omc/` — per-user / OMC plugin state stays local and must not be committed. If you create shared Claude Code assets (slash commands, agents, hooks) intended to ship with the repo, they need a different location or a targeted un-ignore, not a blanket removal of the rule.
- `.env` is gitignored — secrets stay out of the tree.

## External reference symlinks

The repo root holds symlinks to other local checkouts the maintainer wants accessible while working here:

- [`oh-my-claudecode/`](oh-my-claudecode/) → maintainer's checkout of the upstream `oh-my-claudecode` project. Source material this "research" repo is built around — read it for prior art, naming, structure, and "how does upstream do X" (`oh-my-claudecode/README.md`, `CLAUDE.md`, `AGENTS.md`).
- [`DoD-Agent/`](DoD-Agent/) → maintainer's checkout of a separate research project (`DoD-Agent`). Available as cross-reference; its own `CLAUDE.md` describes its scope. Don't assume content from `DoD-Agent` belongs in this repo unless the user says so.

Rules that apply to **all** symlinks in this section:

- Targets are **absolute paths on the maintainer's machine**, so each entry is gitignored individually and will not exist for other contributors or CI. Do not commit them, do not rewrite paths to make them portable, and do not assume they resolve anywhere except the maintainer's machine.
- Treat contents as **read-only reference**. Never edit files through these symlinks — writes would land in the external working tree, not this repo. If something from one of them should live here, copy the relevant excerpt into a tracked file under this repo.
- If a symlink is missing, ask the user to recreate it with `ln -s <absolute-path> <name>` rather than guessing at the external structure.
- When adding a new external symlink, follow this same pattern: create at repo root, add `/<name>` to `.gitignore`, list it in this section with a one-line purpose.

## File layout

```
oh-my-claudecode-research/
├── .claude-plugin/plugin.json        # plugin manifest (registers agents/commands/skills/hooks)
├── .gitattributes                    # LF line-ending normalization
├── agents/                           # 6 generic core agents (kebab-case, frontmatter required)
│   ├── supervisor.md
│   ├── analysis-implementer.md
│   ├── paper-writer.md
│   ├── figure-descriptor.md
│   ├── reviewer.md
│   └── literature-curator.md         # bibliography curator + BibTeX/summary-table owner
├── commands/                         # 4 parameterized slash commands (thin dispatchers)
│   ├── omcr-setup.md                 # /omcr-setup — install OMCR infra (CLAUDE.md markers, agent-memory, bib, permissions). No interview.
│   ├── start-research.md             # /start-research — interview-driven first-project init (fills CLAUDE.md, manuscript scaffold)
│   ├── todofig.md                    # /todofig — deck-vs-outline gap analyzer
│   └── sync.md                       # /sync — state reconciler + optional figure embed
├── skills/
│   ├── cropfig/                      # generic figure-only crop (env-var + CLAUDE.md driven)
│   │   ├── SKILL.md
│   │   └── crop_top_label.py
│   ├── manuscript-scaffold/          # state check / journal lookup / skeleton / commit-push — phase-split; called by /start-research phase 5, also standalone
│   │   ├── SKILL.md
│   │   └── phases/
│   │       ├── 01-state-check.md
│   │       ├── 02-journal-template.md
│   │       ├── 03-skeleton.md
│   │       └── 04-commit-push.md
│   ├── omcr-setup/                   # /omcr-setup — install-style OMCR infra. 6 phases: state / CLAUDE.md scaffold / agent-memory / bib / permissions / report. No interview.
│   │   ├── SKILL.md
│   │   └── phases/
│   │       ├── 01-state-check.md
│   │       ├── 02-claude-md-scaffold.md
│   │       ├── 03-agent-memory.md
│   │       ├── 04-bibliography.md
│   │       ├── 05-permissions.md
│   │       └── 06-report.md
│   ├── start-research/               # /start-research — interview-driven init. 6 phases: precheck / interview / fill CLAUDE.md / preset overlay / manuscript / report
│   │   ├── SKILL.md
│   │   └── phases/
│   │       ├── 01-precheck.md
│   │       ├── 02-interview.md
│   │       ├── 03-fill-claude-md.md
│   │       ├── 04-preset-overlay.md
│   │       ├── 05-manuscript-scaffold.md
│   │       └── 06-report.md
│   └── verify-citation/              # CrossRef/OpenAlex existence + metadata check; updates summary CSV
│       ├── SKILL.md
│       └── verify_citation.py
├── hooks/                            # 4 shell-script hooks + their config
│   ├── hooks.json                    # event registration
│   ├── pii-scrub.sh                  # PreToolUse:Write|Edit blocker
│   ├── memory-load.sh                # SessionStart MEMORY.md injector
│   ├── citation-warn.sh              # PostToolUse:Write|Edit non-blocking warner
│   ├── setup-nudge.sh                # SessionStart nudge if CLAUDE.md is uninitialized
│   ├── default-scrub-patterns.txt    # default PII patterns (project can override)
│   └── README.md                     # configuration guide
├── examples/                         # field-specific overlays
│   └── neuro-fmri/                   # worked specialization for neuroimaging studies (fMRI preprocessing / parcellation / connectivity / ISC)
│       ├── agents/                   # neuro-flavored analysis-implementer body
│       ├── memory-templates/         # 6 redacted MEMORY.md skeletons
│       └── README.md                 # how to overlay + author-your-own guide
├── templates/
│   ├── MEMORY.template.md            # canonical empty MEMORY.md schema
│   ├── journal-registry.json         # venue → CTAN class lookup (27 entries; CTAN packages only, no bundled .cls)
│   └── manuscript-skeleton/          # default LaTeX scaffold copied by /start-research (via manuscript-scaffold skill) into the user's Manuscript dir
│       ├── main.tex                  # documentclass possibly rewritten by manuscript-scaffold per journal-registry
│       ├── sections/{abstract,introduction,methods,results,discussion}.tex
│       ├── figures/.gitkeep
│       ├── references.bib            # empty; managed by @literature-curator post-setup
│       ├── .gitignore                # strips LaTeX build artifacts
│       └── README.md                 # conventions reference
├── wiki/                             # 11-page documentation deep dive (browse here or push to GitHub Wiki)
│   ├── Home.md                       # navigation hub
│   ├── Getting-Started.md            # install + first session
│   ├── Standalone-Usage.md           # OMCR alone walkthrough
│   ├── With-OMC.md                   # OMCR + OMC companion install
│   ├── Configuration.md              # ## Research stack block reference + env vars
│   ├── OMC-Tool-Reference.md         # 47 OMC MCP tools mapped to research stages
│   ├── Agents.md                     # 6 agents reference
│   ├── Commands.md                   # /todofig + /sync + cropfig reference
│   ├── Hooks.md                      # 4 hooks reference
│   ├── Specializing.md               # author a field-specific preset
│   └── README.md                     # how to sync this dir to GitHub Wiki
├── README.md                         # public landing page (front door, links to wiki)
├── CLAUDE.md                         # this file
├── CONTRIBUTING.md                   # contributor guide
└── LICENSE                           # MIT
```

`commands/`, `skills/`, and `hooks/` were originally drafted under `examples/neuro-fmri/` in v0.1.0 and promoted to the core in v0.1.1, rewritten as parameter-driven generics that resolve config from the user's project CLAUDE.md `## Research stack` block.

## Conventions to enforce when editing

- **kebab-case** for all filenames in `agents/`, `commands/`, `skills/`. Renaming an agent breaks `@`-mentions everywhere — don't rename without checking cross-references.
- **YAML frontmatter** required on every agent / skill / command file: `name`, `description` at minimum; `model`, `color`, `memory` where applicable. Mirror upstream `oh-my-claudecode/agents/executor.md` for structure.
- **No PII** in any tracked file outside `examples/<field>/` and `LICENSE`. The PII set: institution names, advisor names, real subject IDs, email addresses, absolute paths on the maintainer's machine, target journal names. Domain-specific worked content (atlases, hyperparameters, dataset references) is allowed only under `examples/<field>/`.
- **English-first** language directive on all agents in `agents/`. Agents say "default to English; override via project CLAUDE.md". Do not bake a specific non-English default into the core.
- **Domain-specific content** belongs under `examples/<field>/`, never in the core. If you find yourself adding `nilearn` / `Biopython` / `astropy` / etc. to a core agent, move that content to a preset.

## Memory pattern

Each agent maintains a persistent memory at `.claude/agent-memory/<agent-name>/MEMORY.md` in the **user's project** (not in this plugin repo — `.claude/` is gitignored here). The `memory-load.sh` hook auto-loads them on `SessionStart`.

- The canonical empty schema is [`templates/MEMORY.template.md`](templates/MEMORY.template.md).
- Redacted worked examples (one per agent, neuro-flavored) live under [`examples/neuro-fmri/memory-templates/`](examples/neuro-fmri/memory-templates/).
- Per-agent `MEMORY.md` should be ~200 lines max — push longer detail into linked topic files (e.g. `hypothesis-log.md`, `bugs-log.md`, `nomenclature.md`).

When editing agents, link to the template file via a relative path so users discover the schema.

## Harness — what's wired in

The plugin manifest (`.claude-plugin/plugin.json`) declares four registries:
- `agents: ./agents/` — 6 `@`-mentionable agents
- `commands: ./commands/` — 4 slash commands (`/omcr-setup` installs OMCR infrastructure; `/start-research` runs the interview-driven first-project init; `/todofig` and `/sync` resolved against the user's `## Research stack` block)
- `skills: ./skills/` — 5 invocable skills (`omcr-setup`, `start-research`, `cropfig`, `verify-citation`, `manuscript-scaffold`)
- `hooks: ./hooks/hooks.json` — 4 lifecycle hooks

The 4 hooks wire to Claude Code events:
- `PreToolUse:Write|Edit` → `pii-scrub.sh` — blocks writes containing matched PII patterns.
- `SessionStart` → `memory-load.sh` — concatenates `.claude/agent-memory/*/MEMORY.md` into session context.
- `SessionStart` → `setup-nudge.sh` — non-blocking one-line nudge if `CLAUDE.md` lacks the `## Project context` or `## Research stack` blocks (suggests `/omcr-setup`, then `/start-research`).
- `PostToolUse:Write|Edit` → `citation-warn.sh` — heuristic warning for manuscript markdown with uncited paragraphs.

All four honor `CLAUDE_RESEARCH_DISABLE_<NAME>=1` env vars for per-project disabling. See [`hooks/README.md`](hooks/README.md) for the full configuration guide and how to extend.

The commands + skill read three layers (in priority order): env vars → user CLAUDE.md `## Research stack` block → hardcoded defaults. First-run pattern: if the block is missing, the command asks the user once and offers to persist it to CLAUDE.md. See [`wiki/Configuration.md`](wiki/Configuration.md) for the field reference.

## Language directive

Agents in `agents/` default to English for both manuscript work and user-facing dialog. To override (e.g., user prefers Korean for status updates while keeping manuscript text in English), the user sets the language preference in their **own** project's `CLAUDE.md`. Do not commit a non-English default into the core agents.

## OMC companion (recommended, not bundled)

This plugin treats upstream `oh-my-claudecode` as a companion — components like `scientist`, `document-specialist`, `verifier`, `tracer`, `autoresearch`, `deep-interview`, and `trace` add real value for research workflows but are coupled to OMC's MCP server / bridge runtime / `.omc/` storage. Bundling them would drag in OMC's runtime; instead, recommend OMC alongside in the README and document which OMC components fit which research-workflow stage.

If a contributor proposes bundling an OMC component into this plugin, push back: it's almost always better to ship a thin pointer in the README than to fork the runtime coupling.
