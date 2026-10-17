#!/usr/bin/env python3
"""Write profile UUIDs into Release PROVISIONING_PROFILE_SPECIFIER.

Xcode looks up a target-level SPECIFIER by display name. Per-target xcconfig
keys (ALADDINContentFilter_PROVISIONING_PROFILE_SPECIFIER=UUID) do not win
over a hardcoded name in project.pbxproj. The main app works because its
name ("ALADDIN AI App Store") matches the installed profile. Content Filter
and Shield Action fail because their pbx names do not.

CI must write the decoded UUID into the Release block — same path as
ALADDIN_PROVISIONING_PROFILE_SPECIFIER for the app.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

UUID_RE = re.compile(
    r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)

TARGETS = (
    ("ALADDINShieldAction", "ALADDIN_PBX_SHIELD_ACTION_UUID"),
    ("ALADDINContentFilter", "ALADDIN_PBX_CONTENT_FILTER_UUID"),
)


def _apply_uuid(text: str, target: str, uuid: str) -> str:
    marker = f'Release configuration for PBXNativeTarget "{target}"'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"FAIL: no Release config for {target}")
    settings_at = text.find("buildSettings = {", idx)
    end_at = text.find("\n\t\t\tname = Release;", settings_at)
    if settings_at < 0 or end_at < 0 or end_at <= settings_at:
        raise SystemExit(f"FAIL: Release buildSettings not found for {target}")
    block = text[settings_at:end_at]
    replacement = f'PROVISIONING_PROFILE_SPECIFIER = "{uuid}";'
    if "PROVISIONING_PROFILE_SPECIFIER" in block:
        block2, n = re.subn(
            r"PROVISIONING_PROFILE_SPECIFIER = [^;]+;",
            replacement,
            block,
            count=1,
        )
        if n != 1:
            raise SystemExit(f"FAIL: could not replace SPECIFIER for {target}")
    else:
        insert = f"\n\t\t\t\t{replacement}"
        brace = block.find("{")
        block2 = block[: brace + 1] + insert + block[brace + 1 :]
    return text[:settings_at] + block2 + text[end_at:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pbx",
        default="ALADDIN.xcodeproj/project.pbxproj",
        help="path to project.pbxproj",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pbx = Path(args.pbx)
    text = pbx.read_text(encoding="utf-8")
    applied: list[str] = []
    for target, env_key in TARGETS:
        uuid = os.environ.get(env_key, "").strip()
        if not uuid:
            print(f"skip {target}: {env_key} empty")
            continue
        if not UUID_RE.match(uuid):
            raise SystemExit(f"FAIL: {env_key} is not a UUID")
        text = _apply_uuid(text, target, uuid)
        applied.append(f"{target}={uuid}")

    if not applied:
        print("⚠️  no UUIDs applied (both env vars empty)")
        return 0

    stale_by_target = {
        "ALADDINContentFilter": "ALADDIN AI ContentFilter App Store",
        "ALADDINShieldAction": "ALADDIN AI ShieldAction App Store",
    }
    applied_names = {item.split("=", 1)[0] for item in applied}
    for target, name in stale_by_target.items():
        if target in applied_names and name in text:
            raise SystemExit(f"FAIL: stale profile name still in pbx: {name}")

    if args.dry_run:
        print("DRY-RUN OK: " + ", ".join(applied))
        return 0

    pbx.write_text(text, encoding="utf-8")
    print("✅ pbx Release SPECIFIER → UUID: " + ", ".join(applied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
