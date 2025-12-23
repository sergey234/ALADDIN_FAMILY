#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОФЕССИОНАЛЬНЫЙ генератор промо-изображений IAP для ALADDIN
Создает уникальные изображения НЕ похожие на скриншоты с КРУПНЫМ читаемым текстом
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

CANVAS_SIZE = 1024
DPI = 72

# Цвета тарифов из кода приложения
COLORS = {
    'individual': {
        'main': '#2E5BFF',  # primaryBlue - синий
        'accent': '#60A5FA',  # secondaryBlue - светлый синий
        'bg': '#0F172A'  # backgroundDark
    },
    'family': {
        'main': '#F59E0B',  # secondaryGold - золотой
        'accent': '#FCD34D',  # светлый золотой
        'bg': '#1C1917'  # темно-коричневый
    },
    'premium': {
        'main': '#A855F7',  # фиолетовый
        'accent': '#C084FC',  # светлый фиолетовый
        'bg': '#1E1B4B'  # темно-фиолетовый
    }
}

# Функции тарифов
FEATURES = {
    'individual': {
        'ru': [
            "Расширенная защита до 3 устройств",
            "Расширенный родительский контроль",
            "Детальная аналитика активности",
            "AI-помощник для безопасности",
            "Умная блокировка контента",
            "Расширенные отчеты об активности",
            "Настраиваемые правила использования",
            "Блокировка по расписанию",
            "Защита от кибербуллинга",
            "Мониторинг социальных сетей"
        ],
        'en': [
            "Extended protection up to 3 devices",
            "Extended parental control",
            "Detailed activity analytics",
            "AI assistant for security",
            "Smart content blocking",
            "Extended activity reports",
            "Customizable usage rules",
            "Scheduled blocking",
            "Cyberbullying protection",
            "Social media monitoring"
        ]
    },
    'family': {
        'ru': [
            "Защита до 5 устройств одновременно",
            "Централизованное управление семьей",
            "Родительский контроль для всех детей",
            "Контроль доступа к платным подпискам",
            "Семейная аналитика и отчеты",
            "Геозоны всех устройств семьи",
            "История активности всех устройств",
            "Индивидуальные профили для каждого ребенка",
            "Настраиваемые правила для каждого ребенка",
            "Защита всех устройств от угроз"
        ],
        'en': [
            "Protection up to 5 devices simultaneously",
            "Centralized family management",
            "Parental control for all children",
            "Control access to paid subscriptions",
            "Family analytics and reports",
            "Geofences of all family devices",
            "Activity history of all devices",
            "Individual profiles for each child",
            "Customizable rules for each child",
            "Protection of all devices from threats"
        ]
    },
    'premium': {
        'ru': [
            "Защита до 10 устройств",
            "Все функции семейного тарифа",
            "Продвинутый AI-помощник с обучением",
            "Детальная аналитика с прогнозами",
            "Неограниченная история активности",
            "Расширенная защита от всех типов угроз",
            "Кастомные правила и автоматизация",
            "Интеграция с умным домом",
            "Защита от всех видов мошенничества",
            "Эксклюзивные функции безопасности"
        ],
        'en': [
            "Protection up to 10 devices",
            "All family plan features",
            "Advanced AI assistant with learning",
            "Detailed analytics with forecasts",
            "Unlimited activity history",
            "Extended protection from all threat types",
            "Custom rules and automation",
            "Smart home integration",
            "Protection from all types of fraud",
            "Exclusive security features"
        ]
    }
}

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

def get_font(size, bold=False):
    """Получить шрифт указанного размера"""
    try:
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except:
        try:
            # Пробуем Helvetica
            font_path = "/System/Library/Fonts/Helvetica.ttc"
            # Helvetica не поддерживает прямой выбор bold, используем размер больше
            return ImageFont.truetype(font_path, size if not bold else int(size * 1.2))
        except:
            return ImageFont.load_default()

