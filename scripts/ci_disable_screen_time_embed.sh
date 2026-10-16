#!/usr/bin/env bash
# CI fallback when Screen Time App Store profiles are missing — skip embed + dependency
# (same pattern as ci_disable_widgets_embed.sh / ci_disable_call_directory_embed.sh).
# Local Xcode / Device QA still use the ST targets; only CI archive is stripped.
set -euo pipefail

PBX="ALADDIN.xcodeproj/project.pbxproj"
if [ ! -f "$PBX" ]; then
  echo "❌ $PBX not found"
  exit 1
fi

cp "$PBX" "${PBX}.bak_screentime"

python3 <<'PY'
from pathlib import Path

path = Path("ALADDIN.xcodeproj/project.pbxproj")
text = path.read_text()
removals = [
    "\t\t\t\tSTMON0112F90000200C7D34B /* ALADDINDeviceActivityMonitor.appex in Embed App Extensions */,\n",
    "\t\t\t\tSTREP0112F90000200C7D34B /* ALADDINDeviceActivityReport.appex in Embed App Extensions */,\n",
    "\t\t\t\tSTSHD0112F90000200C7D34B /* ALADDINShieldConfiguration.appex in Embed App Extensions */,\n",
    "\t\t\t\tSTMON0132F90000200C7D34B /* PBXTargetDependency */,\n",
    "\t\t\t\tSTREP0132F90000200C7D34B /* PBXTargetDependency */,\n",
    "\t\t\t\tSTSHD0132F90000200C7D34B /* PBXTargetDependency */,\n",
]
removed = 0
for block in removals:
    if block in text:
        text = text.replace(block, "", 1)
        removed += 1
    else:
        print(f"⚠️  block not present (ok if already absent): {block.strip()!r}")

if removed == 0:
    raise SystemExit("❌ No Screen Time embed/dependency lines found to remove")

path.write_text(text)
print(f"✅ Screen Time embed/dependency removed for CI archive ({removed} lines)")
print("   Add App Store profiles + GitHub secrets later to ship Monitor/Report/Shield in IPA")
PY
