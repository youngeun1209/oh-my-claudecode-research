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

## Recipes — pairing OMCR engines with OMC orchestrators (v0.4+)

The R1–R4 recipes above pair OMCR **agents** (`@supervisor`, `@analysis-implementer`, `@reviewer`, `@paper-writer`, …) with OMC orchestrators. The five recipes below pair OMCR's **6 engines** (the slash commands `/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive` introduced in v0.2–v0.4) with OMC's generic execution modes (`/ralph`, `/team`, `/ultraqa`, `/autopilot`) and OMC specialist agents (`@verifier`, `@tracer`). Each recipe gives a concrete command, a 2–3 sentence "why this composition", and forward-links to OMCR's engine doc + the OMC reference.

These compose because OMCR engines and OMC skills share no state: OMCR writes to `.claude/omcr-state/`, OMC writes to `.omc/`. Each layer's verdicts surface to the other unchanged — OMCR's `DONE | BLOCKED | HALT` per-engine verdicts are exactly what OMC's outer loop checks. See [Orchestration-Comparison.md](Orchestration-Comparison.md) for the full task → tool matrix backing these five.

### Recipe 1 — `/iterate-revision` wrapped in `/ralph` for verifier-gated revision

**When**: you just got R1 back, addressed comments by hand, but one section (typically the discussion) keeps tripping OMCR's reviewer on an "over-claim" issue. You want the loop to keep iterating until OMC's independent `@oh-my-claudecode:verifier` agrees the central claim is supported — not just OMCR's own `@reviewer`.

**Pair**: OMCR `/iterate-revision` + OMC `/oh-my-claudecode:ralph` + OMC `@oh-my-claudecode:verifier`

```bash
/oh-my-claudecode:ralph \
  "/iterate-revision sections/discussion.tex --max-iter 3 --venue Nature" \
  --max-iter 5 \
  --verifier "@oh-my-claudecode:verifier check the central claim in sections/discussion.tex against sections/methods.tex and sections/results.tex; flag any over-claims"
```

What happens:

1. `/oh-my-claudecode:ralph` invokes `/iterate-revision` on `sections/discussion.tex`.
2. OMCR's loop runs up to its inner `--max-iter 3` cap with `@paper-writer` ↔ `@reviewer`, emitting `DONE | BLOCKED | HALT` per OMCR's severity-threshold verdict rule.
3. Ralph then dispatches `@oh-my-claudecode:verifier` as the outer verifier.
4. If `@verifier` flags "over-claim re. effect size given N=8", ralph re-invokes `/iterate-revision` with the verifier's note appended (ralph passes the verifier's feedback through to the next iteration's task brief).
5. Loop continues until **both** OMCR's `@reviewer` says DONE **and** OMC's `@verifier` says PASS, or ralph's outer `--max-iter 5` is exhausted.

**Why this composition**: OMCR's verdict rule trusts its own reviewer, whose MEMORY.md may have drifted toward over-permissive reviews. `/ralph` adds the second-opinion layer with an independent verifier that has no state coupling to `@reviewer`. The result is a revision that passes two different gates, which is what reviewer 2 will effectively be doing on resubmission.

