#!/usr/bin/env bash
# setup-nudge.sh — SessionStart matcher.
#
# If the current project looks uninitialized (no AGENTS.md, OR AGENTS.md is
# missing the `## Project context` / `## Research stack` blocks that OMXR's
# agents and commands rely on), print a single non-blocking nudge suggesting
# `$omxr-setup`. Does NOT run setup itself — the actual interview lives in the
# skill.
#
# No-op (exit 0, prints nothing) if:
#   - the project is already initialized, OR
#   - the directory looks like the OMXR plugin checkout itself (we have a
#     AGENTS.md but no agents to set up for).
#
# Disable per-project: set CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1.

set -u

if [[ "${CODEX_RESEARCH_DISABLE_SETUP_NUDGE:-0}" == "1" ]]; then
  exit 0
fi

# If we're inside the plugin's own checkout, don't nudge — the maintainer
# isn't setting up a research project here. Heuristic: presence of
# `.codex-plugin/plugin.json` at the cwd.
if [[ -f ".codex-plugin/plugin.json" ]]; then
  exit 0
fi

has_codex_md=0
has_project_context=0
has_research_stack=0

if [[ -f "AGENTS.md" ]]; then
  has_codex_md=1
  if grep -qE "^##[[:space:]]+Project context" AGENTS.md 2>/dev/null; then
    has_project_context=1
  fi
  if grep -qE "^##[[:space:]]+Research stack" AGENTS.md 2>/dev/null; then
    has_research_stack=1
  fi
fi

# Fully initialized → no nudge.
if [[ "$has_codex_md" == 1 && "$has_project_context" == 1 && "$has_research_stack" == 1 ]]; then
  exit 0
fi

# Build the nudge message based on what's missing.
echo "# oh-my-codex-research — setup nudge"
echo ""
if [[ "$has_codex_md" == 0 ]]; then
  echo "This project has no \`AGENTS.md\`. The 6 research agents and the skills depend on it for project context (hypothesis / venue / paths)."
elif [[ "$has_project_context" == 0 && "$has_research_stack" == 0 ]]; then
  echo "Your \`AGENTS.md\` is missing both the \`## Project context\` and \`## Research stack\` blocks that OMXR's agents and commands read."
elif [[ "$has_project_context" == 0 ]]; then
  echo "Your \`AGENTS.md\` is missing the \`## Project context\` block — \`@supervisor\` and the other agents need this for hypothesis / venue / narrative framing."
else
  echo "Your \`AGENTS.md\` is missing the \`## Research stack\` block — \`$todofig\`, \`$sync\`, and the \`verify-citation\` / \`cropfig\` skills need this for paths and parameters."
fi
echo ""
echo "Run \`\$omxr-setup\` to scaffold the missing blocks, per-agent memory directories, and optional \`references.bib\` + \`references.csv\` files for \`literature-curator\`."
echo ""
echo "To suppress this nudge: \`export CODEX_RESEARCH_DISABLE_SETUP_NUDGE=1\`."

exit 0
