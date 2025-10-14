#!/bin/bash

echo "🚀 СОЗДАНИЕ AAB ФАЙЛА ЧЕРЕЗ ТЕРМИНАЛ"
echo "===================================="

# Переходим в папку проекта
cd "/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"

echo "📁 Текущая директория: $(pwd)"

# Проверяем наличие keystore
if [ ! -f "aladdin-release-key.keystore" ]; then
    echo "❌ Keystore не найден! Сначала создайте keystore:"
    echo "   ./create_release_keystore.sh"
    exit 1
fi

echo "✅ Keystore найден: aladdin-release-key.keystore"

# Настраиваем Java
echo "☕ Настройка Java..."
source setup_java_env.sh

# Синхронизируем Gradle
echo "🔄 Синхронизация Gradle..."
./gradlew clean

# Создаем AAB файл
echo "📦 Создание AAB файла..."
./gradlew bundleRelease

if [ $? -eq 0 ]; then
    echo "✅ AAB файл создан успешно!"
    echo ""
    echo "📁 Расположение AAB файла:"
    echo "   app/build/outputs/bundle/release/app-release.aab"
    echo ""
    
    # Проверяем размер файла
    AAB_FILE="app/build/outputs/bundle/release/app-release.aab"
    if [ -f "$AAB_FILE" ]; then
        SIZE=$(ls -lh "$AAB_FILE" | awk '{print $5}')
        echo "📏 Размер AAB файла: $SIZE"
        echo "📅 Дата создания: $(ls -l "$AAB_FILE" | awk '{print $6, $7, $8}')"
        echo ""
        echo "🎉 ГОТОВО! AAB файл создан!"
        echo ""
        echo "📱 Следующие шаги:"
        echo "1. Зарегистрироваться в Google Play Console"
        echo "2. Загрузить AAB файл: $AAB_FILE"
        echo "3. Заполнить описания приложения"
        echo "4. Опубликовать приложение"
    else
        echo "❌ AAB файл не найден в ожидаемом месте"
        exit 1
    fi
else
    echo "❌ Ошибка создания AAB файла"
    echo ""
    echo "🔧 Возможные причины:"
    echo "1. Проблемы с keystore"
    echo "2. Ошибки в build.gradle"
    echo "3. Проблемы с зависимостями"
    echo ""
    echo "💡 Попробуйте через Android Studio:"
    echo "   Build → Generate Signed Bundle/APK"
    exit 1
fi

echo ""
echo "🚀 AAB файл готов для загрузки в Google Play!"
