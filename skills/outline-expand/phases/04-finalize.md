# Phase 4 — Finalize

User-facing summary after the reduce step lands. Renders the per-section verdicts, the drift count, and pre-filled `$iterate-revision` lines so the user can refine each new draft. Appends the close + summary records to `_run-log.jsonl`. No git commit, no push, no auto-call of any other engine.

This phase is engine-specific logic — no orchestrate primitives are imported. The orchestrate `loop` primitive was never used by this engine (no iteration), so the close record is emitted directly here, mirroring the loop primitive's format so JSONL readers don't need to special-case `outline-expand`.

## Inputs (from phase 03)

| Name | Source | Purpose |
|---|---|---|
| `paper_state` | phase 03 | Final state of `paper.json`; used to pick "next suggested section" hints. |
| `manuscript_root` | phase 03 | Surfaced in the summary so the user knows where the drift file lives. |
| `write_results` | phase 03 | List of per-section write outcomes. Drives the verdict row. |
| `drift_clusters` | phase 03 | Drift list (may be empty); count surfaced. |
| `terminology_decisions` | phase 03 | Writer-logged decisions; count surfaced. |
| `drift_artifact_path` | phase 03 | Pointer surfaced in the summary. |
| `run_id` | phase 02 | UUID; ties this summary to the `_run-log.jsonl` records. |
| `run_started_at` | phase 02 | For duration computation. |

## Step 1 — Tally per-section outcomes

From `write_results`:

```
n_drafted   = count of entries with wrote == true
n_failed    = count of entries with wrote == false
n_total     = len(write_results)
```

Group failed entries by reason prefix:
- `dispatch failed: ...` (dispatch errored in phase 02)
- `parent directory ...` (filesystem)
- `write failed: ...` (Write tool / hook block)

Each failure category gets a one-line tally in the user summary.

## Step 2 — Compute duration

`ended_at = <UTC ISO-8601 now>`
`duration_sec = ended_at - run_started_at` in whole seconds.

Format identically to `$iterate-revision` phase 05:
- `< 60s` → `"<N>s"`
- `< 3600s` → `"<Nm <S>s"` (e.g., `2m 34s`)
- otherwise → `"<H>h <M>m"` (e.g., `1h 04m`)

## Step 3 — Determine the overall verdict

`$outline-expand` does not use the four-verdict severity rule (this engine has no reviewer dispatch). The verdict surfaced in the user summary follows this simpler table:

| Condition | Verdict | Status |
|---|---|---|
| `n_drafted == n_total` AND `n_total > 0` | `DONE` | "all sections drafted" |
| `0 < n_drafted < n_total` | `PARTIAL` | "<n_drafted> of <n_total> sections drafted; <n_failed> failed" |
| `n_drafted == 0` AND `n_total > 0` | `BLOCKED` | "no sections drafted — all <n_total> dispatches failed" |
| `n_total == 0` | `DONE` (no-op) | "nothing to draft (phase 01 returned an empty section_plan)" |

The DONE-no-op case can only reach phase 04 if phase 01 explicitly handed off a zero-length plan without aborting, which it does not — phase 01 exits cleanly in the zero-length case. So in practice, phase 04 only sees DONE / PARTIAL / BLOCKED.

Note: `HALT` is not a possible verdict for this engine. There is no iteration cap to exceed. The orchestrate verdict vocabulary (DONE/CONTINUE/BLOCKED/HALT) does not apply directly here — this engine surfaces its own three-way verdict in the user summary, and the `_run-log.jsonl` close record uses the closest orchestrate value (see step 5).

## Step 4 — Render the user summary

Print this block to the transcript:

```
Engine:        outline-expand
Outline:       <args.outline_path from the run-start record>
Verdict:       <DONE | PARTIAL | BLOCKED>
Sections:      <n_drafted> drafted, <n_failed> failed, <n_total> total
Duration:      <formatted duration>
Run id:        <run_id>

Per-section results:
  [ok]   <name1>  →  <path1>  (<bytes1> bytes, status: <before> → <after>)
  [ok]   <name2>  →  <path2>  (<bytes2> bytes, status: <before> → <after>)
  [fail] <name3>  →  <path3>  (<reason>)
  ...

Terminology drift report: <drift_artifact_path>
  Drift clusters:                <len(drift_clusters)>
  Writer-logged decisions:       <len(terminology_decisions)>
  Top clusters: <comma-separated list of normalized forms from the top 3 drift_clusters, or "(none)">
```

