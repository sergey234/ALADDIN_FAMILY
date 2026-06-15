#!/usr/bin/env bash
# D-01 — Archive for TestFlight (Call Directory + Antifake Share embedded).
#
# Requires env (see fastlane/Fastfile):
#   APP_PROFILE_UUID, PROVISIONING_PROFILE_EXTENSION_UUID
#   PROVISIONING_PROFILE_CALL_DIRECTORY_UUID (recommended)
#   PROVISIONING_PROFILE_ANTIFAKE_SHARE_UUID (optional)
#   APPLE_TEAM_ID, DIST_CERT_NAME
#
# Usage:
#   ./scripts/archive_antifake_device_build.sh
#   ./scripts/archive_antifake_device_build.sh --simulator-only
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--simulator-only" ]]; then
  DEST="${ANTIFAKE_SIM_DEST:-platform=iOS Simulator,id=A900C6B0-6E81-4779-9305-E32CAA039BF6}"
  echo ">>> D-01 simulator build (no signing): ${DEST}"
  xcodebuild \
    -project ALADDIN.xcodeproj \
    -scheme ALADDIN \
    -configuration Debug \
    -destination "${DEST}" \
    -quiet \
    build
  echo "OK simulator build"
  exit 0
fi

if ! command -v bundle >/dev/null 2>&1; then
  echo "ERROR: bundle not found — install Ruby bundler or use --simulator-only"
  exit 1
fi

echo ">>> D-01 fastlane archive (Release)"
bundle exec fastlane ios build_archive
