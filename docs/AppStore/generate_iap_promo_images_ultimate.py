#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УНИКАЛЬНЫЙ генератор промо-изображений IAP для ALADDIN
Использует цвета главной страницы (золото-фиолетовый-синий) с элементами защиты и AI
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

CANVAS_SIZE = 1024
DPI = 72

# ЦВЕТА ИЗ ГЛАВНОЙ СТРАНИЦЫ И ПРИЛОЖЕНИЯ
COLORS = {
    'individual': {
        'main': '#2E5BFF',      # primaryBlue - синий (из главной страницы)
        'accent': '#60A5FA',    # secondaryBlue - светлый синий
        'gold': '#F59E0B',      # secondaryGold - золотой (топ цвет)
        'bg': '#0F172A',        # backgroundDark
        'gradient1': '#0a1128', # gradientStart
        'gradient2': '#1e3a5f', # gradientMiddle
        'gradient3': '#2e5090'  # gradientEnd
    },
    'family': {
        'main': '#F59E0B',      # secondaryGold - золотой (топ цвет)
        'accent': '#FCD34D',    # светлый золотой
        'purple': '#A855F7',    # Premium цвет - фиолетовый
        'bg': '#1C1917',
        'gradient1': '#3d2817',
        'gradient2': '#6b4423',
        'gradient3': '#9c6e2f'
    },
    'premium': {
        'main': '#A855F7',      # Premium - фиолетовый (топ цвет)
        'accent': '#C084FC',    # светлый фиолетовый
        'gold': '#F59E0B',      # золотой акцент
        'blue': '#2E5BFF',      # синий акцент
        'bg': '#1E1B4B',
        'gradient1': '#2d1b69',
        'gradient2': '#4c2a9e',
        'gradient3': '#6b3bd3'
    }
}

# САМЫЕ ВАЖНЫЕ ФУНКЦИИ (выбраны из того что вы отправляли)
FEATURES = {
    'individual': {
        'ru': [
            "Расширенная защита до 3 устройств",
            "Расширенный родительский контроль",
            "AI-помощник для безопасности",
            "Умная блокировка контента",
            "Блокировка по расписанию",
            "Защита от кибербуллинга",
            "Мониторинг социальных сетей",
            "Детектирование подозрительной активности",
            "Защита от кражи данных",
            "Блокировка нежелательных звонков"
        ],
        'en': [
            "Extended protection up to 3 devices",
            "Extended parental control",
            "AI assistant for security",
            "Smart content blocking",
            "Scheduled blocking",
            "Cyberbullying protection",
            "Social media monitoring",
            "Suspicious activity detection",
            "Data theft protection",
            "Unwanted calls blocking"
        ]
    },
    'family': {
        'ru': [
            "Защита от более чем 80% видов угроз",
            "До 5 устройств одновременно",
            "Родительский контроль для всех детей",
            "Контроль доступа к платным подпискам",
            "Геозоны всех устройств семьи",
            "Настраиваемые правила для каждого ребенка",
            "Блокировка нежелательных контактов",
            "Мониторинг социальных сетей всех детей",
            "Защита от кибербуллинга для всех детей",
            "Блокировка приложений по возрасту ребенка",
            "Контроль расходов на покупки в приложениях",
            "Автоматическая блокировка в ночное время",
            "Защита от нежелательного контента в поиске",
            "Защита от фишинга и мошенничества",
            "Блокировка игр с возрастными ограничениями"
        ],
        'en': [
            "Protection from more than 80% of threat types",
            "Up to 5 devices simultaneously",
            "Parental control for all children",
            "Control access to paid subscriptions",
            "Geofences of all family devices",
            "Customizable rules for each child",
            "Blocking unwanted contacts",
            "Social media monitoring for all children",
            "Cyberbullying protection for all children",
            "App blocking by child's age",
            "Purchase spending control in apps",
            "Automatic blocking at night",
            "Undesirable content protection in search",
            "Phishing and fraud protection",
            "Age-restricted game blocking"
        ]
    },
    'premium': {
        'ru': [
            "Защита до 10 устройств",
            "Все функции семейного тарифа",
            "Продвинутый AI-помощник с обучением",
            "Расширенная защита от всех типов угроз",
            "Интеграция с умным домом",
            "Защита от всех видов мошенничества",
            "Продвинутый мониторинг всех каналов связи",
            "Детектирование и предотвращение угроз в реальном времени",
            "Эксклюзивные функции безопасности",
            "Поведенческий анализ",
            "Мониторинг утечек в темной сети",
            "Защита от продвинутого фишинга",
            "Защита от шпионского ПО",
            "Защита от социальной инженерии",
            "Продвинутая защита от шпионского ПО и троянов",
            "Детектирование подозрительных паттернов поведения",
            "Расширенная защита банковских приложений и платежей",
            "Мониторинг утечек данных из всех подключенных сервисов",
            "Защита от кражи личности и мошенничества с документами"
        ],
        'en': [
            "Protection up to 10 devices",
            "All family plan features",
            "Advanced AI assistant with learning",
            "Extended protection from all threat types",
            "Smart home integration",
            "Protection from all types of fraud",
            "Advanced monitoring of all communication channels",
            "Real-time threat detection and prevention",
            "Exclusive security features",
            "Behavioral analysis",
            "Dark web leak monitoring",
            "Advanced phishing protection",
            "Spyware protection",
            "Social engineering protection",
            "Advanced spyware and trojan protection",
            "Suspicious behavior pattern detection",
            "Extended bank app and payment protection",
            "Data leak monitoring from all connected services",
            "Identity theft and document fraud protection"
        ]
    }
}

