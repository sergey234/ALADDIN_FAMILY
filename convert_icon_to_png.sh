#!/bin/bash

# 🔄 Конвертация иконки приложения из JPEG в PNG
# Требуется для App Store Connect (Apple требует PNG формат)

echo "🔄 Конвертация иконки приложения..."

ICON_PATH="Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg"
OUTPUT_PATH="Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.png"

# Проверка существования файла
if [ ! -f "$ICON_PATH" ]; then
    echo "❌ Ошибка: Файл $ICON_PATH не найден!"
    exit 1
fi

# Конвертация
echo "📦 Конвертация JPEG → PNG..."
sips -s format png "$ICON_PATH" --out "$OUTPUT_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Иконка успешно сконвертирована!"
    echo "📁 Файл: $OUTPUT_PATH"
    
    # Проверка размера
    echo ""
    echo "📏 Размер файла:"
    sips -g pixelWidth -g pixelHeight "$OUTPUT_PATH" | grep -E "pixelWidth|pixelHeight"
    
    echo ""
    echo "✅ Готово! Теперь можно использовать PNG версию для App Store Connect."
else
    echo "❌ Ошибка при конвертации!"
    exit 1
fi


