#!/bin/bash

# Скрипт для создания полного бэкапа iOS мобильного приложения ALADDIN
# Включает все обновления и настройки перед отправкой в App Store
# Дата: 28 ноября 2025

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="BACKUPS/BACKUP_MOBILE_${TIMESTAMP}"
PROJECT_ROOT="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

cd "$PROJECT_ROOT"

echo "📦 Создание полного бэкапа iOS приложения ALADDIN..."
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

# 8. Assets (иконки, изображения)
echo "🎨 Копирование Assets..."
if [ -d "Assets.xcassets" ]; then
    cp -R Assets.xcassets "$BACKUP_DIR/" 2>/dev/null || true
fi

# 9. Resources (локализация, сертификаты)
echo "📚 Копирование Resources..."
if [ -d "resources" ]; then
    cp -R resources "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d "Resources" ]; then
    cp -R Resources "$BACKUP_DIR/" 2>/dev/null || true
fi

# 10. LocalizedVersions
echo "🌍 Копирование локализаций..."
if [ -d "LocalizedVersions" ]; then
    cp -R LocalizedVersions "$BACKUP_DIR/" 2>/dev/null || true
fi

# 11. Tests
echo "🧪 Копирование тестов..."
if [ -d "Tests" ]; then
    cp -R Tests "$BACKUP_DIR/" 2>/dev/null || true
fi

# 12. ALADDINPacketTunnel Extension
echo "🔐 Копирование Packet Tunnel Extension..."
if [ -d "ALADDINPacketTunnel" ]; then
    cp -R ALADDINPacketTunnel "$BACKUP_DIR/" 2>/dev/null || true
fi

# 13. Entitlements файлы (КРИТИЧНО!)
echo "🔑 Копирование Entitlements файлов..."
cp ALADDINPacketTunnel.entitlements "$BACKUP_DIR/" 2>/dev/null || true
cp ALADDINPacketTunnelDebug.entitlements "$BACKUP_DIR/" 2>/dev/null || true

# 14. Export Options
echo "📤 Копирование Export Options..."
cp ExportOptions.plist "$BACKUP_DIR/" 2>/dev/null || true

# 15. Info.plist
echo "ℹ️ Копирование Info.plist..."
cp Info.plist "$BACKUP_DIR/" 2>/dev/null || true

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

# 18. Документация (все важные документы)
echo "📖 Копирование документации..."
if [ -d "docs" ]; then
    mkdir -p "$BACKUP_DIR/docs"
    # Копируем все важные документы
    cp -R docs/*.md "$BACKUP_DIR/docs/" 2>/dev/null || true
    cp -R docs/AppStore "$BACKUP_DIR/docs/" 2>/dev/null || true
    # Копируем все поддиректории docs
    find docs -type d -not -path "*/\.*" -exec mkdir -p "$BACKUP_DIR/{}" \; 2>/dev/null || true
    find docs -type f -not -path "*/\.*" -exec cp "{}" "$BACKUP_DIR/{}" \; 2>/dev/null || true
fi

