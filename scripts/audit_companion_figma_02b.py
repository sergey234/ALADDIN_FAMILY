#!/usr/bin/env python3
"""HERO-3-02b — live audit Companion-Heroes via Figma REST API.

Requires Personal Access Token (never account password):
  https://www.figma.com/developers/api#access-tokens

Usage:
  export FIGMA_ACCESS_TOKEN='figd_...'
  python3 scripts/audit_companion_figma_02b.py

Or add to docs/FIGMA_COMPANION.env (do NOT commit token):
  FIGMA_ACCESS_TOKEN=figd_...
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / "docs" / "FIGMA_COMPANION.env"
FILE_KEY = "vwKcGPUUEZjgayEHNn0BJM"
EXPECTED_PAGES = ("01_Unicorn", "02_Aladdin_Human", "03_Genie")
EXPECTED_EMOTIONS = (
    "idle",
    "listening",
    "thinking",
    "happy",
    "playful",
    "sad",
    "comfort",
    "celebrate",
    "curious",
    "nostalgic",
    "excited",
    "alert",
)
FRAME_W, FRAME_H = 360, 480


def load_token() -> str:
    token = os.environ.get("FIGMA_ACCESS_TOKEN", "").strip()
    if token:
        return token
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("FIGMA_ACCESS_TOKEN="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def figma_get(path: str, token: str) -> dict:
    url = f"https://api.figma.com/v1{path}"
    req = urllib.request.Request(
        url,
        headers={"X-Figma-Token": token},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def node_size(node: dict) -> tuple[float, float] | None:
    box = node.get("absoluteBoundingBox")
    if not box:
        return None
    return (round(box.get("width", 0), 1), round(box.get("height", 0), 1))


def walk(node: dict):
    yield node
    for child in node.get("children") or []:
        yield from walk(child)


def emotion_name_from_frame(name: str) -> str | None:
    # unicorn/emotion/happy, genie/emotion/idle, aladdin/emotion/sad
    m = re.search(r"/emotion/([a-z_]+)$", name)
    if m:
        return m.group(1)
    if name in EXPECTED_EMOTIONS:
        return name
    return None


def audit_page(page: dict) -> dict:
    frames: list[dict] = []
    for node in walk(page):
        if node.get("type") != "FRAME":
            continue
        name = node.get("name", "")
        emo = emotion_name_from_frame(name)
        if not emo and "emotion" not in name.lower():
            continue
        size = node_size(node)
        frames.append(
            {
                "name": name,
                "emotion": emo,
                "size": size,
                "id": node.get("id"),
            }
        )

    by_emo: dict[str, list] = {}
    for f in frames:
        if f["emotion"]:
            by_emo.setdefault(f["emotion"], []).append(f)

    size_ok = [f for f in frames if f["size"] == (FRAME_W, FRAME_H)]
    return {
        "page": page.get("name"),
        "frame_count": len(frames),
        "size_ok_count": len(size_ok),
        "emotions_found": sorted(by_emo.keys()),
        "missing_emotions": sorted(set(EXPECTED_EMOTIONS) - set(by_emo.keys())),
        "extra_emotions": sorted(set(by_emo.keys()) - set(EXPECTED_EMOTIONS)),
        "samples": frames[:3],
    }


def main() -> int:
    token = load_token()
    if not token:
        print(
            "ERROR: FIGMA_ACCESS_TOKEN not set.\n"
            "1) Figma → Settings → Security → Personal access tokens → Create\n"
            f"2) Add to {ENV_FILE} or: export FIGMA_ACCESS_TOKEN='figd_...'\n"
            "Never put account password in chat or repo.",
            file=sys.stderr,
        )
        return 2

    try:
        file_json = figma_get(f"/files/{FILE_KEY}?depth=2", token)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"ERROR: Figma API {e.code}: {body}", file=sys.stderr)
        return 1

    pages = {p["name"]: p for p in file_json.get("document", {}).get("children") or []}
    print(f"File: Companion-Heroes ({FILE_KEY})")
    print(f"Last modified: {file_json.get('lastModified', '?')}\n")

    total_frames = 0
    all_pass = True
    for page_name in EXPECTED_PAGES:
        page = pages.get(page_name)
        if not page:
            print(f"FAIL: page missing: {page_name}")
            all_pass = False
            continue
        # deeper fetch per page
        page_id = page["id"].replace(":", "%3A")
        deep = figma_get(f"/files/{FILE_KEY}/nodes?ids={page_id}", token)
        nodes = deep.get("nodes", {})
        page_node = next(iter(nodes.values()), {}).get("document") or page
        report = audit_page(page_node)
        total_frames += report["frame_count"]
        ok = (
            report["frame_count"] >= 12
            and not report["missing_emotions"]
            and report["size_ok_count"] >= 12
        )
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"[{status}] {page_name}")
        print(f"  frames: {report['frame_count']} (360x480: {report['size_ok_count']})")
        if report["missing_emotions"]:
            print(f"  missing: {report['missing_emotions']}")
        if report["extra_emotions"]:
            print(f"  extra: {report['extra_emotions']}")
        print(f"  emotions: {len(report['emotions_found'])}/12")
        print()

    print(f"TOTAL emotion frames: {total_frames} (expected >= 36)")
    if total_frames >= 36 and all_pass:
        print("\n✅ HERO-3-02b LIVE AUDIT PASS — safe to start HERO-3-07")
        return 0
    print("\n❌ HERO-3-02b needs fixes before Rive 07")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
