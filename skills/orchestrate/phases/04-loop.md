# Phase 04 — loop (primitive)

Drive an engine's `dispatch_plan` through iterations of dispatch →
evaluate → maybe-commit, until the verdict says stop. The only place
`max_iter`, budget enforcement, and `_run-log.jsonl` writes live.

## Inputs

| Name | Required | Type | Default | Purpose |
|---|---|---|---|---|
| `engine_name` | yes | string | — | Recorded into `_run-log.jsonl` and reviews entries. |
| `dispatch_plan` | yes | list | — | Ordered list of dispatch specs to run **per iteration** (see "Dispatch plan shape" below). |
| `verdict_rule_spec` | yes | dict | — | Passed verbatim to `phases/03-evaluate.md`. |
| `max_iter` | no  | int | 3 | Hard cap. Reaching it without DONE/BLOCKED emits HALT. |
| `budget_tokens` | no | int / null | null | Cumulative cap. If `tokens_used > budget_tokens` at the end of an iteration, emit HALT. Post-hoc only (Phase 0 decision §6). |
| `on_iter_end` | no | string / null | null | If `"git-commit"`: after each non-final iteration, `git add -A && git commit -m "omcr: iter {n} of {engine_name}/{run_id}"`. Anything else is ignored. |
| `engine_args` | no | dict | `{}` | Free-form engine inputs (e.g. `{section: "results", venue: "..."}`). Recorded into `_run-log.jsonl` `args` field. |

## Dispatch plan shape

A list of dicts, each describing one Agent-tool invocation. The list is
executed **sequentially** within each iteration.

```jsonc
[
  {
    "persona":                "paper-writer",
    "task_brief":             "Revise {section} addressing issues from review {prev_review_id}.",
    "state_slice":            <dict | null>,
    "expected_output_schema": <dict | null>
  },
  {
    "persona":                "reviewer",
    "task_brief":             "Review {section} for {venue}. Return issues list.",
    "state_slice":            <dict | null>,
    "expected_output_schema": { "issues": [{"severity": "...", "text": "...", "location": "..."}] }
  }
]
```

Each step is passed through `phases/02-dispatch.md` exactly as-is. The
engine is responsible for any template substitution (`{section}`,
`{venue}`, etc.) — the loop does not interpret braces.

The **last dispatch in the plan** is conventionally the one whose
output `phases/03-evaluate.md` will read (e.g. a `@reviewer` call whose
output is the issues list). Engines that need verdicts from a non-final
dispatch should restructure the plan or use the `engine-supplied`
escape hatch in the verdict rule.

## Behavior

Execute in order:

1. **Generate `run_id`.** A UUID (v4) string. The engine and the
   primitive both reference this id.

2. **Append run-start to `_run-log.jsonl`.** One line, atomic-append:

   ```jsonc
   {
     "run_id":   "<uuid>",
     "engine":   "<engine_name>",
     "args":     <engine_args>,
     "started":  "<UTC ISO-8601>",
     "phase":    "start"
   }
   ```

   Note: `phase: "start"` distinguishes the open record from the close
   record written in step 5. JSONL readers can pair them by `run_id`.

