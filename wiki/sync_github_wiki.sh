#!/usr/bin/env bash
# Sync a folder-structured wiki tree into a GitHub Wiki repo (<repo>.wiki.git).
#
# GitHub Wiki is a flat namespace, so this FLATTENS <src>/**/*.md into single pages
# (basenames must be globally unique, so flattening is safe and [[slug]] links keep
# working). Folder structure is preserved only for Obsidian / the main repo.
#
# Usage:
#   sync_github_wiki.sh <src-wiki-dir> <wiki-git-url>
#     e.g. sync_github_wiki.sh docs/wiki https://github.com/<owner>/<repo>.wiki.git
#
#   Both args may also be supplied via env: WIKI_SRC, WIKI_URL.
#
# ONE-TIME prerequisite (web UI, cannot be scripted):
#   1. Repo Settings -> Features -> enable "Wikis".
#   2. Open the Wiki tab -> "Create the first page" -> save anything.
#      (The .wiki.git repo cannot be cloned until you do this.)
#
# Mapping:
#   <src>/home.md          -> Home.md  (GitHub Wiki landing page; Home.md also accepted)
#   <src>/<...>/<slug>.md  -> <slug>.md (flattened)
#   YAML frontmatter is stripped; a folder-grouped _Sidebar.md is generated.
#   [[slug]] cross-links render natively in GitHub Wiki.
#
# Note: GitHub Wiki has no graph view — for the link graph open <src> in Obsidian.

set -euo pipefail

SRC="${1:-${WIKI_SRC:-}}"
WIKI_URL="${2:-${WIKI_URL:-}}"

[ -n "$SRC" ] || { echo "usage: sync_github_wiki.sh <src-wiki-dir> <wiki-git-url>"; exit 1; }
[ -n "$WIKI_URL" ] || { echo "ERROR: wiki git URL missing (arg 2 or \$WIKI_URL)"; exit 1; }
[ -d "$SRC" ] || { echo "ERROR: source dir not found: $SRC"; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "Cloning wiki repo..."
if ! git clone "$WIKI_URL" "$WORK" 2>/dev/null; then
  echo "ERROR: could not clone $WIKI_URL"
  echo "       Enable Wikis AND create the first page in the Wiki tab first."
  exit 1
fi

# Remove previously-synced pages (keep .git); regenerate fresh.
find "$WORK" -maxdepth 1 -name '*.md' -delete

SIDEBAR="$WORK/_Sidebar.md"
printf '## Project Wiki\n\n- [[Home]]\n' > "$SIDEBAR"

prevdir=""
while IFS= read -r f; do
  rel="${f#"$SRC"/}"
  dir="$(dirname "$rel")"
  base="$(basename "$f")"
  # Landing page: accept home.md or Home.md.
  if [ "$base" = "home.md" ] || [ "$base" = "Home.md" ]; then out="Home.md"; else out="$base"; fi
  # strip a leading YAML frontmatter block ( --- ... --- )
  awk 'BEGIN{fm=0}
       NR==1 && $0=="---" {fm=1; next}
       fm==1 && $0=="---" {fm=0; next}
       fm==0 {print}' "$f" > "$WORK/$out"
  if [ "$out" != "Home.md" ]; then
    if [ "$dir" != "$prevdir" ]; then
      printf '\n**%s**\n' "$dir" >> "$SIDEBAR"
      prevdir="$dir"
    fi
    printf -- '- [[%s]]\n' "${out%.md}" >> "$SIDEBAR"
  fi
done < <(find "$SRC" -name '*.md' | sort)

cd "$WORK"
git add -A
if git diff --cached --quiet; then
  echo "Nothing changed; wiki already up to date."
  exit 0
fi
git commit -m "wiki: sync from folder structure" >/dev/null
echo "Pushing..."
git push origin HEAD
echo "Done."
