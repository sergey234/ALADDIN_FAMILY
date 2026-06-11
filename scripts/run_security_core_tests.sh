#!/usr/bin/env bash
# Security core unit tests for CI (B7-UT-01 / ALADDINUnitTests — not legacy ALADDINTests).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEST="${DESTINATION:-platform=iOS Simulator,name=iPhone 13 Pro Max,OS=18.4}"

SUITES=(
  AppConfigTests
  SecurityVerdictModelsTests
  DeviceEicarScanTests
  DeviceThreatCatalogTests
  IdentityMonitorViewModelTests
  IdentityFraudThreatCatalogTests
  FamilyChildThreatCatalogTests
  ParentalMonitoringValidationTests
  AntifakeSharePayloadStoreTests
  AntifakeDeepLinkRouterTests
  AIPIIRedactorTests
  FamilyE2EECryptoEngineTests
  DEFENSIVEJWTTests
  WellnessModelsTests
  NetworkManagerTests
  APIServiceTests
  LocalizationManagerTests
)

ARGS=()
for suite in "${SUITES[@]}"; do
  ARGS+=("-only-testing:ALADDINUnitTests/${suite}")
done

xcodebuild test \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -destination "$DEST" \
  -configuration Debug \
  "${ARGS[@]}"
