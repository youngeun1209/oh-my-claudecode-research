---
name: figure-bake-implement
description: Phase 3 of /figure-bake. Dispatch @analysis-implementer with the brief + data_root to render a vector PDF at figures.json.figures[<fig-id>].vector_path, then auto-invoke the cropfig skill so manuscript + outline artifacts land in one pass.
---

# Phase 3 — Implement

Invoke `@analysis-implementer` to translate the brief from phase 02 into working code that actually runs and writes a vector PDF (or PNG) to `entry.vector_path`. After the implementer reports success, **auto-invoke the `cropfig` skill** so the manuscript-grade PDF and outline-grade PNG land in their canonical locations from the same crop decision.

This phase is the most expensive iteration step in the engine. It runs real code via Bash inside the dispatched subagent, and on top of that it pipes the result through the cropfig pipeline. The default `max_iter = 3` in the engine's SKILL.md is deliberately conservative for this reason.

## Inputs (from phase 02)

| Name | Source | Purpose |
|---|---|---|
| `fig_id` | phase 02 | Key in `figures.json.figures`. |
| `figures_state` | phase 02 | Parsed dict; `figures[fig_id]` is the entry this phase mutates. |
| `brief_text` | phase 02 | The descriptor's brief — the implementer's primary instruction source. |
| `data_root` | phase 01 (passed through phase 02) | Absolute path. The implementer reads inputs from here. |
| `code_dir` | phase 01 | Absolute path or null. The implementer writes its renderer script here. |
| `vector_path` | phase 01 | Absolute path to the PDF the implementer must produce. |
| `current_iter` | loop primitive | Iter being implemented. |
| `max_iter` | phase 01 | Surfaced to the implementer brief. |
| `brief_dispatched` | phase 02 | True if phase 02 ran the descriptor this iter; false if it reused an approved brief. |

## Step 1 — Guard on a missing brief

If phase 02 set `brief_dispatched == true` AND `brief_text` is empty (descriptor returned nothing), short-circuit:

- Do **not** dispatch the implementer (no point — it has no instructions).
- Set `figures_state.figures[fig_id].impl_status = "missing"`.
- Persist `figures.json` atomically.
- Fabricate a synthetic implementer "output" describing the missing brief, so the loop primitive's step 3b (which checks for dispatch errors) can route this to the verdict cleanly:

  ```jsonc
  {
    "output":    "(synthetic) phase 02 produced no brief — implementer skipped.",
    "persona":   "analysis-implementer",
    "timestamp": "<UTC ISO-8601 now>",
    "synthetic_error": "no-brief"
  }
  ```

- Skip step 2 through step 5; jump to step 6 (`Write impl_status`) which will set `impl_status = "missing"` and pass an empty render result to phase 04. Phase 04 will then fabricate a `critical` issue (`"Brief was not produced this iter; nothing to critique"`) which routes to BLOCKED in phase 05.

This guard prevents wasting an implementer dispatch on a no-op iter.

## Step 2 — Resolve the renderer script location

The implementer needs a place to write its Python (or other-language) script. Resolution order:

1. If `code_dir` (from phase 01 `--code-dir`) is non-null, use it.
2. Else if `figures_state.figures[fig_id].code_dir` is non-null (from a prior run), reuse that.
3. Else default to `<parent of vector_path>/code/`.

Expand `~` and resolve to an absolute path. `mkdir -p` the directory (idempotent). Record the resolved path into `figures_state.figures[fig_id].code_dir` and persist `figures.json` atomically.

The renderer script is named `<fig_id>.py` inside this directory (default). The implementer may choose a different name; if it does, it must report the chosen path in its output so this phase can capture it.

## Step 3 — Build the implementer task brief

Build the `task_brief` for `@analysis-implementer`:

