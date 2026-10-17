#!/usr/bin/env bash
# Set GitHub Actions secrets for Family Controls App Store + Screen Time profiles.
# Requires: gh auth login  OR  export GH_TOKEN=... (repo admin / secrets:write)
#
# Default staging dir (created by agent):
#   ~/ALADDIN_VPN_SAFE/github_profile_secrets_staging_20261017
set -euo pipefail

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
REPO="${REPO:-sergey234/ALADDIN_FAMILY}"
STAGING="${1:-$HOME/ALADDIN_VPN_SAFE/github_profile_secrets_staging_20261017}"

if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh not found. Install GitHub CLI or add /usr/local/bin to PATH."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ gh not authenticated."
  echo "   Run:  gh auth login"
  echo "   Or:   export GH_TOKEN=ghp_...   # scope: repo (classic) or Actions secrets write"
  exit 1
fi

if [ ! -d "$STAGING" ]; then
  echo "❌ Staging dir not found: $STAGING"
  exit 1
fi

set_b64() {
  local name="$1"
  local file="$STAGING/${name}.b64"
  if [ ! -f "$file" ]; then
    echo "❌ missing $file"
    exit 1
  fi
  # verify FC before upload
  local tmp
  tmp=$(mktemp)
  base64 -d < "$file" > "$tmp"
  if ! security cms -D -i "$tmp" 2>/dev/null | grep -q 'com.apple.developer.family-controls'; then
    echo "❌ $name: no family-controls in profile — abort"
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
  gh secret set "$name" --repo "$REPO" < "$file"
  echo "✅ set $name"
}

set_text() {
  local name="$1"
  local file="$STAGING/${name}.txt"
  if [ ! -f "$file" ]; then
    echo "❌ missing $file"
    exit 1
  fi
  gh secret set "$name" --repo "$REPO" < "$file"
  echo "✅ set $name"
}

set_b64 PROVISIONING_PROFILE_APP
set_b64 PROVISIONING_PROFILE_ST_MONITOR
set_b64 PROVISIONING_PROFILE_ST_REPORT
set_b64 PROVISIONING_PROFILE_ST_SHIELD
set_b64 PROVISIONING_PROFILE_ST_SHIELD_ACTION
set_text PROVISIONING_PROFILE_ST_MONITOR_UUID
set_text PROVISIONING_PROFILE_ST_REPORT_UUID
set_text PROVISIONING_PROFILE_ST_SHIELD_UUID
set_text PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID

echo ""
echo "✅ ST/FC secrets updated on $REPO (incl. Shield Action)"
echo "   Next: commit CI decode wiring if needed, then push when GO."
