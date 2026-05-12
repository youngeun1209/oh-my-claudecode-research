# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

OMCR is at **v0.1**, work-in-progress. The only tagged releases are `v0.1.0` and `v0.1.1`; the plugin manifest (`.claude-plugin/plugin.json`) declares `0.1.0`. Everything currently on `main` — including the orchestration engines and the autonomous supervisor — is unreleased v0.1 work. There is no v0.2 / v0.3 / v0.4 — those labels showed up in earlier docs by mistake and are being removed. Current tree ships:
- 6 research-team agents (`agents/`)
- 10 slash commands (`commands/`) — 4 setup/workflow (`/omcr-setup`, `/start-research`, `/todofig`, `/sync`) + 6 orchestration engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`)
- 14 skills (`skills/`) — 7 setup/workflow skills + 1 primitive (`orchestrate`) + 6 engine skills backing the orchestration commands
- 4 lightweight hooks (`hooks/`)
- a canonical memory schema (`templates/MEMORY.template.md`)
- canonical orchestration-state schemas (`develop/example-state/` — tracked reference for `.claude/omcr-state/{paper,reviews,citations,figures,rebuttals}.json` + `_run-log.jsonl`)
- the plugin manifest (`.claude-plugin/plugin.json`)
- one worked example preset (`examples/neuro-fmri/` — neuro-flavored analysis-implementer body + redacted MEMORY.md skeletons)
- wiki documentation (`wiki/`) — 15 markdown pages, mirrors to GitHub Wiki via `wiki/README.md` instructions

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
├── commands/                         # 10 thin dispatcher slash commands — all delegate to a matching skill
│   ├── omcr-setup.md                 # /omcr-setup → skills/omcr-setup/
│   ├── start-research.md             # /start-research → skills/start-research/
│   ├── todofig.md                    # /todofig → skills/todofig/
│   ├── sync.md                       # /sync → skills/sync/
│   ├── iterate-revision.md           # /iterate-revision → skills/iterate-revision/
│   ├── literature-sweep.md           # /literature-sweep → skills/literature-sweep/
│   ├── respond-reviewer.md           # /respond-reviewer → skills/respond-reviewer/
│   ├── figure-bake.md                # /figure-bake → skills/figure-bake/
│   ├── outline-expand.md             # /outline-expand → skills/outline-expand/
│   └── supervisor-drive.md           # /supervisor-drive → skills/supervisor-drive/
├── skills/                           # 14 skills: 1 primitive + 6 engines + 7 setup/workflow
│   ├── orchestrate/                  # PRIMITIVE: state-read + dispatch + evaluate + loop. Internal — composed by engines, never invoked directly.
│   │   ├── SKILL.md
│   │   └── phases/{01-state-read,02-dispatch,03-evaluate,04-loop}.md
│   ├── iterate-revision/             # ENGINE: writer ↔ reviewer loop on one section
│   │   ├── SKILL.md
│   │   └── phases/{01-precheck,02-draft-or-revise,03-review,04-evaluate,05-finalize}.md
│   ├── literature-sweep/             # ENGINE: parallel curator dispatch + verify-citation hard gate
│   │   ├── SKILL.md
│   │   └── phases/{01-precheck,02-search,03-parallel-read,04-deduplicate,05-verify,06-finalize}.md
│   ├── respond-reviewer/             # ENGINE: classify-and-dispatch rebuttal letter
│   │   ├── SKILL.md
│   │   └── phases/{01-parse-letter,02-classify,03-dispatch-per-comment,04-aggregate,05-evaluate,06-finalize}.md
│   ├── figure-bake/                  # ENGINE: 3-agent figure loop with cropfig integration
│   │   ├── SKILL.md
│   │   └── phases/{01-precheck,02-brief,03-implement,04-critique,05-evaluate,06-finalize}.md
│   ├── outline-expand/               # ENGINE: map-reduce parallel section drafting
│   │   ├── SKILL.md
│   │   └── phases/{01-precheck,02-map,03-reduce,04-finalize}.md
│   ├── supervisor-drive/             # ENGINE: autonomous orchestrator with 6 safety gates
│   │   ├── SKILL.md
│   │   └── phases/{00-resume-check,01-state-survey,02-action-plan,03-confirm-or-auto,04-engine-invoke,05-checkpoint,06-iterate-or-finalize,07-report}.md
│   ├── cropfig/                      # generic figure-only crop (env-var + CLAUDE.md driven)
│   │   ├── SKILL.md
│   │   └── {crop_bounds,crop_figures,export_deck,upload_figures}.py
│   ├── manuscript-scaffold/          # state check / journal lookup / skeleton / commit-push — called by /start-research phase 6, also standalone
│   │   ├── SKILL.md
│   │   └── phases/{01-state-check,02-journal-template,03-skeleton,04-commit-push}.md
│   ├── omcr-setup/                   # backs /omcr-setup — install-style OMCR infra. 6 phases: state / CLAUDE.md scaffold / agent-memory / bib / permissions / report. No interview. Also scaffolds .claude/omcr-state/ for engines.
│   │   ├── SKILL.md
│   │   └── phases/{01-state-check,02-claude-md-scaffold,03-agent-memory,04-bibliography,05-permissions,06-report}.md
│   ├── start-research/               # backs /start-research — interview-driven init; phase 5 seeds @reviewer's venue-specific bar from journal-registry / WebFetch
│   │   ├── SKILL.md
│   │   └── phases/{01-precheck,02-interview,03-fill-claude-md,04-preset-overlay,05-venue-scope-seed,06-manuscript-scaffold,07-report}.md
│   ├── sync/                         # backs /sync — state reconciler (status snapshot + agent-memory drift)
│   │   └── SKILL.md
│   ├── todofig/                      # backs /todofig — deck-vs-outline gap analyzer
│   │   └── SKILL.md
│   └── verify-citation/              # CrossRef/OpenAlex existence + metadata check; hard gate for /literature-sweep
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
│   ├── journal-registry.json         # venue → CTAN class lookup + aims/scope/editorial-priorities/reviewer-concerns per venue (27 entries; CTAN packages only, no bundled .cls). Schema v1.1.
│   └── manuscript-skeleton/          # default LaTeX scaffold copied by /start-research (via manuscript-scaffold skill) into the user's Manuscript dir
│       ├── main.tex                  # documentclass possibly rewritten by manuscript-scaffold per journal-registry
│       ├── sections/{abstract,introduction,methods,results,discussion}.tex
│       ├── figures/.gitkeep
│       ├── references.bib            # empty; managed by @literature-curator post-setup
│       ├── .gitignore                # strips LaTeX build artifacts
│       └── README.md                 # conventions reference
├── develop/                          # local working drafts (gitignored — EXCEPT example-state/)
│   ├── example-state/                # TRACKED: canonical .claude/omcr-state/ JSON schemas (copied by /omcr-setup)
│   │   ├── README.md                 # populated examples + schema enums
│   │   ├── paper.json                # manuscript progress (status / iter / outline / hypothesis)
│   │   ├── reviews.json              # append-only reviewer verdict history
│   │   ├── citations.json            # BibTeX queue + verified + last_sweep
│   │   ├── figures.json              # per-figure brief / impl / critique status
│   │   ├── rebuttals.json            # per-run rebuttal entries from /respond-reviewer
│   │   └── _run-log.jsonl            # append-only run log (one JSON per line)
│   └── (other develop/ files are gitignored — design notes, decisions, test fixtures, smoketest)
├── wiki/                             # 15-page documentation deep dive (browse here or push to GitHub Wiki)
│   ├── Home.md                       # navigation hub
│   ├── Getting-Started.md            # install + first session
│   ├── Standalone-Usage.md           # OMCR alone walkthrough (@-mention style)
│   ├── Using-Orchestration.md        # how to use the 6 engines (Level 1/2/3 walkthrough)
│   ├── With-OMC.md                   # OMCR + OMC companion install + 5 worked recipes
│   ├── Configuration.md              # ## Research stack block reference + env vars (incl. data_root)
│   ├── OMC-Tool-Reference.md         # OMC MCP tools mapped to research stages + inverse map per OMCR engine
│   ├── Orchestration-Model.md        # state store + 4 primitives + frontmatter conventions (writes:, cost_estimate_tokens:)
│   ├── Orchestration-Comparison.md   # OMCR-alone vs OMCR+OMC matrix + decision tree
│   ├── Autonomous-Drive.md           # /supervisor-drive deep dive (6 safety gates)
│   ├── Agents.md                     # 6 agents reference
│   ├── Commands.md                   # all 10 slash commands reference
│   ├── Hooks.md                      # 4 hooks reference
│   ├── Specializing.md               # author a field-specific preset + engine-skill frontmatter
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

## Plugin wiring — what this registers with Claude Code

The plugin manifest (`.claude-plugin/plugin.json`) declares four registries:
- `agents: ./agents/` — 6 `@`-mentionable agents
- `commands: ./commands/` — 10 thin dispatcher slash commands: 4 setup/workflow (`/omcr-setup`, `/start-research`, `/sync`, `/todofig`) + 6 orchestration engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`) — each forwards `$ARGUMENTS` to its matching skill
- `skills: ./skills/` — 14 invocable skills: 7 setup/workflow (`omcr-setup`, `start-research`, `sync`, `todofig`, `cropfig`, `verify-citation`, `manuscript-scaffold`) + 1 primitive (`orchestrate` — internal building block, composed by engines, not invoked directly) + 6 engine skills backing the orchestration commands. `cropfig`, `verify-citation`, `manuscript-scaffold` are also standalone-invocable.
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
