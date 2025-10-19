#!/bin/bash

# 🧪 ДОБАВЛЕНИЕ 1 ФАЙЛА - ТЕСТОВЫЙ РЕЖИМ
# Безопасное добавление одного файла с проверкой

echo "🧪 Добавляем 1 файл для тестирования..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Создаем резервную копию
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.single_test_backup

echo "✅ Создана резервная копия"

# Функция для генерации уникального ID
generate_id() {
    echo "A$(jot -r 1 1000000000000000000000 9999999999999999999999)"
}

# Добавляем NavigationManager.swift (самый важный файл)
FILE_PATH="Core/Navigation/NavigationManager.swift"
FILE_NAME="NavigationManager.swift"

if [ -f "$FILE_PATH" ]; then
    echo "➕ Добавляем: $FILE_NAME"
    
    # Генерируем уникальные ID
    file_id=$(generate_id)
    build_id=$(generate_id)
    
    echo "   File ID: $file_id"
    echo "   Build ID: $build_id"
    
    # Создаем временный файл
    TEMP_PROJECT="temp_single_project.pbxproj"
    cp ALADDIN.xcodeproj/project.pbxproj "$TEMP_PROJECT"
    
    # Добавляем в PBXFileReference
    sed -i '' "/End PBXFileReference section/i\\
		$file_id /* $FILE_NAME */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"$FILE_NAME\"; sourceTree = \"<group>\"; };\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXBuildFile
    sed -i '' "/End PBXBuildFile section/i\\
		$build_id /* $FILE_NAME in Sources */ = {isa = PBXBuildFile; fileRef = $file_id /* $FILE_NAME */; };\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXGroup
    sed -i '' "/A1234567890123456789012P \/\* Preview Content \*\//i\\
				$file_id /* $FILE_NAME */,\\
" "$TEMP_PROJECT"
    
    # Добавляем в PBXSourcesBuildPhase
    sed -i '' "/End PBXSourcesBuildPhase section/i\\
				$build_id /* $FILE_NAME in Sources */,\\
" "$TEMP_PROJECT"
    
    # Заменяем оригинальный файл
    mv "$TEMP_PROJECT" ALADDIN.xcodeproj/project.pbxproj
    
    echo "✅ Файл добавлен в project.pbxproj"
    
    # Тестируем сборку
    echo "🔨 Тестируем сборку..."
    if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build 2>&1 | grep -q "BUILD SUCCEEDED"; then
        echo "🎉 УСПЕХ! NavigationManager.swift добавлен и проект собирается!"
        echo "✅ Можно добавлять остальные файлы"
    else
        echo "❌ ОШИБКА! Восстанавливаем резервную копию..."
        cp ALADDIN.xcodeproj/project.pbxproj.single_test_backup ALADDIN.xcodeproj/project.pbxproj
        echo "🔄 Восстановлена резервная копия"
        echo "🚫 НЕ добавляем остальные файлы!"
    fi
else
    echo "❌ Файл не найден: $FILE_PATH"
fi

echo "🧪 Тест завершен!"
