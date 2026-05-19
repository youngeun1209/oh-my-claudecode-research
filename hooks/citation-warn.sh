#!/usr/bin/env bash
# citation-warn.sh — PostToolUse:Write|Edit non-blocking warner.
#
# Reads a JSON tool-call payload from stdin. If the file written/edited lives
# under paper/, manuscript/, drafts/, or has a name matching *draft*.md, scans
# paragraphs for any citation-like form (`[text](url)` or `(Author YYYY)`).
# Emits a warning to stderr listing paragraph indices that lack any citation.
#
# Never blocks — exit 0 always. This is a heuristic nudge, not a hard gate.
#
# Disable per-project: set CLAUDE_RESEARCH_DISABLE_CITATION_WARN=1.

set -u

if [[ "${CLAUDE_RESEARCH_DISABLE_CITATION_WARN:-0}" == "1" ]]; then
  exit 0
fi

payload="$(cat)"

result="$(printf '%s' "$payload" | python3 -c '
import json, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = data.get("tool_input", {}) if isinstance(data, dict) else {}
file_path = (ti.get("file_path") or "").strip()
content = ti.get("content") or ti.get("new_string") or ""
if not file_path or not content:
    sys.exit(0)

# Gate: only warn for paper-like markdown files.
fp_lower = file_path.lower()
gate = (
    "/paper/" in fp_lower
    or "/manuscript/" in fp_lower
    or "/drafts/" in fp_lower
    or "draft" in fp_lower.rsplit("/", 1)[-1]
)
if not (gate and fp_lower.endswith(".md")):
    sys.exit(0)

# Split into paragraphs (blank-line delimited).
paragraphs = re.split(r"\n\s*\n", content)
# Citation patterns: markdown link with http URL, or "(Author 2024)" / "Author et al. 2024".
link_re = re.compile(r"\[[^\]]+\]\(https?://", re.IGNORECASE)
authoryear_re = re.compile(r"\b[A-Z][A-Za-zÀ-ɏ]+(?:\s+et\s+al\.)?,?\s+\d{4}\b")

uncited = []
for i, p in enumerate(paragraphs, 1):
    text = p.strip()
    # Skip code fences, blockquotes, tables, list-only, headings, and short stubs.
    if not text or text.startswith(("```", "#", ">", "|", "- ", "* ")):
        continue
    if len(text) < 80:
        continue
    if link_re.search(text) or authoryear_re.search(text):
        continue
    uncited.append(i)

if uncited:
    print(f"CITATION-WARN: {file_path}", file=sys.stderr)
    print(f"  paragraphs without citations: {uncited}", file=sys.stderr)
    print("  (heuristic — set CLAUDE_RESEARCH_DISABLE_CITATION_WARN=1 to silence)", file=sys.stderr)
' 2>&1)"

# Pass result through (warnings already on stderr from python). Always exit 0.
[[ -n "$result" ]] && printf '%s' "$result" >&2
exit 0
