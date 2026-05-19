# Phase 1 — Precheck

Validate the call, resolve state, and decide whether the loop should even run. Output of this phase is either:
- An early exit (already approved, no `--force`; or `[TBD: blockers without `--allow-tbd`; or unrecoverable error), or
- A primed `paper.json` dict + resolved venue + section name, ready for phase 02.

## Inputs

From the slash command:
- `<section-path>` — positional, required
- `--max-iter N` — optional, default `3`
- `--venue VENUE` — optional, falls back to `paper.json.venue`
- `--force` — optional flag, default false
- `--allow-tbd` — optional flag, default false

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate `<section-path>`

- The path is interpreted relative to the project root (the Claude Code session's working directory).
- Verify the file exists. If not, abort with:
  ```
  iterate-revision: <section-path> not found.
  Create the file first, or update paper.json.sections[*].path to match.
  ```
- Verify the extension is one of `.tex`, `.md`, `.txt`. If not, abort with:
  ```
  iterate-revision: unsupported section extension <ext>. Must be one of: .tex, .md, .txt.
  ```

Record the absolute path and the extension; phase 02 / 03 will need them.

### 2. Read `paper.json`

Call the primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = paper`. This bootstraps the file from the empty schema if it doesn't exist.

If the bootstrap path was taken (state-read just created the file), warn:
```
iterate-revision: paper.json was missing — bootstrapped an empty one. Run /omcr-setup
or /start-research first if you intended to use existing state.
```
Then proceed.

### 3. Identify the matching `sections` key

Scan `paper.json.sections` for an entry whose `path` field matches `<section-path>` (compare normalized paths — strip leading `./`, collapse duplicate slashes).

- **Match found** → use that key as `section_name`. Record the section dict.
- **No match** → derive a name from the file stem (e.g., `sections/results.tex` → `results`) and append a new entry:
  ```jsonc
  {
    "path":            "<section-path>",
    "status":          "empty",
    "iter":            0,
    "last_review_id":  null,
    "outline":         null
  }
  ```
  Note in the run-start log that a new section was registered.

If the derived name collides with an existing key whose `path` differs, append a numeric suffix (`results-2`) and proceed. Do not silently overwrite.

### 4. Resolve venue

Resolution order (first non-empty wins):

1. CLI `--venue VENUE`
2. `paper.json.venue`

If neither resolves to a non-empty string, abort with:
```
iterate-revision: venue required. Either pass --venue VENUE or set paper.json.venue
(via /start-research or hand-edit).
```

Record the resolved venue. Phase 03 uses it to set reviewer strictness.

### 5. TBD scan (Phase 1 decision Q2)

Scan for the literal pattern `[TBD:` in three places:

1. The full contents of `<section-path>`.
2. `paper.json.sections[section_name].outline` if that field is non-null. (If null, do **not** read `<manuscript_root>/outline.md` for the TBD check — the fallback outline is shared across all sections and false-positives would block every run.)
3. `paper.json.hypothesis` (top-level string).

Collect every match with its location:
- For files: line number and a ≤80-char excerpt of the surrounding text.
- For the inline `outline` field: `<key>=sections[<name>].outline` + character offset.
- For `hypothesis`: `<key>=hypothesis`.

If any matches were found AND `--allow-tbd` is **false**:

1. Set `paper.json.sections[section_name].status = "blocked-on-tbd"`. Write `paper.json` back atomically (tmp + rename, per the orchestrate primitive convention).
2. Abort with a multi-line message naming each marker. Example:
   ```
   iterate-revision: refusing to draft — [TBD:] markers found.

     sections/results.tex:L42:  "we will use [TBD: classifier]"
     paper.json.sections[results].outline: char 118: "compare to [TBD: baseline]"
     paper.json.hypothesis: "[TBD: rewrite after pilot]"

   Drafting around undecided facts produces fabricated content the reviewer
   cannot catch. Resolve the markers, or pass --allow-tbd to override.
   Section status set to blocked-on-tbd.
   ```

If `--allow-tbd` is **true**, log a warning listing the markers and proceed:
```
iterate-revision: --allow-tbd is set; proceeding despite N [TBD:] markers.
The writer will treat these as literal text. Make sure that is what you want.
```

### 6. Early-exit on `status == "approved"`

If `paper.json.sections[section_name].status == "approved"` AND `--force` is **false**, abort cleanly (this is **not** an error):

```
iterate-revision: <section_name> is already approved (iter <N>).
Pass --force to re-iterate, or move on:
  /iterate-revision <next-unwritten-section>
```

Do not touch `paper.json` in this branch.

If `--force` is **true** on an `approved` section: log the override, set `status = "revising"` (do not reset `iter`), and continue.

### 7. Set the iteration entry status

Based on the section dict's current `status` and `iter`:

| Current status | Current iter | New status | Notes |
|---|---|---|---|
| `empty` | 0 | `drafted` | Phase 02 will run in DRAFT mode. |
| `drafted` | 0 | `revising` | Phase 02 will run in REVISE mode (writer revises its own iter-0 draft, or freshly drafts if the file is actually empty — phase 02 re-checks the file content). |
| `revising` | ≥ 1 | `revising` | Resuming a CONTINUE / HALT run. |
| `blocked` | ≥ 1 | `revising` | User addressed the critical issue manually; resume. |
| `blocked-on-tbd` | any | `revising` | TBD scan passed this run (either no markers, or `--allow-tbd`). |
| `approved` | any | `revising` | Only reached with `--force`. |

Write `paper.json` back atomically. Also update `paper.json.last_updated` to current UTC ISO-8601.

### 8. Hand off to phase 02

Pass forward to phase 02:
- `section_name` (the resolved sections key)
- `section_path` (the file path)
- `section_ext` (one of `tex`, `md`, `txt`)
- `venue` (resolved string)
- `max_iter` (int)
- `current_iter` (the value from `paper.json` before this run started — phase 02 uses it to decide DRAFT vs REVISE)
- the parsed `paper.json` dict (so phase 02 / 04 don't re-read disk needlessly)

## Failure modes

| Condition | Behavior |
|---|---|
| `<section-path>` missing | Abort with create-the-file hint. |
| Section extension not in `{.tex, .md, .txt}` | Abort with the supported list. |
| `paper.json` parse error | Aborted upstream by the orchestrate state-read primitive. Surface its message. |
| Venue unresolvable | Abort with the pass-`--venue`-or-set-state hint. |
| `[TBD:` present + no `--allow-tbd` | Status → `blocked-on-tbd`; abort with all locations listed. |
| Section already `approved` + no `--force` | Clean exit (not an error); no state change. |
| Filesystem write permission denied | Bubble the OS error verbatim; abort. |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero dispatches in phase 01.
- Does **not** read `reviews.json` (phase 02 does that for the REVISE-mode last-review lookup).
- Does **not** read the fallback `outline.md` (phase 02 does that if `sections[name].outline` is null).
- Does **not** clear `last_review_id`. The pointer persists across runs so resume can find the prior review.
