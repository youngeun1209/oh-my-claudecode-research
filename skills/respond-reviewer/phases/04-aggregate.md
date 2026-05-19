---
name: respond-reviewer-phase-04-aggregate
description: Assemble the rebuttal letter, one section per `comment_id`, in the format requested by `--format` (default LaTeX). Honor `--draft-only` (manuscript files are untouched; the letter is the only artifact). Output is a single in-memory letter string ready for phase 05 evaluation and phase 06 disk-write.
---

# Phase 4 — Aggregate

Assemble the per-comment responses into one rebuttal letter. The shape is the same regardless of `--format` — what changes is the rendering (LaTeX command structure vs. markdown headings).

This phase is pure synthesis — no dispatch, no state writes. It builds an in-memory string that phase 05 reads (for the supervisor re-evaluation) and phase 06 writes to disk.

## Inputs (from phase 03)

| Name | Source | Purpose |
|---|---|---|
| `run_id` | phase 01 | Recorded in the letter header for cross-reference with `rebuttals.json`. |
| `review_letter_path` | phase 01 | Quoted in the letter preamble so the reviewer can match the response to the original. |
| `output_format` | phase 01 | `latex | md`. Default `latex` per Phase 2 decision §2. |
| `manuscript_root` | phase 01 | Mentioned in the preamble for the user's own reference. |
| `draft_only` | phase 01 | Surfaced in the letter preamble as a disclosure ("this is a draft-only response — no manuscript edits were applied"). |
| `comments` | phase 02 | The enriched comments list (with labels, target_section, etc.). |
| `responses` | phase 03 | Per-comment response dicts. Aligned by `comment_id` with `comments` entries that have non-null `agent`. |
| `user_attention` | phase 03 | List of `structural` comments — surfaced as a deferred section in the letter. |
| `paper_state` | phase 01 | For the manuscript title / venue in the letter preamble (optional). |

## Step 1 — Decide the output filename

The letter is written to disk in phase 06; this phase only records the planned filename for the preamble:

```
letter_filename = "rebuttal-letter." + ("tex" if output_format == "latex" else "md")
```

The letter is written into the manuscript root (`<manuscript_root>/rebuttal-letter.tex`). If `manuscript_root` is not a writable directory, phase 06 falls back to `./rebuttal-letter.<ext>`; for this phase, the planned absolute path is just `<manuscript_root>/<letter_filename>` regardless.

## Step 2 — Assemble the response map

Build a dict `response_by_id` mapping `comment_id → response_dict` from `responses`. This lets the renderer walk `comments` in order and look up the matching response.

For comments whose `agent` was null (`structural`), there is no entry in `response_by_id` — the renderer handles them in the user-attention section, not the per-comment section.

## Step 3 — Render the letter (LaTeX branch)

If `output_format == "latex"`:

Build the letter as a standalone `.tex` file. It must compile on its own without depending on the manuscript's `main.tex`. Use the default `article` class — the user can rewrite the documentclass to match the journal's rebuttal template if needed (the same flexibility the `manuscript-scaffold` skill provides for the manuscript itself).

```latex
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{parskip}
\usepackage{hyperref}

\title{Response to Reviewers}
\author{}
\date{\today}

\begin{document}
\maketitle

\section*{Preamble}

We thank the reviewers for their careful reading and constructive feedback. Below
we respond to each comment in turn. The reviewer's comment is quoted in italics;
our response follows.

\textit{This response was assembled by \texttt{$respond-reviewer} (OMXR run id:
\texttt{<run_id>}) from the letter at \texttt{<review_letter_path>}.}

<if draft_only is true:>
\textit{Note: this run was invoked with \texttt{--draft-only}; no manuscript files
were edited. Cited line numbers and proposed changes are quoted in each response;
the user will apply them manually before submission.}

% --- per-comment responses ---

<for each comment in `comments` whose label != "structural", in order:>

\subsection*{<comment.reviewer>, Comment <comment.comment_id>}

\textit{<comment.text, escaped for LaTeX>}

\medskip

<response_by_id[comment.comment_id].response, with any markdown converted to LaTeX equivalents>

<if response_by_id[comment.comment_id].actions_taken is non-empty:>
\paragraph{Actions taken.}
\begin{itemize}
<for each action in actions_taken:>
  \item <action, escaped for LaTeX>
\end{itemize>

<if response_by_id[comment.comment_id].next_steps is non-empty:>
\paragraph{Suggested follow-up.}
\begin{itemize}
<for each step in next_steps:>
  \item \texttt{<step, escaped for LaTeX>} \emph{(user action — engines do not auto-invoke other engines)}
\end{itemize>

% --- user-attention section ---

<if user_attention is non-empty:>

\section*{Comments requiring human decision}

The following comments were classified as \textbf{structural} by the supervisor —
they require a framing or scope decision and have not been auto-answered. Please
address each before submission.

<for each comment in user_attention, in order:>

\subsection*{<comment.reviewer>, Comment <comment.comment_id> (structural)}

\textit{<comment.text, escaped for LaTeX>}

\medskip

\emph{Classification reason:} <comment.reason, escaped for LaTeX>

\medskip

\emph{Target section (best guess):} \texttt{<comment.target_section or "(unspecified)">}

\end{document}
```

LaTeX escaping rules to apply to user-supplied strings (comment text, response prose, actions):

