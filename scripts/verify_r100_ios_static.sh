#!/usr/bin/env bash
# r100 — статическая проверка iOS (без xcodebuild, <5 с).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PBX="ALADDIN.xcodeproj/project.pbxproj"
fail=0

check_pbx() {
  local needle="$1"
  local msg="$2"
  if grep -q "$needle" "$PBX"; then
    echo "OK  $msg"
  else
    echo "FAIL $msg"
    fail=1
  fi
}

check_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    echo "OK  file $path"
  else
    echo "FAIL missing $path"
    fail=1
  fi
}

check_pbx "WellnessModelsTests.swift in Sources" "WellnessModelsTests → ALADDINUnitTests"
check_pbx "WellnessCompanionNavUITests.swift in Sources" "WellnessCompanionNavUITests → ALADDINUITests"
check_file "Tests/UnitTests/WellnessModelsTests.swift"
check_file "Tests/UITests/WellnessCompanionNavUITests.swift"
check_file "docs/WELLNESS_I18N_GLOSSARY.md"
check_file "docs/WELLNESS_TESTFLIGHT_SMOKE_15.md"

if grep -q "product-type = \"com.apple.product-type.app-extension\"" "$PBX" && grep -q "ALADDINWidgets" "$PBX"; then
  echo "OK  ALADDINWidgets extension target in pbxproj"
else
  echo "WARN ALADDINWidgets.appex target not in pbxproj (r100-2-06 — Xcode manual)"
fi

if grep -q "UITestWellnessNavSmoke" ALADDINApp.swift; then
  echo "OK  UITestWellnessNavSmoke bootstrap"
else
  echo "FAIL UITestWellnessNavSmoke missing in ALADDINApp.swift"
  fail=1
fi

if [[ $fail -ne 0 ]]; then
  exit 1
fi
echo "OK — r100 iOS static gate passed"
