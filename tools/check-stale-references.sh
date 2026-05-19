#!/usr/bin/env bash
set -u

allowlist="tools/stale-reference-allowlist.txt"
mkdir -p tools
if [[ ! -f "$allowlist" ]]; then
  : > "$allowlist"
fi

pattern='oh-my-claudecode|claudecode|Claude Code|\.claude|CLAUDE\.md|\bOMCR\b|OpenClaw|\bClaw\b'
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
)

raw="$(mktemp)"
remaining="$(mktemp)"
patterns="$(mktemp)"
trap 'rm -f "$raw" "$remaining" "$patterns"' EXIT

rg -n -i "$pattern" "${roots[@]}" --glob '!wiki/migration/**' > "$raw"
rg_status=$?
if [[ $rg_status -gt 1 ]]; then
  cat "$raw" >&2
  exit "$rg_status"
fi

if [[ ! -s "$raw" ]]; then
  exit 0
fi

grep -v -E '^[[:space:]]*(#|$)' "$allowlist" > "$patterns"
if [[ ! -s "$patterns" ]]; then
  cat "$raw" > "$remaining"
else
  grep -v -E -f "$patterns" "$raw" > "$remaining"
fi
grep_status=$?
if [[ $grep_status -eq 1 ]]; then
  exit 0
fi
if [[ $grep_status -gt 1 ]]; then
  cat "$remaining" >&2
  exit "$grep_status"
fi

cat "$remaining"
exit 1
