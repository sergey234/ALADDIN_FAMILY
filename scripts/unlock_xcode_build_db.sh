#!/usr/bin/env bash
# Снимает "database is locked" / "unable to attach DB" для ALADDIN.
# Причина: Xcode IDE + xcodebuild (или Cursor) собирают проект одновременно.
set -euo pipefail

echo "==> Останавливаем Xcode и все сборки ALADDIN…"
osascript -e 'tell application "Xcode" to quit' 2>/dev/null || true
pkill -9 -f "xcodebuild.*ALADDIN" 2>/dev/null || true
pkill -9 -f "xcodebuild" 2>/dev/null || true
pkill -9 -f "swift-frontend" 2>/dev/null || true
pkill -9 -x Xcode 2>/dev/null || true
sleep 2

DD="$HOME/Library/Developer/Xcode/DerivedData"
while IFS= read -r -d '' folder; do
  echo "==> Удаляем заблокированный кэш: $folder/Build"
  rm -rf "$folder/Build"
done < <(find "$DD" -maxdepth 1 -type d -name 'ALADDIN-*' -print0 2>/dev/null || true)

echo "✓ build.db разблокирован. Собирайте только из одного места: Xcode ИЛИ терминал."
echo "  Откройте Xcode → Product → Build (Cmd+B). Не запускайте xcodebuild параллельно."
