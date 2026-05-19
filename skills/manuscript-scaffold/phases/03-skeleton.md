# Phase 3 — Skeleton (with or without Overleaf)

Branches on whether `$OVERLEAF_GIT_URL` was provided.

## Skeleton contents (used by both branches)

Source: `$CODEX_PLUGIN_ROOT/templates/manuscript-skeleton/`. After copying, the layout in `$MANUSCRIPT_DIR/` is:

```
<MANUSCRIPT_DIR>/
  main.tex                  # documentclass line possibly rewritten per phase 2
  sections/{abstract,introduction,methods,results,discussion}.tex
  figures/.gitkeep
  references.bib            # empty header — managed by @literature-curator
  .gitignore                # LaTeX build artifacts
  README.md                 # conventions reference (+ "Journal template" section if phase 2 applied)
```

If phase 2 produced a rewrite plan, apply it to the **copied** `main.tex` (not the plugin source) before continuing.

---

## Branch A — No Overleaf (`$OVERLEAF_GIT_URL` is empty)

1. Create `$MANUSCRIPT_DIR` if missing.
2. Copy the skeleton from `$CODEX_PLUGIN_ROOT/templates/manuscript-skeleton/` into it.
3. If phase 2 recorded a rewrite plan, apply it to `<MANUSCRIPT_DIR>/main.tex` and append the "Journal template" section to `<MANUSCRIPT_DIR>/README.md`.
4. Initialize git if the dir is not already a repo: `git init` in `$MANUSCRIPT_DIR`.
5. Continue to phase 4.

---

## Branch B — Overleaf (`$OVERLEAF_GIT_URL` is non-empty)

### B1 — Pre-flight disclosure (do this once, before touching anything)

Tell the user:

- Overleaf Git Integration requires a **paid Overleaf plan** (Personal / Pro / Group / Premium). On the free tier this will fail.
- The user must have **already created an empty project on Overleaf** — we cannot create one programmatically (that needs the browser). The Git URL comes from `Overleaf menu → Sync → Git`.
- The user must generate a **Git authentication token** at `Overleaf → Account Settings → Git Integration → Generate Token`. The token grants access to **all** their Overleaf projects, so treat it as a secret.

### B2 — Token handling — non-negotiable

- **NEVER** write the token into `AGENTS.md`, the project repo, agent memory, this plugin, or any tracked file.
- **NEVER** echo the full token back to the user. If you must reference it, mask all but the last 4 characters.
- The token value lives only in (i) the user's session input and (ii) the credential store the user picked. Nowhere else.

### B3 — Collect URL + token

1. Confirm the URL format matches `https://git.overleaf.com/<24-hex-id>`. Reject anything else and stop.
2. Ask the user to paste the Git authentication token. Treat the input as sensitive — do not echo full value, do not log it.

### B4 — Cache the credential

Ask the user which credential helper they prefer (default to `git credential-store`):

**Option 1 — `git credential-store` (default):**
```bash
git config --global credential.https://git.overleaf.com.helper store
# then append a single line to ~/.git-credentials:
#   https://git:<TOKEN>@git.overleaf.com
```

**Option 2 — `~/.netrc`:**
```
machine git.overleaf.com
  login git
  password <TOKEN>
```

Scope the credential to `git.overleaf.com` only. Do not write a host-wildcard entry.

### B5 — Verify access

```bash
git ls-remote "$OVERLEAF_GIT_URL" HEAD
```

If this fails, stop. Show the error verbatim. Ask the user to re-check (i) the URL, (ii) the token, (iii) that their Overleaf plan includes Git Integration. Do not proceed.

### B6 — Detect whether the Overleaf project is empty

A truly empty Overleaf project returns no refs from `git ls-remote "$OVERLEAF_GIT_URL"`. A non-empty one returns the default branch.

**If non-empty:**
- Show the user what is there (branches + last commit summary).
- **Stop and ask.** Do not clobber an existing Overleaf project. Offer (a) pick a different Overleaf project, (b) skip Overleaf integration entirely (fall back to Branch A — local only), (c) manually clear the Overleaf project via the web UI and re-run.

**If empty:** continue.

### B7 — Clone

```bash
git clone "$OVERLEAF_GIT_URL" "$MANUSCRIPT_DIR"
```

For a truly empty remote, git will warn that the remote is empty — this is expected.

### B8 — Detect the default branch name

New Overleaf projects use `master`; some newer ones use `main`. After the clone:

```bash
git -C "$MANUSCRIPT_DIR" remote show origin | awk '/HEAD branch/ {print $NF}'
```

If the clone showed an empty remote (no `HEAD branch` line), default `default_branch=master` (Overleaf's historical default). The first commit in phase 4 will create the branch.

### B9 — Copy the skeleton over the (empty) clone

Copy `$CODEX_PLUGIN_ROOT/templates/manuscript-skeleton/` into `$MANUSCRIPT_DIR` (which is now a git repo with `origin` pointing at Overleaf). If phase 2 recorded a rewrite plan, apply it to `<MANUSCRIPT_DIR>/main.tex` and append the "Journal template" section to `<MANUSCRIPT_DIR>/README.md`.

Continue to phase 4.

---

## State recorded for phase 4

After this phase, record:

- `default_branch` — `master` / `main` (or the local detection when no remote).
- `has_remote` — `true` if Branch B succeeded, else `false`.
- `overleaf_url_masked` — the URL with everything after `https://git.overleaf.com/` truncated to last 4 chars, for safe reporting.