Then append one of the verdict-specific blocks below.

### DONE block

```
All sections drafted. paper.json: <n_drafted> sections set to status="drafted", iter=1.

Suggested next:
  $iterate-revision <path1>
  $iterate-revision <path2>
  ...
  (one $iterate-revision per drafted section, ordered by section_plan order)

Review the drift report before iterating — terms flagged there will resurface as
reviewer issues in $iterate-revision unless the user reconciles them first.
```

The `$iterate-revision <path>` lines should be pre-filled with the actual section paths from `write_results` (only entries with `wrote == true`), in the original `section_plan` order.

### PARTIAL block

```
Partial success. <n_drafted> of <n_total> sections drafted.

Failed sections (<n_failed>):
  <name>: <reason>
  ...

To retry only the failed sections:
  $outline-expand <outline_path> --sections <comma-separated failed names>

To refine the sections that did succeed:
  $iterate-revision <path>
  ...

The drift report covers the <n_drafted> sections that did succeed.
```

### BLOCKED block

```
No sections drafted. All <n_total> dispatches failed.

Failure breakdown:
  <reason category 1>: <count>
  <reason category 2>: <count>
  ...

Common causes:
- Plugin manifest unreachable (paper-writer persona file missing). Verify the
  plugin is installed: ls $CODEX_PLUGIN_ROOT/agents/paper-writer.md
- PII-scrub hook blocking writes. Check hooks/pii-scrub.sh against your section
  paths.
- Filesystem permissions on manuscript_root. Verify: ls -ld <manuscript_root>

No paper.json state was changed. Safe to re-run after addressing the cause.

Full log: .omx/state/omxr/_run-log.jsonl (run_id=<run_id>)
```

### Writer-logged terminology decisions footer

After whichever verdict block was rendered above, if `terminology_decisions` is non-empty, append:

```
Writer-logged terminology decisions (also in the drift report):
  (in <section>) <term> = <chosen-form>  — <reason>
  ...

Consider adopting these into .omx/omxr/agent-memory/paper-writer/nomenclature.md
so future map-reduce expansions converge.
```

If `terminology_decisions` is empty, omit this footer entirely.

## Step 5 — Append close record to `_run-log.jsonl`

Mirror the orchestrate loop primitive's close-record format (`phase: "end"`), so JSONL readers that pair start-end records by `run_id` keep working without a special case:

```jsonc
{
  "run_id":       "<run_id>",
  "engine":       "outline-expand",
  "args":         {
    "outline_path":     "<outline_path>",
    "sections":         [<names from section_plan>],
    "manuscript_root":  "<manuscript_root>",
    "nomenclature_src": "file | stub"
  },
  "started":      "<run_started_at>",
  "ended":        "<ended_at>",
  "iter_count":   1,
  "verdict":      "<DONE-or-BLOCKED-or-HALT — mapping below>",
  "reason":       "<the one-line summary from step 3>",
  "tokens_used":  <sum of tokens across all phase-02 dispatches; 0 if unavailable>,
  "phase":        "end"
}
```

**Verdict mapping for the close record.** Since `$outline-expand`'s three-way verdict (DONE / PARTIAL / BLOCKED) doesn't map cleanly to the orchestrate four-verdict set (DONE / CONTINUE / BLOCKED / HALT), use this mapping:

| Engine verdict (step 3) | `_run-log.jsonl` verdict |
|---|---|
| DONE | `DONE` |
| PARTIAL | `DONE` (with `reason` describing the partial) — the run completed; PARTIAL is a per-section quality signal, not a run-failure signal |
| BLOCKED | `BLOCKED` |

