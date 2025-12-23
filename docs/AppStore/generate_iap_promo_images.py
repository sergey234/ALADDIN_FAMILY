#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор промо-изображений IAP для ALADDIN
Создает 6 изображений 1024x1024 согласно спецификациям
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import sys

# Размер холста
CANVAS_SIZE = 1024
# DPI согласно требованиям Apple
DPI = 72

# Функция для преобразования pt в px (при 72 DPI: 1pt = 1px)
# Но для читаемости делаем немного больше
def pt_to_px(pt):
    # При 72 DPI 1pt = 1px, но для большей читаемости умножаем на 1.33
    return int(pt * 1.33)  # Делаем текст чуть больше для читаемости

# Функция для hex в RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Функция для создания градиента
def create_gradient(size, color1, color2, direction='horizontal'):
    """Создает градиентное изображение"""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    if direction == 'horizontal':
        for x in range(size[0]):
            ratio = x / size[0]
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x, 0), (x, size[1])], fill=(r, g, b))
    else:  # diagonal
        for y in range(size[1]):
            for x in range(size[0]):
                ratio = (x + y) / (size[0] + size[1])
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                img.putpixel((x, y), (r, g, b))
    
    return img

# Функция для добавления тени текста
def draw_text_with_shadow(draw, position, text, font, fill, shadow_color, shadow_offset=(2, 2), shadow_blur=0):
    """Рисует текст с тенью"""
    x, y = position
    
    # Упрощенная тень (без альфа канала, просто черный)
    if isinstance(shadow_color, tuple) and len(shadow_color) == 4:
        shadow_rgb = shadow_color[:3]
    else:
        shadow_rgb = (0, 0, 0) if shadow_color == (0, 0, 0) or shadow_color == (0, 0, 0, 102) else shadow_color
    
    # Простая тень (1-2 смещения)
    if shadow_blur > 0:
        for i in range(shadow_blur):
            offset = (shadow_offset[0] + i, shadow_offset[1] + i)
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_rgb)
    elif shadow_offset != (0, 0):
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_rgb)
    
    # Основной текст
    draw.text(position, text, font=font, fill=fill)

# Функция для создания премиум эффектов
def add_premium_effects(img, color):
    """Добавляет премиум эффекты (блестящие частицы)"""
    draw = ImageDraw.Draw(img)
    import random
    
    # Блестящие частицы
    for _ in range(30):
        x = random.randint(0, CANVAS_SIZE)
        y = random.randint(0, CANVAS_SIZE)
        size = random.randint(2, 8)
        opacity = random.randint(100, 200)
        color_with_opacity = color + (opacity,)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=color_with_opacity)
    
    return img

