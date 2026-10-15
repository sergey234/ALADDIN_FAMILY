#!/usr/bin/env bash
# Honesty gate: Family Time «Статистика сегодня» must not invent usage.
# Exit 0 = PASS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*"; exit 1; }
ok() { echo "OK: $*"; }

# 1) No writer of parental_time_stats except FamilyTimeControl persistUsageCache (source=device_activity)
writers="$(
  rg -n 'forKey:\s*"parental_time_stats"|\"parental_time_stats\"\s*,' \
    --glob '*.swift' \
    -g '!Family_Registration*' -g '!LocalizedVersions*' -g '!ML_SYSTEM*' \
    -g '!.derivedData*' -g '!build/**' -g '!CLEAN_EXPORT*' \
    || true
)"
# Allowed: set(payload) in 02_FamilyScreen persistUsageCache + dictionary reads
bad="$(echo "$writers" | rg -v 'dictionary\(forKey:|persistUsageCache|UserDefaults\.standard\.set\(payload' || true)"
# Any .set( that is not our payload path
set_lines="$(echo "$writers" | rg '\.set\(' || true)"
if echo "$set_lines" | rg -q .; then
  if ! echo "$set_lines" | rg -q 'persistUsageCache|set\(payload'; then
    fail "unexpected parental_time_stats writers:\n$set_lines"
  fi
fi
ok "parental_time_stats writers gated (device_activity cache only)"

# 2) fetchRealScreenTimeStats still returns []
rg -n 'func fetchRealScreenTimeStats' -A6 Core/Managers/ParentalControlManager.swift \
  | rg -q 'return \[\]' \
  || fail "fetchRealScreenTimeStats must return [] until DeviceActivity Report exists"
ok "fetchRealScreenTimeStats returns []"

# 3) getAppUsageStatistics must not hardcode Instagram mock rows
block="$(rg -n 'func getAppUsageStatistics' -A25 Core/Managers/ParentalControlManager.swift)"
echo "$block" | rg -q 'fetchRealScreenTimeStats' || fail "getAppUsageStatistics must delegate to fetchRealScreenTimeStats"
echo "$block" | rg -q 'timeSpent: 1800' && fail "Instagram mock timeSpent:1800 still present" || true
ok "getAppUsageStatistics has no Instagram/TikTok mock payload"

# 4) Live FamilyTimeControlModal has no hardcoded 1h 36m
modal="$(
  awk '/struct FamilyTimeControlModal/,/struct FamilyNetworkLayersLocalStatusBlock/' Screens/02_FamilyScreen.swift
)"
echo "$modal" | rg -q '1h 36m' && fail "mock 1h 36m still in FamilyTimeControlModal" || true
echo "$modal" | rg -q 'family_statistics_today_empty' || fail "empty-state key missing in modal"
echo "$modal" | rg -q 'hasRealTimeStats' || fail "hasRealTimeStats missing"
ok "FamilyTimeControlModal honest empty path"

# 5) No DeviceActivityMonitor extension source in app tree
if rg -l 'class .*DeviceActivityMonitor' --glob '*.swift' \
  -g '!.derivedData*' -g '!build/**' 2>/dev/null | rg -q .; then
  ok "DeviceActivityMonitor source present (usage path may become real later)"
else
  ok "no DeviceActivityMonitor extension source (usage cannot be collected yet)"
fi

# 6) Localization keys present
for lang in ru en; do
  f="Resources/Localization/${lang}.lproj/Localizable.strings"
  rg -q 'family_statistics_today_empty' "$f" || fail "missing family_statistics_today_empty in $lang"
  rg -q 'duration_minutes_fmt' "$f" || fail "missing duration_minutes_fmt in $lang"
done
ok "RU/EN duration + empty keys present"

./scripts/verify_localization_manager_integrity.sh >/dev/null
ok "LocalizationManager integrity"

echo "PASS: parental time stats honesty"
