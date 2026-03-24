#!/usr/bin/env bash
# Advanced Settings smoke (curl-only) with color GO/STOP
# Usage:
#   export BASE_URL="https://aladdin-ai.ru"
#   export TOKEN="<jwt>"
#   ./docs/server/test_advanced_settings_smoke.sh

set -euo pipefail

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

BASE_URL="${BASE_URL:-https://aladdin-ai.ru}"
TOKEN="${TOKEN:-}"
AUTH="Authorization: Bearer $TOKEN"

stop() {
  echo -e "${RED}[STOP]${NC} $*"
  exit 1
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $*"
}

pass() {
  echo -e "${GREEN}[PASS]${NC} $*"
}

info() {
  echo -e "[INFO] $*"
}

check_env() {
  info "BASE_URL=$BASE_URL"
  [[ -n "$TOKEN" ]] || stop "TOKEN is empty. Export TOKEN before running."
  command -v jq >/dev/null 2>&1 || warn "jq not found. Output will be raw JSON."
}

req() {
  local method="$1"; shift
  local path="$1"; shift
  local data="${1:-}"
  if [[ -n "$data" ]]; then
    curl -sS -X "$method" "$BASE_URL$path" -H "$AUTH" -H "Content-Type: application/json" -d "$data"
  else
    curl -sS -X "$method" "$BASE_URL$path" -H "$AUTH"
  fi
}

verify_equals() {
  local json="$1"; shift
  local key="$1"; shift
  local expected="$1"; shift
  local actual
  actual=$(printf '%s' "$json" | jq -r --arg k "$key" '.[$k] // empty' 2>/dev/null || true)
  [[ "$actual" == "$expected" ]] || stop "$key: expected=$expected got=$actual"
}

verify_exists_array_len_ge() {
  local json="$1"; shift
  local key="$1"; shift
  local minlen="$1"; shift
  local len
  len=$(printf '%s' "$json" | jq -r --arg k "$key" '.[$k] | if type=="array" then length else -1 end' 2>/dev/null || echo -1)
  [[ "$len" -ge "$minlen" ]] || stop "$key length < $minlen (got $len)"
}

get_settings() {
  local component="$1"; shift
  local resp
  resp=$(req GET "/api/components/configuration/$component")
  local code
  code=$(printf '%s' "$resp" | jq -r '.__status__? // empty' 2>/dev/null || true)
  printf '%s' "$resp" | jq -r '.configuration.settings' 2>/dev/null || printf '%s' "$resp"
}

main() {
  check_env

  # 1) Safari (browser_security_bot)
  info "Safari: write settings"
  req POST "/api/components/configuration/browser_security_bot" '{
    "settings": {
      "selectedCategories": ["adult","violence","gambling","forums"],
      "safariSitesEnabled": true,
      "safariSocialEnabled": true
    }
  }' >/dev/null

  info "Safari: read/verify"
  local_safari=$(get_settings "browser_security_bot")
  if command -v jq >/dev/null 2>&1; then
    verify_equals "$local_safari" "safariSitesEnabled" "true"
    verify_equals "$local_safari" "safariSocialEnabled" "true"
    pass "Safari settings verified"
  else
    echo "$local_safari"
  fi

  # 2) Parental monitoring (parental_control_bot)
  info "Parental: write toggles"
  req POST "/api/components/configuration/parental_control_bot" '{
    "settings": {
      "messagesMonitoringEnabled": true,
      "screenshotsEnabled": true,
      "parental_messages_monitoring": true,
      "parental_screenshots_enabled": true
    }
  }' >/dev/null

  info "Parental: read/verify"
  local_parental=$(get_settings "parental_control_bot")
  if command -v jq >/dev/null 2>&1; then
    verify_equals "$local_parental" "messagesMonitoringEnabled" "true"
    verify_equals "$local_parental" "screenshotsEnabled" "true"
    pass "Parental monitoring verified"
  else
    echo "$local_parental"
  fi

  # 3) Time management (parental_control_bot)
  info "TimeMgmt: write"
  req POST "/api/components/configuration/parental_control_bot" '{
    "settings": {
      "scheduleWeekdayStart": 1.0,
      "scheduleWeekdayEnd": 2.0,
      "scheduleWeekendStart": 3.0,
      "scheduleWeekendEnd": 4.0,
      "scheduleIsWeekdaySelected": true,
      "sleepBedtimeStart": 5.0,
      "sleepBedtimeEnd": 6.0,
      "sleepEmergencyCallsEnabled": true,
      "appLimits": [
        {"app":"Instagram","limit":30.0},
        {"app":"TikTok","limit":20.0}
      ]
    }
  }' >/dev/null

  info "TimeMgmt: read/verify"
  local_tm=$(get_settings "parental_control_bot")
  if command -v jq >/dev/null 2>&1; then
    verify_equals "$local_tm" "scheduleWeekdayStart" "1"
    verify_equals "$local_tm" "scheduleWeekdayEnd" "2"
    verify_equals "$local_tm" "sleepEmergencyCallsEnabled" "true"
    verify_exists_array_len_ge "$local_tm" "appLimits" 2
    pass "Time management verified"
  else
    echo "$local_tm"
  fi

  echo -e "${GREEN}[GO] Advanced Settings curl smoke passed${NC}"
}

main "$@"

