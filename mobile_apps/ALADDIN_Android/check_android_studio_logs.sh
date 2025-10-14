#!/bin/bash

echo "🔍 ПРОВЕРЯЕМ ЛОГИ ANDROID STUDIO"
echo "================================="

# Проверяем логи Android Studio
echo "📋 Логи Android Studio:"
tail -n 50 ~/Library/Logs/AndroidStudio*/idea.log 2>/dev/null || echo "Логи не найдены"

echo ""
echo "📋 Логи Gradle:"
tail -n 20 ~/.gradle/daemon/*/daemon-*.out.log 2>/dev/null || echo "Логи Gradle не найдены"

echo ""
echo "📋 Проверяем статус проекта:"
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
echo "Текущая папка: $(pwd)"
echo "Содержимое:"
ls -la

echo ""
echo "📋 Проверяем Gradle wrapper:"
./gradlew --version

