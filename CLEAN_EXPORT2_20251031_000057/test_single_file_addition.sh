#!/bin/bash

# 🧪 ТЕСТОВЫЙ СКРИПТ - ДОБАВЛЕНИЕ 1 ФАЙЛА
# Безопасное добавление одного файла для тестирования

echo "🧪 Тестируем добавление одного файла..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Создаем резервную копию
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.test_backup

echo "✅ Создана резервная копия"

# Тестируем добавление NavigationManager.swift
FILE_PATH="Core/Navigation/NavigationManager.swift"
FILE_NAME="NavigationManager.swift"

# Генерируем ID
FILE_ID="A$(shuf -i 1000000000000000000000-9999999999999999999999 -n 1)"
BUILD_ID="A$(shuf -i 1000000000000000000000-9999999999999999999999 -n 1)"

echo "➕ Добавляем: $FILE_NAME"
echo "   File ID: $FILE_ID"
echo "   Build ID: $BUILD_ID"

# Создаем временный файл
TEMP_PROJECT="temp_test_project.pbxproj"
cp ALADDIN.xcodeproj/project.pbxproj "$TEMP_PROJECT"

# Добавляем в PBXFileReference
sed -i '' "/End PBXFileReference section/i\\
		$FILE_ID /* $FILE_NAME */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"$FILE_NAME\"; sourceTree = \"<group>\"; };\\
" "$TEMP_PROJECT"

# Добавляем в PBXBuildFile
sed -i '' "/End PBXBuildFile section/i\\
		$BUILD_ID /* $FILE_NAME in Sources */ = {isa = PBXBuildFile; fileRef = $FILE_ID /* $FILE_NAME */; };\\
" "$TEMP_PROJECT"

# Добавляем в PBXGroup
sed -i '' "/A1234567890123456789012P \/\* Preview Content \*\//i\\
				$FILE_ID /* $FILE_NAME */,\\
" "$TEMP_PROJECT"

# Добавляем в PBXSourcesBuildPhase
sed -i '' "/End PBXSourcesBuildPhase section/i\\
				$BUILD_ID /* $FILE_NAME in Sources */,\\
" "$TEMP_PROJECT"

# Заменяем оригинальный файл
mv "$TEMP_PROJECT" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Файл добавлен в project.pbxproj"

# Тестируем сборку
echo "🔨 Тестируем сборку..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build -quiet 2>/dev/null; then
    echo "✅ УСПЕХ! Проект собирается с новым файлом!"
    echo "🎉 Можно добавлять остальные файлы"
else
    echo "❌ ОШИБКА! Восстанавливаем резервную копию..."
    cp ALADDIN.xcodeproj/project.pbxproj.test_backup ALADDIN.xcodeproj/project.pbxproj
    echo "🔄 Восстановлена резервная копия"
    echo "🚫 НЕ добавляем остальные файлы!"
fi

echo "🧪 Тест завершен!"
