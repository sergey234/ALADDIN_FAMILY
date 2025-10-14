#!/bin/bash

# 🚀 ALADDIN Android - Полное исправление и запуск
# Скрипт для исправления ошибки "Module not specified" и запуска приложения

echo "🚀 ALADDIN Android - Полное исправление и запуск"
echo "================================================"

# Установка переменных окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"
export DYLD_LIBRARY_PATH="$ANDROID_HOME/emulator/lib64"

echo "📱 Переменные окружения:"
echo "JAVA_HOME: $JAVA_HOME"
echo "ANDROID_HOME: $ANDROID_HOME"

echo ""
echo "🔧 Шаг 1: Очистка проекта..."
./gradlew clean

echo ""
echo "🔧 Шаг 2: Синхронизация Gradle..."
./gradlew build --refresh-dependencies

echo ""
echo "🔧 Шаг 3: Сборка проекта..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo "✅ Проект успешно собран!"
    
    echo ""
    echo "📱 Шаг 4: Проверка APK..."
    if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
        echo "✅ APK файл найден!"
        ls -lh app/build/outputs/apk/debug/app-debug.apk
    else
        echo "❌ APK файл не найден!"
        exit 1
    fi
    
    echo ""
    echo "📱 Шаг 5: Проверка подключенных устройств..."
    adb devices
    
    echo ""
    echo "📱 Шаг 6: Попытка установки и запуска..."
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
        echo "📋 Инструкции:"
        echo "1. Запустите эмулятор через Android Studio (AVD Manager)"
        echo "2. Или подключите физическое Android устройство"
        echo "3. Повторите команду: ./fix_and_run.sh"
        echo ""
        echo "🚀 Открываем Android Studio для ручного запуска..."
        open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
    fi
else
    echo "❌ Ошибка сборки проекта!"
    echo "Проверьте логи выше для диагностики."
fi

echo ""
echo "🎯 Скрипт завершен!"
echo ""
echo "📋 Если возникли проблемы:"
echo "1. Прочитайте FIX_MODULE_ERROR.md"
echo "2. Проверьте APP_READINESS_REPORT.md"
echo "3. Запустите Android Studio вручную"

