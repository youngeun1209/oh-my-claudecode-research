# Configuration

OMCR is configured via three layers, in order of precedence:

1. **Environment variables** — highest priority, useful for one-off overrides
2. **Project `CLAUDE.md` `## Research stack` block** — persistent project-level config
3. **Hardcoded defaults** in the command / skill / hook source

This page documents what each layer carries.

## Layer 2 — `## Research stack` block in CLAUDE.md

Add a `## Research stack` section to your project's `CLAUDE.md`. The slash commands (`/todofig`, `/sync`) and the `cropfig` skill read from it.

```markdown
## Research stack (used by /todofig, /sync, /cropfig)

- **Deck export dir:** figures/captured/
- **Tight-crop output dir:** figures/tight/
- **Outline file:** outline.md
- **Figure count:** 8
- **Result pattern:** `^### Result (\d+)`
- **Slide → figure offset:** 0
- **Report language:** English
- **Report output dir:** ./todofig_reports/
- **Sync report dir:** ./sync_reports/
- **Deck export script:** bash export.sh  (optional)
- **Embed target:** outline.docx  (optional — for /sync Phase 4)
```

### Field reference

| Field | Used by | Type | Default | Purpose |
|---|---|---|---|---|
| `Deck export dir` | `/todofig`, `/sync`, `cropfig` | path | `figures/captured/` | Captured figure PNGs (input). Your slide-export pipeline writes here. Read-only by OMCR. |
| `Tight-crop output dir` | `cropfig`, `/sync` Phase 4 | path | `figures/tight/` | Header-stripped figure-only PNGs. Owned by `cropfig`; rewritten each invocation. |
| `Outline file` | `/todofig`, `/sync` | path | (required) | Markdown outline describing intended figure contents. |
| `Figure count` | `/todofig`, `/sync` | integer | (required) | Total figures expected in the project. Used for the status table loop. |
| `Result pattern` | `/todofig`, `/sync` | regex | `^### Result (\d+)` | Pattern used to find result/figure blocks in the outline. Capture group → figure identifier. |
| `Slide → figure offset` | `/todofig`, `/sync` Phase 4 | integer | `0` | Slide-index minus figure-number. Set to `1` if slide 1 is a conceptual schematic and slide 2 = Fig 1. |
| `Report language` | `/todofig`, `/sync` | string | `English` | Output language for the human-readable report. Manuscript content always stays English. |
| `Report output dir` | `/todofig` | path | `./todofig_reports/` | Where `/todofig` saves its dated TODO report. |
| `Sync report dir` | `/sync` | path | `./sync_reports/` | Where `/sync` saves its dated status snapshot. |
| `Deck export script` | `/todofig`, `/sync`, `cropfig` | shell command | (optional) | Idempotent command to refresh the deck export. Skipped if not set. |
| `Embed target` | `/sync` Phase 4 | path | (optional) | Document (`.docx` / `.md`) into which cropped figures are embedded at each result heading. Phase 4 skipped if not set. |

### First-run wizard

On the first invocation of `/todofig` or `/sync` in a project without a `## Research stack` block:

1. The command notices the missing config.
2. It asks the user (via natural conversation) for the required fields.
3. It **offers to write** the block to `CLAUDE.md` automatically.
4. Subsequent invocations use the stored values.

You can skip the wizard by adding the block manually before first invocation.

## Layer 1 — Environment variables

Use environment variables to override layer 2 for a single invocation or to pass values to the `cropfig` skill before the project CLAUDE.md exists.

| Variable | Used by | Maps to layer 2 field |
|---|---|---|
| `FIGURES_SRC` | `cropfig` | `Deck export dir` |
| `FIGURES_DST` | `cropfig` | `Tight-crop output dir` |
| `EXPORT_SCRIPT` | `cropfig` | `Deck export script` |
| `CLAUDE_RESEARCH_DISABLE_PII_SCRUB` | `pii-scrub` hook | (n/a — disables) |
| `CLAUDE_RESEARCH_DISABLE_MEMORY_LOAD` | `memory-load` hook | (n/a — disables) |
| `CLAUDE_RESEARCH_DISABLE_CITATION_WARN` | `citation-warn` hook | (n/a — disables) |

Set environment variables in `.claude/settings.json` (per-project) or your shell profile (global).

Example `.claude/settings.json` snippet:

```json
{
  "env": {
    "FIGURES_SRC": "results/figures_v3/captured/",
    "FIGURES_DST": "results/figures_v3/tight/",
    "EXPORT_SCRIPT": "bash scripts/export_keynote.sh"
  }
}
```

## PII scrub patterns

The `pii-scrub` hook looks for patterns in this order:

1. **`.claude/scrub-patterns.txt`** in the current project (wins entirely if present).
2. **`hooks/default-scrub-patterns.txt`** shipped with OMCR (fallback defaults).

The project-level file is gitignored (covered by `.claude/`), so your actual sensitive patterns (advisor names, internal subject-ID formats) never get committed.

Format: one extended regex per line. Lines starting with `#` and blank lines ignored.

Example project override (`.claude/scrub-patterns.txt`):

```
# Standard contact info
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}

# This project's internal subject ID format (5-digit prefix HCP-#####)
\bHCP-[0-9]{5}\b

# Lab / advisor names you don't want leaking
(?i)\b(your-lab-name|advisor-name)\b
```

Test before committing:

```bash
echo '{"tool_input":{"file_path":"foo.md","content":"contact me at alice@example.com"}}' \
  | bash ~/.claude/plugins/oh-my-claudecode-research/hooks/pii-scrub.sh
echo "exit code: $?"   # expect 2 (blocked)
```

## CLAUDE.md project-context section

Beyond the `## Research stack` block, your project's `CLAUDE.md` should also have a `## Project context` (or similar) block that the 5 agents read for hypothesis / venue / narrative:

```markdown
## Project context

- **Working title:** [your project name]
- **Field:** [your field]
- **First author / PI:** [your name] / [PI name]
- **Target venue:** [target journal / conference]
- **Central hypothesis:** [one sentence]
- **Narrative spine:**
  1. *Gap:* [what the field has not established]
  2. *Question:* [the specific testable question]
  3. *Approach:* [methodology in one sentence]
  4. *Finding:* [filled as results emerge]
  5. *Implication:* [what this changes]

## Language preference (optional)

- **User-dialog language:** Korean  (default is English)
- **Manuscript language:** English  (default — do not change)
```

The 5 agents are coded to default to English. If you want user-facing reports in another language, set `User-dialog language` here and the agents will adapt.

## See also

- [Standalone Usage](Standalone-Usage.md) — using OMCR's commands with this config
- [Commands](Commands.md) — full reference for `/todofig`, `/sync`, `cropfig`
- [Hooks](Hooks.md) — full reference for the 3 hooks
