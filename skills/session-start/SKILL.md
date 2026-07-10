---
name: session-start
description: Session-orientation workflow — read the project's Markdown corpus (CLAUDE.md, the outline, project MEMORY, the wiki landing page), build a genuine understanding of the study, then report a concise project summary and an honest current-status snapshot. Read-only with zero side effects — no exports, no memory edits, no report files, no analysis runs. Runs in light mode (cheap, core files only — the default for auto-trigger) or full mode (full corpus sweep). Use at the start of a session to reproduce the effect of "understand this project", or when the user types /session-start.
---

# Session Start (orientation)

Reproduce the effect of the user saying *"understand this project"* at the start of a
session: **read the project's Markdown corpus, build a genuine understanding, then report a
concise project summary and an honest current-status snapshot.**

This is a **read-and-report** workflow with **no side effects**: do NOT export a figure deck,
edit memories, write report files, or run analyses. (For a status snapshot + memory
reconciliation use `/sync`; for figure↔outline gap TODOs use `/todofig`.)

Default to **English** for the report; keep file names and identifiers verbatim. Override the
report language via the project `CLAUDE.md`.

## Configuration

Resolve config in priority order: env var → project `CLAUDE.md` `## Research stack` block → default.

| Setting | `## Research stack` key | Env var | Default |
|---|---|---|---|
| Outline file | `Outline file` | `OUTLINE_FILE` | `outline.md` |
| Wiki dir | `Wiki dir` | `WIKI_DIR` | `docs/wiki/` (if present) |

## Modes — light (default for auto-trigger) vs full

- **Light mode** — the default when invoked by a SessionStart hook (its injected context will
  say "light mode"), or when the user types `/session-start light`. Do **Step 1 → Step 3 → Step 4**
  only; **skip Step 2** (the full corpus sweep). Rationale: the harness already auto-injects
  `CLAUDE.md`, the project `MEMORY.md`, and agent memories at startup; light mode only adds the
  outline + wiki landing page synthesis that isn't auto-loaded. Keep the report tight.
- **Full mode** — when the user types `/session-start` (no arg), `/session-start full`, or passes
  a focus area. Do **all steps**, including the Step 2 corpus sweep.

If unsure which mode, default to **light**.

## Step 1 — Read the orientation core (always — both modes)

Read these first — they are the spine of the project:

1. `CLAUDE.md` — the single most authoritative file (`## Project context` = scientific identity; `## Research stack` = config).
2. The **`Outline file`** (from `## Research stack`) — the canonical outline / scientific ground truth; supersedes any digest table in `CLAUDE.md` if they disagree.
3. Any project TODO / execution-state file the outline or CLAUDE.md points to (what is ✅ / 🟡 / ⬜ / 🚧).
4. The **wiki landing page** if a `Wiki dir` is configured (e.g. `<Wiki dir>/home.md` or `Home.md`) — one cheap file that mirrors the outline in curated form and tells you which wiki pages to open in Step 2. **Scientific-content precedence:** `Outline file` (canonical) > wiki (curated) > memory. If the wiki disagrees with the outline, trust the outline and flag it.
5. The project `MEMORY.md` files (usually already injected at session start — re-scan rather than re-read if so).

## Step 2 — Sweep the rest of the Markdown corpus  (FULL mode only — skip in light mode)

Discover every other `.md` in the workspace and read those relevant to current state:

```bash
find . -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
```

Prioritize and read as needed: pipeline/method docs, the configured `Wiki dir` result & method
pages (from the landing page's links — open the pages relevant to current work rather than the
whole vault), and the most recent dated reports (e.g. under a `sync_reports/` or `todofig_reports/`
dir if present). **Budget note:** read the Step 1 core fully; for the rest, read the most recent /
most relevant files and skim archives. State in the report if you deliberately skipped archives.

**Freshness check:** if the `Outline file` is newer than the TODO / latest report, flag that the
status files may lag the outline.

## Step 3 — Build the understanding

Synthesize — do not just concatenate file contents. Make sure you can answer:

- **The claim** — the one-line thesis and the canonical key-finding statement.
- **The narrative spine** — Gap → Question → Approach → Finding → Implication.
- **The load-bearing fact(s)** — the empirical result(s) the argument rests on, and any invariants / non-circularity commitments.
- **Result structure** — the current results/figures layout and what each asserts.
- **Pre-registered commitments** — any success criteria + fallbacks that are not to be relitigated.

## Step 4 — Report

Deliver a concise orientation report (this is orientation, not a manuscript):

```
# Project orientation — YYYY-MM-DD

## Identity
- Title / lead author · PI / target venue / central hypothesis (one sentence)

## Narrative spine
- Gap → Question → Approach → Finding → Implication (one line each)
- Invariants / non-circularity commitments
- Most load-bearing empirical fact

## Result structure (current N results / M figures)
- R1 … RN, one line each + owning figure + what it asserts

## Current status
| Result | Figure | State | Remaining work |
(✅ done / 🟡 partial / ⬜ not started / 🚧 new·in-progress)

## Most urgent work (P0)
- 1–3 items from the TODO's P0 tier

## Caution / drift flags
- File-to-file inconsistencies, status files older than the outline, unresolved CRITICAL issues
```

End with one line offering next steps.

## Argument handling

- `light` → **light mode** (Step 1 → 3 → 4; skip Step 2). Also what a SessionStart hook requests.
- `full` or empty → **full mode** (all steps, full corpus sweep).
- A focus area (e.g. `R3`, `figures`) → **full mode** but **narrow Step 4's status report to that focus** — give that result/figure its full detail and compress the rest into a one-line context header.

## Guardrails

- **Read-only.** No exports, no memory edits, no report files, no analysis runs. If the user wants any of those, point them to `/sync` or `/todofig`.
- **Outline wins.** When a `CLAUDE.md` digest table and the `Outline file` disagree, trust the outline and flag the discrepancy. Precedence: `Outline file` > wiki > memory.
- **No fabrication.** If a file is missing or unreadable, say so; do not invent panel contents, numbers, or status.
- **Observed state over stale memory.** If a memory/report contradicts the current outline or TODO, prefer the current files and flag the drift.
