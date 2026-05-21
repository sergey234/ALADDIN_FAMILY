#!/usr/bin/env python3
"""Sync WORDMARK V2 transparent PNGs into Xcode imageset and FigmaExports.

Source of truth:
  Resources/BrandAssets/ALADDIN_AI_V2_Logo/WORDMARK_V2_transparent_figma_1x*.png

Figma (manual / MCP upload):
  EXPORT_WORDMARK_V2_transparent (185:53) → WORDMARK_V2_raster (185:54)
  OB_01 WORDMARK_V2 (88:53), OB_07 WORDMARK_V2 (168:53)
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "Resources/BrandAssets/ALADDIN_AI_V2_Logo"
XC = ROOT / "Assets.xcassets/OnboardingLogo_V2_Cinematic.imageset"
FIG_OB01 = ROOT / "Resources/FigmaExports/OB_01"

PAIRS = [
    ("WORDMARK_V2_transparent_figma_1x.png", "OnboardingLogo_V2_Cinematic@1x.png"),
    ("WORDMARK_V2_transparent_figma_1x@2x.png", "OnboardingLogo_V2_Cinematic@2x.png"),
    ("WORDMARK_V2_transparent_figma_1x@3x.png", "OnboardingLogo_V2_Cinematic@3x.png"),
]


def main() -> None:
    FIG_OB01.mkdir(parents=True, exist_ok=True)
    XC.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in PAIRS:
        src = BRAND / src_name
        if not src.exists():
            raise SystemExit(f"Missing source: {src}")
        shutil.copy2(src, XC / dst_name)
        shutil.copy2(src, FIG_OB01 / src_name)
        print(f"OK {src_name} -> imageset + FigmaExports/OB_01")
    print("Done. Upload WORDMARK_V2_transparent_figma_1x.png to Figma nodes 185:54, 88:53, 168:53 (FIT).")


if __name__ == "__main__":
    main()
