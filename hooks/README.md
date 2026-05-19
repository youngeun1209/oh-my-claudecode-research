# `hooks/` — research-flavored Codex hooks

This directory ships four lightweight shell-script hook/check helpers (no Node, no MCP, no plugin runtime — just `bash` + `python3`). Codex plugin manifests expose skills, not runtime hooks, so `$omxr-setup` or base OMX setup must wire these as native hooks or explicit workflow checks where supported.

| Hook | Event | Behavior | Blocking? |
|---|---|---|---|
| [pii-scrub.sh](pii-scrub.sh) | `PreToolUse:Write\|Edit` | Greps staged content against a pattern list (default: emails / SSNs / 6-digit subject IDs). | **Blocks** (exit 2) on match. |
| [memory-load.sh](memory-load.sh) | `SessionStart` | Reads `.omx/omxr/agent-memory/<agent>/MEMORY.md` from the project root and emits to stdout for context injection. | Never blocks. |
| [setup-nudge.sh](setup-nudge.sh) | `SessionStart` | If `AGENTS.md` is missing `## Project context` or `## Research stack`, prints a one-line reminder to run `$omxr-setup`. | Never blocks. |
| [citation-warn.sh](citation-warn.sh) | `PostToolUse:Write\|Edit` | When the edited file looks like manuscript markdown (`paper/`, `manuscript/`, `drafts/`, or `*draft*.md`), warns about paragraphs missing any citation form. | Never blocks (heuristic only). |

## How they hang together

A typical research session uses all four:

1. **Session starts** → `memory-load.sh` injects each agent's `MEMORY.md` into the context, so `@supervisor`, `@analysis-implementer`, etc. all begin with their persistent state from prior conversations. In parallel, `setup-nudge.sh` checks whether `AGENTS.md` is initialized; if not, it prints a one-line `$omxr-setup` reminder. Once the project is initialized, this hook goes silent automatically.
2. **You ask the agent to write something** → `pii-scrub.sh` checks the staged content for sensitive patterns *before* the file is touched. Block on match, with a stderr message naming the matched pattern(s).
3. **The write succeeds** → if it looks like manuscript markdown, `citation-warn.sh` flags paragraphs without `[text](url)` or `(Author YYYY)` citations. Just a nudge — does not block.

## Configuring the PII pattern list

`pii-scrub.sh` looks for patterns in this order:

1. **`.omx/omxr/scrub-patterns.txt`** in the *current project* (wins entirely if present).
2. **`hooks/default-scrub-patterns.txt`** shipped with this plugin (fallback).

Override format: one extended regex (POSIX ERE) per line. Lines starting with `#` and blank lines are ignored.

Example project override:

```
# .omx/omxr/scrub-patterns.txt
# (project-specific PII; wins entirely over hooks/default-scrub-patterns.txt)

# Standard contact info
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}

# This project's internal subject ID format (5-digit prefix HCP-####)
\bHCP-[0-9]{5}\b

# Lab / advisor names you don't want leaking into public commits
(?i)\b(your-lab-name|advisor-name)\b
```

Test before committing:

```bash
echo '{"tool_input":{"file_path":"foo.md","content":"contact me at me@example.com"}}' | bash hooks/pii-scrub.sh
echo "exit code: $?"   # expect 2 (blocked)
```

## Disabling per-project

Each hook honors a `CODEX_RESEARCH_DISABLE_<NAME>=1` env var:

| Env var | Disables |
|---|---|
| `CODEX_RESEARCH_DISABLE_PII_SCRUB=1` | `pii-scrub.sh` (Write/Edit always pass) |
| `CODEX_RESEARCH_DISABLE_MEMORY_LOAD=1` | `memory-load.sh` (no MEMORY.md injection) |
| `CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1` | `setup-nudge.sh` (no `$omxr-setup` reminder on uninitialized projects) |
| `CODEX_RESEARCH_DISABLE_CITATION_WARN=1` | `citation-warn.sh` (no manuscript warnings) |

Set in the Codex hook environment, project shell environment, or explicit workflow-check environment. The helper exits 0 immediately when the corresponding var is `1`.

## When to extend

- **Add another `PreToolUse` blocker** (e.g., reproducibility-checklist gate before committing): write a sibling shell script and add an entry to `hooks/hooks.json`. Keep the same exit-code contract — exit 2 to block, exit 0 to pass.
- **Add a `Stop` or `SessionEnd` summary** (e.g., dump session-flagged drifts to a log): same pattern. Beware long-running scripts — the timeout in `hooks.json` is enforced.
- **Replace `memory-load.sh` with something smarter** (e.g., a `python` script that filters MEMORY.md by token budget): drop in your own and update `hooks.json`. The shipped version is intentionally minimal.

## When NOT to extend in this plugin

- A keyword auto-trigger `UserPromptSubmit` hook (mirroring OMX's `keyword-detector.mjs`). Risk of false positives in research prose is real; leave to future work or per-project hooks.
- A full `.codex/hooks.json.example`. Per-project drift and base OMX shared ownership make a static template low-value; `$omxr-setup` reports the effective hook/check state instead.

## Smoke-test a fresh checkout

```bash
# pii-scrub blocks
echo '{"tool_input":{"file_path":"a.md","content":"alice@example.com"}}' | bash hooks/pii-scrub.sh; echo "exit=$?"

# pii-scrub passes
echo '{"tool_input":{"file_path":"a.md","content":"hello world"}}' | bash hooks/pii-scrub.sh; echo "exit=$?"

# memory-load no-ops cleanly when no .omx/omxr/agent-memory exists
bash hooks/memory-load.sh; echo "exit=$?"

# setup-nudge prints reminder for an uninitialized project
(cd $(mktemp -d) && bash $OLDPWD/hooks/setup-nudge.sh); echo "exit=$?"

# setup-nudge stays silent for a fully-initialized project
tmp=$(mktemp -d); printf '## Project context\nhi\n\n## Research stack\nbye\n' > $tmp/AGENTS.md
(cd $tmp && bash $OLDPWD/hooks/setup-nudge.sh); echo "exit=$?"   # expect empty output, exit 0

# citation-warn ignores non-manuscript files
echo '{"tool_input":{"file_path":"src/foo.md","content":"a paragraph long enough to trigger the heuristic but in src/, so this should pass silently."}}' | bash hooks/citation-warn.sh; echo "exit=$?"
```
