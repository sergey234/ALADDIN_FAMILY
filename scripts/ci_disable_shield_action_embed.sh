#!/usr/bin/env bash
# CI fallback when PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID is missing.
set -euo pipefail

PBX="ALADDIN.xcodeproj/project.pbxproj"
if [ ! -f "$PBX" ]; then
  echo "❌ $PBX not found"
  exit 1
fi

cp "$PBX" "${PBX}.bak_shieldaction"

python3 <<'PY'
from pathlib import Path

path = Path("ALADDIN.xcodeproj/project.pbxproj")
text = path.read_text()
removals = [
    "\t\t\t\tSTACT0112F90000200C7D34B /* ALADDINShieldAction.appex in Embed App Extensions */,\n",
    "\t\t\t\tSTACT0132F90000200C7D34B /* PBXTargetDependency */,\n",
]
removed = 0
for block in removals:
    if block in text:
        text = text.replace(block, "", 1)
        removed += 1
    else:
        print(f"⚠️  block not present (ok if already absent): {block.strip()!r}")

if removed == 0:
    raise SystemExit("❌ No Shield Action embed/dependency lines found to remove")

path.write_text(text)
print("✅ Shield Action embed/dependency removed for CI archive (no ST_SHIELD_ACTION profile)")
print("   Create App ID ai.aladdin.ShieldAction + App Store profile → secret PROVISIONING_PROFILE_ST_SHIELD_ACTION")
PY
