#!/bin/bash

echo "🔧 Исправляю дублирующие записи в project.pbxproj..."

# Создаем резервную копию
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_duplicates_fix

# Удаляем дублирующие записи (вторые записи с A3000054+)
echo "Удаляю дублирующие PBXBuildFile записи..."
sed -i '' '/A300005[0-9]/d' ALADDIN.xcodeproj/project.pbxproj

echo "Удаляю дублирующие PBXFileReference записи..."
sed -i '' '/A300005[0-9]/d' ALADDIN.xcodeproj/project.pbxproj

echo "Удаляю дублирующие записи в группах..."
sed -i '' '/A300005[0-9]/d' ALADDIN.xcodeproj/project.pbxproj

echo "Удаляю дублирующие записи в Sources..."
sed -i '' '/A300005[0-9]/d' ALADDIN.xcodeproj/project.pbxproj

echo "✅ Дублирующие записи удалены!"
echo "📊 Проверяю результат..."

# Проверяем что дублирующих записей больше нет
duplicates=$(grep -c "A300005" ALADDIN.xcodeproj/project.pbxproj)
echo "Осталось дублирующих записей: $duplicates"

if [ $duplicates -eq 0 ]; then
    echo "🎉 Все дублирующие записи успешно удалены!"
else
    echo "⚠️ Остались дублирующие записи, нужно проверить вручную"
fi
