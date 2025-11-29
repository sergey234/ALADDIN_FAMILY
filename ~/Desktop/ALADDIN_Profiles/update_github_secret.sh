#!/bin/bash

# Скрипт для обновления секрета PROVISIONING_PROFILE_EXTENSION в GitHub

REPO="sergey234/ALADDIN_FAMILY"
SECRET_NAME="PROVISIONING_PROFILE_EXTENSION"
SECRET_FILE="$HOME/Desktop/ALADDIN_Profiles/extension_profile_base64_fixed.txt"

echo "🔧 ОБНОВЛЕНИЕ СЕКРЕТА В GITHUB"
echo ""

# Проверка файла
if [ ! -f "$SECRET_FILE" ]; then
    echo "❌ Ошибка: Файл не найден: $SECRET_FILE"
    exit 1
fi

echo "✅ Файл найден: $SECRET_FILE"
echo "📋 Размер: $(wc -c < "$SECRET_FILE") байт"
echo ""

# Проверка токена
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN не установлен"
    echo ""
    echo "📋 ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ОБНОВЛЕНИЯ:"
    echo "1. Откройте: https://github.com/$REPO/settings/secrets/actions"
    echo "2. Найдите: $SECRET_NAME"
    echo "3. Нажмите: Update"
    echo "4. Вставьте содержимое файла: $SECRET_FILE"
    echo "5. Нажмите: Update secret"
    echo ""
    echo "📋 Содержимое файла скопировано в буфер обмена!"
    cat "$SECRET_FILE" | pbcopy
    echo "✅ Готово к вставке (Cmd+V)"
    exit 0
fi

echo "✅ GITHUB_TOKEN найден"
echo "🔄 Обновляю секрет через GitHub API..."
echo ""

# Читаем содержимое файла
SECRET_VALUE=$(cat "$SECRET_FILE")

# Получаем публичный ключ репозитория
echo "📥 Получаю публичный ключ репозитория..."
REPO_KEY=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/actions/secrets/public-key")

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при получении публичного ключа"
    exit 1
fi

KEY_ID=$(echo "$REPO_KEY" | grep -o '"key_id":"[^"]*"' | cut -d'"' -f4)
KEY=$(echo "$REPO_KEY" | grep -o '"key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$KEY_ID" ] || [ -z "$KEY" ]; then
    echo "❌ Не удалось получить публичный ключ"
    echo "Проверьте права доступа токена (нужны: repo, actions)"
    exit 1
fi

echo "✅ Публичный ключ получен"
echo "🔐 Шифрую секрет..."

# Шифруем секрет (требуется openssl и base64)
# Для этого нужна библиотека libsodium или другой способ шифрования
# GitHub использует NaCl box для шифрования секретов

echo "⚠️  Автоматическое шифрование требует дополнительных библиотек"
echo ""
echo "📋 РЕКОМЕНДУЕТСЯ РУЧНОЕ ОБНОВЛЕНИЕ:"
echo "1. Откройте: https://github.com/$REPO/settings/secrets/actions"
echo "2. Найдите: $SECRET_NAME"
echo "3. Нажмите: Update"
echo "4. Вставьте (Cmd+V) - содержимое уже в буфере обмена"
echo "5. Нажмите: Update secret"
echo ""
echo "✅ Содержимое файла скопировано в буфер обмена!"

