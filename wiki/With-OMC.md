# With OMC (companion install)

Installing OMC alongside OMCR unlocks: a stateful Python REPL, a literature wiki, an experiment-state machine, an evidence-driven causal tracer, an evidence-based verifier, and a Socratic interviewer for hypothesis crystallization — all via [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)'s MCP server.

OMCR + OMC = the "fully-loaded" research stack.

## Install OMC alongside

```bash
# Option 1 — Claude Code marketplace (recommended once it's listed):
# In Claude Code: /plugin install oh-my-claudecode

# Option 2 — npm (the runtime that backs OMC's MCP):
npm install -g oh-my-claude-sisyphus

# Option 3 — clone the repo into ~/.claude/plugins/:
git clone https://github.com/Yeachan-Heo/oh-my-claudecode ~/.claude/plugins/oh-my-claudecode
```

After installation, verify in Claude Code:

```
/oh-my-claudecode:
```

The autocomplete should list `/oh-my-claudecode:autopilot`, `/oh-my-claudecode:deep-interview`, `/oh-my-claudecode:trace`, `/oh-my-claudecode:autoresearch`, etc.

And:

```
@
```

Should now include OMC's 19 agents alongside OMCR's 5.

## Workflow stages — OMCR + OMC mapping

| Stage | OMCR | + OMC adds |
|---|---|---|
| **Project bootstrap** | `@supervisor` + your CLAUDE.md | `/oh-my-claudecode:deep-interview` — Socratic clarification until the hypothesis is testable + the evaluator is specified |
| **Literature anchoring** | `@supervisor` maintains a list in MEMORY.md | `@document-specialist` fetches + cites with Context Hub (`chub`); `wiki_add` / `wiki_query` MCP for a searchable literature database |
| **Analysis implementation** | `@analysis-implementer` | `@scientist` adds statistical rigor enforcement (CIs, p-values, effect sizes, `[LIMITATION]` markers); `python_repl` MCP for stateful in-session Python |
| **Iterative experimentation** | (you script the loop) | `/oh-my-claudecode:autoresearch` — bounded evaluator-driven improvement loop with per-iteration JSON + decision logs |
| **Methodology validation** | `@reviewer` raises objections | `@tracer` + `/oh-my-claudecode:trace` — competing-hypotheses ranking, disconfirmation, "next probe" recommendation |
| **Reproducibility / test discipline** | (manual) | `@test-engineer` — TDD-style edge case coverage; `@verifier` enforces fresh-evidence completion checks |
| **Figure design** | `@figure-descriptor` | (no OMC analog — OMCR handles this well alone) |
| **Manuscript writing** | `@paper-writer` | `@writer` for lab-protocol docs / methods appendices / reproducibility guides |
| **Pre-submission review** | `@reviewer` | `@critic` adds multi-perspective stress-tests (pre-mortem, alternative explanations, assumption extraction) |
| **Commit / history hygiene** | (manual) | `@git-master` — atomic-commit discipline for analysis pipelines |
| **Memory across sessions** | OMCR's `memory-load` hook | OMC's `project_memory_*` MCP family for in-session memory operations |
| **State across runs** | (manual logs in MEMORY.md) | OMC's `state_*` MCP family + `notepad_*` MCP family |

## A "full stack" session — example

You sit down to a project that has both installed. A typical session:

### 1. Bootstrap / re-orient

```
@supervisor where are we?
```

Standalone OMCR behavior. Supervisor reads its memory and reports status.

### 2. Refine a vague new direction (OMC)

If your supervisor surfaces a new direction that's still vague:

```
/oh-my-claudecode:deep-interview the question of whether [your new direction] is testable
```

Deep-interview asks Socratic questions until you have a falsifiable hypothesis + an evaluator (a function that says PASS / FAIL given results). Output saved to `.omc/specs/deep-interview-{slug}.md`.

### 3. Literature work (OMC)

```
@document-specialist find recent papers on [topic] in [target_venue]
```

