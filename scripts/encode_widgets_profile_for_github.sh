#!/usr/bin/env bash
# Owner helper: .mobileprovision → one-line base64 for GitHub Secret PROVISIONING_PROFILE_WIDGETS
# Usage:
#   ./scripts/encode_widgets_profile_for_github.sh ~/Downloads/*.mobileprovision
#   ./scripts/encode_widgets_profile_for_github.sh ~/Downloads/ALADDIN_AI_Widgets_App_Store.mobileprovision
set -euo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 /path/to/Widgets.mobileprovision"
  echo "Then paste stdout into GitHub Secret: PROVISIONING_PROFILE_WIDGETS"
  exit 1
fi

# Verify App Group + bundle hint (best-effort)
XML=$(security cms -D -i "$FILE" 2>/dev/null || true)
if echo "$XML" | grep -q 'group.ai.aladdin'; then
  echo "✅ App Group group.ai.aladdin found in profile" >&2
else
  echo "⚠️  group.ai.aladdin NOT found — recreate profile with App Groups" >&2
fi
if echo "$XML" | grep -q 'ai.aladdin.widgets'; then
  echo "✅ Bundle ai.aladdin.widgets found in profile" >&2
else
  echo "⚠️  ai.aladdin.widgets NOT found — wrong App ID?" >&2
fi

NAME=$(echo "$XML" | plutil -extract Name raw -o - - 2>/dev/null || echo "(unknown)")
UUID=$(echo "$XML" | plutil -extract UUID raw -o - - 2>/dev/null || echo "(unknown)")
echo "Profile Name: $NAME" >&2
echo "Profile UUID: $UUID" >&2
echo "--- copy line below into GitHub Secret PROVISIONING_PROFILE_WIDGETS ---" >&2
base64 < "$FILE" | tr -d '\n'
echo
