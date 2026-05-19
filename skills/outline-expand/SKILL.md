---
name: outline-expand
description: Map-reduce engine — given an outline file and a `paper.json`, draft N sections in parallel by dispatching `@paper-writer` once per section in a single Agent-tool batch, then assemble the prose into each section's `paper.json.sections[name].path`. Passes a shared `nomenclature.md` payload to every dispatch (Phase 2 decision §4) so parallel writers share terminology. After merge, emits a non-blocking `terminology-drift.md` lint artifact listing terms that disagree across sections. First drafts only — does **not** call `/iterate-revision`. Safe to re-run; safe to scope with `--sections`.
writes: [paper]
cost_estimate_tokens: 40000
---

# /outline-expand

This engine is OMCR's map-reduce shape: one outline in, N first-draft sections out, one Agent-tool dispatch per section, all dispatched in a single message so Claude Code's runtime fans them out in parallel. It is the second-simplest engine after `/iterate-revision` — there is no loop and no reviewer; the verdict is "we wrote the files we said we would."

If you are reading this because Claude Code's skill auto-discovery surfaced it: invoke it via `/outline-expand <outline-path>`. Do not hand-edit the manuscript sections or `.claude/omcr-state/paper.json` while a run is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
/outline-expand <outline-path> [--sections <list>] [--max-iter-per-section N]
```

| Flag | Default | Purpose |
|---|---|---|
| `--sections` | all sections discovered in the outline whose `paper.json.sections[name].status` is not `approved` | Comma-separated subset to draft. Explicit names override the "already drafted" early-skip but never the `approved` guard (use `--sections` + manual status reset to redo an approved section). |
| `--max-iter-per-section` | `1` (unused currently) | Reserved for now `--auto-iterate`. This engine produces first drafts only. |

Examples:
- `/outline-expand outline.md` — draft every not-yet-approved section listed in the outline.
- `/outline-expand outline.md --sections introduction,methods` — draft only those two.
- `/outline-expand manuscript/outline.tex --sections results` — single section out of a LaTeX outline.

## The shape

```
phase 01 — precheck     (parse outline, resolve manuscript_root, decide section set)
phase 02 — map          (build N task briefs, dispatch @paper-writer × N in one message)
phase 03 — reduce       (write each prose to its section file, update paper.json,
                         run terminology drift lint, emit terminology-drift.md)
phase 04 — finalize     (user summary, suggest /iterate-revision per section,
                         append summary line to _run-log.jsonl)
