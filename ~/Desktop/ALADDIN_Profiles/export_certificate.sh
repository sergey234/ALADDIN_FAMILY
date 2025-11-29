#!/bin/bash

# Скрипт для экспорта сертификата подписи из Keychain

echo "🔐 ЭКСПОРТ СЕРТИФИКАТА ПОДПИСИ"
echo ""

# Создать директорию для сертификатов
CERT_DIR="$HOME/Desktop/ALADDIN_Profiles/Certificates"
mkdir -p "$CERT_DIR"

# Поиск всех сертификатов Distribution
echo "🔍 Ищем сертификаты Distribution..."
echo ""

# Список всех сертификатов для подписи
IDENTITIES=$(security find-identity -v -p codesigning 2>/dev/null | grep -i "distribution" || echo "")

if [ -z "$IDENTITIES" ]; then
    echo "❌ Сертификаты Distribution не найдены в Keychain!"
    echo ""
    echo "📋 ВАРИАНТЫ РЕШЕНИЯ:"
    echo ""
    echo "1. Откройте Keychain Access (⌘+Space → 'Keychain Access')"
    echo "2. Проверьте раздел 'My Certificates'"
    echo "3. Если сертификата нет:"
    echo "   - Откройте Xcode → Preferences → Accounts"
    echo "   - Выберите ваш Apple ID"
    echo "   - Нажмите 'Manage Certificates'"
    echo "   - Нажмите '+' → 'Apple Distribution'"
    echo ""
    echo "4. Или используйте автоматическую подпись (если настроены App Store Connect API ключи)"
    echo ""
    exit 1
fi

echo "✅ Найдены сертификаты:"
echo "$IDENTITIES"
echo ""

# Попробовать найти сертификат с Team ID
TEAM_ID="6CJVBBUGSN"
CERT_NAME=$(echo "$IDENTITIES" | grep -i "$TEAM_ID\|SERGEY" | head -1 | sed 's/.*"\(.*\)".*/\1/')

if [ -z "$CERT_NAME" ]; then
    # Взять первый найденный
    CERT_NAME=$(echo "$IDENTITIES" | head -1 | sed 's/.*"\(.*\)".*/\1/')
fi

echo "📋 Используем сертификат: $CERT_NAME"
echo ""

# Получить SHA1 hash сертификата
CERT_HASH=$(echo "$IDENTITIES" | grep "$CERT_NAME" | awk '{print $2}')

if [ -z "$CERT_HASH" ]; then
    echo "❌ Не удалось найти hash сертификата"
    exit 1
fi

echo "🔑 Hash сертификата: $CERT_HASH"
echo ""

# Экспортировать сертификат и приватный ключ
CERT_FILE="$CERT_DIR/distribution_certificate.p12"
CERT_PASSWORD=$(openssl rand -base64 32)

echo "📤 Экспортируем сертификат в .p12 формат..."
echo ""

# Попробовать экспортировать через security
security export -k "$CERT_HASH" -f pkcs12 -P "$CERT_PASSWORD" -o "$CERT_FILE" 2>&1

if [ $? -ne 0 ] || [ ! -f "$CERT_FILE" ]; then
    echo "⚠️  Автоматический экспорт не удался"
    echo ""
    echo "📋 РУЧНОЙ ЭКСПОРТ:"
    echo ""
    echo "1. Откройте Keychain Access"
    echo "2. Найдите сертификат: $CERT_NAME"
    echo "3. Правый клик → Export..."
    echo "4. Сохраните как: $CERT_FILE"
    echo "5. Выберите формат: Personal Information Exchange (.p12)"
    echo "6. Введите пароль (запомните его!)"
    echo ""
    echo "После экспорта запустите:"
    echo "  cd $CERT_DIR"
    echo "  base64 -i distribution_certificate.p12 | tr -d '\n' > distribution_certificate_base64.txt"
    echo "  echo 'Пароль: $CERT_PASSWORD' > certificate_password.txt"
    echo ""
    exit 1
fi

echo "✅ Сертификат экспортирован: $CERT_FILE"
echo ""

# Кодировать в base64
BASE64_FILE="$CERT_DIR/distribution_certificate_base64.txt"
base64 -i "$CERT_FILE" | tr -d '\n' > "$BASE64_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Сертификат закодирован в base64: $BASE64_FILE"
    echo "📏 Размер: $(wc -c < "$BASE64_FILE") байт"
    echo ""
    
    # Копировать в буфер обмена
    cat "$BASE64_FILE" | pbcopy
    echo "✅ Base64 скопирован в буфер обмена!"
    echo ""
    
    # Сохранить пароль
    echo "$CERT_PASSWORD" > "$CERT_DIR/certificate_password.txt"
    echo "$CERT_PASSWORD" | pbcopy
    echo "✅ Пароль сохранен и скопирован в буфер обмена!"
    echo ""
    
    echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
    echo ""
    echo "1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions"
    echo ""
    echo "2. Добавьте секрет IOS_DISTRIBUTION_CERTIFICATE:"
    echo "   - Name: IOS_DISTRIBUTION_CERTIFICATE"
    echo "   - Value: содержимое файла $BASE64_FILE"
    echo "   (уже в буфере обмена - просто вставьте Cmd+V)"
    echo ""
    echo "3. Добавьте секрет IOS_DISTRIBUTION_CERTIFICATE_PASSWORD:"
    echo "   - Name: IOS_DISTRIBUTION_CERTIFICATE_PASSWORD"
    echo "   - Value: $CERT_PASSWORD"
    echo "   (уже в буфере обмена - просто вставьте Cmd+V)"
    echo ""
    echo "4. Запустите workflow 'Build and Upload to App Store' снова"
    echo ""
    echo "📁 Файлы сохранены в: $CERT_DIR"
    echo ""
else
    echo "❌ Ошибка при кодировании в base64"
    exit 1
fi

