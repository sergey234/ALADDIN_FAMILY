#!/bin/bash

# 🚀 ALADDIN Android App Test Script
# Скрипт для тестирования Android приложения ALADDIN

echo "🚀 ALADDIN Android App Test Script"
echo "=================================="

# Установка переменных окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"

echo "📱 Проверка Android SDK..."
echo "ANDROID_HOME: $ANDROID_HOME"
echo "JAVA_HOME: $JAVA_HOME"

echo ""
echo "📱 Проверка доступных эмуляторов..."
$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager list avd

echo ""
echo "📱 Проверка подключенных устройств..."
adb devices

echo ""
echo "📱 Попытка запуска эмулятора..."
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu swiftshader_indirect &

echo "⏳ Ожидание запуска эмулятора (60 секунд)..."
sleep 60

echo ""
echo "📱 Проверка подключенных устройств после запуска..."
adb devices

echo ""
echo "📱 Попытка установки APK..."
if adb devices | grep -q "device"; then
    echo "✅ Устройство найдено! Устанавливаем APK..."
    adb install -r app/build/outputs/apk/debug/app-debug.apk
    
    echo ""
    echo "📱 Запуск приложения ALADDIN..."
    adb shell am start -n family.aladdin.android/.MainActivity
    
    echo ""
    echo "✅ Приложение запущено! Проверьте эмулятор."
else
    echo "❌ Устройство не найдено. Попробуйте запустить эмулятор вручную."
fi

echo ""
echo "🎯 Тестирование завершено!"
