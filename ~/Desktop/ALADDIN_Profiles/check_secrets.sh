#!/bin/bash

# Скрипт для проверки секретов GitHub (требует GitHub CLI или токен)

echo "🔍 Проверка секретов GitHub..."
echo ""

REPO="sergey234/ALADDIN_FAMILY"
SECRETS_URL="https://github.com/$REPO/settings/secrets/actions"

echo "📋 Ожидаемые секреты:"
echo "  1. PROVISIONING_PROFILE_APP"
echo "  2. PROVISIONING_PROFILE_EXTENSION"
echo "  3. APPLE_TEAM_ID"
echo ""

# Проверка через GitHub CLI (если установлен)
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    echo "✅ GitHub CLI доступен, проверяю секреты..."
    echo ""
    gh secret list --repo "$REPO" | grep -E "PROVISIONING_PROFILE|APPLE_TEAM_ID" || echo "⚠️ Секреты не найдены через CLI"
    echo ""
    echo "📋 Для детальной проверки откройте в браузере:"
    echo "   $SECRETS_URL"
else
    echo "⚠️ GitHub CLI не установлен или не авторизован"
    echo ""
    echo "📋 Проверьте секреты вручную в браузере:"
    echo "   $SECRETS_URL"
    echo ""
    echo "✅ Должны быть видны:"
    echo "  - PROVISIONING_PROFILE_APP"
    echo "  - PROVISIONING_PROFILE_EXTENSION"
    echo "  - APPLE_TEAM_ID"
fi

echo ""
echo "✅ Проверка завершена!"

