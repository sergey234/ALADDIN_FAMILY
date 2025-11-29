#!/bin/bash

echo "🔐 ПОДГОТОВКА СЕКРЕТОВ ДЛЯ APP STORE CONNECT API"
echo "================================================"
echo ""

# Директория для файлов
CERT_DIR="$HOME/Desktop/ALADDIN_Profiles"
cd "$CERT_DIR" || exit 1

echo "📋 ШАГ 1: НАЙТИ .p8 ФАЙЛ"
echo ""

# Поиск .p8 файлов
P8_FILES=$(find "$CERT_DIR" -name "AuthKey_*.p8" -o -name "*.p8" 2>/dev/null)

if [ -z "$P8_FILES" ]; then
    echo "⚠️  .p8 файл не найден в $CERT_DIR"
    echo ""
    echo "📋 ИНСТРУКЦИЯ:"
    echo "1. Создайте API ключ: https://appstoreconnect.apple.com/access/api"
    echo "2. Скачайте .p8 файл"
    echo "3. Сохраните его в: $CERT_DIR"
    echo "4. Запустите этот скрипт снова"
    echo ""
    exit 1
fi

echo "✅ Найдены .p8 файлы:"
echo "$P8_FILES" | while read -r file; do
    echo "  - $file"
done
echo ""

# Выбрать первый файл
P8_FILE=$(echo "$P8_FILES" | head -1)
echo "📄 Используем файл: $P8_FILE"
echo ""

# Проверить формат файла
if ! grep -q "BEGIN PRIVATE KEY" "$P8_FILE" 2>/dev/null; then
    echo "⚠️  ВНИМАНИЕ: Файл не похож на валидный .p8 ключ"
    echo "   Убедитесь, что это правильный файл из App Store Connect"
    echo ""
fi

echo "📋 ШАГ 2: ПОДГОТОВИТЬ СОДЕРЖИМОЕ ДЛЯ GITHUB SECRETS"
echo ""

# Прочитать содержимое .p8 файла
API_KEY_CONTENT=$(cat "$P8_FILE")

# Сохранить в файл
API_KEY_FILE="$CERT_DIR/APP_STORE_CONNECT_API_KEY.txt"
echo "$API_KEY_CONTENT" > "$API_KEY_FILE"

echo "✅ Содержимое .p8 файла сохранено в: $API_KEY_FILE"
echo "📏 Размер: $(wc -c < "$API_KEY_FILE") байт"
echo ""

# Копировать в буфер обмена
echo "$API_KEY_CONTENT" | pbcopy
echo "✅ Содержимое скопировано в буфер обмена!"
echo ""

echo "📋 ШАГ 3: ЗАПИСАТЬ ISSUER ID И KEY ID"
echo ""

echo "Введите данные из App Store Connect:"
echo ""

# Запросить Issuer ID
read -p "Issuer ID (UUID): " ISSUER_ID

if [ -z "$ISSUER_ID" ]; then
    echo "❌ Issuer ID не может быть пустым"
    exit 1
fi

# Запросить Key ID
read -p "Key ID: " KEY_ID

if [ -z "$KEY_ID" ]; then
    echo "❌ Key ID не может быть пустым"
    exit 1
fi

# Сохранить в файлы
echo "$ISSUER_ID" > "$CERT_DIR/APP_STORE_CONNECT_ISSUER_ID.txt"
echo "$KEY_ID" > "$CERT_DIR/APP_STORE_CONNECT_API_KEY_ID.txt"

echo ""
echo "✅ Данные сохранены:"
echo "  - Issuer ID: $ISSUER_ID"
echo "  - Key ID: $KEY_ID"
echo ""

# Копировать Issuer ID в буфер обмена
echo "$ISSUER_ID" | pbcopy
echo "✅ Issuer ID скопирован в буфер обмена!"
echo ""

echo "📋 ШАГ 4: ДОБАВИТЬ СЕКРЕТЫ В GITHUB"
echo ""

echo "Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions"
echo ""
echo "Добавьте 3 секрета:"
echo ""
echo "1. APP_STORE_CONNECT_API_KEY"
echo "   - Содержимое уже в буфере обмена (Cmd+V)"
echo "   - Или скопируйте из файла: $API_KEY_FILE"
echo ""
echo "2. APP_STORE_CONNECT_ISSUER_ID"
echo "   - Значение: $ISSUER_ID"
echo "   - (уже в буфере обмена)"
echo ""
echo "3. APP_STORE_CONNECT_API_KEY_ID"
echo "   - Значение: $KEY_ID"
echo "   - Скопируйте из файла: $CERT_DIR/APP_STORE_CONNECT_API_KEY_ID.txt"
echo ""

# Копировать Key ID в буфер обмена
echo "$KEY_ID" | pbcopy
echo "✅ Key ID скопирован в буфер обмена!"
echo ""

echo "📁 Все файлы сохранены в: $CERT_DIR"
echo ""
echo "✅ ГОТОВО! Теперь добавьте секреты в GitHub и запустите workflow!"
echo ""

