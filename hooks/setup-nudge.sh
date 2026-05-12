#!/usr/bin/env bash
# setup-nudge.sh — SessionStart matcher.
#
# If the current project looks uninitialized (no CLAUDE.md, OR CLAUDE.md is
# missing the `## Project context` / `## Research stack` blocks that OMCR's
# agents and commands rely on), print a single non-blocking nudge suggesting
# `/omcr-setup`. Does NOT run setup itself — the actual interview lives in the
# slash command.
#
# No-op (exit 0, prints nothing) if:
#   - the project is already initialized, OR
#   - the directory looks like the OMCR plugin checkout itself (we have a
#     CLAUDE.md but no agents to set up for).
#
# Disable per-project: set CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1.

set -u

if [[ "${CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE:-0}" == "1" ]]; then
  exit 0
fi

# If we're inside the plugin's own checkout, don't nudge — the maintainer
# isn't setting up a research project here. Heuristic: presence of
# `.claude-plugin/plugin.json` at the cwd.
if [[ -f ".claude-plugin/plugin.json" ]]; then
  exit 0
fi

has_claude_md=0
has_project_context=0
has_research_stack=0

if [[ -f "CLAUDE.md" ]]; then
  has_claude_md=1
  if grep -qE "^##[[:space:]]+Project context" CLAUDE.md 2>/dev/null; then
    has_project_context=1
  fi
  if grep -qE "^##[[:space:]]+Research stack" CLAUDE.md 2>/dev/null; then
    has_research_stack=1
  fi
fi

# Fully initialized → no nudge.
if [[ "$has_claude_md" == 1 && "$has_project_context" == 1 && "$has_research_stack" == 1 ]]; then
  exit 0
fi

# Build the nudge message based on what's missing.
echo "# oh-my-claudecode-research — setup nudge"
echo ""
if [[ "$has_claude_md" == 0 ]]; then
  echo "This project has no \`CLAUDE.md\`. The 6 research agents and the slash commands depend on it for project context (hypothesis / venue / paths)."
elif [[ "$has_project_context" == 0 && "$has_research_stack" == 0 ]]; then
  echo "Your \`CLAUDE.md\` is missing both the \`## Project context\` and \`## Research stack\` blocks that OMCR's agents and commands read."
elif [[ "$has_project_context" == 0 ]]; then
  echo "Your \`CLAUDE.md\` is missing the \`## Project context\` block — \`@supervisor\` and the other agents need this for hypothesis / venue / narrative framing."
else
  echo "Your \`CLAUDE.md\` is missing the \`## Research stack\` block — \`/todofig\`, \`/sync\`, and the \`verify-citation\` / \`cropfig\` skills need this for paths and parameters."
fi
echo ""
echo "Run \`/omcr-setup\` to walk through an interactive interview that populates the missing blocks, scaffolds the per-agent memory directories, and (optionally) initializes \`references.bib\` + \`references.csv\` for \`@literature-curator\`."
echo ""
echo "To suppress this nudge: \`export CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1\`."

exit 0
