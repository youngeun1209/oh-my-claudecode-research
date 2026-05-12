---
name: figure-bake-evaluate
description: Phase 5 of /figure-bake. Apply the severity-threshold verdict rule to the reviewer's issues list, update figures.json.figures[<fig-id>] critique_status / impl_status / brief_status / iter, and return the verdict to the loop primitive.
---

# Phase 5 — Evaluate

Decide one of `DONE | CONTINUE | BLOCKED | HALT` from the issues list phase 04 produced. Update the critique entry's `verdict` + `reason`. Update `figures.json.figures[<fig-id>]` status fields per the verdict. Return the verdict to the loop primitive so it can decide whether to break or continue.

This phase composes [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md). The primitive owns rule application and (when applicable) the reviews.json update; this phase owns the engine-specific rule spec and the `figures.json` writes.

## Inputs (from phase 04)

| Name | Source | Purpose |
|---|---|---|
| `fig_id` | phase 04 | Key in `figures.json.figures`. |
| `figures_state` | phase 04 | Parsed dict with the new critique appended. |
| `current_iter` | loop primitive | Iter just critiqued; compared against `max_iter`. |
| `max_iter` | phase 01 | Hard cap from CLI / default. |
| `run_id` | loop primitive | UUID — used to update the existing critique entry in place. |
| `issues` | phase 04 | Normalized list of `{severity, text, location}` objects. |
| `last_output` | phase 04 | Shaped as `{parsed: {issues: [...]}, ...}` so the primitive's dotted-path can read `last_output.parsed.issues`. |
| `implementer_status` | phase 04 | `"ok" | "failed" | "no-brief"`. Drives the `impl_status` write in step 4. |
| `venue` | engine_args (optional) | Recorded into the critique entry. |

## Step 1 — Build the verdict rule spec

Pass a `severity-threshold` family rule to the orchestrate primitive. Canonical spec for this engine:

```jsonc
{
  "kind":                  "severity-threshold",
  "issues_path":           "last_output.parsed.issues",
  "blocking_severities":   ["critical"],
  "must_clear_severities": ["critical", "major"],
  "halt_on_max_iter":      true
}
```

Application order (the primitive runs this; repeated here for auditability):

1. If any issue has severity in `blocking_severities` (`critical`) → **BLOCKED**.
2. Else if no issue has severity in `must_clear_severities` (`critical` ∪ `major` — i.e., the issues list contains only `minor` / `nit` / nothing) → **DONE**.
3. Else if `current_iter >= max_iter` and `halt_on_max_iter` is true → **HALT**.
4. Else → **CONTINUE**.

Canonical table from the engine SKILL.md:

| iter | critical | major | result |
|---|---|---|---|
| any   | ≥ 1 | any | **BLOCKED** |
| < max | 0   | ≥ 1 | **CONTINUE** |
| < max | 0   | 0   | **DONE** |
| = max | 0   | ≥ 1 | **HALT** |
| = max | 0   | 0   | **DONE** |

`minor` and `nit` never gate.

## Step 2 — Build the `reason` string

After the primitive returns its verdict, replace the primitive's generic `reason` with an engine-specific one (longer reasons are better here — phase 06 surfaces them to the user). Count issues by severity:

- `crit = #critical`
- `maj  = #major`
- `min  = #minor`
- `nit  = #nit`

Pick the reason per verdict:

| Verdict | `reason` template |
|---|---|
| `BLOCKED`  | `critical issue requires structural fix — see: "<first critical text, truncated to 120 chars>"` |
| `CONTINUE` | `<maj> major + <min> minor + <nit> nit remaining — iter <current_iter>/<max_iter>, looping` |
| `DONE` (iter < max) | `all critical + major cleared in <current_iter> iter (minor=<min>, nit=<nit>)` |
| `DONE` (iter == max) | `all critical + major cleared on the final allowed iter (minor=<min>, nit=<nit>)` |
| `HALT`     | `max_iter <max_iter> reached with <maj> major issue(s) remaining (critical=0)` |

Truncate `text` for the BLOCKED template to 120 characters; append `…` if truncated.

## Step 3 — Call the orchestrate evaluate primitive

Call [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md) with:

```jsonc
{
  "engine_name":       "figure-bake",
  "state_after":       <figures_state — the dict, with phase 04's critique appended>,
  "last_output":       <last_output from phase 04>,
  "iter":              <current_iter>,
  "max_iter":          <max_iter>,
  "verdict_rule_spec": <the spec from step 1>,
  "run_id":            <run_id>,
  "section":           null,
  "venue":             <venue or null>
}
```

`section` is `null` — `/figure-bake` operates on a fig-id, not a paper section. The orchestrate primitive's reviews.json update path is conditional on the engine having dispatched `@reviewer` to evaluate a section; this engine *does* dispatch `@reviewer`, but the durable critique record lives in `figures.json.figures[<fig-id>].critiques`, not in `reviews.json`. To match that ownership convention:

