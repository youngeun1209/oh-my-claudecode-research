# Phase 3 — Review

Invoke `@reviewer` to critique the prose phase 02 just wrote. Parse the output into a structured issues list and append a new entry to `reviews.json.runs`. This phase is the second half of each loop iteration; phase 04 reads its `issues` list to decide the verdict.

## Inputs (from phase 02)

| Name | Source | Purpose |
|---|---|---|
| `section_name` | phase 02 | Recorded in the reviews.json entry. |
| `section_path` | phase 02 | The reviewer reads this file from disk. |
| `venue` | phase 02 | Drives reviewer strictness. |
| `new_iter` | phase 02 | The iter that was just drafted/revised (i.e., the iter being reviewed). |
| `run_id` | loop primitive | UUID for the current run; used as the reviews.json entry `run_id`. |
| `iter_started` | loop primitive | Start-of-iter UTC ISO-8601, for the `started` field on the reviews entry. |
| `dispatch_meta` | phase 02 | Includes the writer-empty-output flag, if any. |

## Step 1 — Read the section content from disk

Read `section_path` into `current_content`. **Do not** trust the writer's in-memory output — read from disk so the reviewer sees exactly what was committed (including any framing the writer preserved or any post-write artifacts).

If the file is empty or whitespace-only (e.g., phase 02 declined to write due to an empty writer output):

- Skip the dispatch entirely.
- Fabricate a single `issues` entry to feed phase 04:
  ```jsonc
  {
    "severity": "major",
    "text":     "Section is empty — writer produced no prose this iteration.",
    "location": "<section_path>"
  }
  ```
- Continue at step 5 with this synthetic issues list. Do not call the reviewer on an empty section.

## Step 2 — Build the reviewer brief

Venue-specific strictness is conveyed through one line in the brief; the persona body already encodes the general standards. Build the `task_brief`:

```
Review the <section_name> section of the manuscript below as a peer reviewer for
<venue>. Apply the standards of <venue> — be strict but specific. Do not rewrite;
flag issues only.

Section content:
<current_content>

For each issue, return one JSON object with this exact shape:
  {
    "severity": "critical" | "major" | "minor" | "nit",
    "text":     "<one-to-three sentence description of the problem and what is required>",
    "location": "<line number, line range like L34-38, or a quoted phrase from the section>"
  }

Severity definitions (use them strictly):

  critical — fundamental flaw that blocks publication at <venue>. Examples:
             data insufficient for the claim, causal language without causal
             inference, ethics violation, fabricated result, framing dishonest.
             A `critical` is a structural problem the writer cannot fix in a
             single revision pass — it needs new analysis, new data, or a
             reframing decision.

  major    — significant concern that must be addressed before submission but
             is fixable in a revision. Examples: missing comparison to baseline,
             unclear methodology paragraph, jumped conclusion, weak prior-work
             coverage, missing effect size next to a p-value, structural
             paragraph reordering needed.

  minor    — improvement that helps but won't block acceptance. Examples:
             citation request for one specific claim, hedging language tightening,
             one clarification sentence, a single missing definition on first use.

  nit      — typography, formatting, style. Examples: inconsistent capitalization,
             a stray "very" or "clearly", an Oxford-comma slip.

Output: a JSON array of issue objects only. No preamble, no explanation, no
trailing prose. If the section has no issues at all, return an empty array [].
```

