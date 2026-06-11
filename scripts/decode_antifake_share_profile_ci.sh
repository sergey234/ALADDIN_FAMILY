#!/usr/bin/env bash
# Optional CI decode for ALADDINAntifakeShare App Store profile.
# If PROVISIONING_PROFILE_ANTIFAKE_SHARE is unset, enables Automatic signing fallback.
set -euo pipefail

PROFILE_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"
mkdir -p "$PROFILE_DIR"

if [ -z "${PROVISIONING_PROFILE_ANTIFAKE_SHARE:-}" ]; then
  echo "⚠️  PROVISIONING_PROFILE_ANTIFAKE_SHARE not set"
  echo "    ALADDINAntifakeShare → Automatic signing (-allowProvisioningUpdates)"
  echo "ANTIFAKE_USE_AUTOMATIC_SIGNING=true" >> "${GITHUB_ENV:-/dev/null}"
  echo "ANTIFAKE_PROFILE_UUID=" >> "${GITHUB_ENV:-/dev/null}"
  exit 0
fi

CLEANED_SECRET=$(echo -n "$PROVISIONING_PROFILE_ANTIFAKE_SHARE" | tr -d '\n\r\t ' | tr -dc 'A-Za-z0-9+/=')
echo -n "$CLEANED_SECRET" | base64 -d > "$PROFILE_DIR/antifake_share.mobileprovision"

PROFILE_XML=$(security cms -D -i "$PROFILE_DIR/antifake_share.mobileprovision" 2>/dev/null || true)
UUID=$(echo "$PROFILE_XML" | plutil -extract UUID raw -o - - 2>/dev/null || echo "")
if [ -z "$UUID" ]; then
  UUID=$(echo "$PROFILE_XML" | grep -oE '[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}' | head -1 || echo "")
fi

if [ -z "$UUID" ]; then
  echo "❌ Failed to extract UUID from antifake share profile"
  exit 1
fi

mv -f "$PROFILE_DIR/antifake_share.mobileprovision" "$PROFILE_DIR/${UUID}.mobileprovision"
echo "✅ Antifake Share profile UUID: $UUID"
echo "ANTIFAKE_USE_AUTOMATIC_SIGNING=false" >> "${GITHUB_ENV:-/dev/null}"
echo "ANTIFAKE_PROFILE_UUID=$UUID" >> "${GITHUB_ENV:-/dev/null}"
