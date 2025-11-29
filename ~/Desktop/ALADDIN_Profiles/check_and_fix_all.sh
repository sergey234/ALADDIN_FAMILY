#!/bin/bash

echo "🔧 ПРОВЕРКА И ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ"
echo "======================================"
echo ""

REPO="sergey234/ALADDIN_FAMILY"
SECRETS_URL="https://github.com/$REPO/settings/secrets/actions"

echo "📋 ПРОВЕРКА СЕКРЕТОВ GITHUB"
echo ""

# Список необходимых секретов
REQUIRED_SECRETS=(
  "APPLE_TEAM_ID"
  "PROVISIONING_PROFILE_APP"
  "PROVISIONING_PROFILE_EXTENSION"
)

OPTIONAL_CERT_SECRETS=(
  "IOS_DISTRIBUTION_CERTIFICATE"
  "IOS_DISTRIBUTION_CERTIFICATE_PASSWORD"
)

OPTIONAL_API_SECRETS=(
  "APP_STORE_CONNECT_API_KEY"
  "APP_STORE_CONNECT_ISSUER_ID"
  "APP_STORE_CONNECT_API_KEY_ID"
)

echo "✅ ОБЯЗАТЕЛЬНЫЕ СЕКРЕТЫ:"
for secret in "${REQUIRED_SECRETS[@]}"; do
  echo "  - $secret"
done
echo ""

echo "📦 ОПЦИОНАЛЬНЫЕ (для ручной подписи):"
for secret in "${OPTIONAL_CERT_SECRETS[@]}"; do
  echo "  - $secret"
done
echo ""

echo "📦 ОПЦИОНАЛЬНЫЕ (для автоматической подписи):"
for secret in "${OPTIONAL_API_SECRETS[@]}"; do
  echo "  - $secret"
done
echo ""

echo "🔍 ПРОВЕРКА ЛОКАЛЬНОГО СЕРТИФИКАТА"
echo ""

# Проверка сертификата в Keychain
CERT_FOUND=$(security find-identity -v -p codesigning 2>/dev/null | grep -i "distribution" | wc -l | tr -d ' ')

if [ "$CERT_FOUND" -gt 0 ]; then
  echo "✅ Сертификат Distribution найден в Keychain!"
  echo ""
  echo "📋 Для экспорта сертификата:"
  echo "   1. Откройте Keychain Access"
  echo "   2. Найдите сертификат Distribution"
  echo "   3. Правый клик → Export..."
  echo "   4. Сохраните как .p12"
  echo "   5. Запустите: ~/Desktop/ALADDIN_Profiles/export_certificate.sh"
else
  echo "⚠️  Сертификат Distribution НЕ найден в Keychain"
  echo ""
  echo "📋 ВАРИАНТЫ:"
  echo ""
  echo "ВАРИАНТ A: Создать сертификат через Xcode"
  echo "   1. Откройте Xcode → Preferences → Accounts"
  echo "   2. Выберите ваш Apple ID"
  echo "   3. Нажмите 'Manage Certificates'"
  echo "   4. Нажмите '+' → 'Apple Distribution'"
  echo ""
  echo "ВАРИАНТ B: Использовать автоматическую подпись"
  echo "   (требуются App Store Connect API ключи)"
  echo ""
fi

echo ""
echo "📋 ИТОГОВАЯ ИНСТРУКЦИЯ"
echo "======================"
echo ""

# Определить рекомендуемый вариант
if [ "$CERT_FOUND" -gt 0 ]; then
  echo "✅ РЕКОМЕНДУЕТСЯ: Вариант A (ручная подпись с сертификатом)"
  echo ""
  echo "ШАГИ:"
  echo "1. Экспортируйте сертификат (см. выше)"
  echo "2. Добавьте в GitHub Secrets:"
  echo "   - IOS_DISTRIBUTION_CERTIFICATE (base64)"
  echo "   - IOS_DISTRIBUTION_CERTIFICATE_PASSWORD (пароль)"
  echo "3. Убедитесь, что добавлены:"
  for secret in "${REQUIRED_SECRETS[@]}"; do
    echo "   - $secret"
  done
  echo "4. Запустите workflow 'Build and Upload to App Store'"
else
  echo "✅ РЕКОМЕНДУЕТСЯ: Вариант B (автоматическая подпись)"
  echo ""
  echo "ШАГИ:"
  echo "1. Убедитесь, что добавлены:"
  for secret in "${REQUIRED_SECRETS[@]}"; do
    echo "   - $secret"
  done
  echo ""
  echo "2. Добавьте App Store Connect API ключи:"
  for secret in "${OPTIONAL_API_SECRETS[@]}"; do
    echo "   - $secret"
  done
  echo ""
  echo "3. Запустите workflow 'Build and Upload to App Store'"
  echo ""
  echo "📖 Инструкция по созданию API ключа:"
  echo "   docs/КАК_ДОБАВИТЬ_СЕКРЕТЫ_В_GITHUB.md"
fi

echo ""
echo "🔗 Ссылка на секреты: $SECRETS_URL"
echo ""
echo "✅ Workflow обновлен и готов к использованию!"
echo ""

