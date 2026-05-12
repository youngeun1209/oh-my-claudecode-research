# Getting Started

A 5-minute walkthrough: install OMCR, run `/omcr-setup` to initialize a project, start a first session. Assumes you have Claude Code installed.

## 1. Install

**Option A — Claude Code marketplace flow (recommended):** in any Claude Code session, run these one at a time (do not paste both at once):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Option B — manual checkout** (no plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Then run `/plugin` to load it.

**Option C — cherry-pick individual files** (skips hooks and commands):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

For full feature parity, use Option A.

## 2. Verify install

In a Claude Code session, type `@` and check the autocomplete picker for 6 agents:
`@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator`.

The slash-command picker should show `/omcr-setup`, `/start-research`, `/todofig`, `/sync`.

If they appear, install succeeded.

## 3. Initialize your project — `/omcr-setup` then `/start-research`

Two commands, in order. `/omcr-setup` is the installer (no questions). `/start-research` is the interview that fills in your project.

### 3a. `/omcr-setup` (install — no questions)

In your project's root, run:

```
/omcr-setup
```

This lays down the infrastructure OMCR needs:

- Empty `## Project context`, `## Research stack`, `## Language preference` blocks in `CLAUDE.md` (with `[TBD]` placeholders).
- `.claude/agent-memory/<agent>/MEMORY.md` for all 6 agents, from the canonical schema. Existing memory files are **never overwritten**.
- Empty `paper/references.bib` (with header comment) + `./references.csv` (with canonical header row) for `@literature-curator`.
- A curated `.claude/settings.json` permission allowlist. You pick which safe categories to auto-allow (read-only git, file search, edits, LaTeX build, citation API, figure crop). Dangerous operations (git write, file deletion, wildcard bash) are **never offered** — they always prompt per call.

If a previous `.claude/settings.json` had broad wildcards (`"Bash"`, `"Write"`, etc.) or invalid entries (`"Web Fetch"` with a space), `/omcr-setup` offers to narrow them with backup to `.claude/settings.json.backup.YYYY-MM-DD`.

Safe to re-run after plugin updates — never overwrites your filled-in content.

### 3b. `/start-research` (interview — fills your project in)

```
/start-research
```

This walks an interactive interview to fill the `[TBD]` placeholders that `/omcr-setup` scaffolded:

**`## Project context`** (scientific identity — never invented for you)
- Working title, field / sub-field, first author / PI
- Target venue (+ optional 2–3 backups)
- Central hypothesis, research topic, datasets
- Narrative spine: Gap / Question / Approach / Implication

**`## Research stack`** (infrastructure — defaults proposed, you can accept)
- `Deck file` (`.key` / `.pptx` path), outline file, figure count, result-pattern regex
- Report language and output directories
- `BibTeX file` and `Summary file` paths for `@literature-curator`
- Optional: CrossRef email, Overleaf git URL

**Preset overlay** (optional) — apply `neuro-fmri` or stay field-neutral. Only replaces agent `MEMORY.md` files that are still byte-identical to the canonical template (so you can re-run safely without losing notes).

**Manuscript scaffold** — delegates to the `manuscript-scaffold` skill: copies the LaTeX skeleton into `Manuscript dir`, optionally rewrites `\documentclass` from `templates/journal-registry.json` based on your target venue, optionally clones an Overleaf project (paid plan + Git Integration required), commits locally, asks before pushing.

If you run `/start-research` before `/omcr-setup`, it offers to run `/omcr-setup` automatically and then continue.

### What if you don't know the answers yet?

**Infrastructure fields** — accept the proposed default by pressing enter / typing `[skip]`.

**Scientific fields** — say "skip" or "don't know yet". `/start-research` pushes back **once** with the reason it matters (e.g. "without a hypothesis, `@supervisor` will ask every conversation"), then accepts `[TBD: <one-line note>]` if you still skip. **It never invents content** for hypothesis / venue / dataset / topic / spine — those are scientific decisions only you can make.

Every `[TBD: ...]` becomes a tracked follow-up item that `@supervisor` will surface in later conversations.

### Skipping the nudge

If you skip both `/omcr-setup` and `/start-research`, the SessionStart `setup-nudge` hook prints a one-line reminder at every session start until you initialize. Suppress with `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

Safe to re-run either command later — they surface existing values as defaults and only write through changes you confirm.

## 4. First real session

After `/omcr-setup`, start with:

```
@supervisor where are we?
```

Supervisor reads `CLAUDE.md` plus its memory and orients you: what's known, what's the immediate next action, and which subagent to delegate to.

Then drill into a specific task:

```
@analysis-implementer implement the [your-analysis-name] pipeline
@paper-writer draft the Introduction
@figure-descriptor design Fig 2 — show [the result]
@literature-curator resolve all [CITE: ...] placeholders in the Introduction
@reviewer stress-test the Methods at our target-venue bar
```

The five "doer" subagents report back to `@supervisor`, who decides when to advance and when to loop back.

## 5. Hooks behavior

Once the plugin is loaded, four hooks run automatically:

- **`pii-scrub`** (on every Write/Edit) — blocks writes whose content matches your PII pattern list. Customize via `.claude/scrub-patterns.txt` in your project.
- **`memory-load`** (on every session start) — auto-injects each agent's `MEMORY.md` into the new session's context.
- **`setup-nudge`** (on every session start, until you've run `/omcr-setup`) — one-line non-blocking reminder if `CLAUDE.md` is missing the `## Project context` or `## Research stack` blocks.
- **`citation-warn`** (on every Write/Edit of manuscript markdown) — non-blocking warning when paragraphs lack citations.

To disable a hook for a project, set the corresponding env var (`CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1`, `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`, etc.) in `.claude/settings.json`. See [Hooks](Hooks.md) for details.

## Common pitfalls

- **No agents in the picker.** Plugin not loaded. Run `/plugin` and check it's listed; if not, verify the marketplace/clone landed correctly.
- **`/omcr-setup` keeps nudging me.** You haven't run it yet, or your CLAUDE.md is missing one of the two blocks. Run `/omcr-setup`, or set `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` to silence the nudge.
- **PII scrub blocks a legitimate write.** Edit your project's `.claude/scrub-patterns.txt` to refine the regex, or set `CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1` to bypass.
- **Memory not loading.** Check that `.claude/agent-memory/<agent>/MEMORY.md` files exist in your project. The `memory-load` hook is a no-op if no `agent-memory/` directory exists (deliberately safe-by-default).
- **Hooks not running.** Verify in `~/.claude/plugins/oh-my-claudecode-research/hooks/*.sh` that the scripts are executable (`chmod +x hooks/*.sh`). If they're not (Git on some systems strips exec bits), the plugin loader will silently skip.

## Next steps

- **[Configuration](Configuration.md)** — Full Research stack block reference + env vars
- **[Standalone Usage](Standalone-Usage.md)** — Concrete walkthroughs without OMC
- **[With OMC](With-OMC.md)** — Add OMC for richer features (literature wiki, python_repl, verifier, tracer)
- **[Specializing](Specializing.md)** — Author a field-specific preset
