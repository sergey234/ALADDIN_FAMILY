#!/bin/bash

# 🚀 ALADDIN Quick Install Script
# Быстрая установка APK без эмулятора

echo "🚀 ALADDIN Quick Install Script"
echo "==============================="

# Установка переменных окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"

echo "📱 Переменные окружения:"
echo "JAVA_HOME: $JAVA_HOME"
echo "ANDROID_HOME: $ANDROID_HOME"

echo ""
echo "📱 Проверка APK файла..."
if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
    echo "✅ APK файл найден!"
    ls -lh app/build/outputs/apk/debug/app-debug.apk
    echo ""
    echo "📱 Информация о APK:"
    echo "Размер: $(du -h app/build/outputs/apk/debug/app-debug.apk | cut -f1)"
    echo "Дата создания: $(stat -f "%Sm" app/build/outputs/apk/debug/app-debug.apk)"
else
    echo "❌ APK файл не найден!"
    exit 1
fi

echo ""
echo "📱 Попытка найти подключенные устройства..."
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
    echo ""
    echo "1. 📱 Подключите Android устройство по USB"
    echo "   - Включите режим разработчика"
    echo "   - Включите отладку по USB"
    echo ""
    echo "2. 🖥️ Запустите эмулятор через Android Studio"
    echo "   - Откройте Android Studio"
    echo "   - Tools → AVD Manager"
    echo "   - Запустите Pixel_7_Pro_API_34"
    echo ""
    echo "3. 📦 Альтернативно - установите APK вручную"
    echo "   - Скопируйте APK на устройство:"
    echo "     cp app/build/outputs/apk/debug/app-debug.apk /path/to/device/"
    echo "   - Установите APK на устройстве"
    echo ""
    echo "4. 🔄 После подключения устройства повторите команду:"
    echo "   ./quick_install.sh"
fi

echo ""
echo "🎯 Скрипт завершен!"

