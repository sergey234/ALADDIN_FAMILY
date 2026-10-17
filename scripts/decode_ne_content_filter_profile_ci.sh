#!/usr/bin/env bash
# CI: decode NE Content Filter App Store profile (ai.aladdin.ContentFilter).
# Secrets:
#   PROVISIONING_PROFILE_NE_CONTENT_FILTER (+ optional _UUID)
# Writes GITHUB_ENV: PROVISIONING_PROFILE_NE_CONTENT_FILTER_UUID
# If secret empty → Fastlane runs ci_disable_content_filter_embed.sh
set -euo pipefail

PROFILE_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"
mkdir -p "$PROFILE_DIR"

if [ -z "${PROVISIONING_PROFILE_NE_CONTENT_FILTER:-}" ]; then
  echo "⚠️  PROVISIONING_PROFILE_NE_CONTENT_FILTER not set — Content Filter embed will be skipped"
  echo "PROVISIONING_PROFILE_NE_CONTENT_FILTER_UUID=" >> "${GITHUB_ENV:-/dev/null}"
  exit 0
fi

CLEANED_SECRET=$(echo -n "$PROVISIONING_PROFILE_NE_CONTENT_FILTER" | tr -d '\n\r\t ' | tr -dc 'A-Za-z0-9+/=')
TMP_PATH="$(mktemp -t aladdin_ne_filter.XXXXXX).mobileprovision"
echo -n "$CLEANED_SECRET" | base64 -d > "$TMP_PATH"
if [ ! -s "$TMP_PATH" ]; then
  echo "❌ NE Content Filter: base64 decode produced empty file"
  rm -f "$TMP_PATH"
  exit 1
fi

PROFILE_XML=$(security cms -D -i "$TMP_PATH" 2>/dev/null || true)
if [ -z "$PROFILE_XML" ]; then
  echo "❌ NE Content Filter: security cms -D failed"
  rm -f "$TMP_PATH"
  exit 1
fi

UUID=$(printf '%s' "$PROFILE_XML" | tr '\n' ' ' | sed -n 's/.*<key>UUID<\/key>[[:space:]]*<string>\([^<]*\)<\/string>.*/\1/p' | head -1)
if [ -z "$UUID" ]; then
  UUID=$(printf '%s' "$PROFILE_XML" | plutil -extract UUID raw -o - - 2>/dev/null || true)
fi
if [ -z "$UUID" ]; then
  echo "❌ NE Content Filter: failed to extract UUID"
  rm -f "$TMP_PATH"
  exit 1
fi

if ! printf '%s' "$PROFILE_XML" | grep -q 'content-filter-provider'; then
  echo "❌ NE Content Filter: profile missing content-filter-provider"
  rm -f "$TMP_PATH"
  exit 1
fi
if ! printf '%s' "$PROFILE_XML" | grep -q 'group.ai.aladdin'; then
  echo "❌ NE Content Filter: profile missing App Group group.ai.aladdin"
  rm -f "$TMP_PATH"
  exit 1
fi
if ! printf '%s' "$PROFILE_XML" | grep -q 'ai.aladdin.ContentFilter'; then
  echo "❌ NE Content Filter: bundle id must be ai.aladdin.ContentFilter"
  rm -f "$TMP_PATH"
  exit 1
fi

# Apple may list packet-tunnel among NE types when Network Extensions is on —
# product ships content-filter-provider only (no Personal VPN / Packet Tunnel code).
DEST="${PROFILE_DIR}/${UUID}.mobileprovision"
cp -f "$TMP_PATH" "$DEST"
rm -f "$TMP_PATH"
echo "✅ NE Content Filter: UUID=${UUID} (content-filter-provider + App Group)"
echo "PROVISIONING_PROFILE_NE_CONTENT_FILTER_UUID=${UUID}" >> "${GITHUB_ENV:-/dev/null}"
