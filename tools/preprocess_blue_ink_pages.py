#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError as exc:  # pragma: no cover - runtime guard
    raise SystemExit(
        "This helper requires Pillow. Install it in the Python environment used "
        "to run this script:\n"
        "python3 -m pip install pillow"
    ) from exc


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preprocess photographed exercise pages to suppress blue handwritten "
            "annotations before OCR."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input image paths, in page order. HEIC inputs are converted through sips.",
    )
    parser.add_argument(
        "--output-pdf",
        required=True,
        help="Path to the combined cleaned PDF.",
    )
    parser.add_argument(
        "--images-dir",
        help="Optional directory for the cleaned per-page images.",
    )
    parser.add_argument(
        "--mode",
        choices=["red-grayscale", "blue-mask-red"],
        default="red-grayscale",
        help=(
            "Cleaning strategy. `red-grayscale` keeps only the red channel, which tends "
            "to fade blue ink. `blue-mask-red` first whites blue-dominant pixels, then "
            "keeps the red channel."
        ),
    )
    parser.add_argument(
        "--blue-red-margin",
        type=int,
        default=22,
        help="How much bluer than red a pixel must be before masking in blue-mask-red mode.",
    )
    parser.add_argument(
        "--blue-green-margin",
        type=int,
        default=12,
        help="How much bluer than green a pixel must be before masking in blue-mask-red mode.",
    )
    parser.add_argument(
        "--blue-min",
        type=int,
        default=70,
        help="Minimum blue value for masking in blue-mask-red mode.",
    )
    parser.add_argument(
        "--autocontrast-cutoff",
        type=float,
        default=1.0,
        help="Percent cutoff passed to Pillow autocontrast on the cleaned grayscale page.",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=95,
        help="JPEG quality for cleaned page images.",
    )
    return parser


def build_output_path(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def convert_heic_if_needed(path: Path, temp_dir: Path) -> Path:
    if path.suffix.lower() not in {".heic", ".heif"}:
        return path
    if not shutil.which("sips"):
        raise SystemExit("HEIC input requires macOS `sips`, but it was not found.")
    out_path = temp_dir / f"{path.stem}.jpg"
    completed = subprocess.run(
        ["sips", "-s", "format", "jpeg", str(path), "--out", str(out_path)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "unknown sips error"
        raise SystemExit(f"Failed to convert {path.name} via sips: {message}")
    return out_path


def clean_page(
    image: Image.Image,
    *,
    mode: str,
    blue_red_margin: int,
    blue_green_margin: int,
    blue_min: int,
    autocontrast_cutoff: float,
) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    r, g, b = image.split()

    if mode == "red-grayscale":
        cleaned = r
    else:
        mask = Image.new("L", image.size, 0)
        src = image.load()
        dst = mask.load()
        for y in range(image.height):
            for x in range(image.width):
                rr, gg, bb = src[x, y]
                if bb > rr + blue_red_margin and bb > gg + blue_green_margin and bb > blue_min:
                    dst[x, y] = 255
        cleaned = Image.composite(Image.new("L", image.size, 255), r, mask)

    cleaned = ImageOps.autocontrast(cleaned, cutoff=autocontrast_cutoff)
    return Image.merge("RGB", (cleaned, cleaned, cleaned))


def save_cleaned_pdf(page_paths: list[Path], output_pdf: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in page_paths]
    if not images:
        raise SystemExit("No cleaned pages were produced.")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    first, *rest = images
    first.save(output_pdf, save_all=True, append_images=rest, resolution=300.0)
    for image in images:
        image.close()


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()

    output_pdf = build_output_path(args.output_pdf)
    images_dir = (
        build_output_path(args.images_dir)
        if args.images_dir
        else output_pdf.with_suffix("")
    )
    images_dir.mkdir(parents=True, exist_ok=True)

    input_paths = [build_output_path(item) for item in args.inputs]
    for path in input_paths:
        if not path.exists():
            parser.error(f"Input not found: {path}")

    cleaned_paths: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="blue_ink_clean_") as temp_str:
        temp_dir = Path(temp_str)
        for index, path in enumerate(input_paths, start=1):
            source_path = convert_heic_if_needed(path, temp_dir)
            with Image.open(source_path) as image:
                cleaned = clean_page(
                    image,
                    mode=args.mode,
                    blue_red_margin=args.blue_red_margin,
                    blue_green_margin=args.blue_green_margin,
                    blue_min=args.blue_min,
                    autocontrast_cutoff=args.autocontrast_cutoff,
                )
                page_out = images_dir / f"{index:02d}_{path.stem}.jpg"
                cleaned.save(page_out, quality=args.jpeg_quality)
                cleaned_paths.append(page_out)

    save_cleaned_pdf(cleaned_paths, output_pdf)
    print(f"Wrote cleaned PDF: {output_pdf}")
    print(f"Wrote cleaned page images to: {images_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