```
Render figure "<fig_id>" for the manuscript.

Iter <current_iter> of <max_iter>. Previous iter's reviewer feedback (if any) is in the
"Reviewer concerns from previous iter" block below; address those concerns in your
revised renderer code.

Design brief (from @figure-descriptor):
<brief_text>

Data location:
  data_root = <data_root>
  Read input files from inside this directory only. Do not read from anywhere else
  on disk.

Outputs your code MUST write, at these exact paths:
  PDF (vector): <vector_path>
      The PDF must be true vector — text and lines stay sharp at any zoom. Use
      matplotlib's PDF backend or equivalent; do not rasterize panels unless the
      brief explicitly calls for an image-like panel (heatmap, photo).

Renderer script location:
  Write your rendering script to <code_dir>/<fig_id>.py (or a path of your choice
  inside <code_dir>/; if you choose differently, report the chosen path in your
  output). The script must:
    - Be self-contained (one file).
    - Be reproducible (set numpy.random seed if any randomness; document library
      versions in a top-of-file comment).
    - Be re-runnable from the command line with: python3 <script_path>
    - Read all inputs from <data_root>.
    - Write the PDF to <vector_path>.
    - Print one summary line on success: "OK <fig_id> -> <vector_path>".

<if entry.critiques is non-empty:>
Reviewer concerns from previous iter <entry.iter>:
<bulleted list of issues from entry.critiques[-1], rendered as
 "[<severity>] <location>: <text>" — sort critical, major, minor, nit>

Fix each critical and major concern in this iter. Address minors where doing so does
not require disproportionate rewrites; ignore nits unless trivially addressable.

Procedure:
  1. Write the script to <code_dir>/<fig_id>.py.
  2. Run it via Bash: python3 <code_dir>/<fig_id>.py. Pipe the script's output back.
  3. Verify the PDF exists at <vector_path> using ls -la. If it does not exist or is
     empty, the run failed — debug and re-run.
  4. Verify the PDF is non-trivial (size > 1 KB) and is a real PDF (first bytes "%PDF").
  5. Return one final response with this structure:

       ## Render result for <fig_id>

       Script: <absolute path of the script you wrote>
       Output: <absolute path of the PDF, must equal <vector_path>>
       Size:   <PDF size in bytes>
       Status: ok | failed

       <if ok:>
       Dependencies installed/used: <list libraries actually imported>

       <if failed:>
       Reason: <one-line summary>
       Last command + output:
       <verbatim Bash output showing the error>

If the script fails (traceback, missing library, missing data file), do NOT re-try
silently — return Status: failed with the verbatim error. The next iter will receive
this as feedback.

Do not edit any file outside <code_dir>/ and <vector_path>. Do not push to git.
```

## Step 4 — Dispatch

Call [`../../orchestrate/phases/02-dispatch.md`](../../orchestrate/phases/02-dispatch.md) with:

```jsonc
{
  "persona":     "analysis-implementer",
  "task_brief":  <the brief built in step 3>,
  "state_slice": {
    "fig_id":      <fig_id>,
    "iter":        <current_iter>,
    "max_iter":    <max_iter>,
    "vector_path": <vector_path>,
    "data_root":   <data_root>,
    "code_dir":    <code_dir>
  },
  "expected_output_schema": null
}
```

`expected_output_schema` is `null` — the implementer returns a structured markdown report (as specified in the task brief), not JSON. Phase 04 (reviewer) is where structured output matters.

The dispatch returns:
```jsonc
{
  "output":    "<the implementer's report — script path, output path, size, status>",
  "persona":   "analysis-implementer",
  "timestamp": "..."
}
```

## Step 5 — Parse the implementer's report and verify the artifact

Apply in order:

1. **Extract Status line.** Search the implementer's `output` for a line matching `^Status:\s*(ok|failed)$`. If multiple matches, take the last. If none, treat as `failed` with reason `"no Status: line in implementer output"`.

2. **On Status: ok.** Verify the artifact:
   - Stat `vector_path`. If the file does not exist on disk after the implementer claimed success, treat as `failed` with reason `"implementer reported ok but vector_path does not exist on disk"`.
   - Read the first 5 bytes of `vector_path`. If they are not the literal `%PDF-`, log a warning but proceed — some implementers may legitimately write a PNG when the brief asks for it. Cropfig (step 6) handles both, but the PDF→PNG path is preferred for manuscript-grade output.
   - Stat-check the file size. If < 1 KB, log a warning that the PDF may be empty / placeholder. Do not fail outright — phase 04's reviewer will catch a useless render.
   - Extract the implementer's reported script path (the `Script:` line from the report). Record into `figures_state.figures[fig_id].script_path` (an additive field; phase 01 didn't seed it, but persisting it here is consistent with the pattern of new optional fields being added by the phase that owns them).

