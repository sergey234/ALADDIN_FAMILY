# 💾 Руководство по бэкапу настроек Xcode

**Дата создания:** 28 ноября 2025  
**Статус:** ✅ **Бэкап создан**

---

## 📦 Что сохранено в бэкапе

### ✅ Критичные файлы

1. **Настройки проекта Xcode**
   - `ALADDIN.xcodeproj/project.pbxproj` - **ГЛАВНЫЙ ФАЙЛ** со всеми настройками
   - Схемы сборки (`.xcscheme`)
   - Общие настройки (`xcshareddata/`)
   - Пользовательские настройки (`xcuserdata/`)

2. **Entitlements файлы**
   - `ALADDINPacketTunnel.entitlements` (Release)
   - `ALADDINPacketTunnelDebug.entitlements` (Debug)

3. **Export Options**
   - `ExportOptions.plist` - настройки экспорта IPA

4. **GitHub Actions**
   - `.github/workflows/appstore.yml` - workflow для автоматической сборки

5. **Provisioning Profiles**
   - Все `.mobileprovision` файлы из системы

6. **Документация**
   - Финальные отчеты и чеклисты

---

## 🔍 Что находится в `project.pbxproj`

Этот файл содержит **ВСЕ** настройки проекта:

- ✅ **Code Signing:**
  - Development Team: `6CJVBBUGSN`
  - Code Sign Style: `Automatic` (для ALADDIN), `Manual` (для ALADDINPacketTunnel Debug)
  - Provisioning Profile Specifier: `ALADDINPacketTunnel Dev.` (для Debug)

- ✅ **Bundle Identifiers:**
  - Main App: `family.aladdin.ios`
  - Extension: `family.aladdin.ios.packetTunnel`

- ✅ **Build Settings:**
  - Все флаги компиляции
  - Пути к файлам
  - Настройки таргетов

- ✅ **Targets и Schemes:**
  - Список всех таргетов
  - Зависимости между таргетами
  - Настройки сборки

---

## 📁 Расположение бэкапа

**Директория:** `BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/`  
**Архив:** `BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001.tar.gz`

---

## 🔄 Как восстановить настройки

### Вариант 1: Из директории бэкапа

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Распаковать архив (если нужно)
tar -xzf BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001.tar.gz

# Скопировать файлы обратно
cp -R BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/ALADDIN.xcodeproj/* ALADDIN.xcodeproj/
cp BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/Entitlements/* .
cp BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/ExportOptions.plist .
cp -R BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/.github .
```

### Вариант 2: Только критичные файлы

Если нужно восстановить только самое важное:

```bash
# 1. Восстановить project.pbxproj (ГЛАВНЫЙ ФАЙЛ)
cp BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/ALADDIN.xcodeproj/project.pbxproj \
   ALADDIN.xcodeproj/project.pbxproj

# 2. Восстановить Entitlements
cp BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/Entitlements/* .

# 3. Открыть проект в Xcode
open ALADDIN.xcodeproj
```

---

## ⚠️ Важные замечания

### 1. Provisioning Profiles

Provisioning profiles могут **истечь** или стать недействительными. После восстановления:

1. Откройте проект в Xcode
2. Перейдите в **Signing & Capabilities** для каждого таргета
3. Проверьте статус provisioning profiles
4. При необходимости обновите профили:
   - Xcode → Preferences → Accounts → Download Manual Profiles

### 2. Xcode User Data

Файлы `xcuserdata/` могут отличаться на разных машинах. Это нормально - они содержат личные настройки разработчика.

### 3. Certificates

Сертификаты **НЕ** включены в бэкап (они хранятся в Keychain). Если нужно восстановить:

1. Экспортировать сертификаты из Keychain на исходной машине
2. Импортировать на новую машину
3. Или использовать Automatic Signing (Xcode создаст новые)

---

## 🎯 Что делать после восстановления

1. **Открыть проект в Xcode:**
   ```bash
   open ALADDIN.xcodeproj
   ```

2. **Проверить настройки:**
   - Выбрать таргет `ALADDIN` → **Signing & Capabilities**
   - Проверить, что Team: `6CJVBBUGSN`
   - Проверить, что Code Sign Style: `Automatic`
   - Выбрать таргет `ALADDINPacketTunnel` → **Signing & Capabilities**
   - Проверить, что для Debug: `Manual` с профилем `ALADDINPacketTunnel Dev.`

3. **Проверить Entitlements:**
   - Убедиться, что файлы `ALADDINPacketTunnel.entitlements` и `ALADDINPacketTunnelDebug.entitlements` на месте
   - Проверить, что они подключены в Build Settings → Code Signing Entitlements

4. **Попробовать собрать проект:**
   ```bash
   xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN clean build
   ```

5. **Если есть ошибки с provisioning profiles:**
   - Обновить профили в Xcode (см. выше)
   - Или пересоздать в Apple Developer Portal

---

## 📋 Чеклист после восстановления

- [ ] Проект открывается в Xcode без ошибок
- [ ] Все таргеты видны в списке
- [ ] Signing & Capabilities настроены правильно
- [ ] Entitlements файлы подключены
- [ ] Проект собирается без ошибок (`BUILD SUCCEEDED`)
- [ ] Provisioning profiles актуальны
- [ ] Archive создается успешно

---

## 🔄 Создание нового бэкапа

Если нужно создать новый бэкап:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./BACKUPS/create_xcode_settings_backup.sh
```

Скрипт автоматически:
- Создаст новую директорию с timestamp
- Скопирует все важные файлы
- Создаст архив `.tar.gz`
- Добавит README с описанием

---

## ✅ Итог

**Все настройки Xcode сохранены в бэкапе!**

Главный файл - `project.pbxproj` - содержит все настройки проекта, включая:
- Code Signing
- Bundle IDs
- Build Settings
- Targets и Schemes
- Entitlements paths

**Даже если все остальное потеряется, восстановление из `project.pbxproj` вернет 95% настроек.**

---

**Дата создания бэкапа:** 28 ноября 2025, 16:40  
**Расположение:** `BACKUPS/BACKUP_XCODE_SETTINGS_20251128_164001/`

