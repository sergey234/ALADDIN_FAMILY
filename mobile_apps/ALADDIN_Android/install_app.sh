#!/bin/bash

# 🚀 ALADDIN Android App Installer
# Скрипт для установки Android приложения ALADDIN

echo "🚀 ALADDIN Android App Installer"
echo "================================="

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
echo "📱 Проверка подключенных устройств..."
adb devices

echo ""
echo "📱 Попытка установки APK..."
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
            echo "🎯 Проверьте устройство - приложение ALADDIN должно быть открыто!"
        else
            echo "❌ Ошибка запуска приложения"
        fi
    else
        echo "❌ Ошибка установки APK"
    fi
else
    echo "❌ Устройство не найдено!"
    echo ""
    echo "📋 Инструкции по подключению устройства:"
    echo "1. Подключите Android устройство по USB"
    echo "2. Включите режим разработчика"
    echo "3. Включите отладку по USB"
    echo "4. Запустите эмулятор через Android Studio"
    echo "5. Повторите команду: ./install_app.sh"
    echo ""
    echo "📋 Альтернативно:"
    echo "1. Скопируйте APK на устройство: app/build/outputs/apk/debug/app-debug.apk"
    echo "2. Установите APK вручную на устройстве"
fi

echo ""
echo "🎯 Установка завершена!"
