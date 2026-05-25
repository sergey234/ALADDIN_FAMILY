#!/usr/bin/env python3
"""OB_03: widen hero to L/R=16 (hands visible) and top=70 — match OB_04 / Figma.

Root cause: zone was ~31pt side margins; iOS zoom 1.09 + scaledToFill clipped hands.
Fix: scale zone 1.10 in 361×460 slot, paste @ (16, 42) → bbox L=16 R=376 top=70.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

IOS = Path(__file__).resolve().parents[1]
HERO = IOS / "Resources" / "HeroAssets"
IMAGESET = IOS / "Assets.xcassets" / "OnboardingHero_03.imageset" / "OnboardingHero_03.png"
W, H = 393, 852
ZONE_X = 16
ZONE_SCALE = 1.10
ZONE_OY = 42  # (16, 42) on canvas; top content y=70
BG = (20, 25, 45)


def build_ob03_frame(zone_path: Path) -> Image.Image:
    with Image.open(zone_path) as zone:
        zone = zone.convert("RGBA")
    nw, nh = int(361 * ZONE_SCALE), int(460 * ZONE_SCALE)
    scaled = zone.resize((nw, nh), Image.Resampling.LANCZOS)
    slot = Image.new("RGBA", (361, 460), (0, 0, 0, 0))
    slot.paste(scaled, ((361 - nw) // 2, (460 - nh) // 2), scaled)
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(slot, (ZONE_X, ZONE_OY), slot)
    return canvas


def main() -> None:
    zone = HERO / "OnboardingHero_03_figma_zone_361x460.png"
    if not zone.exists():
        raise SystemExit(f"missing zone: {zone}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for src in (IMAGESET, HERO / "OnboardingHero_03.png"):
        if src.exists():
            shutil.copy2(src, HERO / f"OnboardingHero_03_BEFORE_HANDS_{stamp}.png")
            break

    frame = build_ob03_frame(zone)
    master = HERO / "OnboardingHero_03.png"
    frame.save(master, "PNG", optimize=True)
    IMAGESET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, IMAGESET)
    print(f"OK OB_03 {W}x{H} zone_scale={ZONE_SCALE} paste=({ZONE_X},{ZONE_OY})")


if __name__ == "__main__":
    main()
