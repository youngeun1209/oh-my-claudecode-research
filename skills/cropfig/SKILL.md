---
name: cropfig
description: Three-step pipeline from a Keynote (.key) or PowerPoint (.pptx) deck to manuscript + outline. Func 1 exports vector PDFs per slide; func 2 crops them (vector preserved) and renders an outline-grade PNG from the same cropped artifact; func 3 copies PDFs into the LaTeX manuscript figures dir and PNGs into the outline.md figures dir, then inserts/updates image links after each result heading.
---

<Purpose>
Three-step pipeline that produces, from a `.key` or `.pptx` deck, both manuscript-ready vector PDFs and outline-ready raster PNGs of the figure-only content (top label and bottom caption stripped), and uploads both into the right places. Both image artifacts derive from the same cropped PDF so they cannot drift; the outline embed is idempotent (re-running replaces the link rather than duplicating).
</Purpose>

<Use_When>
- You author figures in Keynote/PowerPoint and need (a) vector PDFs to drop into a LaTeX manuscript and (b) low-resolution PNGs to embed into an outline doc that already carries caption text.
- The `$sync` command needs to embed figure-only PNGs into an outline document at each result section.
- Preparing figures for slides / social-media / a reviewer response where the caption is supplied separately.
</Use_When>

<Do_Not_Use_When>
- The caller wants the slide with its caption / label intact (the full-slide PDFs are intermediate and discarded — only cropped artifacts are saved).
- The deck has no consistent "Figure N. Title" top label or trailing caption (the heuristic still tight-bboxes whitespace, so this is safe but wasted effort).
- You need a different crop policy (e.g. keep top label, drop bottom only) — the band-classification heuristic is symmetric and not configurable per-side.
</Do_Not_Use_When>

<Configuration>
Required inputs: the deck path + (for func 3) the manuscript dir and outline file. Cropping outputs land next to the deck by default; func 3 reads from there and copies into the manuscript + outline-parent figures dirs.

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `DECK_FILE` | (required) | func 1, 2, 3 | Path to a `.key` or `.pptx` deck. Step 1 + 2 read it directly; step 3 derives `<deck_parent>/pdf/` and `<deck_parent>/png/` from it. |
| `MANUSCRIPT_DIR` | `paper` | func 3 | LaTeX manuscript root. Cropped PDFs land in `<MANUSCRIPT_DIR>/figures/figureNN.pdf`. Matches `$omxr-setup`'s default. |
| `OUTLINE_FILE` | `outline.md` | func 3 | Outline markdown file. PNGs land in `<dirname(OUTLINE_FILE)>/figures/figureNN.png`; image links are inserted into the outline itself. |
| `RESULT_PATTERN` | `^### Result (\d+)` | func 3 | Regex with a single capture group = figure number. Used to find result headings in the outline. |
| `CROPFIG_PROBE_DPI` | `100` | func 2 | DPI used for the probe rasterization that drives crop-bound detection. Higher = slower but slightly tighter crops. |
| `CROPFIG_PNG_DPI` | `120` | func 2 | Output DPI for the outline PNGs. Raise for sharper outline review (and larger docx); lower for slimmer docx. |

**Output locations.**

```
<dirname($DECK_FILE)>/
├── <deck>.key|pptx               # the deck itself
├── pdf/figureNN.pdf              # func 2 writes (manuscript-grade vector)
└── png/figureNN.png              # func 2 writes (outline-grade raster)

$MANUSCRIPT_DIR/
└── figures/figureNN.pdf          # func 3 copies here for the .tex

dirname($OUTLINE_FILE)/
├── $OUTLINE_FILE                 # func 3 inserts/updates ![Figure N](...) links
└── figures/figureNN.png          # func 3 copies here for the markdown
```

These defaults match `$omxr-setup`'s conventions (`Manuscript dir: paper/`, `Outline file: outline.md`, `Result pattern: ^### Result (\d+)`). See `wiki/Configuration.md` for the AGENTS.md Research-stack schema.

On first invocation with no `DECK_FILE` and no project `Deck file` in AGENTS.md, ask the user for the deck path then offer to persist it to the project's AGENTS.md.
</Configuration>

<Steps>

### Step 1 — Export deck to per-slide PDFs (`export_deck.py`)

Run the exporter with a temp staging directory:

```bash
STAGE=$(mktemp -d)
python3 "$CODEX_PLUGIN_ROOT"/skills/cropfig/export_deck.py "$DECK_FILE" "$STAGE"
```

