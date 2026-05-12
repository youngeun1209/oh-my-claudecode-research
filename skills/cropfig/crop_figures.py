"""Crop per-slide PDFs to figure-only content + emit outline-grade PNG.

Func 2 of the cropfig pipeline. For each per-slide PDF in <input_dir>:

1. Render a low-DPI probe and run the band-classification heuristic from
   `crop_bounds.py` to find figure bounds (top label, bottom caption, and
   surrounding whitespace all removed).
2. Map the pixel bounds to PDF point coords and apply them as a CropBox on a
   copy of the slide — the cropped PDF stays vector (manuscript-grade).
3. Rasterize the cropped PDF at outline DPI -> PNG (small enough for docx
   embed, sharp enough for on-screen review).

Both outputs share the same crop decision because they are derived from the
same cropped PDF — the PNG is a downsampled view of the manuscript artifact.

Usage:
    DECK_FILE=path/to/deck.pptx python3 crop_figures.py <input_dir>
    python3 crop_figures.py <input_dir> <pdf_out_dir> <png_out_dir>

Outputs land next to the deck by default — `<dirname($DECK_FILE)>/pdf/` and
`<dirname($DECK_FILE)>/png/`. Pass positional args to write elsewhere
(useful for tests or one-off runs). The script errors if `DECK_FILE` is unset
and positional args are not given.

Tunable via env vars:
    CROPFIG_PROBE_DPI   default 100   probe render DPI for bound detection
    CROPFIG_PNG_DPI     default 120   outline PNG render DPI
"""
import os
import sys

import fitz
import numpy as np

from crop_bounds import find_crop_bounds


def _deck_parent():
    p = os.environ.get("DECK_FILE", "")
    return os.path.dirname(os.path.abspath(p)) if p else None


_PARENT = _deck_parent()
DEFAULT_PDF_DST = os.path.join(_PARENT, "pdf") if _PARENT else None
DEFAULT_PNG_DST = os.path.join(_PARENT, "png") if _PARENT else None
PROBE_DPI = int(os.environ.get("CROPFIG_PROBE_DPI", "100"))
PNG_DPI = int(os.environ.get("CROPFIG_PNG_DPI", "120"))


def _pixmap_to_rgb(pix):
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )
    if pix.n == 4:
        arr = arr[..., :3]
    elif pix.n == 1:
        arr = np.repeat(arr, 3, axis=-1)
    return arr


def crop_one(src_pdf, pdf_out, png_out, probe_dpi=PROBE_DPI, png_dpi=PNG_DPI):
    doc = fitz.open(src_pdf)
    if doc.page_count != 1:
        # Per-slide PDFs from export_deck.py have exactly one page; bail on
        # multi-page inputs so the caller notices.
        doc.close()
        raise ValueError(
            f"{src_pdf}: expected single-page PDF, got {doc.page_count}"
        )
    page = doc[0]
    probe = page.get_pixmap(dpi=probe_dpi)
    arr = _pixmap_to_rgb(probe)

    top, bottom, left, right = find_crop_bounds(arr)
    # Pixel -> MuPDF points: same axis orientation as page.rect (top-left
    # origin, y-down), so a direct scale works for set_cropbox.
    s = 72.0 / probe_dpi
    crop_rect = fitz.Rect(left * s, top * s, right * s, bottom * s)
    # Clamp to the page rect — a probe-rounded bound may slip a fraction of a
    # point outside, and PyMuPDF rejects a cropbox not contained in mediabox.
    crop_rect = crop_rect & page.rect

    page.set_cropbox(crop_rect)
    doc.save(pdf_out)
    doc.close()

    out = fitz.open(pdf_out)
    out_pix = out[0].get_pixmap(dpi=png_dpi)
    out_pix.save(png_out)
    out.close()

    label_removed = top > 0
    caption_removed = bottom < arr.shape[0]
    return label_removed, caption_removed


def main(src_dir, pdf_dst=DEFAULT_PDF_DST, png_dst=DEFAULT_PNG_DST):
    if not os.path.isdir(src_dir):
        sys.exit(f"ERROR: input dir not found: {src_dir}")
    os.makedirs(pdf_dst, exist_ok=True)
    os.makedirs(png_dst, exist_ok=True)

    n_total = n_label = n_caption = 0
    skipped = []
    for fname in sorted(os.listdir(src_dir)):
        if not fname.lower().endswith(".pdf"):
            continue
        src = os.path.join(src_dir, fname)
        stem = os.path.splitext(fname)[0]
        pdf_out = os.path.join(pdf_dst, f"{stem}.pdf")
        png_out = os.path.join(png_dst, f"{stem}.png")
        try:
            label, caption = crop_one(src, pdf_out, png_out)
        except Exception as e:
            skipped.append((fname, str(e)))
            continue
        n_total += 1
        n_label += int(label)
        n_caption += int(caption)

    print(f"Cropped {n_total} slide(s)")
    print(f"  -> PDF: {pdf_dst}   (top label removed: {n_label}/{n_total}, "
          f"bottom caption removed: {n_caption}/{n_total})")
    print(f"  -> PNG: {png_dst}   ({PNG_DPI} DPI)")
    if skipped:
        print("Skipped:")
        for f, err in skipped:
            print(f"  - {f}: {err}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    pdf_dst = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PDF_DST
    png_dst = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PNG_DST
    if src is None:
        sys.exit("ERROR: input dir required (positional arg 1).")
    main(src, pdf_dst, png_dst)
