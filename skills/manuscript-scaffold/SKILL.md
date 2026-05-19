---
name: manuscript-scaffold
description: Scaffold a LaTeX manuscript directory for a research project — copy the bundled skeleton (main.tex + sections/* + figures/ + references.bib + .gitignore + README), optionally apply a journal-specific documentclass from templates/journal-registry.json, optionally clone an Overleaf project and cache the Git credential helper (token never persisted to tracked files), commit on the default branch, and ask before pushing. Invoked by $start-research phase 6, but also standalone-callable when adding a manuscript dir to an existing project later.
---

<Purpose>
Set up a LaTeX manuscript directory with optional journal-template customization and optional Overleaf Git integration. The heaviest, riskiest sub-flow inside $start-research (filesystem mutation, external archive fetches, credential handling, network push) — extracted into its own skill so the four sub-steps live in dedicated phase files for clarity, easier security review, and safer maintenance.
</Purpose>

<Use_When>
- `$start-research` reaches phase 6 and the user did not opt out of manuscript scaffolding.
- A project that was set up with `Manuscript dir` empty later wants to add a manuscript directory without re-running the full `$start-research` interview.
- An existing manuscript directory needs to be wired up to a fresh Overleaf project (re-invoke with the new URL — the skill detects existing state and asks before clobbering).
</Use_When>

<Do_Not_Use_When>
- The user wants only journal-template metadata captured in `AGENTS.md` without creating files (no skeleton, no commit) — that is a `AGENTS.md` edit, not this skill.
- The manuscript dir already has substantive content and the user is not asking to scaffold (phase 1 will stop anyway, but don't invoke if you already know).
- The project explicitly opted out of LaTeX (e.g. plain-markdown-only workflow). This skill is LaTeX-shaped.
</Do_Not_Use_When>

<Configuration>
Inputs are resolved by the caller (typically `$start-research`) from the project's `AGENTS.md` blocks, or passed directly when the skill is invoked standalone.

| Input | Required | Source | Used by |
|---|---|---|---|
| `MANUSCRIPT_DIR` | yes | `## Research stack` → `Manuscript dir` (default `paper/`) | all phases |
| `TARGET_VENUE` | no  | `## Project context` → `Target venue` | phase 2 (journal lookup) |
| `OVERLEAF_GIT_URL` | no | `## Research stack` → `Overleaf git URL` | phase 3 (clone), phase 4 (push target) |
| `WORKING_TITLE` | no | `## Project context` → `Working title` | phase 3 (README seed) |
| `CODEX_PLUGIN_ROOT` | yes | env var (set by Codex) | phase 2 (registry path), phase 3 (skeleton source) |

When invoked standalone (not from `$start-research`), if `MANUSCRIPT_DIR` is not given, read the project's `AGENTS.md` `## Research stack` block. If still missing, stop and ask the user.
</Configuration>

## Phases

Execute in order. Each phase is a separate file — read it, follow it exactly, then return here for the next phase.

1. **Phase 1 — State check.** Read [`phases/01-state-check.md`](phases/01-state-check.md). Decide whether to proceed, stop and ask the user, or skip (existing-content path).
2. **Phase 2 — Journal template lookup.** Read [`phases/02-journal-template.md`](phases/02-journal-template.md). Match `TARGET_VENUE` against the bundled registry; on user-confirmed match, prepare the `documentclass` / `bibstyle` rewrite values for phase 3. Skip if no venue.
3. **Phase 3 — Skeleton (with or without Overleaf).** Read [`phases/03-skeleton.md`](phases/03-skeleton.md). Branches internally on whether `OVERLEAF_GIT_URL` was provided.
4. **Phase 4 — Commit and ask before push.** Read [`phases/04-commit-push.md`](phases/04-commit-push.md). Always commit locally; only push on explicit user confirmation (default no on empty input).

If phase 1 stops the flow (existing content, user declines), do not run phases 2–4. Report what happened and return control to the caller.

## Security invariants (apply across all phases)

- **No `.cls` files bundled** in this plugin. Phase 2 may swap a `\documentclass` line in the skeleton copy only; any `.cls` archives a user opts into fetching go into the user's `MANUSCRIPT_DIR`, never into the plugin repo.
- **No silent network calls.** Phase 2's URL-fetch fallback runs WebFetch only when the user passes an `https://` URL **and** confirms the SHA256 of the downloaded archive before extraction.
- **No fuzzy venue matching.** Phase 2 matches case-insensitive *exact* against the registry name and aliases. A near-miss is a miss.
- **Overleaf token never written to a tracked file.** Phase 3 stores the token only in `git credential-store` (scoped to `git.overleaf.com`) or `~/.netrc`. Never write the token into `AGENTS.md`, agent memory, the project repo, or this plugin. When referencing the token in any output, mask all but the last 4 chars.
- **No auto-push.** Phase 4 always asks; default on empty input is `no`. On push failure, leave the local commit in place and surface the exact retry command.

## Return value (for the caller)

After phase 4 (or early stop), return a structured summary in this shape so the caller can fold it into its own report:

```
Manuscript scaffold: <created | skipped | stopped at phase N>
  Manuscript dir:    <path> (<created | existed empty | existed with content — skipped | overleaf clone>)
  Journal template:  <applied <class> + bibstyle <style> | not applied | no venue>
  Overleaf:          <connected to <masked URL> | local only | not configured>
  Branch / commit:   <branch> @ <short-SHA> (<pushed | push deferred | no remote>)
  Deferred push:     <exact `git -C <dir> push origin <branch>` command, only if push deferred>
```

The caller (e.g. `$start-research` phase 6) merges this into its end-of-run report.
