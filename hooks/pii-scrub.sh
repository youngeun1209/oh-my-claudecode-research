#!/usr/bin/env bash
# pii-scrub.sh — PreToolUse:Write|Edit blocker.
#
# Reads a JSON tool-call payload from stdin (Codex hook format) and
# blocks the call with exit 2 if the staged file content matches any pattern
# in the project's scrub-pattern list. Pass-through (exit 0) otherwise.
#
# Pattern lookup order:
#   1. .omx/omxr/scrub-patterns.txt        (project-local override; wins)
#   2. $CODEX_PLUGIN_ROOT/hooks/default-scrub-patterns.txt  (shipped defaults)
#
# Disable per-project: set CODEX_RESEARCH_DISABLE_PII_SCRUB=1 in the
# Codex hook environment, project shell environment, or explicit check runner.
#
# Pattern file format: one extended-regex per line; lines starting with '#'
# and blank lines are ignored.

set -u

if [[ "${CODEX_RESEARCH_DISABLE_PII_SCRUB:-0}" == "1" ]]; then
  exit 0
fi

# Locate pattern file (project override → shipped default).
project_patterns=".omx/omxr/scrub-patterns.txt"
plugin_root="${CODEX_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
default_patterns="$plugin_root/hooks/default-scrub-patterns.txt"

if [[ -r "$project_patterns" ]]; then
  patterns_file="$project_patterns"
elif [[ -r "$default_patterns" ]]; then
  patterns_file="$default_patterns"
else
  # No patterns file anywhere — nothing to check.
  exit 0
fi

# Read stdin payload.
payload="$(cat)"

# Extract content + file_path. Use python for robust JSON parsing.
extracted="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = data.get("tool_input", {}) if isinstance(data, dict) else {}
file_path = ti.get("file_path", "") or ""
# Edit tool uses new_string; Write uses content.
content = ti.get("content") or ti.get("new_string") or ""
print(file_path)
print("---PII-SCRUB-DELIM---")
print(content)
' 2>/dev/null)"

if [[ -z "$extracted" ]]; then
  exit 0
fi

file_path="$(printf '%s' "$extracted" | sed -n '1p')"
content="$(printf '%s' "$extracted" | awk '/^---PII-SCRUB-DELIM---$/{flag=1; next} flag')"

if [[ -z "$content" ]]; then
  exit 0
fi

# Walk patterns and report every match.
hits=()
while IFS= read -r pattern; do
  # Skip blanks and comments.
  [[ -z "$pattern" || "$pattern" =~ ^[[:space:]]*# ]] && continue
  if printf '%s' "$content" | grep -E -q -- "$pattern"; then
    hits+=("$pattern")
  fi
done < "$patterns_file"

if (( ${#hits[@]} > 0 )); then
  echo "PII-SCRUB: blocking write to $file_path — staged content matches the following pattern(s):" >&2
  for p in "${hits[@]}"; do
    echo "  - $p" >&2
  done
  echo "" >&2
  echo "If this is a false positive, edit your project's .omx/omxr/scrub-patterns.txt to refine the patterns, or set CODEX_RESEARCH_DISABLE_PII_SCRUB=1 to bypass entirely." >&2
  echo "Patterns loaded from: $patterns_file" >&2
  exit 2
fi

exit 0
