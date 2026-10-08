#!/usr/bin/env bash
# Optional CI decode for ALADDINWidgets App Store profile (ai.aladdin.widgets).
# If PROVISIONING_PROFILE_WIDGETS is unset, enables Automatic signing fallback.
set -euo pipefail

PROFILE_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"
mkdir -p "$PROFILE_DIR"

if [ -z "${PROVISIONING_PROFILE_WIDGETS:-}" ]; then
  echo "⚠️  PROVISIONING_PROFILE_WIDGETS not set"
  echo "    ALADDINWidgets → Automatic signing (-allowProvisioningUpdates)"
  echo "WIDGETS_USE_AUTOMATIC_SIGNING=true" >> "${GITHUB_ENV:-/dev/null}"
  echo "WIDGETS_PROFILE_UUID=" >> "${GITHUB_ENV:-/dev/null}"
  exit 0
fi

CLEANED_SECRET=$(echo -n "$PROVISIONING_PROFILE_WIDGETS" | tr -d '\n\r\t ' | tr -dc 'A-Za-z0-9+/=')
echo -n "$CLEANED_SECRET" | base64 -d > "$PROFILE_DIR/widgets.mobileprovision"

PROFILE_XML=$(security cms -D -i "$PROFILE_DIR/widgets.mobileprovision" 2>/dev/null || true)
UUID=$(echo "$PROFILE_XML" | plutil -extract UUID raw -o - - 2>/dev/null || echo "")
if [ -z "$UUID" ]; then
  UUID=$(echo "$PROFILE_XML" | grep -oE '[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}' | head -1 || echo "")
fi

if [ -z "$UUID" ]; then
  echo "❌ Failed to extract UUID from Widgets profile"
  exit 1
fi

mv -f "$PROFILE_DIR/widgets.mobileprovision" "$PROFILE_DIR/${UUID}.mobileprovision"
echo "✅ Widgets profile UUID: $UUID"
echo "WIDGETS_USE_AUTOMATIC_SIGNING=false" >> "${GITHUB_ENV:-/dev/null}"
echo "WIDGETS_PROFILE_UUID=$UUID" >> "${GITHUB_ENV:-/dev/null}"
