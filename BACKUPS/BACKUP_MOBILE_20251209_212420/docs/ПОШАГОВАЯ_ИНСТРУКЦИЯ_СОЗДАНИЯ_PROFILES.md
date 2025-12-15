# 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ: Создание Provisioning Profiles для App Store

## 🎯 ЦЕЛЬ
Создать manually managed provisioning profiles для:
- Основного приложения: `family.aladdin.ios`
- Расширения: `family.aladdin.ios.packetTunnel` (с Network Extensions и VPN)

**Team ID:** `6CJVBBUGSN`

---

## ШАГ 1: Проверить App ID для расширения

### 1.1. Откройте https://developer.apple.com/account
- Войдите с вашим Apple ID
- Перейдите в **Certificates, Identifiers & Profiles**

### 1.2. Проверьте App ID для расширения
1. В левом меню выберите **Identifiers**
2. Найдите или создайте App ID: `family.aladdin.ios.packetTunnel`
3. **ВАЖНО:** Проверьте что включены capabilities:
   - ✅ **Network Extensions** (обязательно!)
   - ✅ **Personal VPN** (обязательно!)

### 1.3. Если capabilities не включены:
1. Нажмите на App ID
2. Нажмите **Edit**
3. Включите:
   - ✅ **Network Extensions**
   - ✅ **Personal VPN**
4. Нажмите **Save**

---

## ШАГ 2: Создать Provisioning Profile для основного приложения

### 2.1. Перейдите в Profiles
1. В левом меню выберите **Profiles**
2. Нажмите **+** (создать новый профиль)

### 2.2. Выберите тип профиля
- Выберите **App Store** (Distribution)
- Нажмите **Continue**

### 2.3. Выберите App ID
- Найдите и выберите: **family.aladdin.ios**
- Нажмите **Continue**

### 2.4. Выберите сертификат
- Выберите сертификат **iPhone Distribution**
- Убедитесь что он соответствует Team ID: `6CJVBBUGSN`
- Нажмите **Continue**

### 2.5. Назовите профиль
- **Profile Name:** `ALADDIN App Store Distribution`
- Нажмите **Generate**

### 2.6. Скачайте профиль
- Нажмите **Download**
- Сохраните файл (например, `ALADDIN_App_Store.mobileprovision`)

---

## ШАГ 3: Создать Provisioning Profile для расширения

### 3.1. Создайте новый профиль
1. В **Profiles** нажмите **+**
2. Выберите **App Store** (Distribution)
3. Нажмите **Continue**

### 3.2. Выберите App ID для расширения
- Найдите и выберите: **family.aladdin.ios.packetTunnel**
- **ВАЖНО:** Убедитесь что у этого App ID включены:
  - ✅ Network Extensions
  - ✅ Personal VPN
- Нажмите **Continue**

### 3.3. Выберите сертификат
- Выберите тот же сертификат **iPhone Distribution**
- Нажмите **Continue**

### 3.4. Назовите профиль
- **Profile Name:** `ALADDINPacketTunnel App Store Distribution`
- Нажмите **Generate**

### 3.5. Скачайте профиль
- Нажмите **Download**
- Сохраните файл (например, `ALADDINPacketTunnel_App_Store.mobileprovision`)

---

## ШАГ 4: Конвертировать профили в Base64

### 4.1. Откройте Terminal

### 4.2. Конвертируйте основной профиль
```bash
base64 -i ~/Downloads/ALADDIN_App_Store.mobileprovision -o - | pbcopy
```
(или замените путь на место где вы сохранили файл)

### 4.3. Скопируйте результат
- Base64 строка скопирована в буфер обмена
- **Сохраните её** - понадобится для GitHub Secret

### 4.4. Конвертируйте профиль расширения
```bash
base64 -i ~/Downloads/ALADDINPacketTunnel_App_Store.mobileprovision -o - | pbcopy
```
(или замените путь на место где вы сохранили файл)

### 4.5. Скопируйте результат
- Base64 строка скопирована в буфер обмена
- **Сохраните её** - понадобится для GitHub Secret

---

## ШАГ 5: Обновить GitHub Secrets

### 5.1. Откройте GitHub репозиторий
1. Перейдите на https://github.com/ваш-username/ALADDIN_FAMILY
2. Нажмите **Settings**
3. В левом меню выберите **Secrets and variables** → **Actions**

### 5.2. Обновите PROVISIONING_PROFILE_APP
1. Найдите секрет **PROVISIONING_PROFILE_APP**
2. Нажмите **Update** (или создайте новый если нет)
3. Вставьте base64 строку из ШАГА 4.2
4. Нажмите **Update secret**