```

There is no loop. Each phase runs once. The orchestrate `loop` primitive is **not** used by this engine — `loop` is for engines that iterate dispatch → evaluate → maybe-continue, which `/outline-expand` does not. Instead, phase 02 uses `orchestrate/phases/02-dispatch.md` directly, N times, in a single message.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — Precheck.** Read [`phases/01-precheck.md`](phases/01-precheck.md).
2. **Phase 2 — Map.** Read [`phases/02-map.md`](phases/02-map.md).
3. **Phase 3 — Reduce.** Read [`phases/03-reduce.md`](phases/03-reduce.md).
4. **Phase 4 — Finalize.** Read [`phases/04-finalize.md`](phases/04-finalize.md).

## Composition

This engine imports the following primitives from `skills/orchestrate/`:

- [`phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — read `paper.json` once in phase 01 (bootstrap if missing). The engine carries the parsed dict through phases 02–04 rather than re-reading.
- [`phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — invoked N times in phase 02 (one `@paper-writer` per section). All N invocations are emitted in a single message; Claude Code's Agent tool fans them out in parallel.

This engine **does not** use the `loop` primitive (`phases/04-loop.md`) — there is no iteration. It **does not** use the `evaluate` primitive (`phases/03-evaluate.md`) — there is no reviewer, no severity rule, no verdict. Phase 03 writes files and lints terminology; phase 04 reports stats. Both are engine-specific logic.

The `_run-log.jsonl` start + end records are still emitted, but written directly by phase 02 / phase 04 of this engine (mirroring the loop primitive's pattern), not via the loop primitive itself.

## Shared `nomenclature.md` payload

Phase 02 reads, in priority order:

1. `.claude/agent-memory/paper-writer/nomenclature.md` in the user's project — the canonical author-curated nomenclature list. The `memory-load.sh` hook makes this file part of the session context for subagents, but we **also** embed its content into each dispatch's `task_brief` so the writer cannot miss it.
2. If the file does not exist, the engine substitutes this minimal stub:

   ```
   (No nomenclature.md yet — none has been recorded for this project.
    Use terminology consistent with the Introduction section if one is already
    drafted; if undecided, pick one form and log it in
    .claude/agent-memory/paper-writer/nomenclature.md so future runs can
    converge. Avoid switching between synonyms within a single section.)
   ```

The payload is identical across all N dispatches in a single run — that is the entire point. Parallel writers cannot communicate, so the shared payload is the only synchronization point available before the writes land.

Phase 02 does **not** edit `nomenclature.md`. Writers may *log* terminology decisions into it during their dispatch (the persona body grants that permission), but that is a per-writer side effect, not an engine action.

## Post-merge `terminology-drift.md` lint

After phase 03 writes the prose to each section file, the engine runs a regex-light scan across the newly-written sections to extract candidate-jargon terms:

- **All-caps tokens** of 2+ characters (e.g., `BOLD`, `fMRI`, `RT`) — these are usually acronyms whose expansion or spelling should agree across sections.
- **Hyphenated compounds** of 2+ words (e.g., `working-memory`, `top-down`) — these usually have a canonical hyphenation choice per project.
- **Defined-once-then-reused phrases**: a phrase that appears verbatim 2+ times in one section AND 1+ times in another, with the same surface form, is treated as a candidate. (This is the cheap heuristic — it does not understand synonymy.)

For each candidate, the lint records:
- The variants observed (e.g., `BOLD signal` vs `BOLD-signal` vs `hemodynamic response`).
- The sections each variant appears in.
- A one-line suggested-canonical: the most frequently-used variant across the run.

The output is written to `<manuscript_root>/terminology-drift.md`. **Non-blocking** — the engine returns DONE regardless of what the lint finds. The user reads the drift file (or runs `/iterate-revision` on each section, which will surface the same issues through the reviewer) and decides.

Drift output is regenerated each run. The file is **not** committed to git on behalf of the user; users typically gitignore it (sample gitignore line: `terminology-drift.md`).

## First drafts only — no refinement

This engine **does not** call `/iterate-revision`, ever. Phase 2 decision §5 (engines are leaves) is binding. The user's options after a successful run:

- `/iterate-revision <section-path>` per section, ordered by importance.
- Hand-edit a section (e.g. the abstract is short — faster to write than to iterate).
- `/supervisor-drive` (Phase 3) — when shipped, this will be the engine that can chain `/outline-expand` → N × `/iterate-revision` autonomously.

Phase 04's user summary surfaces this explicitly with the per-section command lines pre-filled.

## What this engine writes

| File | Why |
|---|---|
| `paper.json.sections[name].status` → `"drafted"` for each newly-written section | The default post-draft status; matches `/iterate-revision`'s precondition for REVISE mode. |
| `paper.json.sections[name].iter` → `1` for each newly-written section | The map-reduce produced one iteration of prose. |
| `paper.json.sections[name].path` content | The actual prose, written via the `Write` tool. |
| `paper.json.last_updated` | Current UTC ISO-8601 at phase 03 end. |
| `<manuscript_root>/terminology-drift.md` | Lint artifact. Always written, even if no drift found (file then contains a one-line "no drift detected" stub). |
| `.claude/omcr-state/_run-log.jsonl` | One `phase: "start"` line in phase 02, one `phase: "end"` line in phase 04, one `phase: "summary"` line in phase 04. |

This engine does **not** write `reviews.json`, `citations.json`, or `figures.json`.

## What this engine does NOT do

- Does **not** loop. One pass through the dispatch plan. Refinement is the user's call via `/iterate-revision`.
- Does **not** call another engine. Engines are leaves (Phase 2 §5).
- Does **not** review the prose it produces. There is no reviewer dispatch in this engine. Use `/iterate-revision <section-path>` per section to invoke the reviewer.
- Does **not** auto-resolve `[CITE:]` placeholders. Writers may emit them; `@literature-curator` resolves them in a separate flow (`/literature-sweep`).
- Does **not** clobber `approved` sections. Phase 01 skips them unless they appear in `--sections`.
- Does **not** retry failed dispatches. A partial-failure run is reported, not auto-recovered. The user re-runs with `--sections <failed-names>`.
- Does **not** edit `main.tex`, `references.bib`, or `outline.md`. Writes only section files + the drift artifact.
- Does **not** commit to git. Manuscript-scaffold's phase 4 owns commit-and-push flows; this engine is loop-internal.

## Re-running policy

- All-`approved` section set + no `--sections` → phase 01 reports "nothing to draft" and exits cleanly, no agent calls.
- Outline missing some sections that exist in `paper.json` (e.g., no `methods` heading in the outline) → only sections with both an outline excerpt **and** a `paper.json` entry are drafted.
- Partial failure (e.g., 4 of 5 dispatches return prose, 1 errors): the 4 successes are written and `paper.json` updated for them; the 1 failure is logged. User re-runs with `--sections <failed-name>`.
- Re-run on a project that already has drafted sections, with `--sections introduction,methods`: those two are re-drafted (clobbering existing prose); other sections untouched.

## Cost model

Each section is **one** Agent-tool dispatch. For a 5-section manuscript, the run is 5 parallel dispatches. The `cost_estimate_tokens: 40000` frontmatter field is a coarse upper-bound (≈ 8k tokens × 5 sections); actuals land in `_run-log.jsonl` post-hoc per Phase 0 decision §6.

Parallel dispatch saves wall-clock time, not tokens. Each dispatch carries the full `@paper-writer` persona body (~250 lines) plus the nomenclature payload plus the per-section outline excerpt. Long outlines compound this; the engine does not auto-trim the per-section excerpt (the writer needs the context). If the outline is enormous (>3000 lines), consider splitting it before running.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine composes (this engine uses 2 of 4).
- [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) — pattern reference. The natural follow-up to this engine.
- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — public pattern doc.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — state-file schema reference.
- [`../../develop/phase-2-additional-engines.md`](../../develop/phase-2-additional-engines.md) — engine 5 design rationale and acceptance scenarios.
- [`../../develop/phase-2-decisions.md`](../../develop/phase-2-decisions.md) §4 — the shared `nomenclature.md` + post-merge drift lint decision.
