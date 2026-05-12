# With OMC (companion install)

Installing OMC alongside OMCR unlocks an orchestration layer — workflow skills (`ralph`, `team`, `autopilot`, `deep-interview`, `autoresearch`, …), an MCP server (`python_repl`, `wiki_*`, `state_*`, `notepad_*`, `trace_*`), and 19 specialized agents. For what OMC is and how it works internally, see [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode). **This page is for how to combine OMC with OMCR's own agents and commands.**

## Install OMC alongside

```bash
# In Claude Code (recommended once listed):
/plugin install oh-my-claudecode

# Or npm fallback:
npm install -g oh-my-claude-sisyphus
```

Verify by typing `/oh-my-claudecode:` in Claude Code — autocomplete should list `autopilot`, `deep-interview`, `ralph`, `team`, `autoresearch`, `trace`, etc. For git-clone / advanced install paths, see upstream OMC docs.

## Workflow stages — OMCR + OMC mapping

The detailed recipes below pair specific OMCR assets with specific OMC orchestrators. This table is the per-stage crosswalk reference.

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

## Recipes — pairing OMCR with OMC

Each recipe pairs one OMCR-side asset (agent or command) with one OMC orchestrator. Field-neutral; substitute your domain specifics. Skip any recipe whose OMC piece you haven't installed.

### How these recipes work — type the commands in order

There is **no automatic pipeline** between OMCR agents and OMC orchestrators in v0.1.x. OMCR's 6 agents are prompt-only and do not invoke OMC slash commands directly (a "detect-and-enhance" auto-invocation is on the v0.2 backlog — see [OMC-Tool-Reference.md](OMC-Tool-Reference.md#how-omcr-side-agents-can-call-omc-tools)). "Pairing" in this section means **workflow-stage co-residence**, not magical chaining: you, the user, type each command in turn in the same Claude Code session. The handoff between an OMCR agent and an OMC skill is typically a file path (e.g. `.omc/specs/...`, `.claude/agent-memory/...`) or a natural-language quote of the previous step's output. Each recipe below lists the exact commands in execution order — treat them as a typing sequence, not as one fused command.

### Recipe R1 — Start research on a new topic

**When**: you're sitting down to *start research* on a new topic with `@supervisor` — the project already exists (CLAUDE.md is set up), but this specific research direction is fresh and the question is still vague. Not the `/omcr-setup` + `/start-research` moment (that's project bootstrapping); this is the **intellectual start** of a research thread.

**Pair**: `@supervisor` + `/oh-my-claudecode:deep-interview`

**Why**: deep-interview's Socratic loop forces falsifiability + evaluator specification before you commit a single analysis hour. Catches the "we're researching X" → "but what's the actual testable claim?" gap.

**Flow**:

```
1. @supervisor I want to start research on [topic]
   → supervisor lays out what it knows, surfaces the gap (vague Q, no evaluator)

2. /oh-my-claudecode:deep-interview "starting research on [topic] — is it
   testable, and what's the PASS/FAIL evaluator?"
   → deep-interview iterates Socratically until you have a falsifiable
     hypothesis + a concrete evaluator (the function that says PASS or FAIL
     given results). Output saved to .omc/specs/deep-interview-{slug}.md.

3. @supervisor read .omc/specs/deep-interview-{slug}.md and record the
   result in hypothesis-log.md, update the project goals
   → durable in OMCR's per-agent memory (.claude/agent-memory/supervisor/)
```

**Result**: a research thread starts with a written, testable Q + evaluator, not "we'll figure out the eval as we go".

### Recipe R2 — Must-finish parameter sweep

**When**: parameter sweep or seed-stability check that **must** complete and pass a reviewer gate before you trust the result.

**Pair**: `@analysis-implementer` + `/oh-my-claudecode:ralph` (with `@reviewer` as the reviewer gate)

**Why**: ralph won't terminate on iteration count alone — it requires the configured reviewer to verify completion. Prevents the "ran for 50 epochs, looks fine, ship it" failure mode.

**Flow**:

```
1. @analysis-implementer write the sweep script for the R3 contrast
   → produces analysis/sweep_R3.py with permutation logic + saved
     distribution

2. /oh-my-claudecode:ralph --critic=@reviewer "run the sweep until the
   spin-test p-value stabilizes (delta < 0.001 across last 3 iterations)"
   → ralph loops analysis-implementer; on each iteration @reviewer checks
     stability + spot-checks the perm distribution.

3. ralph blocks completion until @reviewer returns PASS, then writes the
   final state to .omc/state/
```

