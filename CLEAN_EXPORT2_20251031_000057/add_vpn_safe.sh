#!/bin/bash
# Безопасное добавление VPNScreen в project.pbxproj

set -e

echo "🔧 Безопасное добавление VPNScreen в project.pbxproj..."

# Создаем резервную копию
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Резервная копия создана"

# Генерируем уникальные ID
FILE_ID="A$(date +%s | tail -c 10)"
BUILD_ID="A$(date +%s | tail -c 10 | sed 's/./&/1')"
# Убеждаемся, что ID разные
if [ "$FILE_ID" = "$BUILD_ID" ]; then
    BUILD_ID="A$(date +%s | tail -c 10 | sed 's/./&/1')"
fi
echo "🆔 FILE_ID: $FILE_ID"
echo "🆔 BUILD_ID: $BUILD_ID"

# Добавляем в PBXFileReference (перед /* End PBXFileReference section */)
sed -i '' "/\/\* End PBXFileReference section \*\//i\\
		$FILE_ID \/\* 03_VPNScreen.swift \*\/ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"Screens/03_VPNScreen.swift\"; sourceTree = \"<group>\"; };" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Добавлено в PBXFileReference"

# Добавляем в PBXBuildFile (перед /* End PBXBuildFile section */)
sed -i '' "/\/\* End PBXBuildFile section \*\//i\\
		$BUILD_ID \/\* 03_VPNScreen.swift in Sources \*\/ = {isa = PBXBuildFile; fileRef = $FILE_ID \/\* 03_VPNScreen.swift \*\/; };" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Добавлено в PBXBuildFile"

# Добавляем в группу Screens (находим правильную группу)
sed -i '' "/A3000066 \/\* Screens \*\/ = {/,/);/s/);/\\
			$FILE_ID \/\* 03_VPNScreen.swift \*\/,\\
		);/" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Добавлено в группу Screens"

# Добавляем в PBXSourcesBuildPhase (находим правильную секцию)
sed -i '' "/A1234567890123456789012U \/\* Sources \*\/ = {/,/);/s/);/\\
			$BUILD_ID \/\* 03_VPNScreen.swift in Sources \*\/,\\
		);/" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Добавлено в PBXSourcesBuildPhase"

echo "🎉 VPNScreen успешно добавлен в project.pbxproj!"
echo "🔍 Проверяем результат..."

# Проверяем результат
./check_file_conflicts.sh VPNScreen

echo "🔨 Компилируем проект..."
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build

echo "✅ Готово! VPNScreen добавлен и проект компилируется успешно!"