`HALT` never appears in this engine's run log — there is no iteration cap.

`iter_count` is always `1` for this engine — it doesn't iterate. Logged for schema consistency with multi-iter engines.

`tokens_used` is the sum of `tokens_used` per dispatch, if the Agent tool surfaced it. If unavailable, log `0`; the user reads per-dispatch detail from the surrounding `phase: "start"` line and any per-dispatch tracking the runtime provides.

## Step 6 — Append summary record to `_run-log.jsonl`

Add one more line with `phase: "summary"` so a JSONL reader can grep `phase == "summary"` to get per-run user-facing summaries without parsing the full transcript (matches `$iterate-revision` phase 05 convention):

```jsonc
{
  "run_id":          "<run_id>",
  "engine":          "outline-expand",
  "phase":           "summary",
  "outline_path":    "<outline_path>",
  "manuscript_root": "<manuscript_root>",
  "verdict":         "<DONE | PARTIAL | BLOCKED>",
  "reason":          "<one-line summary from step 3>",
  "n_drafted":       <n_drafted>,
  "n_failed":        <n_failed>,
  "n_total":         <n_total>,
  "sections":        [
    { "name": "<name>", "path": "<path>", "wrote": <true|false>, "reason": "<reason or null>" },
    ...
  ],
  "drift_clusters_count":         <len(drift_clusters)>,
  "terminology_decisions_count":  <len(terminology_decisions)>,
  "drift_artifact_path":          "<drift_artifact_path>",
  "duration_sec":    <int>,
  "tokens_used":     <int>,
  "summary_at":      "<UTC ISO-8601 now>"
}
```

Use the same write semantics as the loop primitive's append (orchestrate phase 04 step 2 / step 5): open in append mode, write one line of JSON followed by `\n`, `flush` + `fsync` if available.

If either the close-record append or the summary-record append fails, do **not** abort — the user has already seen the summary in the transcript. Log a warning:

```
outline-expand: failed to append to _run-log.jsonl (<error>). Run output above is
the canonical record of this run; paper.json on disk and terminology-drift.md are
durable.
```

## Step 7 — No git commit, no auto-iterate

Mirroring `$iterate-revision` phase 05 step 5: OMXR does **not** commit on the user's behalf from this phase. The drift artifact and section files are unstaged after the run. Users who want them committed run `git add -A && git commit` themselves.

This engine also does **not** auto-invoke `$iterate-revision`. Phase 2 decision §5 (engines are leaves) is binding. The user reads the suggested-next block and runs the engines they want.

A future iteration may add a `--auto-iterate` flag that chains `$iterate-revision` per section — but that decision is owned by Phase 3's `$supervisor-drive`, not by this engine.

## Failure modes

| Condition | Behavior |
|---|---|
| `write_results` is empty | Render the DONE-no-op block (should not occur — phase 01 exits cleanly in the zero-length case). |
| Duration calculation produces a negative number (clock skew) | Render `"<duration unavailable>"`; do not abort. |
| `_run-log.jsonl` append fails | Warn; do not abort. The transcript is the canonical user-facing record. |
| `paper_state.sections` is missing a key referenced in `write_results` (shouldn't happen — phase 03 mutates the same dict) | Render the entry's `before/after` as `"unknown"`; do not abort. |
| `drift_artifact_path` is null (phase 03 failed to write) | Render the drift counts inline; replace the "Terminology drift report: ..." pointer line with `"Terminology drift report: (write failed in phase 03 — see warnings above)"`. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure rendering + log appends.
- Does **not** mutate `paper.json` or any state file beyond `_run-log.jsonl`. Phase 03 owns the durable writes.
- Does **not** commit to git or push.
- Does **not** call `$iterate-revision`, `$sync`, or `$todofig`. Engines are leaves.
- Does **not** retry failed dispatches. The user re-runs with `--sections`.
- Does **not** auto-merge `terminology_decisions` into `nomenclature.md`. The user reads the suggestion footer and decides.
- Does **not** delete the drift artifact from a previous run. Phase 03 overwrites it; phase 04 only renders the path.