3. **On Status: failed.** Extract the `Reason:` line and the verbatim `Last command + output` block from the report.
   - Do **not** abort. Phase 04 still runs — but it receives an explicit failure signal and synthesizes a `critical` issue for phase 05 to route to BLOCKED.
   - Do **not** retry the implementer in the same iter. The verdict-driven loop is the only retry mechanism (`CONTINUE` → next iter dispatches fresh).

## Step 6 — Auto-invoke `cropfig` (only if Status: ok)

When the implementer's `Status` was `ok` AND `vector_path` exists on disk, invoke the `cropfig` skill to produce the manuscript-grade vector PDF and outline-grade raster PNG from the same crop decision.

Read [`../../cropfig/SKILL.md`](../../cropfig/SKILL.md) and follow it exactly. The cropfig skill expects a deck file (`.key` or `.pptx`) by default; this phase's call is the **PDF-already-produced** pathway. Practical invocation pattern:

- `cropfig`'s funcs 2 and 3 can run independently of func 1 (the deck export). See the cropfig SKILL "Steps" section: "Steps 2 and 3 can run independently if a prior staging dir or PDF/PNG dir already exists."
- This phase's job is to stage the implementer's PDF into the shape cropfig expects, then call func 2 + func 3 over that staging dir.

Concretely:

1. Create a staging directory next to `vector_path`. Convention: `<parent of vector_path>/.figure-bake-stage-<fig_id>/`. `mkdir -p` it.
2. Copy `vector_path` into the staging dir with the name cropfig's func 2 expects: `<stage>/<fig_id>.pdf`. (cropfig's func 2 walks the stage dir for per-slide PDFs.)
3. Set the cropfig environment variables for this invocation:
   - `DECK_FILE` — set to `<parent of vector_path>/<fig_id>.pdf` (a notional deck path; cropfig's func 2/3 derive output dirs from this).
   - `MANUSCRIPT_DIR` — set to `<paper_state.manuscript_root>`.
   - `OUTLINE_FILE` — set to the user's outline path from CLAUDE.md `## Research stack` `outline_file` if available, else skip the func 3b outline embed (cropfig's SKILL handles a missing outline gracefully).
4. Run cropfig's `crop_figures.py` over the stage dir, writing to `<parent of vector_path>/pdf/` and `<parent of vector_path>/png/`.
5. Run cropfig's `upload_figures.py` to copy the cropped PDF into `<MANUSCRIPT_DIR>/figures/` (idempotent overwrite; the manuscript copy is the canonical artifact for `\includegraphics`). Skip the outline-embed half (3b) if no outline file is configured — phase 06 reminds the user to re-run `/sync` to embed once an outline exists.
6. Capture cropfig's stdout/stderr. On non-zero exit:
   - Do **not** fail the whole phase. The uncropped PDF at `vector_path` is still usable for the reviewer in phase 04.
   - Log a warning to the run log with cropfig's stderr.
   - Set a flag `cropfig_status = "failed"` (additive; phase 04 will mention this in the reviewer brief so the reviewer doesn't flag a "weird-looking border" as a brief-level concern when in fact cropfig didn't run).

   On success: `cropfig_status = "ok"` and record the cropped PDF path + the PNG path the reviewer should Read in phase 04.

7. Clean up the staging dir (`rm -rf <stage>`). The canonical outputs land under `<parent of vector_path>/pdf/<fig_id>.pdf` and `<parent of vector_path>/png/<fig_id>.png` per cropfig's output contract.

Persist into `figures_state.figures[fig_id]`:

