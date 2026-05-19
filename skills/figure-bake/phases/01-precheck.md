---
name: figure-bake-precheck
description: Phase 1 of /figure-bake. Resolve the fig-id in figures.json (create entry if missing), apply the three-layer `data_root` resolution, validate the data path on disk, and prime the engine state for phase 02.
---

# Phase 1 — Precheck

Validate the call, resolve state, resolve the dataset root, and decide whether the loop should run at all. Output of this phase is either:

- An early exit (unrecoverable error — usually a `data_root` that does not exist), or
- A primed `figures.json` dict + a registered `figures[<fig-id>]` entry + a resolved `data_root` (absolute path), ready for phase 02.

## Inputs

From the slash command:
- `<fig-id>` — positional, required (e.g., `fig1`, `fig-overview`, `panel-2b`).
- `--max-iter N` — optional, default `3`.
- `--data <path>` — optional, CLI override of `data_root`.
- `--code-dir <path>` — optional, hint for the implementer's renderer script location.

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate `<fig-id>`

- The id is a string. Allowed characters: `[A-Za-z0-9_-]`. Length 1–64. Anything else aborts with:
  ```
  figure-bake: <fig-id> contains disallowed characters or is the wrong length.
  Use only letters, digits, hyphen, and underscore (1–64 chars). Example: fig1, panel-2b, supp-fig3.
  ```
- The id is treated as case-sensitive. `fig1` and `Fig1` are distinct entries.

Record the validated id; phases 02 / 03 / 04 / 05 use it as the key into `figures.json.figures`.

### 2. Read `paper.json`

Call the primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = paper`. This bootstraps the file from the empty schema if it doesn't exist.

If the bootstrap path was taken (state-read just created the file), warn:
```
figure-bake: paper.json was missing — bootstrapped an empty one. Run /omcr-setup
or /start-research first if you intended to use existing state.
```
Then proceed. The only fields phase 01 reads from `paper.json` are `manuscript_root` (for the default `vector_path`) and `title` (passed to the descriptor brief in phase 02). Neither is required to be non-null; defaults apply where the field is null.

Record:
- `manuscript_root` — defaults to `manuscript/` if the field is null.
- `title` — pass-through; phase 02 substitutes `"untitled manuscript"` if null.

### 3. Read `figures.json`

Call the primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = figures`. Bootstraps to `{"schema_version": "1", "figures": {}}` if missing.

### 4. Resolve or create the `figures[<fig-id>]` entry

Check whether `figures_state.figures[<fig-id>]` exists.

- **Entry exists** → use it as-is. Record the current `iter` value (the loop primitive will start counting from `iter + 1` for the next dispatch). Phase 05 will bump `iter` after each completed iteration.
- **Entry missing** → create a new entry with the canonical template:

  ```jsonc
  {
    "title":           null,
    "brief_status":    "missing",
    "impl_status":     "missing",
    "critique_status": "pending",
    "iter":            0,
    "deck_path":       null,
    "vector_path":     "<manuscript_root>/figures/<fig-id>.pdf",
    "code_dir":        null,
    "brief":           null,
    "critiques":       []
  }
  ```

  Field semantics for the new fields (additive on top of the schema in `develop/example-state/figures.json`):

  - `title` — short human-readable label. Phase 02 fills it in from the descriptor's response. Phase 01 leaves it `null` so the descriptor knows it has full latitude.
  - `code_dir` — directory the implementer wrote its renderer script into. Phase 01 seeds with `--code-dir` (CLI flag) if given, else `null`. Phase 03 updates after the implementer chooses a path.
  - `brief` — the design brief string from phase 02. Phase 01 leaves it `null`. Phase 02 fills it.
  - `critiques` — append-only list of per-iter reviewer outputs. Phase 04 appends; phase 01 seeds with `[]`.

  Log in the run-start record that a new figure entry was registered.

Write the entry back into `figures_state.figures[<fig-id>]` and persist `figures.json` atomically (tmp + rename) per the orchestrate state-read primitive's "Atomicity" section.

### 5. Resolve `data_root` (three-layer)

Apply the resolution order from Phase 2 decision §3:

1. **CLI `--data <path>`** — if non-empty, use as-is.
2. **Env `CLAUDE_RESEARCH_DATA_ROOT`** — read the environment variable. If non-empty, use as-is.
3. **CLAUDE.md `## Research stack` block, field `data_root`** — read the user's project `CLAUDE.md` from the project root. Scan for a `## Research stack` heading and a `data_root:` (or `Data root:`) line inside that block. If non-empty, use as-is.
4. **Hardcoded fallback `./data/`** — relative to the project root.

Note the resolution layer that won (for logging). Expand `~` and resolve to an absolute path. Record both the source layer (`cli` / `env` / `claude.md` / `default`) and the absolute path.

### 6. Validate `data_root` exists on disk

Stat the resolved path:

- **Path exists and is a directory** → continue.
- **Path exists but is not a directory** (e.g., a file) → abort with:
  ```
  figure-bake: data_root <path> exists but is not a directory (resolved from <source>).
  The implementer needs a directory it can read input files from. Fix the path and re-run.
  ```
