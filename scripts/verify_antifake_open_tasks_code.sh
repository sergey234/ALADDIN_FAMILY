#!/usr/bin/env bash
# Static code gates for open antifake tasks (no xcodebuild / simulator).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PBX="ALADDIN.xcodeproj/project.pbxproj"
fail=0

check_pbx() {
  if grep -q "$1" "$PBX"; then
    echo "OK  ${2:-$1}"
  else
    echo "FAIL ${2:-$1}"
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

check_grep() {
  if grep -q "$1" "$2"; then
    echo "OK  $3"
  else
    echo "FAIL $3"
    fail=1
  fi
}

echo ">>> J-04 history PDF export"
check_file "Core/Security/AntifakeCheckHistoryPDFExporter.swift"
check_pbx "AntifakeCheckHistoryPDFExporter.swift in Sources" "PDF exporter in ALADDIN target"
check_grep "antifake_history_export_pdf" "Shared/Components/AntifakeCheckHistorySection.swift" "history export button"

echo ">>> D-07 identified vs blocked"
check_file "Tests/UnitTests/AntifakeCallDirectoryStoreTests.swift"
check_pbx "AntifakeCallDirectoryStoreTests.swift in Sources" "CD store unit tests in ALADDINTests"
check_grep "addIdentificationEntry" "ALADDINCallDirectory/CallDirectoryHandler.swift" "CD handler identification"
check_grep "addBlockingEntry" "ALADDINCallDirectory/CallDirectoryHandler.swift" "CD handler blocking"
python3 -m unittest backend_tests.test_antifake_call_directory_store -q

echo ">>> D-08 extension OFF orange status"
check_grep "antifake_call_directory_disabled_banner" "Shared/Components/AntifakeCallDirectorySettingsCard.swift" "disabled banner UI"
check_grep "warningOrange" "Shared/Components/AntifakeCallDirectorySettingsCard.swift" "orange status color"

echo ">>> D-10 EN/RU call labels"
check_file "Core/Security/AntifakeCallDirectoryLabelPolicy.swift"
check_pbx "AntifakeCallDirectoryLabelPolicy.swift in Sources"
check_grep "antifake_call_directory_identification_label" "Core/Localization/LocalizationManager.swift" "RU+EN label keys"
check_grep "relocalizeIfKnownDefault" "Core/Security/AntifakeCallDirectorySyncService.swift" "sync relocalize"

echo ">>> G-03 / Q-01 bypass off"
python3 scripts/verify_antifake_bypass_off.py

echo ">>> D-06 / E-06 / R-02 docs"
check_file "docs/ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md"
check_file "docs/ANTIFAKE_POST_CALL_DEVICE_QA.md"
check_file "docs/release/qa_signoff/antifake/README.md"

if [[ $fail -ne 0 ]]; then
  exit 1
fi
echo "OK — antifake open-task code gates passed"