- `cropped_pdf_path` = `<parent of vector_path>/pdf/<fig_id>.pdf` (the source-of-truth manuscript-grade PDF).
- `cropped_png_path` = `<parent of vector_path>/png/<fig_id>.png` (what phase 04 reads multimodally).
- `cropfig_status` = `"ok" | "failed" | "skipped"` (skipped = step 6 didn't run because Status was failed).

Persist `figures.json` atomically.

## Step 7 — Write `impl_status` and hand off

Based on the implementer's parsed status and cropfig's result:

| Implementer | cropfig | `entry.impl_status` |
|---|---|---|
| `ok` | `ok` | `"drafted"` |
| `ok` | `failed` | `"drafted"` (the uncropped PDF is still usable; phase 04 reads `vector_path` directly if no `cropped_png_path` exists) |
| `failed` | n/a (skipped) | `"missing"` |
| synthetic / no-brief | n/a | `"missing"` |

Note: `impl_status = "approved"` is only set by phase 05 after the reviewer signs off. Phase 03 never writes `"approved"`.

Also bump `entry.iter = current_iter + 1` here? **No** — keep the iter counter as the descriptor / implementer / reviewer triple's iteration. Phase 05 is the single point of `iter` increment so the count corresponds to "completed iters whose verdict was recorded". Phase 03 mid-iter `iter` writes would skew the loop primitive's accounting if the run is killed between phase 03 and phase 05.

Persist `figures.json` atomically.

Pass forward to phase 04:

- `fig_id`, `figures_state` (with updates)
- `current_iter`, `max_iter`
- `implementer_output` — the raw report string. Phase 04 includes it in the reviewer brief so the reviewer can cite the implementer's claims.
- `implementer_status` — `"ok" | "failed" | "no-brief"`.
- `render_pdf_path` — what phase 04 should treat as the renderer's PDF. Prefer `cropped_pdf_path` when cropfig succeeded; else `vector_path` (uncropped).
- `render_png_path` — what phase 04 should Read multimodally. `cropped_png_path` if available; else `null` (phase 04 will fall back to reading the PDF directly via Read, which still works but is slower).
- `cropfig_status` — included for the reviewer brief.

## Failure modes

| Condition | Behavior |
|---|---|
| Implementer dispatch errors out (Agent tool error) | Loop primitive catches in step 3b and emits BLOCKED. `entry.impl_status` is left at its prior value; the loop's BLOCKED reason captures the underlying error. |
| Implementer returns `Status: failed` | Phase 03 sets `impl_status = "missing"` and hands a `failed` signal to phase 04. Phase 04 synthesizes a `critical` issue; phase 05 emits BLOCKED. |
| Implementer returns `Status: ok` but `vector_path` is absent on disk | Treated as `failed` with reason "implementer reported ok but vector_path does not exist on disk". |
| `vector_path` exists but is not a PDF | Warn but proceed. Phase 04's reviewer is the gate. |
| `cropfig` fails | Warn; `cropfig_status = "failed"`. The reviewer reads the uncropped `vector_path` instead. The run is not aborted. |
| `mkdir -p <code_dir>` fails | Bubble the OS error; loop primitive emits BLOCKED. The implementer can't write its script. |
| Implementer claims to have written a script outside `code_dir` | Captured in `script_path`. Warn but do not move the file — the user's project layout is their call. |

## What this phase does NOT do

- Does **not** dispatch `@figure-descriptor`. Phase 02 owns that.
- Does **not** dispatch `@reviewer`. Phase 04 owns that.
- Does **not** retry the implementer on traceback. The retry mechanism is the engine's loop (CONTINUE → fresh next iter); intra-iter retry would mask the bug from the verdict logic.
- Does **not** open / edit `<vector_path>` after the implementer wrote it. The PDF is treated as opaque; cropfig (step 6) is the only post-processing step.
- Does **not** invoke any slash command. Cropfig is a skill, not a command — invoking it is allowed per Phase 2 decision §5.
- Does **not** push the cropped artifact to a remote (Overleaf, S3, etc.). That belongs to `/sync` or `manuscript-scaffold`'s commit-push phase.
- Does **not** update `paper.json`. Only `figures.json` is touched.
- Does **not** auto-install missing Python libraries. If the implementer hits `ModuleNotFoundError`, that lands in `Status: failed` with the verbatim traceback; phase 05 BLOCKED, and the user installs the library before re-running.
