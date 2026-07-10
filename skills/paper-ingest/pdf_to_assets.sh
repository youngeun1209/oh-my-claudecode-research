#!/usr/bin/env bash
# Extract reading assets from a paper PDF using poppler.
#
# The built-in Read tool cannot see the brew-installed pdftoppm (PATH cache), so
# the paper-ingest skill calls poppler DIRECTLY through this wrapper.
#
# Produces, under an output dir:
#   text.txt          full extracted body text (for the model to summarize)
#   page-NN.png       low-res render of every page (figure scouting, ~100 dpi)
#   info.txt          pdfinfo dump (page count, title metadata)
#
# It does NOT crop a final figure — that is a second, targeted step the skill runs
# once it has chosen a figure page (see "crop a figure region" below).
#
# Usage:
#   pdf_to_assets.sh <pdf-path> [out-dir]
#       default out-dir = <scratchpad>/paper-ingest/<pdf-stem>
#
#   # after choosing a page+region, crop a publication figure:
#   pdf_to_assets.sh --crop <pdf-path> <page> <x> <y> <W> <H> <out-png> [dpi]
#       coords are in pixels at the given dpi (default 200).

set -euo pipefail

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' not found — install poppler (brew install poppler)"; exit 3; }; }
need pdftotext
need pdftoppm
need pdfinfo

# ---- crop mode -------------------------------------------------------------
if [ "${1:-}" = "--crop" ]; then
  shift
  PDF="$1"; PAGE="$2"; X="$3"; Y="$4"; W="$5"; H="$6"; OUT="$7"; DPI="${8:-200}"
  [ -f "$PDF" ] || { echo "ERROR: pdf not found: $PDF"; exit 2; }
  mkdir -p "$(dirname "$OUT")"
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  pdftoppm -png -r "$DPI" -x "$X" -y "$Y" -W "$W" -H "$H" -f "$PAGE" -l "$PAGE" "$PDF" "$TMP/crop" 2>/dev/null
  CROPPED="$(ls "$TMP"/crop-*.png 2>/dev/null | head -1)"
  [ -n "$CROPPED" ] || { echo "ERROR: crop produced no image"; exit 4; }
  cp "$CROPPED" "$OUT"
  echo "cropped figure -> $OUT"
  exit 0
fi

# ---- extract mode ----------------------------------------------------------
PDF="${1:?usage: pdf_to_assets.sh <pdf-path> [out-dir]}"
[ -f "$PDF" ] || { echo "ERROR: pdf not found: $PDF"; exit 2; }

STEM="$(basename "${PDF%.*}")"
SCRATCH="${CLAUDE_SCRATCHPAD:-/tmp}"
OUT="${2:-$SCRATCH/paper-ingest/$STEM}"
mkdir -p "$OUT"

pdfinfo "$PDF" > "$OUT/info.txt" 2>/dev/null || true
PAGES="$(grep -i '^Pages:' "$OUT/info.txt" | awk '{print $2}')"
PAGES="${PAGES:-0}"

# Full text (let the model decide what matters; cap to first 30 pages for speed).
LASTTXT=$(( PAGES < 30 ? PAGES : 30 ))
[ "$LASTTXT" -gt 0 ] && pdftotext -f 1 -l "$LASTTXT" "$PDF" "$OUT/text.txt" 2>/dev/null || pdftotext "$PDF" "$OUT/text.txt" 2>/dev/null

# Low-res page renders for figure scouting (cap at 20 pages to stay cheap).
LASTIMG=$(( PAGES < 20 ? PAGES : 20 ))
[ "$LASTIMG" -lt 1 ] && LASTIMG=1
pdftoppm -png -r 100 -f 1 -l "$LASTIMG" "$PDF" "$OUT/page" 2>/dev/null

echo "out_dir: $OUT"
echo "pages: $PAGES"
echo "text: $OUT/text.txt ($(wc -l < "$OUT/text.txt" 2>/dev/null || echo 0) lines)"
echo "page_pngs: $(ls "$OUT"/page-*.png 2>/dev/null | wc -l | tr -d ' ')"
