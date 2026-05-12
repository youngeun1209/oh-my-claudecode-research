# Phase 01 — state-read (primitive)

Read, validate, and (if missing) bootstrap one state JSON file under
`.claude/omcr-state/` in the user's project. Returns a parsed dict that
the calling engine can read or mutate.

## Inputs

| Name | Required | Allowed values | Purpose |
|---|---|---|---|
| `name` | yes | `paper` \| `reviews` \| `citations` \| `figures` \| `rebuttals` | Which state file to read. |

The `_run-log.jsonl` file is **not** read through this primitive — it is
append-only and engines append to it directly via the loop primitive
(`phases/04-loop.md`).

## Resolved path

```
.claude/omcr-state/<name>.json
```

Always relative to the **user's project root** (the current working
directory of the Claude Code session), never the plugin install path.
Flat layout — no `logs/` subdirectory, per Phase 0 decision §1.

## Behavior

Execute in order:

1. **Compute target path.** `.claude/omcr-state/<name>.json` from the
   project root.

2. **Bootstrap if missing.** If the file does not exist:
   - `mkdir -p .claude/omcr-state/` (idempotent).
   - Copy the empty schema from
     `<plugin_root>/develop/example-state/<name>.json` to the target
     path. The plugin root is reachable via `$CLAUDE_PLUGIN_ROOT` (set
     by Claude Code at skill invocation time).
   - If `$CLAUDE_PLUGIN_ROOT` is not set, fall back to writing the
     literal empty schema for that file name (see "Empty schemas"
     below).
   - Set `last_updated` on the bootstrapped file to current UTC ISO-8601
     timestamp where the schema has that field (only `paper.json`).
   - Continue to step 3 against the newly written file.

3. **Parse JSON.** Read the target file and parse as JSON.
   - On parse error: print `state-read: <name>.json is not valid JSON
     — aborting` with the parser error message and the file path. Do
     NOT attempt repair. The engine that called this primitive must
     surface the abort to the user.

4. **Validate `schema_version`.** Expected `"1"` (string).
   - If field missing entirely: print warning `state-read: <name>.json
     has no schema_version field — assuming "1"`. Proceed.
   - If field present but not `"1"`: print warning `state-read:
     <name>.json schema_version is <value>, expected "1" — proceeding
     anyway (no migration runner at v0.2, see Phase 0 decision §2)`.
     Proceed.
   - No migration logic. None. This is intentional.

5. **Return the parsed dict.** The caller may read fields, mutate
   in-memory, and then write back via the engine's own phase (or via
   `phases/04-loop.md` for log appends).

## Output contract

Returns a Python-shaped dict matching the schema for the requested
file. The shape mirrors `develop/example-state/<name>.json` exactly.
See [`../../../develop/example-state/README.md`](../../../develop/example-state/README.md)
for populated examples.

## Empty schemas (used by step 2 fallback)

These are the canonical empty shapes. They MUST stay byte-equivalent
to the files under `develop/example-state/`. If a schema changes there,
update this list too.

### `paper.json`

```json
{
  "schema_version": "1",
  "title": null,
  "venue": null,
  "hypothesis": null,
  "manuscript_root": "manuscript/",
  "sections": {
    "abstract":     { "path": "manuscript/sections/abstract.tex",     "status": "empty", "iter": 0, "last_review_id": null, "outline": null },
    "introduction": { "path": "manuscript/sections/introduction.tex", "status": "empty", "iter": 0, "last_review_id": null, "outline": null },
    "methods":      { "path": "manuscript/sections/methods.tex",      "status": "empty", "iter": 0, "last_review_id": null, "outline": null },
    "results":      { "path": "manuscript/sections/results.tex",      "status": "empty", "iter": 0, "last_review_id": null, "outline": null },
    "discussion":   { "path": "manuscript/sections/discussion.tex",   "status": "empty", "iter": 0, "last_review_id": null, "outline": null }
  },
  "figures": [],
  "submission_ready": false,
  "last_updated": "<UTC-ISO-8601 at bootstrap>"
}
```

Section `status` enum: `empty | drafted | revising | approved | blocked | blocked-on-tbd`.
`outline` is `null` by default; engines fall back to
`<manuscript_root>/outline.md` when null.

### `reviews.json`

```json
{
  "schema_version": "1",
  "runs": []
}
```

### `citations.json`

```json
{
  "schema_version": "1",
  "queue": [],
  "verified": [],
  "last_sweep": null
}
```

### `figures.json`

```json
{
  "schema_version": "1",
  "figures": {}
}
```

### `rebuttals.json`

```json
{
  "schema_version": "1",
  "rebuttals": []
}
```

## Atomicity

When the caller writes the returned dict back to disk (in a later phase),
it must use a write-tmp + rename pattern so an interrupted write never
leaves a half-written JSON file:

```
write   .claude/omcr-state/<name>.json.tmp
fsync
rename  .claude/omcr-state/<name>.json.tmp → .claude/omcr-state/<name>.json
```

This primitive itself only writes during the bootstrap branch of step 2,
where the same atomic pattern applies.

## Errors

| Condition | Behavior |
|---|---|
| `name` not in allowed set | Abort with `state-read: unknown state name <name>`. |
| Plugin root unreachable AND target file missing | Use the inline empty-schema fallback (above). Do not abort — bootstrap must always succeed. |
| Target file present but malformed JSON | Abort. Engine must surface to user. |
| Target file schema_version mismatch | Warn and proceed. Do not abort. |
| Filesystem permission denied | Abort with the OS-level error message. |

## What this primitive does NOT do

- Does NOT migrate between schema versions. Deferred to v0.5+ when a
  real `"2"` ships.
- Does NOT lock the file against concurrent writers. v0.2 assumes
  serial execution (Phase 0 decision §4). Phase 3 will revisit.
- Does NOT validate field-level types beyond the parse + schema_version
  check. Engine phases that depend on specific fields are responsible
  for guarding their own reads.
- Does NOT auto-fix `[TBD: ...]` placeholders in any field. Engines
  decide whether to refuse-on-TBD (e.g., `/iterate-revision`) or pass
  it through (e.g., `/omcr-setup`).
