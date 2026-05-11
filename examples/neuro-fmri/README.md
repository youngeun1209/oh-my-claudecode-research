# `examples/neuro-fmri/` — worked specialization

This is a concrete, neuro-fMRI-flavored specialization layered on top of OMCR's core. The core ships field-neutral agents, parameterized commands, and a generic cropfig skill (all in the repo root under `agents/`, `commands/`, `skills/`); this directory adds the **domain content** that makes those generic surfaces useful for a Mapper-on-fMRI study:

- A neuro-flavored body for the `analysis-implementer` agent (concrete fMRI / TDA / Mapper expertise that the field-neutral core agent does not assume)
- Redacted MEMORY.md skeletons showing what each of the 5 agents typically tracks in a Mapper-on-fMRI project

This preset is what the original DoD-Agent project used internally, with project-specific content (advisor, target journal, subject IDs, hypothesis text, dataset paths, hyperparameters) scrubbed out.

## What's in here

```
examples/neuro-fmri/
├── README.md                                   # this file
├── agents/
│   └── analysis-implementer.md                 # neuro-flavored body (nilearn / kepler-mapper / Schaefer / fMRI preprocessing / TDA)
└── memory-templates/                           # redacted MEMORY.md skeletons for each of the 5 agents
    ├── supervisor/MEMORY.md
    ├── analysis-implementer/MEMORY.md
    ├── paper-writer/MEMORY.md
    ├── figure-descriptor/MEMORY.md
    └── reviewer/MEMORY.md
```

The `cropfig` skill and the `/todofig` and `/sync` commands previously lived under this directory as worked examples. They've been **promoted to the core** (under `skills/cropfig/` and `commands/` at the repo root) and parameterized via a `Research stack` block in the user's project `CLAUDE.md`. See `wiki/Configuration.md` for how to point them at your project's paths.

## Install (overlay on top of the core)

After installing the core plugin, overlay this preset's files:

```bash
# 1. The neuro-flavored analysis-implementer (replaces the field-neutral core version):
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# 2. The MEMORY.md skeletons — copy into your project's .claude/agent-memory/<agent>/:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md .claude/agent-memory/$agent/MEMORY.md
done
```

The cropfig skill and the `/todofig` and `/sync` commands are already shipped in the core — no copy needed. Configure them by adding a `## Research stack` block to your project's `CLAUDE.md` (see `wiki/Configuration.md`).

## What this preset adds vs. the field-neutral core

| Surface | Core | Neuro preset |
|---|---|---|
| `analysis-implementer` agent body | Field-neutral; talks generically about ML / stats / simulation | Concrete neuro tooling: `nilearn`, `nibabel`, `kepler-mapper`, `brainiak`, Schaefer/Gordon parcellations, fMRI preprocessing pitfalls, MATLAB ↔ Python interop |
| Memory templates | None (just `templates/MEMORY.template.md` schema) | Redacted skeletons for all 5 agents showing what each typically tracks in a Mapper-on-fMRI project |

## Adapt to your stack

If you're working on neuroscience but a different methodology (HCP-style functional connectivity instead of Mapper, EEG instead of fMRI, etc.), use this preset as a starting point — copy the analysis-implementer body, then edit out the Mapper-specific paragraphs and add your method's specifics.

## Author your own preset (4-step recipe)

1. **Identify which core agents need a domain-flavored rewrite.** For most fields it's just `analysis-implementer` — the supervisor / paper-writer / figure-descriptor / reviewer can usually stay generic with placeholder fills.
2. **Decide what specific knowledge your `analysis-implementer` needs.** List the canonical libraries, methods, parcellations / atlases / databases, common pipeline pitfalls, and statistical conventions.
3. **Produce redacted memory skeletons.** Show what each agent typically tracks in your field, without leaking your real project content.
4. **Add a `README.md` and submit a PR.** Mirror this file's structure: install recipe, what the preset adds vs. core, adapt-to-your-stack notes.

PRs adding new presets (`examples/wet-lab/`, `examples/ml-research/`, `examples/astronomy/`, …) welcome.
