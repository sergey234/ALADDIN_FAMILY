#!/usr/bin/env bash
# r100 — wellness gates (раздельно: backend быстро, iOS — отдельно в Xcode).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_static() {
  ./scripts/verify_r100_ios_static.sh
}

run_backend() {
  run_static
  echo "== wellness l10n =="
  python3 scripts/check_wellness_l10n.py
  echo "== backend pytest =="
  PYTHONPATH=. python3 -m pytest Tests/test_wellness_*.py -q
  echo "OK — backend wellness gate"
}

run_ios_unit() {
  echo "== iOS WellnessModelsTests (5–15 min, лучше в Xcode: ⌘U на ALADDINUnitTests) =="
  SIM="${WELLNESS_IOS_SIM:-iPhone 16}"
  xcodebuild test \
    -project ALADDIN.xcodeproj \
    -scheme ALADDIN \
    -destination "platform=iOS Simulator,name=${SIM}" \
    -only-testing:ALADDINUnitTests/WellnessModelsTests
}

case "${1:-backend}" in
  static) run_static ;;
  backend) run_backend ;;
  ios-unit) run_ios_unit ;;
  all) run_backend; run_ios_unit ;;
  *) echo "Usage: $0 [static|backend|ios-unit|all]" >&2; exit 1 ;;
esac
