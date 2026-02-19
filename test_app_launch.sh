#!/bin/bash

# Скрипт для тестирования запуска приложения ALADDIN в симуляторе
# Проверяет, что синий экран онбординга исправлен

echo "🔍 Тестирование запуска ALADDIN в симуляторе..."
echo "📱 Цель: Проверить отсутствие синего экрана при входе в онбординг"
echo ""

# Проверяем, что Xcode доступен
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode не найден. Установите Xcode."
    exit 1
fi

# Переходим в директорию проекта
cd "$(dirname "$0")" || exit 1

echo "🏗️ Компиляция приложения..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,id=A45A91AB-838D-4C72-9EAA-B6707D1DB851' build ONLY_ACTIVE_ARCH=YES; then
    echo "✅ Компиляция успешна!"
    echo ""
    echo "🚀 Запуск приложения в симуляторе..."
    echo "📝 Проверьте логи в Xcode console на отсутствие зависания"
    echo "🎯 Ожидаемый результат: Онбординг должен загрузиться без синего экрана"
    echo ""
    echo "💡 Инструкции:"
    echo "1. Если приложение зависает - проблема не решена"
    echo "2. Если онбординг загружается - проблема исправлена!"
    echo "3. Проверьте логи на наличие '🚨 OnboardingScreen загружен!'"
else
    echo "❌ Ошибка компиляции"
    exit 1
fi