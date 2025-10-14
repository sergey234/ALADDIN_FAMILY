#!/bin/bash

echo "☕ Настройка Java окружения для ALADDIN Android"
echo "=============================================="

# Устанавливаем переменные окружения для Java из Android Studio
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

echo "✅ JAVA_HOME установлен: $JAVA_HOME"

# Проверяем Java
echo "🔍 Проверка Java:"
java -version

# Проверяем JavaC
echo "🔍 Проверка JavaC:"
javac -version

# Устанавливаем переменные для Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"

echo "✅ ANDROID_HOME установлен: $ANDROID_HOME"

# Проверяем Android SDK
if [ -d "$ANDROID_HOME" ]; then
    echo "✅ Android SDK найден"
else
    echo "❌ Android SDK не найден в $ANDROID_HOME"
    echo "📥 Установите Android SDK через Android Studio"
fi

# Проверяем ADB
if [ -f "$ANDROID_HOME/platform-tools/adb" ]; then
    echo "✅ ADB найден"
else
    echo "❌ ADB не найден"
fi

echo ""
echo "🚀 Теперь можно запускать Gradle команды!"
echo "Пример: ./gradlew assembleDebug"
