# Phase 1 — Precheck

Parse the outline, decide which sections will be drafted this run, and prepare the per-section outline excerpts that phase 02 will pass to each `@paper-writer` dispatch. Output of this phase is either:
- An early exit (outline missing, no draftable sections, etc.), or
- A primed `paper.json` dict + a `section_plan` list naming each section to draft along with its outline excerpt, ready for phase 02.

## Inputs

From the slash command:
- `<outline-path>` — positional, required
- `--sections <list>` — optional, comma-separated section names
- `--max-iter-per-section N` — optional, accepted but unused in v0.2

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate `<outline-path>`

- The path is interpreted relative to the project root (the Claude Code session's working directory).
- Verify the file exists. If not, abort with:
  ```
  outline-expand: <outline-path> not found.
  Create the file first, or pass an explicit outline path. Common locations:
    outline.md, manuscript/outline.md, manuscript/outline.tex
  ```
- Verify the extension is one of `.md`, `.tex`, `.txt`. If not, abort with:
  ```
  outline-expand: unsupported outline extension <ext>. Must be one of: .md, .tex, .txt.
  ```

Record the absolute path and the extension; step 4 below uses the extension to pick the right parser.

### 2. Read `paper.json`

Call the primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = paper`. This bootstraps the file from the empty schema if it doesn't exist.

If the bootstrap path was taken (state-read just created the file), warn:
```
outline-expand: paper.json was missing — bootstrapped an empty one. Run /omcr-setup
or /start-research first if you intended to use existing state. Continuing with the
default 5-section schema (abstract, introduction, methods, results, discussion).
```
Then proceed.

Record `paper_state` (the parsed dict) and `manuscript_root = paper_state.manuscript_root`.

### 3. Resolve `manuscript_root` on disk

The section paths in `paper.json.sections[*].path` are relative to the project root, not to `manuscript_root` — but phase 03 writes the post-merge drift artifact to `<manuscript_root>/terminology-drift.md`, and the parent directory must exist.

- If `manuscript_root` is `null` or empty, default it to `"manuscript/"` and update `paper_state.manuscript_root` in memory.
- Verify the directory exists. If not, create it (`mkdir -p`). The drift artifact will land there in phase 03.

Do **not** abort if `manuscript_root` doesn't exist — this is a soft creation. The section files' parent directories are checked per-section in phase 03 instead.

### 4. Parse the outline into per-section excerpts

The outline parser depends on the extension:

#### Markdown / plaintext (`.md`, `.txt`)

Treat each top-level heading (`# ...` for `.md`; the first non-empty line of a section block for `.txt`) as a section boundary. The section name is the heading text, lowercased, with spaces collapsed to single spaces.

For `.md`:
- `# Heading` → section boundary at H1.
- `## Subheading` → not a boundary; included in the parent section's body.
- Lines before the first heading → assigned to a synthetic `"_preamble"` section (kept for context but not draftable).

For `.txt`:
- A line that consists entirely of all-caps text (≥3 chars) OR a line that ends with `:` and is followed by a blank line → section boundary.
- The boundary line's text (lowercased, trailing `:` stripped) is the section name.

#### LaTeX (`.tex`)

Detect `\section{...}` and `\subsection{...}` calls.

- `\section{Heading}` → section boundary; section name is the contents of `{...}`, lowercased.
- `\subsection{...}` → not a boundary.
- Lines before the first `\section{...}` → `"_preamble"`.
- `\section*{...}` (starred form) is also a boundary, treated identically.

### 5. Build the `outline_sections` dict

After parsing, `outline_sections` is:

```python
{
  "introduction": "<excerpt — every line from the heading to just before the next heading>",
  "methods":      "<excerpt>",
  ...
}
```

The excerpt **includes** the heading line itself (so the writer sees what the outline author labelled the section). Trailing whitespace is preserved; leading whitespace per line is preserved.

If `outline_sections` has zero entries (no headings found), abort with:
```
outline-expand: <outline-path> contained no parseable section headings.
Markdown outlines use `# Heading`; LaTeX uses \section{...}; plaintext uses
ALL-CAPS lines. Add headings or pick a different outline file.
```

Record `outline_sections` for later use.

### 6. Normalize outline section names to `paper.json` keys

Map each outline section name to a `paper.json.sections[*]` key by:

1. Exact match (lowercased) — preferred. e.g., outline says `# Methods` → maps to `methods` if `paper_state.sections["methods"]` exists.
2. Stem prefix match — e.g., outline says `# Introduction and Motivation` → maps to `introduction` if `introduction` exists and the outline name starts with `introduction `.
3. No match → record under the unmapped bucket; this section will NOT be drafted (the writer has no `paper.json.sections[*].path` to write to). Log a one-line warning:
   ```
   outline-expand: outline section "<name>" has no matching paper.json key — skipping.
   Add an entry to paper.json.sections, or rename the outline heading to match an
   existing key (abstract, introduction, methods, results, discussion).
   ```

After this step, every entry in `outline_sections` is either:
- Mapped (the outline excerpt is now associated with a `paper.json.sections[key]` entry), or
- Unmapped (logged + dropped).

### 7. Apply `--sections` filter, if provided

If the CLI passed `--sections name1,name2,...`:

1. Parse the comma-separated list. Strip whitespace per name; lowercase each.
2. For each requested name:
   - If it is a mapped outline section name → mark it for drafting.
   - If it is NOT in the mapped set → log a warning:
     ```
     outline-expand: --sections requested "<name>" but the outline does not contain
     a matching heading. Skipping this name.
     ```
3. After filtering, the draftable set is exactly the names that were both requested AND mapped.

If the resulting set is empty, abort cleanly (not an error):
```
outline-expand: --sections filter left zero draftable sections. Either drop the
filter, or pass a name that appears as a heading in <outline-path>.
```

If `--sections` was **not** provided, the draftable set is all mapped outline sections.

### 8. Apply the `approved` / `already drafted` guards

For each candidate in the draftable set, check `paper_state.sections[name].status`:

| Status | Action without `--sections` | Action when name appears explicitly in `--sections` |
|---|---|---|
| `empty` | draft | draft |
| `drafted` | **skip** (already drafted, log skip line) | draft (re-draft, clobbering existing prose) |
| `revising` | **skip** (in-flight refinement; user should run `/iterate-revision` to resume) | draft (clobber — user asked) |
| `blocked` | **skip** (user should resolve the block first) | draft (clobber) |
| `blocked-on-tbd` | **skip** (user should resolve the TBD first) | draft (clobber) |
| `approved` | **skip** | **skip** — explicit name in `--sections` does NOT override `approved`. Never auto-redraft approved prose. |

For each `approved`-and-requested-but-skipped name, log:
```
outline-expand: section "<name>" is already approved; refusing to re-draft.
To redo an approved section, manually set its status (e.g., via `/sync` or hand-edit
paper.json: sections.<name>.status = "drafted") and re-run.
```

Record the final `section_plan` as a list of dicts:

```python
[
  {
    "name":         "introduction",
    "path":         paper_state.sections["introduction"].path,
    "outline":      outline_sections["introduction"],     # the excerpt from step 5
    "current_iter": paper_state.sections["introduction"].iter,
    "current_status": paper_state.sections["introduction"].status
  },
  ...
]
```

If `section_plan` is empty after all guards apply, abort cleanly:
```
outline-expand: nothing to draft. All matched outline sections are already approved
or were filtered out. Pass --sections <name> to override (except approved), or run
/iterate-revision <section-path> on existing drafts to refine.
```

### 9. Resolve the shared nomenclature payload

Phase 02 passes the same nomenclature payload to every dispatch. Build it here so phase 02 can paste it into N task briefs without re-reading.

Read, in priority order:

1. `.claude/agent-memory/paper-writer/nomenclature.md` in the user's project root.
   - If it exists, read the full content (no length cap — writers benefit from the full file).
   - If it is empty (≤ 5 non-whitespace characters), fall through to step 2.
2. The minimal stub (verbatim):

   ```
   (No nomenclature.md yet — none has been recorded for this project.
    Use terminology consistent with the Introduction section if one is already
    drafted; if undecided, pick one form and log it in
    .claude/agent-memory/paper-writer/nomenclature.md so future runs can
    converge. Avoid switching between synonyms within a single section.)
   ```

Record the resolved payload as `nomenclature_payload`. Note in the run-start log whether it came from disk (`source: "file"`) or the stub (`source: "stub"`).

### 10. Hand off to phase 02

Pass forward to phase 02:
- `paper_state` (the parsed dict, not re-read in phase 02)
- `manuscript_root` (resolved + created)
- `section_plan` (list of per-section dicts from step 8)
- `nomenclature_payload` (string)
- `outline_path` (for logging only; phase 02 does not re-read the outline)

## Failure modes

| Condition | Behavior |
|---|---|
| `<outline-path>` missing | Abort with the create-the-file hint. |
| Outline extension not in `{.md, .tex, .txt}` | Abort with the supported list. |
| `paper.json` parse error | Aborted upstream by the orchestrate state-read primitive. Surface its message. |
| `manuscript_root` directory cannot be created | Abort with the OS-level error. |
| Outline has zero parseable headings | Abort with the heading-syntax hint. |
| All outline sections are unmapped | Treated as `section_plan` empty → clean exit (not an error). |
| All matched sections are `approved` | Clean exit (not an error); no state change. |
| `--sections` lists only unmapped or already-approved names | Clean exit (not an error). |
| Filesystem write permission denied (for `manuscript_root` mkdir) | Bubble the OS error verbatim; abort. |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero dispatches in phase 01.
- Does **not** write to `paper.json`. Phase 03 owns the writes-back after the prose lands.
- Does **not** read `reviews.json`, `citations.json`, or `figures.json`. Out of scope for `/outline-expand`.
- Does **not** scan for `[TBD: ...]` markers in the outline. The `/iterate-revision` engine has that guard; this engine is for first drafts, where TBD markers in the outline are a legitimate way to flag "draft around this" intent. (If a section's outline excerpt contains `[TBD: ...]`, the writer will see it and may either incorporate the marker or work around it; the engine does not gate.)
- Does **not** read the fallback `<manuscript_root>/outline.md`. The user passed an explicit outline path; that path is canonical.
- Does **not** edit `nomenclature.md`. Reads only.