**Links**: [`/iterate-revision` SKILL.md](../skills/iterate-revision/SKILL.md) · [`/oh-my-claudecode:ralph`](https://github.com/Yeachan-Heo/oh-my-claudecode#features) · [Orchestration-Comparison §A row 1](Orchestration-Comparison.md#a--task--tool-matrix)

### Recipe 2 — Distributed literature sweep via `omc team` (tmux survives session restart)

**When**: 50+ candidate papers to triage on a single topic, week-long sweep, and you want the work to keep going after your Claude Code session closes for the night. OMCR's `/literature-sweep --parallel 4` caps at 4 in-session parallel curator instances; for true distributed work that survives a session restart you need OMC's tmux-backed `omc team`.

**Pair**: OMCR `/literature-sweep` (in-session) vs OMC `omc team N:literature-curator` (tmux CLI)

In-session (≤ 4 batches, single Claude Code session, dies if session ends):

```bash
/literature-sweep "neural manifolds in motor cortex" --n 30 --parallel 4
```

Cross-session (tmux panes, survive session restart):

```bash
omc team 5:literature-curator \
  "sweep topic 'neural manifolds in motor cortex' in 5 batches of ~10 papers each; \
   each worker emits BibTeX + summary CSV rows; \
   merge into <project>/paper/references.bib + ./references.csv; \
   verify-citation every entry before commit"
```

What happens:

1. `omc team` spawns 5 tmux panes, each running a `literature-curator` worker.
2. Each worker handles ~10 candidate papers (CrossRef/OpenAlex query + summary extraction + the `verify-citation` skill).
3. Verified entries land in `references.bib` and the summary CSV; rejected entries (failed `verify-citation`) land in `citations.json.last_sweep.rejected` with a reason.
4. If your Claude Code session closes, the tmux panes keep going. Reattach later with `omc team status <session-name>`.

**Why this composition**: OMCR's `/literature-sweep` is sequential by default (Phase 2 §1) and capped at `--parallel 4` for in-session safety. The parallelism is real but bounded by the runtime's rate limiter and lifecycled with the Claude Code session. For genuinely large sweeps where (a) 50+ papers is closer to a week's work than an hour's and (b) you want to walk away from the terminal, OMC's tmux team is the right runtime. OMCR's `verify-citation` skill is the hard gate on each entry in both runtimes — the workers reuse it, so the verification rigor is identical.

**Links**: [`/literature-sweep` SKILL.md](../skills/literature-sweep/SKILL.md) · [`/oh-my-claudecode:team` (tmux variant)](https://github.com/Yeachan-Heo/oh-my-claudecode#tmux-cli-workers--codex--gemini-v440) · [verify-citation skill](../skills/verify-citation/SKILL.md) · [Orchestration-Comparison §A row 2](Orchestration-Comparison.md#a--task--tool-matrix)

### Recipe 3 — Multi-style revision via `/ultraqa`

**When**: you want to try 3 different revision strategies (e.g., "concise", "detailed", "narrative") on the same section in parallel and keep the best by the reviewer's own rating. OMCR's `/iterate-revision` converges on a single output by design; OMC's `/ultraqa` is built for "fork-and-pick".

**Pair**: OMCR `/iterate-revision` (inner engine, one per strategy) + OMC `/oh-my-claudecode:ultraqa` (outer strategy explorer)

```bash
/oh-my-claudecode:ultraqa \
  "/iterate-revision sections/discussion.tex --max-iter 3 --venue Nature" \
  --strategies "concise,detailed,narrative" \
  --selector reviewer-rating
```

What happens:

1. `/oh-my-claudecode:ultraqa` forks 3 parallel branches, each running `/iterate-revision` with a different `style` directive in the brief (`concise` / `detailed` / `narrative`).
2. Each branch runs OMCR's normal writer ↔ reviewer loop up to `--max-iter 3` and produces a DONE verdict + a final section file.
3. `--selector reviewer-rating` instructs `/ultraqa` to compare the three DONE versions on `@reviewer`'s composite severity score (lowest issue count wins, ties broken by token count).
4. The winning branch's section file is committed to disk; the other two branches' outputs are surfaced in `.omc/ultraqa-<run-id>/branches/` for the user to inspect.

**Why this composition**: OMCR engines are designed to converge on one output — that is the right shape when you trust your inputs. When you don't trust your *style choice*, the right move is to try several styles in parallel and let an arbiter pick. `/ultraqa` is the arbiter; OMCR's `@reviewer` is the scoring function. The fact that they share no state is why this works: each branch's reviewer has its own MEMORY.md and verdict; ultraqa just compares the verdicts.

**Links**: [`/iterate-revision` SKILL.md](../skills/iterate-revision/SKILL.md) · [`/oh-my-claudecode:ultraqa`](https://github.com/Yeachan-Heo/oh-my-claudecode#features) · [Orchestration-Comparison §A row 3](Orchestration-Comparison.md#a--task--tool-matrix)

### Recipe 4 — Autonomous paper drive with `/autopilot` wrapping `/supervisor-drive`

**When**: greenfield project, no `paper.json` yet, you want the drive to run end-to-end with OMC's budget-tracking + structured decision logging on top of OMCR's domain-aware bottleneck ranker. The recommended composition for any week-long autonomous run.

**Pair**: OMCR `/supervisor-drive --auto` + OMC `/oh-my-claudecode:autopilot`

```bash
# Step 1 — clarify the idea (no code runs yet)
/oh-my-claudecode:deep-interview \
  "I want to test whether inter-subject correlation predicts learning gains in MOOC video viewers. \
   I have N=40 subjects, 6 videos, post-test scores."

# Step 2 — commit to OMCR scaffold (creates paper.json + manuscript skeleton + agent-memory)
/start-research

# Step 3 — drive autonomously, budget-tracked
/oh-my-claudecode:autopilot \
  "drive paper.json to submission_ready" \
  --inner-engine "/supervisor-drive --auto --max-iter 8 --budget-tokens 100000" \
  --max-budget 200000 \
  --decision-log .omc/decisions.jsonl
```

What happens:

1. Step 1's `deep-interview` removes ambiguity (testable hypothesis + evaluator) before any code runs. Output lands in `.omc/specs/deep-interview-<slug>.md`.
2. Step 2's `/start-research` lays down the OMCR substrate — `paper.json` with hypothesis pulled from Step 1, the LaTeX manuscript skeleton, empty `references.bib`, agent-memory directories for all 6 OMCR agents.
3. Step 3's `/autopilot` wraps `/supervisor-drive`. OMCR's supervisor surveys the 5 state files (`paper`, `reviews`, `citations`, `figures`, `rebuttals`), applies its 8-rule priority ranker, and dispatches one engine. Autopilot's `--max-budget 200000` is the outer ceiling; OMCR's `--budget-tokens 100000` is the inner ceiling.
4. OMCR's 6 safety gates (HypothesisChange, NewCitation, NewExperiment, StructuralRewrite, BudgetExceeded, CriticalIssue) still fire inside the autopilot wrapper. Autopilot pauses when OMCR's gate is tripped; the user types the gate's confirmation phrase; autopilot resumes.
5. Every engine dispatch is recorded once in OMCR's `_run-log.jsonl` (with `run_id`) and once in OMC's `.omc/decisions.jsonl` (with autopilot's decision shape). Cross-referencing the two gives a full audit trail.

**Why this composition**: OMCR's supervisor knows what to do next (it understands `paper.json.sections[name].status` and the citation queue); OMC's autopilot knows how to bound the cost and log the structured decisions. Neither layer alone covers both responsibilities. The composition is legal because they share no state — autopilot's wrapping is purely an outer execution context, not a state merge. See [Autonomous-Drive § Composability](Autonomous-Drive.md#composability-with-omcs-autopilot-and-ralph) for the architectural justification.

**Links**: [`/supervisor-drive` SKILL.md](../skills/supervisor-drive/SKILL.md) · [`/oh-my-claudecode:autopilot`](https://github.com/Yeachan-Heo/oh-my-claudecode#features) · [Autonomous-Drive deep dive](Autonomous-Drive.md) · [Orchestration-Comparison §A row 8](Orchestration-Comparison.md#a--task--tool-matrix)

### Recipe 5 — Cross-checking a critical claim with `@verifier`

**When**: `/iterate-revision` just returned DONE on `sections/discussion.tex`, but the central claim is bold (e.g., "X causes Y in the population P"). You want OMC's `@oh-my-claudecode:verifier` to sanity-check the claim against the manuscript's own data and methods sections before you submit — not as part of the revision loop, but as a one-shot audit afterward.

**Pair**: OMCR `/iterate-revision` (already complete) + OMC `@oh-my-claudecode:verifier` (one-shot audit)

```text
@oh-my-claudecode:verifier check the central claim in sections/discussion.tex
against the data described in sections/methods.tex and the results reported
in sections/results.tex.

Be specific about which sentence in the discussion makes the claim, which
sentences in methods describe the data the claim depends on, and which
sentences in results report the supporting numbers. Flag any claim where:
  - the discussion's effect size is larger than results.tex reports
  - the discussion's generalization scope is wider than methods.tex's sample
  - the discussion implies causal direction that results doesn't establish
  - the discussion cites a figure that doesn't actually show what's claimed

Output a per-claim table: claim text | supporting sentences | verdict (SUPPORTED | OVER-CLAIM | UNSUPPORTED).
```

What happens:

1. `@oh-my-claudecode:verifier` is a one-shot OMC agent — no loop, no wrapper.
2. It reads the three section files independently, cross-references claim-to-evidence chains, and emits a per-claim verdict table.
3. If any `OVER-CLAIM` or `UNSUPPORTED` rows land, the user re-runs `/iterate-revision sections/discussion.tex` with the verifier's findings pasted into the task brief (or wraps the next revision in Recipe 1's ralph variant for autonomous retry).

**Why this composition**: OMCR's `@reviewer` gates revision *quality* (clarity, tone, severity-flagged structural issues) but is not purpose-built for internal logical consistency between sections. OMC's `@verifier` is — it's a fresh-evidence agent that reads only what's in front of it, with no state coupling to the writer. Using it as a one-shot post-revision audit catches the over-claim class of bugs that the writer-reviewer loop will systematically miss (because the writer's MEMORY.md and the reviewer's MEMORY.md both grew from the same project context).

**Links**: [`/iterate-revision` SKILL.md](../skills/iterate-revision/SKILL.md) · [`@oh-my-claudecode:verifier`](https://github.com/Yeachan-Heo/oh-my-claudecode#features) · [Orchestration-Comparison §A row 5](Orchestration-Comparison.md#a--task--tool-matrix)

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
