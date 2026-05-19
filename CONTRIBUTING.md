# Contributing to oh-my-codex-research

This is a small repo with a focused scope: 6 research-team agents, 10 slash commands, 14 skills, 4 lightweight hooks, and field-specific example presets. Contributions that fit that scope are welcome. Contributions that expand it (npm publishing, build pipelines, domain-specific helpers in the core, etc.) probably belong in upstream [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex) instead.

## How to propose a new agent

The bar for adding an agent to `agents/` is high. New agents must:

1. **Be reusable across research fields.** Domain-specific knowledge belongs in a preset under `examples/<field>/`, not the core.
2. **Justify why they're not a skill.** Skills are for procedural workflows; agents are for personas with persistent state and judgment. If your candidate fits "this is a procedure that runs end-to-end", it's a skill, not an agent.
3. **Cover an unmet research-team role.** The 6 agents (supervisor / analysis-implementer / paper-writer / figure-descriptor / reviewer / literature-curator) cover the canonical pipeline. New agents should fill a real gap, not duplicate.

If your candidate clears those, open an issue first to discuss before sending a PR.

## How to specialize (the `examples/<field>/` overlay pattern)

Use [`examples/neuro-fmri/`](examples/neuro-fmri/) as the worked example. The pattern:

1. **Identify which core agents need a domain-flavored body.** Most of the time it's just `analysis-implementer` — the supervisor / paper-writer / figure-descriptor / reviewer can usually stay generic with a few placeholder fills.
2. **Identify field-specific commands and skills.** Anything tied to a specific export pipeline (Keynote / Jupyter / RMarkdown / Quarto / etc.) belongs in your preset.
3. **Produce redacted memory skeletons.** Show what each agent typically tracks in your field, without leaking your real project content.
4. **Write a `README.md` for the preset.** Mirror [`examples/neuro-fmri/README.md`](examples/neuro-fmri/README.md): what's in the preset, install/overlay recipe, what it adds vs. core, adapt-to-your-stack notes.

Layout:

```
examples/<field>/
├── README.md
├── agents/
│   └── <agent>.md           # only the agents that need domain-flavored bodies
├── commands/                # field-specific slash commands (optional)
├── skills/                  # field-specific skills (optional)
└── memory-templates/        # one redacted MEMORY.md skeleton per agent
    └── <agent>/MEMORY.md
```

PRs adding new presets are welcome.

## Frontmatter contract

Every file in `agents/`, `commands/`, `skills/`, and any `examples/<field>/agents|commands|skills/` must start with YAML frontmatter:

**Agents** (`name`, `description`, `model`, optional `color`, `memory`):

```yaml
---
name: my-agent
description: "Use this agent when you need to ... [examples block]"
model: sonnet
color: blue
memory: project
---
```

**Skills** (`name`, `description`, optional `argument-hint`, `level`):

```yaml
---
name: my-skill
description: One-line skill purpose. Use_When / Do_Not_Use_When sections in the body.
argument-hint: "[--flag <value>]"
---
```

**Commands** (`description`, optional `argument-hint`):

```yaml
---
description: One-line command purpose.
argument-hint: [optional positional or scope hint]
---
```

Mirror the upstream `oh-my-codex` shapes when in doubt. Examples to model: [`oh-my-codex/agents/executor.md`](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/agents/executor.md), [`oh-my-codex/skills/autopilot/skill.md`](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/skills/autopilot/skill.md).

## MEMORY.md schema contract

Every persistent agent memory follows the schema at [`templates/MEMORY.template.md`](templates/MEMORY.template.md):

- Top-of-file: `**Last synced:** [YYYY-MM-DD]` + role line
- Section by topic, not by date
- Linked topic files for detail beyond ~200 lines
- "What to save / NOT to save" rubric

If your preset ships memory examples (under `examples/<field>/memory-templates/`), redact concrete project content — schemas only.

## PII / scrubbing rules

The repo's PII baseline (enforced via `hooks/default-scrub-patterns.txt` + manual review):

- **Never commit** to any tracked file outside `LICENSE`: real subject IDs, email addresses, advisor names, institution names, target-journal names, absolute paths on a contributor's machine.
- Domain-specific worked content (atlases, hyperparameters, dataset references) is allowed only under `examples/<field>/`.
- The `examples/<field>/` directories are intended for **generic field-specific content** (e.g., fMRI preprocessing conventions, statistical norms) — *not* a single user's particular pipeline, hyperparameters, dataset, or hypothesis. Project-specific methodology belongs in **users' own** project `.codex/agents/` overlays, not in shipped presets.

When in doubt, run an audit. Build the regex from the project's actual sensitive strings (institution / lab / advisor names, real subject-ID format, email pattern) and grep:

```bash
# Replace <YOUR_INSTITUTION>, <YOUR_LAB>, etc. with your project's actual sensitive strings.
rg -i '<YOUR_INSTITUTION>|<YOUR_LAB>|<ADVISOR_NAME>|<EMAIL_PATTERN>|<SUBJECT_ID_FORMAT>' \
   agents/ templates/ hooks/ README.md AGENTS.md CONTRIBUTING.md
```

This should return zero hits.

## Commit conventions

Follow the upstream `oh-my-codex` git-trailer convention when commits warrant the extra context: `Constraint:`, `Rejected:`, `Directive:`, `Confidence:`, `Scope-risk:`, `Not-tested:`. See upstream `oh-my-codex/AGENTS.md` for the full description. Trailers are optional for trivial commits.

For larger changes, prefer one PR per logical change (one new preset, one new hook, one new agent) over bundled PRs.

## Testing locally

There's no formal test suite. Smoke checks before opening a PR:

1. **Plugin loads.** Clone into a scratch dir, run Codex with the plugin, confirm `@`-mention picker shows all expected agents and that hooks register.
2. **Hooks behave.** Run the smoke commands at the bottom of [`hooks/README.md`](hooks/README.md) and confirm exit codes match the documented contract.
3. **PII audit clean.** `rg` command above returns zero hits in non-example tracked files.
4. **Agents respond sensibly.** `@supervisor` with "what's this project about?" should default to asking the user for the central hypothesis, not assuming a domain.

## What's out of scope for this repo

- TypeScript/build pipeline (we ship plain markdown + shell).
- npm publishing.
- Marketplace listing.
- An MCP server.
- General-purpose orchestration agents (those belong in upstream OMX).
- Heavy harness extensions (statusline, keyword auto-trigger) — see the future backlog discussion in the project plan.

PRs that move toward any of these will be redirected.
