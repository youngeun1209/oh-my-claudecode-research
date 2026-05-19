# Phase 5 — Hook and Check Readiness

Codex/OMX hook support differs from older host runtimes. This phase classifies each OMXR safety feature as native, runtime fallback, or explicit check.

## Matrix

| Feature | Preferred end state | Fallback |
| --- | --- | --- |
| Memory load | Native/runtime hook references `.omx/omxr/agent-memory/*/MEMORY.md` | Workflow skills read memory explicitly at start |
| Setup nudge | Native/runtime hook detects missing `AGENTS.md`/`.omx/state/omxr` | `$omxr-setup --dry-run` reports missing scaffolding |
| PII scrub | Native write-interception hook when supported | Explicit `$pii-scrub` check before write-heavy finalization |
| Citation warn | Native post-write hook when supported | Explicit `$citation-warn`/`$verify-citation` check in manuscript workflows |

## Behavior

1. Inspect `.codex/hooks.json` if present.
2. Do not remove or overwrite non-OMXR hook entries.
3. If adding wrappers, use clearly named OMXR entries and preserve base OMX hooks.
4. Ensure `.omx/omxr/scrub-patterns.txt` exists only when the project needs local pattern overrides. Otherwise use `hooks/default-scrub-patterns.txt`.
5. Record the chosen state for each feature so phase 6 can report it.

## Environment variables

Use `CODEX_RESEARCH_DISABLE_<NAME>=1` names for OMXR-specific disables:

- `CODEX_RESEARCH_DISABLE_PII_SCRUB`
- `CODEX_RESEARCH_DISABLE_MEMORY_LOAD`
- `CODEX_RESEARCH_DISABLE_SETUP_NUDGE`
- `CODEX_RESEARCH_DISABLE_CITATION_WARN`

Legacy disable variables may be recognized only in migration notes.
