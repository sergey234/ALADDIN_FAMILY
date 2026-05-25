#!/usr/bin/env python3
"""App Store icon v2: WORDMARK V2 (2×) + genie OB_07 · variants navy | legacy_blue.

legacy_blue — фон = May 10 backup (голубой royal blue + кольца/точки), V2 wordmark + джин OB_07.
navy — тёмный radial (новая иконка 08, канон Xcode).
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

IOS = Path(__file__).resolve().parents[1]
ICONSET = IOS / "Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.png"
HERO = IOS / "Resources/HeroAssets/OnboardingHero_07.png"
WORDMARK = IOS / "Resources/BrandAssets/ALADDIN_AI_V2_Logo/WORDMARK_V2_transparent_figma_1x.png"
MAY10_ICON = (
    IOS
    / "NEW_BACKUP_ALADDIN_20260510_120835/Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.png"
)
EXPORT_DIR = IOS / "Resources/FigmaExports"
HERO_ASSETS = IOS / "Resources/HeroAssets"
W = H = 1024

# Navy v2 (тёмный центр — текущий)
BG_NAVY_TOP = (18, 42, 98)
BG_NAVY_BOTTOM = (8, 14, 36)

HEAD_CX, HEAD_CY, HEAD_CROP = 198, 128, 148
GENIE_DIAMETER = 520
GENIE_CY = 575  # центр круга джина (как на 08)
# May 10 backup: зоны старого контента (единорог, тексты, угловые глифы)
MAY10_WORDMARK_BOX = (70, 110, 954, 248)
MAY10_UNICORN_CENTER = (512, 512)
MAY10_UNICORN_RADIUS = 272
MAY10_SUBTITLE_BOX = (280, 730, 1020, 910)
MAY10_SIRIUS_BOX = (60, 890, 964, 1010)
MAY10_CORNER_BOXES = ((0, 0, 88, 88), (936, 0, 1024, 88), (0, 936, 88, 1024), (936, 936, 1024, 1024))
MAY10_GENIE_ERASE_RADIUS = 268


def _radial_navy() -> Image.Image:
    base = Image.new("RGB", (W, H), BG_NAVY_BOTTOM)
    draw = ImageDraw.Draw(base)
    for i in range(W // 2, 0, -2):
        t = i / (W / 2)
        r = int(BG_NAVY_TOP[0] * (1 - t) + BG_NAVY_BOTTOM[0] * t)
        g = int(BG_NAVY_TOP[1] * (1 - t) + BG_NAVY_BOTTOM[1] * t)
        b = int(BG_NAVY_TOP[2] * (1 - t) + BG_NAVY_BOTTOM[2] * t)
        draw.ellipse((W // 2 - i, H // 2 - i - 40, W // 2 + i, H // 2 + i - 40), fill=(r, g, b))
    return base


def _scaled_wordmark(wm: Image.Image) -> tuple[Image.Image, int, int]:
    target_w = 880
    scale = target_w / wm.width
    nw, nh = int(wm.width * scale), int(wm.height * scale)
    wm_scaled = wm.resize((nw, nh), Image.Resampling.LANCZOS)
    return wm_scaled, (W - nw) // 2, 44


def _genie_paste_xy(head: Image.Image) -> tuple[int, int]:
    return W // 2 - head.width // 2, GENIE_CY - head.height // 2


def _may10_erase_mask() -> Image.Image:
    """Inpaint только под старый контент May 10 — фон вне маски = бэкап 1:1."""
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(MAY10_WORDMARK_BOX, fill=255)
    draw.rectangle(MAY10_SUBTITLE_BOX, fill=255)
    draw.rectangle(MAY10_SIRIUS_BOX, fill=255)
    for box in MAY10_CORNER_BOXES:
        draw.rectangle(box, fill=255)
    ux, uy = MAY10_UNICORN_CENTER
    ur = MAY10_UNICORN_RADIUS
    draw.ellipse((ux - ur, uy - ur, ux + ur, uy + ur), fill=255)
    gx, gy = W // 2, GENIE_CY
    gr = MAY10_GENIE_ERASE_RADIUS
    draw.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=6))


def _legacy_canvas_exact_backup(hero: Image.Image, wm: Image.Image) -> Image.Image:
    """09: фон May 10 backup; inpaint старый контент; сверху V2 + джин OB_07 (как 08)."""
    if not MAY10_ICON.exists():
        raise SystemExit(f"missing May 10 icon: {MAY10_ICON}")
    backup = Image.open(MAY10_ICON).convert("RGB")
    head = _circular_genie_head(hero)
    wm_scaled, wm_x, wm_y = _scaled_wordmark(wm)
    hx, hy = _genie_paste_xy(head)

    erase = _may10_erase_mask()
    inpaint = backup.filter(ImageFilter.GaussianBlur(radius=72))
    bg = Image.composite(inpaint, backup, erase)

    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fg.paste(head, (hx, hy), head)
    fg.paste(wm_scaled, (wm_x, wm_y), wm_scaled)
    return Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")


def _legacy_bg_from_old_icon() -> Image.Image:
    """Background layer only (May 10)."""
    if not MAY10_ICON.exists():
        raise SystemExit(f"missing May 10 icon: {MAY10_ICON}")
    backup = Image.open(MAY10_ICON).convert("RGB")
    erase = _may10_erase_mask()
    inpaint = backup.filter(ImageFilter.GaussianBlur(radius=72))
    return Image.composite(inpaint, backup, erase)


def _rings(canvas: Image.Image, cx: int, cy: int, radius: int, bright: bool) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if bright:
        strokes = ((1, 114, 227, 45), (26, 68, 158, 55), (10, 80, 200, 65), (80, 160, 255, 40))
    else:
        strokes = ((80, 160, 255, 28), (80, 160, 255, 38), (80, 160, 255, 48), (80, 160, 255, 58))
    for i, rgba in enumerate(strokes):
        r = radius + i * 26
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=rgba, width=3)
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB"))


def _circular_genie_head(hero: Image.Image) -> Image.Image:
    l = HEAD_CX - HEAD_CROP // 2
    t = HEAD_CY - HEAD_CROP // 2
    crop = hero.crop((l, t, l + HEAD_CROP, t + HEAD_CROP)).convert("RGBA")
    diameter = GENIE_DIAMETER
    crop = crop.resize((diameter, diameter), Image.Resampling.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    out.paste(crop, (0, 0), mask)
    return out


def _paste_wordmark(canvas: Image.Image, wm: Image.Image) -> None:
    wm_scaled, x, y = _scaled_wordmark(wm)
    canvas.paste(wm_scaled, (x, y), wm_scaled)


def build_icon(variant: str) -> Image.Image:
    hero = Image.open(HERO).convert("RGB")
    wm = Image.open(WORDMARK).convert("RGBA")
    if variant == "legacy_blue":
        return _legacy_canvas_exact_backup(hero, wm)

    canvas = _radial_navy()
    _rings(canvas, W // 2, GENIE_CY - 30, 235, bright=False)
    head = _circular_genie_head(hero)
    canvas.paste(head, _genie_paste_xy(head), head)
    _paste_wordmark(canvas, wm)
    return canvas


def _color_report(im: Image.Image, label: str) -> None:
    px = im.load()
    pts = [(100, 100), (512, 350), (512, 512), (512, 80)]
    print(f"  {label}:")
    for p in pts:
        print(f"    {p} -> {px[p[0], p[1]]}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--variant",
        choices=("navy", "legacy_blue", "both"),
        default="both",
        help="navy=08 тёмный v2, legacy_blue=09 May10 голубой фон",
    )
    parser.add_argument("--xcode", action="store_true", help="Write variant to AppIcon.appiconset")
    parser.add_argument(
        "--xcode-variant",
        choices=("navy", "legacy_blue"),
        default="navy",
        help="Which variant to install with --xcode or default both-run (default navy)",
    )
    args = parser.parse_args()
    variants = ["navy", "legacy_blue"] if args.variant == "both" else [args.variant]

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    for v in variants:
        icon = build_icon(v)
        out = EXPORT_DIR / f"APP_AppStoreIcon_ALADDIN_1024_v2_{v}.png"
        master = HERO_ASSETS / f"AppIcon_ALADDIN_1024_v2_{v}.png"
        icon.save(out, "PNG", optimize=True)
        shutil.copy2(out, master)
        paths[v] = out
        _color_report(icon, v)
        print(f"OK {v} -> {out}")

    install = args.xcode or args.variant in ("navy", "both")
    if install:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if ICONSET.exists():
            shutil.copy2(ICONSET, ICONSET.parent / f"ALADDIN_icon_1024_BEFORE_{stamp}.png")
        chosen = args.xcode_variant if args.xcode else "navy"
        if chosen not in paths:
            chosen = variants[0]
        shutil.copy2(paths[chosen], ICONSET)
        icon = Image.open(ICONSET).convert("RGB")
        for s in (20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180):
            icon.resize((s, s), Image.Resampling.LANCZOS).save(
                ICONSET.parent / f"ALADDIN_icon_{s}.jpg", "JPEG", quality=92, optimize=True
            )
        icon.resize((1024, 1024), Image.Resampling.LANCZOS).save(
            ICONSET.parent / "ALADDIN_icon_1024.jpg", "JPEG", quality=92, optimize=True
        )
        print(f"OK xcode AppIcon -> {ICONSET} ({chosen})")


if __name__ == "__main__":
    main()
