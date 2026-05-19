---
name: respond-reviewer
description: Read a reviewer letter, classify each comment by type, dispatch per-comment responses to the right specialist agent (`@paper-writer`, `@analysis-implementer`, `@literature-curator`), and assemble a complete rebuttal letter. Structural comments are surfaced to user attention rather than auto-dispatched. Output defaults to LaTeX; accepts markdown or LaTeX input (auto-detected by extension). Safe to re-run; safe to resume after BLOCKED. The Phase 2 worked example of the classify-and-dispatch orchestration shape.
writes: [rebuttals, reviews, paper]
cost_estimate_tokens: 60000
---

# $respond-reviewer

This engine runs the classify-and-dispatch orchestration shape: one reviewer letter in, N labelled comments out, each routed to the specialist that should answer it, then re-evaluated by `@supervisor` before being assembled into a single rebuttal letter. It is the proof that OMXR can hand-off between specialists under supervisor control — Phase 2's harder counterpart to `$iterate-revision`'s single-loop pattern.

If you are reading this because Codex's skill auto-discovery surfaced it: invoke it via `$respond-reviewer <review-letter-path>`. Do not edit the manuscript, `rebuttals.json`, or `.omx/state/omxr/` by hand while a run is in flight.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

## Signature

```
$respond-reviewer <review-letter-path> [--manuscript <root>] [--draft-only] [--format md|latex]
```

| Flag | Default | Purpose |
|---|---|---|
| `--manuscript` | `paper.json.manuscript_root` | Manuscript root the dispatched agents may edit. Falls back to `paper.json.manuscript_root`; if neither is set, phase 01 aborts. |
| `--draft-only` | `false` | Dispatch all per-comment responses but skip every manuscript edit. The rebuttal letter is the only artifact written. |
| `--format` | `latex` | Output format for the assembled rebuttal letter. `latex` → `rebuttal-letter.tex`; `md` → `rebuttal-letter.md`. **Input** format is auto-detected from the letter extension (Phase 2 decision §2). |

Examples:
- `$respond-reviewer reviews/r1-comments.md` — defaults; auto-detect MD input, write LaTeX out.
- `$respond-reviewer reviews/r1-comments.tex --manuscript paper/` — LaTeX in, LaTeX out, explicit manuscript root.
- `$respond-reviewer reviews/r2-comments.md --draft-only` — read + classify + draft responses, but do not touch the manuscript.
- `$respond-reviewer reviews/r1-comments.txt --format md` — markdown out for a journal that submits rebuttals through a web form.

## The dispatch shape

```
phase 01 — parse-letter        (auto-detect format → structured comments list with stable IDs)
phase 02 — classify            (@supervisor labels every comment: prose|analysis|citation|clarification|structural)
phase 03 — dispatch-per-comment (route each non-structural label to its specialist; collect structural into user-attention)
phase 04 — aggregate           (assemble the rebuttal letter, one section per comment_id, in requested --format)
phase 05 — evaluate            (@supervisor re-reads the draft rebuttal, flags weak responses; verdict per comment)
phase 06 — finalize            (write the letter to disk, append rebuttals.json, log, surface user-attention list)
```

Phases 01 and 02 are **inspect** phases (one supervisor dispatch in 02). Phase 03 is the **fan-out** phase — one dispatch per non-structural comment. Phases 04, 05, 06 are **synthesis + record** — the supervisor revisits only the assembled letter, not every comment.

Unlike `$iterate-revision`, there is no loop body here — `$respond-reviewer` is a one-shot pipeline. The "iteration" is per-comment, but each comment is dispatched once. If a per-comment response is weak, phase 05 marks it `deferred` or `disputed` in `rebuttals.json` for the user to address; the engine does not auto-re-dispatch.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly.

1. **Phase 1 — Parse the letter.** Read [`phases/01-parse-letter.md`](phases/01-parse-letter.md).
2. **Phase 2 — Classify.** Read [`phases/02-classify.md`](phases/02-classify.md).
3. **Phase 3 — Dispatch per comment.** Read [`phases/03-dispatch-per-comment.md`](phases/03-dispatch-per-comment.md).
4. **Phase 4 — Aggregate.** Read [`phases/04-aggregate.md`](phases/04-aggregate.md).
5. **Phase 5 — Evaluate.** Read [`phases/05-evaluate.md`](phases/05-evaluate.md).
6. **Phase 6 — Finalize.** Read [`phases/06-finalize.md`](phases/06-finalize.md).

Phases 03 → 04 → 05 form the synthesis sequence — each runs once per engine invocation. The classify-and-dispatch shape does not loop, by design (Phase 2 decision §5 — engines are leaves; the per-comment dispatch is the "iteration").

## Composition

