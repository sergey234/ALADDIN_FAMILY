# 📥 КАК СКАЧАТЬ MANUALLY MANAGED PROVISIONING PROFILES

**Дата:** 29 ноября 2025  
**Проблема:** Текущие profiles являются "Xcode managed", а нужны "manually managed"

---

## 🎯 ЦЕЛЬ

Скачать **manually managed** provisioning profiles с developer.apple.com для использования в GitHub Actions.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Открыть Developer Portal

1. **Открыть браузер:**
   - Перейти на: https://developer.apple.com/account/resources/profiles/list
   - Войти с Apple ID: `sergey21-02-84@list.ru`

2. **Проверить, что вы вошли:**
   - Должна быть видна страница "Certificates, Identifiers & Profiles"
   - В левом меню выбрать "Profiles"

---

### Шаг 2: Найти существующие профили

1. **Проверить существующие профили:**
   - В списке найти профили для:
     - `family.aladdin.ios` (основное приложение)
     - `family.aladdin.ios.packetTunnel` (Network Extension)

2. **Проверить тип профиля:**
   - Если профиль называется "iOS Team Store Provisioning Profile" → это **Xcode managed** ❌
   - Если профиль называется "App Store" или "Distribution" → это может быть **manually managed** ✅

---

### Шаг 3: Создать новые manually managed профили (если нет)

Если существующие профили являются Xcode managed, нужно создать новые:

#### 3.1: Создать профиль для основного приложения

1. **Нажать "+" (Create a new provisioning profile):**
   - Вверху страницы нажать кнопку "+"

2. **Выбрать тип:**
   - Выбрать "App Store" (для Distribution)
   - Нажать "Continue"

3. **Выбрать App ID:**
   - Выбрать `family.aladdin.ios`
   - Нажать "Continue"

4. **Выбрать сертификат:**
   - Выбрать "Apple Distribution" сертификат
   - Нажать "Continue"

5. **Ввести название:**
   - **Profile Name:** `ALADDIN App Store Distribution`
   - Нажать "Generate"

6. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл (например, `ALADDIN_AppStore.mobileprovision`)

#### 3.2: Создать профиль для Network Extension

1. **Нажать "+" (Create a new provisioning profile):**

2. **Выбрать тип:**
   - Выбрать "App Store" (для Distribution)
   - Нажать "Continue"

3. **Выбрать App ID:**
   - Выбрать `family.aladdin.ios.packetTunnel`
   - Нажать "Continue"

4. **Выбрать сертификат:**
   - Выбрать "Apple Distribution" сертификат
   - Нажать "Continue"

5. **Ввести название:**
   - **Profile Name:** `ALADDIN PacketTunnel App Store Distribution`
   - Нажать "Generate"

6. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл (например, `ALADDIN_PacketTunnel_AppStore.mobileprovision`)

---

### Шаг 4: Проверить, что профили manually managed

1. **Открыть скачанные файлы:**
   - Двойной клик на `.mobileprovision` файл
   - Откроется в Xcode или TextEdit

2. **Проверить содержимое:**
   - Открыть в TextEdit
   - Найти строку `<key>Name</key>`
   - Проверить, что название **НЕ** содержит "iOS Team" или "Xcode Managed"
   - Должно быть что-то вроде "ALADDIN App Store Distribution"

---

### Шаг 5: Закодировать в base64

1. **Открыть Terminal:**
   - Cmd+Space → ввести "Terminal" → Enter

2. **Перейти в папку с профилями:**
   ```bash
   cd ~/Downloads  # или где вы сохранили профили
   ```

3. **Закодировать основной профиль:**
   ```bash
   base64 -i ALADDIN_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/app_profile_manual_base64.txt
   ```

4. **Закодировать профиль для Extension:**
   ```bash
   base64 -i ALADDIN_PacketTunnel_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/extension_profile_manual_base64.txt
   ```

---

### Шаг 6: Обновить GitHub Secrets

1. **Открыть GitHub:**
   - https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Обновить PROVISIONING_PROFILE_APP:**
   - Найти `PROVISIONING_PROFILE_APP`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/app_profile_manual_base64.txt`
   - Скопировать всё содержимое (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

3. **Обновить PROVISIONING_PROFILE_EXTENSION:**
   - Найти `PROVISIONING_PROFILE_EXTENSION`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/extension_profile_manual_base64.txt`
   - Скопировать всё содержимое (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

---

## ✅ ПРОВЕРКА

### Что должно быть:

1. **В Developer Portal:**
   - ✅ Профили созданы с названиями "ALADDIN App Store Distribution"
   - ✅ Профили **НЕ** содержат "iOS Team" в названии
   - ✅ Профили скачаны и сохранены

2. **В GitHub Secrets:**
   - ✅ `PROVISIONING_PROFILE_APP` обновлен
   - ✅ `PROVISIONING_PROFILE_EXTENSION` обновлен

3. **В workflow:**
   - ✅ После обновления секретов запустить workflow снова
   - ✅ Ошибка "Xcode managed" должна исчезнуть

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После обновления секретов:
1. Запустить workflow "Build and Upload to App Store"
2. Проверить, что ошибка "Xcode managed" исчезла
3. Если всё работает → билд должен собраться успешно!

---

**Дата:** 29 ноября 2025  
**Инструкция:** Как скачать manually managed provisioning profiles

