# Hooks And Explicit Checks

OMXR ships four shell helpers under `hooks/`. Codex plugin manifests expose skills and metadata; they do **not** make these helpers active by themselves. Base `omx setup` owns the generic Codex hook runtime, and `$omxr-setup` may report or add clearly named OMXR wrappers only when it can preserve existing hook entries.

If native hook support is unavailable for a feature, the same helper should be used as an explicit workflow check.

## Feature Matrix

| Feature | Helper | Preferred end state | Fallback |
| --- | --- | --- | --- |
| PII scrub | `hooks/pii-scrub.sh` | Native write-interception hook when supported | Explicit check before write-heavy finalization |
| Memory load | `hooks/memory-load.sh` | Native/runtime session hook | Workflow skills read `.omx/omxr/agent-memory/*/MEMORY.md` explicitly |
| Citation warn | `hooks/citation-warn.sh` | Native post-write hook when supported | Explicit manuscript check in finalization workflows |
| Setup nudge | `hooks/setup-nudge.sh` | Native/runtime session hook | `$omxr-setup --dry-run` style readiness report |

## PII Scrub

`pii-scrub.sh` reads a Codex hook JSON payload from stdin and exits `2` when staged file content matches a configured pattern.

Pattern lookup order:

1. `.omx/omxr/scrub-patterns.txt`
2. `hooks/default-scrub-patterns.txt`

Smoke test:

```bash
echo '{"tool_input":{"file_path":"a.md","content":"alice@example.com"}}' | bash hooks/pii-scrub.sh
echo '{"tool_input":{"file_path":"a.md","content":"hello"}}' | bash hooks/pii-scrub.sh
```

Disable with `CODEX_RESEARCH_DISABLE_PII_SCRUB=1`.

## Memory Load

`memory-load.sh` prints `.omx/omxr/agent-memory/*/MEMORY.md` content for use by a native/runtime session hook or an explicit workflow prelude. If no memory directory exists, it exits `0` silently.

Disable with `CODEX_RESEARCH_DISABLE_MEMORY_LOAD=1`.

## Citation Warn

`citation-warn.sh` checks manuscript-like markdown payloads for long uncited paragraphs and exits `0` after printing warnings. It is intentionally non-blocking.

Disable with `CODEX_RESEARCH_DISABLE_CITATION_WARN=1`.

## Setup Nudge

`setup-nudge.sh` detects missing `AGENTS.md`, `## Project context`, or `## Research stack` blocks and prints a non-blocking `$omxr-setup` nudge. It is silent inside the plugin checkout itself.

Disable with `CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1`.

## Wiring Rules

- Do not assume `.codex-plugin/plugin.json` registers hooks.
- Do not overwrite user or base OMX hook entries.
- If `$omxr-setup` installs wrappers, they must be clearly named OMXR entries and preserve existing `.codex/hooks.json` content.
- If native hook support cannot provide the relevant event, document and use the explicit check path instead.

See also [`hooks/README.md`](../hooks/README.md).
