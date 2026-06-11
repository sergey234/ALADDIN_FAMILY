#!/usr/bin/env bash
# Восстанавливает Swift Package Manager (RiveRuntime) для ALADDIN.xcodeproj.
# Запускать при ошибке Xcode: "Missing package product 'RiveRuntime'".
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> ALADDIN iOS — resolve SPM (RiveRuntime 6.20.5)"
echo "    Simulator target: iPhone 13 Pro Max (единственный)"
echo "    Закройте Xcode (Cmd+Q) перед запуском."
pkill -f "xcodebuild.*ALADDIN" 2>/dev/null || true
sleep 1

bash "$ROOT/scripts/reset_rive_spm_cache.sh"

xcodebuild -resolvePackageDependencies \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN

# Xcode 15+ иногда читает Package.resolved из обоих путей.
RESOLVED="ALADDIN.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved"
mkdir -p ALADDIN.xcodeproj/xcshareddata/swiftpm
cp -f "$RESOLVED" ALADDIN.xcodeproj/xcshareddata/swiftpm/Package.resolved

echo ""
echo "==> Проверка сборки (симулятор)..."
if xcodebuild -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13 Pro Max' \
  -quiet build; then
  echo "BUILD SUCCEEDED — RiveRuntime подключён."
else
  echo "BUILD FAILED — закройте Xcode (Cmd+Q), выполните:"
  echo "  rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-*"
  echo "  $0"
  exit 1
fi

echo ""
echo "Готово. Откройте ALADDIN.xcodeproj в Xcode — ошибка Missing package должна исчезнуть."