3. **Run iterations.** For `iter` in `1..max_iter`:

   a. Record iteration start timestamp as `iter_started`.

   b. **Run each dispatch step in order.** Call `phases/02-dispatch.md`
      with the step's inputs. Collect the returned dict into a list
      `iter_outputs`.

      If any dispatch errors:
      - Set `verdict = "BLOCKED"`, `reason = "dispatch error: <message>"`.
      - Skip step c. Go to step d.

   c. **Evaluate.** Call `phases/03-evaluate.md` with:
      - `engine_name`
      - `state_after` = the engine's current state (engines pass a
        callable or freshly-read dict — the loop does not read state
        itself)
      - `last_output` = `iter_outputs[-1]` (the last dispatch's result)
      - `iter`, `max_iter`, `verdict_rule_spec`, `run_id`,
        plus optional `section`, `venue` from `engine_args`.
      Get back `{verdict, reason, iter}`.

   d. **Cost check (post-hoc).** Accumulate the iteration's tokens
      from each dispatch's metadata into a running `tokens_used` total.
      If `budget_tokens` is set and `tokens_used > budget_tokens`:
      - Override the verdict to `HALT` (regardless of what evaluate
        returned, unless it was already `BLOCKED` — BLOCKED wins).
      - Append `" + budget_tokens cap exceeded ({tokens_used} > {budget_tokens})"`
        to the reason string.

   e. **on_iter_end commit (optional).** If `on_iter_end ==
      "git-commit"` AND the verdict is `CONTINUE` (i.e., we're going
      to loop again):
      - Run `git add -A` (from the project root).
      - Run `git commit -m "omcr: iter {iter} of {engine_name}/{run_id}"`.
      - If the commit fails (e.g. nothing to commit), log a warning to
        the run log and continue. Do not abort the loop.

      Why only on `CONTINUE`: a `DONE` or `HALT` iteration is already
      the last one; engines that want a final commit do it themselves
      in their report phase so the message can include the verdict.

   f. **Break or continue.** If verdict is `DONE`, `BLOCKED`, or
      `HALT`: break the loop. Else: `iter += 1` and repeat.

4. **Final fallthrough.** If the loop exited the `for` without an
   explicit break (i.e., `iter` reached `max_iter` and the last
   verdict was `CONTINUE`):
   - Override verdict to `HALT`, reason to `"max_iter {max_iter}
     reached without DONE"`.

5. **Append run-close to `_run-log.jsonl`.** One line, atomic-append:

   ```jsonc
   {
     "run_id":       "<uuid>",
     "engine":       "<engine_name>",
     "args":         <engine_args>,
     "started":      "<UTC ISO-8601 from step 2>",
     "ended":        "<UTC ISO-8601 now>",
     "iter_count":   <final iter value>,
     "verdict":      "<verdict>",
     "reason":       "<reason>",
     "tokens_used":  <cumulative>,
     "phase":        "end"
   }
   ```

6. **Return.** Hand the engine its summary so it can format a
   user-facing report:

   ```jsonc
   {
     "run_id":      "<uuid>",
     "verdict":     "<verdict>",
     "reason":      "<reason>",
     "iter_count":  <iter>,
     "tokens_used": <int>,
     "iter_outputs": [ <per-iter dispatch result lists> ]
   }
   ```

## Cost model

Post-hoc, single-iteration granularity. There is no pre-flight token
estimation currently (Phase 0 decision §6). `budget_tokens` is honored
**at the iteration boundary** — a runaway iteration is bounded by one
iteration's actual cost, not by mid-iteration aborts. With default
`max_iter = 3` this is acceptable.

A future Phase 3 implementation may add tokenizer-based pre-flight
estimation; this primitive's input contract already accepts
`budget_tokens` so the engine API does not change.

## Safety invariants

- **`max_iter` is never silently exceeded.** Step 4 always emits HALT
  if the loop ran out without DONE/BLOCKED.
- **Dispatch errors break the loop with BLOCKED.** Step 3b. The user
  sees the underlying error in the run log.
- **Atomic writes.** Each `_run-log.jsonl` append uses
  `open(...,"a")` + `flush` + `fsync` semantics. The reviews/state
  writes use the tmp + rename pattern from `phases/01-state-read.md`.
- **Resumability is partial.** A killed loop leaves the start record
  in `_run-log.jsonl` without an end record. Phase 3
  (`/supervisor-drive`) defines the resume contract; this primitive
  does not auto-resume.

## Errors

| Condition | Behavior |
|---|---|
| `dispatch_plan` is empty list | Abort before iter 1 with `loop: dispatch_plan is empty`. |
| `max_iter < 1` | Abort with `loop: max_iter must be >= 1`. |
| `on_iter_end` is set to something other than `"git-commit"` or null | Warn `loop: unknown on_iter_end value <value> — ignoring`. Proceed without the hook. |
| Run log append fails | Print the OS error and abort. The run is unsafe to continue without a log trail. |
| Git commit at `on_iter_end` fails | Log warning, continue. Do not abort. |

## What this primitive does NOT do

- Does NOT read state files itself. Engines pass `state_after` to
  evaluate; the loop only forwards.
- Does NOT mutate `paper.json` / `citations.json` / `figures.json`.
  Engines do that between dispatch steps using their own phase logic.
- Does NOT retry failed dispatches. One shot per iteration step.
- Does NOT push to git. `on_iter_end == "git-commit"` only commits
  locally. Engines that want to push prompt the user from their report
  phase, matching `manuscript-scaffold` phase 4 convention.
- Does NOT lock the state directory against concurrent runs. Serial
  execution is the current assumption (Phase 0 decision §4).
