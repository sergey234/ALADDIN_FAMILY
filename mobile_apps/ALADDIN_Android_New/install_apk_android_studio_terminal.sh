#!/bin/bash

echo "📱 Установка APK через терминал Android Studio"
echo "============================================="

# Путь к APK файлу
APK_PATH="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/build/outputs/apk/debug/app-debug.apk"

# Проверяем наличие APK
if [ ! -f "$APK_PATH" ]; then
    echo "❌ APK не найден: $APK_PATH"
    exit 1
fi

echo "✅ APK найден: $APK_PATH"
echo "📏 Размер APK: $(ls -lh "$APK_PATH" | awk '{print $5}')"

# Настраиваем переменные окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$PATH"

echo "🔧 Переменные окружения настроены"

# Проверяем ADB
if [ ! -f "$ANDROID_HOME/platform-tools/adb" ]; then
    echo "❌ ADB не найден: $ANDROID_HOME/platform-tools/adb"
    exit 1
fi

echo "✅ ADB найден"

# Проверяем подключенные устройства
echo "📱 Проверка подключенных устройств..."
DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)

if [ "$DEVICES" -eq 0 ]; then
    echo "❌ Нет подключенных устройств"
    echo ""
    echo "🔧 Варианты решения:"
    echo "1. Подключите реальное Android устройство через USB"
    echo "2. Включите режим разработчика и USB отладку"
    echo "3. Или попробуйте запустить эмулятор:"
    echo "   - Откройте Android Studio"
    echo "   - Tools → AVD Manager"
    echo "   - Запустите любой эмулятор"
    echo ""
    echo "📱 Доступные эмуляторы:"
    $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager list avd | grep "Name:"
    exit 1
fi

echo "✅ Найдено устройств: $DEVICES"

# Показываем список устройств
echo "📱 Подключенные устройства:"
adb devices

echo ""
echo "📥 Установка APK на устройство..."
echo "Команда: adb install -r \"$APK_PATH\""

# Устанавливаем APK
adb install -r "$APK_PATH"

if [ $? -eq 0 ]; then
    echo "✅ APK успешно установлен!"
    echo ""
    echo "🚀 Запуск приложения ALADDIN..."
    
    # Запускаем приложение
    adb shell am start -n family.aladdin.android/.MainActivity
    
    if [ $? -eq 0 ]; then
        echo "✅ Приложение запущено!"
        echo ""
        echo "📱 Приложение ALADDIN теперь работает на устройстве!"
    else
        echo "⚠️ APK установлен, но не удалось запустить приложение"
        echo "💡 Попробуйте запустить вручную с устройства"
    fi
else
    echo "❌ Ошибка установки APK"
    echo ""
    echo "🔧 Возможные причины:"
    echo "1. Устройство заблокировано - разблокируйте экран"
    echo "2. USB отладка отключена - включите в настройках разработчика"
    echo "3. Недостаточно места на устройстве"
    echo "4. Конфликт с существующей версией приложения"
    exit 1
fi

echo ""
echo "🎉 Готово! Приложение ALADDIN установлено и запущено!"
