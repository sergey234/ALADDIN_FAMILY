#!/bin/bash

# 🔍 ALADDIN iOS PROJECT - СКРИПТ ДИАГНОСТИКИ
# Автор: AI Assistant
# Дата: 21 октября 2025
# Назначение: Полная диагностика проекта для ML модели

echo "🛡️ ALADDIN iOS PROJECT - ДИАГНОСТИКА"
echo "======================================"
echo ""

# 📊 1. ОБЩАЯ ИНФОРМАЦИЯ
echo "📊 1. ОБЩАЯ ИНФОРМАЦИЯ О ПРОЕКТЕ"
echo "--------------------------------"
echo "Рабочая директория: $(pwd)"
echo "Дата диагностики: $(date)"
echo ""

# 📁 2. СТРУКТУРА ПРОЕКТА
echo "📁 2. СТРУКТУРА ПРОЕКТА"
echo "----------------------"
echo "Количество Swift файлов: $(find . -name "*.swift" -not -path "./.git/*" -not -path "./DerivedData/*" -not -path "./build/*" | wc -l)"
echo "Экраны (Screens): $(find ./Screens -name "*.swift" | wc -l)"
echo "ViewModels: $(find ./ViewModels -name "*.swift" | wc -l)"
echo "Core модули: $(find ./Core -name "*.swift" | wc -l)"
echo "Shared компоненты: $(find ./Shared -name "*.swift" | wc -l)"
echo ""

# 🔍 3. ПРОВЕРКА СБОРКИ
echo "🔍 3. ПРОВЕРКА СБОРКИ"
echo "--------------------"
echo "Запускаю сборку проекта..."
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | tail -10
echo ""

# 📱 4. ПРОВЕРКА .app ФАЙЛА
echo "📱 4. ПРОВЕРКА .app ФАЙЛА"
echo "------------------------"
APP_PATH="$HOME/Library/Developer/Xcode/DerivedData/ALADDIN-eahryzmutvtbyceygnlyjsmiiaha/Build/Products/Debug-iphonesimulator/ALADDIN.app"
if [ -d "$APP_PATH" ]; then
    echo "✅ .app папка существует"
    echo "Содержимое .app папки:"
    ls -la "$APP_PATH"
    echo ""
    if [ -f "$APP_PATH/ALADDIN" ]; then
        echo "✅ Исполняемый файл ALADDIN найден"
        echo "Размер: $(ls -lh "$APP_PATH/ALADDIN" | awk '{print $5}')"
    else
        echo "❌ Исполняемый файл ALADDIN НЕ НАЙДЕН"
    fi
else
    echo "❌ .app папка НЕ НАЙДЕНА"
fi
echo ""

# 🔍 5. ПОИСК ОШИБОК
echo "🔍 5. ПОИСК ОШИБОК"
echo "-----------------"
echo "Поиск ошибок в Swift файлах..."
ERROR_COUNT=$(grep -r "error:" . --include="*.swift" 2>/dev/null | wc -l)
echo "Найдено ошибок: $ERROR_COUNT"
if [ $ERROR_COUNT -gt 0 ]; then
    echo "Примеры ошибок:"
    grep -r "error:" . --include="*.swift" 2>/dev/null | head -5
fi
echo ""

# 🔍 6. ПОИСК ДУБЛИКАТОВ
echo "🔍 6. ПОИСК ДУБЛИКАТОВ"
echo "---------------------"
echo "Поиск дублирующих файлов..."
DUPLICATES=$(find . -name "*.swift" -exec basename {} \; | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
    echo "Найдены дубликаты:"
    echo "$DUPLICATES"
else
    echo "✅ Дубликатов не найдено"
fi
echo ""

# 🔍 7. ПРОВЕРКА OnboardingScreen
echo "🔍 7. ПРОВЕРКА OnboardingScreen"
echo "------------------------------"
if [ -f "./Screens/OnboardingScreen.swift" ]; then
    echo "✅ OnboardingScreen.swift найден"
    echo "Размер: $(ls -lh "./Screens/OnboardingScreen.swift" | awk '{print $5}')"
    echo "Последние изменения: $(ls -l "./Screens/OnboardingScreen.swift" | awk '{print $6, $7, $8}')"
else
    echo "❌ OnboardingScreen.swift НЕ НАЙДЕН"
fi

if [ -f "./Screens/14_OnboardingScreen.swift" ]; then
    echo "✅ 14_OnboardingScreen.swift найден"
    echo "Размер: $(ls -lh "./Screens/14_OnboardingScreen.swift" | awk '{print $5}')"
else
    echo "❌ 14_OnboardingScreen.swift НЕ НАЙДЕН"
fi
echo ""

# 💾 8. ДОСТУПНЫЕ БЭКАПЫ
echo "💾 8. ДОСТУПНЫЕ БЭКАПЫ"
echo "---------------------"
echo "Список бэкапов project.pbxproj:"
ls -la ALADDIN.xcodeproj/project.pbxproj.backup_* 2>/dev/null | awk '{print $9, $5, $6, $7, $8}'
echo ""

# 📋 9. РЕКОМЕНДАЦИИ
echo "📋 9. РЕКОМЕНДАЦИИ"
echo "-----------------"
echo "1. Исправить OnboardingScreen.swift - создать рабочую версию"
echo "2. Устранить дублирование файлов"
echo "3. Исправить ошибки компиляции по одной"
echo "4. Протестировать сборку после каждого исправления"
echo "5. Использовать бэкап: backup_with_components_20251021_141747"
echo ""

echo "🏁 ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "========================="
echo "Время: $(date)"
echo "Статус: Готов к исправлению"
