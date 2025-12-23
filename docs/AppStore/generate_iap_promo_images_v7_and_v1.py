#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор промо-изображений IAP для ALADDIN
Два варианта: #7 Комбинированный и #1 Flat-дизайн
Только русские версии, по 7 функций на тариф
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

CANVAS_SIZE = 1024
DPI = 72

# ЦВЕТА ИЗ ГЛАВНОЙ СТРАНИЦЫ
COLORS = {
    'individual': {
        'main': '#2E5BFF',      # синий
        'accent': '#60A5FA',    # светлый синий
        'gold': '#F59E0B',      # золотой
        'gradient1': '#0a1128',
        'gradient2': '#1e3a5f',
        'gradient3': '#2e5090'
    },
    'family': {
        'main': '#F59E0B',      # золотой
        'accent': '#FCD34D',    # светлый золотой
        'purple': '#A855F7',    # фиолетовый
        'gradient1': '#3d2817',
        'gradient2': '#6b4423',
        'gradient3': '#9c6e2f'
    },
    'premium': {
        'main': '#A855F7',      # фиолетовый
        'accent': '#C084FC',    # светлый фиолетовый
        'gold': '#F59E0B',      # золотой
        'blue': '#2E5BFF',      # синий
        'gradient1': '#2d1b69',
        'gradient2': '#4c2a9e',
        'gradient3': '#6b3bd3'
    }
}

# ТОП-7 ФУНКЦИЙ ДЛЯ КАЖДОГО ТАРИФА
FEATURES_7 = {
    'individual': [
        "Расширенная защита до 3 устройств",
        "Расширенный родительский контроль",
        "AI-помощник для безопасности",
        "Умная блокировка контента",
        "Блокировка по расписанию",
        "Защита от кибербуллинга",
        "Мониторинг социальных сетей"
    ],
    'family': [
        "Защита от более чем 80% видов угроз",
        "До 5 устройств одновременно",
        "Родительский контроль для всех детей",
        "Геозоны всех устройств семьи",
        "Настраиваемые правила для каждого ребенка",
        "Защита от кибербуллинга для всех детей",
        "Блокировка приложений по возрасту"
    ],
    'premium': [
        "Защита до 10 устройств",
        "Все функции семейного тарифа",
        "Продвинутый AI-помощник с обучением",
        "Расширенная защита от всех типов угроз",
        "Интеграция с умным домом",
        "Мониторинг утечек в темной сети",
        "Защита от всех видов мошенничества"
    ]
}

# ЗАГОЛОВКИ ТАРИФОВ (на английском)
TITLES = {
    'individual': 'ALADDIN INDIVIDUAL',
    'family': 'ALADDIN FAMILY',
    'premium': 'ALADDIN PREMIUM'
}

# ИКОНКИ ДЛЯ ФУНКЦИЙ (emoji как простой вариант)
ICONS = {
    'individual': ['🛡️', '👤', '🤖', '🔒', '⏰', '🛡️', '📱'],
    'family': ['🛡️', '📱', '👨‍👩‍👧‍👦', '📍', '⚙️', '🛡️', '📱'],
    'premium': ['🛡️', '⭐', '🤖', '🛡️', '🏠', '🌐', '💰']
}

