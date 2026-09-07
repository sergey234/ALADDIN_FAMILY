#!/usr/bin/env bash
# Verify all ALADDIN signing-related settings in project.pbxproj + entitlements.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PBX="$ROOT/ALADDIN.xcodeproj/project.pbxproj"

echo "=== DEVELOPMENT_TEAM (unique) ==="
grep -o 'DEVELOPMENT_TEAM = [^;]*' "$PBX" | sort -u

echo
echo "=== PRODUCT_BUNDLE_IDENTIFIER (unique) ==="
grep -o 'PRODUCT_BUNDLE_IDENTIFIER = [^;]*' "$PBX" | sort -u

echo
echo "=== PROVISIONING_PROFILE_SPECIFIER (unique) ==="
grep -o 'PROVISIONING_PROFILE_SPECIFIER = [^;]*' "$PBX" | sort -u || echo "(none / automatic)"

echo
echo "=== Entitlements App Groups (grep) ==="
for f in \
  "$ROOT/ALADDIN.entitlements" \
  "$ROOT/ALADDINContentBlocker/ALADDINContentBlocker.entitlements" \
  "$ROOT/ALADDINAntifakeShare/ALADDINAntifakeShare.entitlements" \
  "$ROOT/ALADDINCallDirectory/ALADDINCallDirectory.entitlements"
do
  echo "-- $(basename "$f")"
  if grep -q 'group.ai.aladdin' "$f" 2>/dev/null; then
    echo "  OK group.ai.aladdin"
  else
    echo "  MISSING group.ai.aladdin"
  fi
done

echo
echo "=== Expected bundles ==="
cat <<'EOF'
ai.aladdin
ai.aladdin.ContentBlocker
ai.aladdin.AntifakeShare
ai.aladdin.CallDirectory
EOF

TEAMS=$(grep -o 'DEVELOPMENT_TEAM = [^;]*' "$PBX" | sort -u | wc -l | tr -d ' ')
if [[ "$TEAMS" != "1" ]]; then
  echo
  echo "FAIL: expected exactly 1 DEVELOPMENT_TEAM value, found $TEAMS"
  exit 2
fi
echo
echo "OK: single DEVELOPMENT_TEAM across project"
