#!/bin/bash

echo "🚀 ПРЯМОЙ ЗАПУСК APK (ОБХОДИМ ANDROID STUDIO)"
echo "=============================================="

# Устанавливаем переменные окружения
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "📱 Проверяем доступные устройства..."
adb devices

echo ""
echo "🔍 Ищем запущенные эмуляторы..."
adb devices | grep emulator

echo ""
echo "📦 Устанавливаем APK..."
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
            echo "🔍 Проверьте логи:"
            adb logcat | grep -i aladdin
        fi
    else
        echo "❌ Ошибка при установке APK"
        echo "🔍 Проверьте подключение устройства"
    fi
else
    echo "❌ APK не найден: $APK_PATH"
    echo "🔧 Собираем APK заново..."
    ./gradlew assembleDebug
fi

echo ""
echo "📋 Дополнительные команды:"
echo "   adb logcat | grep -i aladdin  # Просмотр логов"
echo "   adb shell pm list packages | grep aladdin  # Проверка установки"
echo "   adb uninstall family.aladdin.android  # Удаление приложения"
