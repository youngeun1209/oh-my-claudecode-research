---
name: orchestrate
description: Internal primitive skill — engine skills compose these four phases. Not invoked directly by the user. Provides state-read, dispatch, evaluate, and loop primitives over `.claude/omcr-state/` so that engines (`/iterate-revision`, `/literature-sweep`, `/respond-reviewer`, `/figure-bake`, `/outline-expand`, `/supervisor-drive`) can be expressed as a small composition declaration instead of bespoke code.
---

# Orchestrate (internal primitive)

This skill ships the four primitives every OMCR engine depends on. It is
**not** something a user invokes directly — there is no `/orchestrate`
command and there should never be one. Engines (the user-facing skills
listed above) import its phase files and compose them.

If you are reading this because Claude Code's skill auto-discovery
surfaced it: please pick the engine you actually wanted to run, e.g.
`/iterate-revision` for revising a section against a reviewer.

**When this skill's phase files are referenced from another skill, follow them exactly as written. Do not re-derive behavior from the primitives doc — that doc is the design source; these phase files are the implementation contract.**

## The 4 primitives

| # | Primitive | Purpose | File |
|---|---|---|---|
| 1 | `state-read` | Read + validate + bootstrap a state JSON under `.claude/omcr-state/`. | [`phases/01-state-read.md`](phases/01-state-read.md) |
| 2 | `dispatch`   | Invoke a persona subagent via the Agent tool with inlined prompt. | [`phases/02-dispatch.md`](phases/02-dispatch.md) |
| 3 | `evaluate`   | Apply an engine-supplied verdict rule to the last output + state. | [`phases/03-evaluate.md`](phases/03-evaluate.md) |
| 4 | `loop`       | Drive dispatch → evaluate → repeat with `max_iter` and budget safeties. | [`phases/04-loop.md`](phases/04-loop.md) |

Each phase is short by design — engines do the domain work, the
primitives just keep state, dispatch, and counters honest.

## The state store

Five files under `.claude/omcr-state/` in the user's project. Layout is
flat — no `logs/` subdirectory — per Phase 0 decision §1.

| File | Owner-by-convention | Append-only? |
|---|---|---|
| `paper.json` | engines + `/omcr-setup` + `/start-research` | no |
| `reviews.json` | engines that dispatch `@reviewer` | yes |
| `citations.json` | `@literature-curator` + `verify-citation` skill | no |
| `figures.json` | engines that dispatch `@figure-descriptor` + `cropfig` | no |
| `_run-log.jsonl` | every engine (every run start + completion) | yes |

`schema_version` is a JSON string (`"1"` for v0.2). On mismatch the
primitive warns and proceeds — there is no migration runner yet. See
Phase 0 decision §2 for the rationale and the deferred-to-v0.5 plan.

Full per-field documentation and populated examples live in:

- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — schema reference + populated examples
- [`../../develop/phase-0-primitives.md`](../../develop/phase-0-primitives.md) — original design doc

Ownership is **convention only** — there is no runtime enforcement.
Engines declare what they write via a `writes:` frontmatter field on
their SKILL.md (see "Composition contract" below).

## Composition contract — how an engine uses this skill

An engine skill (e.g. `skills/iterate-revision/SKILL.md`) must:

1. **List the orchestrate phases it imports** in its `## Composition`
   section. Example:

   ```markdown
   ## Composition

   This engine imports the following primitives from `skills/orchestrate/`:
   - `phases/01-state-read.md` — read `paper.json` + `reviews.json`
   - `phases/02-dispatch.md`   — dispatch `@paper-writer`, `@reviewer`
   - `phases/03-evaluate.md`   — verdict rule defined in `phases/04-evaluate.md` of this engine
   - `phases/04-loop.md`       — `max_iter` default 3, `on_iter_end: git-commit`
   ```

2. **Declare `writes:` in frontmatter** — list the state files this
   engine mutates (e.g. `writes: [paper, reviews]`). Reviewers grep
   `writes:` across `skills/*/SKILL.md` to audit which engines touch
   which files. Append-only files (`reviews`, `_run-log.jsonl`) still
   require declaration if the engine appends.

3. **Declare `cost_estimate_tokens:` in frontmatter** (optional but
   recommended for Phase 3 autonomous mode) — a coarse constant the
   `/supervisor-drive` scheduler uses for budget gating. Phase 3
   decision §6 adds rolling-median actuals on top.

4. **Provide a verdict rule.** The engine's own phase files contain
   the verdict-rule spec; `orchestrate/phases/03-evaluate.md` is the
   primitive that applies it. The rule is passed in as data; the
   primitive does not know engine-specific logic.

5. **Never call another engine.** Engines are leaves (Phase 2 decision
   §5, Phase 3 decision §3). If composition between engines is needed,
   `/supervisor-drive` is the only thing that may chain — and it
   re-evaluates state between every step rather than invoking engines
   from inside engines.

## Cost model

Each `dispatch` is one Agent-tool invocation. Engines should budget
`max_iter * len(dispatch_plan)` calls. The `loop` primitive records
actual `tokens_used` to `_run-log.jsonl` after each iteration. There
is no pre-flight tokenizer (Phase 0 decision §6) — `budget_tokens` is
a post-hoc cap that triggers HALT at the iteration boundary if
cumulative usage exceeds the cap.

## Safety invariants

- **Serial execution only** (Phase 0 decision §4). v0.2 does not ship
  a lock file. One engine at a time per project.
- **`max_iter` is hard.** The loop never silently exceeds it — when
  reached without DONE/BLOCKED, the loop emits HALT and exits cleanly.
- **Dispatch errors break the loop.** If the Agent tool errors mid-run,
  the loop emits BLOCKED and the partial state is already on disk.
- **State persists across interruption.** A user Ctrl-C leaves
  `.claude/omcr-state/*.json` in a consistent state because each
  primitive writes atomically (write-tmp + rename).

## When to extend vs. when to fork

Add a phase to `orchestrate/phases/` only when **every** engine would
benefit. Engine-specific logic (e.g. "scan for `[TBD:` markers" from
`/iterate-revision` Phase 0 decision §1.2) goes in that engine's own
phase files. The four primitives here should stay at four for v0.2.

If a fifth primitive looks tempting (e.g. "parallel dispatch fanout"),
that is a Phase 3 concern — the autonomous supervisor is the only
caller that can benefit, and concurrency is deferred per Phase 0
decision §4.

## See also

- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — public-facing pattern doc
- [`../../develop/decisions-summary.md`](../../develop/decisions-summary.md) — all 21 locked decisions
- `wiki/Specializing.md` — preset authoring (includes `writes:` and `cost_estimate_tokens:` frontmatter conventions)
