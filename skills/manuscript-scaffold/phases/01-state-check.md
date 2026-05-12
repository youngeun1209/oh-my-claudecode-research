# Phase 1 — State check

Inspect `$MANUSCRIPT_DIR` and decide how to proceed.

| Current state | Action |
|---|---|
| Does not exist | Continue to phase 2. Dir will be created in phase 3. |
| Exists, empty (no tracked files, no `.git`) | Continue to phase 2. |
| Exists, contains files (non-VCS) | **Stop. Ask the user.** Do NOT clobber. Offer (a) pick a different `Manuscript dir`, (b) re-run after manually clearing the directory, (c) skip manuscript scaffolding entirely. |
| Exists, already a git repo | Note it. Continue to phase 2 — but phases 3 / 4 must NOT clobber existing branches or commits. |

## On user choice (existing content)

- **(a) Different dir** — accept the new path on the spot, update `$MANUSCRIPT_DIR`, and re-run phase 1 with the new value.
- **(b) Re-run later** — end the skill here. Report `stopped at phase 1 — user will clear and re-run`.
- **(c) Skip entirely** — end the skill here. Report `stopped at phase 1 — user declined manuscript scaffolding`.

The caller (e.g. `/omcr-setup`) decides whether to proceed with the remaining steps without manuscript scaffolding. Do not silently continue past a stop.

## Reporting from this phase

If continuing, record `manuscript_dir_state ∈ {does_not_exist, empty, existing_git_repo}` for phases 3 / 4 to consult.

If stopping, return the structured summary (see [SKILL.md](../SKILL.md) "Return value") with `stopped at phase 1` and the reason.
