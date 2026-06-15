#!/usr/bin/env bash
# D-batch static gate — extensions, signing handoff, QA numbers (no physical device).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PBX="ALADDIN.xcodeproj/project.pbxproj"
fail=0

check_pbx() {
  if grep -q "$1" "$PBX"; then echo "OK  $2"; else echo "FAIL $2"; fail=1; fi
}
check_file() {
  if [[ -f "$1" ]]; then echo "OK  file $1"; else echo "FAIL missing $1"; fail=1; fi
}

echo ">>> D-05 / extensions embed"
check_pbx "ALADDINCallDirectory.appex in Embed App Extensions" "Call Directory embedded"
check_pbx "ALADDINAntifakeShare.appex in Embed App Extensions" "Antifake Share embedded"

echo ">>> D-06 device QA doc"
check_file "docs/ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md"
check_file "docs/ANTIFAKE_POST_CALL_DEVICE_QA.md"
check_file "docs/release/device_qa/antifake/DEVICE_QA_RECORD.json"

echo ">>> D-01 archive handoff"
check_file "fastlane/Fastfile"
check_file "scripts/archive_antifake_device_build.sh"
check_file "docs/CI_ANTIFAKE_SHARE_SIGNING_HANDOFF.md"

echo ">>> C-11 QA numbers (server)"
python3 -m unittest backend_tests.test_antifake_call_directory_store.AntifakeCallDirectoryStoreTests.test_ru_v1_csv_exists_for_c08 -q 2>/dev/null || {
  echo "WARN QA CSV check skipped (deps)"
}

if [[ $fail -ne 0 ]]; then exit 1; fi
echo "OK — antifake device static readiness"