This engine imports the following primitives from `skills/orchestrate/`:

- [`phases/01-state-read.md`](../orchestrate/phases/01-state-read.md) — read `paper.json` (phase 01 of this engine, for manuscript context + section paths) and `reviews.json` (phase 03 of this engine, for any prior review history on the affected section). Also reads the new `rebuttals.json` state file.
- [`phases/02-dispatch.md`](../orchestrate/phases/02-dispatch.md) — dispatch `@supervisor` (phases 02 and 05), `@paper-writer` (phase 03 for `prose` / `clarification` labels), `@analysis-implementer` (phase 03 for `analysis` labels), `@literature-curator` (phase 03 for `citation` labels). Each dispatch is one Agent-tool invocation with the persona body inlined.
- [`phases/03-evaluate.md`](../orchestrate/phases/03-evaluate.md) — used in phase 05 to apply an `engine-supplied` verdict rule per comment (one of `addressed | deferred | disputed`). The orchestrate primitive's `severity-threshold` family does not fit the per-comment shape — `$respond-reviewer` uses the escape hatch and computes the verdict in phase 05 itself.
- [`phases/04-loop.md`](../orchestrate/phases/04-loop.md) — **not** the iteration driver for this engine (there is no loop). Phase 06 still uses the primitive's `_run-log.jsonl` append pattern for the start + end + summary records. The loop primitive's `max_iter` machinery is effectively `max_iter = 1` here.

This engine **does not** invent its own state-read, dispatch, or log-append mechanics. If you find yourself replicating that logic inside a phase file, you're solving the wrong problem — fix the primitive, do not fork it.

## State files this engine touches

| File | Read or write? | Purpose |
|---|---|---|
| `paper.json` | read | Resolve `manuscript_root` fallback, section paths, current section statuses. Write-back only if a per-comment dispatch flipped a section's `status` (e.g., `@paper-writer` revising a section creates a new `revising` status). |
| `reviews.json` | read | Look up prior reviewer issues on affected sections (helpful context for the per-comment dispatch). |
| `rebuttals.json` | **append (new file)** | One entry per run. Schema in [`develop/example-state/README.md`](../../develop/example-state/README.md). |
| `_run-log.jsonl` | append | Start + end + summary records via the loop primitive's pattern. |

`rebuttals.json` is the new state file this engine introduces. Its empty form is `{ "schema_version": "1", "rebuttals": [] }`. The full populated schema lives in the example-state README.

## Classification taxonomy

Phase 02 dispatches `@supervisor` to label every comment as exactly one of:

| Label | Dispatched agent | What it covers |
|---|---|---|
| `prose` | `@paper-writer` | Rewording, hedging, clarity, tone, sentence restructuring. The reviewer wants the text to say roughly the same thing better. |
| `analysis` | `@analysis-implementer` | New analysis, robustness check, additional statistical test, re-run with different parameters, figure redraw (figure ID flagged for user follow-up). |
| `citation` | `@literature-curator` | Missing reference, prior-work coverage gap, request to compare against a specific paper. |
| `clarification` | `@paper-writer` | Small text addition or clarification that doesn't require new content — typically a sentence or two added. |
| `structural` | **none — user attention** | Framing change, scope decision, section reorganization, methodological pivot. These are scientific judgment calls that only a human can make. |

The mapping `clarification → @paper-writer` is intentional — `paper-writer` is the only agent that produces manuscript prose, so any label that resolves to "add a sentence" is its responsibility. `prose` and `clarification` differ in scope (reword vs. add) but not in dispatched agent.

## Ethical gate — `structural` is human-only

Comments labeled `structural` are **never** dispatched. Phase 03 explicitly skips them, and phase 06 surfaces them to the user as a "user attention required" list. This is the project's stated ethical posture: comments that require a framing or scope decision should not be auto-answered by an agent.

If `@supervisor` is uncertain between `structural` and another label, it must default to `structural`. Phase 02 instructs it to do exactly that.

## Engines are leaves — figure redraws route to `@analysis-implementer`

Per Phase 2 decision §5, `$respond-reviewer` may not invoke another engine. If a comment requests a figure redraw:

1. Phase 02 labels it `analysis` (not `structural`, not its own label).
2. Phase 03 dispatches `@analysis-implementer` with the figure ID in the brief. The implementer may produce a partial response — e.g., "the figure needs `$figure-bake fig3` to redraw" — but does not run the redraw itself.
3. Phase 06 appends `suggested_next_steps: ["$figure-bake <fig-id>"]` to that comment's entry in `rebuttals.json` and surfaces it in the final summary.

The user (not the engine) decides whether to run `$figure-bake`. This matches the `structural → user-attention` posture: actions with downstream cost get a human ACK.

## Verdict semantics