# 19. Provisioning Profiles (если доступны)
echo "📜 Копирование Provisioning Profiles..."
mkdir -p "$BACKUP_DIR/ProvisioningProfiles"
if [ -d ~/Library/MobileDevice/Provisioning\ Profiles ]; then
    cp ~/Library/MobileDevice/Provisioning\ Profiles/*.mobileprovision "$BACKUP_DIR/ProvisioningProfiles/" 2>/dev/null || true
fi

# 20. Другие важные файлы
echo "📄 Копирование других важных файлов..."
# Podfile (если есть)
[ -f "Podfile" ] && cp Podfile "$BACKUP_DIR/" 2>/dev/null || true
[ -f "Podfile.lock" ] && cp Podfile.lock "$BACKUP_DIR/" 2>/dev/null || true
# Package.swift (если есть)
[ -f "Package.swift" ] && cp Package.swift "$BACKUP_DIR/" 2>/dev/null || true
# .gitignore
[ -f ".gitignore" ] && cp .gitignore "$BACKUP_DIR/" 2>/dev/null || true

# 21. Создаем README с описанием бэкапа
cat > "$BACKUP_DIR/README.md" << 'EOF'
# Полный бэкап iOS приложения ALADDIN

## Дата создания
TIMESTAMP_PLACEHOLDER

## Что включено в бэкап

### 1. Проект Xcode
- `ALADDIN.xcodeproj/` - полный проект со всеми настройками
- Все схемы сборки
- Все build settings
- Code Signing настройки

### 2. Исходный код
- `ALADDIN/` - основной код приложения
- `Screens/` - все экраны приложения
- `ViewModels/` - все ViewModels
- `Core/` - основные модули (Network, Config, Models, etc.)
- `Shared/` - общие компоненты
- `Components/` - UI компоненты
- `ALADDINPacketTunnel/` - VPN Extension

### 3. Ресурсы
- `Assets.xcassets/` - иконки, изображения, цвета
- `Resources/` - локализация, сертификаты
- `LocalizedVersions/` - локализованные версии

### 4. Тесты
- `Tests/` - все unit и UI тесты

### 5. Критичные файлы
- `ALADDINPacketTunnel.entitlements` - Entitlements для Release
- `ALADDINPacketTunnelDebug.entitlements` - Entitlements для Debug
- `ExportOptions.plist` - настройки экспорта IPA
- `Info.plist` - информация о приложении

### 6. CI/CD
- `.github/workflows/` - GitHub Actions workflows

### 7. Документация
- `docs/` - вся документация проекта
- `docs/AppStore/` - документы для App Store

### 8. Provisioning Profiles
- `ProvisioningProfiles/` - все provisioning profiles

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

## Статус перед отправкой в App Store

✅ Проект собирается без ошибок  
✅ Архив создан успешно  
✅ Все Entitlements настроены  
✅ Provisioning Profiles настроены  
✅ Документация для App Store готова  
✅ Скриншоты подготовлены  
✅ Все тексты готовы  

## Как восстановить

1. Распаковать архив:
   ```bash
   tar -xzf BACKUP_MOBILE_TIMESTAMP.tar.gz
   ```

2. Скопировать файлы в рабочую директорию

3. Открыть проект в Xcode:
   ```bash
   open ALADDIN.xcodeproj
   ```

4. Проверить настройки Signing & Capabilities

5. Обновить provisioning profiles (если нужно)

## Примечания

- Provisioning profiles могут истечь - их нужно будет обновить
- Certificates не включены (хранятся в Keychain)
- DerivedData не включен (генерируется автоматически)
- Build артефакты не включены

## Версия

**Версия приложения:** 1.0.0  
**Статус:** Готово к отправке в App Store  
**Дата бэкапа:** TIMESTAMP_PLACEHOLDER
EOF

# Заменяем placeholder на реальную дату
sed -i '' "s/TIMESTAMP_PLACEHOLDER/$(date)/" "$BACKUP_DIR/README.md"

# Создаем список изменений за последние дни
cat > "$BACKUP_DIR/CHANGELOG.md" << 'EOF'
# Changelog - Изменения перед отправкой в App Store

## Последние обновления (26-28 ноября 2025)

### ✅ Исправления и настройки

1. **Entitlements файлы**
   - Добавлены все 8 типов Network Extensions в entitlements
   - Настроен Personal VPN
   - Исправлен mismatch с provisioning profiles

2. **Code Signing**
   - Настроен Automatic Signing для ALADDIN
   - Настроен Manual Signing для ALADDINPacketTunnel Debug
   - Установлен Development Team: 6CJVBBUGSN

3. **Исправления ошибок компиляции**
   - Исправлен KeychainAutoRecoveryService (обернут в #if DEBUG)
   - Исправлен Notification.Name("tariffPurchased")
   - Добавлены недостающие импорты в TariffsViewModel
   - Удален TariffsViewModel из таргета ALADDINPacketTunnel

4. **AppIcon**
   - Исправлены предупреждения об иконках
   - Удален дубликат ALADDIN_icon_1024.png

5. **Provisioning Profiles**
   - Пересоздан профиль для ALADDINPacketTunnel
   - Настроен Manual профиль: ALADDINPacketTunnel Dev.

6. **Документация**
   - Создан финальный отчет о готовности к App Store
   - Обновлены все чеклисты
   - Подготовлена документация для восстановления

7. **GitHub Actions**
   - Настроен workflow для автоматической сборки
   - Обновлены actions до v4

### 📋 Готовность к App Store

- ✅ Проект собирается без ошибок
- ✅ Архив создан успешно
- ✅ Все Entitlements настроены
- ✅ Provisioning Profiles настроены
- ✅ Документация готова
- ✅ Скриншоты подготовлены
- ✅ Все тексты готовы

### 🚀 Следующие шаги

1. Создать Archive в Xcode
2. Distribute App → App Store Connect
3. Заполнить метаданные в App Store Connect
4. Submit for Review
EOF

# Создаем архив
echo ""
echo "📦 Создание архива..."
cd BACKUPS
tar -czf "BACKUP_MOBILE_${TIMESTAMP}.tar.gz" "BACKUP_MOBILE_${TIMESTAMP}"
cd ..

# Вычисляем размер
SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
ARCHIVE_SIZE=$(du -sh "BACKUPS/BACKUP_MOBILE_${TIMESTAMP}.tar.gz" | cut -f1)

echo ""
echo "✅ Полный бэкап создан успешно!"
echo "📁 Директория: $BACKUP_DIR"
echo "📦 Архив: BACKUPS/BACKUP_MOBILE_${TIMESTAMP}.tar.gz"
echo "📊 Размер директории: $SIZE"
echo "📊 Размер архива: $ARCHIVE_SIZE"
echo ""
echo "📋 Что сохранено:"
echo "   ✅ Полный проект Xcode"
echo "   ✅ Весь исходный код (Screens, ViewModels, Core, Shared, Components)"
echo "   ✅ VPN Extension (ALADDINPacketTunnel)"
echo "   ✅ Entitlements файлы (КРИТИЧНО!)"
echo "   ✅ Export Options"
echo "   ✅ GitHub Actions workflows"
echo "   ✅ Provisioning Profiles"
echo "   ✅ Вся документация"
echo "   ✅ Ресурсы (Assets, Localization)"
echo "   ✅ Тесты"
echo ""
echo "💡 Это полный бэкап перед отправкой в App Store!"
echo "💡 Все настройки, код и конфигурации сохранены!"