### 5.3. Обновите PROVISIONING_PROFILE_EXTENSION
1. Найдите секрет **PROVISIONING_PROFILE_EXTENSION**
2. Нажмите **Update** (или создайте новый если нет)
3. Вставьте base64 строку из ШАГА 4.4
4. Нажмите **Update secret**

### 5.4. Проверьте APPLE_TEAM_ID
1. Найдите секрет **APPLE_TEAM_ID**
2. Убедитесь что значение: `6CJVBBUGSN`
3. Если нет - обновите на `6CJVBBUGSN`

---

## ШАГ 6: Проверить сертификат

### 6.1. Проверьте IOS_DISTRIBUTION_CERTIFICATE
1. В GitHub Secrets найдите **IOS_DISTRIBUTION_CERTIFICATE**
2. Убедитесь что это base64 .p12 файла с сертификатом **iPhone Distribution**
3. Сертификат должен соответствовать Team ID: `6CJVBBUGSN`

### 6.2. Проверьте IOS_DISTRIBUTION_CERTIFICATE_PASSWORD
1. Найдите секрет **IOS_DISTRIBUTION_CERTIFICATE_PASSWORD**
2. Убедитесь что это правильный пароль для .p12 файла

---

## ШАГ 7: Запустить сборку

### 7.1. Запустите workflow
1. Перейдите в **Actions** в GitHub
2. Выберите workflow **Build and Upload to App Store**
3. Нажмите **Run workflow**
4. Выберите ветку (обычно `main` или `master`)
5. Нажмите **Run workflow**

### 7.2. Проверьте логи
1. Дождитесь выполнения шага **Setup Signing Certificate**
2. Проверьте что видите: `✅ Signing certificate installed and verified`
3. Проверьте шаг **Setup Provisioning Profiles**
4. Убедитесь что видите:
   - ✅ App provisioning profile installed with UUID: ...
   - ✅ Extension provisioning profile installed with UUID: ...
   - Для extension: ✅ Network Extensions: Supported, ✅ VPN API: Supported

---

## ✅ ЧЕКЛИСТ ПРОВЕРКИ

Перед запуском сборки убедитесь:

- [ ] App ID `family.aladdin.ios.packetTunnel` имеет включенные:
  - [ ] Network Extensions
  - [ ] Personal VPN
- [ ] Создан provisioning profile для `family.aladdin.ios` (App Store Distribution)
- [ ] Создан provisioning profile для `family.aladdin.ios.packetTunnel` (App Store Distribution)
- [ ] Оба профиля конвертированы в base64
- [ ] GitHub Secret `PROVISIONING_PROFILE_APP` обновлен
- [ ] GitHub Secret `PROVISIONING_PROFILE_EXTENSION` обновлен
- [ ] GitHub Secret `APPLE_TEAM_ID` = `6CJVBBUGSN`
- [ ] GitHub Secret `IOS_DISTRIBUTION_CERTIFICATE` установлен
- [ ] GitHub Secret `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD` установлен

---

## 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Provisioning profiles должны быть manually managed**
   - НЕ используйте "iOS Team Store Provisioning Profile" (это Xcode managed)
   - Создавайте профили вручную на developer.apple.com

2. **App ID для extension должен иметь правильные capabilities**
   - Network Extensions (обязательно!)
   - Personal VPN (обязательно!)

3. **Team ID должен совпадать везде**
   - В секрете `APPLE_TEAM_ID`: `6CJVBBUGSN`
   - В provisioning profiles: `6CJVBBUGSN`
   - В сертификате: `6CJVBBUGSN`

4. **Сертификат должен быть правильным**
   - "iPhone Distribution" (не "Apple Distribution")
   - Должен соответствовать Team ID
   - Должен иметь приватный ключ

---

## 📞 ЕСЛИ ВОЗНИКЛИ ПРОБЛЕМЫ

### Проблема: "Provisioning profile is Xcode managed"
**Решение:** Убедитесь что вы создали профиль вручную на developer.apple.com, а не использовали автоматически созданный Xcode.

### Проблема: "Network Extensions not supported"
**Решение:** 
1. Проверьте App ID для extension
2. Убедитесь что включены Network Extensions и Personal VPN
3. Пересоздайте provisioning profile после включения capabilities

### Проблема: "Team ID mismatch"
**Решение:** Убедитесь что везде используется один Team ID: `6CJVBBUGSN`

---

**Дата:** 28 ноября 2025  
**Team ID:** 6CJVBBUGSN  
**Bundle IDs:** 
- `family.aladdin.ios`
- `family.aladdin.ios.packetTunnel`

