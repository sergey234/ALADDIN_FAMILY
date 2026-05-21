#!/usr/bin/env python3
"""Build OnboardingHero_00…07.imageset PNGs (393×852) for Xcode batch."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

IOS = Path(__file__).resolve().parents[1]
HERO = IOS / "Resources" / "HeroAssets"
XCASSETS = IOS / "Assets.xcassets"
W, H = 393, 852
ZONE_XY = (16, 24)
COSMIC_BG = (10, 17, 40)  # #0a1128

CONTENTS = {
    "images": [
        {"filename": None, "idiom": "universal", "scale": "1x"},
        {"filename": None, "idiom": "universal", "scale": "2x"},
        {"filename": None, "idiom": "universal", "scale": "3x"},
    ],
    "info": {"author": "xcode", "version": 1},
}


def build_frame(n: int) -> Image.Image:
    nn = f"{n:02d}"
    master = HERO / f"OnboardingHero_{nn}.png"
    zone = HERO / f"OnboardingHero_{nn}_figma_zone_361x460.png"
    if not master.exists():
        raise FileNotFoundError(master)

    with Image.open(master) as im:
        mw, mh = im.size

    # Already full-screen portrait
    if mw == W and mh == H:
        return Image.open(master).convert("RGB")

    # Cosmic / tall masters: composite pre-built zone (background baked in)
    if zone.exists():
        bg = COSMIC_BG if n >= 4 else (20, 25, 45)
        canvas = Image.new("RGB", (W, H), bg)
        with Image.open(zone) as z:
            z = z.convert("RGBA")
            canvas.paste(z, ZONE_XY, z)
        return canvas

    # Fallback: center cover crop
    with Image.open(master) as im:
        im = im.convert("RGB")
        scale = max(W / im.width, H / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        left = (nw - W) // 2
        top = (nh - H) // 2
        return im.crop((left, top, left + W, top + H))


def write_imageset(n: int, frame: Image.Image) -> Path:
    nn = f"{n:02d}"
    name = f"OnboardingHero_{nn}"
    out_dir = XCASSETS / f"{name}.imageset"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{name}.png"
    frame.save(png_path, "PNG", optimize=True)
    contents = json.loads(json.dumps(CONTENTS))
    for entry in contents["images"]:
        entry["filename"] = f"{name}.png"
    (out_dir / "Contents.json").write_text(
        json.dumps(contents, indent=2) + "\n", encoding="utf-8"
    )
    return out_dir


def main() -> None:
    for n in range(8):
        frame = build_frame(n)
        assert frame.size == (W, H), f"OB_{n:02d}: {frame.size}"
        path = write_imageset(n, frame)
        print(f"OK {path.name} -> {frame.size[0]}x{frame.size[1]}")


if __name__ == "__main__":
    main()
