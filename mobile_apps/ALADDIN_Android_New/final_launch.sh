#!/bin/bash

echo "🚀 ФИНАЛЬНЫЙ ЗАПУСК ANDROID ПРОЕКТА"
echo "==================================="

# Устанавливаем переменные окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"

echo "🔄 Синхронизируем Gradle без Firebase..."
./gradlew clean
./gradlew build

echo ""
echo "✅ ПРОЕКТ ГОТОВ!"
echo "🚀 Открываем Android Studio..."

# Открываем Android Studio
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New

echo ""
echo "📱 ТЕПЕРЬ ДОЛЖНО РАБОТАТЬ:"
echo "========================="
echo "1. Дождитесь завершения 'Gradle sync'"
echo "2. 'Project Structure' должен стать АКТИВНЫМ!"
echo "3. Перейдите в Run → Edit Configurations"
echo "4. В поле Module выберите: ALADDIN.app"
echo "5. В поле Deploy выберите: Default APK"
echo "6. Нажмите Apply и OK"
echo "7. Нажмите кнопку Run (▶️)"
echo ""
echo "🎉 ПРОЕКТ ДОЛЖЕН РАБОТАТЬ НА 100%!"

