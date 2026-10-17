#!/usr/bin/env bash
# CI: decode Screen Time App Store profiles (Monitor / Report / Shield).
# Expects secrets:
#   PROVISIONING_PROFILE_ST_MONITOR (+ optional _UUID)
#   PROVISIONING_PROFILE_ST_REPORT  (+ optional _UUID)
#   PROVISIONING_PROFILE_ST_SHIELD  (+ optional _UUID)
#   PROVISIONING_PROFILE_ST_SHIELD_ACTION (+ optional _UUID)  # WAVE3 B3
# Writes GITHUB_ENV: PROVISIONING_PROFILE_ST_*_UUID for Fastlane.
set -euo pipefail

PROFILE_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"
mkdir -p "$PROFILE_DIR"

extract_uuid() {
  local xml="$1"
  local uuid=""
  # Prefer the <key>UUID</key> string (not the first UUID-shaped blob in certs)
  uuid=$(printf '%s' "$xml" | tr '\n' ' ' | sed -n 's/.*<key>UUID<\/key>[[:space:]]*<string>\([^<]*\)<\/string>.*/\1/p' | head -1)
  if [ -z "$uuid" ]; then
    uuid=$(printf '%s' "$xml" | plutil -extract UUID raw -o - - 2>/dev/null || true)
  fi
  printf '%s' "$uuid"
}

decode_one() {
  local label="$1"
  local secret_b64="$2"
  local expected_uuid="${3:-}"
  local env_uuid_key="$4"
  local tmp_name="$5"

  if [ -z "${secret_b64}" ]; then
    echo "⚠️  ${label}: secret empty — ST appex will be skipped in Fastlane"
    echo "${env_uuid_key}=" >> "${GITHUB_ENV:-/dev/null}"
    return 0
  fi

  local cleaned tmp_path profile_xml uuid dest
  cleaned=$(echo -n "$secret_b64" | tr -d '\n\r\t ' | tr -dc 'A-Za-z0-9+/=')
  tmp_path="$(mktemp -t "aladdin_${tmp_name}.XXXXXX").mobileprovision"
  echo -n "$cleaned" | base64 -d > "$tmp_path"
  if [ ! -s "$tmp_path" ]; then
    echo "❌ ${label}: base64 decode produced empty file"
    rm -f "$tmp_path"
    exit 1
  fi

  profile_xml=$(security cms -D -i "$tmp_path" 2>/dev/null || true)
  if [ -z "$profile_xml" ]; then
    echo "❌ ${label}: security cms -D failed (bad base64 / corrupt profile)"
    rm -f "$tmp_path"
    exit 1
  fi

  uuid=$(extract_uuid "$profile_xml")
  if [ -z "$uuid" ]; then
    echo "❌ ${label}: failed to extract UUID"
    rm -f "$tmp_path"
    exit 1
  fi

  if [ -n "$expected_uuid" ]; then
    local exp_lc uuid_lc
    exp_lc=$(printf '%s' "$expected_uuid" | tr '[:upper:]' '[:lower:]')
    uuid_lc=$(printf '%s' "$uuid" | tr '[:upper:]' '[:lower:]')
    if [ "$exp_lc" != "$uuid_lc" ]; then
      echo "⚠️  ${label}: secret UUID ${expected_uuid} ≠ profile ${uuid} — using profile UUID"
    fi
  fi

  if ! printf '%s' "$profile_xml" | grep -q 'com.apple.developer.family-controls'; then
    echo "❌ ${label}: profile missing family-controls — regenerate App Store profile"
    rm -f "$tmp_path"
    exit 1
  fi
  if ! printf '%s' "$profile_xml" | grep -q 'group.ai.aladdin'; then
    echo "❌ ${label}: profile missing App Group group.ai.aladdin"
    rm -f "$tmp_path"
    exit 1
  fi

  dest="${PROFILE_DIR}/${uuid}.mobileprovision"
  cp -f "$tmp_path" "$dest"
  rm -f "$tmp_path"
  echo "✅ ${label}: UUID=${uuid} (family-controls + App Group)"
  echo "${env_uuid_key}=${uuid}" >> "${GITHUB_ENV:-/dev/null}"
}

decode_one "ST Monitor" \
  "${PROVISIONING_PROFILE_ST_MONITOR:-}" \
  "${PROVISIONING_PROFILE_ST_MONITOR_UUID:-}" \
  "PROVISIONING_PROFILE_ST_MONITOR_UUID" \
  "st_monitor"

decode_one "ST Report" \
  "${PROVISIONING_PROFILE_ST_REPORT:-}" \
  "${PROVISIONING_PROFILE_ST_REPORT_UUID:-}" \
  "PROVISIONING_PROFILE_ST_REPORT_UUID" \
  "st_report"

decode_one "ST Shield" \
  "${PROVISIONING_PROFILE_ST_SHIELD:-}" \
  "${PROVISIONING_PROFILE_ST_SHIELD_UUID:-}" \
  "PROVISIONING_PROFILE_ST_SHIELD_UUID" \
  "st_shield"

decode_one "ST Shield Action" \
  "${PROVISIONING_PROFILE_ST_SHIELD_ACTION:-}" \
  "${PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID:-}" \
  "PROVISIONING_PROFILE_ST_SHIELD_ACTION_UUID" \
  "st_shield_action"
