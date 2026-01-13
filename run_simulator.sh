#!/bin/bash

echo "🚀 Запуск приложения в симуляторе iPhone 11 Pro Max..."

# Находим симулятор
SIMULATOR_ID=$(xcrun simctl list devices booted | grep "iPhone 11 Pro Max" | grep -oE '[A-F0-9-]{36}' | head -1)

if [ -z "$SIMULATOR_ID" ]; then
    echo "📱 Запускаю симулятор..."
    xcrun simctl boot "iPhone 11 Pro Max" 2>&1
    sleep 3
    SIMULATOR_ID=$(xcrun simctl list devices booted | grep "iPhone 11 Pro Max" | grep -oE '[A-F0-9-]{36}' | head -1)
fi

if [ -z "$SIMULATOR_ID" ]; then
    echo "❌ Не удалось запустить симулятор"
    exit 1
fi

echo "✅ Симулятор запущен: $SIMULATOR_ID"

# Находим приложение
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/ALADDIN-*/Build/Products/Debug-iphonesimulator -name "ALADDIN.app" -type d 2>/dev/null | head -1)

if [ -z "$APP_PATH" ]; then
    echo "❌ Приложение не найдено. Собираю проект..."
    cd "$(dirname "$0")"
    xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 11 Pro Max' build 2>&1 | tail -3
    APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/ALADDIN-*/Build/Products/Debug-iphonesimulator -name "ALADDIN.app" -type d 2>/dev/null | head -1)
fi

if [ -z "$APP_PATH" ]; then
    echo "❌ Не удалось найти приложение после сборки"
    exit 1
fi

echo "📦 Устанавливаю приложение: $APP_PATH"
xcrun simctl install "$SIMULATOR_ID" "$APP_PATH" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Приложение установлено!"
    echo "🚀 Запускаю приложение..."
    xcrun simctl launch "$SIMULATOR_ID" family.aladdin.ios 2>&1
    echo "✅ Приложение запущено в симуляторе!"
else
    echo "❌ Ошибка при установке приложения"
    exit 1
fi


