"""Tight-crop captioned figure PNGs to figure-only content.

Reads PNGs from the source directory (typically already trimmed of bottom
captions by your slide-export pipeline), removes the top "Figure N. Title"
label band using a band-classification heuristic, then tight-bbox crops and
writes to the destination directory with uniform white padding.

Invariants:
- The source directory is read-only here.
- The destination directory is fully owned by this script and rewritten on
  every run.

Configurable via env vars or positional args:

    FIGURES_SRC=path/to/src FIGURES_DST=path/to/dst python3 crop_top_label.py
    python3 crop_top_label.py [SRC_DIR] [DST_DIR]

Defaults:
    SRC_DIR = $FIGURES_SRC or "figures/captured"
    DST_DIR = $FIGURES_DST or "figures/tight"
"""
import os
import sys
import numpy as np
from PIL import Image

DEFAULT_SRC = os.environ.get("FIGURES_SRC", "figures/captured")
DEFAULT_DST = os.environ.get("FIGURES_DST", "figures/tight")

MIN_LABEL_HEIGHT = 30        # cumulative top-label band height (rows) to trigger crop
PADDING = 10                  # uniform white padding around the cropped figure
DARK_THRESHOLD = 200          # pixel <= this counts as "ink"
SAT_THRESHOLD = 0.15          # HSV saturation above which a pixel is "colored"
COLOR_FRAC_THRESHOLD = 0.005  # band is "figure" if colored-pixel fraction exceeds this
LINE_WIDTH_FRAC = 0.25        # band is "figure" if a single dark run is longer than this fraction of width
WHITE_BBOX_THRESHOLD = 250    # pixels with mean(rgb) >= this count as white for bbox crop


def classify_band(arr, s, e):
    band = arr[s:e + 1]
    if band.shape[0] < 6:
        return "empty"
    rgb = band.astype(np.float32) / 255.0
    mx = rgb.max(axis=-1); mn = rgb.min(axis=-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    if (sat > SAT_THRESHOLD).mean() > COLOR_FRAC_THRESHOLD:
        return "figure"
    gray = band.mean(axis=-1)
    dark = gray < 130
    max_run = 0
    for row in dark:
        if not row.any():
            continue
        a = np.concatenate(([0], row.astype(int), [0]))
        diff = np.diff(a)
        starts = np.where(diff == 1)[0]; ends = np.where(diff == -1)[0]
        runs = ends - starts
        if runs.size:
            r = int(runs.max())
            if r > max_run:
                max_run = r
    if max_run > arr.shape[1] * LINE_WIDTH_FRAC:
        return "figure"
    return "caption"


def find_top_cut(arr):
    """Return the row index just below the last 'caption-like' band at the top,
    or None if no top label is detected."""
    h = arr.shape[0]
    gray = arr.mean(axis=-1)
    is_content = gray.min(axis=1) < DARK_THRESHOLD
    segs = []
    kind = "C" if is_content[0] else "G"
    start = 0
    for i in range(1, h):
        cur = "C" if is_content[i] else "G"
        if cur != kind:
            segs.append((kind, start, i - 1))
            kind, start = cur, i
    segs.append((kind, start, h - 1))

    label_bottom = None
    label_total = 0
    for kind, s, e in segs:
        if kind == "G":
            continue
        cls = classify_band(arr, s, e)
        if cls == "figure":
            break
        if cls == "caption":
            label_bottom = e
            label_total += (e - s + 1)
    if label_bottom is None or label_total < MIN_LABEL_HEIGHT:
        return None
    return label_bottom + 1


def tight_bbox(arr):
    gray = arr.mean(axis=-1)
    nonwhite = gray < WHITE_BBOX_THRESHOLD
    rows = np.where(nonwhite.any(axis=1))[0]
    cols = np.where(nonwhite.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        return arr
    return arr[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def main(src=DEFAULT_SRC, dst=DEFAULT_DST):
    if not os.path.isdir(src):
        sys.exit(f"ERROR: source folder not found: {src}")
    os.makedirs(dst, exist_ok=True)
    n_total = n_label_removed = 0
    skipped_label = []
    for fname in sorted(os.listdir(src)):
        if not fname.lower().endswith(".png"):
            continue
        arr = np.array(Image.open(os.path.join(src, fname)).convert("RGB"))
        top = find_top_cut(arr)
        if top is not None:
            arr = arr[top:]
            n_label_removed += 1
        else:
            skipped_label.append(fname)
        arr = tight_bbox(arr)
        canvas = np.full(
            (arr.shape[0] + 2 * PADDING, arr.shape[1] + 2 * PADDING, 3),
            255, dtype=np.uint8,
        )
        canvas[PADDING:PADDING + arr.shape[0], PADDING:PADDING + arr.shape[1]] = arr
        Image.fromarray(canvas).save(os.path.join(dst, fname))
        n_total += 1

    print(f"Tight-cropped {n_total} PNG(s) -> {dst}")
    print(f"Top label removed on {n_label_removed}/{n_total}")
    if skipped_label:
        print("Top label NOT detected (left as tight-bbox only):")
        for f in skipped_label:
            print(f"  - {f}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    dst = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DST
    main(src, dst)
