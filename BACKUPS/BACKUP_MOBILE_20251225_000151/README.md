# Полный бэкап iOS приложения ALADDIN

## Дата создания
Thu Dec 25 00:02:02 +04 2025

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
- `Core/` - основные модули (Network, Config, Models, Security, ContentBlocker, etc.)
- `Shared/` - общие компоненты
- `Components/` - UI компоненты
- `ALADDINContentBlocker/` - Content Blocker Extension (актуальный)
- `ALADDINWidgets/` - Widgets Extension

### 3. Ресурсы
- `Assets.xcassets/` - иконки, изображения, цвета
- `Resources/` - локализация, сертификаты
- `LocalizedVersions/` - локализованные версии

### 4. Тесты
- `Tests/` - все unit и UI тесты

### 5. Критичные файлы
- `ExportOptions.plist` - настройки экспорта IPA
- `ALADDINApp.swift` - точка входа приложения

### 6. CI/CD
- `.github/workflows/` - GitHub Actions workflows
  - `check-secrets.yml` - актуальный workflow для проверки секретов
  - `appstore.yml` - workflow для сборки App Store
  - другие workflows

### 7. Документация
- `docs/` - важная документация проекта
- `docs/AppStore/` - документы для App Store

### 8. Fastlane
- `fastlane/` - конфигурация Fastlane для автоматизации

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
   ```bash
   unzip BACKUP_MOBILE_20251225_000151.zip
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
- Предыдущие бэкапы не включены

## Версия

**Версия приложения:** 1.0.0  
**Статус:** Готово к отправке в App Store  
**Дата бэкапа:** Thu Dec 25 00:02:02 +04 2025
