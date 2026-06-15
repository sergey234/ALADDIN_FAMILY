#!/usr/bin/env bash
# Phase C quick runner — one suite per xcodebuild (avoids 10+ min hangs).
set -euo pipefail
cd "$(dirname "$0")/.."
LOG_DIR="${TMPDIR:-/tmp}/mnemo_phase_c"
mkdir -p "$LOG_DIR"
DEST="${MNEMO_TEST_DEST:-platform=iOS Simulator,id=A900C6B0-6E81-4779-9305-E32CAA039BF6}"
DD="${MNEMO_DERIVED_DATA:-$HOME/Library/Developer/Xcode/DerivedData/ALADDIN-eahryzmutvtbyceygnlyjsmiiaha}"

echo "==> gate mnemo-full"
python3 scripts/child_localization_gate.py --mnemo-full

echo "==> test-without-building (build in Xcode first: Cmd+B on $DEST)"

run_suite() {
  local name="$1"
  local arg="$2"
  local log="$LOG_DIR/${name}.log"
  echo "==> $name -> $log"
  if xcodebuild test-without-building -scheme ALADDIN -destination "$DEST" -derivedDataPath "$DD" "$arg" >"$log" 2>&1; then
    echo "✅ $name"
    grep -E "TEST SUCCEEDED|Executed [0-9]+ test" "$log" | tail -2 || true
  else
    echo "❌ $name"
    grep -E "error:|TEST FAILED|failed \(" "$log" | tail -8 || tail -8 "$log"
    return 1
  fi
}

FAIL=0
run_suite "MnemoCoreV3Tests" "-only-testing:ALADDINUnitTests/MnemoCoreV3Tests" || FAIL=1
run_suite "MnemonicSRSStoreTests" "-only-testing:ALADDINUnitTests/MnemonicSRSStoreTests" || FAIL=1
run_suite "MnemonicBaselineAssessmentTests" "-only-testing:ALADDINUnitTests/MnemonicBaselineAssessmentTests" || FAIL=1
run_suite "MnemonicCapstoneStoreTests" "-only-testing:ALADDINUnitTests/MnemonicCapstoneStoreTests" || FAIL=1
run_suite "MnemonicChampionshipStoreTests" "-only-testing:ALADDINUnitTests/MnemonicChampionshipStoreTests" || FAIL=1
run_suite "MnemonicPictogramStoreTests" "-only-testing:ALADDINUnitTests/MnemonicPictogramStoreTests" || FAIL=1
run_suite "MnemonicTableEngineTests" "-only-testing:ALADDINUnitTests/MnemonicTableEngineTests" || FAIL=1
run_suite "MnemoAcademyUITests" "-only-testing:ALADDINUITests/MnemoAcademyUITests" || FAIL=1

if [[ "$FAIL" -eq 0 ]]; then
  echo "✅ mnemo_phase_c_quick — all green (logs: $LOG_DIR)"
else
  echo "❌ mnemo_phase_c_quick — see $LOG_DIR"
  exit 1
fi
