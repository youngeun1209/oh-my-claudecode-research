# Hooks — reference

OMCR ships 3 shell-script hooks under `hooks/`, registered via `hooks/hooks.json`. They run automatically once the plugin is loaded. All three are written in plain `bash` + `python3` — no Node, no MCP, no external runtime.

## `pii-scrub.sh` — block writes containing PII

**Event:** `PreToolUse:Write|Edit` (runs **before** every file Write or Edit)

**Behavior:** Reads the staged file content from the tool-call JSON payload. Greps it against a list of regex patterns. If any pattern matches, blocks the write with **exit 2** + a stderr message naming the matched pattern(s).

**Pattern lookup order:**
1. `.claude/scrub-patterns.txt` in the current project (wins entirely if present)
2. `hooks/default-scrub-patterns.txt` shipped with OMCR (fallback)

**Default patterns** (`hooks/default-scrub-patterns.txt`):
- Email addresses
- US Social Security Numbers (strict 9-digit form)
- 6-digit subject IDs (common in HCP-style datasets)
- Placeholder for adding your own

**Disable per-project:** `CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1` env var in `.claude/settings.json`.

**Test:**
```bash
echo '{"tool_input":{"file_path":"a.md","content":"alice@example.com"}}' \
  | bash hooks/pii-scrub.sh
echo "exit: $?"   # expect 2 (blocked)

echo '{"tool_input":{"file_path":"a.md","content":"hello"}}' \
  | bash hooks/pii-scrub.sh
echo "exit: $?"   # expect 0 (pass)
```

**Why this exists:** Research projects accumulate sensitive content (subject IDs, advisor names, internal URLs, dataset paths). The cost of accidentally pushing a 6-digit subject ID to a public repo is high — IRB violations, data-sharing breach, retracted papers. This hook is a system-level guard.

[Source: `hooks/pii-scrub.sh`](../hooks/pii-scrub.sh)

## `memory-load.sh` — auto-inject MEMORY.md on session start

**Event:** `SessionStart` (runs once when Claude Code opens a new session)

**Behavior:** Walks `.claude/agent-memory/*/MEMORY.md` files in the current project. Concatenates them (with `## <agent>` section headers) and prints to stdout. Claude Code injects the stdout into the new session's context.

**No-op safe:** If `.claude/agent-memory/` doesn't exist, the hook exits 0 and prints nothing — safe to ship enabled-by-default.

**Disable per-project:** `CLAUDE_RESEARCH_DISABLE_MEMORY_LOAD=1`.

**Test:**
```bash
# In a project with .claude/agent-memory/supervisor/MEMORY.md populated:
bash hooks/memory-load.sh
# → prints concatenated MEMORY.md content

# In a project without:
bash hooks/memory-load.sh
# → exits 0, prints nothing
```

**Why this exists:** Per-agent memory is OMCR's primary continuity mechanism. Without auto-load, each new session starts cold — the agents would need to be explicitly told to read their memory files. The hook makes loading transparent.

**Implementation note:** Written for bash 3.2 (macOS default) — uses `find ... | sort | while read` instead of `mapfile`.

[Source: `hooks/memory-load.sh`](../hooks/memory-load.sh)

## `citation-warn.sh` — heuristic warning for uncited manuscript paragraphs

**Event:** `PostToolUse:Write|Edit` (runs **after** every file Write or Edit)

**Behavior:** Checks if the modified file is manuscript markdown (`paper/`, `manuscript/`, `drafts/` directories, or filename matches `*draft*.md`). If yes, scans paragraphs for any citation form:
- Markdown link: `[text](https://...)`
- Author-year inline: `Smith 2024`, `Smith et al. 2024`, `(Smith, 2024)`

Paragraphs longer than 80 characters and lacking any citation form get flagged in a **stderr warning** (the hook never blocks — exit 0 always).

**Gate:** files outside the manuscript paths / naming convention are skipped silently. So editing `src/foo.md` or `notes/research.md` never triggers a warning.

**Disable per-project:** `CLAUDE_RESEARCH_DISABLE_CITATION_WARN=1`.

**Test:**
```bash
# Uncited paragraph in manuscript markdown → warning
echo '{"tool_input":{"file_path":"paper/draft.md","content":"This paragraph asserts a substantive scientific claim about the field without citing any source whatsoever, which the warner should flag."}}' \
  | bash hooks/citation-warn.sh

# Cited paragraph → no warning
echo '{"tool_input":{"file_path":"paper/draft.md","content":"This paragraph asserts a claim ([Smith 2024](https://example.com))."}}' \
  | bash hooks/citation-warn.sh

# Non-manuscript file → no warning regardless of content
echo '{"tool_input":{"file_path":"src/foo.md","content":"long paragraph in src/, ignored entirely by the warner."}}' \
  | bash hooks/citation-warn.sh
```

**Why this exists:** Catching uncited claims at write-time is much cheaper than catching them at submission. The hook is heuristic (false positives are possible — short claims, lists, code blocks are not flagged) but useful as a nudge.

[Source: `hooks/citation-warn.sh`](../hooks/citation-warn.sh)

## Hook registration

The plugin's `.claude-plugin/plugin.json` points to `hooks/hooks.json`, which registers the three scripts to their events:

```json
{
  "hooks": {
    "PreToolUse":   [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PLUGIN_ROOT\"/hooks/pii-scrub.sh", "timeout": 5}]}],
    "SessionStart": [{"matcher": "*",          "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PLUGIN_ROOT\"/hooks/memory-load.sh", "timeout": 5}]}],
    "PostToolUse":  [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PLUGIN_ROOT\"/hooks/citation-warn.sh", "timeout": 5}]}]
  }
}
```

The `$CLAUDE_PLUGIN_ROOT` variable resolves to the plugin's install directory at runtime.

## Adding your own hook

Drop a shell script into `hooks/`, then add a stanza to `hooks/hooks.json`:

```json
{
  "PreCommit": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PLUGIN_ROOT\"/hooks/your-hook.sh", "timeout": 5}]}]
}
```

Conventions:
- Each hook script honors a `CLAUDE_RESEARCH_DISABLE_<NAME>=1` env var (exit 0 immediately if set).
- Blocking hooks (PreToolUse) exit 2 to block; non-blocking hooks exit 0 always.
- Read tool-call payloads from stdin as JSON; use `python3 -c "import json, sys; ..."` for parsing.
- Keep hooks fast (< 5s) — they run on every event.

## See also

- [Configuration](Configuration.md) — env vars and `.claude/scrub-patterns.txt` format
- [`hooks/README.md`](../hooks/README.md) — quick-reference + smoke tests
- [`hooks/default-scrub-patterns.txt`](../hooks/default-scrub-patterns.txt) — shipped default PII patterns
