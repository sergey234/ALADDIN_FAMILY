#!/bin/bash

# Создание фоновых изображений
BACKGROUNDS=("background_gradient" "card_background" "modal_background" "splash_screen")

for bg in "${BACKGROUNDS[@]}"; do
    echo "Создание изображений для $bg..."
    
    # Создание 1x
    sips -s format png -z 375 812 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$bg.imageset/gradient_1x.png
    
    # Создание 2x
    sips -s format png -z 750 1624 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$bg.imageset/gradient_2x.png
    
    # Создание 3x
    sips -s format png -z 1125 2436 Assets.xcassets/AppIcon.appiconset/ALADDIN_icon_1024.jpg --out Assets.xcassets/Images.xcassets/$bg.imageset/gradient_3x.png
    
    echo "✅ $bg готов"
done

echo "🎉 Все фоновые изображения созданы!"
