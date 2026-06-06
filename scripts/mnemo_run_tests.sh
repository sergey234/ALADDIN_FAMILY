#!/usr/bin/env bash
# MNEMO-B15-T02: MnemoCore v3 unit suites + UITest smoke (CI-friendly).
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${MNEMO_TEST_DEST:-platform=iOS Simulator,name=iPhone 16}"

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
xcodebuild test -scheme ALADDIN -destination "$DEST" \
  "${ONLY_TESTING_ARGS[@]}" \
  | xcpretty || true

echo "==> MnemoAcademyUITests"
xcodebuild test -scheme ALADDIN -destination "$DEST" \
  -only-testing:ALADDINUITests/MnemoAcademyUITests \
  | xcpretty || true

echo "✅ mnemo_run_tests.sh finished"
