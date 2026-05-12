# Phase 3 — Agent memory + orchestration state

Two infrastructure scaffolds in one phase: agent memory directories (so
the 6 personas have a persistence target on first run) and the
orchestration state directory (so the v0.2+ engines have empty state
files to read).

## Part A — Agent memory (6 personas)

Create `.claude/agent-memory/<agent>/` for each of the 6 core agents and seed each with a `MEMORY.md` from the canonical template at `templates/MEMORY.template.md` (in the plugin root).

Agents to scaffold:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

For each agent:

- If `.claude/agent-memory/<agent>/MEMORY.md` already exists, **skip** — do not overwrite.
- Otherwise, copy `templates/MEMORY.template.md` (from the plugin root) to that path.

Always use the **canonical template** here. Preset-specific templates (e.g. `examples/neuro-fmri/memory-templates/<agent>/MEMORY.md`) are applied later by `/start-research`'s preset-overlay phase — only if the user selects a preset AND the existing `MEMORY.md` is still byte-identical to the canonical template (i.e. user hasn't started writing in it).

Record what was created vs. skipped so phase 6 can summarize.

### Why preset templates aren't applied here

`/omcr-setup` runs without knowing the user's domain. Applying a neuro-fMRI memory template to a project that turns out to be astrophysics would create misleading context. Canonical-template seeding is always safe; preset application is opt-in via `/start-research`.

## Part B — Orchestration state (5 state files)

Scaffold the `.claude/omcr-state/` directory and seed it with the four
empty JSON state files plus an empty append-only run log. These are the
files the v0.2+ orchestration engines (`/iterate-revision`,
`/literature-sweep`, `/respond-reviewer`, `/figure-bake`,
`/outline-expand`, `/supervisor-drive`) read on every run.

Files to scaffold (flat layout — no `logs/` subdirectory, per Phase 0
decision §1):

- `.claude/omcr-state/paper.json`
- `.claude/omcr-state/reviews.json`
- `.claude/omcr-state/citations.json`
- `.claude/omcr-state/figures.json`
- `.claude/omcr-state/_run-log.jsonl`

### Steps

1. **mkdir.** `mkdir -p .claude/omcr-state/` (idempotent).

2. **Copy the four JSON files.** For each of `paper`, `reviews`,
   `citations`, `figures`:
   - If `.claude/omcr-state/<name>.json` already exists, **skip** — do
     not overwrite. State that the user has already accumulated must
     never be clobbered by a re-run of `/omcr-setup`.
   - Otherwise, copy `<plugin_root>/develop/example-state/<name>.json`
     to `.claude/omcr-state/<name>.json`. `$CLAUDE_PLUGIN_ROOT` gives
     the plugin root.

3. **Touch the run log.** If `.claude/omcr-state/_run-log.jsonl` does
   not exist, create it as an empty file (zero bytes). If it already
   exists, leave it alone — it is append-only across runs.

4. **Record outcomes.** For each of the 5 files, record one of
   `{created, skipped-already-existed}` so phase 6 can summarize. The
   `omcr-state` block in the final report sits next to the
   `agent-memory` block.

### Why bootstrap state here instead of lazily on first engine run

The `skills/orchestrate/phases/01-state-read.md` primitive does have a
lazy-bootstrap branch (it writes an empty schema on missing file), but
doing it here too means:

- A user who runs `/omcr-setup` then opens `.claude/omcr-state/` sees
  the canonical schema immediately — useful for hand-editing
  `paper.json` before invoking any engine.
- The 5 files exist in a single commit-able state when the user adds
  `.claude/` to version control (some users do, despite our default
  gitignore).
- First engine run sees a populated dir, so its run log appends to an
  existing empty file rather than racing the bootstrap.

Idempotency is preserved either way — both paths use existence checks
before writing.

### What this phase explicitly does NOT do

- Does NOT populate `paper.json` with a working title / hypothesis /
  venue. Those fields stay `null` here; `/start-research` fills them
  during its interview phase.
- Does NOT migrate state between schema versions. v0.2 ships only
  `"1"`; future migration is deferred per Phase 0 decision §2.
- Does NOT create `.claude/omcr-state/logs/`. Flat layout only.
