#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания изображений 1024x1024 для тарифов
Использование: python3 create_tariff_images.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Цвета для каждого тарифа
TARIFF_COLORS = {
    'free': {
        'bg': (30, 30, 40),  # Темно-серый
        'accent': (150, 150, 150),  # Серый
        'text': (255, 255, 255)  # Белый
    },
    'personal': {
        'bg': (20, 40, 80),  # Темно-синий
        'accent': (0, 122, 255),  # Синий iOS
        'text': (255, 255, 255)
    },
    'family': {
        'bg': (40, 30, 20),  # Темно-коричневый
        'accent': (255, 193, 7),  # Золотой
        'text': (255, 255, 255)
    },
    'premium': {
        'bg': (40, 20, 60),  # Темно-фиолетовый
        'accent': (168, 85, 247),  # Фиолетовый (#A855F7)
        'text': (255, 255, 255)
    }
}

# Функции для каждого тарифа (топ-10)
TARIFF_FEATURES = {
    'free': {
        'ru': [
            'Защита от вирусов и троянов',
            'Блокировка фишинговых сайтов',
            'Блокировка вредоносных ссылок',
            'Защита от шпионского ПО',
            'Блокировка поддельных приложений',
            'Блокировка опасных сайтов',
            'Защита от майнеров',
            'Защита от руткитов',
            'Блокировка приложений',
            'История и мониторинг'
        ],
        'en': [
            'Virus and Trojan Protection',
            'Phishing Site Blocking',
            'Malicious Link Blocking',
            'Spyware Protection',
            'Fake App Blocking',
            'Dangerous Site Blocking',
            'Miner Protection',
            'Rootkit Protection',
            'App Blocking',
            'History and Monitoring'
        ]
    },
    'personal': {
        'ru': [
            'Все функции FREE тарифа',
            'Расширенная защита от угроз',
            'AI-помощник безопасности',
            'Расширенная аналитика угроз',
            'Защита от социальной инженерии',
            'Блокировка рекламы и трекеров',
            'Защита от утечки данных',
            'Образовательный контент',
            'Приоритетная поддержка',
            'Расширенная база угроз'
        ],
        'en': [
            'All FREE tier features',
            'Advanced Threat Protection',
            'AI Security Assistant',
            'Advanced Threat Analytics',
            'Social Engineering Protection',
            'Ad and Tracker Blocking',
            'Data Leak Protection',
            'Educational Content',
            'Priority Support',
            'Extended Threat Database'
        ]
    },
    'family': {
        'ru': [
            'Все функции Personal тарифа',
            'Родительский контроль',
            'Защита до 5 устройств',
            'Блокировка опасных приложений',
            'Контроль времени использования',
            'Блокировка онлайн-казино',
            'Мониторинг активности детей',
            'Геозона и безопасные места',
            'Семейная группа через QR-код',
            'Образовательные игры'
        ],
        'en': [
            'All Personal tier features',
            'Parental Controls',
            'Protection for up to 5 devices',
            'Dangerous App Blocking',
            'Screen Time Control',
            'Online Casino Blocking',
            'Children Activity Monitoring',
            'Geofencing and Safe Places',
            'Family Group via QR Code',
            'Educational Security Games'
        ]
    },
    'premium': {
        'ru': [
            'Все функции Family тарифа',
            'Защита до 10 устройств',
            'Приоритетная поддержка 24/7',
            'Эксклюзивные функции безопасности',
            'Расширенная защита от фейков',
            'Максимальная база угроз',
            'Детальная аналитика и отчеты',
            'Защита от продвинутых атак',
            'Корпоративные функции',
            'Эксклюзивный контент'
        ],
        'en': [
            'All Family tier features',
            'Protection for up to 10 devices',
            '24/7 Priority Support',
            'Exclusive Security Features',
            'Extended Fake Protection',
            'Maximum Threat Database',
            'Detailed Analytics and Reports',
            'Advanced Attack Protection',
            'Enterprise Features',
            'Exclusive Content and Updates'
        ]
    }
}

# Названия тарифов
TARIFF_NAMES = {
    'free': {'ru': 'FREE', 'en': 'FREE'},
    'personal': {'ru': 'PERSONAL', 'en': 'PERSONAL'},
    'family': {'ru': 'FAMILY', 'en': 'FAMILY'},
    'premium': {'ru': 'PREMIUM', 'en': 'PREMIUM'}
}


def create_tariff_image(tariff_type, language='ru'):
    """Создать изображение для тарифа"""
    size = (1024, 1024)
    colors = TARIFF_COLORS[tariff_type]
    features = TARIFF_FEATURES[tariff_type][language]
    name = TARIFF_NAMES[tariff_type][language]
    
    # Создать изображение
    img = Image.new('RGB', size, colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # Попытаться загрузить шрифт (используем системные шрифты)
    try:
        # Для macOS
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 72)
        feature_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
    except:
        try:
            # Альтернативный путь
            title_font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 72)
            feature_font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 32)
        except:
            # Базовый шрифт
            title_font = ImageFont.load_default()
            feature_font = ImageFont.load_default()
    
    # Рисуем заголовок
    title_y = 80
    title_text = f"ALADDIN {name}"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_x = (size[0] - title_width) // 2
    draw.text((title_x, title_y), title_text, fill=colors['accent'], font=title_font)
    
    # Рисуем подзаголовок
    subtitle_y = title_y + 100
    subtitle_text = "Защита от 100 видов угроз" if language == 'ru' else "Protection from 100 types of threats"
    bbox = draw.textbbox((0, 0), subtitle_text, font=feature_font)
    subtitle_width = bbox[2] - bbox[0]
    subtitle_x = (size[0] - subtitle_width) // 2
    draw.text((subtitle_x, subtitle_y), subtitle_text, fill=colors['text'], font=feature_font)
    
    # Рисуем функции
    start_y = subtitle_y + 80
    line_height = 50
    feature_x = 100
    
    for i, feature in enumerate(features[:10]):  # Топ-10
        y = start_y + i * line_height
        # Рисуем маркер
        marker_size = 12
        marker_x = feature_x - 30
        marker_y = y + 10
        draw.ellipse(
            [marker_x - marker_size//2, marker_y - marker_size//2,
             marker_x + marker_size//2, marker_y + marker_size//2],
            fill=colors['accent']
        )
        # Рисуем текст функции
        draw.text((feature_x, y), feature, fill=colors['text'], font=feature_font)
    
    # Рисуем нижнюю линию с акцентом
    line_y = size[1] - 60
    draw.rectangle([0, line_y, size[0], line_y + 4], fill=colors['accent'])
    
    return img


def main():
    """Главная функция"""
    # Создать папку для изображений
    output_dir = 'tariff_images_1024x1024'
    os.makedirs(output_dir, exist_ok=True)
    
    # Создать изображения для всех тарифов
    for tariff_type in ['free', 'personal', 'family', 'premium']:
        for language in ['ru', 'en']:
            print(f"Создаю изображение: {tariff_type} ({language})...")
            img = create_tariff_image(tariff_type, language)
            filename = f"{output_dir}/{tariff_type}_{language}_1024x1024.png"
            img.save(filename, 'PNG')
            print(f"✅ Сохранено: {filename}")
    
    print(f"\n✅ Все изображения созданы в папке: {output_dir}/")
    print("📁 Файлы:")
    for tariff_type in ['free', 'personal', 'family', 'premium']:
        for language in ['ru', 'en']:
            filename = f"{tariff_type}_{language}_1024x1024.png"
            print(f"   - {filename}")


if __name__ == '__main__':
    main()
