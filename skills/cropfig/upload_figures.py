"""Upload cropped figures to manuscript and outline.

Func 3 of the cropfig pipeline. Reads from `<deck_parent>/pdf/` and
`<deck_parent>/png/` (produced by `crop_figures.py`), and:

3a. Copies each PDF to `<Manuscript dir>/figures/figureNN.pdf`. The .tex
    references them via `\\includegraphics{figures/figureNN}`. This script does
    NOT modify the .tex — figure blocks are author content.

3b. Copies each PNG to `<dirname(Outline file)>/figures/figureNN.png`, then
    inserts or updates an image link in the outline:
        ![Figure N](figures/figureNN.png)
    immediately after each result heading matching `Result pattern` (default
    `^### Result (\\d+)`). Idempotent — repeated runs replace the existing
    link with the same content rather than duplicating.

Configuration (precedence: env var > CLAUDE.md Research stack > built-in):
    DECK_FILE         (required)  path to deck — used to locate pdf/ and png/
    MANUSCRIPT_DIR    `paper/`    destination for cropped PDFs
    OUTLINE_FILE      `outline.md`  outline markdown file
    RESULT_PATTERN    `^### Result (\\d+)`  regex with single capture group =
                                            figure number (1-indexed)

Usage:
    DECK_FILE=... MANUSCRIPT_DIR=paper OUTLINE_FILE=outline.md \\
        python3 upload_figures.py
"""
import os
import re
import shutil
import sys

DEFAULT_MANUSCRIPT_DIR = os.environ.get("MANUSCRIPT_DIR", "paper")
DEFAULT_OUTLINE_FILE = os.environ.get("OUTLINE_FILE", "outline.md")
DEFAULT_RESULT_PATTERN = os.environ.get("RESULT_PATTERN", r"^### Result (\d+)")

FIGURE_RE = re.compile(r"^figure(\d+)\.(pdf|png)$", re.IGNORECASE)


def _deck_dirs():
    deck = os.environ.get("DECK_FILE", "")
    if not deck:
        sys.exit("ERROR: DECK_FILE not set — needed to locate pdf/ and png/.")
    parent = os.path.dirname(os.path.abspath(deck))
    return os.path.join(parent, "pdf"), os.path.join(parent, "png")


def _figure_index(filename):
    m = FIGURE_RE.match(filename)
    return int(m.group(1)) if m else None


def copy_pdfs_to_manuscript(pdf_src, manuscript_dir):
    if not os.path.isdir(pdf_src):
        return [], f"PDF source dir not found: {pdf_src}"
    dst = os.path.join(manuscript_dir, "figures")
    os.makedirs(dst, exist_ok=True)
    copied = []
    for fname in sorted(os.listdir(pdf_src)):
        if _figure_index(fname) is None or not fname.lower().endswith(".pdf"):
            continue
        shutil.copy2(os.path.join(pdf_src, fname), os.path.join(dst, fname))
        copied.append(fname)
    return copied, None


def copy_pngs_for_outline(png_src, outline_file):
    if not os.path.isdir(png_src):
        return [], None, f"PNG source dir not found: {png_src}"
    dst_dir = os.path.join(os.path.dirname(os.path.abspath(outline_file)), "figures")
    os.makedirs(dst_dir, exist_ok=True)
    copied = []
    for fname in sorted(os.listdir(png_src)):
        if _figure_index(fname) is None or not fname.lower().endswith(".png"):
            continue
        shutil.copy2(os.path.join(png_src, fname), os.path.join(dst_dir, fname))
        copied.append(fname)
    return copied, dst_dir, None


def update_outline(outline_file, png_copied, result_pattern):
    """Insert/update `![Figure N](figures/figureNN.png)` after each result heading.

    Returns (updated_headings, headings_without_figure, orphan_figures, error).
    `orphan_figures` = figures copied but no matching result heading.
    """
    if not os.path.exists(outline_file):
        return [], [], [], f"Outline file not found: {outline_file}"

    available = {}
    for fname in png_copied:
        idx = _figure_index(fname)
        if idx is not None:
            available[idx] = fname

    heading_re = re.compile(result_pattern)
    # Match an existing figure link line we may have written previously.
    existing_link_re = re.compile(r"^\s*!\[Figure \d+\]\(figures/figure\d+\.png\)\s*$")

    with open(outline_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    out_lines = []
    updated_headings = []
    headings_without_figure = []
    matched_indices = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        m = heading_re.match(line)
        if m:
            try:
                idx = int(m.group(1))
            except (IndexError, ValueError):
                i += 1
                continue
            fname = available.get(idx)
            # Look ahead: if the next non-blank line is an existing figure link
            # placed by this script, drop it (we re-emit below).
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                out_lines.append(lines[j])
                j += 1
            if j < len(lines) and existing_link_re.match(lines[j]):
                j += 1  # skip the old link
            if fname:
                out_lines.append(f"![Figure {idx}](figures/{fname})")
                updated_headings.append(idx)
                matched_indices.add(idx)
            else:
                headings_without_figure.append(idx)
            i = j
            continue
        i += 1

    with open(outline_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + ("\n" if out_lines else ""))

    orphan_figures = sorted(set(available.keys()) - matched_indices)
    return updated_headings, headings_without_figure, orphan_figures, None


def main():
    pdf_src, png_src = _deck_dirs()
    manuscript_dir = DEFAULT_MANUSCRIPT_DIR
    outline_file = DEFAULT_OUTLINE_FILE
    result_pattern = DEFAULT_RESULT_PATTERN

    pdfs, pdf_err = copy_pdfs_to_manuscript(pdf_src, manuscript_dir)
    if pdf_err:
        print(f"WARN (3a): {pdf_err}", file=sys.stderr)
    pngs, png_dst, png_err = copy_pngs_for_outline(png_src, outline_file)
    if png_err:
        print(f"WARN (3b copy): {png_err}", file=sys.stderr)

    if pngs:
        updated, missing, orphan, outline_err = update_outline(
            outline_file, pngs, result_pattern
        )
    else:
        updated, missing, orphan, outline_err = [], [], [], None

    print(f"3a manuscript: copied {len(pdfs)} PDF(s) -> "
          f"{os.path.join(manuscript_dir, 'figures')}")
    print(f"3b outline:    copied {len(pngs)} PNG(s) -> {png_dst}")
    if outline_err:
        print(f"WARN (3b embed): {outline_err}", file=sys.stderr)
    else:
        print(f"               embedded into {outline_file}: "
              f"{len(updated)} heading(s) updated")
        if missing:
            print(f"               headings without matching figure: "
                  f"{', '.join(f'#{n}' for n in missing)}")
        if orphan:
            print(f"               orphan figures (no matching heading): "
                  f"{', '.join(f'figure{n}' for n in orphan)}")


if __name__ == "__main__":
    main()
