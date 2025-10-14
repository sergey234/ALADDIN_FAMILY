#!/bin/bash

# Скрипт для добавления CSS стилей для button элементов

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🎨 Добавление CSS стилей для button...${NC}"

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

button_css="
        /* Button resets for accessibility */
        button.back-btn,
        button.profile-btn,
        button.nav-item,
        button.card {
            background: none;
            border: none;
            font-family: inherit;
            font-size: inherit;
            color: inherit;
            cursor: pointer;
        }
"

count=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # Ищем </style> и добавляем перед ним CSS
        if grep -q "</style>" "$file"; then
            # Создаем временный файл
            awk -v css="$button_css" '
                /<\/style>/ {
                    print css
                }
                { print }
            ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
            
            echo -e "${GREEN}✅ Добавлены стили в: $file${NC}"
            ((count++))
        else
            echo -e "${YELLOW}⚠️  Тег </style> не найден в: $file${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Файл не найден: $file${NC}"
    fi
done

echo -e "${GREEN}✅ Обработано файлов: $count${NC}"
echo -e "${GREEN}🎉 Готово!${NC}"


