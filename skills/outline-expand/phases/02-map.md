# Phase 2 — Map (parallel dispatch)

Build N per-section `task_brief` strings and dispatch `@paper-writer` once per draftable section. **All N dispatches are emitted in a single message** so Claude Code's Agent tool fans them out in parallel — this is the entire point of the map shape, and the demonstration this engine exists to ship.

This phase composes [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) N times. The orchestrate `loop` primitive is **not** used — there is no iteration. Each dispatch is one-shot; phase 03 reduces the outputs.

## Inputs (from phase 01)

| Name | Source | Purpose |
|---|---|---|
| `paper_state` | phase 01 | Parsed `paper.json` dict; carried forward through phases. |
| `manuscript_root` | phase 01 | For brief context (writers reference cross-section paths). |
| `section_plan` | phase 01 | List of per-section dicts: `{name, path, outline, current_iter, current_status}`. |
| `nomenclature_payload` | phase 01 | Shared string; identical across all N dispatches. |
| `outline_path` | phase 01 | For the run-log only. |

## Step 1 — Generate the run id

Generate a UUID (v4) string. Call it `run_id`. Phase 03 and phase 04 reference the same id.

## Step 2 — Append run-start to `_run-log.jsonl`

One line, atomic append (mirrors the loop primitive's start-record format so JSONL readers don't need to special-case this engine):

```jsonc
{
  "run_id":   "<uuid>",
  "engine":   "outline-expand",
  "args":     {
    "outline_path":     "<outline_path>",
    "sections":         [<name> for each entry in section_plan],
    "manuscript_root":  "<manuscript_root>",
    "nomenclature_src": "file | stub"
  },
  "started":  "<UTC ISO-8601>",
  "phase":    "start"
}
```

Use `open(...,"a")` + `flush` + `fsync` semantics. If the append fails (disk full, permission denied), abort — running without a log trail is unsafe for a multi-dispatch run.

Record `run_started_at` for the phase 04 end-record.

## Step 3 — Build the per-section task briefs

For each entry in `section_plan`, build one `task_brief` string. The brief shape is identical across sections; only the substituted variables differ.

### Section length defaults (matches `/iterate-revision` phase 02)

| Section | Default length range | Note |
|---|---|---|
| `abstract` | 150–250 words | Many venues cap at 150 or 250. |
| `introduction` | 600–900 words | Longer for review-heavy venues. |
| `methods` | 800–1500 words | Some venues move detail to supplementary. |
| `results` | 700–1200 words | Tracks figure count. |
| `discussion` | 600–1000 words | Some venues merge with Results. |
| other | "match the section's role in the manuscript" | — |

Resolve a length range for each section by name (lowercased). Unknown names get the catch-all fallback.

### Cross-reference context

For each section being drafted, build a one-line cross-reference list naming the other drafted/approved sections (so the writer knows what context it can lean on). Pull from `paper_state.sections[k]` where `k != name` and `status in {drafted, revising, approved}`. Format:

```
- <key>: <paper_state.sections[k].path> (status=<status>, iter=<iter>)
```

If no other sections are drafted, render `(no other sections drafted yet — this is part of a fresh map-reduce expansion)`.

### Mode decision per section

Inspect the section file on disk:

