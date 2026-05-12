# Phase 5 — Checkpoint

After every clean engine completion, commit progress to git, append a summary line to `_run-log.jsonl`, and update the cumulative budget tally. This phase is **skipped on engine exception** (phase 04 routes the error case directly to phase 07).

## Inputs

From phase 04:

- `plan.next_action` — the dispatched engine + args
- Engine return: `{ verdict, reason, iter_count, tokens_used, run_id_engine }`
- `cumulative_tokens_used` (already incremented in phase 04 step 9a)
- `no_commit` — bool from the original flags
- All carry-forward fields

## Steps

### 1. Git commit (unless `--no-commit`)

If `no_commit == false`:

```
git add -A
git commit -m "omcr supervisor-drive: <engine> <args-summary> verdict=<v> run=<supervisor-run_id>"
```

Where:

- `<engine>` — the dispatched engine name (kebab-case, e.g. `iterate-revision`).
- `<args-summary>` — first 60 chars of the args summary (e.g. `section_path=sections/methods.tex venue=NeurIPS`). Truncate with `…` if longer.
- `<v>` — the engine's returned verdict (`DONE | BLOCKED | HALT`).
- `<supervisor-run_id>` — the supervisor's drive UUID, **not** the engine's internal `run_id_engine`. This way `git log --grep="run=<id>"` returns every commit from a single drive.

Outcomes:

| Outcome | Action |
|---|---|
| Commit succeeds | Capture the commit hash (`git rev-parse HEAD`); log it. |
| Commit fails because nothing to commit (e.g. `--draft-only` engine run, all-read engine, or files already staged before drive started but no engine edits) | Log a warning `supervisor-drive: nothing to commit after <engine> — continuing.` Do NOT abort. |
| Commit fails for any other reason (e.g. pre-commit hook fail, GPG sign fail, repo state lock) | Log the error and abort the drive — bubble to phase 07 with `verdict: "HALT"` and `reason: "commit failed after <engine>: <error>"`. Per the spec, autonomous mode without commits = chaos to roll back; if we cannot commit, we should not advance. |
| Not in a git repo | First time: log a warning `supervisor-drive: not in a git repo — skipping commits for this drive.` Set `no_commit = true` for remaining iters of the drive. Continue. |

The supervisor never re-amends, never skips hooks, never force-pushes. Commits are plain `commit` — if a pre-commit hook fails, the user has signaled they want that check; respecting it is correct.

### 2. Append `phase: "iter-summary"` line to `_run-log.jsonl`

```jsonc
{
  "run_id":              "<supervisor run_id>",
  "engine":              "supervisor-drive",
  "phase":               "iter-summary",
  "iter":                <iter>,
  "dispatched_engine":   "<engine>",
  "dispatched_args":     <args>,
  "engine_run_id":       "<run_id_engine>",
  "engine_verdict":      "<DONE | BLOCKED | HALT>",
  "engine_reason":       "<reason>",
  "engine_iter_count":   <int>,
  "tokens_used_this_dispatch": <int>,
  "cumulative_tokens_used":    <int>,
  "budget_tokens":             <int>,
  "commit_hash":         "<hash or null>",
  "commit_skipped":      <bool>,
  "summary_at":          "<UTC ISO-8601 now>"
}
```

This line is the per-iter audit record. A reader can:

- `jq 'select(.phase == "iter-summary")' _run-log.jsonl` — every dispatch the drive ran, with verdict + token cost + commit hash.
- `git log --grep="run=<supervisor-run_id>"` — every commit the same drive made.

The two are joinable on `supervisor_run_id`. This is how `@supervisor` (the advisory persona, post-Phase 3 update) answers "what happened recently?".

### 3. Update the running budget tally

The phase 04 step 9a already incremented `cumulative_tokens_used`. Phase 05 has nothing more to add — it just persists the value into the iter-summary line so phase 06's budget check has a fresh authoritative number.

Optional: print a one-line per-iter cost line:

```
[iter <iter>/<max_iter>] checkpoint
  engine:      <engine> <args>
  verdict:     <v>
  tokens:      <tokens_used_this_dispatch> (this dispatch) → <cumulative> / <budget> total
  commit:      <hash> | (skipped) | (nothing to commit)
```

### 4. Hand off to phase 06

Pass forward all updated state. Phase 06 owns the termination decision.

## Failure modes

| Condition | Behavior |
|---|---|
| Commit succeeds — proceed | Normal path. |
| Commit fails (no changes) | Warn, continue. |
| Commit fails (hook / lock / GPG) | Halt drive — phase 07 with reason. |
| Not a git repo | First time: warn, switch to no_commit for the drive. Continue. |
| `_run-log.jsonl` append fails | Bubble OS error; halt drive. Same posture as phase 04: log trail is non-negotiable. |
| `tokens_used_this_dispatch` is missing from the engine return (engine bug) | Log a warning `supervisor-drive: engine <engine> did not report tokens_used; using projected_cost as estimate.` Use the phase 04 projection as the fallback. Continue. |

## What this phase does NOT do

- Does **not** push to a remote. Local commits only.
- Does **not** make a commit if `no_commit` is set. The `--no-commit` flag is binding for the entire drive — once set (either by the user or by the auto-fallback when not in a repo), never overridden mid-drive.
- Does **not** modify the commit message format at runtime. The format is fixed for v0.4 so `git log --grep="run="` is reliable.
- Does **not** include the engine's `run_id_engine` in the commit message. The supervisor's `run_id` is the user-visible thread; the engine's id is in `_run-log.jsonl` for cross-reference but would clutter `git log`.
- Does **not** retry on commit failure. Same Phase 3 §2 spirit applied to local actions.
- Does **not** evaluate the engine's verdict — that is phase 04's job (it sets the verdict; phase 05 records and commits).
- Does **not** loop. Phase 06 handles the iterate-or-finalize decision.
