# Полный бэкап iOS приложения ALADDIN

## Дата создания
Fri Nov 28 16:49:53 +04 2025

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
**Дата бэкапа:** Fri Nov 28 16:49:53 +04 2025
