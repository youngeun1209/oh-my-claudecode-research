---
name: update-version
description: When a project artifact whose filename carries a version — the canonical outline or the figure deck — is bumped (e.g. v4→v5, ver7→ver8), propagate the new filename into every file that references the old one (CLAUDE.md, command/skill files, agent memories, manuscript anchors, export scripts) so no downstream tool points at a stale file, then offer to delete genuinely-obsolete archive files (never auto-delete). Reads the previously-current values from CLAUDE.md ## Research stack (Deck file / Outline file). Dated historical records (sync/todofig reports, changelog entries) stay frozen. Use when the user bumps a version, or types /update-version.
---

# Update Version Pointers

When the user bumps a version — the figure `Deck file`, the `Outline file`, or a working copy of
either — **propagate the new filename/version into every file that references the old one** so no
downstream tool points at a stale file. Then **offer to delete genuinely-obsolete archive files**
(never auto-delete).

Default to **English** for the report; keep filenames verbatim. Override the report language via
the project `CLAUDE.md`.

**Core principle:** there is ONE current version of each artifact. Every *live* reference should
name the current file. The only references that stay frozen are **dated historical records**
(sync/todofig reports, dated changelog entries inside agent memories) — those record what was true
at a past date and must not be rewritten.

## Configuration

The previously-current values live in `CLAUDE.md` `## Research stack`:

| Setting | `## Research stack` key | Env var |
|---|---|---|
| Figure deck | `Deck file` | `DECK_FILE` |
| Outline | `Outline file` | `OUTLINE_FILE` |

The delta between these and the user's new files gives the rename pairs. **After propagating, update
the `## Research stack` values themselves** so they hold the new current names.

## Step 1 — Resolve the current files

You need the NEW current value for each bumped artifact (outline and/or deck). If `$ARGUMENTS`
contains `@`-mentions, parse them. Otherwise **ask the user and stop for input** — say exactly which
to provide and that they should reply with `@`-mentions. Do not guess versions. A user may bump only
one artifact (e.g. only the deck); accept a partial set and only propagate what changed.

## Step 2 — Derive OLD → NEW token pairs

For each bumped artifact:
- Read `CLAUDE.md` `## Research stack` — `Deck file:` and `Outline file:` hold the *previously-current*
  values. The delta gives the rename pairs (e.g. `figures_v7.key → figures_v8.key`; `outline_v4.md → outline_v5.md`).
- Also build **generic→versioned** pairs for any unversioned references (e.g. `outline.md → <new .md>`)
  if the project has legacy suffix-less references that silently resolve to the old file.
- Compute a **tolerant** search pattern that catches *any* old version, not just the immediate
  predecessor: e.g. `figures_v[0-9]+\.key`, `outline(_v[0-9]+)?\.(md|docx)`.

Print the derived OLD → NEW pairs before applying.

## Step 3 — Sweep for pointers (live search, cross-checked against a checklist)

The **live sweep is the source of truth** (line numbers drift — never trust cached line numbers).
Search the workspace for the tolerant pattern (force-include gitignored `.claude/` internals):

```bash
PAT='figures_v[0-9]|outline(_v[0-9]+)?\.(md|docx)|<your old tokens>'
grep -rInE "$PAT" . --include='*.md' --include='*.sh' --include='*.py' \
  -g '!.git' 2>/dev/null | grep -av 'Binary file' | sort -u
# .claude internals (some paths are gitignored):
grep -rInE --no-ignore --hidden "$PAT" .claude 2>/dev/null | grep -av 'Binary file' | sort -u
```

### LIVE pointers — UPDATE these (find by token, not cached line number)

Cross-check the sweep against the usual homes of a version pointer (project-specific — the sweep
finds the exact set):
- **`CLAUDE.md`** — `## Research stack` `Deck file:` / `Outline file:`; any prose in the file-layout / figure-map / conventions sections that names the current outline or deck.
- **Export / build scripts** — the variable or comment that names the deck the figure export reads (a stale name here silently breaks figure export).
- **Command / skill files** that hardcode the outline or deck name (e.g. a `/sync` docx-embed target, a `/todofig` mtime-compare line, the `cropfig` default deck path).
- **Manuscript anchors** — README / section files that say "anchored to `<outline>`".
- **Agent memories** — lines stating the *current* ground-truth outline/deck (leave dated "Last synced" markers + changelog bullets alone — those are frozen).

### FROZEN — never rewrite (dated historical records)

- Dated snapshot reports (e.g. `sync_reports/*.md`, `todofig_reports/*.md`).
- Every agent's `Last synced:` marker + past-dated changelog bullets; a sync-coordinator's dated log entries.
- A review *of* a past version, correctly named for that version.
- The **internal version header inside an archive file** (e.g. the `Outline v4` line atop `outline_v3.md`) — that file *is* that version.

## Step 4 — Apply the updates

Edit each LIVE pointer with the OLD → NEW replacement (exact string replacement; replace-all where the
token repeats). Then update the `## Research stack` `Deck file:` / `Outline file:` values to the new
names. After editing config/scripts, verify:

```bash
# script syntax still parses, and the new file the script now points to exists:
bash -n <export-script> && echo "export script OK"
ls -la <new deck/outline file>
```

If the user only bumped one artifact, only touch that artifact's pointers.

## Step 5 — Obsolete-file cleanup (DESTRUCTIVE — confirm first)

Superseded files accumulate. After the pointer update, list **delete candidates** (superseded outline
archives, retired generators, old changelogs) and ask the user which to remove. **Never delete without
explicit per-file confirmation.** Re-verify each still exists and is truly superseded before proposing.
Present them as a checklist (`[ ] delete` per file); act only on the ones the user checks. Use `git rm`
if tracked, `rm` if not. If a deleted file was referenced by a LIVE pointer, fix that reference too.

## Step 6 — Report

```
# Version pointer update — YYYY-MM-DD

## Renames applied
- <old> → <new>  (per artifact)

## Files updated (LIVE pointers)
- <file> : <what changed> ✅

## Skipped (FROZEN — historical records)
- <file / reason>

## Delete candidates (confirmation needed)
- [ ] <file>

## Verification
- export script syntax OK / new file exists / config values updated
```

End by noting anything the sweep surfaced that wasn't expected, so future runs know where new pointers live.

## Guardrails

- **Ask for the new file(s) first** (Step 1) unless `@`-mentioned. Never assume the new version number.
- **Never rewrite dated historical records** (Step 3 FROZEN list).
- **Never auto-delete** — Step 5 is confirm-gated, per file.
- **Verify after editing** scripts/config (Step 4) — a wrong deck name in an export script silently breaks `/todofig`, `/sync`, and `cropfig`.
- **Update `## Research stack` last** so it always reflects the new current state.
- If the live sweep surfaces a new pointer you didn't expect, update it and report it.