- **Path does not exist** → abort with:
  ```
  figure-bake: data_root <path> does not exist (resolved from <source>).

  Resolution layers checked, in order:
    1. CLI --data            → <value or "(not set)">
    2. env CLAUDE_RESEARCH_DATA_ROOT → <value or "(not set)">
    3. CLAUDE.md ## Research stack data_root → <value or "(not set)">
    4. default               → ./data/

  Set one of the above to an existing directory, then re-run.
  ```

Do **not** auto-create the directory. The implementer can't invent input data — if the path is wrong, the user must fix their config.

The `--data` CLI flag does not skip validation. It is a one-off override of the resolution order, not a "trust me, just try it" escape.

### 7. Resolve `--code-dir` (optional)

If the CLI passed `--code-dir <path>`:
- Expand `~` and resolve to an absolute path (relative paths are relative to the project root).
- Record into `figures_state.figures[<fig-id>].code_dir`. Phase 03 will create the directory if it does not exist (the implementer writes the renderer script there).
- Do **not** validate existence here — the implementer is allowed to create the directory.

If not passed:
- Leave `code_dir` at whatever value the entry currently holds (`null` for a fresh entry, possibly a path from a prior run).

### 8. Resolve `vector_path` and pre-create its parent dir

`figures_state.figures[<fig-id>].vector_path` is the file path the implementer is contracted to write its rendered PDF to. Phase 01:

1. If the field is unset or `null`, set it to `<manuscript_root>/figures/<fig-id>.pdf`. (Phase 01 step 4 already does this for fresh entries.)
2. Expand `~` and resolve against the project root.
3. `mkdir -p` the parent directory (idempotent). The implementer needs a writable parent to land the PDF in.

If the `mkdir -p` fails (permission denied, read-only filesystem), abort:
```
figure-bake: cannot create parent directory for vector_path <path> (<os error>).
Phase 03 will not be able to write the PDF. Fix permissions and re-run.
```

### 9. Set the iteration entry status

Based on the entry's current `brief_status`, `impl_status`, `critique_status`:

| Current state | Action |
|---|---|
| All-`missing` / freshly-created entry | Leave as-is. Phase 02 will set `brief_status` after the descriptor returns. |
| `brief_status = "approved"`, `impl_status ∈ {missing, drafted}` | Phase 02 may skip the descriptor dispatch (see phase 02 step 1). Leave as-is. |
| `brief_status = "approved"`, `impl_status = "approved"`, `critique_status = "done"` | Already-DONE figure being re-run. Leave as-is — the user re-invoked deliberately; the loop will run a fresh iter. |
| Any other combination | Leave as-is. The loop adapts per phase. |

Phase 01 does **not** auto-flip any status — the per-phase rules in 02 / 03 / 04 / 05 own that responsibility, with the goal of keeping the state legible after a Ctrl-C.

### 10. Hand off to phase 02

Pass forward to phase 02:

- `fig_id` (the validated id)
- `figures_state` (the parsed dict, with the entry registered)
- `paper_state.title` and `paper_state.manuscript_root`
- `data_root` (absolute path, source layer recorded)
- `code_dir` (absolute path or null)
- `vector_path` (absolute path)
- `max_iter` (int)
- `current_iter` (the value of `figures_state.figures[<fig-id>].iter` before the run started — phase 02 uses it to decide whether to re-use the existing brief)

## Failure modes

| Condition | Behavior |
|---|---|
| `<fig-id>` invalid chars / length | Abort with the allowed-charset hint. |
| `paper.json` or `figures.json` parse error | Aborted upstream by the orchestrate state-read primitive. Surface its message. |
| `--data` path missing | Abort listing all four resolution layers' values. |
| `CLAUDE_RESEARCH_DATA_ROOT` env path missing | Same abort — env miss is treated identically to the CLI miss. |
| CLAUDE.md `data_root` missing | Same abort. |
| Default `./data/` missing | Same abort — the user has no config and no `./data/` dir; they need to do at least one thing. |
| `data_root` exists but is a file, not a directory | Abort with the file-vs-dir distinction. |
| `mkdir -p <parent of vector_path>` fails | Abort. The implementer needs to be able to write the PDF. |
| `figures.json` write fails after registering the entry | Bubble the OS error; abort. |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero dispatches in phase 01.
- Does **not** read the `## Research stack` block for anything other than `data_root`. Other fields the engine cares about (max_iter overrides, etc.) are read by the slash-command dispatcher if at all; phase 01 only owns the `data_root` resolution.
- Does **not** validate that `<vector_path>` already contains a usable PDF. The implementer (phase 03) is responsible for writing it. A pre-existing PDF at the path is ignored — it will be overwritten on the next implement dispatch.
- Does **not** invoke `cropfig`. That happens at the end of phase 03 after the implementer succeeds.
- Does **not** read the descriptor / implementer / reviewer persona files — that's the dispatch primitive's job in phases 02 / 03 / 04.
- Does **not** check whether the implementer's eventual Python environment has the libraries it needs (`matplotlib`, `numpy`, etc.). That diagnosis lives inside the implementer dispatch in phase 03; if a library is missing, the implementer reports back and phase 03 surfaces it as BLOCKED.