Dispatch inside `export_deck.py` — each format uses its native app to avoid cross-format import drift:
- `.key` → macOS Keynote via AppleScript → single deck PDF.
- `.pptx` → macOS PowerPoint via AppleScript when `/Applications/Microsoft PowerPoint.app` is present; otherwise LibreOffice headless (`soffice --convert-to pdf`).

The single deck PDF is then split into `figure01.pdf`, `figure02.pdf`, … using PyMuPDF. These per-slide PDFs are vector (text and lines stay sharp at any zoom) and feed Step 2.

**Guard:** if export fails (missing tool, permission denied, headless env), surface the error and stop.

### Step 2 — Crop + emit both artifacts (`crop_figures.py`)

```bash
python3 "$CODEX_PLUGIN_ROOT"/skills/cropfig/crop_figures.py "$STAGE"
rm -rf "$STAGE"
```

This writes to `<dirname($DECK_FILE)>/pdf/` and `<dirname($DECK_FILE)>/png/`. To write elsewhere, pass positional output dirs:

```bash
python3 "$CODEX_PLUGIN_ROOT"/skills/cropfig/crop_figures.py "$STAGE" "$PDF_OUT" "$PNG_OUT"
```

For each slide PDF, the script:
1. Renders a `CROPFIG_PROBE_DPI` probe and runs `find_crop_bounds` from `crop_bounds.py` (band-classification heuristic on top + bottom; tight-bbox on remaining content).
2. Maps the pixel bounds back to PDF point coordinates and applies them as a CropBox on a copy of the slide — output stays vector.
3. Writes the cropped PDF next to the deck under `pdf/figureNN.pdf`.
4. Re-rasterizes the cropped PDF at `CROPFIG_PNG_DPI` → `png/figureNN.png` next to the deck.

Both outputs share the same crop decision because the PNG is a downsampled view of the manuscript PDF.

### Step 3 — Upload to manuscript + outline (`upload_figures.py`)

```bash
python3 "$CODEX_PLUGIN_ROOT"/skills/cropfig/upload_figures.py
```

Reads from `<deck_parent>/pdf/` and `<deck_parent>/png/` (so func 2 must have run first). Does two things:

**3a. Manuscript copy.** For each `figureNN.pdf`, copies to `$MANUSCRIPT_DIR/figures/figureNN.pdf`. The .tex is **not modified** — `\includegraphics{figures/figureNN}` is author content.

**3b. Outline embed.** For each `figureNN.png`:
1. Copy to `<dirname($OUTLINE_FILE)>/figures/figureNN.png`.
2. Scan the outline for lines matching `$RESULT_PATTERN`. For each match, the captured `N` is the figure number; insert (or replace, if previously inserted by this script) the link `![Figure N](figures/figureNN.png)` immediately after the heading (skipping blank lines).

The embed is idempotent — re-running replaces the existing link line with the same content rather than appending a new one. Result heading without a matching figure is reported as `missing`; figure with no matching result heading is reported as `orphan`.

### Step 4 — Report

```
## Cropfig run — YYYY-MM-DD

- Deck: $DECK_FILE (N slides)
- Manuscript PDFs: <dirname($DECK_FILE)>/pdf/ (N files)
- Outline PNGs:    <dirname($DECK_FILE)>/png/ (N files, $CROPFIG_PNG_DPI DPI)
- Top label removed: A / N
- Bottom caption removed: B / N

Upload:
- $MANUSCRIPT_DIR/figures/: N PDF(s) copied
- $OUTLINE_FILE: M heading(s) updated  (missing: ..., orphan: ...)

Slides where heuristic skipped a side (still tight-bboxed):
- <filename> — <which side>
```

If Step 1 failed, report only that and skip the rest. Steps 2 and 3 can run independently if a prior staging dir or PDF/PNG dir already exists.

</Steps>

<Output_Contract>

| Path | Owner | Content | Used by |
|---|---|---|---|
| `<dirname($DECK_FILE)>/pdf/figureNN.pdf` | func 2 | cropped vector PDF (no top label, no bottom caption, tight-bbox); page CropBox set | source of truth — func 3 reads here for the manuscript copy |
| `<dirname($DECK_FILE)>/png/figureNN.png` | func 2 | rasterized view of the same cropped PDF at `CROPFIG_PNG_DPI` | source of truth — func 3 reads here for the outline copy |
| `$MANUSCRIPT_DIR/figures/figureNN.pdf` | func 3 (copy) | identical to the source PDF | `\includegraphics{figures/figureNN}` in the .tex |
| `<dirname($OUTLINE_FILE)>/figures/figureNN.png` | func 3 (copy) | identical to the source PNG | `![Figure N](figures/figureNN.png)` in the outline |
| `$OUTLINE_FILE` | func 3 (modifies) | image link inserted after each result heading | outline rendering (GitHub, VS Code preview, Pandoc → docx) |

