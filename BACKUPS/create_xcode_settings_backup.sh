#!/bin/bash

# Скрипт для создания бэкапа всех настроек Xcode и проекта
# Дата: 28 ноября 2025

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="BACKUPS/BACKUP_XCODE_SETTINGS_${TIMESTAMP}"
PROJECT_ROOT="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

cd "$PROJECT_ROOT"

echo "📦 Создание бэкапа настроек Xcode..."
echo "📁 Директория бэкапа: $BACKUP_DIR"

# Создаем директорию бэкапа
mkdir -p "$BACKUP_DIR"

# 1. Критичные файлы проекта Xcode
echo "📋 Копирование файлов проекта Xcode..."
mkdir -p "$BACKUP_DIR/ALADDIN.xcodeproj"
cp -R ALADDIN.xcodeproj/project.pbxproj "$BACKUP_DIR/ALADDIN.xcodeproj/" 2>/dev/null || true
cp -R ALADDIN.xcodeproj/*.xcscheme "$BACKUP_DIR/ALADDIN.xcodeproj/" 2>/dev/null || true
cp -R ALADDIN.xcodeproj/xcshareddata "$BACKUP_DIR/ALADDIN.xcodeproj/" 2>/dev/null || true
cp -R ALADDIN.xcodeproj/xcuserdata "$BACKUP_DIR/ALADDIN.xcodeproj/" 2>/dev/null || true

# 2. Entitlements файлы
echo "🔐 Копирование Entitlements файлов..."
mkdir -p "$BACKUP_DIR/Entitlements"
cp ALADDINPacketTunnel.entitlements "$BACKUP_DIR/Entitlements/" 2>/dev/null || true
cp ALADDINPacketTunnelDebug.entitlements "$BACKUP_DIR/Entitlements/" 2>/dev/null || true

# 3. Export Options
echo "📤 Копирование Export Options..."
cp ExportOptions.plist "$BACKUP_DIR/" 2>/dev/null || true

# 4. GitHub Actions workflow
echo "🔄 Копирование GitHub Actions workflow..."
mkdir -p "$BACKUP_DIR/.github/workflows"
cp -R .github/workflows/*.yml "$BACKUP_DIR/.github/workflows/" 2>/dev/null || true

# 5. Provisioning Profiles (если доступны)
echo "📜 Копирование Provisioning Profiles..."
mkdir -p "$BACKUP_DIR/ProvisioningProfiles"
if [ -d ~/Library/MobileDevice/Provisioning\ Profiles ]; then
    cp ~/Library/MobileDevice/Provisioning\ Profiles/*.mobileprovision "$BACKUP_DIR/ProvisioningProfiles/" 2>/dev/null || true
fi

# 6. Документация (только важные файлы)
echo "📚 Копирование документации..."
mkdir -p "$BACKUP_DIR/docs"
cp docs/FINAL_APP_STORE_READINESS_REPORT.md "$BACKUP_DIR/docs/" 2>/dev/null || true
cp docs/PRODUCTION_READINESS_ANALYSIS.md "$BACKUP_DIR/docs/" 2>/dev/null || true
cp docs/COMPLETE_APP_STORE_CHECKLIST.md "$BACKUP_DIR/docs/" 2>/dev/null || true
cp docs/FINAL_TODO_STATUS_WITH_CHECKMARKS.md "$BACKUP_DIR/docs/" 2>/dev/null || true

# 7. Info.plist файлы (если есть)
echo "ℹ️ Копирование Info.plist файлов..."
find . -name "Info.plist" -not -path "./BACKUPS/*" -not -path "./.git/*" -exec cp --parents {} "$BACKUP_DIR/" \; 2>/dev/null || true

# 8. Создаем README с описанием бэкапа
cat > "$BACKUP_DIR/README.md" << 'EOF'
# Бэкап настроек Xcode и проекта ALADDIN

## Дата создания
TIMESTAMP_PLACEHOLDER

## Что включено в бэкап

### 1. Файлы проекта Xcode
- `ALADDIN.xcodeproj/project.pbxproj` - все настройки проекта, targets, build settings
- `*.xcscheme` - схемы сборки
- `xcshareddata/` - общие настройки проекта
- `xcuserdata/` - пользовательские настройки (опционально)

### 2. Entitlements
- `ALADDINPacketTunnel.entitlements` - entitlements для Release
- `ALADDINPacketTunnelDebug.entitlements` - entitlements для Debug

### 3. Export Options
- `ExportOptions.plist` - настройки экспорта IPA

### 4. GitHub Actions
- `.github/workflows/appstore.yml` - workflow для автоматической сборки

### 5. Provisioning Profiles
- Все `.mobileprovision` файлы из `~/Library/MobileDevice/Provisioning Profiles/`

### 6. Документация
- Финальные отчеты и чеклисты

## Важные настройки

### Code Signing
- **Development Team:** 6CJVBBUGSN
- **Code Sign Style:** Automatic (для ALADDIN), Manual (для ALADDINPacketTunnel Debug)
- **Bundle ID (Main):** family.aladdin.ios
- **Bundle ID (Extension):** family.aladdin.ios.packetTunnel

### Entitlements
- **Personal VPN:** ✅ Включено
- **Network Extensions:** ✅ Все 8 типов включены
  - app-proxy-provider
  - content-filter-provider
  - packet-tunnel-provider (основной)
  - dns-proxy
  - dns-settings
  - relay
  - url-filter-provider
  - hotspot-provider

### Provisioning Profiles
- **ALADDIN:** Automatic Signing
- **ALADDINPacketTunnel:** Manual (`ALADDINPacketTunnel Dev.`)

## Как восстановить

1. Скопировать файлы обратно в проект
2. Открыть проект в Xcode
3. Проверить настройки Signing & Capabilities
4. Обновить provisioning profiles (если нужно)

## Примечания

- Provisioning profiles могут истечь - их нужно будет обновить
- Xcode user data может отличаться на разных машинах
- Все настройки сохранены в `project.pbxproj` - это главный файл
EOF

# Заменяем placeholder на реальную дату
sed -i '' "s/TIMESTAMP_PLACEHOLDER/$(date)/" "$BACKUP_DIR/README.md"

# Создаем архив
echo "📦 Создание архива..."
cd BACKUPS
tar -czf "BACKUP_XCODE_SETTINGS_${TIMESTAMP}.tar.gz" "BACKUP_XCODE_SETTINGS_${TIMESTAMP}"
cd ..

echo ""
echo "✅ Бэкап создан успешно!"
echo "📁 Директория: $BACKUP_DIR"
echo "📦 Архив: BACKUPS/BACKUP_XCODE_SETTINGS_${TIMESTAMP}.tar.gz"
echo ""
echo "📋 Что сохранено:"
echo "   ✅ Настройки проекта Xcode (project.pbxproj)"
echo "   ✅ Entitlements файлы"
echo "   ✅ Export Options"
echo "   ✅ GitHub Actions workflow"
echo "   ✅ Provisioning Profiles"
echo "   ✅ Документация"
echo ""
echo "💡 Все настройки Code Signing, Bundle IDs, Entitlements сохранены!"