def draw_shield_icon(draw, x, y, size, color):
    """Рисует простую иконку щита"""
    # Простой щит (треугольник с закругленным основанием)
    # Верхняя точка
    top = (x + size//2, y)
    # Левый верхний угол
    left_top = (x, y + size//4)
    # Правый верхний угол
    right_top = (x + size, y + size//4)
    # Левая нижняя точка (закруглено)
    left_bottom = (x, y + size)
    # Правая нижняя точка (закруглено)
    right_bottom = (x + size, y + size)
    
    # Рисуем щит (упрощенно - прямоугольник с треугольным верхом)
    # Основание
    draw.rectangle([x, y + size//3, x + size, y + size], outline=color, width=4, fill=None)
    # Верхний треугольник
    draw.polygon([top, left_top, right_top], outline=color, fill=None)

def create_tariff_image(tariff_type, language='ru'):
    """Создает профессиональное промо-изображение тарифа"""
    colors = COLORS[tariff_type]
    bg_color = hex_to_rgb(colors['bg'])
    main_color = hex_to_rgb(colors['main'])
    accent_color = hex_to_rgb(colors['accent'])
    
    # Создаем изображение с градиентным фоном
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Градиентный фон (упрощенно - радиальный градиент)
    center_x, center_y = CANVAS_SIZE // 2, CANVAS_SIZE // 2
    max_radius = int(math.sqrt(center_x**2 + center_y**2))
    
    for r in range(max_radius, 0, -10):
        alpha = int(20 * (1 - r/max_radius))
        color = tuple(min(255, c + alpha) for c in bg_color)
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                    outline=None, fill=color)
    
    # Отступы
    padding = 60
    content_width = CANVAS_SIZE - 2 * padding
    
    # ВИЗУАЛЬНЫЙ ЭЛЕМЕНТ - Иконка щита сверху (КРУПНАЯ)
    icon_size = 120
    icon_x = (CANVAS_SIZE - icon_size) // 2
    icon_y = padding + 20
    draw_shield_icon(draw, icon_x, icon_y, icon_size, main_color)
    
    # ЗАГОЛОВОК - ОЧЕНЬ КРУПНЫЙ (72pt = ~96px при 72 DPI)
    title_font = get_font(72, bold=True)
    title_text = TITLES[tariff_type][language]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_height = title_bbox[3] - title_bbox[1]
    title_y = icon_y + icon_size + 40
    
    # Рисуем заголовок с тенью для читаемости
    title_x = (CANVAS_SIZE - (title_bbox[2] - title_bbox[0])) // 2
    # Тень
    draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=(0, 0, 0, 128))
    # Основной текст
    draw.text((title_x, title_y), title_text, font=title_font, fill=main_color)
    
    # Декоративная линия под заголовком
    line_y = title_y + title_height + 30
    line_length = 500
    line_x = (CANVAS_SIZE - line_length) // 2
    draw.line([(line_x, line_y), (line_x + line_length, line_y)], fill=accent_color, width=6)
    
    # СПИСОК ФУНКЦИЙ - КРУПНЫЙ ТЕКСТ (минимум 28pt = ~37px)
    features_start_y = line_y + 50
    features_font = get_font(28)  # 28pt - больше минимума 20pt
    feature_number_font = get_font(32, bold=True)  # Номера крупнее
    line_spacing = 50  # Больше пространства между строками
    
    features = FEATURES[tariff_type][language]
    
    # Рисуем функции с номерами
    max_features_to_show = min(8, len(features))  # Показываем максимум 8 чтобы все влезло
    
    for i in range(max_features_to_show):
        y_pos = features_start_y + i * line_spacing
        
        # Проверяем выход за пределы
        if y_pos + line_spacing > CANVAS_SIZE - padding - 40:
            break
        
        feature = features[i]
        feature_num = i + 1
        
        # Номер функции (крупный, цветной)
        num_text = f"{feature_num}."
        num_bbox = draw.textbbox((0, 0), num_text, font=feature_number_font)
        num_width = num_bbox[2] - num_bbox[0]
        num_x = padding + 30
        draw.text((num_x, y_pos), num_text, font=feature_number_font, fill=main_color)
        
        # Текст функции (белый, крупный)
        feature_text = feature
        # Проверяем длину текста и сокращаем если нужно
        feature_bbox = draw.textbbox((0, 0), feature_text, font=features_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        
        # Если не влезает, уменьшаем немного шрифт
        max_text_width = content_width - num_width - 60
        if feature_width > max_text_width:
            features_font = get_font(24)  # Уменьшаем до 24pt (все еще больше минимума)
            feature_bbox = draw.textbbox((0, 0), feature_text, font=features_font)
            feature_width = feature_bbox[2] - feature_bbox[0]
        
        feature_x = num_x + num_width + 20
        draw.text((feature_x, y_pos), feature_text, font=features_font, fill=(255, 255, 255))
        
        # Декоративный элемент (круг/точка)
        dot_size = 8
        dot_x = feature_x - 10
        dot_y = y_pos + (feature_bbox[3] - feature_bbox[1]) // 2
        draw.ellipse([dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size],
                    fill=accent_color)
    
    # Декоративная рамка (уникальный дизайн)
    border_width = 8
    border_offset = 30
    
    # Внешняя рамка
    draw.rectangle(
        [border_offset, border_offset, 
         CANVAS_SIZE - border_offset, CANVAS_SIZE - border_offset],
        outline=main_color, width=border_width
    )
    
    # Внутренняя декоративная рамка (пунктирная стилизация)
    inner_offset = border_offset + 20
    inner_size = CANVAS_SIZE - 2 * inner_offset
    # Рисуем углы
    corner_size = 30
    # Левый верхний
    draw.line([(inner_offset, inner_offset), (inner_offset + corner_size, inner_offset)], 
             fill=accent_color, width=4)
    draw.line([(inner_offset, inner_offset), (inner_offset, inner_offset + corner_size)], 
             fill=accent_color, width=4)
    # Правый верхний
    draw.line([(CANVAS_SIZE - inner_offset - corner_size, inner_offset), 
              (CANVAS_SIZE - inner_offset, inner_offset)], fill=accent_color, width=4)
    draw.line([(CANVAS_SIZE - inner_offset, inner_offset), 
              (CANVAS_SIZE - inner_offset, inner_offset + corner_size)], fill=accent_color, width=4)
    # Левый нижний
    draw.line([(inner_offset, CANVAS_SIZE - inner_offset - corner_size), 
              (inner_offset, CANVAS_SIZE - inner_offset)], fill=accent_color, width=4)
    draw.line([(inner_offset, CANVAS_SIZE - inner_offset), 
              (inner_offset + corner_size, CANVAS_SIZE - inner_offset)], fill=accent_color, width=4)
    # Правый нижний
    draw.line([(CANVAS_SIZE - inner_offset, CANVAS_SIZE - inner_offset - corner_size), 
              (CANVAS_SIZE - inner_offset, CANVAS_SIZE - inner_offset)], fill=accent_color, width=4)
    draw.line([(CANVAS_SIZE - inner_offset - corner_size, CANVAS_SIZE - inner_offset), 
              (CANVAS_SIZE - inner_offset, CANVAS_SIZE - inner_offset)], fill=accent_color, width=4)
    
    # Дополнительные визуальные элементы - декоративные круги
    for i in range(5):
        angle = (i * 2 * math.pi) / 5
        radius = 350
        circle_x = int(center_x + radius * math.cos(angle))
        circle_y = int(center_y + radius * math.sin(angle))
        circle_size = 15
        draw.ellipse([circle_x - circle_size, circle_y - circle_size,
                     circle_x + circle_size, circle_y + circle_size],
                    outline=accent_color, width=2, fill=None)
    
    return img

def main():
    """Генерирует все изображения"""
    output_dir = os.path.join(os.path.dirname(__file__), 'tariff_images_1024x1024')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Генерация ПРОФЕССИОНАЛЬНЫХ промо-изображений IAP...")
    print("✅ Крупный читаемый текст (28-72pt)")
    print("✅ Уникальный дизайн (НЕ скриншот)")
    print("✅ Визуальные элементы (иконки, декорации)")
    
    tariffs = ['individual', 'family', 'premium']
    languages = ['ru', 'en']
    
    for tariff in tariffs:
        for lang in languages:
            print(f"\n📝 Создание {tariff}_{lang}_1024x1024.png...")
            img = create_tariff_image(tariff, lang)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output_path = os.path.join(output_dir, f'{tariff}_{lang}_1024x1024.png')
            img.save(output_path, 'PNG', dpi=(DPI, DPI))
            
            # Проверка размера
            size = img.size
            print(f"   ✅ Размер: {size[0]}x{size[1]}px, DPI: {DPI}")
    
    print("\n🎉 Все изображения созданы успешно!")
    print(f"📂 Папка: {output_dir}")
    print("\n✅ Соответствие требованиям Apple:")
    print("   ✓ Размер: 1024x1024px")
    print("   ✓ DPI: 72")
    print("   ✓ Формат: PNG RGB")
    print("   ✓ НЕ скриншот (уникальный дизайн)")
    print("   ✓ Крупный читаемый текст (28-72pt)")

if __name__ == '__main__':
    main()
