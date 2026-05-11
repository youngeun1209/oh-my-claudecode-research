---
name: cropfig
description: Tight-crop captioned figure PNGs to figure-only content. Detects and removes the top "Figure N. Title" label band (and trailing whitespace), useful when an outline document already provides its own caption text and the embedded image must not duplicate it. Output goes to a configurable directory; the source directory is read-only.
---

<Purpose>
Strip the top label band from captioned figure PNGs (typical of slide-export pipelines) and emit figure-only PNGs that can be embedded into a separate manuscript / outline document without caption duplication.
</Purpose>

<Use_When>
- The `/sync` command needs to embed figure-only PNGs into an outline document that already carries caption text.
- A subagent or slash command (`paper-writer`, `figure-descriptor`, `reviewer`, custom commands) needs the figure content of a slide without its "Figure N. Title" header.
- Preparing a figure for slides / a social-media post / a reviewer response where the caption is supplied separately.
- Preparing a figure for downstream image processing where surrounding text would interfere.
</Use_When>

<Do_Not_Use_When>
- The caller wants the canonical caption-bearing PNG (just read the source directory directly — this skill never overwrites it).
- The caller only needs figure metadata or layout, not a processed image.
- The source PNGs don't have a "Figure N. Title" top label (the heuristic will fail open — output equals input minus whitespace, so this is safe but wasted effort).
</Do_Not_Use_When>

<Configuration>
This skill reads three environment variables (with defaults relative to the project root):

| Variable | Default | Purpose |
|---|---|---|
| `FIGURES_SRC` | `figures/captured/` | Captioned PNG source — produced by your slide-export pipeline. Read-only here. |
| `FIGURES_DST` | `figures/tight/` | Figure-only PNG destination. Owned by this skill; overwritten on every run. |
| `EXPORT_SCRIPT` | (unset) | Optional: idempotent script to refresh `FIGURES_SRC`. If set, this skill runs it as Step 1; otherwise Step 1 is skipped. |

Resolution order on each invocation:
1. **Environment variables** (highest priority — useful for one-off overrides).
2. **Project CLAUDE.md "Research stack" block** — fields `Deck export dir`, `Tight-crop output dir`, `Deck export script`. See `wiki/Configuration.md` for the schema.
3. **Defaults above.**

On first invocation in a project with no env vars and no CLAUDE.md research-stack block, ask the user once for `FIGURES_SRC` and `FIGURES_DST` (and `EXPORT_SCRIPT` if relevant), then offer to persist them to the project's CLAUDE.md.
</Configuration>

<Steps>

### Step 1 — Refresh source PNGs (if configured)

If `EXPORT_SCRIPT` is set and exists, run it (must be idempotent):

```bash
bash "$EXPORT_SCRIPT"
```

If the user passes a custom path argument, forward it: `bash "$EXPORT_SCRIPT" "$ARGUMENT"`.

**Guard:** if the export fails (missing tool, permission denied, headless environment), surface the error and stop. Do not crop stale PNGs without telling the user.

If no `EXPORT_SCRIPT` configured, assume the user has already populated `FIGURES_SRC` and proceed.

### Step 2 — Tight-crop each PNG

Run the bundled Python script:

```bash
python3 "$CLAUDE_PLUGIN_ROOT"/skills/cropfig/crop_top_label.py
```

Or with explicit overrides:

```bash
python3 "$CLAUDE_PLUGIN_ROOT"/skills/cropfig/crop_top_label.py "$FIGURES_SRC" "$FIGURES_DST"
```

The script:
1. Detects and removes the top label band using a band-classification heuristic (color saturation + long-dark-run detection).
2. Tight-bbox crops the remaining content.
3. Adds 10 px uniform white padding.
4. Writes to `$FIGURES_DST` (filename mirrors source so callers can map slide → output 1-to-1).

### Step 3 — Report

```
## Tight figure crop — YYYY-MM-DD

- Source: $FIGURES_SRC (N PNGs)
- Output: $FIGURES_DST (N PNGs)
- Top label removed: M / N

Slides where label was NOT detected (left as tight-bbox only):
- <filename> — tight-bbox only
```

If Step 1 failed, report only that and skip Steps 2–3.

</Steps>

<Output_Contract>

| Path | Owner | Top label | Bottom caption | Used by |
|---|---|---|---|---|
| `$FIGURES_SRC` | your export pipeline | KEPT | should already be removed by export | slide-context readers, `/todofig`, agents reading slide content |
| `$FIGURES_DST` | **this skill** | **removed** | (removed by upstream export) | embeds in outline documents, figure-only consumers |

`$FIGURES_DST/<filename>` mirrors the source filename exactly.

</Output_Contract>

<Failure_Modes>

| Symptom | Cause | Action |
|---|---|---|
| `Export script returned non-zero` | tool missing, permission denied | surface error; do not crop stale PNGs |
| Top label NOT removed on a slide | label band thinner than `MIN_LABEL_HEIGHT=30` rows, or contains a colored element | accept — tight-bbox still removes whitespace; don't globally lower threshold to catch one slide |
| `ModuleNotFoundError: PIL` / `numpy` | bare environment | `python3 -m pip install pillow numpy` |
| Output directory wasn't created | first run, no write permission on parent | the script creates the directory; if permission denied, report it |

</Failure_Modes>

<Files>
- `SKILL.md` — this file.
- `crop_top_label.py` — the cropper. Importable (`from crop_top_label import main`) or runnable as a script. Heuristic constants at the top of the file; tune there if your slide-deck layout changes.
</Files>