# INDIVIDUAL - Премиальный с золотом
def create_individual_ru():
    """Создает individual_ru_1024x1024.png"""
    # Фон
    bg_color = hex_to_rgb('#1D1D1F')
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Цвета
    gold = hex_to_rgb('#FFD700')
    white = (255, 255, 255)
    gold_light = hex_to_rgb('#FFED4E')
    
    # Попытка загрузить шрифт, иначе использовать стандартный
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(60))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(28))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(24))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Иконка щита (упрощенная - прямоугольник с закругленными углами)
    shield_size = 120
    shield_x = (CANVAS_SIZE - shield_size) // 2
    shield_y = 80
    
    # Рисуем щит
    draw.rectangle([shield_x, shield_y, shield_x + shield_size, shield_y + shield_size], 
                   outline=gold, width=4, fill=(0, 0, 0, 0))
    
    # Буква A в щите
    try:
        shield_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(60))
        text_bbox = draw.textbbox((0, 0), "A", font=shield_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((shield_x + (shield_size - text_width) // 2, 
                  shield_y + (shield_size - text_height) // 2), 
                  "A", font=shield_font, fill=gold)
    except:
        draw.text((shield_x + 50, shield_y + 40), "A", font=title_font, fill=gold)
    
    # Заголовок "ALADDIN ЛИЧНЫЙ"
    title_text = "ALADDIN ЛИЧНЫЙ"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = text_bbox[2] - text_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    title_y = 180
    
    # Тень и текст
    draw_text_with_shadow(draw, (title_x, title_y), title_text, title_font, gold, 
                         (0, 0, 0, 102), shadow_offset=(0, 2), shadow_blur=4)
    
    # Подзаголовок
    subtitle_text = "Персональная защита\nнового уровня"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    subtitle_y = 280
    
    draw_text_with_shadow(draw, (subtitle_x, subtitle_y), subtitle_text, subtitle_font, white,
                         (0, 0, 0, 64), shadow_offset=(0, 1))
    
    # Декоративная рамка (880x880, отступ 72px)
    frame_size = 880
    frame_offset = 72
    frame_color = gold
    frame_width = 4
    
    # Внешняя рамка
    draw.rectangle([frame_offset, frame_offset, 
                   frame_offset + frame_size, frame_offset + frame_size],
                  outline=frame_color, width=frame_width)
    
    # Внутренняя рамка
    inner_offset = 16
    draw.rectangle([frame_offset + inner_offset, frame_offset + inner_offset,
                   frame_offset + frame_size - inner_offset, frame_offset + frame_size - inner_offset],
                  outline=frame_color, width=2)
    
    # Функции внутри рамки
    features_text = "• 3 устройства • AI • Аналитика"
    text_bbox = draw.textbbox((0, 0), features_text, font=features_font)
    features_width = text_bbox[2] - text_bbox[0]
    features_x = (CANVAS_SIZE - features_width) // 2
    features_y = 420
    
    draw_text_with_shadow(draw, (features_x, features_y), features_text, features_font, gold,
                         (0, 0, 0, 51), shadow_offset=(0, 1))
    
    # Премиум эффекты
    img = add_premium_effects(img.convert('RGBA'), gold).convert('RGB')
    
    return img

def create_individual_en():
    """Создает individual_en_1024x1024.png"""
    img = create_individual_ru()
    draw = ImageDraw.Draw(img)
    
    gold = hex_to_rgb('#FFD700')
    white = (255, 255, 255)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(58))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(26))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(24))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Заголовок "ALADDIN INDIVIDUAL"
    title_text = "ALADDIN INDIVIDUAL"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = text_bbox[2] - text_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    title_y = 180
    
    # Закрашиваем старый текст
    draw.rectangle([0, 180, CANVAS_SIZE, 280], fill=hex_to_rgb('#1D1D1F'))
    
    draw_text_with_shadow(draw, (title_x, title_y), title_text, title_font, gold,
                         (0, 0, 0, 102), shadow_offset=(0, 2), shadow_blur=4)
    
    # Подзаголовок
    subtitle_text = "Personal Protection\nof New Level"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    subtitle_y = 280
    
    draw_text_with_shadow(draw, (subtitle_x, subtitle_y), subtitle_text, subtitle_font, white,
                         (0, 0, 0, 64), shadow_offset=(0, 1))
    
    # Функции
    features_text = "• 3 devices • AI • Analytics"
    text_bbox = draw.textbbox((0, 0), features_text, font=features_font)
    features_width = text_bbox[2] - text_bbox[0]
    features_x = (CANVAS_SIZE - features_width) // 2
    
    draw.rectangle([0, 420, CANVAS_SIZE, 460], fill=hex_to_rgb('#1D1D1F'))
    draw_text_with_shadow(draw, (features_x, 420), features_text, features_font, gold,
                         (0, 0, 0, 51), shadow_offset=(0, 1))
    
    return img

