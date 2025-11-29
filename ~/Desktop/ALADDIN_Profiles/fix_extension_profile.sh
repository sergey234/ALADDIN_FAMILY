#!/bin/bash

# Скрипт для правильного кодирования extension provisioning profile

echo "🔧 ИСПРАВЛЕНИЕ EXTENSION PROFILE"
echo ""

# Вариант 1: Если есть оригинальный .mobileprovision файл
if [ -f "extension.mobileprovision" ]; then
    echo "✅ Найден оригинальный файл: extension.mobileprovision"
    echo "📦 Кодирую в base64..."
    
    # Кодируем в base64 БЕЗ переносов строк
    base64 -i extension.mobileprovision | tr -d '\n' > extension_profile_base64_fixed.txt
    
    echo "✅ Готово! Новый файл: extension_profile_base64_fixed.txt"
    echo ""
    echo "📋 Размер файла:"
    wc -c extension_profile_base64_fixed.txt
    echo ""
    echo "📋 Первые 100 символов:"
    head -c 100 extension_profile_base64_fixed.txt
    echo ""
    echo ""
    echo "✅ Теперь скопируйте содержимое extension_profile_base64_fixed.txt в GitHub Secret"
    
# Вариант 2: Если нужно исправить существующий base64 файл
elif [ -f "extension_profile_base64.txt" ]; then
    echo "⚠️  Оригинальный .mobileprovision не найден"
    echo "🔧 Пытаюсь исправить существующий base64 файл..."
    
    # Удаляем все не-base64 символы (оставляем только A-Z, a-z, 0-9, +, /, =)
    cat extension_profile_base64.txt | tr -d '\n' | grep -o '[A-Za-z0-9+/=]*' | tr -d '\n' > extension_profile_base64_fixed.txt
    
    echo "✅ Исправленный файл: extension_profile_base64_fixed.txt"
    echo ""
    echo "📋 Размер файла:"
    wc -c extension_profile_base64_fixed.txt
    echo ""
    echo "📋 Первые 100 символов:"
    head -c 100 extension_profile_base64_fixed.txt
    echo ""
    echo ""
    echo "⚠️  ВНИМАНИЕ: Проверьте, что файл валидный!"
    echo "   Попробуйте декодировать: base64 -d extension_profile_base64_fixed.txt | head -c 100"
    
else
    echo "❌ Ошибка: Не найден ни оригинальный .mobileprovision, ни base64 файл"
    echo ""
    echo "📋 Инструкция:"
    echo "1. Найдите файл extension.mobileprovision в:"
    echo "   ~/Library/MobileDevice/Provisioning Profiles/"
    echo "2. Скопируйте его в ~/Desktop/ALADDIN_Profiles/"
    echo "3. Запустите этот скрипт снова"
    exit 1
fi