- The orchestrate primitive's reviews.json append in its step 3 should be **suppressed** for this engine. Two options:
  1. Have the primitive treat `section == null` as "do not write to reviews.json" (already the spirit of the primitive's "if the engine dispatched @reviewer" condition — the primitive only writes when `section` is non-null in the canonical interpretation).
  2. If the primitive writes anyway, the duplicate-record consequence is benign: a `reviews.json.runs[]` entry with `section: null` is recoverable on read.

Phase 05 of this engine relies on interpretation (1). If the primitive evolves and starts writing unconditionally, file a follow-up issue against the orchestrate primitive rather than working around it here.

The primitive returns `{verdict, reason, iter}`. Capture both. Then **immediately** overwrite the critique entry's `reason` field with the engine-specific reason from step 2:

1. Read `figures.json` via the state-read primitive (re-read for safety).
2. Find the entry in `figures.json.figures[fig_id].critiques` where `run_id == <run_id>` AND `iter == <current_iter>`.
3. Set `entry.verdict = <verdict>` and `entry.reason = <engine reason from step 2>`.
4. Write `figures.json` back atomically.

This mirrors the `/iterate-revision` phase 04 pattern of overwriting the primitive's terse reason with an engine-specific one — phase 06's summary reads better that way.

## Step 4 — Update `figures.json.figures[<fig-id>]` status fields

Based on the verdict and `implementer_status`, write:

| Verdict | `entry.critique_status` | `entry.impl_status` | `entry.brief_status` |
|---|---|---|---|
| `DONE` | `"done"` | `"approved"` (only if `implementer_status == "ok"`; else leave as-is — DONE with a synthetic implementer-failure issue is unreachable because step 1 of phase 04 would have synthesized a critical, routing to BLOCKED) | `"approved"` |
| `BLOCKED` | `"done"` | `"missing"` if `implementer_status != "ok"`, else `"drafted"` | If any critical issue's `location` starts with `"brief:"`, set to `"drafted"` (so phase 02 re-runs on resume); else leave as-is |
| `HALT` | `"done"` | `"drafted"` (the render exists but isn't approved) | leave as-is |
| `CONTINUE` | `"done"` | `"drafted"` | If any major+ issue's `location` starts with `"brief:"`, set to `"drafted"` (phase 02 re-runs next iter); else leave as-is |

Why the `"brief:"` location prefix matters: the reviewer in phase 04 prefixes the `location` with `"brief:"` when the issue is brief-level (the descriptor's spec is the problem, not the rendering). When phase 05 sees that prefix on a `critical` or `major` issue, it flips `brief_status` back to `"drafted"` so phase 02 of the *next* iter dispatches the descriptor again instead of reusing the approved brief. This is the only mechanism by which the descriptor gets re-run mid-engine; without it, the loop would re-render against the same broken brief forever.

Also bump `entry.iter = current_iter + 1`. This is the single point of `iter` increment for this engine — phase 02 / 03 / 04 deliberately leave the counter alone so a partial run leaves a legible state. The new `iter` value reflects "this iter completed; the next dispatch (if any) will be iter+1 of the loop".

If the verdict is `DONE`, also persist some summary fields:
- `entry.title` — should already be set by phase 02 from the descriptor's title extraction.
- `entry.approved_at` — UTC ISO-8601 now. Additive field; first time this lands. Phase 06 reads it.

Write `figures.json` back atomically.

## Step 5 — Hand off to the loop primitive

Return to the orchestrate loop primitive:

```jsonc
{
  "verdict": "DONE | CONTINUE | BLOCKED | HALT",
  "reason":  <engine-specific reason from step 2>,
  "iter":    <current_iter>
}
```

The loop primitive uses `verdict` to decide:
- `DONE` / `BLOCKED` / `HALT` → break the loop, fall through to phase 06.
- `CONTINUE` → bump `current_iter` by 1, re-enter phase 02. Phase 02 decides whether to re-dispatch the descriptor based on `brief_status`; phase 03 re-dispatches the implementer; phase 04 re-dispatches the reviewer.

The loop primitive also applies its post-hoc `budget_tokens` cap here (Phase 0 decision §6) — if cumulative tokens exceeded the cap and the verdict was `CONTINUE`, the loop overrides to `HALT`. That logic lives in the primitive, not in this phase.

## Failure modes

| Condition | Behavior |
|---|---|
| `issues` list is null (phase 04 produced nothing usable) | Treat as one synthetic `major` issue and proceed. The rule will likely emit `CONTINUE` or `HALT`. |
| Verdict rule kind unknown | Should not happen — the spec is hardcoded above. If the primitive aborts with "unknown kind", that is a bug in this phase file. |
| `figures.json` re-read for the step 3 fix-up fails | Log a warning; the primitive's terse reason remains in place. Phase 06 still works (it pulls `reason` from the return dict, not from disk). |
| `figures.json` write fails in step 4 | Bubble the OS error. Loop primitive emits BLOCKED at its next safety check. The critique entry already exists, so the run's verdict is durable; only the per-figure status fields missed the write. |
| Multiple critical issues at the `brief:` location | Set `brief_status = "drafted"` once; the rest cascade through naturally on the next iter. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure logic + state writes.
- Does **not** decide whether to commit (loop's `on_iter_end` owns that; v0.2 leaves it off for `/figure-bake`).
- Does **not** modify `_run-log.jsonl`. The loop primitive owns that file.
- Does **not** touch `paper.json` / `citations.json` / `reviews.json`. Out of scope for `/figure-bake`. The orchestrate evaluate primitive's reviews.json append is suppressed (see step 3 note); `paper.json` is only read in phase 01.
- Does **not** invent verdict values. Only the four are allowed.
- Does **not** retry. One verdict per iter; if `CONTINUE`, the next iter is a fresh design / implement / critique triple.
- Does **not** delete prior critique entries. The `critiques[]` list is append-only; old iters' critiques persist for audit.
- Does **not** re-invoke `cropfig`. Phase 03 owns the crop pass.
