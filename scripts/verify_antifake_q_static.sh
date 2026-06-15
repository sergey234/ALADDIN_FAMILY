#!/usr/bin/env bash
# Q-02…Q-05 static release gates (no xcodebuild).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PBX="ALADDIN.xcodeproj/project.pbxproj"
fail=0

check_pbx() {
  if grep -q "$1" "$PBX"; then
    echo "OK  $2"
  else
    echo "FAIL $2"
    fail=1
  fi
}

check_file() {
  if [[ -f "$1" ]]; then
    echo "OK  file $1"
  else
    echo "FAIL missing $1"
    fail=1
  fi
}

echo ">>> Q-02 XCUITest Hub 4 tabs (static)"
check_pbx "AntifakeHubTabsUITests.swift in Sources" "AntifakeHubTabsUITests → ALADDINUITests"
check_file "Tests/UITests/AntifakeHubTabsUITests.swift"
if grep -q "UITestAntifakeHubSmoke" ALADDINApp.swift; then
  echo "OK  UITestAntifakeHubSmoke bootstrap"
else
  echo "FAIL UITestAntifakeHubSmoke missing in ALADDINApp.swift"
  fail=1
fi
if grep -q 'antifake_hub_tab_' Screens/AntifakeHubScreen.swift; then
  echo "OK  hub tab accessibility ids"
else
  echo "FAIL hub tab accessibility ids"
  fail=1
fi
for tab in text audio video call; do
  if grep -q "case \\.${tab}" Screens/AntifakeHubScreen.swift; then
    echo "OK  hub tab .${tab}"
  else
    echo "FAIL hub tab .${tab}"
    fail=1
  fi
done

echo ">>> Q-03 call-directory contract"
check_file "backend_tests/test_antifake_call_directory_contract.py"
python3 -m unittest backend_tests.test_antifake_call_directory_contract -q

echo ">>> Q-04 TestFlight beta criteria doc"
check_file "docs/release/ANTIFAKE_TESTFLIGHT_BETA_CRITERIA.md"

echo ">>> Q-05 no mock pre-submit"
python3 scripts/verify_antifake_no_mock_pre_submit.py

echo ">>> Q-01 bypass off (release branch)"
python3 scripts/verify_antifake_bypass_off.py

if [[ $fail -ne 0 ]]; then
  exit 1
fi
echo "OK — antifake Q static gates passed"
