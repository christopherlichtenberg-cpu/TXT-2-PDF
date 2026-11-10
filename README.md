# TXT-2-PDF

Convert every `.txt` file in a folder into a `.pdf` file.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python txt2pdf.py path/to/folder
```

Each `name.txt` becomes `name.pdf` next to it. Options:

| Option | Description |
| --- | --- |
| `-o, --output-dir DIR` | Write PDFs to `DIR` instead (subfolder structure is kept) |
| `-r, --recursive` | Also convert `.txt` files in subfolders |
| `--font-size N` | Font size in points (default 10) |
| `--page-size letter\|a4` | Page size (default letter) |
| `--font PATH` | Use a specific `.ttf` font |
| `--overwrite` | Replace PDFs that already exist (skipped by default) |

Long lines wrap, tabs are expanded, form feeds start a new page, and files are
read as UTF-8 (falling back to Windows-1252/Latin-1). A Unicode monospace font
(DejaVu Sans Mono, Courier New or Consolas) is used when found; otherwise the
built-in Courier font is used, which only covers Latin-1 characters.
