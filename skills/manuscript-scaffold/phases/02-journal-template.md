# Phase 2 — Journal template lookup

If `$TARGET_VENUE` is empty / not provided, skip this phase entirely. Record `journal_template = none` and continue to phase 3.

## Match the venue against the bundled registry

Read `$CLAUDE_PLUGIN_ROOT/templates/journal-registry.json`.

**Matching policy — strict:**
- **Case-insensitive exact** match against each entry's name OR any string in its `aliases` list.
- **No fuzzy matching.** A partial match is treated as a miss. A near-miss is treated as a miss.

## On match — confirm before applying

Show the user:

```
Target venue "<user input>" matched: <registry name>
  Publisher:               <publisher>
  LaTeX class:             <ctan_package>
  documentclass line:      <documentclass>
  Submission guidelines:   <submission_guidelines_url>
  Registry verified on:    <verified_on>  ← OMCR snapshot, may be stale; verify against the publisher guidelines above before submission.

Apply this class to main.tex and bibstyle to the \bibliographystyle line? (y/N)
```

Default on empty input is **no**. The user has to explicitly say yes.

### On confirmation (`y` / `yes`)

Record the rewrite plan for phase 3 to apply against the skeleton copy:

- Replace `\documentclass[11pt]{article}` → registry's `documentclass`.
- Replace `\bibliographystyle{plainnat}` → `\bibliographystyle{<bibstyle>}`.
- Append a "Journal template" section to the manuscript dir's `README.md` recording the registry name, ctan_package, documentclass, submission_guidelines_url, and verified_on date.

Print to the user (unless `ctan_package == "base"`):

```
TeX Live note — this class requires the '<ctan_package>' package.
If your TeX install does not have it, run:
  tlmgr install <ctan_package>
```

Record `journal_template = applied(<class>, <bibstyle>)` for phase 3 to consume.

### On user declines (or no match)

Print the registry's `not_in_registry_response` (the three-option fallback) and act on the user's choice:

- **(a) Keep generic article** — leave the skeleton as-is. Record `journal_template = not applied`. Continue.
- **(b) Specify a class name** — accept a single class name from the user (e.g. `IEEEtran`). Swap the `\documentclass` line in the skeleton copy only. **Do not fetch any `.cls` file.** The user is responsible for ensuring the class is installed locally. Record `journal_template = applied(<class>, <unchanged bibstyle>)`. Continue.
- **(c) Paste a publisher URL** — advanced flow with strict gates:
  1. Validate the URL starts with `https://`. Reject plain `http://`.
  2. WebFetch the archive.
  3. **Display the SHA256 of the downloaded bytes to the user. Stop and wait for explicit confirmation of the hash.** If the user does not confirm, abort this option and offer (a) or (b) instead.
  4. On confirmed hash, extract the archive into `<MANUSCRIPT_DIR>/` (never into the plugin repo).
  5. Swap the `\documentclass` line. Record the source URL + hash in the `README.md` "Journal template" section.

## Hard rules — applies regardless of branch above

- **Never** bundle a `.cls` file into the OMCR plugin repo. Anything fetched in (c) lands in the user's `MANUSCRIPT_DIR`.
- **Never** fetch anything without (i) explicit user-supplied `https://` URL AND (ii) shown SHA256 AND (iii) explicit user OK.
- **Never** fuzzy-match the venue. A close-but-not-exact match is a miss — fall through to the fallback prompt.
