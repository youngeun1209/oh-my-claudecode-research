#!/usr/bin/env bash
# memory-load.sh — SessionStart matcher.
#
# Walks .omx/omxr/agent-memory/*/MEMORY.md (relative to the current project
# root, i.e. the cwd when the session starts) and prints the concatenated
# content to stdout, with one section per agent. Codex injects this
# stdout into the new session's context.
#
# No-op (exit 0, prints nothing) if the directory doesn't exist — safe to
# ship enabled-by-default.
#
# Disable per-project: set CODEX_RESEARCH_DISABLE_MEMORY_LOAD=1.

set -u

if [[ "${CODEX_RESEARCH_DISABLE_MEMORY_LOAD:-0}" == "1" ]]; then
  exit 0
fi

memory_root=".omx/omxr/agent-memory"

if [[ ! -d "$memory_root" ]]; then
  exit 0
fi

# Collect MEMORY.md files in stable sorted order. (bash 3.2 compatible — no mapfile.)
memory_files_list="$(find "$memory_root" -mindepth 2 -maxdepth 2 -name MEMORY.md -type f 2>/dev/null | sort)"

if [[ -z "$memory_files_list" ]]; then
  exit 0
fi

echo "# Agent Memory (auto-loaded by oh-my-codex-research)"
echo ""
echo "The following per-agent MEMORY.md files were read from \`$memory_root/\` at session start. Each agent's section reflects its persistent state from prior conversations."
echo ""

while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  # Extract agent name from path: .omx/omxr/agent-memory/<agent>/MEMORY.md
  agent="$(basename "$(dirname "$f")")"
  echo "---"
  echo ""
  echo "## ${agent}"
  echo ""
  cat "$f"
  echo ""
done <<< "$memory_files_list"

exit 0
