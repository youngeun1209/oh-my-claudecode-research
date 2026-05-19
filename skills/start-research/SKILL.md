---
name: start-research
description: Interview-driven first-research-project initialization — asks about working title, field, hypothesis, target venue, datasets, narrative spine; fills the AGENTS.md placeholders that $omxr-setup scaffolded; applies an optional domain preset to agent memory (when the existing MEMORY.md is still canonical-template); seeds @reviewer's persistent memory with target-venue aims/scope/editorial-priorities (registry-first, WebFetch fallback); scaffolds the LaTeX manuscript directory via the manuscript-scaffold skill. Requires $omxr-setup to have run first — will offer to run it if not. Safe to re-run; never overwrites filled-in answers, modified MEMORY.md, or existing manuscript content.
---

# Start-Research

Interview-style flow that takes a freshly-installed OMXR project (post-`$omxr-setup`) and walks the user through filling in **what their research is about** — working title, hypothesis, target venue, datasets, narrative spine, preset choice — then scaffolds the LaTeX manuscript directory.

**When this skill is invoked, immediately execute the workflow below. Do not only restate or summarize these instructions back to the user.**

This is the "deep interview" complement to `$omxr-setup`'s "install" role.

## Argument parsing

Inspect `$ARGUMENTS` (passed through by [`commands/start-research.md`](../../commands/start-research.md)). Treat the **first token** as the preset hint:

- `minimal` — skip the preset-overlay prompt entirely (no `examples/<field>/` overlay)
- `neuro-fmri` — pre-select the neuro-fMRI preset overlay (still confirms before applying in phase 2)
- `no-overlay` — alias of `minimal`
- (empty) — ask the user during the interview (phase 2)

Additional standalone flags (may appear in any position; not mutually exclusive with the preset hint):

- `--no-venue-seed` — skip phase 5 (venue scope seed). `@reviewer` stays generic. Record this so phase 7 surfaces it.

Record the preset hint as `preset_arg` and any flags as `flags` so downstream phases can consume them.

## Phase execution

Execute phases sequentially. For each phase, read the linked file and follow its instructions exactly. If an earlier phase reports an early stop (e.g. user cancelled, `$omxr-setup` not run and user declined to run it), do **not** skip phase 7 (the report) — surface the stop reason there.

1. **Phase 1 — Precheck.** Read [`phases/01-precheck.md`](phases/01-precheck.md).
2. **Phase 2 — Interview.** Read [`phases/02-interview.md`](phases/02-interview.md).
3. **Phase 3 — Fill AGENTS.md.** Read [`phases/03-fill-agents-md.md`](phases/03-fill-agents-md.md).
4. **Phase 4 — Preset overlay (agent memory).** Read [`phases/04-preset-overlay.md`](phases/04-preset-overlay.md).
5. **Phase 5 — Venue scope seed (reviewer specialization).** Read [`phases/05-venue-scope-seed.md`](phases/05-venue-scope-seed.md). Runs **after** phase 4 on purpose: if phase 4 installed a preset reviewer `MEMORY.md`, phase 5 appends the venue block to it without disturbing the preset content. If phase 4 didn't run (no preset), the canonical template is still byte-identical to the schema, so phase 5 performs a full structured replacement instead.
6. **Phase 6 — Manuscript scaffold (delegated).** Read [`phases/06-manuscript-scaffold.md`](phases/06-manuscript-scaffold.md). This phase delegates to the `manuscript-scaffold` skill.
7. **Phase 7 — Report.** Read [`phases/07-report.md`](phases/07-report.md).

## Re-running policy

Safe to re-run on an initialized project. The re-run contract:

- Phase 2 surfaces existing `AGENTS.md` values as defaults. The user can confirm-all to apply only newly-added fields.
- Phase 3 writes only fields that changed.
- Phase 4 only replaces agent `MEMORY.md` files that are still byte-identical to the canonical template (untouched). Modified memory is never overwritten.
- Phase 5 leaves an existing `## Venue-specific bar` section in `reviewer/MEMORY.md` alone. To refresh, delete just that section and re-run.
- Phase 6 delegates to `manuscript-scaffold`, which has its own existing-content guard.

If the user wants to **reset** an agent's memory, instruct them to delete that specific `.omx/omxr/agent-memory/<agent>/MEMORY.md` and re-run `$start-research`. There is intentionally no `--reset` flag — deletion is an explicit, reviewable action.

## Final recommendation

After phase 7's report, end by recommending the user run `@supervisor where are we?` for the first real conversation.
