#!/bin/bash

echo "🚀 ЗАПУСК ЭМУЛЯТОРА И УСТАНОВКА APK"
echo "==================================="

# Устанавливаем переменные окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "📱 Запускаем эмулятор Pixel_7_Pro_API_34..."
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34 -no-snapshot-load -no-snapshot-save -no-boot-anim -no-audio -gpu off -memory 2048 &

echo "⏳ Ждем запуска эмулятора (30 секунд)..."
sleep 30

echo "🔍 Проверяем подключение..."
adb devices

echo "⏳ Ждем полной загрузки эмулятора (еще 30 секунд)..."
sleep 30

echo "📱 Проверяем доступные устройства..."
adb devices

echo ""
echo "📦 Устанавливаем APK..."
APK_PATH="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/build/outputs/apk/debug/app-debug.apk"

if [ -f "$APK_PATH" ]; then
    echo "✅ APK найден: $APK_PATH"
    echo "📏 Размер APK: $(ls -lh "$APK_PATH" | awk '{print $5}')"
    
    echo ""
    echo "🔄 Устанавливаем APK на эмулятор..."
    adb install -r "$APK_PATH"
    
    if [ $? -eq 0 ]; then
        echo "✅ APK успешно установлен!"
        
        echo ""
        echo "🚀 Запускаем приложение..."
        adb shell am start -n family.aladdin.android/.MainActivity
        
        if [ $? -eq 0 ]; then
            echo "✅ Приложение успешно запущено!"
            echo ""
            echo "📱 Приложение ALADDIN должно появиться на экране эмулятора!"
            echo "🎉 Поздравляем! Приложение работает!"
        else
            echo "❌ Ошибка при запуске приложения"
            echo "🔍 Проверяем логи..."
            adb logcat | grep -i aladdin | head -20
        fi
    else
        echo "❌ Ошибка при установке APK"
        echo "🔍 Проверяем статус эмулятора..."
        adb devices
    fi
else
    echo "❌ APK не найден: $APK_PATH"
fi

echo ""
echo "📋 Полезные команды:"
echo "   adb logcat | grep -i aladdin  # Просмотр логов"
echo "   adb shell pm list packages | grep aladdin  # Проверка установки"
echo "   adb uninstall family.aladdin.android  # Удаление приложения"
echo "   adb shell am start -n family.aladdin.android/.MainActivity  # Запуск приложения"