def hex_to_rgb(hex_color):
    """Конвертирует hex цвет в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size, bold=False):
    """Получает шрифт нужного размера"""
    try:
        # Пробуем использовать системный шрифт
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except:
        try:
            if bold:
                return ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", size)
            return ImageFont.truetype("/Library/Fonts/Arial.ttf", size)
        except:
            return ImageFont.load_default()

def create_gradient_background(size, color1, color2, color3):
    """Создает градиентный фон"""
    img = Image.new('RGB', size, color1)
    draw = ImageDraw.Draw(img)
    
    for y in range(size[1]):
        ratio = y / size[1]
        if ratio < 0.5:
            r = int(color1[0] * (1 - ratio*2) + color2[0] * (ratio*2))
            g = int(color1[1] * (1 - ratio*2) + color2[1] * (ratio*2))
            b = int(color1[2] * (1 - ratio*2) + color2[2] * (ratio*2))
        else:
            r = int(color2[0] * (1 - (ratio-0.5)*2) + color3[0] * ((ratio-0.5)*2))
            g = int(color2[1] * (1 - (ratio-0.5)*2) + color3[1] * ((ratio-0.5)*2))
            b = int(color2[2] * (1 - (ratio-0.5)*2) + color3[2] * ((ratio-0.5)*2))
        
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return img

# ============================================================================
# ВАРИАНТ #7: КОМБИНИРОВАННЫЙ (Крупные цифры + иконки)
# ============================================================================

def create_v7_image(tariff_type):
    """Вариант #7: Крупные цифры (120pt) + иконки (100px) + текст"""
    colors = COLORS[tariff_type]
    bg = create_gradient_background(
        (CANVAS_SIZE, CANVAS_SIZE),
        hex_to_rgb(colors['gradient1']),
        hex_to_rgb(colors['gradient2']),
        hex_to_rgb(colors['gradient3'])
    )
    
    draw = ImageDraw.Draw(bg)
    main_color = hex_to_rgb(colors['main'])
    accent_color = hex_to_rgb(colors.get('accent', colors['main']))
    
    # ЗАГОЛОВОК (72pt, жирный, вверху по центру)
    title_font = get_font(72, bold=True)
    title_text = TITLES[tariff_type]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    title_y = 60
    
    # Тень для заголовка
    draw.text((title_x + 4, title_y + 4), title_text, font=title_font, fill=(0, 0, 0, 180))
    draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
    
    # ФУНКЦИИ - крупные цифры + текст (БЕЗ иконок и полосок)
    features = FEATURES_7[tariff_type]
    
    # Шрифты
    num_font = get_font(120, bold=True)  # ОЧЕНЬ крупные цифры
    text_font = get_font(32, bold=True)  # Крупный текст функций
    
    # Отступы
    padding_left = 80
    padding_top = 180
    padding_bottom = 60
    available_height = CANVAS_SIZE - padding_top - padding_bottom
    
    # Распределяем функции равномерно
    num_features = len(features)
    if num_features > 1:
        line_spacing = available_height / num_features
    else:
        line_spacing = 80
    
    y_start = padding_top
    
    for i, feature in enumerate(features):
        y_pos = int(y_start + i * line_spacing)
        num = i + 1
        
        # НОМЕР (50pt)
        num_text = str(num)
        num_bbox = draw.textbbox((0, 0), num_text, font=num_font)
        num_width = num_bbox[2] - num_bbox[0]
        num_height = num_bbox[3] - num_bbox[1]
        num_x = padding_left
        # Выравниваем по базовой линии - учитываем высоту цифры
        num_y = y_pos - num_bbox[1]  # Используем смещение из bbox для выравнивания
        
        # Тень для номера
        draw.text((num_x + 5, num_y + 5), num_text, font=num_font, fill=(0, 0, 0, 180))
        draw.text((num_x, num_y), num_text, font=num_font, fill=main_color)
        
        # ТЕКСТ ФУНКЦИИ (32pt, справа от номера, БЕЗ иконок, выровнен с цифрой)
        text_bbox = draw.textbbox((0, 0), feature, font=text_font)
        text_x = num_x + num_width + 50
        # Выравниваем текст по той же базовой линии что и цифра
        text_y = y_pos - text_bbox[1]  # Используем смещение из bbox для выравнивания
        
        # Тень для текста
        draw.text((text_x + 3, text_y + 3), feature, font=text_font, fill=(0, 0, 0, 180))
        draw.text((text_x, text_y), feature, font=text_font, fill=(255, 255, 255))
    
    # Рамка (тонкая, декоративная)
    border_width = 6
    border_offset = 30
    draw.rectangle([border_offset, border_offset, CANVAS_SIZE-border_offset, CANVAS_SIZE-border_offset],
                  outline=main_color, width=border_width)
    
    return bg

# ============================================================================
# ВАРИАНТ #1: FLAT-ДИЗАЙН (Плоские иконки в цветных квадратах)
# ============================================================================

