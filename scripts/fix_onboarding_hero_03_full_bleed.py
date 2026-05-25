#!/usr/bin/env python3
"""OB_03 full-bleed like OB_02: content width ~369, L/R≈12, top≈70, hands in frame.

Rebuild 393×852 PNG from zone, then iOS uses scaledToFill + zoom 1.09 (same as OB_02).
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
TARGET_CONTENT_W = 369  # OB_02 bbox width
TARGET_TOP = 70
PASTE_X = 12  # OB_02 L margin
BG = (10, 17, 40)  # #0a1128 — match Figma frame + iOS onboardingFigmaCanvasBG


def _tight_content_bbox(im: Image.Image, bg: tuple[int, int, int] = BG, tol: int = 18) -> tuple[int, int, int, int]:
    rgb = im.convert("RGB")
    px = rgb.load()
    w, h = rgb.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg[0]) > tol or abs(g - bg[1]) > tol or abs(b - bg[2]) > tol:
                xs.append(x)
                ys.append(y)
    if not xs:
        return 0, 0, w - 1, h - 1
    return min(xs), min(ys), max(xs), max(ys)


def build_ob03_full_bleed(zone_path: Path) -> Image.Image:
    with Image.open(zone_path) as zone:
        zone = zone.convert("RGBA")
    l, t, r, b = _tight_content_bbox(zone)
    crop = zone.crop((l, t, r + 1, b + 1))
    cw, ch = crop.size
    scale = TARGET_CONTENT_W / cw
    nw, nh = int(cw * scale), int(ch * scale)
    scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    x = PASTE_X if nw >= TARGET_CONTENT_W - 2 else (W - nw) // 2
    canvas.paste(scaled, (x, TARGET_TOP), scaled)
    return canvas


def bbox_report(im: Image.Image) -> tuple[int, int, int, int]:
    im = im.convert("RGB")
    px = im.load()
    bg = BG
    tol = 12
    xs, ys = [], []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            if abs(r - bg[0]) > tol or abs(g - bg[1]) > tol or abs(b - bg[2]) > tol:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def main() -> None:
    zone = HERO / "OnboardingHero_03_figma_zone_361x460.png"
    if not zone.exists():
        raise SystemExit(f"missing zone: {zone}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for src in (IMAGESET, HERO / "OnboardingHero_03.png"):
        if src.exists():
            shutil.copy2(src, HERO / f"OnboardingHero_03_BEFORE_FULL_BLEED_{stamp}.png")
            break

    frame = build_ob03_full_bleed(zone)
    l, t, r, b = bbox_report(frame)
    print(f"bbox L={l} R={r} top={t} w={r - l + 1} (target L={PASTE_X} w={TARGET_CONTENT_W} top={TARGET_TOP})")

    master = HERO / "OnboardingHero_03.png"
    frame.save(master, "PNG", optimize=True)
    IMAGESET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, IMAGESET)
    print(f"OK OB_03 full-bleed -> {IMAGESET}")


if __name__ == "__main__":
    main()
