#!/bin/bash

# Скрипт для добавления ARIA labels во все HTML файлы

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Добавление ARIA labels...${NC}"

# Массив файлов для обработки
files=(
    "02_protection_screen.html"
    "03_family_screen.html"
    "04_analytics_screen.html"
    "05_settings_screen.html"
    "06_child_interface.html"
    "07_elderly_interface.html"
    "08_ai_assistant.html"
    "08_notifications_screen.html"
    "09_tariffs_screen.html"
    "10_info_screen.html"
    "11_profile_screen.html"
    "12_devices_screen.html"
    "13_referral_screen.html"
    "14_parental_control_screen.html"
    "15_device_detail_screen.html"
    "17_family_chat_screen.html"
)

count=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ Обрабатываем: $file${NC}"
        
        # 1. Заменяем <div class="back-btn"> на <button class="back-btn" aria-label="Назад">
        sed -i '' 's/<div class="back-btn">/<button class="back-btn" aria-label="Назад">/g' "$file"
        sed -i '' 's/<\/div><!--.*back-btn.*-->/<\/button>/g' "$file"
        
        # 2. Заменяем profile-btn
        sed -i '' 's/<div class="profile-btn"/<button class="profile-btn" aria-label="Открыть профиль"/g' "$file"
        
        # 3. Заменяем bottom-nav
        sed -i '' 's/<div class="bottom-nav">/<nav class="bottom-nav" role="navigation" aria-label="Основная навигация">/g' "$file"
        sed -i '' 's/<\/div><!--.*bottom-nav.*-->/<\/nav>/g' "$file"
        
        # 4. Заменяем nav-item на button с aria-label
        sed -i '' 's/<div class="nav-item active"/<button class="nav-item active" aria-current="page"/g' "$file"
        sed -i '' 's/<div class="nav-item"/<button class="nav-item"/g' "$file"
        
        # 5. Добавляем role="main" к main-content
        sed -i '' 's/<div class="main-content">/<div class="main-content" role="main">/g' "$file"
        
        ((count++))
    else
        echo -e "${YELLOW}⚠️  Файл не найден: $file${NC}"
    fi
done

echo -e "${GREEN}✅ Обработано файлов: $count${NC}"
echo -e "${GREEN}🎉 Готово!${NC}"


