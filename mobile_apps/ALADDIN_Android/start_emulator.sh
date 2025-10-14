#!/bin/bash

# 🚀 ALADDIN Android Emulator Launcher
# Скрипт для запуска эмулятора Android

echo "🚀 ALADDIN Android Emulator Launcher"
echo "===================================="

# Установка переменных окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "📱 Переменные окружения:"
echo "ANDROID_HOME: $ANDROID_HOME"
echo "DYLD_LIBRARY_PATH: $DYLD_LIBRARY_PATH"

echo ""
echo "📱 Доступные эмуляторы:"
$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager list avd

echo ""
echo "📱 Попытка запуска Pixel_7_Pro_API_34..."

# Попробуем разные варианты запуска
echo "Вариант 1: Базовый запуск"
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save &
EMULATOR_PID=$!

echo "⏳ Ожидание 30 секунд..."
sleep 30

echo ""
echo "📱 Проверка статуса эмулятора..."
adb devices

if adb devices | grep -q "device"; then
    echo "✅ Эмулятор запущен успешно!"
    echo "📱 Установка APK..."
    adb install -r app/build/outputs/apk/debug/app-debug.apk
    
    echo "📱 Запуск приложения ALADDIN..."
    adb shell am start -n family.aladdin.android/.MainActivity
    
    echo "✅ Приложение запущено! Проверьте эмулятор."
else
    echo "❌ Эмулятор не запустился. Попробуем другой вариант..."
    
    # Убиваем предыдущий процесс
    kill $EMULATOR_PID 2>/dev/null
    
    echo "Вариант 2: Запуск с отключенной графикой"
    $ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu off -memory 2048 &
    
    echo "⏳ Ожидание 45 секунд..."
    sleep 45
    
    echo "📱 Проверка статуса эмулятора..."
    adb devices
    
    if adb devices | grep -q "device"; then
        echo "✅ Эмулятор запущен успешно!"
        echo "📱 Установка APK..."
        adb install -r app/build/outputs/apk/debug/app-debug.apk
        
        echo "📱 Запуск приложения ALADDIN..."
        adb shell am start -n family.aladdin.android/.MainActivity
        
        echo "✅ Приложение запущено! Проверьте эмулятор."
    else
        echo "❌ Эмулятор не запустился. Попробуйте запустить через Android Studio."
    fi
fi

echo ""
echo "🎯 Скрипт завершен!"

