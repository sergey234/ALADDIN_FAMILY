#!/bin/bash

echo "🔧 ИСПРАВЛЯЕМ ЭМУЛЯТОР И УСТАНАВЛИВАЕМ APK"
echo "=========================================="

# Устанавливаем переменные окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "🔍 Проверяем доступные эмуляторы..."
$ANDROID_HOME/emulator/emulator -list-avds

echo ""
echo "📱 Пробуем запустить эмулятор с исправлением библиотек..."

# Пробуем разные варианты запуска эмулятора
echo "🔄 Вариант 1: Базовый запуск..."
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu swiftshader_indirect &

EMULATOR_PID=$!
echo "📱 PID эмулятора: $EMULATOR_PID"

echo "⏳ Ждем запуска эмулятора (45 секунд)..."
sleep 45

echo "🔍 Проверяем подключение..."
adb devices

echo "⏳ Ждем полной загрузки эмулятора (еще 30 секунд)..."
sleep 30

echo "📱 Проверяем доступные устройства..."
adb devices

# Проверяем, есть ли подключенные устройства
DEVICES=$(adb devices | grep -v "List of devices attached" | grep -v "^$" | wc -l)

if [ $DEVICES -gt 0 ]; then
    echo "✅ Устройство найдено! Устанавливаем APK..."
    
    APK_PATH="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/build/outputs/apk/debug/app-debug.apk"
    
    if [ -f "$APK_PATH" ]; then
        echo "✅ APK найден: $APK_PATH"
        echo "📏 Размер APK: $(ls -lh "$APK_PATH" | awk '{print $5}')"
        
        echo ""
        echo "🔄 Устанавливаем APK на устройство..."
        adb install -r "$APK_PATH"
        
        if [ $? -eq 0 ]; then
            echo "✅ APK успешно установлен!"
            
            echo ""
            echo "🚀 Запускаем приложение..."
            adb shell am start -n family.aladdin.android/.MainActivity
            
            if [ $? -eq 0 ]; then
                echo "✅ Приложение успешно запущено!"
                echo ""
                echo "📱 Приложение ALADDIN должно появиться на экране устройства!"
                echo "🎉 Поздравляем! Приложение работает!"
            else
                echo "❌ Ошибка при запуске приложения"
                echo "🔍 Проверяем логи..."
                adb logcat | grep -i aladdin | head -10
            fi
        else
            echo "❌ Ошибка при установке APK"
            echo "🔍 Проверяем статус устройства..."
            adb devices
        fi
    else
        echo "❌ APK не найден: $APK_PATH"
    fi
else
    echo "❌ Устройства не найдены"
    echo "🔍 Пробуем альтернативные способы..."
    
    echo ""
    echo "📱 Пробуем запустить другой эмулятор..."
    $ANDROID_HOME/emulator/emulator -avd Pixel_3a_API_36_extension_level_17_x86_64 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu swiftshader_indirect &
    
    echo "⏳ Ждем запуска второго эмулятора (60 секунд)..."
    sleep 60
    
    echo "🔍 Проверяем подключение..."
    adb devices
    
    DEVICES=$(adb devices | grep -v "List of devices attached" | grep -v "^$" | wc -l)
    
    if [ $DEVICES -gt 0 ]; then
        echo "✅ Второй эмулятор работает! Устанавливаем APK..."
        adb install -r "$APK_PATH"
        adb shell am start -n family.aladdin.android/.MainActivity
    else
        echo "❌ Эмуляторы не запускаются"
        echo "🔧 Рекомендации:"
        echo "   1. Перезагрузите компьютер"
        echo "   2. Обновите Android SDK"
        echo "   3. Используйте физическое устройство"
        echo "   4. Попробуйте другой эмулятор"
    fi
fi

echo ""
echo "📋 Полезные команды:"
echo "   adb devices  # Список устройств"
echo "   adb logcat | grep -i aladdin  # Просмотр логов"
echo "   adb shell pm list packages | grep aladdin  # Проверка установки"
echo "   adb uninstall family.aladdin.android  # Удаление приложения"
echo "   adb shell am start -n family.aladdin.android/.MainActivity  # Запуск приложения"

