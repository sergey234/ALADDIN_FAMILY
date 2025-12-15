#!/bin/bash

# Полный бэкап мобильного приложения ALADDIN iOS
# Включает все необходимые файлы для сборки IPA

set -e

# Получить текущую дату и время
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="BACKUP_MOBILE_${TIMESTAMP}"
BACKUP_DIR="BACKUPS/${BACKUP_NAME}"
PROJECT_ROOT="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

cd "$PROJECT_ROOT"

echo "📦 Создание полного бэкапа мобильного приложения..."
echo "📁 Директория бэкапа: $BACKUP_DIR"

# Создать директорию бэкапа
mkdir -p "$BACKUP_DIR"

# 1. Проектные папки (как в предыдущем бэкапе)
echo "📂 Копирование проектных папок..."
[ -d "ALADDIN.xcodeproj" ] && cp -R "ALADDIN.xcodeproj" "$BACKUP_DIR/" || echo "⚠️  ALADDIN.xcodeproj не найден"
[ -d "Assets.xcassets" ] && cp -R "Assets.xcassets" "$BACKUP_DIR/" || echo "⚠️  Assets.xcassets не найден"
[ -d "Components" ] && cp -R "Components" "$BACKUP_DIR/" || echo "⚠️  Components не найден"
[ -d "Core" ] && cp -R "Core" "$BACKUP_DIR/" || echo "⚠️  Core не найден"
[ -d "LocalizedVersions" ] && cp -R "LocalizedVersions" "$BACKUP_DIR/" || echo "⚠️  LocalizedVersions не найден"
[ -d "Screens" ] && cp -R "Screens" "$BACKUP_DIR/" || echo "⚠️  Screens не найден"
[ -d "Shared" ] && cp -R "Shared" "$BACKUP_DIR/" || echo "⚠️  Shared не найден"
[ -d "Tests" ] && cp -R "Tests" "$BACKUP_DIR/" || echo "⚠️  Tests не найден"
[ -d "ViewModels" ] && cp -R "ViewModels" "$BACKUP_DIR/" || echo "⚠️  ViewModels не найден"
[ -d "docs" ] && cp -R "docs" "$BACKUP_DIR/" || echo "⚠️  docs не найден"
[ -d "Resources" ] && cp -R "Resources" "$BACKUP_DIR/" || echo "⚠️  Resources не найден"
[ -d "resources" ] && cp -R "resources" "$BACKUP_DIR/" || echo "⚠️  resources не найден"
[ -d "scripts" ] && cp -R "scripts" "$BACKUP_DIR/" || echo "⚠️  scripts не найден"

# 2. Файлы для сборки IPA
echo "📂 Копирование файлов для сборки IPA..."

# GitHub workflows (включая check-secrets.yml)
[ -d ".github" ] && cp -R ".github" "$BACKUP_DIR/" || echo "⚠️  .github не найден"

# ExportOptions.plist
[ -f "ExportOptions.plist" ] && cp "ExportOptions.plist" "$BACKUP_DIR/" || echo "⚠️  ExportOptions.plist не найден"

# Podfile
[ -f "Podfile" ] && cp "Podfile" "$BACKUP_DIR/" || echo "⚠️  Podfile не найден"

# ALADDIN папка (с Info.plist и сертификатами)
[ -d "ALADDIN" ] && cp -R "ALADDIN" "$BACKUP_DIR/" || echo "⚠️  ALADDIN не найден"

# ALADDINWidgets
[ -d "ALADDINWidgets" ] && cp -R "ALADDINWidgets" "$BACKUP_DIR/" || echo "⚠️  ALADDINWidgets не найден"

# ALADDINApp.swift (корневой файл)
[ -f "ALADDINApp.swift" ] && cp "ALADDINApp.swift" "$BACKUP_DIR/" || echo "⚠️  ALADDINApp.swift не найден"

# Info.plist (если есть в корне)
[ -f "Info.plist" ] && cp "Info.plist" "$BACKUP_DIR/" || echo "⚠️  Info.plist не найден в корне"

