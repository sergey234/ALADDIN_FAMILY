#!/bin/bash

echo "🔍 CRASH DIAGNOSTICS TEST SCRIPT"
echo "================================="
echo ""

echo "Тестирование различных сценариев crash диагностики..."
echo ""

# Test 1: Normal build (with SSL pinning)
echo "🧪 ТЕСТ 1: Обычная сборка (с SSL pinning)"
echo "   - DISABLE_SSL_PINNING: не установлена"
echo "   - Ожидание: SSL pinning включен"
echo ""

# Test 2: Build with SSL pinning disabled
echo "🧪 ТЕСТ 2: Сборка с отключенным SSL pinning"
echo "   - DISABLE_SSL_PINNING: 1"
echo "   - Ожидание: SSL pinning отключен, подробные логи"
echo ""

echo "📋 Инструкции для тестирования:"
echo "1. Запустите приложение в симуляторе"
echo "2. Посмотрите логи в Xcode Console"
echo "3. Ищите сообщения с префиксами:"
echo "   - 💥💥💥 GLOBAL CRASH DETECTED (если crash)"
echo "   - 🔐 SSL PINNING: Final decision"
echo "   - 🌐🌐🌐 URLSessionDelegate (network logs)"
echo "   - 💥💥💥 CRASH PREVENTION (API errors)"
echo "   - 🧪🧪🧪 ISOLATED TESTING (network test)"
echo ""

echo "🎯 Ожидаемые результаты:"
echo "- Если crash из-за SSL pinning: тест 2 должен работать"
echo "- Если crash из-за сети: будут детальные логи"
echo "- Если crash из-за API: будет try-catch с подробностями"
echo ""

echo "🔧 Переменные окружения для тестирования:"
echo "DISABLE_SSL_PINNING=1 - отключает SSL pinning"
echo ""

echo "📱 Запуск в симуляторе:"
echo "1. Откройте ALADDIN.xcodeproj в Xcode"
echo "2. Выберите схему ALADDIN"
echo "3. Product → Scheme → Edit Scheme"
echo "4. Run → Arguments → Environment Variables"
echo "5. Добавьте DISABLE_SSL_PINNING=1"
echo "6. Запустите приложение"
echo ""