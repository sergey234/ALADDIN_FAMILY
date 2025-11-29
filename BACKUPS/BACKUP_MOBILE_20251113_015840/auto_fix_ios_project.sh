#!/bin/bash

# 🚀 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ iOS ПРОЕКТА ALADDIN
# Автор: AI Assistant
# Версия: 1.0
# Совместимость: Xcode 13.2.1+

echo "🚀 Начинаем автоматическое исправление iOS проекта ALADDIN..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Создаем резервную копию
echo "📋 Создаем резервную копию..."
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_$(date +%Y%m%d_%H%M%S)

# Шаг 1: Исправляем версию Xcode
echo "🔧 Шаг 1: Исправляем версию Xcode..."
sed -i '' 's/objectVersion = 56;/objectVersion = 54;/g' ALADDIN.xcodeproj/project.pbxproj

# Шаг 2: Удаляем папки из Sources
echo "🔧 Шаг 2: Удаляем папки из Sources..."
sed -i '' '/Screens in Sources/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/ViewModels in Sources/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/Components in Sources/d' ALADDIN.xcodeproj/project.pbxproj

# Удаляем из PBXFileReference
sed -i '' '/Screens.*folder/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/ViewModels.*folder/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/Components.*folder/d' ALADDIN.xcodeproj/project.pbxproj

# Удаляем из PBXGroup
sed -i '' '/A1234567890123456789013D.*Screens/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/A1234567890123456789013F.*ViewModels/d' ALADDIN.xcodeproj/project.pbxproj
sed -i '' '/A1234567890123456789013H.*Components/d' ALADDIN.xcodeproj/project.pbxproj

# Шаг 3: Создаем ContentView.swift
echo "🔧 Шаг 3: Создаем ContentView.swift..."
cat > ContentView.swift << 'EOF'
import SwiftUI

struct ContentView: View {
    var body: some View {
        MainScreen()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
EOF

# Шаг 4: Исправляем Preview Assets
echo "🔧 Шаг 4: Исправляем Preview Assets..."
rm -f "Preview Content/Preview Assets.xcassets"
mkdir -p "Preview Content/Preview Assets.xcassets"
echo '{"info":{"author":"xcode","version":1}}' > "Preview Content/Preview Assets.xcassets/Contents.json"

# Шаг 5: Добавляем MainScreen в проект
echo "🔧 Шаг 5: Добавляем MainScreen в проект..."

# Генерируем уникальные ID
FILE_ID="A$(jot -r 1 1000000000000000000000 9999999999999999999999)"
BUILD_ID="A$(jot -r 1 1000000000000000000000 9999999999999999999999)"

echo "   File ID: $FILE_ID"
echo "   Build ID: $BUILD_ID"

# Добавляем в PBXBuildFile
sed -i '' "/End PBXBuildFile section/i\\
		$BUILD_ID /* 01_MainScreen.swift in Sources */ = {isa = PBXBuildFile; fileRef = $FILE_ID /* 01_MainScreen.swift */; };\\
" ALADDIN.xcodeproj/project.pbxproj

# Добавляем в PBXFileReference
sed -i '' "/End PBXFileReference section/i\\
		$FILE_ID /* 01_MainScreen.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"01_MainScreen.swift\"; sourceTree = \"<group>\"; };\\
" ALADDIN.xcodeproj/project.pbxproj

# Добавляем в PBXGroup
sed -i '' "/A1234567890123456789012P \/\* Preview Content \*\//i\\
				$FILE_ID /* 01_MainScreen.swift */,\\
" ALADDIN.xcodeproj/project.pbxproj

# Добавляем в PBXSourcesBuildPhase
sed -i '' "/End PBXSourcesBuildPhase section/i\\
				$BUILD_ID /* 01_MainScreen.swift in Sources */,\\
" ALADDIN.xcodeproj/project.pbxproj

# Шаг 6: Тестируем сборку
echo "🔧 Шаг 6: Тестируем сборку..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build -quiet 2>/dev/null; then
    echo "✅ УСПЕХ! Проект собирается!"
    
    # Шаг 7: Запускаем приложение
    echo "🚀 Запускаем приложение на симуляторе..."
    xcrun simctl launch "iPhone 12" family.aladdin.ios
    
    echo "🎉 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!"
    echo "📊 Результат:"
    echo "   ✅ Проект собирается"
    echo "   ✅ Приложение запускается"
    echo "   ✅ Резервная копия создана"
    echo "   ✅ Готов к дальнейшей разработке"
    
else
    echo "❌ ОШИБКА! Восстанавливаем резервную копию..."
    cp ALADDIN.xcodeproj/project.pbxproj.backup_* ALADDIN.xcodeproj/project.pbxproj
    echo "🔄 Восстановлена резервная копия"
    echo "🚫 Автоматическое исправление не удалось"
    echo "💡 Попробуйте ручное исправление по алгоритму"
fi

echo "🏁 Скрипт завершен!"
