# Getting Started

A 5-minute walkthrough: install OMCR, open a research project, run a first session. Assumes you have Claude Code installed.

## 1. Install

**Option A — Claude Code plugin (recommended):**

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Then in any project, open Claude Code and run `/plugin` to list / load it.

**Option B — copy individual files** (no plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
# Copy the agents you want into a specific project's .claude/agents/:
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

Option B gives you the agents but skips the hooks and the slash commands. For full feature parity, use Option A.

## 2. Verify install

After loading, in a Claude Code session:

```
@
```

The autocomplete picker should now show 5 agents:
- `@supervisor`
- `@analysis-implementer`
- `@paper-writer`
- `@figure-descriptor`
- `@reviewer`

Slash command picker should show:
- `/todofig`
- `/sync`

If they appear, install succeeded.

## 3. Configure your project (one-time)

OMCR's agents are field-neutral by default. To use them, your project's `CLAUDE.md` needs minimal context. Open `CLAUDE.md` (or create one) at the root of your research project and add:

```markdown
## Project context

- **Working title:** [your project name]
- **Field:** [e.g., computational neuroscience / wet-lab biology / ML research]
- **First author / PI:** [your name] / [PI name]
- **Target venue:** [target journal / conference]
- **Central hypothesis:** [one sentence]
- **Narrative spine:**
  1. *Gap:* [what the field has not established]
  2. *Question:* [the specific testable question]
  3. *Approach:* [methodology in one sentence]
  4. *Finding:* [filled as results emerge]
  5. *Implication:* [what this changes]
```

For the `/todofig` and `/sync` commands, also add the [Research stack block](Configuration.md):

```markdown
## Research stack (used by /todofig, /sync, /cropfig)

- **Deck export dir:** figures/captured/
- **Outline file:** outline.md
- **Figure count:** [N]
- **Result pattern:** `^### Result (\d+)`
- **Report language:** English
- **Report output dir:** ./todofig_reports/
- **Sync report dir:** ./sync_reports/
```

The commands prompt for these on first run and offer to write the block automatically — you can skip this step and let them ask.

## 4. First session

Open Claude Code in your project root and try:

```
@supervisor where are we?
```

The supervisor will read your `CLAUDE.md` (and any `.claude/agent-memory/supervisor/MEMORY.md` if it exists — loaded via the `memory-load` hook), then give you a status orientation: what's known, what's the immediate next action, and which subagent to delegate to.

Then drill into a specific task:

```
@analysis-implementer implement the [your-analysis-name] pipeline
```

Or:

```
@paper-writer draft the Introduction
```

The four subagents (`analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`) report back to `@supervisor`. The supervisor decides when to advance and when to loop back.

## 5. Hooks behavior

Once the plugin is loaded, three hooks run automatically:

- **`pii-scrub`** (on every Write/Edit) — blocks writes whose content matches your PII pattern list. Customize via `.claude/scrub-patterns.txt` in your project.
- **`memory-load`** (on every session start) — auto-injects each agent's `MEMORY.md` into the new session's context.
- **`citation-warn`** (on every Write/Edit of manuscript markdown) — non-blocking warning when paragraphs lack citations.

To disable a hook for a project, set the corresponding env var (`CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1`, etc.) in `.claude/settings.json`. See [Hooks](Hooks.md) for details.

## Common pitfalls

- **No agents in the picker.** Plugin not loaded. Run `/plugin` and check it's listed; if not, verify the clone landed in `~/.claude/plugins/oh-my-claudecode-research`.
- **`/todofig` complains about missing config.** You haven't set up the [Research stack block](Configuration.md). On first run, let the command ask you for the fields — it'll offer to persist them automatically.
- **PII scrub blocks a legitimate write.** Edit your project's `.claude/scrub-patterns.txt` to refine the regex, or set `CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1` to bypass.
- **Memory not loading.** Check that `.claude/agent-memory/<agent>/MEMORY.md` files exist in your project. The `memory-load` hook is a no-op if no `agent-memory/` directory exists (deliberately safe-by-default).
- **Hooks not running.** Verify in `~/.claude/plugins/oh-my-claudecode-research/hooks/*.sh` that the scripts are executable (`chmod +x hooks/*.sh`). If they're not (Git on some systems strips exec bits), the plugin loader will silently skip.

## Next steps

- **[Configuration](Configuration.md)** — Full Research stack block reference + env vars
- **[Standalone Usage](Standalone-Usage.md)** — Concrete walkthroughs without OMC
- **[With OMC](With-OMC.md)** — Add OMC for richer features (literature wiki, python_repl, verifier, tracer)
- **[Specializing](Specializing.md)** — Author a field-specific preset
