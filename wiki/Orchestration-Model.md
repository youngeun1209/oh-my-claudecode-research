# Orchestration model

OMXR+ ships a small set of orchestration primitives that engine
skills (`$iterate-revision`, `$literature-sweep`, `$respond-reviewer`,
`$figure-bake`, `$outline-expand`, `$supervisor-drive`) compose into
their workflows. This page explains the model so contributors can
author new engines without re-inventing the wheel and so users can
read `.omx/state/omxr/` confidently.

If you are a user and just want a single section revised by the
reviewer team, you do not need this page — pick the engine from
[Engines](Commands.md) and run it. This page is for people writing
engines or debugging a run log.

## The state store — `.omx/state/omxr/`

A flat directory inside the **user's project** (not the plugin
install). Contains five files:

| File | Purpose | Append-only? |
|---|---|---|
| `paper.json` | Manuscript progress: title, venue, hypothesis, per-section status + iter. | no |
| `reviews.json` | Append-only history of every `@reviewer` verdict. | yes |
| `citations.json` | BibTeX queue + verification states. | no |
| `figures.json` | Per-figure design / impl / critique status. | no |
| `_run-log.jsonl` | One JSON-per-line log of every engine invocation (start + end records). | yes |

**Flat layout** — no `logs/` subdirectory, no nested per-engine dirs.
The leading underscore on `_run-log.jsonl` sorts it to the top of `ls`
output as the only separation the layout needs. Rationale:
`.omx/omxr/agent-memory/<agent>/MEMORY.md` already adds one level of
nesting; adding a second tree under `omxr-state/` would double the
mental model for a single log file.

### Gitignore status

The whole `.codex/` directory is gitignored by OMXR's default. This
keeps per-user state — including any sensitive content engines might
accumulate in `paper.json` (working title, hypothesis) or
`citations.json` (paper queries with research-question context) — out
of the project's tracked tree. Users who want versioning can un-ignore
specific files in their own project's `.gitignore`; OMXR will not
do that for them.

### Schema versioning

Every JSON state file carries a `schema_version` field. OMXR ships
`"1"` (a JSON **string**, not int — so a future `"1.1"` bump can
remain semver-shaped). The string-versus-int choice mirrors how
`templates/journal-registry.json` already keys venues by string.

| Version | Meaning |
|---|---|
| `"1"`   | The shape documented on this page. |
| `"1.x"` | Additive change — new optional fields. Old readers ignore unknown fields. |
| `"2"`   | Breaking change — requires a migration runner. Deferred. |

When the orchestrate `state-read` primitive sees a `schema_version` it
does not recognize, it prints a warning and proceeds. There is no
auto-migration currently. If you maintain an engine, do not branch on
schema_version values that do not yet exist.

## The 4 primitives

Engine skills compose four small primitives that live under
`skills/orchestrate/phases/`. The orchestrate skill is **internal** —
not user-invocable, not in any command. Its only job is to keep state,
dispatch, evaluation, and loop counters honest so engines can be
written as small composition declarations instead of bespoke code.

| Primitive | One-liner | File |
|---|---|---|
| `state-read` | Read + validate + bootstrap one state JSON. | `skills/orchestrate/phases/01-state-read.md` |
| `dispatch`   | Invoke a persona subagent via the Agent tool with inlined prompt. | `skills/orchestrate/phases/02-dispatch.md` |
| `evaluate`   | Apply an engine-supplied verdict rule to last output + state. | `skills/orchestrate/phases/03-evaluate.md` |
| `loop`       | Run dispatch → evaluate → maybe-commit until verdict says stop. | `skills/orchestrate/phases/04-loop.md` |

A typical engine iteration looks like:

```
state-read(paper.json) -> paper_state
   for iter in 1..max_iter:
       dispatch(@paper-writer, "revise <section>", state_slice)
       dispatch(@reviewer,     "review <section>", state_slice)
       evaluate(verdict_rule, last_output, iter, max_iter)
       if verdict in {DONE, BLOCKED, HALT}: break
   loop primitive appends run start + end to _run-log.jsonl
```

The verdict is one of exactly four: `DONE`, `CONTINUE`, `BLOCKED`,
`HALT`. Engines do not invent new verdicts; if a new flow needs a
different exit signal, encode it into the `reason` string the
verdict carries.

## Cost model — post-hoc only

OMXR does not pre-flight token cost. The `loop` primitive records
**actual** `tokens_used` to `_run-log.jsonl` after each iteration. If
the engine passed a `budget_tokens` cap, the loop emits `HALT` **at
the iteration boundary** when cumulative usage exceeds the cap — never
mid-iteration. Worst-case overrun is one iteration's actual cost,
bounded by `max_iter` (default 3).

This is intentional. Pre-flight tokenization would require shipping a
tokenizer dependency (Python `tiktoken` or equivalent), which breaks
OMXR's "plain markdown + shell scripts" stance. A rough char-count
heuristic would be wrong often enough to either over-abort or
under-protect. Post-hoc is honest: the user sees what was actually
spent.

Phase 4 (`$supervisor-drive`, autonomous mode) is the right place to
add pre-flight estimation; cost-sensitive scheduling is its core value
prop, and the budget input on the loop primitive is already shaped to
accept it without API changes.

## Engine SKILL.md frontmatter — two new conventions

