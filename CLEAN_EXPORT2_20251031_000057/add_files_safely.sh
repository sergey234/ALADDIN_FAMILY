#!/bin/bash

# 🛡️ БЕЗОПАСНОЕ ДОБАВЛЕНИЕ ФАЙЛОВ В XCODE ПРОЕКТ
# Совместимо с Xcode 13.2.1

echo "🛡️ Безопасное добавление файлов в Xcode проект..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Создаем резервную копию
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.safe_backup_$(date +%Y%m%d_%H%M%S)

echo "✅ Создана резервная копия"

# Функция для генерации уникального ID
generate_id() {
    echo "A$(shuf -i 1000000000000000000000-9999999999999999999999 -n 1)"
}

# Список файлов для добавления (по приоритету)
FILES=(
    "Core/Navigation/NavigationManager.swift"
    "ALADDINApp_WithNavigation.swift"
    "Shared/Components/Navigation/ALADDINNavigationBar.swift"
    "Screens/02_FamilyScreen.swift"
    "Screens/03_VPNScreen.swift"
    "Screens/04_AnalyticsScreen.swift"
    "Screens/05_SettingsScreen.swift"
    "Screens/06_AIAssistantScreen.swift"
    "Screens/07_ParentalControlScreen.swift"
    "Screens/08_ChildInterfaceScreen.swift"
    "Screens/09_ElderlyInterfaceScreen.swift"
    "Screens/10_TariffsScreen.swift"
    "Screens/11_ProfileScreen.swift"
    "Screens/12_NotificationsScreen.swift"
    "Screens/13_SupportScreen.swift"
    "Screens/14_OnboardingScreen.swift"
    "Screens/18_PrivacyPolicyScreen.swift"
    "Screens/19_TermsOfServiceScreen.swift"
    "Screens/20_DevicesScreen.swift"
    "Screens/21_ReferralScreen.swift"
    "Screens/22_DeviceDetailScreen.swift"
    "Screens/23_FamilyChatScreen.swift"
    "Screens/24_VPNEnergyStatsScreen.swift"
    "Screens/25_PaymentQRScreen.swift"
)

echo "📱 Будет добавлено ${#FILES[@]} файлов"

# Добавляем файлы по одному с проверкой
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "➕ Добавляем: $file"
        
        # Генерируем уникальные ID
        file_id=$(generate_id)
        build_id=$(generate_id)
        
        # Создаем временный файл
        TEMP_PROJECT="temp_safe_project.pbxproj"
        cp ALADDIN.xcodeproj/project.pbxproj "$TEMP_PROJECT"
        
        # Добавляем в PBXFileReference
        sed -i '' "/End PBXFileReference section/i\\
		$file_id /* $(basename "$file") */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"$(basename "$file")\"; sourceTree = \"<group>\"; };\\
" "$TEMP_PROJECT"
        
        # Добавляем в PBXBuildFile
        sed -i '' "/End PBXBuildFile section/i\\
		$build_id /* $(basename "$file") in Sources */ = {isa = PBXBuildFile; fileRef = $file_id /* $(basename "$file") */; };\\
" "$TEMP_PROJECT"
        
        # Добавляем в PBXGroup
        sed -i '' "/A1234567890123456789012P \/\* Preview Content \*\//i\\
				$file_id /* $(basename "$file") */,\\
" "$TEMP_PROJECT"
        
        # Добавляем в PBXSourcesBuildPhase
        sed -i '' "/End PBXSourcesBuildPhase section/i\\
				$build_id /* $(basename "$file") in Sources */,\\
" "$TEMP_PROJECT"
        
        # Заменяем оригинальный файл
        mv "$TEMP_PROJECT" ALADDIN.xcodeproj/project.pbxproj
        
        # Тестируем сборку
        echo "🔨 Тестируем сборку..."
        if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build -quiet 2>/dev/null; then
            echo "✅ УСПЕХ! $file добавлен"
        else
            echo "❌ ОШИБКА с $file! Восстанавливаем..."
            cp ALADDIN.xcodeproj/project.pbxproj.safe_backup_* ALADDIN.xcodeproj/project.pbxproj
            echo "🔄 Восстановлена резервная копия"
            break
        fi
    else
        echo "⚠️ Файл не найден: $file"
    fi
done

echo "🎉 Скрипт завершен!"
echo "📊 Статистика:"
echo "   - Добавлено файлов: $(grep -c "sourcecode.swift" ALADDIN.xcodeproj/project.pbxproj)"
echo "   - Резервная копия: ALADDIN.xcodeproj/project.pbxproj.safe_backup_*"
