---
name: save-session-log
description: Write a structured Markdown record of the current session — the requests, the analyses run, the files touched, decisions made, and open next steps — to the project's session-logs dir (one dated file per invocation), then propagate any durable result/decision into the wiki knowledge vault. This is a working record for the user, not a scientific artifact and not a status/sync report. Reconstructs content faithfully from the actual conversation; never invents. Use at the end of (or partway through) a session, or when the user types /save-session-log.
---

# Save Session Log

Write a structured Markdown record of what happened in **this** session to the project's
session-logs dir, so the user has a durable, skimmable trace of the conversation, the analyses
run, the files touched, and what's left open — then mirror any lasting knowledge into the wiki.

This is a **working record for the user** — not a scientific artifact, not a replacement for a
TODO file or agent memories, and not a sync/status report. Default to **English** for the
narrative; keep file paths, commands, filenames, and identifiers verbatim. Override the
narrative language via the project `CLAUDE.md`.

Reconstruct content from **this conversation's actual context** — do not invent. If something is
uncertain (e.g. whether a long job finished), say so explicitly rather than guessing.

## Configuration

Resolve config in priority order: env var → project `CLAUDE.md` `## Research stack` block → default.

| Setting | `## Research stack` key | Env var | Default |
|---|---|---|---|
| Session logs dir | `Session logs dir` | `SESSION_LOGS_DIR` | `session-logs/` |
| Wiki dir | `Wiki dir` | `WIKI_DIR` | `docs/wiki/` (if present) |

## Step 1 — Determine the output path

Get the timestamp from the shell (never assume the date):

```bash
mkdir -p <Session logs dir>
date '+%Y-%m-%d_%H%M'
```

Filename: `<Session logs dir>/session_<YYYY-MM-DD_HHMM>_<slug>.md`.
- `<slug>` = `$ARGUMENTS` if provided; otherwise derive a short kebab-case slug (≤4 words) from the session's main theme.
- If a file with the same name already exists, append `-2`, `-3`, … rather than overwriting.

## Step 2 — Reconstruct what happened (from context)

Scan the conversation and pull out, faithfully:

1. **What the user asked for** — each distinct request/goal this session, in order.
2. **What was actually done** — analyses run, code/files created or edited, commands executed, decisions reached. Tie each to its request.
3. **Where things were saved** — concrete paths for every created/modified/deleted file. Distinguish repo files from external outputs (cloud storage, etc.).
4. **Analysis results / numbers** — any quantitative findings, test outcomes, or verification results (mark long/background jobs that may be unfinished honestly).
5. **Decisions & rationale** — choices made and why (especially anything future sessions must not relitigate).
6. **Open / next steps** — unfinished work, things waiting on the user, follow-ups.
7. **Reproduction notes** — key commands or how to re-run / verify the session's work, if applicable.

Skip empty sections rather than padding them.

## Step 3 — Write the file

Use this structure (translate the headings if the project language is not English):

```
# Session Log — YYYY-MM-DD HHMM

**Slug:** <slug>
**One-line:** <what this session did, one sentence>

## 1. Goals / requests this session
- <request 1>

## 2. What was done (workflow)
- <task 1> — <result/state> ✅/🟡/❌

## 3. Files created / modified / deleted (save locations)
| Action | Path | What |
|--------|------|------|
| created | `path` | … |

## 4. Analysis results / verification (if any)
- <result/number — mark unfinished background jobs explicitly>

## 5. Decisions (do not relitigate)
- <decision + reason>

## 6. Open / next steps
- [ ] <todo / waiting-on>

## 7. Reproduction / reference commands (if any)
- `command` — what it does
```

Keep it concise and scannable — this is a record, not an essay.

## Step 4 — Propagate durable knowledge to the wiki (if a `Wiki dir` is configured)

The session log is a per-session trace; the **wiki** is the project's canonical distilled
knowledge base. When this session produced knowledge that outlives the session, mirror it in so
future sessions actually see it — this is the step that keeps the vault from going stale.

1. **Decide if anything is wiki-worthy.** A session earns a wiki edit only if it produced a
   **settled result / number**, a **status change** for a result, a **method/pipeline decision**
   future work must respect, or a **retired/added analysis**. Pure discussion, inconclusive
   debugging, or half-finished jobs are **not** wiki-worthy — log them only and skip this step.
2. **Find the matching page.** Map the knowledge to its home page, mirroring the existing vault
   layout — do not invent new top-level folders.
3. **Edit surgically, in the vault's own style.** Update the specific status marker / numbers /
   sentences in place; keep `[[wikilink]]` cross-references. Do not restructure a page, rewrite
   prose wholesale, or duplicate the whole log into the wiki.
4. **Gate the interpretive edits.** Factual status/number updates to an existing page: make them
   and report them. Anything that adds a **new page**, changes a **narrative framing**, or touches
   a **pre-registered success criterion**: do **not** write it — surface it in the Step 5 report as
   a proposal and let the user confirm first. Never silently contradict the canonical `Outline file`;
   if the session's result conflicts with it, flag it rather than overwriting the wiki to match.

If nothing is wiki-worthy, state "no wiki update (nothing settled to distill this session)" and move on.

## Step 5 — Confirm

After writing, tell the user:
1. the exact log file path created and a one-line summary of what it contains;
2. **which wiki pages were updated** (path + one-line what-changed for each), or "no wiki update"; and
3. any **proposed** wiki edits held back for confirmation (Step 4 gate), phrased as a yes/no question.

Do not commit to git unless the user asks.

## Guardrails

- **Faithful, not aspirational.** Only record what actually happened. Mark unfinished/background work as such; never claim a job succeeded without evidence in context. Same faithfulness for wiki edits — only distill confirmed knowledge.
- **New file per invocation** — never overwrite a prior log (disambiguate with `-2`, `-3`).
- **Side effects are limited to (a) writing the log and (b) surgical factual updates to existing wiki pages per Step 4.** Do not run analyses, edit other project files, or modify agent/user memories. New wiki pages, framing changes, and pre-reg edits are proposed-not-written. (For status snapshots + memory reconciliation use `/sync`; for figure TODOs use `/todofig`.)
- **Outline is canonical.** The wiki mirrors the `Outline file`; never let a wiki edit contradict it — flag the conflict instead.
- **Paths over prose** for the save-locations section — the user uses it to find things later, so be exact.