# Entitlements файлы
[ -f "ALADDINPacketTunnel.entitlements" ] && cp "ALADDINPacketTunnel.entitlements" "$BACKUP_DIR/" || echo "⚠️  ALADDINPacketTunnel.entitlements не найден"
[ -f "ALADDINPacketTunnelDebug.entitlements" ] && cp "ALADDINPacketTunnelDebug.entitlements" "$BACKUP_DIR/" || echo "⚠️  ALADDINPacketTunnelDebug.entitlements не найден"

# fastlane
[ -d "fastlane" ] && cp -R "fastlane" "$BACKUP_DIR/" || echo "⚠️  fastlane не найден"

# .gitignore (если есть)
[ -f ".gitignore" ] && cp ".gitignore" "$BACKUP_DIR/" || echo "⚠️  .gitignore не найден"

# CoreModules (если есть)
[ -d "CoreModules" ] && cp -R "CoreModules" "$BACKUP_DIR/" || echo "⚠️  CoreModules не найден"

# Preview Content (если есть)
[ -d "Preview Content" ] && cp -R "Preview Content" "$BACKUP_DIR/" || echo "⚠️  Preview Content не найден"

# Создать файл с информацией о бэкапе
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
Полный бэкап мобильного приложения ALADDIN iOS
Дата создания: $(date)
Версия: Актуальная версия с workflow check-secrets.yml

Включенные компоненты:
1. Проектные папки:
   - ALADDIN.xcodeproj
   - Assets.xcassets
   - Components
   - Core
   - LocalizedVersions
   - Screens
   - Shared
   - Tests
   - ViewModels
   - docs
   - Resources/resources
   - scripts

2. Файлы для сборки IPA:
   - .github/workflows (все workflow файлы, включая check-secrets.yml)
   - ExportOptions.plist
   - Podfile
   - ALADDIN/ (Info.plist, сертификаты)
   - ALADDINWidgets/
   - ALADDINApp.swift
   - Entitlements файлы
   - fastlane/Fastfile
   - .gitignore

Этот бэкап содержит все необходимые файлы для:
- Восстановления проекта на 100%
- Сборки IPA архива для Apple App Store
- Запуска GitHub Actions workflows

Для восстановления:
1. Распакуйте архив
2. Скопируйте все файлы в корень проекта
3. Установите зависимости: pod install
4. Откройте проект в Xcode: open ALADDIN.xcodeproj
EOF

echo "✅ Бэкап создан: $BACKUP_DIR"

# Подсчитать размер и количество файлов
echo ""
echo "📊 Статистика бэкапа:"
FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l | tr -d ' ')
SWIFT_COUNT=$(find "$BACKUP_DIR" -name "*.swift" | wc -l | tr -d ' ')
DIR_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo "   Всего файлов: $FILE_COUNT"
echo "   Swift файлов: $SWIFT_COUNT"
echo "   Размер: $DIR_SIZE"

# Создать ZIP архив
echo ""
echo "📦 Создание ZIP архива..."
ZIP_FILE="BACKUPS/${BACKUP_NAME}.zip"
cd BACKUPS
zip -r "${BACKUP_NAME}.zip" "${BACKUP_NAME}" -q
ZIP_SIZE=$(du -sh "${BACKUP_NAME}.zip" | cut -f1)
cd ..

echo "✅ ZIP архив создан: $ZIP_FILE"
echo "   Размер архива: $ZIP_SIZE"

# Проверка целостности архива
echo ""
echo "🔍 Проверка целостности архива..."
cd BACKUPS
if unzip -t "${BACKUP_NAME}.zip" > /dev/null 2>&1; then
    echo "✅ Архив целостен, ошибок не обнаружено"
else
    echo "❌ ОШИБКА: Архив поврежден!"
    exit 1
fi
cd ..

echo ""
echo "✅ Полный бэкап успешно создан!"
echo "📁 Директория: $BACKUP_DIR"
echo "📦 Архив: $ZIP_FILE"
echo ""
echo "Для восстановления распакуйте архив и скопируйте файлы в корень проекта."
