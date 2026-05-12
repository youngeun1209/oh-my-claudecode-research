# Phase 2 — Action plan

Apply the **hardcoded bottleneck-ranker** to `current_picture` and emit a structured plan: one `next_action` (always single-target — Phase 3 §4) plus an `alternatives` list for the interactive-mode picker.

**Priority rules are hardcoded currently.** Per Phase 3 §5 (locked decision): no `CLAUDE.md`-driven override, no JSON config knob, no flag. Users who disagree on a specific run use `--interactive` (and pick from `alternatives`) or `--plan-only` (inspect and stop). The future backlog item is "user-configurable priority overrides" — keep this file's rules byte-stable currently so the future design has a clean baseline.

## Inputs

From phase 01:

- `current_picture` — the structured snapshot
- All carry-forward fields (run_id, mode, iter, max_iter, etc.)

## Hardcoded priority rules — applied in order, first match wins

### Priority 1 — Blocked sections (human action required → HALT)

Trigger: `current_picture.paper.sections_by_status.blocked` is non-empty.

Action: emit a HALT plan. There is no engine that auto-resolves a `blocked` section — the section reached `blocked` because a prior engine returned BLOCKED (e.g., `@reviewer` flagged a critical methodological issue). Continuing would just re-trip the same gate.

```jsonc
{
  "next_action": {
    "engine":   null,
    "args":     {},
    "reason":   "Section <name> is blocked: <last review's critical issue text>. Human action required.",
    "priority": 1,
    "verdict":  "HALT"
  },
  "alternatives": []
}
```

Phase 03 / 04 see `engine: null` and skip directly to phase 07.

### Priority 2 — Sections with `blocked-on-tbd` status

Trigger: `current_picture.paper.sections_by_status["blocked-on-tbd"]` is non-empty.

Action: HALT with TBD advisory. Same rationale as priority 1 — no engine auto-clears TBDs.

```jsonc
{
  "next_action": {
    "engine":   null,
    "args":     {},
    "reason":   "Section <name> is blocked-on-tbd. Resolve [TBD: ...] markers or re-invoke /iterate-revision <path> --allow-tbd.",
    "priority": 2,
    "verdict":  "HALT"
  },
  "alternatives": []
}
```

### Priority 3 — Critical citations missing

Trigger: **either** of:

- `current_picture.citations.cite_placeholder_total > 0` (manuscript text has `[CITE: ...]` placeholders), OR
- `current_picture.citations.queue_pending > 0` (`citations.json.queue` has entries with `status: pending`).

Action: dispatch `/literature-sweep <topic>`. The topic resolution rule:

