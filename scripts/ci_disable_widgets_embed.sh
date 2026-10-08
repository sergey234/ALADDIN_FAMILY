#!/usr/bin/env bash
# CI fallback when PROVISIONING_PROFILE_WIDGETS is missing — skip dependency
# (Widgets may not be in Embed phase yet; dependency alone still forces signing).
set -euo pipefail

PBX="ALADDIN.xcodeproj/project.pbxproj"
if [ ! -f "$PBX" ]; then
  echo "❌ $PBX not found"
  exit 1
fi

cp "$PBX" "${PBX}.bak_widgets"

python3 <<'PY'
from pathlib import Path

path = Path("ALADDIN.xcodeproj/project.pbxproj")
text = path.read_text()
removals = [
    "\t\t\t\tWDGT0112F90000100C7D34B /* ALADDINWidgets.appex in Embed App Extensions */,\n",
    "\t\t\t\tWDGT0132F90000100C7D34B /* PBXTargetDependency */,\n",
]
removed = 0
for block in removals:
    if block in text:
        text = text.replace(block, "", 1)
        removed += 1
    else:
        print(f"⚠️  block not present (ok if already absent): {block.strip()!r}")

if removed == 0:
    raise SystemExit("❌ No Widgets embed/dependency lines found to remove")

path.write_text(text)
print("✅ Widgets embed/dependency removed for CI archive (no PROVISIONING_PROFILE_WIDGETS)")
PY
