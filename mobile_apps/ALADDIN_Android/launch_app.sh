#!/bin/bash

# 🚀 ALADDIN Android App Launcher
# Скрипт для запуска Android приложения ALADDIN

echo "🚀 ALADDIN Android App Launcher"
echo "==============================="

# Установка переменных окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "📱 Переменные окружения:"
echo "JAVA_HOME: $JAVA_HOME"
echo "ANDROID_HOME: $ANDROID_HOME"

echo ""
echo "📱 Проверка APK файла..."
if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
    echo "✅ APK файл найден!"
    ls -lh app/build/outputs/apk/debug/app-debug.apk
else
    echo "❌ APK файл не найден! Сначала соберите проект."
    exit 1
fi

echo ""
echo "📱 Попытка запуска эмулятора..."
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu off -memory 2048 &
EMULATOR_PID=$!

echo "⏳ Ожидание запуска эмулятора (45 секунд)..."
sleep 45

echo ""
echo "📱 Проверка подключенных устройств..."
adb devices

if adb devices | grep -q "device"; then
    echo "✅ Устройство найдено! Устанавливаем APK..."
    adb install -r app/build/outputs/apk/debug/app-debug.apk
    
    if [ $? -eq 0 ]; then
        echo "✅ APK успешно установлен!"
        
        echo ""
        echo "📱 Запуск приложения ALADDIN..."
        adb shell am start -n family.aladdin.android/.MainActivity
        
        if [ $? -eq 0 ]; then
            echo "✅ Приложение успешно запущено!"
            echo "🎯 Проверьте эмулятор - приложение ALADDIN должно быть открыто!"
            echo ""
            echo "📱 Информация о приложении:"
            echo "   - Название: ALADDIN - AI Защита Семьи"
            echo "   - Пакет: family.aladdin.android"
            echo "   - Версия: 1.0 Debug"
            echo "   - Размер: 39 MB"
        else
            echo "❌ Ошибка запуска приложения"
        fi
    else
        echo "❌ Ошибка установки APK"
    fi
else
    echo "❌ Устройство не найдено!"
    echo ""
    echo "📋 Инструкции:"
    echo "1. Запустите эмулятор через Android Studio (AVD Manager)"
    echo "2. Или подключите физическое Android устройство"
    echo "3. Повторите команду: ./launch_app.sh"
    echo ""
    echo "🚀 Открываем Android Studio для ручного запуска..."
    open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
fi

echo ""
echo "🎯 Скрипт завершен!"

