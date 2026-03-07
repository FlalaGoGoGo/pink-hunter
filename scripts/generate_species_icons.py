#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "public" / "assets" / "guide" / "species"
OUTPUT_DIR = ROOT / "public" / "assets" / "guide" / "species-icons"
OUTPUT_SIZE = 256
PADDING_RATIO = 0.08

SPECIES_FILES = {
    "cherry": "cherry-blossom.png",
    "plum": "plum-blossom.png",
    "peach": "peach-blossom.png",
    "magnolia": "magnolia-blossom.png",
    "crabapple": "crabapple-blossom.png",
}


def build_icon(source_path: Path, output_path: Path) -> None:
    image = Image.open(source_path).convert("RGBA")
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"No non-transparent pixels found in {source_path}")

    cropped = image.crop(bbox)
    cropped_width, cropped_height = cropped.size
    padded_max = int(max(cropped_width, cropped_height) * (1 + PADDING_RATIO * 2))
    square_size = max(cropped_width, cropped_height, padded_max)

    canvas = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
    offset_x = (square_size - cropped_width) // 2
    offset_y = (square_size - cropped_height) // 2
    canvas.alpha_composite(cropped, (offset_x, offset_y))

    icon = canvas.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    icon.save(output_path)


def main() -> int:
    for species, filename in SPECIES_FILES.items():
        source_path = SOURCE_DIR / filename
        output_path = OUTPUT_DIR / f"{species}-icon.png"
        build_icon(source_path, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
