# Phase 5 — Permission allowlist

Configure project-local `.claude/settings.json` so common research-flow tools do not prompt every time. **Dangerous operations are intentionally excluded** from the menu — git writes, file deletion, wildcard bash, unrestricted curl. Those always require explicit per-call approval.

## Step 5.1 — Surface existing state

Phase 1 recorded the state of `.claude/settings.json`. If broad wildcards or invalid entries are present, tell the user what was found:

> "Found in `.claude/settings.json`: <list>. These are broader / typo'd compared to the curated categories below."

Use AskUserQuestion:

**Question:** "How should I handle the existing permissions?"

**Options:**
1. **Narrow them (Recommended)** — replace `permissions.allow` with the curated category list you select below. The existing file is backed up to `.claude/settings.json.backup.YYYY-MM-DD`.
2. **Keep + add curated on top** — preserve existing entries (including broad wildcards), merge in the curated categories you select.
3. **Skip permissions entirely** — leave `.claude/settings.json` alone. Every tool call will continue to prompt as usual.

Record the choice as `PERMS_STRATEGY` ∈ {`narrow`, `merge`, `skip`}.

If `PERMS_STRATEGY = skip`, jump to phase 6.

If there is **no existing** `.claude/settings.json`, skip the question above — proceed directly to step 5.2 with `PERMS_STRATEGY = narrow` (i.e. create a fresh file from the selected categories).

## Step 5.2 — Curated category menu

Present these 7 categories with explanations. The user picks which to allow. Default ON/OFF indicated.

### ① Read-only Git inspection — *default ON*

- **What it does:** `git status`, `git diff`, `git log`, `git show`, `git branch` run without prompting.
- **Why safe:** All read-only — never modifies files, history, or remotes.
- **Skip if:** You want to see every git command before it runs (uncommon).

Patterns: `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git show:*)`, `Bash(git branch:*)`

### ② File search & exploration — *default ON*

- **What it does:** `ls`, `find`, `grep`, `rg`, plus the `Read` / `Glob` / `Grep` tools run freely.
- **Why safe:** All read-only — never modifies any file.
- **Skip if:** Almost never — without these, the agent cannot see your project.

Patterns: `Read`, `Glob`, `Grep`, `Bash(ls:*)`, `Bash(find:*)`, `Bash(grep:*)`, `Bash(rg:*)`

### ③ Edit code/text files — *default ON*

- **What it does:** Modify and create files (`.py`, `.tex`, `.bib`, `.md`, etc.) without prompting.
- **Why OK:** Every change is tracked by git — `git diff` shows it, `git checkout` reverts. The plugin's `pii-scrub` hook still blocks writes containing matched PII patterns.
- **Skip if:** Working on a sensitive final draft and you want every edit reviewed first.

Patterns: `Edit`, `Write`

### ④ LaTeX build — *default ON*

- **What it does:** `pdflatex`, `xelatex`, `lualatex`, `bibtex`, `biber`, `latexmk` run freely so the agent can compile your manuscript to PDF.
- **Why safe:** Only creates local build artifacts (`.aux`, `.pdf`, etc.). No network, no system changes.
- **Skip if:** Not a LaTeX project.

Patterns: `Bash(pdflatex:*)`, `Bash(xelatex:*)`, `Bash(lualatex:*)`, `Bash(bibtex:*)`, `Bash(biber:*)`, `Bash(latexmk:*)`

### ⑤ Citation API lookups — *default ON*

- **What it does:** `verify-citation` skill can fetch from CrossRef, OpenAlex, and doi.org without prompting.
- **Why safe:** Read-only HTTPS to public academic APIs. No auth, no payment, your data does not leave the machine.
- **Skip if:** Offline environment, or you verify citations manually.

Patterns: `WebFetch(domain:api.crossref.org)`, `WebFetch(domain:api.openalex.org)`, `WebFetch(domain:doi.org)`

### ⑥ Run Python analysis scripts — *default OFF*

- **What it does:** `python`, `python3`, `jupyter` can execute any of your scripts without prompting.
- **Warning:** This grants whatever your scripts can do — file writes, large downloads, system changes. Default OFF for safety. Enable only when you trust your scripts and find the prompts repetitive.

Patterns: `Bash(python:*)`, `Bash(python3:*)`, `Bash(jupyter:*)`

### ⑦ Figure crop tool (bundled) — *default ON*

- **What it does:** The plugin's `skills/cropfig/` Python helpers run without prompting. No other Python.
- **Why safe:** Scoped to the bundled scripts; they only crop images and write outputs to your figure directory.
- **Skip if:** Not using `cropfig`.

Patterns: `Bash(python skills/cropfig/*:*)`, `Bash(python3 skills/cropfig/*:*)`

Use AskUserQuestion (or a numbered checklist if AskUserQuestion does not support multi-select) and collect the user's selection.

## Step 5.3 — Excluded categories (informational)

After collecting selections, print this one-line note:

> "Intentionally excluded from auto-allow (will always prompt): git write (commit / push / gh), file deletion (rm / mv / git reset --hard), wildcard `Bash`, unrestricted `curl`. These are too easy to do irreversible damage with — opt in per call."

## Step 5.4 — Write `.claude/settings.json`

Build the new allowlist:

- **Selected categories** → resolve each to its patterns (above).
- If `PERMS_STRATEGY = narrow`: the new `permissions.allow` is exactly the union of selected category patterns.
- If `PERMS_STRATEGY = merge`: the new `permissions.allow` is the union of (existing entries) ∪ (selected category patterns), deduped, with invalid entries (e.g. `"Web Fetch"` with a space) dropped.

Backup first if a previous file exists:

```bash
if [ -f .claude/settings.json ]; then
  cp .claude/settings.json ".claude/settings.json.backup.$(date -u +%Y-%m-%d)"
fi
```

Then write using `jq` to ensure valid JSON:

```bash
mkdir -p .claude
ALLOWLIST_JSON='[<comma-separated quoted patterns>]'
jq -n --argjson allow "$ALLOWLIST_JSON" '{permissions: {allow: $allow}}' > .claude/settings.json
```

Validate:

```bash
jq empty .claude/settings.json && echo "VALID JSON"
jq '.permissions.allow | length' .claude/settings.json
```

Report:
- backup path (if a previous file existed),
- entry count,
- which categories ended up enabled.

## Note on scope

This phase writes **project-local** `./.claude/settings.json`. If the user wants the same allowlist globally, they can copy `.claude/settings.json` to `~/.claude/settings.json` manually. Project-local is the default because different research projects often have different stacks (Python-heavy vs LaTeX-only vs cropfig-only).