def create_v1_image(tariff_type):
    """Вариант #1: Flat-дизайн - крупные иконки в плоских цветных квадратах"""
    colors = COLORS[tariff_type]
    bg = create_gradient_background(
        (CANVAS_SIZE, CANVAS_SIZE),
        hex_to_rgb(colors['gradient1']),
        hex_to_rgb(colors['gradient2']),
        hex_to_rgb(colors['gradient3'])
    )
    
    draw = ImageDraw.Draw(bg)
    main_color = hex_to_rgb(colors['main'])
    accent_color = hex_to_rgb(colors.get('accent', colors['main']))
    
    # ЗАГОЛОВОК (72pt, жирный, вверху по центру)
    title_font = get_font(72, bold=True)
    title_text = TITLES[tariff_type]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    title_y = 60
    
    # Тень для заголовка
    draw.text((title_x + 4, title_y + 4), title_text, font=title_font, fill=(0, 0, 0, 180))
    draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
    
    # ФУНКЦИИ БЕЗ ИКОНОК И КВАДРАТОВ (только номера и текст)
    features = FEATURES_7[tariff_type]
    
    # Шрифты
    num_font = get_font(50, bold=True)  # Средние цифры (как на другой карточке)
    text_font = get_font(32, bold=True)  # Крупный текст функций
    
    # Отступы
    padding_left = 80
    padding_top = 180  # Начинаем сразу после заголовка (без декоративных элементов)
    padding_bottom = 60
    available_height = CANVAS_SIZE - padding_top - padding_bottom
    
    # Распределяем функции равномерно
    num_features = len(features)
    if num_features > 1:
        line_spacing = available_height / num_features
    else:
        line_spacing = 80
    
    y_start = padding_top
    
    for i, feature in enumerate(features):
        y_pos = int(y_start + i * line_spacing)
        num = i + 1
        
        # НОМЕР (50pt)
        num_text = str(num)
        num_bbox = draw.textbbox((0, 0), num_text, font=num_font)
        num_width = num_bbox[2] - num_bbox[0]
        num_height = num_bbox[3] - num_bbox[1]
        num_x = padding_left
        # Выравниваем по базовой линии - учитываем высоту цифры
        num_y = y_pos - num_bbox[1]  # Используем смещение из bbox для выравнивания
        
        # Тень для номера
        draw.text((num_x + 5, num_y + 5), num_text, font=num_font, fill=(0, 0, 0, 180))
        draw.text((num_x, num_y), num_text, font=num_font, fill=main_color)
        
        # ТЕКСТ ФУНКЦИИ (справа от номера, БЕЗ иконок и квадратов, выровнен с цифрой)
        text_bbox = draw.textbbox((0, 0), feature, font=text_font)
        text_x = num_x + num_width + 50
        # Выравниваем текст по той же базовой линии что и цифра
        text_y = y_pos - text_bbox[1]  # Используем смещение из bbox для выравнивания
        
        # Тень для текста
        draw.text((text_x + 3, text_y + 3), feature, font=text_font, fill=(0, 0, 0, 180))
        draw.text((text_x, text_y), feature, font=text_font, fill=(255, 255, 255))
    
    # Рамка (тонкая)
    border_width = 6
    border_offset = 30
    draw.rectangle([border_offset, border_offset, CANVAS_SIZE-border_offset, CANVAS_SIZE-border_offset],
                  outline=main_color, width=border_width)
    
    return bg

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Генерирует оба варианта для всех тарифов (только русские)"""
    
    output_dir = "tariff_images_1024x1024"
    os.makedirs(output_dir, exist_ok=True)
    
    tariffs = ['individual', 'family', 'premium']
    
    print("🎨 Генерация промо-изображений IAP...")
    print("=" * 60)
    
    for tariff in tariffs:
        print(f"\n📱 {tariff.upper()}:")
        
        # Вариант #7: Комбинированный
        print("  ⚙️  Создание варианта #7 (Комбинированный)...")
        img_v7 = create_v7_image(tariff)
        filename_v7 = f"{output_dir}/{tariff}_ru_v7_1024x1024.png"
        img_v7.save(filename_v7, "PNG", dpi=(DPI, DPI))
        print(f"  ✅ Сохранено: {filename_v7}")
        
        # Вариант #1: Flat-дизайн
        print("  ⚙️  Создание варианта #1 (Flat-дизайн)...")
        img_v1 = create_v1_image(tariff)
        filename_v1 = f"{output_dir}/{tariff}_ru_v1_1024x1024.png"
        img_v1.save(filename_v1, "PNG", dpi=(DPI, DPI))
        print(f"  ✅ Сохранено: {filename_v1}")
    
    print("\n" + "=" * 60)
    print("✅ Все изображения созданы успешно!")
    print(f"\n📁 Папка: {output_dir}/")
    print("\nСозданные файлы:")
    for tariff in tariffs:
        print(f"  - {tariff}_ru_v7_1024x1024.png (Вариант #7)")
        print(f"  - {tariff}_ru_v1_1024x1024.png (Вариант #1)")

if __name__ == '__main__':
    main()
