#!/usr/bin/env bash
# af-ux static gate — Hub layout, Call tab sections, collapsed family reports.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

check_grep() {
  local file="$1" pattern="$2" label="$3"
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "OK  $label"
  else
    echo "FAIL $label"
    fail=1
  fi
}

check_not_grep() {
  local file="$1" pattern="$2" label="$3"
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "FAIL $label (found forbidden pattern)"
    fail=1
  else
    echo "OK  $label"
  fi
}

echo ">>> af-ux-01 Call Directory not global in Hub"
if grep -A25 "ScrollView" Screens/AntifakeHubScreen.swift | grep -q "AntifakeCallDirectorySettingsCard"; then
  echo "FAIL CD card still in global ScrollView"
  fail=1
else
  echo "OK  CD card not in global ScrollView"
fi

echo ">>> af-ux-04 AntifakeCallTabView"
check_grep "Screens/AntifakeHubScreen.swift" "AntifakeCallTabView" "Hub uses AntifakeCallTabView"
check_grep "Shared/Components/AntifakeCallTabView.swift" "antifake_call_section_recording" "recording section id"
check_grep "Shared/Components/AntifakeCallTabView.swift" "antifake_call_section_incoming" "incoming section id"
check_grep "Shared/Components/AntifakeCallTabView.swift" "AntifakeCallDirectorySettingsCard" "CD card in Call tab only"

echo ">>> af-ux-11 post-call toggle placement"
check_grep "Shared/Components/AntifakeCallTabView.swift" "AntifakePostCallReminderToggle" "toggle in Call tab section A"
check_not_grep "Shared/Components/AntifakeCallDirectorySettingsCard.swift" "postCallReminderToggle" "toggle removed from CD card"

echo ">>> af-ux-16 family reports collapsed"
check_grep "Shared/Components/AntifakeFamilyMoatViews.swift" "isExpanded = false" "collapsed by default"
check_grep "Shared/Components/AntifakeFamilyMoatViews.swift" "antifake_family_reports_collapsed_hint" "collapsed hint key"

echo ">>> af-ux-02 localization"
check_grep "Core/Localization/LocalizationManager.swift" "antifake_call_directory_extension_name" "extension display name key"
check_grep "Core/Localization/LocalizationManager.swift" "ALADDIN Call Filter" "ALADDIN Call Filter in strings"

echo ">>> af-ux-09 UITest"
check_grep "Tests/UITests/AntifakeHubTabsUITests.swift" "testCallDirectoryCardOnlyOnCallTab" "CD card tab UITest"

if [[ $fail -ne 0 ]]; then exit 1; fi
echo "OK — af-ux hub static gate"
