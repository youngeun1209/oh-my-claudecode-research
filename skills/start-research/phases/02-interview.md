# Phase 2 — Interview

Ask the user **only for fields that are missing or still `[TBD]`** (consult the state recorded by phase 1).

**Tone (important):** Treat this as a friendly conversation, not a form. Phrase each question as a gentle guiding prompt — short, low-pressure, one at a time. Wait for the answer, acknowledge briefly ("ok, got it"), then move on. Ask in the user's dialog language (default English; if Korean, use 존댓말 but stay conversational, not stiff).

There are two sections with different policies: infrastructure (batch confirm) and scientific identity (one-at-a-time conversation).

## A. Infrastructure fields — batch confirm

Show the defaults table below once, then ask a single batch question along the lines of:

> "These are the defaults — want to go with them, or change any?"
> ("이 기본값으로 가도 될까요? 바꾸고 싶은 항목 있으면 알려주세요.")

Accept silence / "looks good" / "이대로 가요" as full acceptance. Only revisit the specific fields the user names. No per-field loop.

| Field | Default | Goes into |
|---|---|---|
| `Deck file` | (ask user — `.key` or `.pptx` path; no default) | `## Research stack` |
| `Outline file` | `outline.md` | `## Research stack` |
| `Figure count` | `8` | `## Research stack` |
| `Result pattern` | `^### Result (\d+)` | `## Research stack` |
| `Report language` | `English` | `## Research stack` |
| `Report output dir` | `./todofig_reports/` | `## Research stack` |
| `Sync report dir` | `./sync_reports/` | `## Research stack` |
| `Figure PDF dir` | `<dirname(Deck file)>/pdf/` | `## Research stack` (optional override) |
| `Figure PNG dir` | `<dirname(Deck file)>/png/` | `## Research stack` (optional override) |
| `Manuscript dir` | `paper/` | `## Research stack` |
| `BibTeX file` | `<Manuscript dir>/references.bib` (i.e. `paper/references.bib`) | `## Research stack` |
| `Summary file` | `references.csv` (project root — kept OUT of the manuscript dir so it doesn't get pushed to Overleaf) | `## Research stack` |
| `CrossRef email` | (none) | `## Research stack` (optional — recommend the user provide it for verify-citation polite-pool access) |
| `Overleaf git URL` | (none) | `## Research stack` (optional — only if user has Overleaf with Git Integration enabled, which requires a paid plan) |
| `Data root` | `./data/` | `## Research stack` (used by `/figure-bake` to resolve figure data paths) |
| `User-dialog language` | `English` | `## Language preference` (optional) |
| `Manuscript language` | `English` (do not let the user change this — keep manuscripts in English for venue compatibility) | `## Language preference` |

> **Tip:** ask the `User-dialog language` field first if it's still `[TBD]`, so the rest of the interview can run in the user's preferred language right away.

For the one field with no default (`Deck file`), ask it as a single follow-up after the batch step — *"What's the path to your deck file (`.key` / `.pptx`)?"*

## B. Scientific identity — conversational, one question at a time

Never invent content. Ask each question as a gentle guiding prompt. If the user skips, push back **exactly once** with the rationale in the table at the bottom of this section, then accept `[TBD: <one-line note>]` if they still want to skip.

### Step 1 — Open with one big question

Start with a single open-ended guiding question. Example phrasings:

> "What kind of research are you hoping to do? Just describe it in a paragraph or two — big picture or specific, whatever's easiest."
>
> ("어떤 연구를 하고 싶으신가요? 한두 단락으로 자유롭게 적어주세요. 큰 그림이든 구체적인 질문이든 편하게요.")

From the user's free-form answer, extract **candidate values** for:
- Working title (a rough draft you propose)
- Field / sub-field
- Research topic (paraphrase of the big-picture question)
- Central hypothesis (if any specific testable claim was implied)
- Datasets (if mentioned)

### Step 2 — Walk through your proposals, one at a time

For each field where Step 1 gave you a candidate, present it back as a soft check — not a form field. Example phrasings:

- **Working title:** *"How does `<draft title>` sound as a working title? Any keywords you'd want to swap in?"*
- **Field:** *"Would you call this `<field>`, or is there a narrower sub-field that fits better?"*
- **Research topic:** *"So the big-picture question is roughly `<paraphrase>` — does that capture it?"*
- **Central hypothesis:** *"If I had to compress the hypothesis to one sentence: `<draft>` — close?"*
- **Datasets:** *"You mentioned `<dataset>` — can you tell me the source, modality, rough size, and whether you already have access?"*

If a field had **no candidate** from Step 1, just ask plainly with a guiding tone — one at a time:

- *"What field / sub-field is this in?"*
- *"What's the one-sentence hypothesis you want to test?"*
- *"Which dataset(s) are you planning to use?"*

### Step 3 — Remaining fields (these rarely show up in the opening answer)

Ask each one as a single guiding question, waiting for the answer before moving on:

- **Target venue:** *"Where are you aiming to submit? A journal or conference — even just a top pick is fine."*
- **Backup venues:** *"If your top pick doesn't land, where would you try next? Two or three is plenty."* (skip allowed without push-back)
- **Narrative spine — Gap:** *"What has the field NOT figured out yet that this study will?"*
- **Narrative spine — Question:** *"What's the specific, testable question that sits inside that gap?"*
- **Narrative spine — Approach:** *"How are you going to attack it? One sentence is fine."*
- **Narrative spine — Implication:** *"If this works out, what does it change about how the field thinks?"* (skip → `[TBD: filled as results emerge]`)

### Push-back rationales (use once per skipped field)

| Field | Rationale to use on first skip |
|---|---|
| `Working title` | "Even a placeholder title gives `supervisor` something to anchor on — can be a rough one-liner." |
| `Field / sub-field` | "Field determines which preset to suggest and how `figure-descriptor` defaults plot conventions — please name it even if narrow." |
| `Target venue` | "Venue determines word limits, figure budget, reviewer expectations, and `reviewer`'s severity bar. Even a top-2 short list is more useful than `[TBD]`." |
| `Central hypothesis` | "Without a hypothesis, `supervisor` will ask every conversation. A rough one-sentence stake is far better than `[TBD]` — refine later." |
| `Research topic` | "What's the **big-picture question**, distinct from the specific hypothesis? One or two sentences." |
| `Datasets` | "Which dataset(s) are you using? Source, modality, approximate size, access status. If none decided yet, `[TBD]` is OK but flagged." |
| `Narrative spine — Gap / Question / Approach` | "The spine is what `paper-writer` anchors the intro and discussion to — even rough one-liners help." |

`Backup venues` and `Narrative spine — Implication` skip without push-back.

## C. Preset overlay (final step of the interview)

Consult `preset_arg` from the [SKILL.md](../SKILL.md) argument parsing:

- If `preset_arg ∈ {minimal, no-overlay}`: skip this section entirely.
- If `preset_arg = neuro-fmri`: confirm once with the user before applying. No need to re-list options.
- Otherwise (empty): ask: "Apply a domain preset? Available presets in this plugin: `neuro-fmri`. Or `none` to stay field-neutral."

If the user selects a preset, record the preset name. Phase 3 will write it as `Preset overlay: <name>` in the `## Project context` block; phase 4 will use it to pick the right memory template per agent.
