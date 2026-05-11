# OMC Tool Reference (research workflow mapping)

This page maps OMC's 47 MCP tools to research workflow stages, so you can find the right OMC primitive for the job. **Assumes OMC is installed alongside OMCR** — see [With OMC](With-OMC.md) for install.

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

Currently (v0.1.x), OMCR's 5 agents are prompt-only — they don't directly invoke OMC's MCP tools. But Claude Code's session-level tool list includes both OMCR's hooks and OMC's MCP tools when both are installed, so:

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
