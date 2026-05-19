# Phase 4 — Commit on the default branch, then ask before pushing

**Safety harness:** local commits are always safe; pushing is irreversible from the user's perspective (collaborators see it immediately) and requires explicit confirmation. Never auto-push, even when an Overleaf URL is configured.

## 1. Determine the default branch

```bash
# If phase 3 ran branch B and set a remote:
default_branch=$(git -C "$MANUSCRIPT_DIR" remote show origin 2>/dev/null | awk '/HEAD branch/ {print $NF}')

# Else (local-only, no remote):
default_branch=$(git -C "$MANUSCRIPT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
```

If the clone in phase 3 came from an empty Overleaf remote, there is no checked-out branch yet — initialize one matching the remote's `HEAD` symref, or default to `master` (Overleaf's historical default).

## 2. Check out the default branch

```bash
git -C "$MANUSCRIPT_DIR" checkout "$default_branch"
```

If the branch does not exist locally yet (empty-clone case), create it with `git checkout -b "$default_branch"`.

## 3. Stage and commit

```bash
git -C "$MANUSCRIPT_DIR" add .
git -C "$MANUSCRIPT_DIR" commit -m "Scaffold manuscript via oh-my-codex-research $omxr-setup

- main.tex with section includes
- sections/{abstract,introduction,methods,results,discussion}.tex stubs
- figures/ (empty, .gitkeep)
- references.bib (empty, managed by @literature-curator)
- .gitignore for LaTeX artifacts
"
```

## 4. Show the commit summary and ask before pushing

Show `git -C "$MANUSCRIPT_DIR" log -1 --stat`, then ask **explicitly**:

```
Manuscript scaffold committed locally on `<default_branch>`.
<if has_remote (Overleaf was configured in phase 3)>
  This would push to your Overleaf project at <overleaf_url_masked>.
  Saying "yes" makes the scaffold visible in Overleaf web immediately.
  Saying "no" keeps the commit local — you can run `git push` later when ready.
<else>
  Local-only — no remote configured. (No push to perform.)
</if>

Push now? (y/N)
```

Default on empty input is **no**. Err on the side of not touching the network.

## 5. Push only on explicit `y` / `yes`

```bash
git -C "$MANUSCRIPT_DIR" push origin "$default_branch"
```

### On push failure

- Show the error verbatim.
- Leave the local commit in place. Do not retry automatically.
- Surface the exact retry command:
  ```
  git -C <MANUSCRIPT_DIR> push origin <default_branch>
  ```
- Record `push_status = failed` for the return summary so the caller can include the retry command in its final report.

### On user declined (or no remote)

Record `push_status = deferred` (or `no_remote`). Record the exact retry command so the caller can surface it in its final report.

### On push success

Record `push_status = pushed`.

## Return values for the caller

After this phase, return to the caller:

```
manuscript_dir_state: <created | existed empty | overleaf clone>
journal_template:     <applied(<class>, <bibstyle>) | not applied | no venue>
overleaf:             <connected_to(<masked URL>) | local only | not configured>
default_branch:       <branch>
commit_sha:           <short SHA>
push_status:          <pushed | deferred | failed | no remote>
deferred_push_cmd:    <exact git command, only if deferred / failed>
```

The caller (e.g. `$omxr-setup` Step 6) merges these into its end-of-run report.