Document-specialist uses Context Hub (`chub`) for curated docs, falls back to WebSearch / WebFetch, returns synthesized findings with URL citations.

Persist to your literature wiki:

```
Use wiki_add to register the Smith 2024 paper under tag "rest-state-scaffold" with the finding "individual rest topology predicts ..."
```

(`wiki_add` is OMC's MCP tool — accessible from the session.)

### 4. Stateful analysis (OMC)

Standalone OMCR's `@analysis-implementer` writes Python scripts you run externally. With OMC's `python_repl`:

```
@analysis-implementer compute the spin-test p-value for the R3 contrast using the saved permutation distribution
```

The agent invokes `python_repl` to execute the computation in a persistent Python kernel — variables stay alive across calls, so subsequent analyses can reuse loaded data.

### 5. Methodology validation (OMC)

When you have a contested result:

```
/oh-my-claudecode:trace the observation that the R4 contrast is non-significant
```

Trace orchestrates `@tracer` in team mode: enumerates competing hypotheses (truly null vs. underpowered vs. wrong operationalization vs. confound), ranks evidence for/against each, names the discriminating probe.

### 6. Figure design (OMCR)

```
@figure-descriptor design Fig 5
```

Unchanged from standalone — no OMC analog.

### 7. Iterative refinement (OMC)

If a result is borderline and you want to systematically improve a parameter:

```
/oh-my-claudecode:autoresearch on the mission "maximize R3 cross-validated accuracy" with evaluator "perm-test p-value < 0.05"
```

Autoresearch runs a bounded loop: iterate the parameter, run the evaluator, persist the JSON + decision log, continue until max-runtime or terminal condition.

### 8. Pre-submission gate (OMCR + OMC)

```
@reviewer review the full draft
```

OMCR's reviewer applies target-venue criteria.

Then:

```
/oh-my-claudecode:critic the analysis plan for R4
```

OMC's critic adds pre-mortem + assumption extraction + alternative-interpretation stress-test on the *plan*, complementing reviewer's *manuscript* focus.

### 9. Save state (OMCR + OMC)

```
/sync
```

OMCR reconciles MEMORY.md files. OMC's `project_memory_write` MCP (if used by any agent during the session) persists in-session updates automatically.

## Configuration overlap

OMC and OMCR each maintain their own state directories:

| Tool | Storage location |
|---|---|
| OMC | `.omc/` in your project (autoresearch runs, deep-interview specs, wiki ingests) |
| OMCR | `.claude/agent-memory/` in your project (per-agent MEMORY.md) |

These do not collide. Both should be gitignored — OMCR's `.gitignore` already excludes `.claude/` and `.omc/`; if you don't have those entries, add them.

If you want OMCR's `memory-load` hook to also surface OMC's `project_memory_*` content on session start, you can write a thin shell adapter — but in most cases the two stay separate by design (OMCR's hook reads its files, OMC's project_memory loads on demand).

## Recommended install order

1. Install OMCR first (lightweight; agents work alone).
2. Run a few sessions to get a feel for the agent personas.
3. Install OMC when you hit a gap (literature volume / python_repl need / iterative experiment loop / methodology stress-test).
4. Add OMC companions one workflow stage at a time. You don't have to use all 19 OMC agents — pick the 3–5 most relevant to your project.

## Disabling OMC features per-project

If you have OMC installed globally but want a specific project to use only OMCR (e.g., for a quick draft or a project with no Python work), disable OMC's hooks in that project's `.claude/settings.json`:

```json
{
  "hooks": {
    "disabled": ["oh-my-claudecode"]
  }
}
```

(Verify the exact field name in your Claude Code version; the principle is "scope OMC's hooks to projects that want them".)

## See also

- [Configuration](Configuration.md) — research-stack block (shared between OMCR commands and OMC's autoresearch)
- [OMC Tool Reference](OMC-Tool-Reference.md) — all 47 OMC MCP tools mapped to research workflow stages
- [Agents](Agents.md) — OMCR's 5 agents reference
