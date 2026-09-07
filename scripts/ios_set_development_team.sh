#!/usr/bin/env bash
# Replace DEVELOPMENT_TEAM in ALADDIN.xcodeproj for all targets.
# Usage: ./scripts/ios_set_development_team.sh <COMPANY_TEAM_ID>
# Example: ./scripts/ios_set_development_team.sh ABCD123456
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PBX="$ROOT/ALADDIN.xcodeproj/project.pbxproj"
NEW_TEAM="${1:-}"

if [[ -z "$NEW_TEAM" ]]; then
  echo "Usage: $0 <COMPANY_TEAM_ID>"
  echo "Current teams in pbxproj:"
  grep -o 'DEVELOPMENT_TEAM = [^;]*' "$PBX" | sort -u
  exit 1
fi

if [[ ! "$NEW_TEAM" =~ ^[A-Z0-9]{8,12}$ ]]; then
  echo "ERROR: Team ID should look like 8–12 alphanumeric chars (got: $NEW_TEAM)"
  exit 1
fi

if [[ ! -f "$PBX" ]]; then
  echo "ERROR: missing $PBX"
  exit 1
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
cp "$PBX" "$PBX.bak_team_${STAMP}"

python3 - "$PBX" "$NEW_TEAM" <<'PY'
import re, sys
from pathlib import Path
path = Path(sys.argv[1])
new_team = sys.argv[2]
text = path.read_text()
new = re.sub(r"DEVELOPMENT_TEAM = [^;]+;", f"DEVELOPMENT_TEAM = {new_team};", text)
if new == text:
    print("WARNING: no DEVELOPMENT_TEAM lines changed (pattern miss?)")
path.write_text(new)
print(f"Updated DEVELOPMENT_TEAM -> {new_team}")
print("Occurrences:", new.count(f"DEVELOPMENT_TEAM = {new_team};"))
PY

echo "Backup: $PBX.bak_team_${STAMP}"
echo "Next: ./scripts/ios_verify_signing_targets.sh"
echo "Then open Xcode → select Company team → Archive"
