# Agents — reference

OMCR ships 5 agents under `agents/`. Each is a single markdown file with YAML frontmatter (loaded into Claude Code's `@`-mention picker) plus a structured prose body.

## `@supervisor`

**Role:** PI-level scientific vision keeper + project orchestrator. Owns the central hypothesis and the narrative spine; delegates implementation, writing, figures, and review to the four subagents.

**When to use:**
- "Where are we in the project? What's next?"
- "Does this output align with our hypothesis?"
- "How should we frame [X] in the paper?"
- "A reviewer might argue [Y] — how do we respond?"

**Reads:** project CLAUDE.md (`## Project context`, `## Research stack`), `.claude/agent-memory/supervisor/MEMORY.md` + linked topic files.

**Writes:** updates to `supervisor/MEMORY.md` (hypothesis log, literature anchor list, settled framing decisions, venue strategy, project status).

**Delegates to:** `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`.

**Model:** `opus` (color: red, memory: project).

[Source: `agents/supervisor.md`](../agents/supervisor.md)

## `@analysis-implementer`

**Role:** Implements analysis pipelines, statistical analyses, ML/sim models. Field-neutral by default; overlay `examples/<field>/agents/analysis-implementer.md` for domain-flavored expertise.

**When to use:**
- "Implement the [analysis name] pipeline"
- "The [output] is giving weird edge cases — diagnose"
- "Train a model to predict [outcome] from [features]"

**Reads:** project CLAUDE.md, `analysis-implementer/MEMORY.md` (pipeline state, hyperparameter conventions, exclusion criteria, bug log).

**Writes:** modular Python (or other-language) code; intermediate outputs to disk; sanity-check plots; run logs. Updates `analysis-implementer/MEMORY.md` when a new parameter choice / exclusion rule is settled.

**Defers to:** `@supervisor` for framing calls. Hands off to `@figure-descriptor` for visualization design and `@paper-writer` for results writeup.

**Model:** `sonnet` (color: cyan, memory: project).

[Source: `agents/analysis-implementer.md`](../agents/analysis-implementer.md) | [Neuro-fmri preset: `examples/neuro-fmri/agents/analysis-implementer.md`](../examples/neuro-fmri/agents/analysis-implementer.md)

## `@paper-writer`

**Role:** Drafts and revises manuscript sections (abstract, introduction, methods, results, discussion, cover letter, response to reviewers) at high-impact-venue prose quality.

**When to use:**
- "Draft the Introduction"
- "Revise the Discussion to interpret rather than restate"
- "Write a 150-word abstract for [target venue]"
- "Draft a rebuttal to Reviewer 2's concern about [X]"

**Reads:** project CLAUDE.md (narrative spine, target venue, language preference), `paper-writer/MEMORY.md` (section status, locked nomenclature, hard-won phrasings, reviewer-response log).

**Writes:** manuscript sections; updates `paper-writer/MEMORY.md` with section-status changes and any newly-locked phrasings or nomenclature.

**Defers to:** `@supervisor` for framing decisions. Hands off claims requiring new data to `@analysis-implementer`.

**Model:** `opus` (color: yellow, memory: project).

[Source: `agents/paper-writer.md`](../agents/paper-writer.md)

## `@figure-descriptor`

**Role:** Designs figures as implementation-ready briefs — does not generate images. Output is detailed enough for direct implementation in Keynote / Illustrator / Inkscape / matplotlib.

**When to use:**
- "Design Fig N — show [the result]"
- "We need a conceptual overview figure for the Introduction"
- "Reviewer says Fig 3 is confusing — diagnose and propose redesign"
- "What color palette should we use across all figures?"

**Reads:** project CLAUDE.md, `figure-descriptor/MEMORY.md` + linked `color-system.md` (locked palette and plot-type conventions).

**Writes:** per-figure design briefs (panel structure, layout, color encoding, caption text, implementation notes); updates `figure-descriptor/MEMORY.md` with approved figure designs and color-system entries.

**Defers to:** `@supervisor` for "what should this figure show?" framing. Hands off prose to `@paper-writer`.

**Model:** `sonnet` (color: orange, memory: project).

[Source: `agents/figure-descriptor.md`](../agents/figure-descriptor.md)

## `@reviewer`

**Role:** Adversarial pre-submission peer review at the target venue's level. Finds every weakness before the editor does.

**When to use:**
- "Review the Introduction draft"
- "Is Fig 3 good enough for [target venue]?"
- "Stress-test our methodology — what would a reviewer attack?"
- "Do a full pre-submission review"

**Reads:** project CLAUDE.md (target venue, central hypothesis), `reviewer/MEMORY.md` (open major concerns, resolved concerns, project-specific attack vectors).

**Writes:** structured reviews (verdict, major/minor concerns, optional suggestions) in formal peer-review format; updates `reviewer/MEMORY.md` with concern status changes.

**Does NOT:** resolve concerns. Resolution belongs to `@supervisor`, `@analysis-implementer`, or `@paper-writer`.

**Model:** `opus` (color: red, memory: project).

[Source: `agents/reviewer.md`](../agents/reviewer.md) | Generic attack vectors are in the agent body; for domain-specific attacks see `examples/<field>/`.

## Agent interaction pattern

```
                    @supervisor
                   ┌───────┼───────┐
                   ▼       ▼       ▼
          @analysis-    @paper-    @figure-
           implementer   writer    descriptor
                   ▲       ▲       ▲
                   └───────┼───────┘
                       @reviewer
                         (any output may be reviewed)
```

`@supervisor` defines the task. The three "doer" agents (`@analysis-implementer`, `@paper-writer`, `@figure-descriptor`) produce outputs. `@reviewer` stress-tests any output. Concerns flow back to `@supervisor` for routing.

## Frontmatter contract

All 5 agents follow this YAML frontmatter shape (mirrors upstream `oh-my-claudecode/agents/executor.md`):

```yaml
---
name: agent-name        # kebab-case, must match @-mention
description: "Use this agent when ... [Examples block]"
model: opus | sonnet | haiku
color: red | yellow | cyan | orange | blue | ...
memory: project | none
---
```

## Domain specialization

To use OMCR for a specific field, you can either:

1. **Edit the core agent files** in `agents/` to add field-specific content (loses portability — your edits diverge from upstream).
2. **Overlay a preset** from `examples/<field>/` (recommended — keeps core upgradable).

Currently shipped preset: `examples/neuro-fmri/` (Mapper-on-fMRI flavor for `@analysis-implementer`). To author your own: see [Specializing](Specializing.md).

## See also

- [Commands](Commands.md) — `/todofig` and `/sync` workflows
- [Hooks](Hooks.md) — `memory-load` auto-loads each agent's MEMORY.md on session start
- [Configuration](Configuration.md) — project CLAUDE.md schema the agents read
- [Specializing](Specializing.md) — authoring field-specific presets
