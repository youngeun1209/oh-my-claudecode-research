"""Export a Keynote (.key) or PowerPoint (.pptx) deck to per-slide vector PDFs.

Func 1 of the cropfig pipeline. Each format uses its native app to avoid
cross-format import drift (font substitution, layout shifts):

- .key  -> macOS Keynote via AppleScript -> single deck PDF.
- .pptx -> macOS PowerPoint via AppleScript when installed; otherwise
           LibreOffice headless. The choice is deterministic — once PowerPoint
           is detected we use it and surface its errors directly rather than
           silently switching engines.

The single deck PDF is then split into per-slide PDFs using PyMuPDF, written
to <output_dir>/figureNN.pdf. These per-slide PDFs are vector (text and lines
stay sharp at any zoom) and feed `crop_figures.py` as input.

Usage:
    python3 export_deck.py <deck_path> <output_dir>
    DECK_FILE=deck.pptx python3 export_deck.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

import fitz

DEFAULT_DECK = os.environ.get("DECK_FILE", "")


def _export_keynote_pdf(deck_path, pdf_out):
    deck_abs = os.path.abspath(deck_path)
    pdf_abs = os.path.abspath(pdf_out)
    script = f'''
    tell application "Keynote"
        activate
        set theDoc to open POSIX file "{deck_abs}"
        export theDoc to POSIX file "{pdf_abs}" as PDF
        close theDoc saving no
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Keynote export failed: {result.stderr.strip()}")
    if not os.path.exists(pdf_abs):
        raise RuntimeError(f"Keynote did not produce {pdf_abs}")


def _export_powerpoint_pdf(deck_path, pdf_out):
    deck_abs = os.path.abspath(deck_path)
    pdf_abs = os.path.abspath(pdf_out)
    # Mac PowerPoint's `open` does not return a document reference, so bind via
    # `active presentation` after a short delay for the doc to register.
    script = f'''
    tell application "Microsoft PowerPoint"
        activate
        open POSIX file "{deck_abs}"
        delay 1
        set thePres to active presentation
        save thePres in POSIX file "{pdf_abs}" as save as PDF
        close thePres saving no
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerPoint export failed: {result.stderr.strip()}")
    if not os.path.exists(pdf_abs):
        raise RuntimeError(f"PowerPoint did not produce {pdf_abs}")


def _export_libreoffice_pdf(deck_path, pdf_out):
    if not shutil.which("soffice"):
        raise RuntimeError("LibreOffice (`soffice`) not on PATH.")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", tmp, deck_path],
            check=True,
        )
        produced = os.path.join(
            tmp, os.path.splitext(os.path.basename(deck_path))[0] + ".pdf"
        )
        if not os.path.exists(produced):
            raise RuntimeError(f"LibreOffice did not produce {produced}")
        shutil.copy(produced, pdf_out)


def _export_deck_to_single_pdf(deck_path, pdf_out):
    ext = os.path.splitext(deck_path)[1].lower()
    is_macos = sys.platform == "darwin"

    if ext == ".key":
        if not is_macos:
            sys.exit("ERROR: .key export requires macOS + Keynote.")
        _export_keynote_pdf(deck_path, pdf_out)
        return

    if ext == ".pptx":
        powerpoint_installed = is_macos and os.path.isdir(
            "/Applications/Microsoft PowerPoint.app"
        )
        if powerpoint_installed and shutil.which("osascript"):
            _export_powerpoint_pdf(deck_path, pdf_out)
        else:
            _export_libreoffice_pdf(deck_path, pdf_out)
        return

    sys.exit(f"ERROR: unsupported extension {ext!r}; expected .key or .pptx.")


def _split_pdf(deck_pdf, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(deck_pdf)
    n = doc.page_count
    width = max(2, len(str(n)))
    for i in range(n):
        single = fitz.open()
        single.insert_pdf(doc, from_page=i, to_page=i)
        out_path = os.path.join(out_dir, f"figure{i + 1:0{width}d}.pdf")
        single.save(out_path)
        single.close()
    doc.close()
    return n


def _staging_root():
    # macOS Microsoft Office apps are sandboxed and cannot write to /var/folders/
    # (the default TMPDIR), surfacing as AppleScript error -9074. Stage under
    # ~/Library/Caches/cropfig/ instead, which is in Office's allowed paths.
    if sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Caches/cropfig")
        os.makedirs(root, exist_ok=True)
        return root
    return None


def main(deck_path=DEFAULT_DECK, out_dir=None):
    if not deck_path:
        sys.exit("ERROR: no deck path. Pass as arg or set $DECK_FILE.")
    if not os.path.exists(deck_path):
        sys.exit(f"ERROR: deck not found: {deck_path}")
    if out_dir is None:
        sys.exit("ERROR: output dir required (positional arg 2).")

    with tempfile.TemporaryDirectory(dir=_staging_root()) as tmp:
        deck_pdf = os.path.join(tmp, "deck.pdf")
        _export_deck_to_single_pdf(deck_path, deck_pdf)
        n = _split_pdf(deck_pdf, out_dir)

    print(f"Exported {n} slide PDF(s) -> {out_dir}")


if __name__ == "__main__":
    deck = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DECK
    out = sys.argv[2] if len(sys.argv) > 2 else None
    main(deck, out)
