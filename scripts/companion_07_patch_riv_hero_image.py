#!/usr/bin/env python3
"""HERO-3-07 — swap embedded 360×480 PNG inside production .riv (SM unchanged).

Copies template .riv (unicorn) and replaces the single embedded PNG with hero master art.
Does not replace State Machine / triggers — only raster inside the file.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "Resources" / "Companion"
ASSETS = ROOT / "docs" / "assets"

PNG_SIG = b"\x89PNG\r\n\x1a\n"

HEROES = {
    "aladdin": {
        "template": COMPANION / "unicorn.riv",
        "png": ASSETS / "aladdin_master_OB01_crop_360x480.png",
        "out": COMPANION / "aladdin.riv",
        "label_renames": (
            (b"unicorn_master_crop_360x480", b"aladdin_master_crop_360x480"),
            (b"unicorn_master", b"aladdin_master"),
        ),
    },
    "genie": {
        "template": COMPANION / "unicorn.riv",
        "png": ASSETS / "onboarding_OB03_APP_360x480_FILL_headfix_v1.png",
        "out": COMPANION / "genie.riv",
        "label_renames": (
            (b"unicorn_master_crop_360x480", b"genie_master_crop_360x480"),
            (b"unicorn_master", b"genie_master"),
        ),
    },
}


def extract_png(data: bytes, offset: int) -> bytes:
    pos = offset + 8
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        pos += 8 + length + 4
        if ctype == b"IEND":
            return data[offset:pos]
    raise ValueError("PNG IEND not found")


def load_png(path: Path) -> bytes:
    raw = path.read_bytes()
    if not raw.startswith(PNG_SIG):
        raise ValueError(f"Not a PNG: {path}")
    w = struct.unpack(">I", raw[16:20])[0]
    h = struct.unpack(">I", raw[20:24])[0]
    if (w, h) != (360, 480):
        raise ValueError(f"{path.name}: expected 360×480, got {w}×{h}")
    return raw


def patch_riv(template: bytes, png: bytes, renames: tuple[tuple[bytes, bytes], ...]) -> bytes:
    off = template.find(PNG_SIG)
    if off < 0:
        raise ValueError("No embedded PNG in template .riv")
    old_png = extract_png(template, off)
    out = template[:off] + png + template[off + len(old_png) :]
    for old, new in renames:
        if old not in out:
            raise ValueError(f"Missing label {old!r} in template")
        if len(new) > len(old):
            raise ValueError(f"Label {new!r} longer than {old!r} — unsafe patch")
        padded = new + b"\x00" * (len(old) - len(new))
        out = out.replace(old, padded, 1)
    for name in (b"HeroSM", b"mouth_open", b"idle", b"listening", b"speaking"):
        if name not in out:
            raise ValueError(f"Missing SM marker {name!r} after patch")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch hero PNG into .riv from unicorn template.")
    parser.add_argument("hero", choices=sorted(HEROES.keys()), help="aladdin | genie")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write")
    args = parser.parse_args()
    spec = HEROES[args.hero]

    template = spec["template"].read_bytes()
    png = load_png(spec["png"])
    patched = patch_riv(template, png, spec["label_renames"])

    print(f"template: {spec['template'].name} ({len(template)} bytes)")
    print(f"png: {spec['png'].name} ({len(png)} bytes)")
    print(f"output: {spec['out'].name} ({len(patched)} bytes)")

    if args.dry_run:
        print("DRY RUN — not written")
        return 0

    backup = spec["out"].with_suffix(".riv.placeholder.bak")
    if spec["out"].exists():
        backup.write_bytes(spec["out"].read_bytes())
        print(f"backup: {backup.name}")

    spec["out"].write_bytes(patched)
    print(f"OK: wrote {spec['out']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