- `&` → `\&`
- `%` → `\%`
- `$` → `\$` (unless the string is already known math — detect by `$.../` pairs).
- `#` → `\#`
- `_` → `\_` (unless inside `\texttt{...}` or a citation key — detect by surrounding context).
- `{` and `}` → `\{` and `\}` (only when not part of a LaTeX command in the response — the agents may have emitted LaTeX directly).
- `~` → `\textasciitilde{}`
- `^` → `\textasciicircum{}`
- `\` → `\textbackslash{}` (only when not part of an emitted LaTeX command).

Pragmatic rule: if the input string already contains `\section{`, `\textit{`, `\citep{`, or other top-level LaTeX commands, the agent likely emitted ready-to-compile LaTeX — leave it alone. Apply escapes only when the string is plain prose with stray special characters. The renderer should err on the side of preserving agent output; the user can fix compile errors in 30 seconds, but lost content is permanent.

## Step 4 — Render the letter (markdown branch)

If `output_format == "md"`:

Markdown letters have looser conventions. Use this shape:

```markdown
# Response to Reviewers

We thank the reviewers for their careful reading and constructive feedback. Below
we respond to each comment in turn. The reviewer's comment is quoted; our
response follows.

*This response was assembled by `$respond-reviewer` (OMXR run id: `<run_id>`) from
the letter at `<review_letter_path>`.*

<if draft_only is true:>
*Note: this run was invoked with `--draft-only`; no manuscript files were edited.
Cited line numbers and proposed changes are quoted in each response; the user will
apply them manually before submission.*

---

<for each comment in `comments` whose label != "structural", in order:>

## <comment.reviewer>, Comment <comment.comment_id>

> <comment.text, with each line prefixed by "> ">

<response_by_id[comment.comment_id].response>

<if response_by_id[comment.comment_id].actions_taken is non-empty:>
**Actions taken:**

<for each action in actions_taken:>
- <action>

<if response_by_id[comment.comment_id].next_steps is non-empty:>
**Suggested follow-up:**

<for each step in next_steps:>
- `<step>` *(user action — engines do not auto-invoke other engines)*

---

<if user_attention is non-empty:>

# Comments requiring human decision

The following comments were classified as **structural** by the supervisor — they
require a framing or scope decision and have not been auto-answered. Please
address each before submission.

<for each comment in user_attention, in order:>

## <comment.reviewer>, Comment <comment.comment_id> (structural)

> <comment.text, blockquoted>

*Classification reason:* <comment.reason>

*Target section (best guess):* `<comment.target_section or "(unspecified)">`
```

Markdown needs no escaping for special LaTeX characters; preserve agent output as-is. Backtick-escape any raw filenames or commands that appear in prose.

## Step 5 — Sanity-check the assembled letter

After rendering, verify:

- The letter is non-empty (at least 200 characters of content excluding the preamble).
- Every comment in `comments` is referenced at least once (either in the per-comment section if non-structural, or in user-attention if structural).
- The user-attention section appears if and only if `len(user_attention) > 0`.

If any check fails, log a warning but **do not abort** — phase 05 (supervisor re-read) will catch substantive problems, and phase 06 still writes the artifact so the user has something to inspect.

## Step 6 — `--draft-only` enforcement note

This phase honors `--draft-only` only by surfacing the disclosure in the preamble. The engine cannot retroactively un-edit files that a phase-03 agent already touched. If the user invoked with `--draft-only` and the side-effect tally from phase 03 (`files_touched_all`) is non-empty, log a warning:

```
respond-reviewer phase 04 — WARNING: --draft-only was set but phase 03 reports
N file(s) touched by dispatched agents. The engine cannot enforce read-only
mode against agents that ignored the brief instruction. Files touched:
  <list>
Review these manually and revert if unintended.
```

The warning is informational. The rebuttal letter still assembles. Phase 06 records the same warning in the user-facing summary.

## Step 7 — Hand off to phase 05

Pass forward (everything from phase 03 plus):
- `letter_content` (the rendered string, in-memory only).
- `letter_filename` (`rebuttal-letter.tex` or `rebuttal-letter.md`).
- `letter_target_path` (`<manuscript_root>/<letter_filename>`).
- Render warnings (the sanity-check failures and the `--draft-only` mismatch, if any).

## Failure modes

| Condition | Behavior |
|---|---|
| Empty `comments` list (shouldn't happen — phase 01 aborts on zero comments) | Render a minimal letter with just the preamble + a note. Phase 06 still writes. |
| All comments are `structural` | Letter contains only preamble + user-attention section. Acceptable — phase 06 will mark run `HALT`. |
| LaTeX escape ambiguity | Prefer preserving the agent's emitted text. Compile errors are user-fixable; lost responses are not. |
| `--draft-only` violated by an agent | Log warning; render the letter unchanged. Phase 06 surfaces the warning in the user summary. |
| `response_by_id` missing an expected key | Render a placeholder paragraph: "[Response missing — dispatch may have failed; check `rebuttals.json` for the parse_error or dispatch_error fields.]" Continue. |

## What this phase does NOT do

- Does **not** invoke any subagent. Pure rendering.
- Does **not** write to disk. Phase 06 owns the letter write.
- Does **not** evaluate response quality. Phase 05 does that.
- Does **not** modify `responses` or `user_attention` lists. The renderer reads them; nothing else.
- Does **not** decide the per-comment verdict (`addressed | deferred | disputed`). Phase 05 does that based on the assembled letter the supervisor re-reads.
- Does **not** strip `actions_taken` even if `--draft-only` was set — the actions taken are recorded as the agents reported them, and the warning is what flags the inconsistency.
- Does **not** call the orchestrate primitives. This phase composes nothing — it is the synthesis bridge between phase 03's outputs and phase 05's supervisor re-read.
