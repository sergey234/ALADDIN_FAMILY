#!/bin/bash
# Простой скрипт для кодирования профилей в base64

echo "🚀 КОДИРОВАНИЕ ПРОФИЛЕЙ В BASE64"
echo ""

# Создать папку
mkdir -p ~/Desktop/ALADDIN_Profiles

# Найти последние скачанные профили
echo "🔍 Ищу профили в Downloads..."
PROFILES=$(find ~/Downloads -name "*.mobileprovision" -type f -mtime -1 2>/dev/null | sort -r)

if [ -z "$PROFILES" ]; then
    echo "⚠️  Не найдены профили, ищу все .mobileprovision файлы..."
    PROFILES=$(find ~/Downloads -name "*.mobileprovision" -type f 2>/dev/null | sort -r)
fi

# Показать найденные профили
echo ""
echo "📋 Найденные профили:"
echo "$PROFILES" | nl

# Найти основной профиль (содержит "App Store" или "Distribution", но не "PacketTunnel")
APP_PROFILE=$(echo "$PROFILES" | grep -i "app.*store\|distribution" | grep -v -i "packettunnel\|packet" | head -1)

# Найти профиль Extension (содержит "PacketTunnel" или "packet")
EXT_PROFILE=$(echo "$PROFILES" | grep -i "packettunnel\|packet" | head -1)

# Если не найдены автоматически, использовать последние 2 файла
if [ -z "$APP_PROFILE" ] || [ -z "$EXT_PROFILE" ]; then
    echo ""
    echo "⚠️  Не удалось определить профили автоматически"
    echo "   Используем последние 2 скачанных файла..."
    APP_PROFILE=$(echo "$PROFILES" | head -1)
    EXT_PROFILE=$(echo "$PROFILES" | head -2 | tail -1)
fi

echo ""
echo "✅ Используемые профили:"
echo "   Основной: $APP_PROFILE"
echo "   Extension: $EXT_PROFILE"
echo ""

# Кодировать основной профиль
echo "📦 Кодирование основного профиля..."
base64 -i "$APP_PROFILE" | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt

if [ $? -eq 0 ]; then
    SIZE=$(wc -c < ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt)
    echo "✅ Основной профиль закодирован!"
    echo "   Файл: ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt"
    echo "   Размер: $SIZE байт"
else
    echo "❌ Ошибка при кодировании основного профиля"
    exit 1
fi

echo ""
echo "📦 Кодирование профиля Extension..."
base64 -i "$EXT_PROFILE" | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt

if [ $? -eq 0 ]; then
    SIZE=$(wc -c < ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt)
    echo "✅ Профиль Extension закодирован!"
    echo "   Файл: ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt"
    echo "   Размер: $SIZE байт"
else
    echo "❌ Ошибка при кодировании профиля Extension"
    exit 1
fi

echo ""
echo "✅ ГОТОВО! Оба профиля закодированы в base64"
echo ""
echo "📋 Следующий шаг:"
echo "1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions"
echo "2. Обновите PROVISIONING_PROFILE_APP"
echo "3. Обновите PROVISIONING_PROFILE_EXTENSION"
echo ""
echo "📁 Файлы готовы в: ~/Desktop/ALADDIN_Profiles/"