1. If `paper_state.hypothesis` is non-null and non-`[TBD:`, use the first noun-phrase-shaped substring from the hypothesis (the supervisor's heuristic — phase 02 does not need an NLP pipeline; the engine will refine the search anyway).
2. Else if `citations.json.queue[0].context` exists, use the first 60 chars of that context as the topic.
3. Else: emit the action with `args: { topic: null }` and a `reason` noting that the topic must be supplied by the user. In `--auto` mode this triggers a halt at phase 03 (the engine cannot run without a topic).

```jsonc
{
  "next_action": {
    "engine":   "literature-sweep",
    "args":     { "topic": "<resolved topic>" },
    "reason":   "<N> [CITE:] placeholders in manuscript and <M> pending citations.json.queue entries. Dispatching /literature-sweep to populate references.bib.",
    "priority": 3
  },
  "alternatives": []
}
```

If a `@literature-curator` direct dispatch is more appropriate (e.g., only 1 placeholder, a known citekey is needed — not a topic sweep), the engine-of-choice belongs to the supervisor here. the current implementation always picks `/literature-sweep` because that engine is the leaf the supervisor is allowed to dispatch; the per-placeholder workflow (a direct `@literature-curator` dispatch with the placeholder context) is a future refinement and is not yet emitted by phase 02.

### Priority 4 — Unwritten sections (`status: empty`)

Trigger: `current_picture.paper.sections_by_status.empty` is non-empty.

Action branches on whether an outline exists:

1. **Outline path resolution.** For the first empty section in the list (in `paper.json.sections` declaration order), check:
   - If `sections_detail[name].outline` is a non-null inline string → use it (the engine receives it via the outline field; no file dispatch).
   - Else check whether `<manuscript_root>/outline.md` exists on disk.

2. **If an outline exists** (inline OR fallback file): dispatch `/outline-expand <outline-path>`. The engine handles every empty section in one map-reduce shot — phase 02 emits one plan, not N plans. The args set `--sections <comma-separated list of every empty section name>` for explicitness (the engine would default to "all not-approved sections", but the supervisor scope-limits it so the run is predictable).

   ```jsonc
   {
     "next_action": {
       "engine":   "outline-expand",
       "args":     { "outline_path": "<resolved-path>",
                     "sections":     "<comma-separated empty section names>" },
       "reason":   "<N> empty sections and an outline exists at <path>. Map-reduce drafting.",
       "priority": 4
     },
     "alternatives": [
       { "engine": "iterate-revision",
         "args":   { "section_path": "<first empty section's path>" },
         "reason": "Single-section draft instead of map-reduce.",
         "priority": 4 }
     ]
   }
   ```

3. **If no outline exists**: dispatch `/iterate-revision <section-path>` on the first empty section (single-section DRAFT mode).

   ```jsonc
   {
     "next_action": {
       "engine":   "iterate-revision",
       "args":     { "section_path": "<first empty section's path>" },
       "reason":   "Section <name> is empty and no outline.md exists. Single-section draft via /iterate-revision.",
       "priority": 4
     },
     "alternatives": []
   }
   ```

Single-target invariant: always one plan. If there are 3 empty sections, the user (or `--auto`) advances through them one iter at a time (the supervisor re-evaluates after each one — Phase 3 §3).

### Priority 5 — Drafted-but-unreviewed (`status: drafted`)

Trigger: `current_picture.paper.sections_by_status.drafted` is non-empty.

Action: dispatch `/iterate-revision <section-path>` on the first drafted section.

```jsonc
{
  "next_action": {
    "engine":   "iterate-revision",
    "args":     { "section_path": "<first drafted section's path>" },
    "reason":   "Section <name> is drafted; reviewer pass needed.",
    "priority": 5
  },
  "alternatives": [
    { "engine": "iterate-revision",
      "args":   { "section_path": "<next drafted section's path>" },
      "reason": "Or run on <name2> first.",
      "priority": 5 }
    // up to 3 alternatives if more drafted sections exist
  ]
}
```

`alternatives` is non-empty here because the user may have a preferred order (e.g., methods before results). In `--auto` mode `alternatives` is ignored and the first one is dispatched.

### Priority 6 — Pending reviewer rebuttals

Trigger: `current_picture.rebuttals.unresolved` is non-empty.

Action: dispatch `/respond-reviewer <letter>` on the first unresolved entry's `review_letter` path.

```jsonc
{
  "next_action": {
    "engine":   "respond-reviewer",
    "args":     { "letter_path": "<first unresolved rebuttal's review_letter>" },
    "reason":   "Rebuttal for <letter-path> has <N> unresolved comments (deferred/disputed) or run-level HALT.",
    "priority": 6
  },
  "alternatives": [
    // additional unresolved letters, up to 3
  ]
}
```

### Priority 7 — Figures with mismatched briefs

Trigger: `current_picture.figures.diverged` is non-empty (entries where `brief_status: approved` but `impl_status != approved`) OR `current_picture.figures.blocked` is non-empty (entries where the latest critique returned BLOCKED — typically a structural redesign was flagged).

Action: dispatch `/figure-bake <fig-id>`.

```jsonc
{
  "next_action": {
    "engine":   "figure-bake",
    "args":     { "fig_id": "<first diverged or blocked fig-id>" },
    "reason":   "Figure <fig-id>: brief approved but impl <impl_status> (or critique BLOCKED on last run).",
    "priority": 7
  },
  "alternatives": [
    // additional fig-ids, up to 3
  ]
}
```

### Priority 8 — Submission ready

Trigger: ALL of:

- `current_picture.paper.sections_by_status.approved` covers every section (i.e., all status values are `approved`).
- `current_picture.figures.all_done == true`.
- `current_picture.citations.queue_pending == 0` AND `current_picture.citations.cite_placeholder_total == 0`.
- `current_picture.rebuttals.unresolved` is empty.

Action: emit DONE. Phase 04 will set `paper_state.submission_ready = true` and write it atomically (this is the one place the supervisor mutates `paper.json` directly — every other write goes through an engine).

```jsonc
{
  "next_action": {
    "engine":   null,
    "args":     {},
    "reason":   "All sections approved, all figures done, all citations verified, all rebuttals addressed. Setting submission_ready.",
    "priority": 8,
    "verdict":  "DONE"
  },
  "alternatives": []
}
```

## Steps

### 1. Apply the rules in order

Iterate priorities 1 → 8. The **first** trigger that fires wins. Build the `plan` dict as shown in the rules above.

### 2. Anti-loop guard

Check `current_picture.prior_trail.consecutive_blocked`. If the same engine + same target combination returned BLOCKED on the immediately prior iter (i.e., `prior_trail.last_engine == plan.next_action.engine` AND `prior_trail.last_target` matches `plan.next_action.args` AND `prior_trail.last_verdict == "BLOCKED"`):

- Bump the plan's `priority` upward by emitting an inline note in `reason`: `"WARNING: prior iter already returned BLOCKED on this target — this is the consecutive failure."`
- If `current_picture.prior_trail.consecutive_blocked >= 2`: override the plan to a HALT with `reason: "Two consecutive BLOCKED on <engine>/<target>; supervisor will not retry. Resolve the blocker manually."`. Phase 04 propagates the HALT.

This is the only place phase 02 deviates from the priority rules table — and it deviates **toward halt**, never toward "try a different engine instead." That would violate Phase 3 §2 (halt-on-exception spirit) and §3 (engine-calls-engine: no, but also no implicit fallback dispatch).

### 3. Emit the structured plan

The plan dict, plus a one-line summary printed to the transcript:

```
[iter <iter>/<max_iter>] plan
  next:    <engine> <args>
  reason:  <reason>
  priority: <P>
  alts:    <N alternative(s) — see plan dump for picker>
```

If `engine == null`: print the verdict instead (`HALT` or `DONE`) with the reason.

### 4. Hand off to phase 03

Pass forward:

- `plan` dict
- `current_picture` (phase 04 may re-reference it for cost projection state slice)
- All carry-forward fields

## Failure modes

| Condition | Behavior |
|---|---|
| No priority triggers (paper has zero sections, no citations, no figures, no rebuttals) | Emit priority 8 DONE — submission_ready is vacuously true. This is the empty-project / `/omcr-setup`-only state. Phase 07 will note "no work to drive". |
| `prior_trail.consecutive_blocked >= 2` on the matched plan | Override to HALT with the anti-loop reason. |
| Priority 4 outline-path resolution fails (no inline outline, no outline.md on disk) | Fall through to the no-outline branch (single-section `/iterate-revision`). Do not abort. |
| Priority 3 topic resolution returns null | Emit the plan with `topic: null` and a reason flagging that the user must supply it. In `--auto`, phase 03 will halt because the engine cannot dispatch with a null required arg. |

## What this phase does NOT do

- Does **not** dispatch any engine. Plan generation only.
- Does **not** mutate any state file. Read-only against `current_picture`.
- Does **not** apply safety gates. Phase 04 does that, post-confirmation.
- Does **not** combine multiple engines into one plan. Single-target invariant (Phase 3 §4).
- Does **not** read `_run-log.jsonl` itself (it consumes `current_picture.prior_trail` and `current_picture.recent_runs`, which phase 01 populated).
- Does **not** override the priority table from a CLAUDE.md block. Hardcoded currently per Phase 3 §5.
- Does **not** rank alternatives by anything other than the natural order of the underlying state (e.g., section declaration order in `paper.json`). a future iteration may revisit.
