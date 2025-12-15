# 🔧 ИСПРАВЛЕНИЕ ОШИБОК СБОРКИ ДЛЯ APP STORE

## 🚨 ПРОБЛЕМЫ

При сборке архива в GitHub Actions возникают следующие ошибки:

1. **Нет сертификата "iOS Distribution"**
   ```
   error: No signing certificate "iOS Distribution" found: No "iOS Distribution" signing certificate matching team ID "***" with a private key was found.
   ```

2. **Provisioning profile принадлежит другой команде**
   ```
   error: Provisioning profile "iOS Team Store Provisioning Profile: family.aladdin.ios" belongs to team "SERGEY KHLYSTOV", which does not match the selected team "***".
   ```

3. **Provisioning profile управляется Xcode**
   ```
   error: Provisioning profile "iOS Team Store Provisioning Profile: family.aladdin.ios" is Xcode managed, but signing settings require a manually managed profile.
   ```

4. **Для ALADDINPacketTunnel нет поддержки Network Extensions**
   ```
   error: Provisioning profile "iOS Team Store Provisioning Profile: family.aladdin.ios" doesn't support the Network Extensions and Personal VPN capability.
   ```

---

## ✅ РЕШЕНИЕ

### Шаг 1: Получить правильные Provisioning Profiles

**Проблема:** Используются Xcode managed profiles, которые не работают с manual signing.

**Решение:** Нужно скачать **manually managed** profiles с developer.apple.com:

1. **Откройте https://developer.apple.com/account**
2. **Перейдите в Certificates, Identifiers & Profiles**
3. **Для основного приложения (ALADDIN):**
   - Profiles → + (создать новый)
   - Выберите "App Store" distribution profile
   - Выберите App ID: `family.aladdin.ios`
   - Выберите сертификат "iPhone Distribution"
   - Назовите профиль (например, "ALADDIN App Store")
   - Скачайте профиль

4. **Для расширения (ALADDINPacketTunnel):**
   - Profiles → + (создать новый)
   - Выберите "App Store" distribution profile
   - Выберите App ID: `family.aladdin.ios.packetTunnel`
   - **ВАЖНО:** Убедитесь что App ID имеет включенные capabilities:
     - ✅ Network Extensions
     - ✅ Personal VPN
   - Выберите сертификат "iPhone Distribution"
   - Назовите профиль (например, "ALADDINPacketTunnel App Store")
   - Скачайте профиль

### Шаг 2: Конвертировать Profiles в Base64

После скачивания профилей, конвертируйте их в base64 для GitHub Secrets:

```bash
# Для основного приложения
base64 -i ~/Downloads/ALADDIN_App_Store.mobileprovision -o - | pbcopy

# Для расширения
base64 -i ~/Downloads/ALADDINPacketTunnel_App_Store.mobileprovision -o - | pbcopy
```

### Шаг 3: Обновить GitHub Secrets

Обновите секреты в GitHub:

1. **Settings → Secrets and variables → Actions**
2. **Обновите следующие секреты:**

   - `PROVISIONING_PROFILE_APP` - вставьте base64 основного профиля
   - `PROVISIONING_PROFILE_EXTENSION` - вставьте base64 профиля расширения
   - `IOS_DISTRIBUTION_CERTIFICATE` - убедитесь что это правильный сертификат
   - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD` - пароль для .p12 файла
   - `APPLE_TEAM_ID` - должен соответствовать команде в профилях

### Шаг 4: Проверить App ID для Extension

**ВАЖНО:** Убедитесь что App ID `family.aladdin.ios.packetTunnel` имеет включенные capabilities:

1. **Откройте https://developer.apple.com/account**
2. **Identifiers → App IDs**
3. **Найдите `family.aladdin.ios.packetTunnel`**
4. **Проверьте что включены:**
   - ✅ Network Extensions
   - ✅ Personal VPN

Если не включены:
- Нажмите "Edit"
- Включите нужные capabilities
- Сохраните
- **Пересоздайте provisioning profile** для расширения

---

## 🔍 ПРОВЕРКА

После обновления секретов, workflow автоматически проверит:

1. ✅ **Сертификат установлен** - проверит наличие "iPhone Distribution" в keychain
2. ✅ **Provisioning profiles правильные** - проверит:
   - Team ID соответствует
   - Bundle ID правильный
   - Для extension: поддержка Network Extensions и VPN API
   - Не являются Xcode managed

---

## 📋 ЧТО ИЗМЕНЕНО В WORKFLOW

### 1. Улучшена установка сертификата:
- ✅ Проверка что сертификат действительно установлен
- ✅ Показ доступных сертификатов при ошибке
- ✅ Ошибка если сертификат не найден (вместо fallback на automatic)

### 2. Добавлена проверка provisioning profiles:
- ✅ Проверка Team ID
- ✅ Проверка Bundle ID
- ✅ Проверка поддержки Network Extensions для extension
- ✅ Проверка что profiles не Xcode managed
- ✅ Детальная информация о профилях в логах

### 3. Улучшена обработка ошибок:
- ✅ Четкие сообщения об ошибках
- ✅ Проверка всех необходимых параметров перед сборкой
- ✅ Очистка keychain после сборки

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Provisioning profiles должны быть manually managed**
   - Не используйте "iOS Team Store Provisioning Profile"
   - Создавайте профили вручную на developer.apple.com

2. **App ID для extension должен иметь правильные capabilities**
   - Network Extensions
   - Personal VPN

3. **Team ID должен совпадать**
   - В секрете `APPLE_TEAM_ID`
   - В provisioning profiles
   - В сертификате

4. **Сертификат должен быть правильным**
   - "iPhone Distribution" (не "Apple Distribution")
   - Должен соответствовать Team ID
   - Должен иметь приватный ключ

---

## 🎯 БЫСТРАЯ ПРОВЕРКА

После обновления секретов, запустите workflow и проверьте логи:

1. ✅ **Setup Signing Certificate** - должен показать установленный сертификат
2. ✅ **Setup Provisioning Profiles** - должен показать информацию о профилях:
   - Team: правильная команда
   - Bundle ID: правильный
   - Для extension: ✅ Network Extensions: Supported, ✅ VPN API: Supported
3. ✅ **Build Archive** - должен собрать архив без ошибок

---

## 📝 ПРИМЕР ПРАВИЛЬНЫХ ПРОФИЛЕЙ

### Основной профиль (ALADDIN):
- **Type:** App Store Distribution
- **App ID:** `family.aladdin.ios`
- **Certificate:** iPhone Distribution
- **Team:** Ваша команда (не "SERGEY KHLYSTOV")
- **Managed:** Manual (не Xcode managed)

### Профиль расширения (ALADDINPacketTunnel):
- **Type:** App Store Distribution
- **App ID:** `family.aladdin.ios.packetTunnel` (с Network Extensions и VPN)
- **Certificate:** iPhone Distribution
- **Team:** Ваша команда (не "SERGEY KHLYSTOV")
- **Managed:** Manual (не Xcode managed)
- **Capabilities:** ✅ Network Extensions, ✅ Personal VPN

---

**Дата:** 28 ноября 2025  
**Статус:** Исправлено в workflow, требуется обновление секретов

