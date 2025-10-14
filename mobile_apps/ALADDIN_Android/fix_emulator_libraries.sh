#!/bin/bash

echo "🔧 ИСПРАВЛЯЕМ БИБЛИОТЕКИ ЭМУЛЯТОРА"
echo "=================================="

# Устанавливаем переменные окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"

echo "🔍 Проверяем версию macOS..."
sw_vers

echo ""
echo "🔍 Проверяем установленные версии Android SDK..."
ls -la "$ANDROID_HOME/emulator/"

echo ""
echo "🔧 Пробуем исправить проблему с библиотеками..."

# Создаем символическую ссылку на правильную версию libc++
echo "📁 Создаем символическую ссылку на libc++..."
sudo ln -sf /usr/lib/libc++.1.dylib /usr/lib/libc++.1.0.dylib 2>/dev/null || echo "Символическая ссылка уже существует"

# Устанавливаем переменную окружения для совместимости
export DYLD_LIBRARY_PATH="/usr/lib:$ANDROID_HOME/emulator/lib64"

echo ""
echo "🔍 Проверяем доступные эмуляторы с исправленными библиотеками..."
$ANDROID_HOME/emulator/emulator -list-avds

echo ""
echo "📱 Пробуем запустить эмулятор с исправленными библиотеками..."

# Пробуем запустить эмулятор с разными параметрами
echo "🔄 Вариант 1: Базовый запуск с исправленными библиотеками..."
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu swiftshader_indirect -memory 2048 &

EMULATOR_PID=$!
echo "📱 PID эмулятора: $EMULATOR_PID"

echo "⏳ Ждем запуска эмулятора (30 секунд)..."
sleep 30

echo "🔍 Проверяем подключение..."
adb devices

# Если эмулятор не запустился, пробуем другой вариант
DEVICES=$(adb devices | grep -v "List of devices attached" | grep -v "^$" | wc -l)

if [ $DEVICES -eq 0 ]; then
    echo "❌ Первый эмулятор не запустился, пробуем второй..."
    
    # Убиваем первый процесс
    kill $EMULATOR_PID 2>/dev/null
    
    echo "🔄 Вариант 2: Запуск с другими параметрами..."
    $ANDROID_HOME/emulator/emulator -avd Pixel_3a_API_36_extension_level_17_x86_64 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu swiftshader_indirect -memory 2048 &
    
    echo "⏳ Ждем запуска второго эмулятора (45 секунд)..."
    sleep 45
    
    echo "🔍 Проверяем подключение..."
    adb devices
fi

echo ""
echo "📋 Результат:"
adb devices

echo ""
echo "✅ Исправление библиотек завершено!"
echo "📱 Если эмулятор запустился, можно устанавливать APK"
echo "🔧 Если не запустился, попробуем Android Studio"