Per-comment verdicts (set in phase 05, written to `rebuttals.json.rebuttals[*].comments[*].verdict`):

| Verdict | Meaning |
|---|---|
| `addressed` | The per-comment dispatch produced a response that materially answers the reviewer's concern, and the supervisor confirms the response matches the actions taken. |
| `deferred` | The dispatch produced a response, but it points to a follow-up the user must run (e.g., `$figure-bake`, manual `--allow-tbd` clearance, structural decision). Recorded so the user can see what is pending. |
| `disputed` | The supervisor flagged a weak or misleading response (e.g., "we have added X" without X actually being present in the manuscript). The user must rewrite or reject the response. |

There is no `BLOCKED` verdict at the **per-comment** level — that is a run-level state. Run-level verdicts (one of `DONE | BLOCKED | HALT`) are computed by phase 06 from the comment-level distribution:

| Comment distribution | Run verdict |
|---|---|
| All comments `addressed`, no structural | `DONE` |
| Any `disputed`, OR at least one `structural` flagged | `HALT` (user attention required) |
| Dispatch error mid-run | `BLOCKED` (partial state preserved) |

`CONTINUE` never appears — `$respond-reviewer` is single-pass.

## Cost model

Each run dispatches: 1 supervisor (classify) + N specialists (one per non-structural comment) + 1 supervisor (re-evaluate) = `2 + N` Agent-tool calls. For a typical 10-comment letter with ~7 non-structural comments, that's 9 dispatches. With `cost_estimate_tokens: 60000` as the frontmatter upper bound, the engine accommodates letters up to ~15 dispatches without overrunning the `$supervisor-drive` budget gate.

The `cost_estimate_tokens` frontmatter field is a coarse constant for Phase 3 autonomous-mode scheduling (Phase 3 §6 — rolling-median actuals add the empirical correction on top). Actuals land in `_run-log.jsonl` post-hoc per Phase 0 decision §6.

Per-comment dispatch is dominated by the persona body inline (each agent body is ~200–500 lines) plus the comment text + relevant manuscript context (~1–3K tokens of surrounding section content per comment). Letters with many cross-section comments compound this — the engine does not auto-trim.

## What this engine does NOT do

- Does **not** invoke another engine. Engines are leaves (Phase 2 decision §5). Figure-redraw comments are routed to `@analysis-implementer` with a `suggested_next_steps` hint pointing at `$figure-bake` — the user runs it, not the engine.
- Does **not** auto-dispatch `structural` comments. Always surfaced to user attention (the ethical gate).
- Does **not** loop. One comment, one dispatch, one verdict. If the response is `disputed` in phase 05, the user re-runs the engine after deciding what to fix — the engine does not auto-retry weak responses.
- Does **not** commit to git between dispatches. There is no `on_iter_end` hook here. If `--draft-only` is set, the engine never edits manuscript files at all.
- Does **not** rewrite the reviewer letter. The original is read-only; the rebuttal letter is a separate artifact.
- Does **not** invent citekeys or BibTeX entries. The `@literature-curator` dispatch handles citation labels and is the only agent that writes to `references.bib`; the engine just records the actions taken.
- Does **not** push to Overleaf. Manuscript-scaffold owns push flows.

## Re-running policy

- Same review letter re-run (no state change) → phase 01 detects a prior entry in `rebuttals.json` whose `review_letter` path matches and appends a **new** run rather than overwriting. The user sees both entries in the final state; the most recent is the canonical one.
- Mid-run `--draft-only` toggle → must be set at invocation time. The engine does not promote `--draft-only` runs to write-back runs; the user re-invokes without the flag.
- BLOCKED run → phase 06 leaves the partial rebuttal entry in `rebuttals.json` with the comments processed so far. The user re-runs after fixing whatever caused the BLOCKED (typically a dispatch error or unreadable manuscript path); the new run is a fresh entry.

## See also

- [`../orchestrate/SKILL.md`](../orchestrate/SKILL.md) — the 4 primitives this engine composes.
- [`../../wiki/Orchestration-Model.md`](../../wiki/Orchestration-Model.md) — public pattern doc.
- [`../../develop/example-state/README.md`](../../develop/example-state/README.md) — full `rebuttals.json` schema reference + populated example.
- [`../../develop/phase-2-additional-engines.md`](../../develop/phase-2-additional-engines.md) — design doc for this engine ("Engine 3 — `$respond-reviewer`").
- [`../../develop/phase-2-decisions.md`](../../develop/phase-2-decisions.md) — locked decisions §2 (LaTeX out, `--format md`) and §5 (engines are leaves).
- [`../iterate-revision/SKILL.md`](../iterate-revision/SKILL.md) — pattern reference. Voice and structure of this skill mirror that engine.
