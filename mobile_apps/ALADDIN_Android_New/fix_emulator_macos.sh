#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ ЭМУЛЯТОРА ДЛЯ ТЕСТИРОВАНИЯ"
echo "========================================="

# Настраиваем переменные
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"

echo "✅ Переменные окружения настроены"

# Создаем скрипт-обертку для исправления библиотек
cat > "$ANDROID_HOME/emulator/emulator_fixed" << 'EOF'
#!/bin/bash

# Экспортируем переменные для исправления проблем с библиотеками
export DYLD_LIBRARY_PATH="$ANDROID_SDK_PATH/emulator/lib64:$ANDROID_SDK_PATH/emulator/lib64/qt/lib:$DYLD_LIBRARY_PATH"
export QT_PLUGIN_PATH="$ANDROID_SDK_PATH/emulator/lib64/qt/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="$ANDROID_SDK_PATH/emulator/lib64/qt/plugins/platforms"

# Альтернативное решение - используем системные библиотеки
export DYLD_FALLBACK_LIBRARY_PATH="/usr/lib:/System/Library/Frameworks:/System/Library/PrivateFrameworks"

# Запускаем оригинальный эмулятор
exec "$ANDROID_SDK_PATH/emulator/emulator" "$@"
EOF

chmod +x "$ANDROID_HOME/emulator/emulator_fixed"

echo "✅ Скрипт-обертка создан"

# Проверяем доступные AVD
echo "📱 Доступные эмуляторы:"
$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager list avd

echo ""
echo "🚀 Попробуем запустить эмулятор с исправленными библиотеками..."
echo "Выберите эмулятор для запуска:"
echo "1. Pixel_3a_API_36_extension_level_17_x86_64"
echo "2. Pixel_7_Pro_API_34"

read -p "Введите номер (1 или 2): " choice

case $choice in
    1)
        AVD_NAME="Pixel_3a_API_36_extension_level_17_x86_64"
        ;;
    2)
        AVD_NAME="Pixel_7_Pro_API_34"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo "🚀 Запуск эмулятора $AVD_NAME..."

# Запускаем эмулятор с исправленными библиотеками
ANDROID_SDK_PATH="$ANDROID_HOME" "$ANDROID_HOME/emulator/emulator_fixed" -avd "$AVD_NAME" -no-snapshot-load -no-audio -no-window &

echo "⏳ Эмулятор запускается... Подождите 30-60 секунд"
echo "📱 После запуска эмулятора выполните:"
echo "   adb devices"
echo "   ./quick_install.sh"