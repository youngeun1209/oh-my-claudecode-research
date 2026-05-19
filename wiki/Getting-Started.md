# Getting Started

This walkthrough starts from the Codex/OMX runtime and then adds the research-edition project scaffolding.

## 1. Install Base Codex/OMX

```bash
npm install -g @openai/codex oh-my-codex
omx setup
omx doctor
codex login status
omx exec --skip-git-repo-check -C . "Reply with exactly OMX-EXEC-OK"
```

`omx setup` owns base runtime wiring, Codex hooks, config, and generic `AGENTS.md` behavior. OMXR does not replace that setup path.

## 2. Expose OMXR

OMXR ships a Codex plugin manifest at:

```text
.codex-plugin/plugin.json
```

The manifest exposes skills. It does not own runtime hooks or native-agent installation directly; `$omxr-setup` handles research project scaffolding after base OMX is ready.

## 3. Initialize a Research Project

Inside the target research project:

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
- hook/check readiness for memory load, setup nudge, PII scrub, and citation warnings

`$start-research` fills project-specific details such as working title, target venue, central hypothesis, datasets, narrative spine, manuscript paths, and optional presets.

## 4. Start Working

Common entry points:

```text
$sync
$todofig Fig 2
$literature-sweep
$iterate-revision manuscript/sections/introduction.tex
$supervisor-drive --auto
```

The six research roles are installed from tracked templates in `agents/` when native-agent delivery is enabled:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

## Troubleshooting

- `$omxr-setup` says base runtime is missing: run `omx setup` and `omx doctor`.
- A workflow cannot find memory: check `.omx/omxr/agent-memory/<agent>/MEMORY.md`.
- A workflow cannot find state: check `.omx/state/omxr/`.
- PII or citation checks are not automatic: your Codex/OMX runtime may need explicit check fallback rather than native write interception.
