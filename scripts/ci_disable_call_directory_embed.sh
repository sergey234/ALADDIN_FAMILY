#!/usr/bin/env bash
# CI fallback when PROVISIONING_PROFILE_CALL_DIRECTORY is missing — skip embed + dependency.
set -euo pipefail

PBX="ALADDIN.xcodeproj/project.pbxproj"
if [ ! -f "$PBX" ]; then
  echo "❌ $PBX not found"
  exit 1
fi

cp "$PBX" "${PBX}.bak_call_directory"

python3 <<'PY'
from pathlib import Path

path = Path("ALADDIN.xcodeproj/project.pbxproj")
text = path.read_text()
removals = [
    "\t\t\t\tAFCD0112F90000200C7D34B /* ALADDINCallDirectory.appex in Embed App Extensions */,\n",
    "\t\t\t\tAFCD0132F90000200C7D34B /* PBXTargetDependency */,\n",
]
for block in removals:
    if block not in text:
        raise SystemExit(f"❌ Expected block not found in project.pbxproj:\n{block!r}")
    text = text.replace(block, "", 1)

path.write_text(text)
print("✅ Call Directory embed + dependency removed for CI archive")
PY
