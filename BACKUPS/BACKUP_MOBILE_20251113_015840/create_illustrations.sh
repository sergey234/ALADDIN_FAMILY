#!/bin/bash

# Создание иллюстраций
ILLUSTRATIONS=("onboarding_1" "onboarding_2" "onboarding_3" "empty_state" "error_state" "success_state")

for ill in "${ILLUSTRATIONS[@]}"; do
    echo "Создание изображений для $ill..."
    
    # Создание 1x
    sips -s format png -z 300 300 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$ill.imageset/illustration_1x.png
    
    # Создание 2x
    sips -s format png -z 600 600 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$ill.imageset/illustration_2x.png
    
    # Создание 3x
    sips -s format png -z 900 900 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$ill.imageset/illustration_3x.png
    
    echo "✅ $ill готов"
done

echo "🎉 Все иллюстрации созданы!"
