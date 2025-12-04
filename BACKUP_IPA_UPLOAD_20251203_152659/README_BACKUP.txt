# 📦 БЭКАП ВАЖНЫХ ФАЙЛОВ ДЛЯ ОТПРАВКИ IPA

Дата создания: $(date)
Проект: ALADDIN iOS

## 📋 СОДЕРЖИМОЕ БЭКАПА

### 1. GitHub Actions Workflows
- .github/workflows/check-secrets.yml - основной workflow для сборки и загрузки IPA
- .github/workflows/upload-ipa-only.yml - альтернативный workflow для загрузки IPA

### 2. Конфигурация экспорта
- ExportOptions.plist - настройки экспорта IPA для App Store

### 3. Настройки проекта
- ALADDIN.xcodeproj/project.pbxproj - настройки проекта Xcode (build number, версия, bundle ID)

## 🔄 КАК ВОССТАНОВИТЬ

1. Скопировать файлы обратно в проект:
   cp -r .github/workflows/* /путь/к/проекту/.github/workflows/
   cp ExportOptions.plist /путь/к/проекту/
   cp ALADDIN.xcodeproj/project.pbxproj /путь/к/проекту/ALADDIN.xcodeproj/

2. Проверить GitHub Secrets (не в бэкапе, настраиваются отдельно):
   - APP_STORE_CONNECT_API_KEY
   - APP_STORE_CONNECT_ISSUER_ID
   - APP_STORE_CONNECT_API_KEY_ID
   - PROVISIONING_PROFILE_APP
   - PROVISIONING_PROFILE_EXTENSION
   - APPLE_DISTRIBUTION_CERTIFICATE
   - APPLE_DISTRIBUTION_CERTIFICATE_PASSWORD

## ⚠️ ВАЖНО

- GitHub Secrets НЕ включены в бэкап (безопасность)
- Provisioning profiles НЕ включены (хранятся в GitHub Secrets)
- Сертификаты НЕ включены (хранятся в GitHub Secrets)

## 📊 ТЕКУЩИЕ НАСТРОЙКИ

- Версия: 1.0.0
- Build number: 3
- Bundle ID: family.aladdin.ios
- Team ID: 6CJVBBUGSN
