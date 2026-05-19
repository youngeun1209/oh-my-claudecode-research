# Phase 4 — Evaluate

Decide one of `DONE | CONTINUE | BLOCKED | HALT` from the issues list phase 03 produced. Update the reviews.json entry's `verdict` + `reason`. Set `paper.json.sections[name].status` per the verdict. Return the verdict to the loop primitive so it can decide whether to break or continue.

This phase composes [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md). The primitive owns rule application and reviews.json update; this phase owns the engine-specific rule spec and the `paper.json.sections[name].status` write-back.

## Inputs (from phase 03)

| Name | Source | Purpose |
|---|---|---|
| `section_name` | phase 03 | Updated in `paper.json` and recorded in the reviews entry. |
| `venue` | phase 03 | Recorded in the reviews entry. |
| `new_iter` | phase 03 | The iter just reviewed; compared against `max_iter`. |
| `max_iter` | phase 01 | Hard cap from CLI / default. |
| `run_id` | loop primitive | UUID — used by orchestrate evaluate to update the existing reviews entry in place. |
| `issues` | phase 03 | Normalized list of `{severity, text, location}` objects. |
| `last_output` | phase 03 | Shaped as `{parsed: {issues: [...]}, ...}` so the primitive's dotted-path can read `last_output.parsed.issues`. |
| `paper_state` | flows from phase 01/02 | Parsed `paper.json` for the in-place status update. |

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

Application order (the primitive runs this, repeated here for auditability):

1. If any issue has severity in `blocking_severities` (`critical`) → **BLOCKED**.
2. Else if no issue has severity in `must_clear_severities` (`critical` ∪ `major` — i.e., the issues list contains only `minor` / `nit` / nothing) → **DONE**.
3. Else if `new_iter >= max_iter` and `halt_on_max_iter` is true → **HALT**.
4. Else → **CONTINUE**.

This is the canonical table from the spec:

| iter | critical | major | result |
|---|---|---|---|
| any   | ≥ 1 | any | **BLOCKED** |
| < max | 0   | ≥ 1 | **CONTINUE** |
| < max | 0   | 0   | **DONE** |
| = max | 0   | ≥ 1 | **HALT** |
| = max | 0   | 0   | **DONE** |

`minor` and `nit` never gate.

## Step 2 — Build the `reason` string

After the primitive returns its verdict, replace the primitive's generic `reason` with an engine-specific one (longer reasons are better here — phase 05 surfaces them to the user). Count issues by severity from the input list:

- `crit = #critical`
- `maj  = #major`
- `min  = #minor`
- `nit  = #nit`

Pick the reason per verdict:

| Verdict | `reason` template |
|---|---|
| `BLOCKED`  | `critical issue requires structural fix — see: "<first critical text, truncated to 120 chars>"` |
| `CONTINUE` | `<maj> major + <min> minor + <nit> nit remaining — iter <new_iter>/<max_iter>, looping` |
| `DONE` (iter < max) | `all critical + major cleared in <new_iter> iter (minor=<min>, nit=<nit>)` |
| `DONE` (iter == max) | `all critical + major cleared on the final allowed iter (minor=<min>, nit=<nit>)` |
| `HALT`     | `max_iter <max_iter> reached with <maj> major issue(s) remaining (critical=0)` |

Truncate `text` for the BLOCKED template to 120 characters; append `…` if truncated.

## Step 3 — Call the orchestrate evaluate primitive

Call [`../../orchestrate/phases/03-evaluate.md`](../../orchestrate/phases/03-evaluate.md) with:

```jsonc
{
  "engine_name":       "iterate-revision",
  "state_after":       <paper_state — the dict, with phase 02's updates already applied>,
  "last_output":       <last_output from phase 03>,
  "iter":              <new_iter>,
  "max_iter":          <max_iter>,
  "verdict_rule_spec": <the spec from step 1>,
  "run_id":            <run_id>,
  "section":           <section_name>,
  "venue":             <venue>
}
```

The primitive will:

- Apply the rule → `{verdict, reason, iter}`.
- Update the existing entry in `reviews.json.runs` (matched by `run_id`) with the new `verdict` + the **primitive's own** `reason`.

After it returns, **immediately** overwrite the reviews.json entry's `reason` field with the engine-specific reason from step 2:

1. Read `reviews.json` via the state-read primitive.
2. Find the entry where `run_id == <run_id>` AND `iter == <new_iter>`. (The pair disambiguates if a run somehow has multiple entries — should not happen, but the guard is cheap.)
3. Set `entry.reason = <engine reason from step 2>`.
4. Write `reviews.json` back atomically.

This is the small price for using the generic primitive — the primitive's reason is correct but terse, and the user-facing summary in phase 05 reads better with the engine-specific phrasing.

## Step 4 — Update `paper.json.sections[name].status`

Based on the verdict:

| Verdict | `paper_state.sections[section_name].status` becomes |
|---|---|
| `DONE` | `"approved"` |
| `BLOCKED` | `"blocked"` |
| `HALT` | `"revising"` — left open for resume |
| `CONTINUE` | `"revising"` — loop will re-enter phase 02 next iter |

Also set `paper_state.last_updated = <UTC ISO-8601 now>`. Write `paper.json` back atomically.

The `iter` field on the section is **not** touched here — phase 02 already bumped it for the iter that just ran. The `last_review_id` pointer was set by phase 03 and is left as-is.

## Step 5 — Hand off to the loop primitive

Return to the orchestrate loop primitive:

```jsonc
{
  "verdict": "DONE | CONTINUE | BLOCKED | HALT",
  "reason":  <engine-specific reason from step 2>,
  "iter":    <new_iter>
}
```

The loop primitive uses `verdict` to decide:
- `DONE` / `BLOCKED` / `HALT` → break the loop, fall through to phase 05.
- `CONTINUE` → bump `current_iter` by 1, re-enter phase 02.

The loop primitive also applies its post-hoc `budget_tokens` cap here (Phase 0 decision §6) — if cumulative tokens exceeded the cap and the verdict was `CONTINUE`, the loop overrides to `HALT`. That logic lives in the primitive, not in this phase.

## Failure modes

| Condition | Behavior |
|---|---|
| `issues` list is null (phase 03 produced nothing usable) | Treat as one synthetic `major` issue and proceed. The rule will likely emit `CONTINUE` or `HALT`. |
| Verdict rule kind unknown | Should not happen — the spec is hardcoded above. If the primitive aborts with "unknown kind", that is a bug in this phase file. |
| `reviews.json` re-read for step 3 fix-up fails | Log a warning; the primitive's terse reason remains in place. Phase 05 still works (it pulls `reason` from the return dict, not from disk). |
| `paper.json` write fails | Bubble the OS error. Loop primitive emits BLOCKED at its next safety check. The reviews.json entry already exists, so the run's verdict is durable; only the section status missed the write. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure logic + state writes.
- Does **not** decide whether to commit (loop's `on_iter_end` owns that; OMCR currently leaves it off).
- Does **not** modify `_run-log.jsonl`. The loop primitive owns that file.
- Does **not** touch `citations.json` or `figures.json`. Out of scope for `/iterate-revision`.
- Does **not** invent verdict values. Only the four are allowed.
- Does **not** retry. One verdict per iter; if `CONTINUE`, the next iter is a fresh writer + reviewer pair.
