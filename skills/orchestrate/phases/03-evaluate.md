# Phase 03 — evaluate (primitive)

Apply an engine-supplied verdict rule against the current state plus
the last dispatch output. Returns one of four verdicts that the loop
primitive (`phases/04-loop.md`) uses to decide whether to continue.

## Inputs

| Name | Required | Type | Purpose |
|---|---|---|---|
| `engine_name` | yes | string | For logging (`_run-log.jsonl` + reviews.json entry). |
| `state_after` | yes | dict | The state dict after the engine applied any updates from the last dispatch. |
| `last_output` | yes | dict | The dict returned by `phases/02-dispatch.md`. |
| `iter` | yes | int | Current iteration number (1-indexed). |
| `max_iter` | yes | int | Hard cap. Triggers HALT if reached without DONE/BLOCKED. |
| `verdict_rule_spec` | yes | dict | Engine-supplied rule. Shape described below. |
| `run_id` | yes | string | UUID for the current run, set by `phases/04-loop.md`. |
| `section` | no | string | If the engine operates on a paper section (e.g., `iterate-revision`), pass the section name so the verdict can be recorded against it in `reviews.json`. |
| `venue` | no | string | If known, recorded alongside the verdict. |

## Verdict values

Exactly four. Engines never invent new verdicts; if a new flow needs
a different exit signal, encode it into the `reason` string.

| Verdict | Meaning | Loop behavior |
|---|---|---|
| `DONE` | Engine considers the task complete for this run. | Break loop. Engine reports success. |
| `CONTINUE` | More iterations needed. | Loop body runs again at `iter + 1` (if `iter + 1 ≤ max_iter`). |
| `BLOCKED` | A critical issue requires human intervention. | Break loop. Engine surfaces the blocking reason. |
| `HALT` | Budget / iteration cap reached without DONE. | Break loop. Engine reports partial progress + cap hit. |

## `verdict_rule_spec` shape

Engines pass a rule as **data**, not code. The primitive interprets the
data and applies it. Two rule families are supported in v0.2:

### Rule family A — `severity-threshold` (most engines)

For engines whose dispatch output is a list of `issues` with `severity`
fields (`/iterate-revision`, `/respond-reviewer`, `/figure-bake`
critique pass).

```jsonc
{
  "kind": "severity-threshold",
  "issues_path": "last_output.parsed.issues",   // dotted path into last_output
  "blocking_severities": ["critical"],          // any issue with these → BLOCKED
  "must_clear_severities": ["critical", "major"], // all must be empty → DONE
  "halt_on_max_iter": true                        // if iter >= max_iter and not DONE → HALT
}
```

Application order:

1. If any issue's severity is in `blocking_severities` AND a non-clearable
   flag is set (e.g. severity is `critical`): emit `BLOCKED`.
2. Else if no issue's severity is in `must_clear_severities`: emit `DONE`.
3. Else if `iter >= max_iter` and `halt_on_max_iter` is true: emit `HALT`.
4. Else: emit `CONTINUE`.

### Rule family B — `always-after-n` (smoketest, trivial engines)

```jsonc
{
  "kind": "always-after-n",
  "n": 1,
  "verdict": "DONE"
}
```

Application: if `iter >= n`, emit the named verdict. Else `CONTINUE`.

Used by the Phase 0 smoketest (`develop/orchestrate-smoketest/`) to
prove wiring without real verdict logic.

### Rule family C — escape hatch

If a future engine needs a rule the primitive doesn't natively
understand, pass:

```jsonc
{
  "kind": "engine-supplied",
  "verdict": "DONE | CONTINUE | BLOCKED | HALT",
  "reason": "human-readable string"
}
```

The engine computed the verdict in its own phase file; this primitive
just records and returns it. This is the escape hatch — use sparingly,
prefer family A.

## Behavior

Execute in order:

1. **Validate rule kind.** Must be one of `severity-threshold`,
   `always-after-n`, `engine-supplied`. Anything else → abort with
   `evaluate: unknown verdict_rule_spec.kind <kind>`.

2. **Apply rule.** Compute `verdict ∈ {DONE, CONTINUE, BLOCKED, HALT}`
   per the family above. Build a one-line human-readable `reason`
   string (e.g., `"1 major issue remaining, iter 2/3"` or `"all critical
   + major cleared"` or `"max_iter 3 reached without clearing
   majors"`).

3. **Record to `reviews.json`** (if applicable). When the engine
   dispatched `@reviewer` in this iteration, append an entry to
   `reviews.json.runs`:

   ```jsonc
   {
     "run_id":  "<run_id>",
     "engine":  "<engine_name>",
     "section": "<section or null>",
     "iter":    <iter>,
     "venue":   "<venue or null>",
     "started": "<iter start ISO-8601, supplied by loop>",
     "ended":   "<now ISO-8601>",
     "issues":  <list extracted from last_output.parsed.issues, or []>,
     "verdict": "<verdict>",
     "reason":  "<reason>"
   }
   ```

   Use the atomic write pattern (`*.tmp` + rename) per
   `phases/01-state-read.md`.

   If the engine did **not** dispatch `@reviewer` in this iteration
   (e.g., the engine has its own state file like `figures.json` or
   `citations.json` to record verdicts in), the engine's own phase
   handles the state-file update — `evaluate` only logs to
   `reviews.json` when the verdict came from a review dispatch.

4. **Return the verdict dict.**

## Output contract

```jsonc
{
  "verdict": "DONE | CONTINUE | BLOCKED | HALT",
  "reason":  "<short human-readable explanation>",
  "iter":    <iter>
}
```

The loop primitive uses `verdict` to decide its next step. Engines
that need to surface `reason` to the user can pull it from this dict.

## Errors

| Condition | Behavior |
|---|---|
| `verdict_rule_spec.kind` unknown | Abort with the kind value. |
| Dotted path in rule doesn't resolve in `last_output` | Treat the missing field as empty (`[]` for issues lists, `null` otherwise). Emit a warning to the run log. |
| `reviews.json` write fails | Bubble the OS error to the loop primitive, which emits BLOCKED. |

## What this primitive does NOT do

- Does NOT invent severities. Engines that want a custom severity
  taxonomy must map it into the canonical `critical | major | minor |
  nit` enum before calling evaluate.
- Does NOT decide whether to commit (that is `on_iter_end` on the loop
  primitive).
- Does NOT update `paper.json` section status (that is the engine's
  responsibility — `evaluate` only writes to `reviews.json` because
  that file is append-only and verdict-shaped).
- Does NOT estimate token cost. Loop primitive owns that.
