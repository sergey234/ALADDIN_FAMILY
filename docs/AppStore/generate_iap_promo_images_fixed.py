#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор промо-изображений IAP для ALADDIN (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Создает изображения 1024x1024 с правильными цветами тарифов и списком функций
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Размер холста (требование Apple)
CANVAS_SIZE = 1024
DPI = 72

# Цвета тарифов из кода приложения
COLORS = {
    'individual': '#2E5BFF',  # primaryBlue
    'family': '#F59E0B',      # secondaryGold
    'premium': '#A855F7'      # Purple
}

# Функции для каждого тарифа (из StoreManager и требований)
FEATURES = {
    'individual': {
        'ru': [
            "1. Расширенная защита до 3 устройств",
            "2. Расширенный родительский контроль",
            "3. Детальная аналитика активности",
            "4. AI-помощник для безопасности",
            "5. Умная блокировка контента",
            "6. Расширенные отчеты об активности",
            "7. Настраиваемые правила использования",
            "8. Блокировка по расписанию",
            "9. Защита от кибербуллинга",
            "10. Мониторинг социальных сетей"
        ],
        'en': [
            "1. Extended protection up to 3 devices",
            "2. Extended parental control",
            "3. Detailed activity analytics",
            "4. AI assistant for security",
            "5. Smart content blocking",
            "6. Extended activity reports",
            "7. Customizable usage rules",
            "8. Scheduled blocking",
            "9. Cyberbullying protection",
            "10. Social media monitoring"
        ]
    },
    'family': {
        'ru': [
            "1. Защита до 5 устройств одновременно",
            "2. Централизованное управление семьей",
            "3. Родительский контроль для всех детей",
            "4. Контроль доступа к платным подпискам",
            "5. Семейная аналитика и отчеты",
            "6. Геозоны всех устройств семьи",
            "7. История активности всех устройств",
            "8. Индивидуальные профили для каждого ребенка",
            "9. Настраиваемые правила для каждого ребенка",
            "10. Защита всех устройств от угроз"
        ],
        'en': [
            "1. Protection up to 5 devices simultaneously",
            "2. Centralized family management",
            "3. Parental control for all children",
            "4. Control access to paid subscriptions",
            "5. Family analytics and reports",
            "6. Geofences of all family devices",
            "7. Activity history of all devices",
            "8. Individual profiles for each child",
            "9. Customizable rules for each child",
            "10. Protection of all devices from threats"
        ]
    },
    'premium': {
        'ru': [
            "1. Защита до 10 устройств",
            "2. Все функции семейного тарифа",
            "3. Продвинутый AI-помощник с обучением",
            "4. Детальная аналитика с прогнозами",
            "5. Неограниченная история активности",
            "6. Расширенная защита от всех типов угроз",
            "7. Кастомные правила и автоматизация",
            "8. Интеграция с умным домом",
            "9. Защита от всех видов мошенничества",
            "10. Эксклюзивные функции безопасности"
        ],
        'en': [
            "1. Protection up to 10 devices",
            "2. All family plan features",
            "3. Advanced AI assistant with learning",
            "4. Detailed analytics with forecasts",
            "5. Unlimited activity history",
            "6. Extended protection from all threat types",
            "7. Custom rules and automation",
            "8. Smart home integration",
            "9. Protection from all types of fraud",
            "10. Exclusive security features"
        ]
    }
}

# Названия тарифов
TITLES = {
    'individual': {
        'ru': 'ALADDIN ИНДИВИДУАЛЬНЫЙ',
        'en': 'ALADDIN INDIVIDUAL'
    },
    'family': {
        'ru': 'ALADDIN СЕМЕЙНЫЙ',
        'en': 'ALADDIN FAMILY'
    },
    'premium': {
        'ru': 'ALADDIN ПРЕМИУМ',
        'en': 'ALADDIN PREMIUM'
    }
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size):
    """Получить шрифт указанного размера"""
    try:
        # Пытаемся использовать системный шрифт
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()

def create_tariff_image(tariff_type, language='ru'):
    """Создает изображение тарифа"""
    # Фон - темный
    bg_color = (15, 23, 42)  # backgroundDark из Colors.swift
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Цвет тарифа
    tariff_color = hex_to_rgb(COLORS[tariff_type])
    
    # Отступы
    padding = 80
    content_width = CANVAS_SIZE - 2 * padding
    
    # Заголовок
    title_font = get_font(72)
    title_text = TITLES[tariff_type][language]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_height = title_bbox[3] - title_bbox[1]
    title_y = padding + 40
    
    # Рисуем заголовок
    title_x = (CANVAS_SIZE - (title_bbox[2] - title_bbox[0])) // 2
    draw.text((title_x, title_y), title_text, font=title_font, fill=tariff_color)
    
    # Линия под заголовком
    line_y = title_y + title_height + 30
    line_length = 600
    line_x = (CANVAS_SIZE - line_length) // 2
    draw.line([(line_x, line_y), (line_x + line_length, line_y)], fill=tariff_color, width=4)
    
    # Начало списка функций
    features_start_y = line_y + 50
    features_font = get_font(32)
    line_spacing = 45
    
    # Получаем функции
    features = FEATURES[tariff_type][language]
    
    # Рисуем каждую функцию
    for i, feature in enumerate(features):
        y_pos = features_start_y + i * line_spacing
        
        # Проверяем, не выходит ли за пределы
        if y_pos > CANVAS_SIZE - padding:
            break
        
        # Рисуем текст функции
        feature_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        
        # Если текст слишком длинный, сокращаем шрифт
        if feature_width > content_width:
            features_font = get_font(28)
            feature_bbox = draw.textbbox((0, 0), feature, font=features_font)
            feature_width = feature_bbox[2] - feature_bbox[0]
        
        feature_x = (CANVAS_SIZE - feature_width) // 2
        draw.text((feature_x, y_pos), feature, font=features_font, fill=(255, 255, 255))
    
    # Декоративная рамка
    border_width = 6
    border_offset = 40
    draw.rectangle(
        [border_offset, border_offset, 
         CANVAS_SIZE - border_offset, CANVAS_SIZE - border_offset],
        outline=tariff_color, width=border_width
    )
    
    return img

def main():
    """Генерирует все изображения"""
    output_dir = os.path.join(os.path.dirname(__file__), 'tariff_images_1024x1024')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Генерация промо-изображений IAP (исправленная версия)...")
    
    tariffs = ['individual', 'family', 'premium']
    languages = ['ru', 'en']
    
    for tariff in tariffs:
        for lang in languages:
            print(f"📝 Создание {tariff}_{lang}_1024x1024.png...")
            img = create_tariff_image(tariff, lang)
            
            # Убеждаемся что RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Сохраняем с DPI=72
            output_path = os.path.join(output_dir, f'{tariff}_{lang}_1024x1024.png')
            img.save(output_path, 'PNG', dpi=(DPI, DPI))
            print(f"✅ Готово: {output_path}")
    
    print("\n🎉 Все изображения созданы успешно!")
    print(f"📂 Папка: {output_dir}")

if __name__ == '__main__':
    main()