**Result**: sweep terminates only on a verified stable result, with audit trail in `.omc/state/` for the Methods appendix.

### Recipe R3 — Parallel literature scan

**When**: 20–50 candidate papers to triage, where serial `@document-specialist` calls would take hours.

**Pair**: `@literature-curator` (+ OMCR's `verify-citation` skill) + `/oh-my-claudecode:team`

**Why**: team partitions across N clones; each returns a structured summary; literature-curator merges + runs OMCR's `verify-citation` skill on each entry before adding to `references.bib`.

**Flow**:

```
1. @literature-curator give me the candidate paper list for "rest-state
   scaffold"
   → produces a 30-item DOI list with placeholder summaries

2. /team 5:document-specialist "summarize papers 1-6 / 7-12 / 13-18 /
   19-24 / 25-30 with fields: claim, method, dataset, effect size"
   → team spawns 5 clones; each returns structured summaries

3. @literature-curator merge the 5 summary batches, deduplicate, then run
   verify-citation on each DOI before adding to references.bib
   → verify-citation gates each entry against CrossRef/OpenAlex; merged
     BibTeX lands in your manuscript directory
```

**Result**: ~6× throughput on the survey, with `verify-citation` gating preserving citation rigor.

### Recipe R4 — Build analysis *tooling* (not the analysis itself)

**When**: you need a reusable helper — a custom statistical function, a plotting wrapper, a data-loader for a specific schema.

**Pair**: `@analysis-implementer` + `/oh-my-claudecode:autopilot`

**Why**: autopilot ships a spec → code → tests pipeline. Good for tool code (deterministic spec, automated tests possible). **Wrong for hypothesis-driven analysis runs** — those need ralph or autoresearch, where the contract is the evaluator, not test pass.

**Flow**:

```
1. @analysis-implementer specify the contract for a spin-test wrapper:
   inputs, outputs, edge cases
   → produces .omc/specs/spin-test-wrapper.md with signature + invariants

2. /oh-my-claudecode:autopilot "build the spin-test wrapper per the spec
   in .omc/specs/spin-test-wrapper.md"
   → autopilot generates the module + unit tests + verifies on the test
     suite before claiming completion

3. @analysis-implementer use the wrapper in the R3 analysis script
   → analysis script imports the verified helper
```

**Caveat**: do not use autopilot for the analysis script itself — it doesn't know how to iterate on a hypothesis. For analysis runs, see R2 (ralph) or the autoresearch row below.

### More pairings (one-line each)

For these, treat the same pattern as R1–R4: type each command in turn, hand off via file paths or natural language. Flesh out into a full recipe if it starts to recur in your workflow.

| Stage | Pairing | Why |
|---|---|---|
| Plan a costly run | `@supervisor` + `/oh-my-claudecode:ralplan` | Planner/Architect/Critic consensus before commit |
| Parallel datasets | `@analysis-implementer` + `/oh-my-claudecode:ultrawork` | Same analysis on N datasets concurrently |
| Hyperparam loop | `@analysis-implementer` + `/oh-my-claudecode:autoresearch` | Bounded evaluator-driven improvement with persistent JSON log |
| Reproducibility | `@analysis-implementer` + `/oh-my-claudecode:ultraqa` | Fresh-seed re-runs until variance < threshold |
| Cross-model review | `@reviewer` + `/oh-my-claudecode:ccg` | Claude+Codex+Gemini critique synthesis (needs external CLIs) |
| Contested result | `@reviewer` + `/oh-my-claudecode:trace` | Competing-hypotheses ranking with disconfirmation evidence |
| Parallel drafting | `@paper-writer` + `/oh-my-claudecode:team` | Intro/methods/results/discussion in parallel |
| Must-finish revision | `@paper-writer` + `/oh-my-claudecode:ralph` | Loop until `@reviewer` signs off on the manuscript |
| Figure dispatch | `/todofig` + `/oh-my-claudecode:team` | Generate N missing figures in parallel |

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
- [Agents](Agents.md) — OMCR's 6 agents reference
- [OMC's skill catalog (upstream)](https://github.com/Yeachan-Heo/oh-my-claudecode/tree/main/skills) — for the full list of OMC orchestration skills and their CLI flags, defer to upstream
