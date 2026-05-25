#!/usr/bin/env python3
"""Build OnboardingHero_00…07.imageset PNGs (393×852) for Xcode batch."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

IOS = Path(__file__).resolve().parents[1]
HERO = IOS / "Resources" / "HeroAssets"
XCASSETS = IOS / "Assets.xcassets"
W, H = 393, 852
ZONE_XY = (16, 24)
# OB_03: zone was too narrow (~31pt margins); scale slot + lower paste → L/R=16, top=70 (see fix_onboarding_hero_03_hands_sync.py)
OB_03_ZONE_SCALE = 1.10
OB_03_ZONE_OY = 42
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

    # Already full-screen portrait (OB_03 always recomposes from zone — hands/margins recipe)
    if mw == W and mh == H and n != 3:
        return Image.open(master).convert("RGB")

    # Cosmic / tall masters: composite pre-built zone (background baked in)
    if zone.exists():
        bg = COSMIC_BG if n >= 4 else (20, 25, 45)
        canvas = Image.new("RGB", (W, H), bg)
        with Image.open(zone) as z:
            z = z.convert("RGBA")
            if n == 3:
                nw, nh = int(361 * OB_03_ZONE_SCALE), int(460 * OB_03_ZONE_SCALE)
                scaled = z.resize((nw, nh), Image.Resampling.LANCZOS)
                slot = Image.new("RGBA", (361, 460), (0, 0, 0, 0))
                slot.paste(scaled, ((361 - nw) // 2, (460 - nh) // 2), scaled)
                canvas.paste(slot, (ZONE_XY[0], OB_03_ZONE_OY), slot)
            else:
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


def write_imageset(n: int, frame: Image.Image, *, master_path: Path | None = None) -> Path:
    nn = f"{n:02d}"
    name = f"OnboardingHero_{nn}"
    out_dir = XCASSETS / f"{name}.imageset"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{name}.png"
    # Keep HeroAssets and imageset byte-identical when master is already 393×852 (no re-encode drift).
    if master_path is not None and master_path.exists():
        with Image.open(master_path) as im:
            if im.size == (W, H):
                shutil.copy2(master_path, png_path)
                contents = json.loads(json.dumps(CONTENTS))
                for entry in contents["images"]:
                    entry["filename"] = f"{name}.png"
                (out_dir / "Contents.json").write_text(
                    json.dumps(contents, indent=2) + "\n", encoding="utf-8"
                )
                return out_dir
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
        nn = f"{n:02d}"
        master = HERO / f"OnboardingHero_{nn}.png"
        frame = build_frame(n)
        assert frame.size == (W, H), f"OB_{n:02d}: {frame.size}"
        path = write_imageset(n, frame, master_path=master)
        out = XCASSETS / f"OnboardingHero_{nn}.imageset" / f"OnboardingHero_{nn}.png"
        if master.exists() and out.exists():
            same = hashlib.md5(master.read_bytes()).hexdigest() == hashlib.md5(out.read_bytes()).hexdigest()
            print(f"OK {path.name} -> {frame.size[0]}x{frame.size[1]} md5_match={same}")
        else:
            print(f"OK {path.name} -> {frame.size[0]}x{frame.size[1]}")


if __name__ == "__main__":
    main()
