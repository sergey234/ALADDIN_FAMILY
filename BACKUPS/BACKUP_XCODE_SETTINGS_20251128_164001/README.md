# Бэкап настроек Xcode и проекта ALADDIN

## Дата создания
Fri Nov 28 16:40:02 +04 2025

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
