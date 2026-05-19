---
name: respond-reviewer-phase-01-parse-letter
description: Auto-detect the review letter's format from extension, parse the file into a structured comments list with stable IDs (`R1.1`, `R2.3`, …), and prime the state files this engine touches. Output of this phase is either an early exit (missing file / unsupported extension / unparseable) or a primed comments list + parsed `paper.json` + bootstrapped `rebuttals.json` ready for phase 02.
---

# Phase 1 — Parse the letter

Validate the call, resolve state, auto-detect the input format, parse the letter into structured comments. Output of this phase is either:
- An early exit (file missing, unsupported extension, or zero comments parseable), or
- A `comments` list + resolved `manuscript_root` + parsed `paper.json` + bootstrapped `rebuttals.json`, ready for phase 02.

## Inputs

From the slash command:
- `<review-letter-path>` — positional, required.
- `--manuscript <root>` — optional, falls back to `paper.json.manuscript_root`.
- `--draft-only` — optional flag, default false. (Pure pass-through here; phase 03 enforces.)
- `--format md|latex` — optional, default `latex`. (Output format only; this phase only auto-detects **input** format.)

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate `<review-letter-path>`

- Interpret the path relative to the project root (the Claude Code session's working directory).
- Verify the file exists. If not, abort with:
  ```
  respond-reviewer: <review-letter-path> not found.
  Pass a path relative to the project root, or an absolute path.
  ```
- Verify the extension is one of `.md`, `.txt`, `.tex`. If not, abort with:
  ```
  respond-reviewer: unsupported review-letter extension <ext>.
  Must be one of: .md, .txt, .tex.
  ```

Record the absolute path and the extension; subsequent steps need both.

### 2. Auto-detect input format

Map extension to a parser mode:

| Extension | `input_format` |
|---|---|
| `.md` | `markdown` |
| `.txt` | `markdown` (plain text uses markdown's lenient comment-detection rules) |
| `.tex` | `latex` |

Record `input_format`. The flag `--format md|latex` does **not** affect this — it controls the **output** rebuttal letter format (phase 04 reads it). Per Phase 2 decision §2, input is always auto-detected from extension.

### 3. Read `paper.json`

Call the primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = paper`. This bootstraps the file from the empty schema if it doesn't exist.

If the bootstrap path was taken (state-read just created the file), warn:
```
respond-reviewer: paper.json was missing — bootstrapped an empty one. Run /omcr-setup
or /start-research first if you intended to use existing state.
```
Then proceed.

### 4. Bootstrap `rebuttals.json`

Call the same state-read primitive with `name = rebuttals`. **Note:** `rebuttals` is a new state file added by this engine. Its allowed-name list and empty schema live in:
- The state-read primitive's allowed `name` values (engines that add new state files extend that list).
- The canonical empty form: `{ "schema_version": "1", "rebuttals": [] }`.

If the state-read primitive does not yet recognize `rebuttals` in its allowed set (e.g., the primitive hasn't been updated for this engine yet), fall back to:

- `mkdir -p .claude/omcr-state/` (idempotent).
- Write `.claude/omcr-state/rebuttals.json` with the literal empty schema above.
- Parse it back and proceed.

The fallback uses the atomic write pattern (tmp + rename) per the primitive's "Atomicity" section.

### 5. Resolve `manuscript_root`

Resolution order (first non-empty wins):

1. CLI `--manuscript <root>`.
2. `paper.json.manuscript_root`.

If neither resolves to a non-empty string, abort with:
```
respond-reviewer: manuscript_root required. Either pass --manuscript <root>
or set paper.json.manuscript_root (via /start-research or hand-edit).
```

Record the resolved `manuscript_root`. Phase 03 hands it to per-comment dispatches so the writer / implementer / curator know where the manuscript lives.

### 6. Read the letter contents

Read `<review-letter-path>` into `letter_content` (full file, raw bytes decoded as UTF-8). If decoding fails:
```
respond-reviewer: <review-letter-path> is not UTF-8 (got <error>).
Convert the letter to UTF-8 and retry.
```

### 7. Parse comments (mode-specific)

The parser must produce a list of dicts with this shape:

```jsonc
{
  "comment_id":  "R<reviewer>.<index>",   // stable across re-runs of the same letter
  "reviewer":    "<reviewer label, e.g., R1>",
  "text":        "<the comment body, full prose, no truncation>",
  "raw_offset":  <character offset into letter_content where the comment starts>
}
```

`comment_id` shape examples: `R1.1`, `R1.2`, `R2.1`, `Editor.1`. The leading token is the reviewer label as it appeared in the letter; the trailing integer is a 1-indexed count within that reviewer's section. If the letter contains no reviewer headers (e.g., a single flat list of comments), use the synthetic label `R1`.

#### 7a. Markdown mode (`input_format == "markdown"`)

Reviewer-section detection (in priority order — the first pattern that matches the letter wins):

1. **Heading-delimited.** Lines matching the regex `^#{1,3}\s*(Reviewer\s*\d+|Editor)\b` start a new reviewer section. Continue until the next matching heading.
2. **Bold-delimited.** Lines matching `^\*\*(Reviewer\s*\d+|Editor)\b.*\*\*\s*$` start a new reviewer section.
3. **Flat.** No reviewer headers found — treat the entire letter as one section under reviewer label `R1`.

Comment detection within each reviewer section:

- Lines beginning with a numbered list marker (`1.`, `2.`, `1)`, `(1)`) start a new comment.
- A comment continues until the next numbered marker, the next reviewer header, or end of file.
- Blank lines inside a comment are preserved.
- If no numbered markers exist in the section, fall back to **paragraph-delimited** parsing: each blank-line-separated paragraph is one comment. (Useful for letters that read as free prose.)

#### 7b. LaTeX mode (`input_format == "latex"`)

LaTeX letters typically use one of:

- `\section{Reviewer 1}` or `\subsection{Reviewer 1}` headers.
- `\reviewercomment{...}` or `\item` blocks inside an `enumerate` environment.
- Plain numbered text matching the same markdown numbered-list shape.

Reviewer-section detection:

1. **Sectioning command.** Lines matching `\\(section|subsection)\*?\{(Reviewer\s*\d+|Editor)\b.*\}` start a new section.
2. **Comment environment.** If the letter uses `\begin{reviewercomments}{<label>}...\end{reviewercomments}` (or a similar custom env), treat the env-open as the section start.
3. **Flat.** No structural markers → label `R1`.

Comment detection within each reviewer section:

- `\item` inside an `enumerate` env → one comment per `\item`.
- `\reviewercomment{...}` macros → one comment per macro.
- Otherwise fall back to the markdown numbered-list / paragraph rules (LaTeX prose with `\par`-separated paragraphs is parsed paragraph-by-paragraph).

Strip LaTeX comment lines (`^\s*%`) before parsing. Preserve inline LaTeX (math, refs, commands) inside the comment text — phase 02 and 03 dispatches will read it as-is.

### 8. Validate the comments list

After parsing:

- If `len(comments) == 0`, abort with:
  ```
  respond-reviewer: parsed 0 comments from <review-letter-path>.
  Letter may be malformed or use an unrecognized structure.
  Supported shapes: numbered list (`1.` / `2.` …), `**Reviewer N**` headers,
  LaTeX \section{Reviewer N} + \item or \reviewercomment{...}.
  If the structure is novel, split the letter into per-comment files and re-run
  with each, or hand-edit a markdown copy.
  ```
- If `len(comments) > 100`, warn (do not abort):
  ```
  respond-reviewer: parsed <N> comments — that is unusually high.
  Verify the parse before proceeding (phase 03 will dispatch <N> agent calls).
  ```

Sanity-check `comment_id` uniqueness — every parsed `comment_id` must be unique. If a collision occurs (a parser bug), append a numeric suffix to disambiguate (`R1.1-2`) and log a warning. Do not silently overwrite.

### 9. Assign `run_id` and stamp the start

Generate a UUID v4 string for the run. Record `started_at = <UTC ISO-8601 now>`.

This `run_id` flows through every later phase and lands in:
- The `rebuttals.json` entry's `run_id` field (phase 06).
- Every `_run-log.jsonl` record (start in phase 06, summary in phase 06).

### 10. Hand off to phase 02

Pass forward:
- `run_id` (UUID).
- `started_at` (ISO-8601).
- `review_letter_path` (the original input path, as supplied).
- `review_letter_abs` (absolute path).
- `input_format` (`markdown | latex`).
- `output_format` (`md | latex` from `--format`).
- `manuscript_root` (resolved string).
- `draft_only` (boolean).
- `comments` (the parsed list — phase 02 will add `label` and `agent` fields per comment).
- `paper_state` (the parsed `paper.json` dict — phase 03 reads section paths from it).
- `rebuttals_state` (the parsed `rebuttals.json` dict — phase 06 appends to it).

## Failure modes

| Condition | Behavior |
|---|---|
| `<review-letter-path>` missing | Abort with "pass a path relative to the project root" hint. |
| Extension not in `{.md, .txt, .tex}` | Abort with the supported list. |
| File not valid UTF-8 | Abort with the decode error. |
| `paper.json` parse error | Aborted upstream by state-read; surface its message. |
| `manuscript_root` unresolvable | Abort with the pass-`--manuscript`-or-set-state hint. |
| `rebuttals.json` bootstrap fails (filesystem permission) | Bubble the OS error; abort. |
| Parser returns zero comments | Abort with the supported-shapes hint. |
| Parser returns >100 comments | Warn; proceed. |
| Duplicate `comment_id` after parse | Append numeric suffix; log warning; proceed. |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero dispatches in phase 01.
- Does **not** label or classify comments. Phase 02 does that (one supervisor dispatch).
- Does **not** read the manuscript content. Phase 03 reads section files when building per-comment briefs.
- Does **not** validate that referenced section paths or figure IDs actually exist. Phase 03 catches missing referents per-comment.
- Does **not** write to `rebuttals.json` beyond bootstrap. Phase 06 appends the run's entry.
- Does **not** mutate `paper.json`. Per-comment dispatches in phase 03 may, but this phase only reads.