# FAMILY - Яркий градиент
def create_family_ru():
    """Создает family_ru_1024x1024.png"""
    # Градиентный фон
    color1 = hex_to_rgb('#7B2CBF')  # Фиолетовый
    color2 = hex_to_rgb('#5856D6')  # Индиго
    color3 = hex_to_rgb('#007AFF')  # Синий
    
    # Создаем градиент
    img = create_gradient((CANVAS_SIZE, CANVAS_SIZE), color1, color3, 'diagonal')
    
    # Добавляем промежуточный цвет
    overlay = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), color2)
    overlay = overlay.convert('RGBA')
    overlay.putalpha(128)  # 50% прозрачность
    img = Image.blend(img.convert('RGBA'), overlay, 0.3).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    white = (255, 255, 255)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(62))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(34))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(28))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Иллюстрация семьи (упрощенная - иконка)
    family_size = 220
    family_x = (CANVAS_SIZE - family_size) // 2
    family_y = 280
    
    # Рисуем упрощенную иконку семьи (круги для людей)
    # Взрослый 1
    draw.ellipse([family_x + 40, family_y + 60, family_x + 80, family_y + 100], fill=white)
    draw.rectangle([family_x + 50, family_y + 100, family_x + 70, family_y + 160], fill=white)
    # Взрослый 2
    draw.ellipse([family_x + 140, family_y + 60, family_x + 180, family_y + 100], fill=white)
    draw.rectangle([family_x + 150, family_y + 100, family_x + 170, family_y + 160], fill=white)
    # Дети (2 маленьких круга)
    draw.ellipse([family_x + 70, family_y + 120, family_x + 95, family_y + 145], fill=white)
    draw.ellipse([family_x + 125, family_y + 120, family_x + 150, family_y + 145], fill=white)
    
    # Заголовок "СЕМЕЙНЫЙ"
    title_text = "СЕМЕЙНЫЙ"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = text_bbox[2] - text_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    title_y = 200
    
    draw_text_with_shadow(draw, (title_x, title_y), title_text, title_font, white,
                         (0, 0, 0, 77), shadow_offset=(0, 4), shadow_blur=6)
    
    # Подзаголовок
    subtitle_text = "FAMILY PLAN"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    subtitle_y = 300
    
    draw_text_with_shadow(draw, (subtitle_x, subtitle_y), subtitle_text, subtitle_font, white,
                         (0, 0, 0, 64), shadow_offset=(0, 2))
    
    # Рамка с функциями
    frame_width_img = 800
    frame_height_img = 180
    frame_x = (CANVAS_SIZE - frame_width_img) // 2
    frame_y = 440
    
    # Полупрозрачный фон рамки
    frame_bg = Image.new('RGBA', (frame_width_img, frame_height_img), (255, 255, 255, 38))
    img.paste(frame_bg, (frame_x, frame_y), frame_bg)
    
    # Обводка рамки
    draw.rectangle([frame_x, frame_y, frame_x + frame_width_img, frame_y + frame_height_img],
                  outline=white, width=2)
    
    # Функции в рамке
    features = [
        "✓ До 5 устройств",
        "✓ Управление семьей",
        "✓ Родительский контроль",
        "✓ Полная защита семьи"
    ]
    
    features_y = frame_y + 30
    for i, feature in enumerate(features):
        text_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = text_bbox[2] - text_bbox[0]
        feature_x = (CANVAS_SIZE - feature_width) // 2
        draw.text((feature_x, features_y + i * 35), feature, font=features_font, fill=white)
    
    return img

def create_family_en():
    """Создает family_en_1024x1024.png"""
    img = create_family_ru()
    draw = ImageDraw.Draw(img)
    
    white = (255, 255, 255)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(65))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(32))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(28))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Заголовок "FAMILY"
    title_text = "FAMILY"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = text_bbox[2] - text_bbox[0]
    title_x = (CANVAS_SIZE - title_width) // 2
    
    # Закрашиваем старый текст
    draw.rectangle([0, 200, CANVAS_SIZE, 270], fill=hex_to_rgb('#7B2CBF'))
    
    draw_text_with_shadow(draw, (title_x, 200), title_text, title_font, white,
                         (0, 0, 0, 77), shadow_offset=(0, 4), shadow_blur=6)
    
    # Подзаголовок
    subtitle_text = "Family Protection Plan"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    
    draw.rectangle([0, 300, CANVAS_SIZE, 350], fill=hex_to_rgb('#5856D6'))
    draw_text_with_shadow(draw, (subtitle_x, 300), subtitle_text, subtitle_font, white,
                         (0, 0, 0, 64), shadow_offset=(0, 2))
    
    # Функции
    features = [
        "✓ Up to 5 devices",
        "✓ Family management",
        "✓ Parental control",
        "✓ Complete family protection"
    ]
    
    frame_y = 440
    for i, feature in enumerate(features):
        text_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = text_bbox[2] - text_bbox[0]
        feature_x = (CANVAS_SIZE - feature_width) // 2
        draw.rectangle([0, frame_y + 30 + i * 35, CANVAS_SIZE, frame_y + 30 + i * 35 + 35],
                      fill=(123, 44, 191, 38))
        draw.text((feature_x, frame_y + 30 + i * 35), feature, font=features_font, fill=white)
    
    return img

