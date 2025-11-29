#!/bin/bash

# Скрипт для добавления секретов в GitHub через GitHub CLI
# Использование: ./add_secrets_to_github.sh

set -e

REPO="sergey234/ALADDIN_FAMILY"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔐 Добавление секретов в GitHub..."
echo "Репозиторий: $REPO"
echo ""

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) не установлен!"
    echo "Установите: brew install gh"
    echo "Или добавьте секреты вручную через браузер:"
    echo "https://github.com/$REPO/settings/secrets/actions"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI не авторизован!"
    echo "Выполните: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI установлен и авторизован"
echo ""

# Чтение файлов
APP_PROFILE_FILE="$SCRIPT_DIR/app_profile_base64.txt"
EXTENSION_PROFILE_FILE="$SCRIPT_DIR/extension_profile_base64.txt"

if [ ! -f "$APP_PROFILE_FILE" ]; then
    echo "❌ Файл не найден: $APP_PROFILE_FILE"
    exit 1
fi

if [ ! -f "$EXTENSION_PROFILE_FILE" ]; then
    echo "❌ Файл не найден: $EXTENSION_PROFILE_FILE"
    exit 1
fi

echo "📋 Чтение файлов..."
APP_PROFILE_CONTENT=$(cat "$APP_PROFILE_FILE")
EXTENSION_PROFILE_CONTENT=$(cat "$EXTENSION_PROFILE_FILE")

echo "✅ Файлы прочитаны"
echo ""

# Добавление секретов
echo "🔐 Добавление секрета PROVISIONING_PROFILE_APP..."
echo "$APP_PROFILE_CONTENT" | gh secret set PROVISIONING_PROFILE_APP --repo "$REPO" || {
    echo "⚠️ Не удалось добавить PROVISIONING_PROFILE_APP"
    echo "Попробуйте вручную через браузер"
}

echo ""
echo "🔐 Добавление секрета PROVISIONING_PROFILE_EXTENSION..."
echo "$EXTENSION_PROFILE_CONTENT" | gh secret set PROVISIONING_PROFILE_EXTENSION --repo "$REPO" || {
    echo "⚠️ Не удалось добавить PROVISIONING_PROFILE_EXTENSION"
    echo "Попробуйте вручную через браузер"
}

echo ""
echo "🔐 Проверка/добавление секрета APPLE_TEAM_ID..."
if gh secret list --repo "$REPO" | grep -q "APPLE_TEAM_ID"; then
    echo "✅ APPLE_TEAM_ID уже существует"
else
    echo "6CJVBBUGSN" | gh secret set APPLE_TEAM_ID --repo "$REPO" || {
        echo "⚠️ Не удалось добавить APPLE_TEAM_ID"
        echo "Попробуйте вручную через браузер"
    }
fi

echo ""
echo "✅ Готово! Проверка секретов:"
gh secret list --repo "$REPO" | grep -E "PROVISIONING_PROFILE|APPLE_TEAM_ID" || echo "Секреты не найдены"

echo ""
echo "🎉 Секреты добавлены в GitHub!"

