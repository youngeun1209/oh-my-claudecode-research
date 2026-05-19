# Phase 1 — Precheck

Validate the call, resolve paths, ping the metadata sources, and clamp `--parallel`. Output of this phase is either:

- An early abort (empty topic, both sources unreachable, BibTeX path unwritable, invalid `--parallel`), or
- A primed run plan with resolved `bib_file`, `summary_file`, `parallel` clamp, source list, and a freshly bootstrapped `citations.json` dict ready for phases 02–06.

## Inputs

From the slash command:

- `<topic>` — positional, required. Free-form string (e.g., `"neural manifolds in motor cortex"`).
- `--n N` — optional, default `20`.
- `--depth basic|deep` — optional, default `basic`.
- `--source crossref|openalex|both` — optional, default `both`.
- `--parallel P` — optional, default `1`.

## Steps

Execute in order. Abort on the first failure unless the step says otherwise.

### 1. Validate `<topic>`

- Strip leading and trailing whitespace.
- If the resulting string is empty, abort with:
  ```
  literature-sweep: topic is required.
  Example: /literature-sweep "neural manifolds in motor cortex"
  ```
- If the topic is shorter than 4 characters after stripping, warn but proceed:
  ```
  literature-sweep: topic is very short ("<topic>"). Search recall may be poor.
  Continue anyway? Re-run with a more specific phrase if you want better results.
  ```
  Continue without prompting — this is informational. Phase 02 will discover empty results if the topic is too narrow.

Record the cleaned topic string. Phases 02 and 06 will reference it.

### 2. Validate `--n`

- Must be an integer ≥ 1. If parsing fails or `< 1`, abort:
  ```
  literature-sweep: --n must be a positive integer (got <value>).
  ```
- If `n > 100`, warn but proceed:
  ```
  literature-sweep: --n <value> is large; the candidate list (3 * n) will be
  <3 * value>. Phase 02 will take longer and phase 05 will issue <value> verify
  calls. Press on if intentional.
  ```

Record `n_requested = N`.

### 3. Validate `--depth`

Must be exactly `basic` or `deep`. Anything else (including casing variants like `BASIC`) → abort:
```
literature-sweep: --depth must be 'basic' or 'deep' (got '<value>').
```

Record `depth`. Phase 03 branches on this.

### 4. Validate `--source`

Must be exactly one of `crossref`, `openalex`, `both`. Anything else → abort:
```
literature-sweep: --source must be one of 'crossref', 'openalex', 'both' (got '<value>').
```

Expand into a list: `crossref` → `["crossref"]`, `openalex` → `["openalex"]`, `both` → `["crossref", "openalex"]`. Record as `sources`.

### 5. Clamp `--parallel`

Per [`develop/phase-2-decisions.md`](../../../develop/phase-2-decisions.md) §1:

- If `P < 1`: abort:
  ```
  literature-sweep: --parallel must be >= 1 (got <value>).
  ```
- If `P > 4`: warn and clamp to 4:
  ```
  literature-sweep: --parallel <value> exceeds the cap of 4 — clamping to 4.
  Rationale: above 4 instances the speedup collapses while CrossRef / OpenAlex
  rate-limiting risk grows. See phase-2-decisions.md §1.
  ```
- If `1 ≤ P ≤ 4`: accept as-is.

Record the clamped value as `parallel`. Phase 03 uses it.

### 6. Resolve `bib_file` and `summary_file`

Use the standard three-layer resolution (env → CLAUDE.md `## Research stack` → defaults). First non-empty wins:

| Path | Env var | `## Research stack` field | Default |
|---|---|---|---|
| `bib_file` | `CLAUDE_RESEARCH_BIB_FILE` | `BibTeX file` | `references.bib` |
| `summary_file` | `CLAUDE_RESEARCH_SUMMARY_FILE` | `Summary file` | `references.csv` |

