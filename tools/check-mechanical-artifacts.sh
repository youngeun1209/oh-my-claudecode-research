#!/usr/bin/env bash
set -u

pattern='skills\$|commands\$|\.\.\$|engine slash command|used by .*/cropfig|before /start-research|before -research|slash commands|slash command'
roots=(
  README.md
  README.ko.md
  .codex-plugin
  AGENTS.md
  skills
  agents
  hooks
  templates
  develop/example-state
  wiki
  commands
)

raw="$(mktemp)"
trap 'rm -f "$raw"' EXIT

rg -n -i "$pattern" "${roots[@]}" --glob '!wiki/migration/**' > "$raw"
status=$?
if [[ $status -eq 1 ]]; then
  exit 0
fi
if [[ $status -gt 1 ]]; then
  cat "$raw" >&2
  exit "$status"
fi

cat "$raw"
exit 1
