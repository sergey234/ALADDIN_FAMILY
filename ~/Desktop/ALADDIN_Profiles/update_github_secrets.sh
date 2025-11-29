#!/bin/bash
# Скрипт для автоматического обновления GitHub Secrets через API

REPO="sergey234/ALADDIN_FAMILY"
APP_PROFILE_FILE="$HOME/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt"
EXT_PROFILE_FILE="$HOME/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt"

echo "🚀 ОБНОВЛЕНИЕ GITHUB SECRETS"
echo ""

# Проверить наличие файлов
if [ ! -f "$APP_PROFILE_FILE" ]; then
    echo "❌ Файл не найден: $APP_PROFILE_FILE"
    exit 1
fi

if [ ! -f "$EXT_PROFILE_FILE" ]; then
    echo "❌ Файл не найден: $EXT_PROFILE_FILE"
    exit 1
fi

# Проверить наличие GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN не установлен"
    echo ""
    echo "📋 Для автоматического обновления нужен GitHub Personal Access Token"
    echo ""
    echo "Как создать токен:"
    echo "1. Откройте: https://github.com/settings/tokens"
    echo "2. Нажмите 'Generate new token (classic)'"
    echo "3. Выберите права: 'repo' и 'write:packages'"
    echo "4. Скопируйте токен"
    echo "5. Выполните: export GITHUB_TOKEN=your_token_here"
    echo "6. Запустите этот скрипт снова"
    echo ""
    echo "Или обновите секреты вручную:"
    echo "https://github.com/$REPO/settings/secrets/actions"
    exit 1
fi

echo "✅ Токен найден"
echo ""

# Прочитать содержимое файлов
APP_PROFILE_CONTENT=$(cat "$APP_PROFILE_FILE")
EXT_PROFILE_CONTENT=$(cat "$EXT_PROFILE_FILE")

# Обновить PROVISIONING_PROFILE_APP
echo "📦 Обновление PROVISIONING_PROFILE_APP..."
curl -X PUT \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/secrets/PROVISIONING_PROFILE_APP" \
  -d "{\"encrypted_value\":\"$APP_PROFILE_CONTENT\"}" \
  --fail --silent --show-error

if [ $? -eq 0 ]; then
    echo "✅ PROVISIONING_PROFILE_APP обновлен"
else
    echo "❌ Ошибка при обновлении PROVISIONING_PROFILE_APP"
    echo "   Возможно, нужен другой метод (GitHub API требует шифрования)"
    exit 1
fi

# Обновить PROVISIONING_PROFILE_EXTENSION
echo "📦 Обновление PROVISIONING_PROFILE_EXTENSION..."
curl -X PUT \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/secrets/PROVISIONING_PROFILE_EXTENSION" \
  -d "{\"encrypted_value\":\"$EXT_PROFILE_CONTENT\"}" \
  --fail --silent --show-error

if [ $? -eq 0 ]; then
    echo "✅ PROVISIONING_PROFILE_EXTENSION обновлен"
else
    echo "❌ Ошибка при обновлении PROVISIONING_PROFILE_EXTENSION"
    exit 1
fi

echo ""
echo "✅ ГОТОВО! Оба секрета обновлены!"
echo ""
echo "📋 Проверьте: https://github.com/$REPO/settings/secrets/actions"

