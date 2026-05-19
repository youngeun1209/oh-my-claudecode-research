# Phase 02 — dispatch (primitive)

Invoke a persona subagent through Codex's Agent tool with the
persona's markdown body inlined as the prompt prefix. Returns the
agent's output plus metadata.

## Inputs

| Name | Required | Type | Purpose |
|---|---|---|---|
| `persona` | yes | string | One of the 6 OMXR personas (see below). |
| `task_brief` | yes | string | Natural-language task description. Engine-specific. |
| `state_slice` | no | dict / null | Optional context to inline (e.g., the relevant `paper.json` section only — never the whole state). |
| `expected_output_schema` | no | dict / null | Optional shape hint. If given, the primitive attempts to parse the agent's response into this shape and returns both raw + parsed. |

### Allowed `persona` values

Exactly these six. No others exist in OMXR:

- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

If the caller passes anything else, abort with `dispatch: unknown
persona <persona> — must be one of {supervisor, analysis-implementer,
paper-writer, figure-descriptor, reviewer, literature-curator}`.

## Subagent type

**Always `subagent_type: "general-purpose"`.** Per Phase 0 decision §5,
OMXR does not attempt to register each persona as a first-class Codex
Code subagent type. Instead the persona's markdown body is inlined as
the prompt prefix. This keeps OMXR portable across Codex versions
and makes runs reproducible by hand (a user can copy the dispatched
prompt out of `_run-log.jsonl` and paste it into a fresh Codex
session).

## Behavior

Execute in order:

1. **Resolve persona body.** Read `<plugin_root>/agents/<persona>.md`.
   `$CODEX_PLUGIN_ROOT` gives the plugin root. If the agent file does
   not exist, abort with `dispatch: persona file
   agents/<persona>.md not found at plugin root`.

2. **Strip YAML frontmatter.** Detect a leading `---\n...\n---\n` block
   and remove it. Keep only the markdown body. The frontmatter's
   `name`, `description`, `model`, `color`, `memory` fields are
   metadata for Codex itself — they should not be repeated to
   the dispatched subagent.

3. **Assemble the prompt.** Concatenate in this order, separated by
   blank lines:

   ```
   <persona body — with YAML stripped>

   ---

   # Task

   <task_brief>

   ---

   # State slice

   <state_slice rendered as fenced JSON; section omitted if state_slice is null>

   ---

   # Expected output

   <expected_output_schema rendered as fenced JSON; section omitted if expected_output_schema is null>
   ```

   The three `---` separators help the subagent visually distinguish
   role / task / context / output-shape. They are not magic markers,
   just readability.

4. **Invoke the Agent tool.**
   - `subagent_type`: `"general-purpose"` (always)
   - `description`: `"omxr/<persona>: <first 60 chars of task_brief>"` —
     keeps `_run-log.jsonl` and Codex's UI scannable.
   - `prompt`: the assembled prompt from step 3.

5. **Capture the response.** Take the agent's final text response as
   `raw_output`. Record the wall-clock end timestamp as `timestamp`
   (UTC ISO-8601).

6. **Optional parse.** If `expected_output_schema` was provided:
   - Attempt to extract a JSON block from `raw_output` (look for a
     fenced ```json block first, then fall back to the largest
     top-level `{...}` or `[...]` substring).
   - If parse succeeds and the result is shape-compatible with the
     schema hint: set `parsed_output = <the parsed value>`.
   - If parse fails: set `parsed_output = null` and `parse_error =
     "<reason>"`. **Do not abort** — the engine that called dispatch
     decides whether a missing parse is fatal.

## Output contract

Returns a dict:

```jsonc
{
  "output":       "<raw text response from the subagent>",
  "parsed":       <parsed JSON | null>,        // only present if expected_output_schema was given
  "parse_error":  "<reason | null>",            // only present on parse failure
  "persona":      "<persona name>",
  "timestamp":    "<UTC ISO-8601>"
}
```

The caller (typically `phases/04-loop.md` or the engine's own phase)
folds this into the engine's working state and proceeds.

## Why inlined, not registered

OMXR personas in `agents/*.md` are already self-contained: role
description, constraints, language directive, memory pointer. Inlining
is a 10-line implementation. Registering each persona as a Codex
subagent type would couple OMXR to a registration mechanism that varies
by Codex version and would add setup steps to `$omxr-setup`. See
Phase 0 decision §5 for the full rationale.

The trade-off: every dispatch carries the persona body in its prompt
(~200-500 lines per agent), so token cost is higher than a registered
subagent would be. This is acceptable currently (`max_iter` default 3,
6 personas, prompts cached server-side by Codex where possible).

## Statelessness

Codex's Agent tool spawns a **fresh** subagent with no prior
conversation context. Each dispatch is therefore **stateless** — the
caller passes everything the persona needs through `task_brief` and
`state_slice`. The persona reads its own memory from
`.omx/omxr/agent-memory/<persona>/MEMORY.md` (the `memory-load.sh` hook
puts MEMORY.md content into the session context that subagents
inherit), but nothing from a previous dispatch persists.

This is by design. It keeps each agent invocation independently
auditable and resumable. Conversation-style cross-call state would
make `_run-log.jsonl` replay impossible.

## Errors

| Condition | Behavior |
|---|---|
| `persona` not in allowed set | Abort with the explicit list (see above). |
| Persona file missing under plugin root | Abort with file path. |
| Agent tool returns an error | Abort with the underlying error message. The loop primitive will catch this and emit BLOCKED. |
| Agent returns empty response | Return with `raw_output = ""` and `parse_error = "empty response"`. Let the engine decide. |

## What this primitive does NOT do

- Does NOT mutate any state file. Side effects (writing to
  `reviews.json`, `paper.json`, etc.) are the engine's responsibility,
  driven by what the agent's response contained.
- Does NOT retry on failure. One shot per call. The loop primitive may
  re-dispatch on the next iteration if the verdict says CONTINUE.
- Does NOT cap prompt length. Engines that pack large `state_slice`
  dicts are responsible for trimming first.
- Does NOT estimate token cost pre-flight. Post-hoc `tokens_used` is
  recorded by the loop primitive in `_run-log.jsonl` (Phase 0
  decision §6).
