#!/bin/bash

echo "🔧 НАСТРОЙКА ANDROID STUDIO"
echo "============================"

PROJECT_PATH="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"
cd "$PROJECT_PATH" || exit

echo "📁 Текущая директория: $(pwd)"

# Настройка Java
echo "☕ Настройка Java..."
source setup_java_env.sh

# Очистка проекта
echo "🧹 Очистка проекта..."
./gradlew clean

# Синхронизация Gradle
echo "🔄 Синхронизация Gradle..."
./gradlew build

echo ""
echo "✅ Android Studio настроен!"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ В ANDROID STUDIO:"
echo "1. File → Sync Project with Gradle Files"
echo "2. Дождитесь синхронизации (2-3 минуты)"
echo "3. Run → Edit Configurations"
echo "4. Выберите 'ALADDIN Debug'"
echo "5. Убедитесь что Module: ALADDIN_Android_New.app"
echo ""
echo "🎯 Теперь Android Studio должен работать!"
