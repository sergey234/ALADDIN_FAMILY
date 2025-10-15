#!/usr/bin/env python3
"""
Безопасное обновление Xcode проекта - добавление важных файлов с правильной структурой
"""

import os
import re

def generate_xcode_id():
    """Генерирует следующий ID для Xcode проекта"""
    import time
    # Используем timestamp + случайность для уникальности
    timestamp = int(time.time() * 1000000) % 0xFFFFFF
    return f"A1{timestamp:06X}"

def get_next_id():
    """Получает следующий доступный ID"""
    # Читаем проект и находим максимальный ID
    with open('ALADDIN.xcodeproj/project.pbxproj', 'r') as f:
        content = f.read()
    
    # Ищем все существующие ID
    ids = re.findall(r'\t\t(A1[0-9A-F]{6})', content)
    if not ids:
        return "A1000100"  # Начинаем с безопасного номера
    
    # Находим максимальный и увеличиваем
    max_id = max(ids)
    next_num = int(max_id[3:], 16) + 1
    return f"A1{next_num:06X}"

def add_essential_files():
    """Добавляет только самые важные файлы безопасным способом"""
    
    # Список критически важных файлов для добавления
    essential_files = [
        ("Screens/01_MainScreen.swift", "01_MainScreen.swift"),
        ("Core/Config/AppConfig.swift", "AppConfig.swift"), 
        ("Core/Network/NetworkManager.swift", "NetworkManager.swift"),
        ("ViewModels/MainViewModel.swift", "MainViewModel.swift"),
        ("Shared/Styles/Colors.swift", "Colors.swift"),
        ("Shared/Styles/Fonts.swift", "Fonts.swift")
    ]
    
    print("🔧 Безопасное добавление критически важных файлов...")
    
    # Читаем текущий проект
    with open('ALADDIN.xcodeproj/project.pbxproj', 'r') as f:
        content = f.read()
    
    # Проверяем, какие файлы уже есть
    existing_files = set()
    for match in re.finditer(r'/\* (\w+\.swift) \*/', content):
        existing_files.add(match.group(1))
    
    print(f"📊 Уже в проекте: {len(existing_files)} файлов")
    
    # Добавляем только новые файлы
    new_files = []
    for file_path, file_name in essential_files:
        if file_name not in existing_files and os.path.exists(f"ALADDIN/{file_path}"):
            new_files.append((file_path, file_name))
            print(f"✅ Добавим: {file_name}")
        else:
            print(f"⚠️ Пропускаем: {file_name} (уже есть или файл отсутствует)")
    
    if not new_files:
        print("🎉 Все важные файлы уже добавлены!")
        return True
    
    print(f"📝 Добавляем {len(new_files)} новых файлов...")
    
    # НЕ изменяем project.pbxproj напрямую - это может его сломать
    # Вместо этого создаем инструкции для пользователя
    print("\n🚨 ВАЖНО: Для безопасного добавления файлов в Xcode проект:")
    print("1. Откройте ALADDIN.xcodeproj в Xcode")
    print("2. Перетащите следующие папки в Navigator проекта:")
    for file_path, file_name in new_files:
        print(f"   - ALADDIN/{os.path.dirname(file_path)}/ ➡️ {file_name}")
    print("3. Убедитесь что все файлы добавлены в target 'ALADDIN'")
    
    return True

if __name__ == "__main__":
    add_essential_files()
