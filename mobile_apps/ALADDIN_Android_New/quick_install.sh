#!/bin/bash

echo "🚀 БЫСТРАЯ УСТАНОВКА APK ALADDIN"
echo "================================"

# Настраиваем переменные
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

# APK файл
APK="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/build/outputs/apk/debug/app-debug.apk"

echo "📱 Проверка устройств..."
adb devices

echo ""
echo "📥 Установка APK..."
adb install -r "$APK"

if [ $? -eq 0 ]; then
    echo "✅ Установлено! Запускаем..."
    adb shell am start -n family.aladdin.android/.MainActivity
    echo "🎉 Готово!"
else
    echo "❌ Ошибка установки"
fi

