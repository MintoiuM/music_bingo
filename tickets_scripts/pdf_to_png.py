#!/usr/bin/env python3
"""
Extract every page of a PDF into separate PNG images.
"""

import argparse
from pathlib import Path

import fitz  # PyMuPDF


def pdf_to_png(pdf_path: str, output_dir: str | None = None, dpi: int = 150) -> list[str]:
    """
    Extract each page of a PDF as a PNG file.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory for output PNGs. Defaults to "template" folder next to the PDF.
        dpi: Resolution for rendering (default 150). Higher = larger file size.

    Returns:
        List of paths to the created PNG files.
    """
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    out_dir = Path(output_dir).resolve() if output_dir else pdf_path.parent / "template"
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = pdf_path.stem
    created = []

    doc = fitz.open(pdf_path)
    try:
        for i in range(len(doc)):
            page = doc[i]
            # zoom for desired DPI (72 is default PDF resolution)
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_path = out_dir / f"{stem}_page_{i + 1:04d}.png"
            pix.save(str(out_path))
            created.append(str(out_path))
    finally:
        doc.close()

    return created


def _resolve_pdf_path(pdf_arg: str) -> Path:
    """Resolve PDF path: use as-is if it exists, else look in project sources folder."""
    p = Path(pdf_arg)
    if p.exists():
        return p.resolve()
    # Project root: parent of directory containing this script (apps/ -> project root)
    project_root = Path(__file__).resolve().parent.parent
    sources_dir = project_root / "sources"
    candidate = sources_dir / p.name
    if candidate.exists():
        return candidate.resolve()
    return p.resolve()  # return original for a clear FileNotFoundError from pdf_to_png


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract every PDF page as a PNG image.")
    parser.add_argument("pdf", help="Path to the PDF file (or filename; will be looked up in sources/)")
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output directory for PNGs (default: template folder)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Resolution in DPI (default: 150)",
    )
    args = parser.parse_args()

    pdf_path = _resolve_pdf_path(args.pdf)
    try:
        paths = pdf_to_png(str(pdf_path), args.output_dir, args.dpi)
        print(f"Created {len(paths)} PNG(s):")
        for p in paths:
            print(f"  {p}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
