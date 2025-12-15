# 📋 СОЗДАНИЕ APP STORE PROVISIONING PROFILES

**Дата:** 29 ноября 2025  
**Проблема:** Есть только Development профиль, нужны App Store профили

---

## 🔍 ЧТО У ВАС ЕСТЬ

- ✅ **Профиль:** `ALADDINPacketTunnel Dev New` (Development)
- ❌ **Нужен:** App Store профиль для Distribution

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### Шаг 1: Проверить сертификаты

1. **Открыть Developer Portal:**
   - https://developer.apple.com/account/resources/certificates/list

2. **Проверить, есть ли сертификат "Apple Distribution":**
   - Ищите сертификат с типом **"Apple Distribution"**
   - Если его нет → нужно создать (см. Шаг 2)

3. **Если есть "Apple Distribution":**
   - ✅ Можно сразу создавать App Store профили
   - Переходим к Шагу 3

---

### Шаг 2: Создать сертификат "Apple Distribution" (если нет)

1. **Открыть страницу сертификатов:**
   - https://developer.apple.com/account/resources/certificates/list
   - Нажать "+" (Create a new certificate)

2. **Выбрать тип:**
   - Выбрать **"Apple Distribution"**
   - Нажать "Continue"

3. **Следовать инструкциям:**
   - Скачать Certificate Signing Request (CSR) через Keychain Access
   - Загрузить CSR на сайт
   - Скачать готовый сертификат
   - Двойной клик для установки в Keychain

**Результат:**
- ✅ Сертификат "Apple Distribution" установлен в Keychain

---

### Шаг 3: Создать App Store профиль для основного приложения

1. **Открыть страницу Profiles:**
   - https://developer.apple.com/account/resources/profiles/list
   - Нажать "+" (Create a new provisioning profile)

2. **Выбрать тип:**
   - Выбрать **"App Store"** (не Development!)
   - Нажать "Continue"

3. **Выбрать App ID:**
   - Выбрать `family.aladdin.ios` (основное приложение)
   - Нажать "Continue"

4. **Выбрать сертификат:**
   - Выбрать **"Apple Distribution"** сертификат
   - Нажать "Continue"

5. **Ввести название:**
   - **Profile Name:** `ALADDIN App Store Distribution`
   - Нажать "Generate"

6. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл (например, `ALADDIN_AppStore.mobileprovision`)

**Результат:**
- ✅ App Store профиль для `family.aladdin.ios` создан и скачан

---

### Шаг 4: Создать App Store профиль для Network Extension

1. **Нажать "+" (Create a new provisioning profile):**

2. **Выбрать тип:**
   - Выбрать **"App Store"** (не Development!)
   - Нажать "Continue"

3. **Выбрать App ID:**
   - Выбрать `family.aladdin.ios.packetTunnel` (Network Extension)
   - Нажать "Continue"

4. **Выбрать сертификат:**
   - Выбрать **"Apple Distribution"** сертификат
   - Нажать "Continue"

5. **Ввести название:**
   - **Profile Name:** `ALADDIN PacketTunnel App Store Distribution`
   - Нажать "Generate"

6. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл (например, `ALADDIN_PacketTunnel_AppStore.mobileprovision`)

**Результат:**
- ✅ App Store профиль для `family.aladdin.ios.packetTunnel` создан и скачан

---

### Шаг 5: Закодировать в base64

1. **Открыть Terminal:**
   - Cmd+Space → ввести "Terminal" → Enter

2. **Перейти в папку с профилями:**
   ```bash
   cd ~/Downloads  # или где вы сохранили профили
   ```

3. **Создать папку для base64 файлов:**
   ```bash
   mkdir -p ~/Desktop/ALADDIN_Profiles
   ```

4. **Закодировать основной профиль:**
   ```bash
   base64 -i ALADDIN_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt
   ```

5. **Закодировать профиль для Extension:**
   ```bash
   base64 -i ALADDIN_PacketTunnel_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt
   ```

6. **Проверить файлы:**
   ```bash
   ls -lh ~/Desktop/ALADDIN_Profiles/
   ```

**Результат:**
- ✅ Оба профиля закодированы в base64

---

### Шаг 6: Обновить GitHub Secrets

1. **Открыть GitHub:**
   - https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Обновить PROVISIONING_PROFILE_APP:**
   - Найти `PROVISIONING_PROFILE_APP`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt`
   - Скопировать всё содержимое (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

3. **Обновить PROVISIONING_PROFILE_EXTENSION:**
   - Найти `PROVISIONING_PROFILE_EXTENSION`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt`
   - Скопировать всё содержимое (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

**Результат:**
- ✅ GitHub Secrets обновлены с App Store профилями

---

## ✅ ПРОВЕРКА

### Что должно быть:

1. **В Developer Portal:**
   - ✅ Сертификат "Apple Distribution" создан
   - ✅ Профиль "ALADDIN App Store Distribution" создан
   - ✅ Профиль "ALADDIN PacketTunnel App Store Distribution" создан
   - ✅ Оба профиля скачаны

2. **На компьютере:**
   - ✅ Файлы `.mobileprovision` сохранены
   - ✅ Base64 файлы созданы в `~/Desktop/ALADDIN_Profiles/`

3. **В GitHub Secrets:**
   - ✅ `PROVISIONING_PROFILE_APP` обновлен
   - ✅ `PROVISIONING_PROFILE_EXTENSION` обновлен

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После обновления секретов:
1. Запустить workflow "Build and Upload to App Store"
2. Проверить, что ошибка "Xcode managed" исчезла
3. Если всё работает → билд должен собраться успешно!

---

## 📝 РАЗНИЦА МЕЖДУ ПРОФИЛЯМИ

### Development Profile:
- ❌ Для разработки и тестирования
- ❌ Нельзя использовать для App Store
- ❌ Требует регистрацию устройств

### App Store Profile:
- ✅ Для публикации в App Store
- ✅ Не требует регистрацию устройств
- ✅ Работает с Manual signing на CI/CD

---

**Дата:** 29 ноября 2025  
**Инструкция:** Создание App Store provisioning profiles

