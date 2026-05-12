# OMC Tool Reference (research workflow mapping)

This page maps OMC's 47 MCP tools to research workflow stages, so you can find the right OMC primitive for the job. **Assumes OMC is installed alongside OMCR** — see [With OMC](With-OMC.md) for install. For OMC orchestration skills (`ralph`, `team`, `autopilot`, `ralplan`, …) and how to combine them with OMCR's agents, see [With-OMC § Recipes](With-OMC.md#recipes--pairing-omcr-with-omc) — this page covers MCP tools only.

If you only have OMCR installed, none of these tools are available. OMCR's standalone behavior is documented in [Standalone Usage](Standalone-Usage.md).

## Mental model

OMC's MCP tools fall into 8 families:

| Family | Tools | Best for |
|---|---|---|
| `wiki_*` | 8 | Literature anchor schema — searchable bibliography |
| `notepad_*` | 6 | Scratch / hypothesis register / priority working memory |
| `state_*` | 5 | Experiment-run registry — start, status, results across runs |
| `project_memory_*` | 4 | Per-project persistent memory operations (in-session) |
| `shared_memory_*` | 5 | Cross-session shared state (user-level, multi-project) |
| `lsp_*` | 10 | Code intelligence (used by `@verifier`, `@analysis-implementer`) |
| `trace_*` | 2 | Causal tracing surfaces (used by `@tracer`, `/trace`) |
| Misc | 7 | python_repl, session_search, ast_grep_*, deepinit_manifest, list_omc_skills, etc. |

## Tool-by-tool reference (research lens)

### Literature management — `wiki_*`

| Tool | What it does | Use when |
|---|---|---|
| `wiki_add` | Register a new entry (paper, fact, citation) with tags + content | Adding a citation you want to reuse across the project |
| `wiki_query` | Search wiki entries by keyword / tag / content | "Find papers about X that I've already cited" |
| `wiki_ingest` | Bulk-ingest from a file or URL | Importing a literature export (BibTeX, RIS, CSV) |
| `wiki_list` | List all entries (or filter by tag) | Audit what you've already collected |
| `wiki_read` | Read a specific entry by ID | Pull up a remembered citation |
| `wiki_lint` | Validate entries against schema | Pre-submission quality check on the bibliography |
| `wiki_delete` | Remove an entry | After deciding a citation is not relevant |

**Research use case:** Replace ad-hoc literature lists in `supervisor/MEMORY.md` with a structured wiki. `@supervisor` calls `wiki_add` when registering a new anchor paper, `wiki_query` when checking whether something's already cited.

### Hypothesis / working memory — `notepad_*`

| Tool | What it does | Use when |
|---|---|---|
| `notepad_write_manual` | Write a manual scratch note | Capturing a quick fact you want to remember this session |
| `notepad_write_working` | Write to working-memory channel | Capturing in-progress thinking (overwritable) |
| `notepad_write_priority` | Write to priority channel | Capturing a high-priority "do this next" item |
| `notepad_read` | Read all entries | Reviewing current scratch notes |
| `notepad_stats` | Get count / age stats per channel | Audit before pruning |
| `notepad_prune` | Drop old entries | Clean up at end of session |

**Research use case:** Hypothesis register. Use `notepad_write_priority` for active hypotheses being tested, `notepad_write_working` for working notes that change frequently, `notepad_write_manual` for facts to remember.

### Experiment runs — `state_*`

| Tool | What it does | Use when |
|---|---|---|
| `state_write` | Create / update a named state entry (mode, status, JSON payload) | Starting or finishing an experiment run |
| `state_read` | Read a state entry by name | Checking the status of a previous run |
| `state_get_status` | Quick "is this mode active?" check | Conditional logic in skills / commands |
| `state_list_active` | List all currently-active modes | Audit what's in progress |
| `state_clear` | Clear a mode (terminal cleanup) | Closing out an experiment cycle |

**Research use case:** Experiment-run registry. Each `state_write` call corresponds to a run: `state_write(mode="experiment-R3-perm", session_id="20260510", payload={"n_perms": 10000, "p_value": 0.023, "completed_at": "..."})`. Later, `state_read` and `state_list_active` give you a cross-run audit trail.

### Project memory — `project_memory_*`

| Tool | What it does | Use when |
|---|---|---|
| `project_memory_write` | Write a memory entry to project memory | Inside an agent, when you want OMC to remember beyond the session |
| `project_memory_add_directive` | Add a structured directive | Imposing a project rule ("always use seed=42") |
| `project_memory_add_note` | Add a note (less structured) | General observations |
| `project_memory_read` | Read all project memory | At session start, manually |

**Research use case:** OMC's structured alternative to OMCR's `MEMORY.md` files. Less portable (lives in OMC's storage), more queryable (structured). If you use OMC, consider whether to migrate from OMCR's flat-markdown memory to OMC's structured memory — or keep both (OMCR memory for portability / archival, OMC memory for in-session queryability).

### Shared memory — `shared_memory_*`

Like `project_memory_*` but spans multiple projects. Useful for user-level facts that apply everywhere: preferred citation style, default plotting library, hardware specs.

### Code intelligence — `lsp_*`

LSP-backed code intelligence — invoked by `@verifier` (for "fresh diagnostics" verification) and `@analysis-implementer` (for refactoring / renames). Not directly research-flavored, but essential for analysis-script reproducibility.

| Tool | What it does |
|---|---|
| `lsp_diagnostics` | Diagnostics for a file |
| `lsp_diagnostics_directory` | Diagnostics for a directory (used by `@verifier`) |
| `lsp_hover` | Hover info for a symbol |
| `lsp_goto_definition` | Jump to definition |
| `lsp_find_references` | Find all references |
| `lsp_rename` | Rename across the project |
| `lsp_document_symbols` | Symbol outline of a file |
| `lsp_workspace_symbols` | Symbol search across workspace |
| `lsp_code_actions` / `lsp_code_action_resolve` | Auto-fix actions |
| `lsp_servers` | List active LSPs |

**Research use case:** Before declaring an analysis pipeline complete, `@analysis-implementer` (or `@verifier` from OMC) runs `lsp_diagnostics_directory` to confirm no broken imports, no undefined variables — the equivalent of a TypeScript build pass for Python.

### Causal tracing — `trace_*`

| Tool | What it does |
|---|---|
| `trace_summary` | Summarize a trace (evidence-driven causal analysis) |
| `trace_timeline` | Per-step timeline of a trace |

**Research use case:** Used by `@tracer` and `/oh-my-claudecode:trace`. Surfaces causal-analysis runs as inspectable artifacts. Useful when results need to be defended in a Methods / Discussion section — the trace timeline is the audit trail for "why we concluded X."

### Stateful Python REPL — `python_repl`

A persistent Python kernel running across multiple tool calls. Variables loaded once stay alive; subsequent calls reuse the data.

**Research use case:** Replace one-shot Python scripts with a stateful session. Load your processed dataset once, then run dozens of analyses interactively without re-loading. Essential for `@scientist`'s statistical workflow.

### Session search — `session_search`

Search prior Claude Code conversations.

**Research use case:** "What did we decide about parameter X two weeks ago?" Replaces the "scroll through 5 sessions" problem. Especially useful with `@supervisor` to recover historical framing decisions.

### Structural code search — `ast_grep_*`

AST-grep based search / replace. More precise than regex.

**Research use case:** Refactoring an analysis pipeline (e.g., renaming a function across the codebase, finding all call sites of a specific scipy method). Used by `@analysis-implementer` for non-trivial code edits.

### Misc

- `deepinit_manifest` — DeepInit manifest reader (OMC-specific bootstrap)
- `list_omc_skills` — List OMC's installed skills
- `load_omc_skills_global` / `load_omc_skills_local` — Load skill catalogs

## How OMCR-side agents can call OMC tools

Currently (v0.1.x), OMCR's 6 agents are prompt-only — they don't directly invoke OMC's MCP tools. But Claude Code's session-level tool list includes both OMCR's hooks and OMC's MCP tools when both are installed, so:

- A user can ask `@analysis-implementer` to "use python_repl to test the spin-test" and the agent will use OMC's MCP tool naturally.
- A user can ask `@supervisor` to "search session history for our decision about parameter k" and the agent will use `session_search`.

In OMCR v0.2 (per the project's v0.2 backlog), agents may be retrofitted to use the "detect-and-enhance" pattern — automatically use OMC's tools when available, fall back to plain instructions when not.

## Quick lookup — common research tasks → OMC tool

| Task | Tool |
|---|---|
| Register a new citation | `wiki_add` |
| Search the bibliography | `wiki_query` |
| Track a hypothesis as "currently testing" | `notepad_write_priority` |
| Log an experiment run with parameters + result | `state_write` |
| Audit all experiment runs in this project | `state_list_active` + `state_read` |
| Run a one-off statistical test interactively | `python_repl` |
| Verify analysis code has no broken imports | `lsp_diagnostics_directory` |
| Recall a decision from a prior session | `session_search` |
| Inspect a causal-tracing run's evidence chain | `trace_timeline` |
| Rename a function across the analysis pipeline | `lsp_rename` or `ast_grep_replace` |

## OMC tools that compose with each OMCR engine

The mapping above is **OMC tool → research stage**. This section is the **inverse map**: per OMCR engine, which OMC skills, agents, and MCP tools compose well with it? Use this when you have already picked an OMCR engine and want to know "what OMC piece can I wrap around it / call before it / call after it?"

This is a curated, opinionated list — not every OMC piece is mentioned. For the full catalog of OMC skills (`ralph`, `team`, `autopilot`, `ultrawork`, `ultraqa`, `ralplan`, `deep-interview`, `autoresearch`, `verifier`, `tracer`, `document-specialist`, …), see [upstream OMC docs](https://github.com/Yeachan-Heo/oh-my-claudecode). For worked recipes that turn these compositions into copy-pasteable commands, see [With-OMC § Recipes](With-OMC.md#recipes--pairing-omcr-engines-with-omc-orchestrators-v04).

### `/iterate-revision` (OMCR engine)

Single-section revise-to-ready engine. Loops `@paper-writer` ↔ `@reviewer` until DONE / BLOCKED / HALT. Composes well with:

| OMC piece | Composition role | Why |
|---|---|---|
| `/oh-my-claudecode:ralph` | outer retry loop | Wrap `/iterate-revision` to retry until an independent verifier (not OMCR's `@reviewer`) confirms DONE. See [With-OMC Recipe 1](With-OMC.md#recipe-1--iterate-revision-wrapped-in-ralph-for-verifier-gated-revision). |
| `/oh-my-claudecode:ultraqa` | strategy explorer | Try N revision styles (concise / detailed / narrative) in parallel; pick best by reviewer rating. See [With-OMC Recipe 3](With-OMC.md#recipe-3--multi-style-revision-via-ultraqa). |
| `@oh-my-claudecode:verifier` | post-loop audit | One-shot cross-check after DONE: does the central claim hold against methods + results? See [With-OMC Recipe 5](With-OMC.md#recipe-5--cross-checking-a-critical-claim-with-verifier). |
| `@oh-my-claudecode:tracer` | debug instrumentation | When the loop keeps returning HALT, instrument the next run for per-phase timing + dispatched task-brief diffs. |
| `wiki_query` / `wiki_add` | context lookup | If `@literature-curator`'s MEMORY.md is sparse, the writer / reviewer can pull anchor citations from OMC's wiki during a revision iter. |
| `python_repl` | inline numerical check | When the reviewer flags a results table, an in-loop `python_repl` call can confirm / refute the number before the next iter. |

### `/literature-sweep` (OMCR engine)

Topic-to-bibliography engine. Dispatches `@literature-curator` over CrossRef/OpenAlex candidates, hard-gates every survivor through `verify-citation`, writes to `references.bib` + summary CSV. Composes with:

| OMC piece | Composition role | Why |
|---|---|---|
| `omc team N:literature-curator` | cross-session parallelism | When you need 50+ papers / week-long sweeps, OMC's tmux-backed team survives session restarts. OMCR's `--parallel 4` cap is in-session only. See [With-OMC Recipe 2](With-OMC.md#recipe-2--distributed-literature-sweep-via-omc-team-tmux-survives-session-restart). |
| `wiki_ingest` | external import | Bulk-import an existing BibTeX / RIS export into OMC's queryable wiki before sweeping; lets `@literature-curator` deduplicate against prior project work. |
| `wiki_add` | post-sweep registration | After `/literature-sweep` writes to `references.bib`, mirror the same entries into OMC's wiki via `wiki_add` for cross-project reuse. |
| `wiki_lint` | pre-submission QC | After all sweeps complete, `wiki_lint` validates the final entry shape (DOI present, year sane, no fabricated fields). |
| `@oh-my-claudecode:document-specialist` | deep-read pass | OMCR's curator extracts abstract-level metadata. For 5–10 anchor papers you actually want a deep read on, hand them to OMC's heavier-weight specialist. |

### `/respond-reviewer` (OMCR engine)

Reviewer-letter rebuttal engine. Classifies each comment, dispatches per-comment to the right specialist, assembles `rebuttal-letter.tex`. Composes with:

| OMC piece | Composition role | Why |
|---|---|---|
| `/oh-my-claudecode:ralph` | retry-until-no-overclaim | Wrap to retry until `@verifier` confirms the rebuttal claims actually match the manuscript changes. |
| `@oh-my-claudecode:verifier` | per-claim audit | OMCR's supervisor flags weak / disputed responses in phase 05, but doesn't independently audit the claim chain. `@verifier` can read the rebuttal letter + the cited manuscript sections and flag mismatches. |
| `/oh-my-claudecode:ralplan` | structural-comment replan | When the engine surfaces `structural` comments to user attention (the ethical gate), use `ralplan` for consensus-replanning the scope decision before manually answering. |
| `state_write` / `state_read` | per-letter audit trail | Log each rebuttal run as a structured experiment record alongside OMCR's own `rebuttals.json`. |
| `wiki_query` | citation-comment lookup | When a comment requests a missing reference, `wiki_query` checks if OMC's wiki already has it before dispatching `@literature-curator`. |

### `/figure-bake` (OMCR engine)

Single-figure design-to-PDF engine. 3-agent loop: `@figure-descriptor` → `@analysis-implementer` → `@reviewer`, with `cropfig` invoked per iter. Composes with:

| OMC piece | Composition role | Why |
|---|---|---|
| `/oh-my-claudecode:ultrawork` | parallel figure backlog | When `/todofig` reports 5+ figures missing or stale, fan out across them with `/ultrawork` calling `/figure-bake` per id. |
| `/oh-my-claudecode:ralph` | iterate until reviewer DONE | Wrap a single figure-bake to retry until the figure passes both OMCR's reviewer and an independent verifier on the rendered PNG. |
| `python_repl` | inline render debug | When the implementer's matplotlib code errors, `python_repl` keeps the session state alive so the next iter can resume without re-loading the dataset. |
| `@oh-my-claudecode:tracer` | render-pipeline debug | When `/figure-bake` returns BLOCKED on a Python traceback, `@tracer` instruments the next implementer dispatch for evidence-driven debugging. |
| `@oh-my-claudecode:scientist` | stats correctness | If the figure is a statistical plot (effect-size forest plot, CI ribbon, etc.), `@scientist` audits the math before the renderer hits the data. |

### `/outline-expand` (OMCR engine)

Map-reduce first-draft engine. One `@paper-writer` per section, fanned out in a single Agent-tool message, with shared `nomenclature.md` payload. Composes with:

| OMC piece | Composition role | Why |
|---|---|---|
| `/oh-my-claudecode:team` | cross-process parallelism | When the manuscript has 8+ sections and a single in-session parallel dispatch is too heavy, `omc team N:paper-writer` shards across tmux panes. |
| `/oh-my-claudecode:ultraqa` | per-section strategy explore | After `/outline-expand` produces first drafts, run `/ultraqa` per section to try N styles before settling. |
| `wiki_query` | per-section anchor pull | When a section's outline references "the Smith 2023 finding", `@paper-writer` can `wiki_query` it before drafting. |
| `notepad_write_priority` | hypothesis register | Pre-draft, log the section's argumentative claim to OMC's notepad so all parallel writers reference the same hypothesis. |

### `/supervisor-drive` (OMCR engine)

Autonomous orchestrator. The only OMCR engine allowed to chain other engines; re-evaluates state between every step. 6 safety gates, 8-rule priority ranker. Composes with:

| OMC piece | Composition role | Why |
|---|---|---|
| `/oh-my-claudecode:autopilot` | outer budget + decision log | Wrap `/supervisor-drive --auto` in `/autopilot` for budget tracking, structured decision log, and outer-loop recovery from engine exceptions. **The recommended composition for any week-long drive.** See [With-OMC Recipe 4](With-OMC.md#recipe-4--autonomous-paper-drive-with-autopilot-wrapping-supervisor-drive). |
| `omc team 1:supervisor` | cross-session persistence | When the drive will exceed a single Claude Code session (multi-day autonomous run), wrap `/supervisor-drive --auto` in an `omc team` pane so it survives session restarts. |
| `/oh-my-claudecode:ralplan` | between-drives consensus replan | After a halt on safety gate 4 (StructuralRewrite), use `ralplan` to consensus-replan the scope decision before resuming. |
| `@oh-my-claudecode:verifier` | post-drive audit | After `/supervisor-drive` returns `submission_ready = true`, run `@verifier` on the discussion-vs-methods-vs-results chain as a final cross-check before submission. |
| `@oh-my-claudecode:tracer` | halted-drive diagnosis | When `_run-log.jsonl` shows a halt on a specific engine, `@tracer` reads the run record + the engine's last brief and emits a causal diagnosis. |
| `state_*` MCP family | drive-event registry | Each safety-gate trip writes a state entry; `state_list_active` shows currently-stuck drives across all projects. |

### Cross-cutting MCP tools (compose with every engine)

Some OMC MCP tools are useful regardless of which OMCR engine you reach for:

| Tool | What it's good for |
|---|---|
| `wiki_query` | Pre-flight check: "have we already cited this paper?" — answer before any engine adds a new entry. |
| `python_repl` | Stateful Python kernel for any engine's analysis check; survives across the engine's iterations within one session. |
| `lsp_diagnostics_directory` | Run after any engine that touches code (e.g., `/figure-bake`'s implementer phase) to confirm no broken imports landed. |
| `session_search` | "What did we decide about parameter k two weeks ago?" — recall context any engine's persona might need. |
| `state_list_active` | Cross-engine audit: which OMCR / OMC modes are currently active across all your projects? |
| `notepad_write_priority` | Hypothesis register that survives across engines — `/iterate-revision` and `/respond-reviewer` should both reference the same priority hypothesis. |

## See also

- [With OMC](With-OMC.md) — install + 5 worked recipes pairing OMCR engines with OMC orchestrators.
- [Orchestration Comparison](Orchestration-Comparison.md) — the full task → tool matrix backing these inverse-map entries.
- [Commands](Commands.md) — OMCR engine command reference.
- [Autonomous Drive](Autonomous-Drive.md) — `/supervisor-drive` deep dive.
