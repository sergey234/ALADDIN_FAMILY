#!/bin/bash

# Создание placeholder изображений для всех иконок
ICONS=("family_icon" "security_icon" "analytics_icon" "settings_icon" "profile_icon" "notification_icon" "support_icon" "rewards_icon" "games_icon")

for icon in "${ICONS[@]}"; do
    echo "Создание изображений для $icon..."
    
    # Создание 24x24
    sips -s format png -z 24 24 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_40.jpg --out Assets.xcassets/Images.xcassets/$icon.imageset/icon_24.png
    
    # Создание 48x48
    sips -s format png -z 48 48 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_40.jpg --out Assets.xcassets/Images.xcassets/$icon.imageset/icon_48.png
    
    # Создание 96x96
    sips -s format png -z 96 96 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_40.jpg --out Assets.xcassets/Images.xcassets/$icon.imageset/icon_96.png
    
    echo "✅ $icon готов"
done

echo "🎉 Все placeholder изображения созданы!"
