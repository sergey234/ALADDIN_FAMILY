#!/usr/bin/env bash
# Static evidence: China mainland geo-gate for Family Chat + Companion + AI Assistant.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
check() {
  local label="$1"
  local pattern="$2"
  local file="$3"
  if rg -q "$pattern" "$file"; then
    echo "OK  $label"
  else
    echo "FAIL $label ($file)"
    fail=1
  fi
}

check "compliance module" "restrictsEncryptedChatAndAIGC" "Core/Compliance/ChinaMainlandCompliance.swift"
check "storefront CHN" 'mainlandChinaStorefrontCode = "CHN"' "Core/Compliance/ChinaMainlandCompliance.swift"
check "AppConfig family flag" "isFamilyChatAvailable" "Core/Config/AppConfig.swift"
check "AppConfig companion flag" "isCompanionAvailable" "Core/Config/AppConfig.swift"
check "AppConfig AI flag" "isAIAssistantAvailable" "Core/Config/AppConfig.swift"
check "nav gate" "isBlockedByChinaMainlandCompliance" "Core/Navigation/NavigationManager.swift"
check "launch refresh" "refreshStorefrontFromAppStore" "ALADDINApp.swift"
check "unit tests" "ChinaMainlandComplianceTests" "Tests/UnitTests/ChinaMainlandComplianceTests.swift"
check "pbxproj sources" "ChinaMainlandCompliance.swift in Sources" "ALADDIN.xcodeproj/project.pbxproj"

# Must NOT gate HK/Macau/Taiwan as mainland
if rg -n 'HKG|MAC|TWN' Core/Compliance/ChinaMainlandCompliance.swift | rg -v 'not|не|Hong Kong|Macau|Taiwan' >/dev/null 2>&1; then
  echo "WARN unexpected HKG/MAC/TWN equality gate — review file"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "VERIFY FAIL"
  exit 1
fi
echo "VERIFY OK — China mainland gate present; ASC answer after release: Нет"
