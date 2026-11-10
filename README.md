# TXT-2-PDF

Convert every `.txt` file in a folder into a `.pdf` file.

## Windows .exe (no Python needed)

1. Go to the repository's **Releases** page and download `txt2pdf.exe`.
2. Either:
   - **Double-click** `txt2pdf.exe` and choose a folder in the window that opens, or
   - **Drag a folder** onto `txt2pdf.exe`, or
   - run it from a command prompt: `txt2pdf.exe C:\path\to\folder -r -o C:\pdfs`
     (same options as below).

The PDFs are saved next to the `.txt` files. Windows SmartScreen may warn about
an unrecognised app the first time; click **More info → Run anyway**.

To build a new release, either push a tag such as `v1.0.1`, or open the
**Actions** tab, pick **Build Windows exe → Run workflow**, and enter a version.
The workflow builds the exe, smoke-tests it, and attaches it to the release.

## Running with Python

### Setup

```bash
pip install -r requirements.txt
```

### Usage

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
