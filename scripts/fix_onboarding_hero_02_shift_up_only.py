#!/usr/bin/env python3
"""OB_02: shift hero up only (crop top letterbox), keep horizontal L/R unchanged.

Current imageset has ~118pt top band; target ~69pt (same as OB_03–06) without re-centering zone.
Verified: crop 49px preserves content bbox L=12, R=380.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

IOS = Path(__file__).resolve().parents[1]
HERO = IOS / "Resources" / "HeroAssets"
IMAGESET = IOS / "Assets.xcassets" / "OnboardingHero_02.imageset" / "OnboardingHero_02.png"
W, H = 393, 852
TOP_TRIM = 49  # 118 -> 69


def shift_up_only(src: Path) -> Image.Image:
    with Image.open(src) as im:
        im = im.convert("RGB")
        if im.size != (W, H):
            raise SystemExit(f"expected {W}x{H}, got {im.size}")
        bg = im.getpixel((0, 0))
        out = Image.new("RGB", (W, H), bg)
        out.paste(im.crop((0, TOP_TRIM, W, H)), (0, 0))
        return out


def main() -> None:
    src = IMAGESET if IMAGESET.exists() else HERO / "OnboardingHero_02.png"
    if not src.exists():
        raise SystemExit(f"missing source: {src}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = HERO / f"OnboardingHero_02_OLD_letterbox_{stamp}.png"
    shutil.copy2(src, backup)
    print(f"backup -> {backup}")

    frame = shift_up_only(src)
    master = HERO / "OnboardingHero_02.png"
    master.parent.mkdir(parents=True, exist_ok=True)
    frame.save(master, "PNG", optimize=True)
    IMAGESET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, IMAGESET)
    print(f"OK OnboardingHero_02 {W}x{H} top_trim={TOP_TRIM} -> {master} + imageset")


if __name__ == "__main__":
    main()
