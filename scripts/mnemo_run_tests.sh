#!/usr/bin/env bash
# MNEMO-B15-T02: MnemoCore v3 unit suites + UITest smoke (CI-friendly).
set -euo pipefail
cd "$(dirname "$0")/.."
# Default: booted iPhone 13 Pro Max 15.2 (override with MNEMO_TEST_DEST)
DEST="${MNEMO_TEST_DEST:-platform=iOS Simulator,id=A900C6B0-6E81-4779-9305-E32CAA039BF6}"
DD="${MNEMO_DERIVED_DATA:-$HOME/Library/Developer/Xcode/DerivedData/ALADDIN-eahryzmutvtbyceygnlyjsmiiaha}"

echo "==> child_localization_gate (mnemo full B15-T01)"
python3 scripts/child_localization_gate.py --mnemo-full

echo "==> child_localization_gate (incremental child screens)"
python3 scripts/child_localization_gate.py

MNEMO_UNIT_SUITES=(
  MnemonicSRSStoreTests
  MnemonicBaselineAssessmentTests
  MnemonicCapstoneStoreTests
  MnemonicChampionshipStoreTests
  MnemonicPictogramStoreTests
  MnemonicTableEngineTests
  MnemoCoreV3Tests
)

ONLY_TESTING_ARGS=()
for suite in "${MNEMO_UNIT_SUITES[@]}"; do
  ONLY_TESTING_ARGS+=("-only-testing:ALADDINUnitTests/${suite}")
done

echo "==> MnemoCore unit suites (${#MNEMO_UNIT_SUITES[@]})"
xcodebuild test-without-building -scheme ALADDIN -destination "$DEST" -derivedDataPath "$DD" \
  "${ONLY_TESTING_ARGS[@]}"

echo "==> MnemoAcademyUITests"
xcodebuild test-without-building -scheme ALADDIN -destination "$DEST" -derivedDataPath "$DD" \
  -only-testing:ALADDINUITests/MnemoAcademyUITests

echo "✅ mnemo_run_tests.sh finished"
