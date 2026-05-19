# oh-my-codex-research (OMXR)

Research-edition workflows for [OpenAI Codex CLI](https://github.com/openai/codex) and [oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex).

OMXR is the research companion to `oh-my-codex`: six research agent templates plus Codex skills for hypothesis work, analysis, manuscript drafting, figures, citations, reviewer response, and project-state driven research loops.

## What You Get

- Six research agents: `supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`
- Research setup with `$omxr-setup`
- First-project interview with `$start-research`
- Figure and manuscript workflows: `$todofig`, `$sync`, `$figure-bake`, `$outline-expand`
- Literature and review workflows: `$literature-sweep`, `$verify-citation`, `$respond-reviewer`, `$iterate-revision`
- Durable project state under `.omx/state/omxr/`
- Per-agent research memory under `.omx/omxr/agent-memory/`

## Recommended Install

Install the base Codex/OMX runtime first:

```bash
npm install -g @openai/codex oh-my-codex
omx setup
omx doctor
codex login status
omx exec --skip-git-repo-check -C . "Reply with exactly OMX-EXEC-OK"
```

Then install or expose this plugin through Codex plugin discovery. The canonical plugin manifest is:

```text
.codex-plugin/plugin.json
```

This plugin manifest exposes skills. Runtime wiring, hooks, base config, and generic `AGENTS.md` behavior remain owned by `omx setup`; research project scaffolding is owned by `$omxr-setup`.

## Start a Research Project

Inside the research project:

```text
$omxr-setup
$start-research
```

`$omxr-setup` creates or refreshes:

- `AGENTS.md` research blocks
- `.omx/state/omxr/{paper,reviews,citations,figures,rebuttals}.json`
- `.omx/state/omxr/_run-log.jsonl`
- `.omx/omxr/agent-memory/<agent>/MEMORY.md`
- optional `.codex/agents/omxr/<agent>.md`
- `paper/references.bib`
- `references.csv`

`$start-research` fills the project-specific fields: working title, field, target venue, central hypothesis, datasets, narrative spine, manuscript paths, and optional preset overlays.

## Agent Roster

| Agent | Role |
| --- | --- |
| `supervisor` | PI-level scientific vision keeper and project orchestrator |
| `analysis-implementer` | Pipelines, statistics, ML/simulation models, and numerical validation |
| `paper-writer` | Manuscript sections, abstracts, cover letters, and reviewer responses |
| `figure-descriptor` | Figure design briefs and figure-plan critique |
| `reviewer` | Adversarial pre-submission review |
| `literature-curator` | BibTeX, citation resolution, literature summary table, and citation verification |

## State and Memory

OMXR state is project-local and intentionally gitignored:

```text
.omx/state/omxr/
.omx/omxr/agent-memory/
```

Tracked source templates live in:

```text
agents/
templates/
develop/example-state/
```

## Hooks and Safety

Codex/OMX hook support differs by runtime version. OMXR classifies safety features as native hook, runtime fallback, or explicit check:

- memory load
- setup nudge
- PII scrub
- citation warning

If native write interception is unavailable, workflows must call the explicit check before finalizing write-heavy manuscript changes.

## Documentation

- [Getting Started](wiki/Getting-Started.md)
- [Agents](wiki/Agents.md)
- [Configuration](wiki/Configuration.md)
- [Hooks](wiki/Hooks.md)
- [Using Orchestration](wiki/Using-Orchestration.md)
- [Specializing](wiki/Specializing.md)

## Migration

Older research projects can copy prior agent memory and state into the new OMXR paths:

- old agent memory -> `.omx/omxr/agent-memory/<agent>/MEMORY.md`
- old state -> `.omx/state/omxr/<name>.json`

Do not delete old local state until the migrated project has passed `$omxr-setup` and at least one workflow smoke test.

## Contributor Checks

Run the stale reference guard before release:

```bash
bash tools/check-stale-references.sh
```

Clean output with exit code `0` means onboarding/runtime surfaces no longer contain unallowlisted legacy branding.

## License

MIT — see [LICENSE](LICENSE).
