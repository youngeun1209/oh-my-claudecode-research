---
bibkey: lastnameYYYY          # 1:1 with the record in bibliographic-management/<file>.md
relevance: [intro, R1, discussion]   # which manuscript sections / results use it
bucket: <your-bucket>         # a tag from your project's bucket vocabulary (see README)
status: to-read               # to-read | skimmed | read
---

# FirstAuthor et al. YEAR — how this project uses it

<!--
  <library root>/ = how THIS project cites and uses the paper.
  The paper's own summary + main figure live in the bib record:
    bibliographic-management/<this-file>.md   (the source of truth for what the paper IS).
  Keep this file focused on OUR usage — do not duplicate the summary.
  Only papers RELEVANT to this project get a file here.
  Scientific content in English (default; override language via project CLAUDE.md).
-->

| | |
|---|---|
| **Paper** | FirstAuthor et al. YEAR — short phrase |
| **Full summary** | [`bibliographic-management/<file>.md`](bibliographic-management/<file>.md) |
| **Bucket** | `<your-bucket>` |
| **Used in** | Intro §N · R1 · Discussion point N |
| **Position** | `support` / ⚠️ `contrast` |
| **Status** | to-read |

## Why it's relevant
> One sentence: what about this paper matters to our argument.

## How we cite & use it
- **We cite for:** which claim of ours this backs (or contrasts with).
- **Position:** `support` / ⚠️ `contrast` — one line on how we sit relative to it.
- **Cited in:** Intro §N · R3 framing · Discussion point N  (be exact).
- **What we borrow / extend:** the exact methodological step, figure, or phrasing we build on.

## Connections to our analyses
<!-- Links to our results, wiki pages, follow-up analyses this paper informs. -->
- …

## Links
<!-- [[wikilink]] are slug-based. Cross-link to the bib record and related papers. -->
[[literature-map]] · YYYY-otherauthor-keyword
