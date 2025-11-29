#!/bin/bash

# Скрипт для перекодирования extension.mobileprovision в правильный base64

cd ~/Desktop/ALADDIN_Profiles

echo "🔧 ПЕРЕКОДИРОВАНИЕ EXTENSION PROFILE"
echo ""

# Проверяем наличие файла
if [ ! -f "extension.mobileprovision" ]; then
    echo "❌ Ошибка: extension.mobileprovision не найден!"
    exit 1
fi

echo "✅ Найден файл: extension.mobileprovision"
echo "📦 Кодирую в base64 (без переносов строк)..."
echo ""

# Кодируем в base64 БЕЗ переносов строк
base64 -i extension.mobileprovision | tr -d '\n' > extension_profile_base64_fixed.txt

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при кодировании!"
    exit 1
fi

echo "✅ Файл создан: extension_profile_base64_fixed.txt"
echo ""

# Проверяем размер
SIZE=$(wc -c < extension_profile_base64_fixed.txt)
echo "📋 Размер файла: $SIZE байт"
echo ""

# Проверяем валидность
echo "🔍 Проверка валидности base64..."
base64 -d extension_profile_base64_fixed.txt > /tmp/test_decode.mobileprovision 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Base64 валидный! Декодирование успешно."
    rm /tmp/test_decode.mobileprovision
else
    echo "❌ Ошибка: Base64 невалидный!"
    exit 1
fi

echo ""
echo "📋 Копирую в буфер обмена..."
cat extension_profile_base64_fixed.txt | pbcopy

echo ""
echo "✅ ГОТОВО!"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions"
echo "2. Найдите: PROVISIONING_PROFILE_EXTENSION"
echo "3. Нажмите: Update"
echo "4. Вставьте (Cmd+V) в поле Secret"
echo "5. Нажмите: Update secret"
echo ""
echo "📁 Файл также сохранён:"
echo "   ~/Desktop/ALADDIN_Profiles/extension_profile_base64_fixed.txt"

