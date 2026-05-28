#!/usr/bin/env python3
"""Verify Figma ↔ iOS sync for onboarding OB_01–OB_05 (hero MD5, anchors, copy)."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

IOS = Path(__file__).resolve().parents[1]
HERO = IOS / "Resources" / "HeroAssets"
XC = IOS / "Assets.xcassets"
SWIFT = IOS / "Screens" / "14_OnboardingScreen.swift"
RU = IOS / "Resources/Localization/ru.lproj/Localizable.strings"

# Live Figma OnboardingHero_00 (2026-05-24)
FIGMA_ANCHORS = {
    0: {
        "wordmark": (17, 271, 360, 121),
        "title": (14, 450, 361, 60),
        "desc": (22, 546, 346, 66),
        "scrim": (0, 528, 393, 324),
        "scrim_max": 0.45,
        "layout": "standard",
    },
    1: {
        "title": (12, 412, 361, 78),
        "desc": (12, 494, 370, 132),
        "scrim": (0, 504, 393, 310),
        "scrim_max": 0.42,
        "layout": "standard",
    },
    2: {
        "title": (16, 552, 361, 60),
        "desc": (14, 630, 361, 80),
        "scrim": (0, 500, 393, 320),
        "scrim_max": 0.40,
        "layout": "standard",
    },
    3: {
        "title": (12, 440, 370, 60),
        "desc": (12, 522, 370, 132),
        "scrim": (0, 542, 393, 310),
        "scrim_max": 0.35,
        "layout": "standard",
    },
    4: {
        "title": (12, 440, 370, 60),
        "desc": (12, 522, 370, 144),
        "scrim": (0, 532, 393, 320),
        "scrim_max": 0.38,
        "layout": "standard",
    },
}

RU_STRINGS = {
    "onboarding_page1_title": "Защита всей семьи в кармане",
    "onboarding_page1_desc": "Комплексная система защиты от более 100 видов киберугроз",
    "onboarding_page2_title": "Ваш персональный агент безопасности",
    "onboarding_page2_desc": "ИИ охраняет вашу семью 24/7 + Многоуровневая система защита ⭐⭐⭐⭐⭐! Военные технологии шифрования",
    "onboarding_page3_title": "Родительский контроль",
    "onboarding_page3_desc": "Система обучения детей безопасности. Вы видите всю активность детей в интернете. Самообучающаяся система защиты AI",
    "onboarding_page4_title": "Аналитика рисков",
    "onboarding_page4_desc": "Система ALADDIN AI предсказывает, обнаруживает и предотвращает киберугрозы. Постоянно обучается и улучшается.",
}

ZOOM = {"01": 1.0, "02": 1.09}


def parse_swift_case(case: int) -> dict:
    text = SWIFT.read_text(encoding="utf-8")
    block = re.search(rf"case {case}:\s*\n(.*?)case \d+:|case {case}:\s*\n(.*?)default:", text, re.S)
    if not block:
        raise RuntimeError(f"case {case} not found")
    b = block.group(1) or block.group(2)
    out: dict = {}
    if m := re.search(r"wordmark: CGRect\(x: ([^,]+), y: ([^,]+), width: ([^,]+), height: ([^)]+)\)", b):
        out["wordmark"] = tuple(map(float, m.groups()))
    for key in ("title", "desc", "scrim"):
        if m := re.search(rf"{key}: CGRect\(x: ([^,]+), y: ([^,]+), width: ([^,]+), height: ([^)]+)\)", b):
            out[key] = tuple(map(float, m.groups()))
    if m := re.search(r"scrimMaxOpacity: ([0-9.]+)", b):
        out["scrim_max"] = float(m.group(1))
    if m := re.search(r"layoutMode: \.(standard|ob07Final)", b):
        out["layout"] = m.group(1)
    return out


def load_ru() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in RU.read_text(encoding="utf-8").splitlines():
        m = re.match(r'"([^"]+)"\s*=\s*"(.*)";\s*$', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def md5_match(nn: str) -> bool:
    a = HERO / f"OnboardingHero_{nn}.png"
    b = XC / f"OnboardingHero_{nn}.imageset" / f"OnboardingHero_{nn}.png"
    return hashlib.md5(a.read_bytes()).hexdigest() == hashlib.md5(b.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    ru = load_ru()

    for case in (0, 1, 2, 3, 4):
        swift = parse_swift_case(case)
        figma = FIGMA_ANCHORS[case]
        for key in ("title", "desc", "scrim"):
            if key not in swift or key not in figma:
                errors.append(f"case {case}: missing {key}")
                continue
            if tuple(swift[key]) != figma[key]:
                errors.append(f"case {case} {key}: swift {swift[key]} != figma {figma[key]}")
        if swift.get("scrim_max") != figma["scrim_max"]:
            errors.append(f"case {case} scrim_max: {swift.get('scrim_max')} != {figma['scrim_max']}")
        if swift.get("layout") != figma["layout"]:
            errors.append(f"case {case} layoutMode: {swift.get('layout')} != {figma['layout']}")
        if case == 0 and "wordmark" in figma:
            if tuple(swift.get("wordmark", ())) != figma["wordmark"]:
                errors.append(f"case 0 wordmark: {swift.get('wordmark')} != {figma['wordmark']}")

    for k, v in RU_STRINGS.items():
        if ru.get(k) != v:
            errors.append(f"RU strings {k}: mismatch")

    hero_swift = (IOS / "Shared/Components/HeroAmbientPresentation.swift").read_text(encoding="utf-8")
    for nn, z in ZOOM.items():
        if nn == "01":
            if 'case "OnboardingHero_02"' not in hero_swift:
                errors.append("zoom: OnboardingHero_02 case missing")
        if nn == "02" and "OnboardingHero_02" in hero_swift and "1.09" not in hero_swift:
            errors.append("zoom OB_02 not 1.09")
        if nn == "03":
            m_zoom = re.search(
                r"private func heroOnboardingTopZoom.*?case ([^\n]+):\s*\n\s*return 1\.09",
                hero_swift,
                re.S,
            )
            if not m_zoom or "OnboardingHero_03" not in m_zoom.group(1):
                errors.append("OB_03 must be in heroOnboardingTopZoom 1.09 switch")
            if "OnboardingHero_07" not in m_zoom.group(1) if m_zoom else True:
                errors.append("OB_07 must be in heroOnboardingTopZoom 1.09 switch")
            if "usesFigmaCanvasFit" in hero_swift:
                errors.append("usesFigmaCanvasFit removed — OB_07 uses fill+zoom like OB_03")

    for nn in ("01", "02", "03"):
        if not md5_match(nn):
            errors.append(f"MD5 mismatch OnboardingHero_{nn} HeroAssets vs imageset")

    if errors:
        print("FAIL:")
        for e in errors:
            print(" -", e)
        return 1

    print("PASS: OB_01–OB_05 Figma anchors, RU copy, hero MD5, zoom rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
