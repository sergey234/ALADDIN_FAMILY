#!/bin/bash

# 🚀 АВТОМАТИЧЕСКИЙ СКРИПТ ДОБАВЛЕНИЯ ВСЕХ ФАЙЛОВ В XCODE ПРОЕКТ
# Автор: AI Assistant
# Дата: $(date)

echo "🚀 Начинаем добавление всех файлов в Xcode проект..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Создаем резервную копию project.pbxproj
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_$(date +%Y%m%d_%H%M%S)

echo "✅ Создана резервная копия project.pbxproj"

# Функция для генерации уникального ID
generate_id() {
    echo "A$(shuf -i 1000000000000000000000-9999999999999999999999 -n 1)"
}

# Получаем все Swift файлы
SWIFT_FILES=($(find . -name "*.swift" -not -path "./ALADDIN.xcodeproj/*" | sort))

echo "📱 Найдено ${#SWIFT_FILES[@]} Swift файлов"

# Создаем временный файл для нового project.pbxproj
TEMP_PROJECT="temp_project.pbxproj"
cp ALADDIN.xcodeproj/project.pbxproj "$TEMP_PROJECT"

# Добавляем каждый файл в project.pbxproj
for file in "${SWIFT_FILES[@]}"; do
    # Получаем относительный путь
    relative_path="${file#./}"
    
    # Генерируем уникальные ID
    file_id=$(generate_id)
    build_id=$(generate_id)
    
    echo "➕ Добавляем: $relative_path"
    
    # Добавляем в PBXFileReference
    sed -i '' "/End PBXFileReference section/i\\
		$file_id /* $(basename "$relative_path") */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"$(basename "$relative_path")\"; sourceTree = \"<group>\"; };\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXBuildFile
    sed -i '' "/End PBXBuildFile section/i\\
		$build_id /* $(basename "$relative_path") in Sources */ = {isa = PBXBuildFile; fileRef = $file_id /* $(basename "$relative_path") */; };\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXGroup (в группу ALADDIN)
    sed -i '' "/A1234567890123456789012P \/\* Preview Content \*\//i\\
				$file_id /* $(basename "$relative_path") */,\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXSourcesBuildPhase
    sed -i '' "/End PBXSourcesBuildPhase section/i\\
				$build_id /* $(basename "$relative_path") in Sources */,\\
" "$TEMP_PROJECT"
done

# Заменяем оригинальный файл
mv "$TEMP_PROJECT" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Все файлы добавлены в project.pbxproj"

# Тестируем сборку
echo "🔨 Тестируем сборку проекта..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build -quiet; then
    echo "✅ Проект успешно собирается!"
else
    echo "❌ Ошибка сборки! Восстанавливаем резервную копию..."
    cp ALADDIN.xcodeproj/project.pbxproj.backup_* ALADDIN.xcodeproj/project.pbxproj
    echo "🔄 Восстановлена резервная копия"
fi

echo "🎉 Скрипт завершен!"
echo "📊 Статистика:"
echo "   - Swift файлов: ${#SWIFT_FILES[@]}"
echo "   - Резервная копия: ALADDIN.xcodeproj/project.pbxproj.backup_*"
echo "   - Статус сборки: $(xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build -quiet 2>/dev/null && echo "✅ Успешно" || echo "❌ Ошибка")"