## Step 3 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":    "reviewer",
  "task_brief": <the brief built in step 2>,
  "state_slice": {
    "section":  <section_name>,
    "venue":    <venue>,
    "iter":     <new_iter>
  },
  "expected_output_schema": [
    { "severity": "critical|major|minor|nit", "text": "<string>", "location": "<string>" }
  ]
}
```

The dispatch primitive will try to parse a JSON array out of the agent response and return it as `parsed`. Capture both `output` (raw) and `parsed` (best-effort).

## Step 4 — Normalize the issues list

Apply in order:

1. **Parse-success case.** If `parsed` is a non-null list:
   - Drop any entry that isn't an object with at least a `severity` field.
   - For each remaining entry, normalize:
     - `severity` → lowercase. If not in `{critical, major, minor, nit}`, coerce to `major` and append `[severity-coerced from <original>]` to the `text`.
     - `text` → string. If missing, use `(no description)`.
     - `location` → string. If missing, use `(unspecified)`.
   - Result: a cleaned list of `{severity, text, location}` dicts.

2. **Parse-failure case.** If `parsed` is null OR not a list:
   - Treat the entire raw `output` as one `major` issue:
     ```jsonc
     {
       "severity": "major",
       "text":     "Reviewer output did not parse as a JSON array. Raw output preserved here for the writer's next pass: <output truncated to 1500 chars>",
       "location": "(unparseable)"
     }
     ```
   - Do **not** abort. Phase 04 will see one `major` and most likely emit `CONTINUE` (or `HALT` at max_iter), so the next iter's writer gets a clean re-review.

3. **Empty-section short-circuit.** If step 1 produced the synthetic empty-section issue, skip this step entirely — that issues list is already canonical.

## Step 5 — Append to `reviews.json`

Read `reviews.json` via [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = reviews`. Append one new entry to `reviews.json.runs`:

```jsonc
{
  "run_id":  "<run_id from the loop primitive>",
  "engine":  "iterate-revision",
  "section": "<section_name>",
  "iter":    <new_iter>,
  "venue":   "<venue>",
  "started": "<iter_started>",
  "ended":   "<UTC ISO-8601 now>",
  "issues":  <normalized list from step 4>,
  "verdict": null,
  "reason":  null
}
```

`verdict` and `reason` are **null at this point** — phase 04 fills them in. The append still happens here so the issues land on disk even if the user Ctrl-Cs between phase 03 and phase 04.

Write `reviews.json` back atomically (tmp + rename).

Update `paper.json.sections[section_name].last_review_id = <run_id>`. Write `paper.json` back atomically. This pointer lets phase 02 of a subsequent run find the most recent review quickly.

## Step 6 — Hand off to phase 04

Pass forward to phase 04:
- `section_name`, `venue`, `new_iter`, `max_iter` (`max_iter` flows through from phase 01)
- `run_id`, the entry index in `reviews.json.runs` (so phase 04 can update verdict/reason in place)
- The normalized `issues` list
- The `last_output` dict in the shape phase 04 expects (`{parsed: {issues: [...]}, output: <raw>, ...}`) so the orchestrate `evaluate` primitive can read `last_output.parsed.issues` per its dotted-path contract.

## Failure modes

| Condition | Behavior |
|---|---|
| Section file unreadable | Bubble the OS error. Loop primitive emits BLOCKED. |
| Section file empty | Skip dispatch; synthesize one `major` issue (step 1). |
| Reviewer dispatch errors out | Loop primitive catches in its step 3b and emits BLOCKED. |
| Reviewer returns empty string | Treat as one `major` "Reviewer returned empty response" issue; proceed to phase 04 (likely CONTINUE / HALT). |
| Reviewer JSON parse fails | Treat raw output as one `major` issue (step 4 case 2). Continue. |
| `reviews.json` write fails | Bubble the OS error. The loop primitive will catch and BLOCKED — but the entry was the only durable record of this iter's issues, so the run's effective state is "iter ran, results lost". Phase 05 should surface this. |

## What this phase does NOT do

- Does **not** compute the verdict. Phase 04 does that.
- Does **not** mutate `paper.json.sections[name].status`. Phase 04 does that based on the verdict.
- Does **not** auto-resolve missing-citation flags by calling `verify-citation`. Those land as plain `major`/`minor` issues per Phase 1 decision Q3.
- Does **not** retry on parse failure. One dispatch per iter. Bad parses become `major` issues; the next iter re-reviews.
- Does **not** show the reviewer prior iterations' issues. The reviewer reads the section fresh every iter, to prevent "you already fixed this" bias (locked constraint, phase-1-iterate-revision.md §7).
