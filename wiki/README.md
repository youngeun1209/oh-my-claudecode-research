# `wiki/` — local browsable documentation

This directory holds the OMCR wiki as plain markdown — browsable directly in the repo or via GitHub.

If you prefer the **GitHub Wiki UI** (the dedicated wiki tab on a GitHub repo): clone the wiki's separate git repo (`<repo>.wiki.git`) and copy these files into it.

```bash
# One-time setup of the GitHub Wiki (run from outside the main repo):
git clone https://github.com/youngeun1209/oh-my-claudecode-research.wiki.git
cd oh-my-claudecode-research.wiki

# Copy current wiki content from the main repo:
cp -r /path/to/oh-my-claudecode-research/wiki/*.md ./

# Commit + push:
git add . && git commit -m "Sync wiki from main repo" && git push origin master
```

GitHub Wiki uses Markdown but has [its own page-naming conventions](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages) — page names become filenames with `-` for spaces and `.md` extension, so the existing filenames (`Home.md`, `Getting-Started.md`, etc.) work directly.

## Entry point

Start at [`Home.md`](Home.md) for navigation.

## Pages

- `Home.md` — Landing + navigation
- `Getting-Started.md` — Install + first session
- `Standalone-Usage.md` — OMCR alone, full walkthrough
- `With-OMC.md` — OMCR + OMC companion install + workflows
- `Configuration.md` — `## Research stack` block + env vars
- `OMC-Tool-Reference.md` — 47 OMC MCP tools mapped to research workflow
- `Agents.md` — 6 agents reference
- `Commands.md` — `/todofig`, `/sync`, `cropfig`, `verify-citation`
- `Hooks.md` — 4 hooks
- `Specializing.md` — Author a field-specific preset
