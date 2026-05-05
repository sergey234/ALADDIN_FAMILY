#!/usr/bin/env bash
# Снимок файлов iOS, связанных с семьёй / join / лимитами / главной (перед работой по API).
# По умолчанию: копии в docs/backup/family-mobile-snapshot-<дата>-<время>/ (см. .gitignore).
# Использование:
#   ./scripts/snapshot_family_mobile_sources.sh
#   DEST="$HOME/Desktop/aladdin_family_ios_backup" ./scripts/snapshot_family_mobile_sources.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${DEST:-$ROOT/docs/backup/family-mobile-snapshot-$STAMP}"

FILES=(
  "Core/Network/APIService.swift"
  "Core/Config/AppConfig.swift"
  "Core/Network/NetworkManager.swift"
  "ViewModels/FamilyRegistrationViewModel.swift"
  "Shared/Components/Modals/InvitationCodeInputModal.swift"
  "Core/Managers/SubscriptionManager.swift"
  "Screens/02_FamilyScreen.swift"
  "Screens/01_MainScreen.swift"
  "ViewModels/MainViewModel.swift"
  "Core/Managers/FamilyLocalStore.swift"
  "Tests/UnitTests/SubscriptionFamilyLimitsTests.swift"
  "docs/server/BACKEND_FAMILY_JOIN_AND_ADD_GATE.md"
  "docs/FAMILY_API_SMOKE_REGIMEN.md"
  "docs/BACKEND_FAMILY_ROLLOUT_SAVEPOINT_AND_PLAN.md"
  "docs/REGISTRATION_AND_TARIFF_MAIN_SCREEN_ML_REFERENCE.md"
  "docs/REGISTRATION_AND_MAIN_TARIFF_CARD.md"
  "docs/release/current/openapi.json"
  "docs/FAMILY_MOBILE_SNAPSHOT_README.md"
)

mkdir -p "$OUT"
echo "ALADDIN family-related iOS snapshot" > "$OUT/README.txt"
echo "Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT/README.txt"
echo "Root: $ROOT" >> "$OUT/README.txt"
echo "" >> "$OUT/README.txt"

for rel in "${FILES[@]}"; do
  src="$ROOT/$rel"
  if [[ ! -f "$src" ]]; then
    echo "MISSING: $rel" >> "$OUT/README.txt"
    continue
  fi
  dst="$OUT/$rel"
  mkdir -p "$(dirname "$dst")"
  cp -f "$src" "$dst"
  echo "OK: $rel" >> "$OUT/README.txt"
done

echo ""
echo "Snapshot written to: $OUT"
echo "Run from repo: (cd \"$OUT\" && find . -type f | head)"
