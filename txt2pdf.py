#!/usr/bin/env python3
"""Convert every .txt file in a folder into a .pdf file.

Usage:
    python txt2pdf.py INPUT_DIR [-o OUTPUT_DIR] [-r] [--font-size 10] [--page-size letter|a4]

Each ``name.txt`` becomes ``name.pdf``. By default PDFs are written next to
the source files; use ``-o`` to write them to another folder instead.
"""

import argparse
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Unicode-capable monospace fonts to try before falling back to built-in Courier
# (Courier only covers Latin-1 characters).
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "/Library/Fonts/Courier New.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
]

PAGE_SIZES = {"letter": letter, "a4": A4}


def load_font(font_path=None):
    """Register a TTF font and return its name, or fall back to Courier."""
    candidates = [font_path] if font_path else FONT_CANDIDATES
    for path in candidates:
        if path and Path(path).is_file():
            try:
                pdfmetrics.registerFont(TTFont("TxtMono", path))
                return "TxtMono"
            except Exception as exc:  # unreadable or unsupported font
                print(f"warning: could not load font {path}: {exc}", file=sys.stderr)
    if font_path:
        print("warning: falling back to Courier", file=sys.stderr)
    return "Courier"


def read_text(path):
    """Read a text file, trying UTF-8 first and then Latin-1."""
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def wrap_line(line, font, size, max_width):
    """Split one line into pieces that fit within max_width."""
    if not line:
        return [""]
    pieces = []
    while line:
        if pdfmetrics.stringWidth(line, font, size) <= max_width:
            pieces.append(line)
            break
        # Find the longest prefix that fits.
        cut = 1
        while cut < len(line) and pdfmetrics.stringWidth(line[: cut + 1], font, size) <= max_width:
            cut += 1
        # Prefer breaking at the last space inside that prefix.
        space = line.rfind(" ", 0, cut + 1)
        if space > 0:
            pieces.append(line[:space])
            line = line[space + 1 :]
        else:
            pieces.append(line[:cut])
            line = line[cut:]
    return pieces


def txt_to_pdf(src, dest, font, font_size=10, page_size=letter, margin=0.75 * inch):
    text = read_text(src).replace("\r\n", "\n").replace("\r", "\n").expandtabs(4)
    width, height = page_size
    max_width = width - 2 * margin
    leading = font_size * 1.2

    c = canvas.Canvas(str(dest), pagesize=page_size)
    c.setTitle(src.stem)
    y = height - margin

    def new_page():
        nonlocal y
        c.showPage()
        y = height - margin

    for raw_line in text.split("\n"):
        # Form feed characters force a page break.
        segments = raw_line.split("\f")
        for i, segment in enumerate(segments):
            if i > 0:
                new_page()
            for piece in wrap_line(segment, font, font_size, max_width):
                if y - leading < margin:
                    new_page()
                y -= leading
                c.setFont(font, font_size)
                c.drawString(margin, y, piece)

    c.save()


def main():
    parser = argparse.ArgumentParser(description="Convert a folder of .txt files to .pdf files.")
    parser.add_argument("input_dir", type=Path, help="folder containing .txt files")
    parser.add_argument("-o", "--output-dir", type=Path, help="folder for the PDFs (default: same as input)")
    parser.add_argument("-r", "--recursive", action="store_true", help="also convert .txt files in subfolders")
    parser.add_argument("--font-size", type=float, default=10, help="font size in points (default: 10)")
    parser.add_argument("--page-size", choices=PAGE_SIZES, default="letter", help="page size (default: letter)")
    parser.add_argument("--font", help="path to a .ttf font to use instead of the default")
    parser.add_argument("--overwrite", action="store_true", help="overwrite PDFs that already exist")
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"{args.input_dir} is not a folder")

    pattern = "**/*" if args.recursive else "*"
    files = sorted(p for p in args.input_dir.glob(pattern) if p.is_file() and p.suffix.lower() == ".txt")
    if not files:
        print(f"No .txt files found in {args.input_dir}")
        return 0

    font = load_font(args.font)
    converted = skipped = failed = 0
    for src in files:
        out_dir = args.output_dir / src.parent.relative_to(args.input_dir) if args.output_dir else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / (src.stem + ".pdf")
        if dest.exists() and not args.overwrite:
            print(f"skip   {dest} (exists; use --overwrite)")
            skipped += 1
            continue
        try:
            txt_to_pdf(src, dest, font, args.font_size, PAGE_SIZES[args.page_size])
            print(f"ok     {src} -> {dest}")
            converted += 1
        except Exception as exc:
            print(f"error  {src}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nDone: {converted} converted, {skipped} skipped, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
