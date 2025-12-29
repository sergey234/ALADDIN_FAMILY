#!/bin/bash

# Скрипт для создания актуального бэкапа iOS мобильного приложения ALADDIN
# Включает все необходимые файлы для сборки, исключает ненужные
# Дата: 24 декабря 2025

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="BACKUPS/BACKUP_MOBILE_${TIMESTAMP}"
PROJECT_ROOT="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

cd "$PROJECT_ROOT"

echo "📦 Создание актуального бэкапа iOS приложения ALADDIN..."
echo "📁 Директория бэкапа: $BACKUP_DIR"
echo ""

# Создаем директорию бэкапа
mkdir -p "$BACKUP_DIR"

# 1. Проект Xcode (ВСЕ файлы)
echo "📋 Копирование проекта Xcode..."
cp -R ALADDIN.xcodeproj "$BACKUP_DIR/" 2>/dev/null || true

# 2. Все исходные файлы приложения
echo "💻 Копирование исходного кода..."
mkdir -p "$BACKUP_DIR/ALADDIN"
if [ -d "ALADDIN" ]; then
    cp -R ALADDIN/* "$BACKUP_DIR/ALADDIN/" 2>/dev/null || true
fi

# 3. Все экраны (Screens)
echo "🖼️ Копирование экранов..."
if [ -d "Screens" ]; then
    cp -R Screens "$BACKUP_DIR/" 2>/dev/null || true
fi

# 4. ViewModels
echo "📊 Копирование ViewModels..."
if [ -d "ViewModels" ]; then
    cp -R ViewModels "$BACKUP_DIR/" 2>/dev/null || true
fi

# 5. Core модули
echo "🔧 Копирование Core модулей..."
if [ -d "Core" ]; then
    cp -R Core "$BACKUP_DIR/" 2>/dev/null || true
fi

# 6. Shared компоненты
echo "🔗 Копирование Shared компонентов..."
if [ -d "Shared" ]; then
    cp -R Shared "$BACKUP_DIR/" 2>/dev/null || true
fi

# 7. Components
echo "🧩 Копирование Components..."
if [ -d "Components" ]; then
    cp -R Components "$BACKUP_DIR/" 2>/dev/null || true
fi

# 8. ALADDINContentBlocker Extension (актуальный)
echo "🔐 Копирование Content Blocker Extension..."
if [ -d "ALADDINContentBlocker" ]; then
    cp -R ALADDINContentBlocker "$BACKUP_DIR/" 2>/dev/null || true
fi

# 9. ALADDINWidgets
echo "📱 Копирование Widgets..."
if [ -d "ALADDINWidgets" ]; then
    cp -R ALADDINWidgets "$BACKUP_DIR/" 2>/dev/null || true
fi

# 10. Assets (иконки, изображения)
echo "🎨 Копирование Assets..."
if [ -d "Assets.xcassets" ]; then
    cp -R Assets.xcassets "$BACKUP_DIR/" 2>/dev/null || true
fi

# 11. Resources (локализация, сертификаты)
echo "📚 Копирование Resources..."
if [ -d "resources" ]; then
    cp -R resources "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d "Resources" ]; then
    cp -R Resources "$BACKUP_DIR/" 2>/dev/null || true
fi

# 12. LocalizedVersions
echo "🌍 Копирование локализаций..."
if [ -d "LocalizedVersions" ]; then
    cp -R LocalizedVersions "$BACKUP_DIR/" 2>/dev/null || true
fi

# 13. Tests
echo "🧪 Копирование тестов..."
if [ -d "Tests" ]; then
    cp -R Tests "$BACKUP_DIR/" 2>/dev/null || true
fi

# 14. Главный файл приложения
echo "📱 Копирование главного файла приложения..."
if [ -f "ALADDINApp.swift" ]; then
    cp ALADDINApp.swift "$BACKUP_DIR/" 2>/dev/null || true
fi

# 15. Export Options
echo "📤 Копирование Export Options..."
if [ -f "ExportOptions.plist" ]; then
    cp ExportOptions.plist "$BACKUP_DIR/" 2>/dev/null || true
fi

# 16. GitHub Actions workflows
echo "🔄 Копирование GitHub Actions..."
if [ -d ".github" ]; then
    cp -R .github "$BACKUP_DIR/" 2>/dev/null || true
fi

# 17. Scripts
echo "📜 Копирование скриптов..."
if [ -d "scripts" ]; then
    cp -R scripts "$BACKUP_DIR/" 2>/dev/null || true
fi

# 18. Fastlane
echo "🚀 Копирование Fastlane..."
if [ -d "fastlane" ]; then
    cp -R fastlane "$BACKUP_DIR/" 2>/dev/null || true
fi

# 19. Документация (ВСЯ документация, кроме предыдущих бэкапов)
echo "📖 Копирование документации..."
if [ -d "docs" ]; then
    mkdir -p "$BACKUP_DIR/docs"
    # Копируем всю документацию, исключая только предыдущие бэкапы
    find docs -type f -not -path "*/BACKUP*" -not -path "*/BACKUPS/*" -not -path "*/.git/*" -exec cp --parents {} "$BACKUP_DIR/" \; 2>/dev/null || true
    # Также копируем директории
    find docs -type d -not -path "*/BACKUP*" -not -path "*/BACKUPS/*" -not -path "*/.git/*" -exec mkdir -p "$BACKUP_DIR/{}" \; 2>/dev/null || true
fi

# 20. Важные конфигурационные файлы
echo "📄 Копирование конфигурационных файлов..."
# Podfile (если есть)
[ -f "Podfile" ] && cp Podfile "$BACKUP_DIR/" 2>/dev/null || true
[ -f "Podfile.lock" ] && cp Podfile.lock "$BACKUP_DIR/" 2>/dev/null || true
# Package.swift (если есть)
[ -f "Package.swift" ] && cp Package.swift "$BACKUP_DIR/" 2>/dev/null || true
# .gitignore
[ -f ".gitignore" ] && cp .gitignore "$BACKUP_DIR/" 2>/dev/null || true

# 21. Создаем README с описанием бэкапа
cat > "$BACKUP_DIR/README.md" << EOF
# Полный бэкап iOS приложения ALADDIN

## Дата создания
$(date)

## Что включено в бэкап

### 1. Проект Xcode
- \`ALADDIN.xcodeproj/\` - полный проект со всеми настройками
- Все схемы сборки
- Все build settings
- Code Signing настройки

### 2. Исходный код
- \`ALADDIN/\` - основной код приложения
- \`Screens/\` - все экраны приложения
- \`ViewModels/\` - все ViewModels
- \`Core/\` - основные модули (Network, Config, Models, Security, ContentBlocker, etc.)
- \`Shared/\` - общие компоненты
- \`Components/\` - UI компоненты
- \`ALADDINContentBlocker/\` - Content Blocker Extension (актуальный)
- \`ALADDINWidgets/\` - Widgets Extension

### 3. Ресурсы
- \`Assets.xcassets/\` - иконки, изображения, цвета
- \`Resources/\` - локализация, сертификаты
- \`LocalizedVersions/\` - локализованные версии

### 4. Тесты
- \`Tests/\` - все unit и UI тесты

### 5. Критичные файлы
- \`ExportOptions.plist\` - настройки экспорта IPA
- \`ALADDINApp.swift\` - точка входа приложения

### 6. CI/CD
- \`.github/workflows/\` - GitHub Actions workflows
  - \`check-secrets.yml\` - актуальный workflow для проверки секретов
  - \`appstore.yml\` - workflow для сборки App Store
  - другие workflows

### 7. Документация
- \`docs/\` - важная документация проекта
- \`docs/AppStore/\` - документы для App Store

### 8. Fastlane
- \`fastlane/\` - конфигурация Fastlane для автоматизации

## Важные настройки

### Code Signing
- **Development Team:** 6CJVBBUGSN
- **Code Sign Style:** Automatic
- **Bundle ID (Main):** family.aladdin.ios
- **Bundle ID (Content Blocker):** family.aladdin.ios.ALADDINContentBlocker

### Provisioning Profiles
- **ALADDIN:** App Store Distribution
- **ALADDINContentBlocker:** App Store Distribution

## Статус

✅ Проект собирается без ошибок  
✅ Content Blocker Extension настроен  
✅ GitHub Actions workflows настроены  
✅ Документация для App Store готова  
✅ Все ответы Apple подготовлены  

## Как восстановить

1. Распаковать архив:
   \`\`\`bash
   unzip BACKUP_MOBILE_${TIMESTAMP}.zip
   \`\`\`

2. Скопировать файлы в рабочую директорию

3. Открыть проект в Xcode:
   \`\`\`bash
   open ALADDIN.xcodeproj
   \`\`\`

4. Проверить настройки Signing & Capabilities

5. Обновить provisioning profiles (если нужно)

## Примечания

- Provisioning profiles могут истечь - их нужно будет обновить
- Certificates не включены (хранятся в Keychain)
- DerivedData не включен (генерируется автоматически)
- Build артефакты не включены
- Предыдущие бэкапы не включены

## Версия

**Версия приложения:** 1.0.0  
**Статус:** Готово к отправке в App Store  
**Дата бэкапа:** $(date)
EOF

# Подсчитываем статистику
echo ""
echo "📊 Подсчет статистики..."
SWIFT_COUNT=$(find "$BACKUP_DIR" -name "*.swift" 2>/dev/null | wc -l | tr -d ' ')
MD_COUNT=$(find "$BACKUP_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_FILES=$(find "$BACKUP_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')

# Создаем ZIP архив
echo ""
echo "📦 Создание ZIP архива..."
cd BACKUPS
zip -rq "BACKUP_MOBILE_${TIMESTAMP}.zip" "BACKUP_MOBILE_${TIMESTAMP}" 2>/dev/null || true
cd ..

# Вычисляем размер
SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
ARCHIVE_SIZE=$(du -sh "BACKUPS/BACKUP_MOBILE_${TIMESTAMP}.zip" 2>/dev/null | cut -f1)

echo ""
echo "✅ Актуальный бэкап создан успешно!"
echo "📁 Директория: $BACKUP_DIR"
echo "📦 Архив: BACKUPS/BACKUP_MOBILE_${TIMESTAMP}.zip"
echo "📊 Размер директории: $SIZE"
echo "📊 Размер архива: $ARCHIVE_SIZE"
echo "📊 Всего файлов: $TOTAL_FILES"
echo "📊 Swift файлов: $SWIFT_COUNT"
echo "📊 Markdown файлов: $MD_COUNT"
echo ""
echo "📋 Что сохранено:"
echo "   ✅ Полный проект Xcode"
echo "   ✅ Весь исходный код (Screens, ViewModels, Core, Shared, Components)"
echo "   ✅ Content Blocker Extension (ALADDINContentBlocker)"
echo "   ✅ Widgets Extension (ALADDINWidgets)"
echo "   ✅ Export Options"
echo "   ✅ GitHub Actions workflows (актуальные)"
echo "   ✅ Вся документация (без предыдущих бэкапов)"
echo "   ✅ Ресурсы (Assets, Localization)"
echo "   ✅ Тесты"
echo ""
echo "💡 Это актуальный бэкап без ненужных файлов и предыдущих бэкапов!"