Filenames mirror across the four image locations so callers can pair `figureNN.pdf` with `figureNN.png`. The staging dir from Step 1 is ephemeral and deleted at the end of the run; no uncropped intermediate is persisted.

</Output_Contract>

<Failure_Modes>

| Symptom | Cause | Action |
|---|---|---|
| `ModuleNotFoundError: fitz` | PyMuPDF not installed | `python3 -m pip install pymupdf` |
| `ModuleNotFoundError: numpy` / `PIL` | bare environment | `python3 -m pip install numpy pillow` |
| `ERROR: .key export requires macOS + Keynote` | running on non-macOS with a `.key` deck | run on macOS, or re-save the deck as `.pptx` and retry |
| `Keynote export failed: ...` | Keynote not installed, deck password-protected, or AppleScript permission denied | grant System Settings → Privacy & Security → Automation → Terminal/your shell → Keynote |
| `PowerPoint export failed: ...` | PowerPoint not licensed/signed in, deck password-protected, or AppleScript permission denied | grant System Settings → Privacy & Security → Automation → Terminal/your shell → Microsoft PowerPoint. Failures are no longer silently swallowed — there is no auto-fallback when PowerPoint IS installed. |
| `PowerPoint export failed: ... -9074` | Office sandbox refused to write to the staging path | the script already stages under `~/Library/Caches/cropfig/` to satisfy Office sandbox; if you see this anyway, check that `~/Library/Caches/` is writable and Office has been granted Full Disk Access if your deck is on a network volume |
| `LibreOffice (soffice) not on PATH` | Linux/PowerPoint-not-installed path with no LibreOffice | `brew install --cask libreoffice` (mac) / `apt install libreoffice` (linux) |
| Top label or bottom caption NOT removed on a slide | band thinner than `MIN_LABEL_HEIGHT=30` rows, or contains a colored element (heuristic treats it as figure content) | accept — tight-bbox still removes whitespace; don't globally lower the threshold to catch one slide |
| Cropped PDF still shows label when opened in some viewers | viewer ignores CropBox and renders MediaBox | use a viewer that honors CropBox (Preview, Acrobat, most LaTeX rasterizers do); the PNG path is unaffected |
| Output PNG looks blurry in docx | `CROPFIG_PNG_DPI` too low | raise to 150 / 180 (file sizes grow proportionally) |
| func 3 reports `headings without matching figure: #N` | outline has more `### Result N` headings than the deck has slides for | either add the missing slide to the deck, or trim the outline heading; func 3 will not invent a figure |
| func 3 reports `orphan figures: figureN` | deck has more slides than the outline has result headings | extend the outline with `### Result N`, or accept the orphan if those slides are non-result (concept, schematic, appendix) |
| `WARN (3b copy): PNG source dir not found` | func 2 has not run yet, or wrote to a different location | run func 1 + 2 first; verify `<dirname($DECK_FILE)>/png/` exists |

</Failure_Modes>

<Files>
- `SKILL.md` — this file.
- `export_deck.py` — func 1: deck → per-slide vector PDFs. Dispatches by extension: `.key` → Keynote AppleScript, `.pptx` → PowerPoint AppleScript when installed, else LibreOffice headless. Splits the resulting deck PDF via PyMuPDF. Stages under `~/Library/Caches/cropfig/` on macOS so Office sandbox can write.
- `crop_figures.py` — func 2: per-slide PDF → cropped PDF (vector, manuscript) + raster PNG (outline). Both share one crop decision.
- `upload_figures.py` — func 3: copies cropped PDFs to `$MANUSCRIPT_DIR/figures/`, copies cropped PNGs to `<dirname($OUTLINE_FILE)>/figures/`, inserts/updates `![Figure N](...)` links in the outline after each `$RESULT_PATTERN` match. Idempotent.
- `crop_bounds.py` — pure heuristic module. `find_top_cut`, `find_bottom_cut`, `find_crop_bounds(arr)` — used by `crop_figures.py`. Tune constants at the top if your slide-deck layout changes (most likely tweak: `MIN_LABEL_HEIGHT` for shorter labels).
</Files>
