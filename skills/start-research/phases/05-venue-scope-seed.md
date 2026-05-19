# Phase 5 — Venue scope seed (reviewer specialization)

Take the `Target venue` confirmed in phases 2–3 and seed `@reviewer`'s persistent memory with that venue's aims & scope, editorial priorities, and typical reviewer concerns. This is what makes `@reviewer` adversarial *at the right bar* instead of generic.

The information flows from one of two sources (in order):

1. **`templates/journal-registry.json`** — a curated, maintainer-verified entry. Fast, no network. Preferred when available.
2. **WebFetch fallback** — fetch the venue's publicly-listed author / scope page, summarize, and ask the user to confirm before writing. Used when the registry lookup fails.

The result is written to `.omx/omxr/agent-memory/reviewer/MEMORY.md` under a new section "Venue-specific bar". After that, the `memory-load.sh` hook auto-injects it into every `@reviewer` invocation — no further user action.

## When to skip

Skip this phase entirely if any of:

- `Target venue` field in `## Project context` is missing, empty, `[TBD]`, or starts with `[TBD:`.
- `.omx/omxr/agent-memory/reviewer/MEMORY.md` already contains a `## Venue-specific bar` section AND is **not byte-identical** to `templates/MEMORY.template.md` (i.e. the user has hand-written content — never overwrite).
- The user explicitly typed `--no-venue-seed` in `$ARGUMENTS` (record this for the phase 7 report).

If skipped, record the reason (`venue-missing` / `memory-modified` / `user-opted-out`) for the phase 7 report.

## Step A — Registry lookup

Read `templates/journal-registry.json` (canonical path inside the plugin). Search `venues` for an entry whose key OR any `aliases` entry matches `Target venue` **case-insensitively, exactly** (no fuzzy match — same policy as the journal-template lookup).

**Hit:** record the matched venue key. Extract `aims_and_scope`, `editorial_priorities`, `typical_reviewer_concerns`. If all three are non-null, jump to step C. If any are null (e.g. preprint servers, or sparsely-populated entries), treat as a partial hit and proceed to step B for the missing fields only.

**Miss:** proceed to step B for full WebFetch.

## Step B — WebFetch fallback (only when registry miss or partial)

1. Determine the source URL:
   - If the registry entry exists with a `submission_guidelines_url`, use that URL.
   - Otherwise, ask the user: "I don't have `<venue>` in the registry. Paste the URL of the venue's aims & scope / author guidelines page, or type `skip` to leave `@reviewer` generic."
   - If the user types `skip`, record `user-opted-out` and exit this phase.

2. WebFetch the URL with this exact prompt:

   > "Extract from this page only what the venue itself states about: (1) its aims and scope, in 1–2 sentences; (2) its editorial priorities — what it most weights in acceptance decisions, as a short bullet list; (3) the kinds of concerns its peer reviewers typically raise, if stated, as a short bullet list. Do NOT invent or infer beyond what the page explicitly states. If a field is not addressed on the page, return null for that field. Output as JSON with keys `aims_and_scope` (string|null), `editorial_priorities` (string[]|null), `typical_reviewer_concerns` (string[]|null)."

3. **If WebFetch fails** (network error, 404, paywall, hash-mismatch): record `fetch-failed`, write nothing, exit this phase. Surface in the phase 7 report so the user can rerun later.

4. Show the extracted JSON to the user verbatim. Ask: "I'll write this into `@reviewer`'s memory under 'Venue-specific bar'. Apply, edit, or skip?" Accept apply / edit (user provides revised text) / skip.

## Step C — Write to reviewer memory

Open `.omx/omxr/agent-memory/reviewer/MEMORY.md` (user's project root, not the plugin tree).

**If the file is byte-identical to `templates/MEMORY.template.md`** (untouched canonical scaffold from `$omxr-setup`), perform a full structured replacement:

- Update the `**Agent role:**` line to `Adversarial peer reviewer for <Target venue>`.
- Update `**Last synced:**` to today's ISO date.
- After the `## Project state` section header, append the canonical reviewer venue block (see template below) populated from the data gathered in step A / B.

**If the file is NOT byte-identical** (user has started editing) AND has no existing `## Venue-specific bar` section: **append** the venue block immediately after the existing `## Project state` section, leaving all other content untouched.

**If the file already has a `## Venue-specific bar` section**: skip this step (covered by the "skip if memory-modified" rule in the top guard). Record `already-seeded`.

### Canonical reviewer venue block

````markdown
## Venue-specific bar

**Target venue:** <Target venue>
**Seeded on:** <YYYY-MM-DD>
**Source:** <registry | webfetch:<host> | user-edited>

**Aims & scope (verbatim from source — paraphrased):**
<aims_and_scope sentence>

**Editorial priorities — review every draft against these:**
- <priority 1>
- <priority 2>
- ...

**Typical reviewer concerns at this venue — probe each one:**
- <concern 1>
- <concern 2>
- ...

<!--
  Maintained by $start-research phase 5. To refresh, delete this whole
  section and re-run $start-research. To override permanently, edit
  freely — the phase will not overwrite a section it already finds here.
-->
````

After writing, **show the diff** to the user (the new section, in context). No further confirmation needed for the registry path; the WebFetch path already confirmed in step B.

## Step D — Record outcome for phase 7

Track this phase's outcome:

| Outcome | When |
|---|---|
| `seeded-from-registry` | Step A full hit, step C wrote |
| `seeded-from-webfetch` | Step B confirmed, step C wrote |
| `seeded-from-user-edit` | Step B user-edited text, step C wrote |
| `partial-from-registry-plus-webfetch` | Registry partial hit + WebFetch filled gaps |
| `skipped-no-venue` | `Target venue` was missing / `[TBD]` |
| `skipped-memory-modified` | reviewer/MEMORY.md not byte-identical to template AND already has a venue section |
| `skipped-user-opted-out` | `--no-venue-seed` arg, or user typed `skip` |
| `skipped-fetch-failed` | WebFetch errored, no registry fallback |
| `already-seeded` | venue section already present, left untouched |

Phase 7 lists this on its own line under "Venue scope seed".

## Re-run policy

Re-running `$start-research` after step C wrote once will fall into `already-seeded` (because the `## Venue-specific bar` section now exists). To refresh:

- User deletes the section manually, then re-runs `$start-research`. The phase will write a fresh seed.

There is intentionally **no `--force-reseed`** — a deletion-by-hand is the explicit, reviewable action, matching the same pattern phase 4 uses for full memory resets.
