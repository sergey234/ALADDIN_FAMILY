#!/usr/bin/env python3
"""
Генератор скриншотов для приложения ALADDIN
Создает изображения интерфейса для демонстрации
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_screenshot(title, description, features, filename):
    """Создает скриншот экрана приложения"""
    
    # Размеры iPhone 14 Pro
    width, height = 393, 852
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Статус бар
    draw.rectangle([(0, 0), (width, 44)], fill='#000000')
    draw.text((20, 15), "9:41", fill='white', font_size=16)
    draw.text((width//2 - 30, 15), "ALADDIN", fill='white', font_size=16)
    draw.text((width - 50, 15), "100%", fill='white', font_size=16)
    
    # Заголовок приложения
    header_height = 60
    draw.rectangle([(0, 44), (width, 44 + header_height)], 
                   fill='linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    draw.text((width//2 - 80, 44 + 20), title, fill='white', font_size=20)
    
    # Контент
    content_y = 44 + header_height + 20
    content_width = width - 40
    
    # Заголовок экрана
    draw.text((20, content_y), title, fill='#333333', font_size=24)
    
    # Описание
    desc_y = content_y + 40
    wrapped_desc = textwrap.fill(description, width=40)
    draw.text((20, desc_y), wrapped_desc, fill='#666666', font_size=14)
    
    # Функции
    if features:
        features_y = desc_y + 80
        draw.text((20, features_y), "Основные функции:", fill='#333333', font_size=16)
        
        for i, feature in enumerate(features):
            feature_y = features_y + 30 + (i * 25)
            draw.text((20, feature_y), f"• {feature}", fill='#444444', font_size=14)
    
    # Сохраняем
    img.save(filename)
    print(f"✅ Создан скриншот: {filename}")

def main():
    """Создает все скриншоты приложения"""
    
    print("📸 Создание скриншотов ALADDIN...")
    
    # Создаем папку для скриншотов
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Экран приветствия
    create_screenshot(
        "Добро пожаловать!",
        "AI система безопасности для всей семьи. Защитите своих близких с помощью передовых технологий искусственного интеллекта.",
        [
            "Семейная защита 24/7",
            "AI ассистент безопасности", 
            "VPN и шифрование",
            "Родительский контроль"
        ],
        f"{screenshots_dir}/01_welcome_screen.png"
    )
    
    # Главный экран
    create_screenshot(
        "Главная панель",
        "Управление всеми функциями безопасности из одного места. Мониторинг в реальном времени.",
        [
            "Статус защиты: 95%",
            "Активные угрозы: 0",
            "Защищенных устройств: 4",
            "Последняя проверка: сейчас"
        ],
        f"{screenshots_dir}/02_main_dashboard.png"
    )
    
    # Семейный экран
    create_screenshot(
        "Семейная защита",
        "Управление профилями всех членов семьи. Персонализированная защита для каждого возраста.",
        [
            "Профили детей и взрослых",
            "Возрастные ограничения",
            "Персональные настройки",
            "История активности"
        ],
        f"{screenshots_dir}/03_family_protection.png"
    )
    
    # AI Ассистент
    create_screenshot(
        "AI Ассистент",
        "Умный помощник, который анализирует угрозы и дает рекомендации по безопасности.",
        [
            "Анализ угроз в реальном времени",
            "Персональные рекомендации",
            "Автоматические действия",
            "Обучение на ваших предпочтениях"
        ],
        f"{screenshots_dir}/04_ai_assistant.png"
    )
    
    # VPN экран
    create_screenshot(
        "VPN Защита",
        "Безопасное подключение к интернету с шифрованием всех данных.",
        [
            "Шифрование трафика",
            "Защита в публичных сетях",
            "Обход блокировок",
            "Статистика использования"
        ],
        f"{screenshots_dir}/05_vpn_protection.png"
    )
    
    # Родительский контроль
    create_screenshot(
        "Родительский контроль",
        "Контроль времени использования устройств и доступа к контенту.",
        [
            "Ограничение времени экрана",
            "Фильтрация контента",
            "Блокировка приложений",
            "Мониторинг активности"
        ],
        f"{screenshots_dir}/06_parental_control.png"
    )
    
    print(f"\n🎉 Все скриншоты созданы в папке: {screenshots_dir}/")
    print("📱 Готово для публикации в App Store!")

if __name__ == "__main__":
    main()
