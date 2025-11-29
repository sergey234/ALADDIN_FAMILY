#!/bin/bash

echo "🔧 ЭТАП 3: Безопасное исправление дублирующих записей..."

# Создаем резервную копию перед исправлением
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_before_duplicates_fix

echo "📊 Найдено дублирующих записей A300005: $(grep -c 'A300005' ALADDIN.xcodeproj/project.pbxproj)"

# Находим все дублирующие записи A300005
echo "🔍 Поиск дублирующих записей..."
grep -n "A300005" ALADDIN.xcodeproj/project.pbxproj

echo "⚠️ ВНИМАНИЕ: Найдены дублирующие записи A300005!"
echo "📋 План исправления:"
echo "1. Удалить дублирующие PBXBuildFile записи"
echo "2. Удалить дублирующие PBXFileReference записи" 
echo "3. Удалить дублирующие записи в группах"
echo "4. Удалить дублирующие записи в Sources"

# Безопасное удаление по одной записи
echo "🔧 Удаление дублирующих записей..."

# Удаляем дублирующие PBXBuildFile записи
sed -i '' '/A300005[0-9].*PBXBuildFile/d' ALADDIN.xcodeproj/project.pbxproj

# Удаляем дублирующие PBXFileReference записи  
sed -i '' '/A300005[0-9].*PBXFileReference/d' ALADDIN.xcodeproj/project.pbxproj

# Удаляем дублирующие записи в группах
sed -i '' '/A300005[0-9]/d' ALADDIN.xcodeproj/project.pbxproj

echo "✅ Дублирующие записи удалены!"
echo "📊 Осталось дублирующих записей: $(grep -c 'A300005' ALADDIN.xcodeproj/project.pbxproj)"

if [ $(grep -c 'A300005' ALADDIN.xcodeproj/project.pbxproj) -eq 0 ]; then
    echo "🎉 Все дублирующие записи успешно удалены!"
else
    echo "⚠️ Остались дублирующие записи, нужно проверить вручную"
fi
