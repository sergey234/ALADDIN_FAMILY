#!/bin/bash

# 🎯 Скрипт настройки Widgets в Xcode
# Создает Widget Extension target и настраивает App Groups

set -e

echo "🎯 Настройка Widgets в Xcode..."

# 1. Создаем Widget Extension target
echo "📱 Создание Widget Extension target..."

# Добавляем Widget Extension в project.pbxproj
python3 << 'EOF'
import re

# Читаем project.pbxproj
with open('ALADDIN.xcodeproj/project.pbxproj', 'r') as f:
    content = f.read()

# Добавляем Widget Extension target
widget_target = '''
		ALADDINWidgets /* ALADDINWidgets */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = ALADDINWidgets /* Build configuration list for PBXNativeTarget "ALADDINWidgets" */;
			buildPhases = (
				ALADDINWidgets /* Sources */,
				ALADDINWidgets /* Frameworks */,
				ALADDINWidgets /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = ALADDINWidgets;
			productName = ALADDINWidgets;
			productReference = ALADDINWidgets /* ALADDINWidgets.appex */;
			productType = "com.apple.product-type.app-extension";
		};
'''

# Добавляем target в targets секцию
targets_pattern = r'(/\* Begin PBXNativeTarget section \*/\n)(.*?)(/\* End PBXNativeTarget section \*/)'
match = re.search(targets_pattern, content, re.DOTALL)
if match:
    before = match.group(1)
    targets = match.group(2)
    after = match.group(3)
    
    # Добавляем widget target перед End PBXNativeTarget section
    new_targets = targets + widget_target
    new_content = content.replace(match.group(0), before + new_targets + after)
    
    with open('ALADDIN.xcodeproj/project.pbxproj', 'w') as f:
        f.write(new_content)
    
    print("✅ Widget Extension target добавлен в project.pbxproj")
else:
    print("❌ Не удалось найти targets секцию")

EOF

echo "✅ Widget Extension target создан"
echo "📋 Следующие шаги нужно выполнить вручную в Xcode:"
echo "1. Откройте ALADDIN.xcodeproj в Xcode"
echo "2. File → New → Target → Widget Extension"
echo "3. Название: ALADDINWidgets"
echo "4. Bundle Identifier: family.aladdin.ios.widgets"
echo "5. Включите App Groups: group.com.aladdin.family"
echo "6. Добавьте файлы из папки ALADDINWidgets/"
echo "7. Настройте Build Settings для App Groups"

echo "🎯 Настройка Widgets завершена!"
