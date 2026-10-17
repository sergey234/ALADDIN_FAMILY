#!/usr/bin/env bash
# CI fallback when PROVISIONING_PROFILE_NE_CONTENT_FILTER_UUID is missing.
set -euo pipefail

PBX="ALADDIN.xcodeproj/project.pbxproj"
if [ ! -f "$PBX" ]; then
  echo "❌ $PBX not found"
  exit 1
fi

cp "$PBX" "${PBX}.bak_contentfilter"

python3 <<'PY'
from pathlib import Path

path = Path("ALADDIN.xcodeproj/project.pbxproj")
text = path.read_text()
removals = [
    "\t\t\t\tCFILT0112F90000200C7D34B /* ALADDINContentFilter.appex in Embed App Extensions */,\n",
    "\t\t\t\tCFILT0302F90000200C7D34B /* PBXTargetDependency */,\n",
]
removed = 0
for block in removals:
    if block in text:
        text = text.replace(block, "", 1)
        removed += 1
    else:
        print(f"⚠️  block not present (ok if already absent): {block.strip()!r}")

if removed == 0:
    raise SystemExit("❌ No Content Filter embed/dependency lines found to remove")

path.write_text(text)
print("✅ Content Filter embed/dependency removed for CI archive (no NE Content Filter profile)")
print("   Create App ID ai.aladdin.ContentFilter + App Store profile when ready")
PY
