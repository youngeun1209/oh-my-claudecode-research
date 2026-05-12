"""Band-classification heuristic for slide images.

Given a numpy RGB array (a rasterized slide), `find_crop_bounds` returns the
pixel bounds (top, bottom, left, right) of the figure content, with top/bottom
label/caption bands removed and surrounding whitespace tight-bboxed.

Used by `crop_figures.py` after rendering a per-slide PDF probe. Operates on
pixels here; the caller maps pixels back to PDF point coordinates and applies
the crop as a vector PDF CropBox.

Constants:
    MIN_LABEL_HEIGHT      cumulative band height (px) to trigger a label cut
    DARK_THRESHOLD        pixel <= this counts as "ink" when finding segments
    SAT_THRESHOLD         HSV saturation above which a pixel is "colored"
    COLOR_FRAC_THRESHOLD  band is "figure" if colored-pixel fraction exceeds
    LINE_WIDTH_FRAC       band is "figure" if a single dark run > frac of width
    WHITE_BBOX_THRESHOLD  pixel mean(rgb) >= this counts as white for bbox
"""
import numpy as np

MIN_LABEL_HEIGHT = 30
DARK_THRESHOLD = 200
SAT_THRESHOLD = 0.15
COLOR_FRAC_THRESHOLD = 0.005
LINE_WIDTH_FRAC = 0.25
WHITE_BBOX_THRESHOLD = 250


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


def _segments(arr):
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
    return segs


def find_top_cut(arr):
    """Row index just below the last 'caption-like' band at the top, or None."""
    label_bottom = None
    label_total = 0
    for kind, s, e in _segments(arr):
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


def find_bottom_cut(arr):
    """Row index of the first 'caption-like' band at the bottom, or None.

    Iterates segments in reverse; symmetric to `find_top_cut`. Returns a row
    index such that `arr[:bottom_cut]` excludes the bottom caption.
    """
    label_top = None
    label_total = 0
    for kind, s, e in reversed(_segments(arr)):
        if kind == "G":
            continue
        cls = classify_band(arr, s, e)
        if cls == "figure":
            break
        if cls == "caption":
            label_top = s
            label_total += (e - s + 1)
    if label_top is None or label_total < MIN_LABEL_HEIGHT:
        return None
    return label_top


def find_crop_bounds(arr):
    """Return (top, bottom, left, right) pixel bounds of the figure region.

    - Removes top label band (if detected) and bottom caption band (if
      detected) via `find_top_cut` / `find_bottom_cut`.
    - Tight-bboxes the remaining content using `WHITE_BBOX_THRESHOLD`.
    - `bottom` and `right` are one-past-the-end indices (Python slice
      convention), so `arr[top:bottom, left:right]` gives the figure region.
    """
    h, w = arr.shape[:2]
    top_cut = find_top_cut(arr)
    bottom_cut = find_bottom_cut(arr)
    top = top_cut if top_cut is not None else 0
    bottom = bottom_cut if bottom_cut is not None else h

    band = arr[top:bottom]
    if band.shape[0] == 0:
        return (0, h, 0, w)
    gray = band.mean(axis=-1)
    nonwhite = gray < WHITE_BBOX_THRESHOLD
    rows = np.where(nonwhite.any(axis=1))[0]
    cols = np.where(nonwhite.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        return (0, h, 0, w)
    return (
        top + int(rows[0]),
        top + int(rows[-1]) + 1,
        int(cols[0]),
        int(cols[-1]) + 1,
    )
