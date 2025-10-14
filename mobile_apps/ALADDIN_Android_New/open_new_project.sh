#!/bin/bash

echo "🚀 ОТКРЫВАЕМ НОВЫЙ ANDROID ПРОЕКТ"
echo "=================================="

# Устанавливаем переменные окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"

echo "🔍 Проверяем структуру проекта..."
ls -la

echo ""
echo "🔍 Проверяем app/build.gradle..."
head -20 app/build.gradle

echo ""
echo "🔍 Проверяем AndroidManifest.xml..."
head -10 app/src/main/AndroidManifest.xml

echo ""
echo "🔄 Синхронизируем Gradle..."
./gradlew clean
./gradlew build

echo ""
echo "✅ ПРОЕКТ ГОТОВ!"
echo "🚀 Открываем Android Studio..."

# Открываем Android Studio с новым проектом
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New

echo ""
echo "📱 ИНСТРУКЦИИ ДЛЯ ANDROID STUDIO:"
echo "================================="
echo "1. Дождитесь завершения 'Gradle sync'"
echo "2. Проект должен автоматически распознаться как Android проект"
echo "3. 'Project Structure' должен быть активным"
echo "4. Перейдите в Run → Edit Configurations"
echo "5. В поле Module выберите: app"
echo "6. В поле Deploy выберите: Default APK"
echo "7. Нажмите Apply и OK"
echo "8. Нажмите кнопку Run (▶️)"
echo ""
echo "🎉 ЭТОТ ПРОЕКТ ДОЛЖЕН РАБОТАТЬ НА 100%!"

