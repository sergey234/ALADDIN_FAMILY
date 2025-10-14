#!/bin/bash

# Исправление закрывающих тегов </div> на </button> для nav-item

GREEN='\033[0;32m'
NC='\033[0m'

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
    "15_device_detail_screen.html"
    "17_family_chat_screen.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ Исправляем: $file${NC}"
        
        # Используем perl для многострочной замены
        perl -i -pe 'BEGIN{undef $/;} s|<button class="nav-item"[^>]*>\s*<div class="nav-icon">([^<]+)</div>\s*<div class="nav-label">([^<]+)</div>\s*</div>|<button class="nav-item" onclick="window.location.href='\''01_main_screen.html'\''" aria-label="$2">\n                    <div class="nav-icon">$1</div>\n                    <div class="nav-label">$2</div>\n                </button>|g' "$file"
    fi
done

echo -e "${GREEN}🎉 Готово!${NC}"
