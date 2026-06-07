#!/usr/bin/env python3
"""Export 36 Companion emotion frames (360×480) from Figma → PNG for Rive 07.

Requires FIGMA_ACCESS_TOKEN (see docs/FIGMA_COMPANION.env).

After export, run companion_07_check_emotion_png_uniqueness.py — production needs
12 unique faces per hero (02b v2), not 12 duplicate masters (02b v1.1).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "docs" / "companion_figma_emotion_manifest.json"
ENV_FILE = REPO / "docs" / "FIGMA_COMPANION.env"
OUT_ROOT = REPO / "Resources" / "Companion" / "figma_exports"


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
    req = urllib.request.Request(
        f"https://api.figma.com/v1{path}",
        headers={"X-Figma-Token": token},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        dest.write_bytes(resp.read())


def main() -> int:
    token = load_token()
    if not token:
        print(
            "ERROR: set FIGMA_ACCESS_TOKEN in docs/FIGMA_COMPANION.env\n"
            "Figma → Settings → Security → Personal access tokens",
            file=sys.stderr,
        )
        return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    file_key = manifest["fileKey"]
    ids: list[str] = []
    paths: dict[str, Path] = {}

    for hero, spec in manifest["heroes"].items():
        for emo, node_id in spec["frames"].items():
            fid = node_id.replace("-", ":")
            ids.append(fid)
            paths[fid] = OUT_ROOT / hero / f"{emo}.png"

    # Figma Images API batches ids
    batch_size = 50
    id_to_url: dict[str, str] = {}
    for i in range(0, len(ids), batch_size):
        chunk = ids[i : i + batch_size]
        query = ",".join(chunk)
        data = figma_get(
            f"/images/{file_key}?ids={query}&format=png&scale=1",
            token,
        )
        id_to_url.update(data.get("images") or {})
        time.sleep(0.3)

    failed = 0
    for fid, dest in paths.items():
        url = id_to_url.get(fid)
        if not url:
            print(f"SKIP no URL: {dest.relative_to(REPO)} ({fid})")
            failed += 1
            continue
        download(url, dest)
        print(f"OK {dest.relative_to(REPO)} ({dest.stat().st_size} bytes)")

    print(f"\nExported to {OUT_ROOT.relative_to(REPO)}")
    print("Next: python3 scripts/companion_07_check_emotion_png_uniqueness.py")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