# PREMIUM - VIP с короной
def create_premium_ru():
    """Создает premium_ru_1024x1024.png"""
    # Темный фон
    bg_color = hex_to_rgb('#0A0A0A')
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Цвета
    platinum = hex_to_rgb('#E5E4E2')
    gold = hex_to_rgb('#FFD700')
    gold_light = hex_to_rgb('#FFED4E')
    
    try:
        title_font1 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(54))
        title_font2 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(56))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(28))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(26))
    except:
        title_font1 = ImageFont.load_default()
        title_font2 = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Корона (упрощенная)
    crown_size = 140
    crown_x = (CANVAS_SIZE - crown_size) // 2
    crown_y = 100
    
    # Рисуем упрощенную корону (треугольники)
    # Основа короны
    draw.rectangle([crown_x + 20, crown_y + 80, crown_x + crown_size - 20, crown_y + 100], fill=gold)
    # Зубцы (5 треугольников)
    for i in range(5):
        x1 = crown_x + 20 + i * 20
        x2 = x1 + 10
        x3 = x1 + 20
        y1 = crown_y + 80
        y2 = crown_y + 60
        draw.polygon([(x1, y1), (x2, y2), (x3, y1)], fill=gold_light)
    
    # Заголовок "ALADDIN" (платина)
    title1_text = "ALADDIN"
    text_bbox = draw.textbbox((0, 0), title1_text, font=title_font1)
    title1_width = text_bbox[2] - text_bbox[0]
    title1_x = (CANVAS_SIZE - title1_width) // 2
    title1_y = 200
    
    draw_text_with_shadow(draw, (title1_x, title1_y), title1_text, title_font1, platinum,
                         (0, 0, 0, 128), shadow_offset=(0, 2), shadow_blur=5)
    
    # Заголовок "ПРЕМИУМ" (золотой)
    title2_text = "ПРЕМИУМ"
    text_bbox = draw.textbbox((0, 0), title2_text, font=title_font2)
    title2_width = text_bbox[2] - text_bbox[0]
    title2_x = (CANVAS_SIZE - title2_width) // 2
    title2_y = 280
    
    draw_text_with_shadow(draw, (title2_x, title2_y), title2_text, title_font2, gold,
                         (255, 215, 0, 102), shadow_offset=(0, 2), shadow_blur=6)
    
    # Подзаголовок
    subtitle_text = "Эксклюзивная защита для избранных"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    subtitle_y = 360
    
    draw_text_with_shadow(draw, (subtitle_x, subtitle_y), subtitle_text, subtitle_font, gold,
                         (0, 0, 0, 102), shadow_offset=(0, 1))
    
    # Декоративная линия
    line_length = 700
    line_x = (CANVAS_SIZE - line_length) // 2
    line_y = 420
    draw.line([(line_x, line_y), (line_x + line_length, line_y)], fill=gold, width=2)
    
    # Роскошная рамка (900x900, отступ 62px)
    frame_size = 900
    frame_offset = 62
    frame_width = 6
    
    # Внешняя рамка
    draw.rectangle([frame_offset, frame_offset,
                   frame_offset + frame_size, frame_offset + frame_size],
                  outline=gold, width=frame_width)
    
    # Функции
    features = [
        "• 10 устройств",
        "• Все функции премиум",
        "• AI+ с обучением",
        "• 99% защита • Zero-day"
    ]
    
    features_y = 480
    for i, feature in enumerate(features):
        text_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = text_bbox[2] - text_bbox[0]
        feature_x = (CANVAS_SIZE - feature_width) // 2
        draw_text_with_shadow(draw, (feature_x, features_y + i * 35), feature, features_font, platinum,
                             (0, 0, 0, 102), shadow_offset=(0, 1))
    
    # VIP элементы (звезды)
    import random
    for _ in range(12):
        x = random.randint(0, CANVAS_SIZE)
        y = random.randint(0, CANVAS_SIZE)
        size = random.randint(10, 20)
        # Простая звезда (круг)
        draw.ellipse([x-size, y-size, x+size, y+size], outline=gold, width=2)
    
    # Эмблема VIP (внизу)
    vip_size = 100
    vip_x = (CANVAS_SIZE - vip_size) // 2
    vip_y = 844
    draw.rectangle([vip_x, vip_y, vip_x + vip_size, vip_y + vip_size], outline=gold, width=3)
    
    try:
        vip_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(40))
        text_bbox = draw.textbbox((0, 0), "VIP", font=vip_font)
        vip_text_width = text_bbox[2] - text_bbox[0]
        vip_text_x = vip_x + (vip_size - vip_text_width) // 2
        vip_text_y = vip_y + (vip_size - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((vip_text_x, vip_text_y), "VIP", font=vip_font, fill=gold)
    except:
        draw.text((vip_x + 30, vip_y + 30), "VIP", font=features_font, fill=gold)
    
    return img

def create_premium_en():
    """Создает premium_en_1024x1024.png"""
    img = create_premium_ru()
    draw = ImageDraw.Draw(img)
    
    platinum = hex_to_rgb('#E5E4E2')
    gold = hex_to_rgb('#FFD700')
    
    try:
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(26))
        features_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", pt_to_px(26))
    except:
        subtitle_font = ImageFont.load_default()
        features_font = ImageFont.load_default()
    
    # Подзаголовок
    subtitle_text = "Exclusive Protection for the Chosen"
    text_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = text_bbox[2] - text_bbox[0]
    subtitle_x = (CANVAS_SIZE - subtitle_width) // 2
    
    draw.rectangle([0, 360, CANVAS_SIZE, 410], fill=hex_to_rgb('#0A0A0A'))
    draw_text_with_shadow(draw, (subtitle_x, 360), subtitle_text, subtitle_font, gold,
                         (0, 0, 0, 102), shadow_offset=(0, 1))
    
    # Функции
    features = [
        "• 10 devices",
        "• All premium functions",
        "• AI+ with learning",
        "• 99% protection • Zero-day"
    ]
    
    features_y = 480
    for i, feature in enumerate(features):
        text_bbox = draw.textbbox((0, 0), feature, font=features_font)
        feature_width = text_bbox[2] - text_bbox[0]
        feature_x = (CANVAS_SIZE - feature_width) // 2
        draw.rectangle([0, features_y + i * 35, CANVAS_SIZE, features_y + i * 35 + 35],
                      fill=hex_to_rgb('#0A0A0A'))
        draw_text_with_shadow(draw, (feature_x, features_y + i * 35), feature, features_font, platinum,
                             (0, 0, 0, 102), shadow_offset=(0, 1))
    
    return img