TITLES = {
    'individual': {
        'ru': 'ALADDIN ЛИЧНЫЙ ТАРИФ',
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

# ИЗЮМИНКА КАЖДОГО ТАРИФА
HIGHLIGHTS = {
    'individual': {
        'ru': 'AI-ЗАЩИТА',
        'en': 'AI PROTECTION'
    },
    'family': {
        'ru': 'СЕМЕЙНАЯ ЗАЩИТА',
        'en': 'FAMILY PROTECTION'
    },
    'premium': {
        'ru': '99% ЗАЩИТА',
        'en': '99% PROTECTION'
    }
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size if not bold else int(size * 1.2))
        except:
            return ImageFont.load_default()

def draw_shield_with_ai(draw, x, y, size, color, accent_color):
    """Рисует щит с AI символом внутри"""
    # Щит (треугольник с закругленным основанием)
    shield_width = size
    shield_height = int(size * 1.2)
    
    # Вершина щита
    top = (x + shield_width//2, y)
    # Левый верх
    left_top = (x, y + shield_height//4)
    # Правый верх
    right_top = (x + shield_width, y + shield_height//4)
    # Левая нижняя
    left_bottom = (x + shield_width//4, y + shield_height)
    # Правая нижняя
    right_bottom = (x + 3*shield_width//4, y + shield_height)
    
    # Рисуем щит
    draw.polygon([top, left_top, left_bottom, right_bottom, right_top], 
                outline=color, fill=None, width=6)
    
    # AI символ внутри (стилизованный мозг/шестеренка)
    ai_size = shield_width // 3
    ai_x = x + shield_width//2
    ai_y = y + shield_height//2
    
    # Внешний круг AI
    draw.ellipse([ai_x - ai_size, ai_y - ai_size, ai_x + ai_size, ai_y + ai_size],
                outline=accent_color, width=4)
    # Внутренние линии (символизирующие нейросеть)
    for i in range(4):
        angle = i * math.pi / 2
        x1 = ai_x + int(ai_size * 0.7 * math.cos(angle))
        y1 = ai_y + int(ai_size * 0.7 * math.sin(angle))
        x2 = ai_x + int(ai_size * 0.3 * math.cos(angle + math.pi/4))
        y2 = ai_y + int(ai_size * 0.3 * math.sin(angle + math.pi/4))
        draw.line([(ai_x, ai_y), (x1, y1)], fill=accent_color, width=2)
        draw.line([(x1, y1), (x2, y2)], fill=accent_color, width=2)

def draw_protection_ring(draw, center_x, center_y, radius, color, segments=8):
    """Рисует кольцо защиты с сегментами"""
    for i in range(segments):
        angle1 = i * 2 * math.pi / segments
        angle2 = (i + 1) * 2 * math.pi / segments
        
        x1 = center_x + int(radius * math.cos(angle1))
        y1 = center_y + int(radius * math.sin(angle1))
        x2 = center_x + int(radius * math.cos(angle2))
        y2 = center_y + int(radius * math.sin(angle2))
        
        draw.line([(x1, y1), (x2, y2)], fill=color, width=4)

def create_gradient_background(size, color1, color2, color3):
    """Создает градиентный фон"""
    img = Image.new('RGB', size, color1)
    draw = ImageDraw.Draw(img)
    
    # Вертикальный градиент
    for y in range(size[1]):
        ratio = y / size[1]
        if ratio < 0.5:
            # От color1 к color2
            r = int(color1[0] * (1 - ratio*2) + color2[0] * (ratio*2))
            g = int(color1[1] * (1 - ratio*2) + color2[1] * (ratio*2))
            b = int(color1[2] * (1 - ratio*2) + color2[2] * (ratio*2))
        else:
            # От color2 к color3
            r = int(color2[0] * (1 - (ratio-0.5)*2) + color3[0] * ((ratio-0.5)*2))
            g = int(color2[1] * (1 - (ratio-0.5)*2) + color3[1] * ((ratio-0.5)*2))
            b = int(color2[2] * (1 - (ratio-0.5)*2) + color3[2] * ((ratio-0.5)*2))
        
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return img

def create_individual_image(language='ru'):
    """INDIVIDUAL - Синий с золотыми акцентами + AI"""
    colors = COLORS['individual']
    bg = create_gradient_background(
        (CANVAS_SIZE, CANVAS_SIZE),
        hex_to_rgb(colors['gradient1']),
        hex_to_rgb(colors['gradient2']),
        hex_to_rgb(colors['gradient3'])
    )
    
    draw = ImageDraw.Draw(bg)
    main_color = hex_to_rgb(colors['main'])
    gold_color = hex_to_rgb(colors['gold'])
    accent_color = hex_to_rgb(colors['accent'])
    
    # ЗАЩИТНОЕ КОЛЬЦО (верх, немного ниже чтобы не перекрывать AI-ЗАЩИТА)
    draw_protection_ring(draw, CANVAS_SIZE//2, 180, 130, main_color, 12)
    
    # AI ЩИТ в центре верха (чуть выше)
    shield_size = 120
    shield_x = (CANVAS_SIZE - shield_size) // 2
    shield_y = 100
    draw_shield_with_ai(draw, shield_x, shield_y, shield_size, main_color, gold_color)
    
    # ЗАГОЛОВОК (смещен вниз на 1-2 см ~50px)
    title_font = get_font(64, bold=True)  # Немного меньше чтобы уместилось
    title_text = TITLES['individual'][language]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_x = (CANVAS_SIZE - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 300  # Смещен вниз на 50px (было 250)
    
    # Тень заголовка
    draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=(0, 0, 0, 128))
    # Заголовок
    draw.text((title_x, title_y), title_text, font=title_font, fill=gold_color)
    
    # ИЗЮМИНКА - AI-ЗАЩИТА (правый верхний угол)
    highlight_font = get_font(28, bold=True)
    highlight_text = HIGHLIGHTS['individual'][language]
    highlight_bbox = draw.textbbox((0, 0), highlight_text, font=highlight_font)
    highlight_width = highlight_bbox[2] - highlight_bbox[0]
    # Правый верхний угол с отступом
    highlight_x = CANVAS_SIZE - highlight_width - 40  # 40px отступ справа
    highlight_y = 50  # 50px отступ сверху
    
    draw.text((highlight_x, highlight_y), highlight_text, font=highlight_font, fill=accent_color)
    
    # ФУНКЦИИ - крупнее, распределены на всю высоту страницы
    features_font = get_font(28)  # Крупнее
    feature_num_font = get_font(32, bold=True)  # Крупнее
    features = FEATURES['individual'][language]
    
    # Отступы для текста (больше чтобы не заходили за края)
    padding_left = 80
    padding_right = 80
    padding_top = 380  # Отступ сверху (после заголовка и AI-защита, смещен вниз на 50px)
    padding_bottom = 70  # Отступ снизу
    
    # Доступная высота для всех функций
    available_height = CANVAS_SIZE - padding_top - padding_bottom
    
    # Рассчитываем равномерное расстояние между функциями
    num_features = len(features)
    if num_features > 1:
        line_spacing = available_height / (num_features - 1)  # Равномерное распределение
    else:
        line_spacing = 50
    
    # Максимальная ширина текста
    max_text_width = CANVAS_SIZE - padding_left - padding_right
    x_start = padding_left
    
    # Рисуем все функции по порядку, распределенные на всю высоту
    for i, feature in enumerate(features):
        num = i + 1
        # Равномерное распределение по высоте
        if num_features == 1:
            y_pos = padding_top
        else:
            y_pos = int(padding_top + i * line_spacing)
        
        # Номер функции (золотой цвет, крупный)
        draw.text((x_start, y_pos), f"{num}.", font=feature_num_font, fill=gold_color)
        
        # Текст функции (белый цвет)
        text_start_x = x_start + 50  # Отступ от номера
        
        # Проверяем ширину текста
        feature_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        max_text_for_line = max_text_width - 50  # Минус место для номера
        
        # Если текст не влезает, уменьшаем шрифт или сокращаем
        if feature_width > max_text_for_line:
            # Пробуем уменьшить шрифт
            smaller_font = get_font(26)
            smaller_bbox = draw.textbbox((0, 0), feature, font=smaller_font)
            if smaller_bbox[2] - smaller_bbox[0] <= max_text_for_line:
                # Уменьшенный шрифт подходит
                draw.text((text_start_x, y_pos), feature, font=smaller_font, fill=(255, 255, 255))
            else:
                # Еще меньше
                smallest_font = get_font(24)
                smallest_bbox = draw.textbbox((0, 0), feature, font=smallest_font)
                if smallest_bbox[2] - smallest_bbox[0] <= max_text_for_line:
                    draw.text((text_start_x, y_pos), feature, font=smallest_font, fill=(255, 255, 255))
                else:
                    # Сокращаем текст (редко, но на всякий случай)
                    max_chars = int(max_text_for_line / 13)  # Примерно 13px на символ
                    shortened = feature[:max_chars-3] + "..."
                    draw.text((text_start_x, y_pos), shortened, font=smallest_font, fill=(255, 255, 255))
        else:
            # Текст влезает
            draw.text((text_start_x, y_pos), feature, font=features_font, fill=(255, 255, 255))
        
        # Дополнительная проверка: убеждаемся что текст не выходит за правый край
        final_text_bbox = draw.textbbox((text_start_x, y_pos), feature if feature_width <= max_text_for_line else (feature[:int(max_text_for_line/13)-3] + "..."), font=features_font if feature_width <= max_text_for_line else get_font(24))
        if final_text_bbox[2] > CANVAS_SIZE - padding_right:
            # Если все равно выходит, уменьшаем шрифт принудительно
            emergency_font = get_font(22)
            draw.text((text_start_x, y_pos), feature[:35] + "..." if len(feature) > 35 else feature, font=emergency_font, fill=(255, 255, 255))
    
    # Декоративные элементы - AI символы
    for i in range(6):
        angle = i * 2 * math.pi / 6
        radius = 350
        x = int(CANVAS_SIZE//2 + radius * math.cos(angle))
        y = int(CANVAS_SIZE//2 + radius * math.sin(angle))
        # Маленький AI символ
        draw.ellipse([x-15, y-15, x+15, y+15], outline=accent_color, width=2)
    
    # Рамка с углами
    border_width = 8
    border_offset = 25
    draw.rectangle([border_offset, border_offset, CANVAS_SIZE-border_offset, CANVAS_SIZE-border_offset],
                  outline=main_color, width=border_width)
    
    return bg

def create_family_image(language='ru'):
    """FAMILY - Золотой с фиолетовыми акцентами + Семейная защита"""
    colors = COLORS['family']
    bg = create_gradient_background(
        (CANVAS_SIZE, CANVAS_SIZE),
        hex_to_rgb(colors['gradient1']),
        hex_to_rgb(colors['gradient2']),
        hex_to_rgb(colors['gradient3'])
    )
    
    draw = ImageDraw.Draw(bg)
    main_color = hex_to_rgb(colors['main'])  # золотой
    purple_color = hex_to_rgb(colors['purple'])
    accent_color = hex_to_rgb(colors['accent'])
    
    # СЕМЕЙНАЯ ИКОНКА (заменены на круглые элементы - не "гробики")
    # Вместо щитов используем круги со звездами внутри
    circle_size = 90
    # Взрослый 1 - левый круг
    circle1_x = CANVAS_SIZE//2 - 110
    circle1_y = 110
    draw.ellipse([circle1_x, circle1_y, circle1_x + circle_size, circle1_y + circle_size],
                outline=main_color, width=4, fill=None)
    # Звезда внутри круга 1
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        inner_radius = 25
        x1 = circle1_x + circle_size//2 + int(inner_radius * math.cos(angle))
        y1 = circle1_y + circle_size//2 + int(inner_radius * math.sin(angle))
        draw.line([(circle1_x + circle_size//2, circle1_y + circle_size//2), (x1, y1)],
                 fill=purple_color, width=3)
    
    # Взрослый 2 - правый круг
    circle2_x = CANVAS_SIZE//2 + 20
    circle2_y = 110
    draw.ellipse([circle2_x, circle2_y, circle2_x + circle_size, circle2_y + circle_size],
                outline=main_color, width=4, fill=None)
    # Звезда внутри круга 2
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        inner_radius = 25
        x1 = circle2_x + circle_size//2 + int(inner_radius * math.cos(angle))
        y1 = circle2_y + circle_size//2 + int(inner_radius * math.sin(angle))
        draw.line([(circle2_x + circle_size//2, circle2_y + circle_size//2), (x1, y1)],
                 fill=purple_color, width=3)
    
    # Дети - маленькие круги
    child_size = 60
    child1_x = CANVAS_SIZE//2 - 50
    child1_y = 200
    draw.ellipse([child1_x, child1_y, child1_x + child_size, child1_y + child_size],
                outline=accent_color, width=3, fill=None)
    # Точка внутри
    draw.ellipse([child1_x + child_size//2 - 5, child1_y + child_size//2 - 5,
                 child1_x + child_size//2 + 5, child1_y + child_size//2 + 5],
                fill=accent_color)
    
    child2_x = CANVAS_SIZE//2 + 10
    child2_y = 200
    draw.ellipse([child2_x, child2_y, child2_x + child_size, child2_y + child_size],
                outline=accent_color, width=3, fill=None)
    # Точка внутри
    draw.ellipse([child2_x + child_size//2 - 5, child2_y + child_size//2 - 5,
                 child2_x + child_size//2 + 5, child2_y + child_size//2 + 5],
                fill=accent_color)
    
    # ЗАГОЛОВОК (смещен вниз как в индивидуальном)
    title_font = get_font(64, bold=True)
    title_text = TITLES['family'][language]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_x = (CANVAS_SIZE - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 300  # Смещен вниз
    
    draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=(0, 0, 0, 128))
    draw.text((title_x, title_y), title_text, font=title_font, fill=main_color)
    
    # ИЗЮМИНКА - СЕМЕЙНАЯ ЗАЩИТА (правый верхний угол, как AI-ЗАЩИТА)
    highlight_font = get_font(28, bold=True)
    highlight_text = HIGHLIGHTS['family'][language]
    highlight_bbox = draw.textbbox((0, 0), highlight_text, font=highlight_font)
    highlight_width = highlight_bbox[2] - highlight_bbox[0]
    # Правый верхний угол с отступом
    highlight_x = CANVAS_SIZE - highlight_width - 40  # 40px отступ справа
    highlight_y = 50  # 50px отступ сверху
    
    draw.text((highlight_x, highlight_y), highlight_text, font=highlight_font, fill=purple_color)
    
    # ФУНКЦИИ - крупнее, распределены на всю высоту страницы (как в индивидуальном)
    features_font = get_font(26)  # Немного меньше для большого количества функций
    feature_num_font = get_font(30, bold=True)
    features = FEATURES['family'][language]
    
    # Отступы для текста (больше чтобы не заходили за края)
    padding_left = 80
    padding_right = 80
    padding_top = 380  # Отступ сверху (после заголовка)
    padding_bottom = 70  # Отступ снизу
    
    # Доступная высота для всех функций
    available_height = CANVAS_SIZE - padding_top - padding_bottom
    
    # Рассчитываем равномерное расстояние между функциями
    num_features = len(features)
    if num_features > 1:
        line_spacing = available_height / (num_features - 1)  # Равномерное распределение
    else:
        line_spacing = 50
    
    # Максимальная ширина текста
    max_text_width = CANVAS_SIZE - padding_left - padding_right
    x_start = padding_left
    
    # Рисуем все функции по порядку, распределенные на всю высоту
    for i, feature in enumerate(features):
        num = i + 1
        # Равномерное распределение по высоте
        if num_features == 1:
            y_pos = padding_top
        else:
            y_pos = int(padding_top + i * line_spacing)
        
        # Номер функции (фиолетовый цвет, крупный)
        draw.text((x_start, y_pos), f"{num}.", font=feature_num_font, fill=purple_color)
        
        # Текст функции (белый цвет)
        text_start_x = x_start + 50  # Отступ от номера
        
        # Проверяем ширину текста
        feature_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        max_text_for_line = max_text_width - 50  # Минус место для номера
        
        # Если текст не влезает, уменьшаем шрифт или сокращаем
        if feature_width > max_text_for_line:
            # Пробуем уменьшить шрифт
            smaller_font = get_font(24)
            smaller_bbox = draw.textbbox((0, 0), feature, font=smaller_font)
            if smaller_bbox[2] - smaller_bbox[0] <= max_text_for_line:
                # Уменьшенный шрифт подходит
                draw.text((text_start_x, y_pos), feature, font=smaller_font, fill=(255, 255, 255))
            else:
                # Еще меньше
                smallest_font = get_font(22)
                smallest_bbox = draw.textbbox((0, 0), feature, font=smallest_font)
                if smallest_bbox[2] - smallest_bbox[0] <= max_text_for_line:
                    draw.text((text_start_x, y_pos), feature, font=smallest_font, fill=(255, 255, 255))
                else:
                    # Сокращаем текст
                    max_chars = int(max_text_for_line / 12)  # Примерно 12px на символ
                    shortened = feature[:max_chars-3] + "..."
                    draw.text((text_start_x, y_pos), shortened, font=smallest_font, fill=(255, 255, 255))
        else:
            # Текст влезает
            draw.text((text_start_x, y_pos), feature, font=features_font, fill=(255, 255, 255))
    
    # Рамка
    border_width = 10
    border_offset = 20
    draw.rectangle([border_offset, border_offset, CANVAS_SIZE-border_offset, CANVAS_SIZE-border_offset],
                  outline=main_color, width=border_width)
    
    # Декоративные золотые звезды
    for i in range(8):
        angle = i * 2 * math.pi / 8
        radius = 400
        x = int(CANVAS_SIZE//2 + radius * math.cos(angle))
        y = int(CANVAS_SIZE//2 + radius * math.sin(angle))
        draw.ellipse([x-12, y-12, x+12, y+12], outline=accent_color, width=2, fill=accent_color)
    
    return bg

def create_premium_image(language='ru'):
    """PREMIUM - Фиолетовый с золотыми и синими акцентами + 99% защита"""
    colors = COLORS['premium']
    bg = create_gradient_background(
        (CANVAS_SIZE, CANVAS_SIZE),
        hex_to_rgb(colors['gradient1']),
        hex_to_rgb(colors['gradient2']),
        hex_to_rgb(colors['gradient3'])
    )
    
    draw = ImageDraw.Draw(bg)
    main_color = hex_to_rgb(colors['main'])  # фиолетовый
    gold_color = hex_to_rgb(colors['gold'])
    blue_color = hex_to_rgb(colors['blue'])
    accent_color = hex_to_rgb(colors['accent'])
    
    # ПРЕМИУМ ИКОНКА - только круг с AI (без пятиугольника вокруг)
    # Круг с AI символом внутри (без внешнего пятиугольника)
    circle_size = 140
    circle_x = (CANVAS_SIZE - circle_size) // 2
    circle_y = 100
    
    # Круг (золотая обводка)
    draw.ellipse([circle_x, circle_y, circle_x + circle_size, circle_y + circle_size],
                outline=gold_color, width=6, fill=None)
    
    # AI символ внутри круга (стилизованный)
    ai_center_x = circle_x + circle_size // 2
    ai_center_y = circle_y + circle_size // 2
    ai_radius = 40
    
    # Внешний круг AI
    draw.ellipse([ai_center_x - ai_radius, ai_center_y - ai_radius,
                 ai_center_x + ai_radius, ai_center_y + ai_radius],
                outline=blue_color, width=4)
    
    # Внутренние линии AI (символизирующие нейросеть)
    for i in range(6):
        angle = i * 2 * math.pi / 6
        x1 = ai_center_x + int(ai_radius * 0.7 * math.cos(angle))
        y1 = ai_center_y + int(ai_radius * 0.7 * math.sin(angle))
        x2 = ai_center_x + int(ai_radius * 0.3 * math.cos(angle + math.pi/6))
        y2 = ai_center_y + int(ai_radius * 0.3 * math.sin(angle + math.pi/6))
        draw.line([(ai_center_x, ai_center_y), (x1, y1)], fill=blue_color, width=3)
        draw.line([(x1, y1), (x2, y2)], fill=blue_color, width=2)
    
    # ЗАГОЛОВОК (смещен вниз как в других тарифах)
    title_font = get_font(64, bold=True)
    title_text = TITLES['premium'][language]
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_x = (CANVAS_SIZE - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 300  # Смещен вниз
    
    draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=(0, 0, 0, 128))
    draw.text((title_x, title_y), title_text, font=title_font, fill=gold_color)
    
    # ИЗЮМИНКА - 99% ЗАЩИТА (правый верхний угол, как в других тарифах)
    highlight_font = get_font(32, bold=True)
    highlight_text = HIGHLIGHTS['premium'][language]
    highlight_bbox = draw.textbbox((0, 0), highlight_text, font=highlight_font)
    highlight_width = highlight_bbox[2] - highlight_bbox[0]
    # Правый верхний угол с отступом
    highlight_x = CANVAS_SIZE - highlight_width - 40  # 40px отступ справа
    highlight_y = 50  # 50px отступ сверху
    
    # Тень
    draw.text((highlight_x + 2, highlight_y + 2), highlight_text, font=highlight_font, fill=(0, 0, 0, 128))
    # Текст
    draw.text((highlight_x, highlight_y), highlight_text, font=highlight_font, fill=blue_color)
    
    # ФУНКЦИИ - крупнее, распределены на всю высоту страницы (как в других тарифах)
    features_font = get_font(24)  # Немного меньше для большого количества функций
    feature_num_font = get_font(28, bold=True)
    features = FEATURES['premium'][language]
    
    # Отступы для текста (больше чтобы не заходили за края)
    padding_left = 80
    padding_right = 80
    padding_top = 380  # Отступ сверху (после заголовка)
    padding_bottom = 70  # Отступ снизу
    
    # Доступная высота для всех функций
    available_height = CANVAS_SIZE - padding_top - padding_bottom
    
    # Рассчитываем равномерное расстояние между функциями
    num_features = len(features)
    if num_features > 1:
        line_spacing = available_height / (num_features - 1)  # Равномерное распределение
    else:
        line_spacing = 50
    
    # Максимальная ширина текста
    max_text_width = CANVAS_SIZE - padding_left - padding_right
    x_start = padding_left
    
    # Рисуем все функции по порядку, распределенные на всю высоту
    for i, feature in enumerate(features):
        num = i + 1
        # Равномерное распределение по высоте
        if num_features == 1:
            y_pos = padding_top
        else:
            y_pos = int(padding_top + i * line_spacing)
        
        # Номер функции (золотой цвет, крупный)
        draw.text((x_start, y_pos), f"{num}.", font=feature_num_font, fill=gold_color)
        
        # Текст функции (белый цвет)
        text_start_x = x_start + 50  # Отступ от номера
        
        # Проверяем ширину текста
        feature_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        max_text_for_line = max_text_width - 50  # Минус место для номера
        
        # Если текст не влезает, уменьшаем шрифт или сокращаем
        if feature_width > max_text_for_line:
            # Пробуем уменьшить шрифт
            smaller_font = get_font(22)
            smaller_bbox = draw.textbbox((0, 0), feature, font=smaller_font)
            if smaller_bbox[2] - smaller_bbox[0] <= max_text_for_line:
                # Уменьшенный шрифт подходит
                draw.text((text_start_x, y_pos), feature, font=smaller_font, fill=(255, 255, 255))
            else:
                # Еще меньше
                smallest_font = get_font(20)
                smallest_bbox = draw.textbbox((0, 0), feature, font=smallest_font)
                if smallest_bbox[2] - smallest_bbox[0] <= max_text_for_line:
                    draw.text((text_start_x, y_pos), feature, font=smallest_font, fill=(255, 255, 255))
                else:
                    # Сокращаем текст
                    max_chars = int(max_text_for_line / 11)  # Примерно 11px на символ
                    shortened = feature[:max_chars-3] + "..."
                    draw.text((text_start_x, y_pos), shortened, font=smallest_font, fill=(255, 255, 255))
        else:
            # Текст влезает
            draw.text((text_start_x, y_pos), feature, font=features_font, fill=(255, 255, 255))
    
    # Защитное кольцо вокруг всего
    draw_protection_ring(draw, CANVAS_SIZE//2, CANVAS_SIZE//2, 450, accent_color, 16)
    
    # Рамка премиум (двойная)
    border_width = 8
    border_offset = 20
    draw.rectangle([border_offset, border_offset, CANVAS_SIZE-border_offset, CANVAS_SIZE-border_offset],
                  outline=main_color, width=border_width)
    inner_offset = 35
    draw.rectangle([inner_offset, inner_offset, CANVAS_SIZE-inner_offset, CANVAS_SIZE-inner_offset],
                  outline=gold_color, width=4)
    
    # VIP элементы - звезды
    for i in range(12):
        angle = i * 2 * math.pi / 12
        radius = 380
        x = int(CANVAS_SIZE//2 + radius * math.cos(angle))
        y = int(CANVAS_SIZE//2 + radius * math.sin(angle))
        draw.ellipse([x-10, y-10, x+10, y+10], outline=gold_color, width=2, fill=gold_color)
    
    return bg

def main():
    output_dir = os.path.join(os.path.dirname(__file__), 'tariff_images_1024x1024')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Генерация УНИКАЛЬНЫХ промо-изображений IAP...")
    print("✅ Цвета: золото-фиолетовый-синий (из главной страницы)")
    print("✅ Элементы: защита + AI")
    print("✅ Изюминка для каждого тарифа")
    print("✅ Текст распределен по всей странице")
    
    tariffs = ['individual', 'family', 'premium']
    languages = ['ru', 'en']
    
    for tariff in tariffs:
        for lang in languages:
            print(f"\n📝 Создание {tariff}_{lang}_1024x1024.png...")
            
            if tariff == 'individual':
                img = create_individual_image(lang)
            elif tariff == 'family':
                img = create_family_image(lang)
            else:  # premium
                img = create_premium_image(lang)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output_path = os.path.join(output_dir, f'{tariff}_{lang}_1024x1024.png')
            img.save(output_path, 'PNG', dpi=(DPI, DPI))
            print(f"   ✅ Готово: {img.size[0]}x{img.size[1]}px, DPI: {DPI}")
    
    print("\n🎉 Все изображения созданы успешно!")
    print(f"📂 Папка: {output_dir}")

if __name__ == '__main__':
    main()
