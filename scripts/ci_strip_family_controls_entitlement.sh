#!/usr/bin/env bash
# CI: App Store profile "ALADDIN AI App Store" does not yet include
# com.apple.developer.family-controls (Distribution). Entitlement stays in git
# for local Device QA with Development profiles; strip only for CI archive.
set -euo pipefail

ENT="ALADDIN.entitlements"
if [ ! -f "$ENT" ]; then
  echo "❌ $ENT not found"
  exit 1
fi

cp "$ENT" "${ENT}.bak_family_controls"

/usr/libexec/PlistBuddy -c 'Delete :com.apple.developer.family-controls' "$ENT" 2>/dev/null \
  && echo "✅ Removed com.apple.developer.family-controls from $ENT for CI archive" \
  || echo "⚠️  family-controls key already absent in $ENT"

plutil -lint "$ENT"
echo "--- entitlements after strip ---"
/usr/libexec/PlistBuddy -c 'Print' "$ENT" | head -40