Engines (skills under `skills/` that compose orchestrate phases)
declare two new frontmatter fields beyond the existing
`name`/`description`:

### `writes:` — declares state-file mutation

```yaml
---
name: iterate-revision
description: ...
writes: [paper, reviews]
---
```

`writes:` is a list of state-file basenames (without `.json`) that this
engine mutates. The values are drawn from `{paper, reviews, citations,
figures, _run-log}`.

It is **convention only** — no runtime enforcement. The value is to
make ownership greppable for review:

```bash
grep -r "^writes:" skills/*/SKILL.md
```

…tells you exactly which engines touch `citations.json`, etc. Append-only
files (`reviews`, `_run-log`) still appear in `writes:` if the engine
appends.

### `cost_estimate_tokens:` — coarse budget hint

```yaml
---
name: iterate-revision
description: ...
writes: [paper, reviews]
cost_estimate_tokens: 25000
---
```

A single integer: a rough per-run token estimate the
`$supervisor-drive` scheduler uses for budget gating. Phase 3 adds a
rolling median of the engine's last 5 actuals on top of this constant,
multiplied by 1.25 padding. The constant only matters for cold-start —
once 5 actuals exist for the engine, they dominate.

Optional for engines that will never run under `$supervisor-drive`.
Recommended otherwise.

See [Specializing](Specializing.md) for the full list of
frontmatter fields including these two.

## Engines are leaves — no engine-to-engine calls

A hard architectural rule: **engines never invoke other engines**.
`$iterate-revision` does not call `$literature-sweep`. `$figure-bake`
does not call `$respond-reviewer`. They are leaves of the orchestration
tree.

Only `$supervisor-drive` (the autonomous engine, Phase 3) may sequence
engines — and even it does so by **re-evaluating state between every
step**, never by invoking an engine from inside another engine's
dispatch plan. This keeps:

- Each engine's verdict logic auditable from one place.
- Composition explicit and visible in `_run-log.jsonl` (one engine =
  one run record).
- Cost predictable — no nested-engine surprise loops.

The forward-references for this rule:

- `wiki/Engine-Iterate-Revision.md` (Phase 1) — first leaf engine.
- `wiki/Autonomous-Drive.md` (Phase 3) — the only engine allowed to
  sequence others. Will document the re-evaluate-between-steps
  invariant in detail.

(Both pages are deferred — they ship with their respective phases.)

## Worked composition example

A hypothetical `iterate-revision` engine's SKILL.md would declare its
imports like this:

```markdown
---
name: iterate-revision
description: Revise a section against the reviewer team until DONE.
writes: [paper, reviews]
cost_estimate_tokens: 25000
---

# $iterate-revision

## Composition

This engine imports the following primitives from `skills/orchestrate/`:
- `phases/01-state-read.md` — read `paper.json` to find the section's
  current `iter`, `status`, `last_review_id`; bootstrap `reviews.json`
  if missing.
- `phases/02-dispatch.md` — dispatch `@paper-writer`, then `@reviewer`,
  per iteration.
- `phases/03-evaluate.md` — verdict rule: `severity-threshold` with
  `blocking_severities = ["critical"]`, `must_clear_severities =
  ["critical", "major"]`.
- `phases/04-loop.md` — `max_iter: 3`, `on_iter_end: "git-commit"`.

## Phases

1. **Phase 1 — Precheck.** ... (engine-specific guards: `[TBD:` scan, etc.)
2. **Phase 2 — Compose dispatch plan.** Build the writer + reviewer
   dispatch steps with the right `task_brief` and `state_slice`.
3. **Phase 3 — Run loop.** Hand off to the orchestrate loop primitive.
4. **Phase 4 — Report.** Render the loop's return value for the user.
```

The point: the engine's own phase files own the **domain logic**
(precheck rules, brief templating, report formatting). The orchestrate
phases own the **mechanics** (state IO, dispatch, verdict, counters).
You should be able to read an engine's SKILL.md and know exactly what
state it touches and what its dispatch plan looks like, without
reading any orchestrate phase files.

## Serial execution — current assumption

OMXR runs **one engine at a time** per project. There is no lock
file in `.omx/state/omxr/`. The realistic concurrency vector is
Phase 3's autonomous supervisor scheduling overlapping subagents, and
the orchestration roadmap defers a lock mechanism to that phase.
A solo researcher with one Codex session cannot run two engines
simultaneously through the normal entrypoints — skills are
turn-based — so the serial assumption holds for the current audience.

`_run-log.jsonl` records start + end timestamps for every run. That is
the only race detection OMXR currently provides. If you see overlapping
`started`/`ended` windows across two runs in the same project, you are
in a regime OMXR does not support.

## See also

- [Configuration](Configuration.md) — the `## Research stack` block
  fields, including the new `data_root` for `$figure-bake`.
- [Specializing](Specializing.md) — preset authoring, including the
  `writes:` and `cost_estimate_tokens:` frontmatter conventions.
- `develop/phase-0-primitives.md` — internal design doc; full
  schemas + behavior contracts for each primitive.
- `develop/decisions-summary.md` — all 21 locked orchestration
  decisions across Phase 0–3.
- `develop/example-state/README.md` — canonical empty + populated
  state-file shapes.
- `wiki/Engine-Iterate-Revision.md` (forthcoming with Phase 1).
- `wiki/Autonomous-Drive.md` (forthcoming with Phase 3).