# Главная функция
def main():
    """Генерирует все изображения"""
    output_dir = os.path.join(os.path.dirname(__file__), 'tariff_images_1024x1024')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Генерация промо-изображений IAP...")
    
    # INDIVIDUAL
    # Функция для сохранения с правильным DPI
    def save_with_dpi(img, path):
        """Сохраняет изображение с DPI=72 согласно требованиям Apple"""
        # Убеждаемся что RGB (без альфа канала)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Сохраняем с DPI=72
        img.save(path, 'PNG', dpi=(DPI, DPI))
    
    print("📝 Создание individual_ru_1024x1024.png...")
    img = create_individual_ru()
    save_with_dpi(img, os.path.join(output_dir, 'individual_ru_1024x1024.png'))
    print("✅ Готово!")
    
    print("📝 Создание individual_en_1024x1024.png...")
    img = create_individual_en()
    save_with_dpi(img, os.path.join(output_dir, 'individual_en_1024x1024.png'))
    print("✅ Готово!")
    
    # FAMILY
    print("📝 Создание family_ru_1024x1024.png...")
    img = create_family_ru()
    save_with_dpi(img, os.path.join(output_dir, 'family_ru_1024x1024.png'))
    print("✅ Готово!")
    
    print("📝 Создание family_en_1024x1024.png...")
    img = create_family_en()
    save_with_dpi(img, os.path.join(output_dir, 'family_en_1024x1024.png'))
    print("✅ Готово!")
    
    # PREMIUM
    print("📝 Создание premium_ru_1024x1024.png...")
    img = create_premium_ru()
    save_with_dpi(img, os.path.join(output_dir, 'premium_ru_1024x1024.png'))
    print("✅ Готово!")
    
    print("📝 Создание premium_en_1024x1024.png...")
    img = create_premium_en()
    save_with_dpi(img, os.path.join(output_dir, 'premium_en_1024x1024.png'))
    print("✅ Готово!")
    
    print("\n🎉 Все изображения созданы успешно!")
    print(f"📂 Папка: {output_dir}")
    print("\n✅ Файлы:")
    print("  - individual_ru_1024x1024.png")
    print("  - individual_en_1024x1024.png")
    print("  - family_ru_1024x1024.png")
    print("  - family_en_1024x1024.png")
    print("  - premium_ru_1024x1024.png")
    print("  - premium_en_1024x1024.png")

if __name__ == '__main__':
    main()