- If the file does not exist OR is empty (after stripping LaTeX `%`-comments for `.tex`), set `mode = "DRAFT"`.
- If the file exists and has non-trivial content, set `mode = "DRAFT-OVERWRITE"` only when the section name was passed explicitly in `--sections` (phase 01's guard already cleared this case). Otherwise phase 01 would have skipped the section. The mode label is informational; the writer brief is identical except for one extra warning line.

For `DRAFT-OVERWRITE`, prepend this line to the writer brief, **before** the outline excerpt:

```
NOTE: This section file already has content. You are re-drafting at the user's
explicit request (--sections <name>). The existing content will be overwritten
by your output. Take the existing prose into consideration only as context —
your output is the new section.
```

Also read the existing content and embed it under a `Existing content (for context):` block after the outline. For pure `DRAFT` mode, this block is omitted.

### The brief template

For each section, build:

```
Draft the <section_name> section for "<paper_state.title or 'untitled manuscript'>",
target venue <paper_state.venue or '(venue not set in paper.json)'>.

Hypothesis: <paper_state.hypothesis or '(unspecified)'>.

<DRAFT-OVERWRITE warning if applicable>

Outline excerpt for this section (verbatim from <outline_path>):

<section_plan[i].outline>

Length target: <range from the table above>.

Shared nomenclature (use these terms consistently; this payload is shared
across all sections being drafted in this run, so other writers will see the
same list):

<nomenclature_payload>

Cross-reference context (read for consistency; do NOT edit these files):
<cross-reference list from above>

Manuscript root: <manuscript_root>
This section's path on disk: <section_plan[i].path>

<Existing content block, only in DRAFT-OVERWRITE mode>

Conventions (binding):
- Use \citep{...} placeholders for citations. If no citekey is known yet,
  write [CITE: <one-line claim>] — @literature-curator will resolve later.
- Use \ref{fig:<label>} for figure references. Do not invent figure files.
- Do not edit main.tex or any non-section file.
- Do not edit references.bib or .claude/agent-memory/paper-writer/nomenclature.md
  in this dispatch — those are owned by @literature-curator and the user
  respectively. If you make a terminology decision, log it back to the
  caller in the form: TERMINOLOGY-DECISION: <term> = <chosen-form> (reason: <reason>).
  The caller will surface these.

Output:
Return the section prose only. No metadata, no commentary, no preamble.
Begin with the first sentence of the section body. If you logged any
TERMINOLOGY-DECISION lines, place them at the very end of your response,
each on its own line, after the prose.
```

Record each brief in a list `dispatch_specs` paired with the section name and path.

## Step 4 — Build the N dispatch specs

For each entry in `section_plan`, assemble one dispatch spec in the shape `phases/02-dispatch.md` expects:

```jsonc
{
  "persona":     "paper-writer",
  "task_brief":  "<the brief built in step 3>",
  "state_slice": {
    "title":           "<paper_state.title>",
    "venue":           "<paper_state.venue>",
    "hypothesis":      "<paper_state.hypothesis>",
    "section":         {
      "name":   "<name>",
      "path":   "<path>",
      "status": "<current_status>",
      "iter":   <current_iter>,
      "outline_source": "outline-expand-run/<run_id>"
    },
    "manuscript_root": "<manuscript_root>"
  },
  "expected_output_schema": null
}
```

`expected_output_schema` is `null` for all N dispatches — writers return free prose, not JSON.

## Step 5 — Dispatch all N in a single message (the map step)

This is the parallel-dispatch demonstration. The orchestrate dispatch primitive at [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) ordinarily handles one Agent-tool invocation per call. For the map step, emit **N Agent-tool calls in a single assistant message** so Claude Code's runtime can run them in parallel.

Operationally:

1. Build an `Agent` tool call per dispatch spec, with:
   - `subagent_type`: `"general-purpose"` (per orchestrate phase 02 step 4 contract).
   - `description`: `"omcr/paper-writer: outline-expand <section_name>"`.
   - `prompt`: the assembled prompt per orchestrate phase 02 step 3 (persona body + `---` + Task + `---` + State slice + `---` + Expected output (omitted, since `expected_output_schema` is null)).
2. Place all N tool calls in **one assistant message**. Claude Code's documented behavior is to dispatch parallel-tool-calls in the same message concurrently. Do not split into multiple messages — that serializes them.
3. Collect the N responses. Each is a dict in the shape orchestrate phase 02 returns:
   ```jsonc
   {
     "output":    "<the writer's prose, plus optional trailing TERMINOLOGY-DECISION lines>",
     "persona":   "paper-writer",
     "timestamp": "<UTC ISO-8601>"
   }
   ```

If a dispatch errors (Agent tool returns an error for one of the N), capture the error message and mark that section as `failed` in the per-section result. **Do not abort the whole run** — partial success is the contract. The other N−1 sections' outputs are still durable.

### Persona body inlining

Following orchestrate phase 02 step 1: read `<plugin_root>/agents/paper-writer.md` exactly once at the start of phase 02, strip its YAML frontmatter (step 2 of the primitive), and reuse the stripped body across all N prompts. This avoids re-reading the persona file N times. The persona body is identical for every dispatch in a single run — only the task brief and state slice vary.

If `$CLAUDE_PLUGIN_ROOT/agents/paper-writer.md` is unreachable, abort with the message specified by orchestrate phase 02's error contract:

```
dispatch: persona file agents/paper-writer.md not found at plugin root
```

The whole map step fails (no dispatches were sent yet). The user re-installs the plugin.

## Step 6 — Build the per-section dispatch result list

For each dispatch, assemble:

```jsonc
{
  "name":          "<section name>",
  "path":          "<section_plan[i].path>",
  "status":        "ok | failed",
  "output":        "<prose | null if failed>",
  "error":         "<error message | null if ok>",
  "timestamp":     "<UTC ISO-8601 from the dispatch>",
  "current_iter":  <section_plan[i].current_iter>,
  "current_status":"<section_plan[i].current_status>"
}
```

Record this list as `dispatch_results`. Phase 03 walks it to do the writes.

## Step 7 — Extract TERMINOLOGY-DECISION lines

Scan each dispatch's `output` for trailing lines matching:

```
TERMINOLOGY-DECISION: <term> = <chosen-form> (reason: <reason>)
```

For each match:
1. Strip the line from the prose (so phase 03 writes prose only, not the metadata footer). The marker line is at the end of the response; trim trailing whitespace-only lines after stripping.
2. Record the decision into a per-run list `terminology_decisions`:
   ```jsonc
   { "section": "<name>", "term": "<term>", "form": "<chosen-form>", "reason": "<reason>" }
   ```

Phase 04 surfaces this list to the user. The engine does **not** edit `nomenclature.md` on the user's behalf — the writer can do that during its dispatch if it chooses, but auto-editing the canonical nomenclature file from a parallel run is unsafe (two writers editing simultaneously). The decisions list is surfaced as a suggestion for the user.

## Step 8 — Hand off to phase 03

Pass forward to phase 03:
- `paper_state` (unchanged; phase 03 writes back)
- `manuscript_root` (for the drift artifact)
- `section_plan` (the original plan, for phase 03's comparison)
- `dispatch_results` (the per-section result list from step 6)
- `terminology_decisions` (from step 7, may be empty)
- `run_id`, `run_started_at` (for phase 04 closing record)

## Failure modes

| Condition | Behavior |
|---|---|
| `_run-log.jsonl` append fails | Abort. Running without a log trail is unsafe for a multi-dispatch run. |
| `paper-writer.md` persona file missing | Abort the whole map step (orchestrate phase 02 contract). No dispatches sent. |
| 1 of N dispatches errors | Record `status: "failed"` for that entry; continue. Phase 03 skips it. Phase 04 reports the partial. |
| All N dispatches error | The map step "succeeded" (in the sense of running its plan), but `dispatch_results` has zero `ok` entries. Phase 03 will write zero files and update zero status fields; phase 04 reports the all-fail case. |
| A dispatch returns empty prose | Mark `status: "failed"`, `error: "writer returned empty prose"`. Phase 03 does **not** write an empty file. |
| Cross-reference list refers to a section file that no longer exists | The brief still mentions it; the writer can ignore. Do not pre-verify the cross-ref files exist (cost is too high for marginal value). |

## What this phase does NOT do

- Does **not** loop. Each dispatch is one-shot. There is no reviewer pass in this engine.
- Does **not** write to disk except `_run-log.jsonl` (run-start record). Section files are written in phase 03.
- Does **not** edit `nomenclature.md`. TERMINOLOGY-DECISION lines are surfaced as suggestions in phase 04, not auto-merged.
- Does **not** retry failed dispatches. The user re-runs with `--sections <failed-name>`.
- Does **not** check for `[TBD: ...]` markers. The outline excerpt may contain them; the writer decides how to handle them. (`/iterate-revision` is the engine with the TBD guard.)
- Does **not** read `reviews.json`. There is no prior-review lookup — this is a fresh map-reduce expansion.