Resolution is relative to the project root (the Claude Code session's working directory).

Also consult `paper.json.manuscript_root` if the resolved `bib_file` is a bare filename (no path separator). Prefer `<manuscript_root>/references.bib` over a root-level `references.bib` when both exist. If neither exists yet, fall back to `<manuscript_root>/references.bib` so phase 06 writes alongside the LaTeX scaffold.

Record the absolute paths for `bib_file` and `summary_file`. Phase 05 reads `bib_file` to dedupe against existing entries; phase 06 appends to both.

If the parent directory of either path does not exist, abort:
```
literature-sweep: parent directory for <bib_file or summary_file> does not exist.
Run /omcr-setup or /start-research first, or pass the correct path via
CLAUDE.md ## Research stack block.
```

If the parent directory exists but is not writable, abort with the OS-level permission error.

### 7. Bootstrap `citations.json`

Call the orchestrate state-read primitive at [`../../orchestrate/phases/01-state-read.md`](../../orchestrate/phases/01-state-read.md) with `name = citations`. This creates `.claude/omcr-state/citations.json` from the empty schema if it doesn't exist, otherwise reads and parses the existing file.

If the bootstrap path was taken (state-read just created the file), warn:
```
literature-sweep: citations.json was missing — bootstrapped an empty one. Run
/omcr-setup first if you intended to use existing citation state.
```

Record the parsed `citations_state` dict. Phase 04 reads its `verified` list (for cross-sweep dedupe); phase 06 writes the `last_sweep` block back.

### 8. Best-effort API reachability check

For each source in `sources`, do a single HEAD or trivial GET to confirm the host is up. Use a short timeout (5 seconds per source).

| Source | Probe URL |
|---|---|
| `crossref` | `https://api.crossref.org/works?rows=0` |
| `openalex` | `https://api.openalex.org/works?per_page=1` |

Behavior:

- **All probed sources reachable.** Continue silently.
- **One source unreachable, the other reachable.** Warn and drop the unreachable one from `sources`:
  ```
  literature-sweep: <source> probe failed (<reason>). Continuing with <remaining sources>.
  This will be recorded in citations.json.last_sweep.notes.
  ```
  Record the dropped source in a `probe_failures` list so phase 06 can write it into `notes`.
- **All sources unreachable.** Warn but proceed — phase 02 will retry the actual queries:
  ```
  literature-sweep: all metadata sources failed the precheck probe. Phase 02 will
  retry; if that also fails, the engine will return an empty result with
  citations.json.last_sweep.notes describing the outage.
  ```
  Do not abort here. Network conditions can change between the probe and the query, and the user may have intentionally configured an internal proxy that 403s the probe URL but accepts authenticated queries.

The reachability check is **best-effort, warn-and-proceed** — never blocking.

### 9. Hand off to phase 02

Pass forward to phase 02:

- `topic` (cleaned string)
- `n_requested` (int)
- `depth` (`"basic"` or `"deep"`)
- `sources` (filtered list, after step 8)
- `parallel` (clamped int)
- `bib_file` (absolute path)
- `summary_file` (absolute path)
- `citations_state` (parsed dict from step 7)
- `probe_failures` (list, may be empty)

## Failure modes

| Condition | Behavior |
|---|---|
| Empty `<topic>` | Abort with the usage hint. |
| `--n` not a positive integer | Abort with the parsed value. |
| `--depth` not in `{basic, deep}` | Abort with the value. |
| `--source` not in `{crossref, openalex, both}` | Abort with the value. |
| `--parallel < 1` | Abort. |
| `--parallel > 4` | Warn, clamp to 4, continue. |
| Parent of `bib_file` / `summary_file` missing | Abort with the path. |
| Parent of `bib_file` / `summary_file` unwritable | Abort with OS error. |
| `citations.json` parse error | Aborted upstream by the orchestrate state-read primitive. |
| One API probe fails | Warn, drop that source, record in `probe_failures`. |
| All API probes fail | Warn, continue (phase 02 will retry). |

## What this phase does NOT do

- Does **not** invoke any subagent. Zero dispatches in phase 01.
- Does **not** issue any real search query. That is phase 02.
- Does **not** write to `references.bib`, the CSV, or `citations.json` (other than the bootstrap created by the state-read primitive on first run).
- Does **not** verify any candidate against CrossRef / OpenAlex. That is phase 05.
- Does **not** modify `paper.json`. `/literature-sweep` is keyed off `citations.json`, not `paper.json`.
