#!/bin/bash
# Скрипт для автоматического кодирования App Store профилей в base64

echo "🚀 КОДИРОВАНИЕ APP STORE ПРОФИЛЕЙ В BASE64"
echo ""

# Создать папку если не существует
mkdir -p ~/Desktop/ALADDIN_Profiles

# Проверить наличие профилей в Downloads
APP_PROFILE=$(find ~/Downloads -name "*ALADDIN*AppStore*.mobileprovision" -o -name "*ALADDIN*App*Store*.mobileprovision" | head -1)
EXT_PROFILE=$(find ~/Downloads -name "*ALADDIN*PacketTunnel*AppStore*.mobileprovision" -o -name "*ALADDIN*PacketTunnel*App*Store*.mobileprovision" | head -1)

if [ -z "$APP_PROFILE" ]; then
    echo "⚠️  Основной профиль не найден в Downloads"
    echo "   Ищу файлы .mobileprovision..."
    APP_PROFILE=$(find ~/Downloads -name "*.mobileprovision" -type f | grep -i "aladdin" | grep -v "Dev" | head -1)
fi

if [ -z "$EXT_PROFILE" ]; then
    echo "⚠️  Профиль Extension не найден в Downloads"
    echo "   Ищу файлы .mobileprovision..."
    EXT_PROFILE=$(find ~/Downloads -name "*.mobileprovision" -type f | grep -i "packettunnel\|packet" | grep -v "Dev" | head -1)
fi

# Если не найдены, попросить указать вручную
if [ -z "$APP_PROFILE" ]; then
    echo ""
    echo "❌ Основной профиль не найден автоматически"
    echo "   Пожалуйста, укажите путь к файлу вручную:"
    read -p "   Путь к основному профилю (.mobileprovision): " APP_PROFILE
fi

if [ -z "$EXT_PROFILE" ]; then
    echo ""
    echo "❌ Профиль Extension не найден автоматически"
    echo "   Пожалуйста, укажите путь к файлу вручную:"
    read -p "   Путь к профилю Extension (.mobileprovision): " EXT_PROFILE
fi

# Проверить что файлы существуют
if [ ! -f "$APP_PROFILE" ]; then
    echo "❌ Файл не найден: $APP_PROFILE"
    exit 1
fi

if [ ! -f "$EXT_PROFILE" ]; then
    echo "❌ Файл не найден: $EXT_PROFILE"
    exit 1
fi

echo ""
echo "✅ Найдены профили:"
echo "   Основной: $APP_PROFILE"
echo "   Extension: $EXT_PROFILE"
echo ""

# Кодировать в base64
echo "📦 Кодирование основного профиля..."
base64 -i "$APP_PROFILE" | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt

if [ $? -eq 0 ]; then
    echo "✅ Основной профиль закодирован: ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt"
    echo "   Размер: $(wc -c < ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt) байт"
else
    echo "❌ Ошибка при кодировании основного профиля"
    exit 1
fi

echo ""
echo "📦 Кодирование профиля Extension..."
base64 -i "$EXT_PROFILE" | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt

if [ $? -eq 0 ]; then
    echo "✅ Профиль Extension закодирован: ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt"
    echo "   Размер: $(wc -c < ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt) байт"
else
    echo "❌ Ошибка при кодировании профиля Extension"
    exit 1
fi

echo ""
echo "✅ ГОТОВО! Оба профиля закодированы в base64"
echo ""
echo "📋 Следующий шаг:"
echo "1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions"
echo "2. Обновите PROVISIONING_PROFILE_APP (вставьте содержимое app_profile_appstore_base64.txt)"
echo "3. Обновите PROVISIONING_PROFILE_EXTENSION (вставьте содержимое extension_profile_appstore_base64.txt)"
echo ""
echo "📁 Файлы готовы в: ~/Desktop/ALADDIN_Profiles/"

