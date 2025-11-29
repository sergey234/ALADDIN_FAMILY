# ✅ APP ID НАЙДЕНЫ! СОЗДАЕМ ПРОФИЛИ

**Дата:** 29 ноября 2025

---

## ✅ ЧТО ЕСТЬ

✅ **App ID для основного приложения:**
- Название: `XC family aladdin ios`
- Bundle ID: `family.aladdin.ios`

✅ **App ID для Network Extension:**
- Название: `XC family aladdin ios packetTunnel`
- Bundle ID: `family.aladdin.ios.packetTunnel`

---

## 🎯 ТЕПЕРЬ СОЗДАЕМ ПРОФИЛИ!

### Шаг 1: Создать профиль для основного приложения

1. **Открыть:** https://developer.apple.com/account/resources/profiles/list
2. **Нажать "+"** (Create a new provisioning profile)

3. **Выбрать тип:**
   - Выбрать **Distribution → App Store Connect**
   - Нажать "Continue"

4. **Выбрать App ID:**
   - В списке найти: **`XC family aladdin ios`** (или `family.aladdin.ios`)
   - Выбрать его
   - Нажать "Continue"

5. **Выбрать сертификат:**
   - Выбрать сертификат **"Distribution"** (2026/11/29)
   - Нажать "Continue"

6. **Ввести название:**
   - **Profile Name:** `ALADDIN App Store Distribution`
   - Нажать "Generate"

7. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл

---

### Шаг 2: Создать профиль для Network Extension

1. **Нажать "+"** (Create a new provisioning profile)

2. **Выбрать тип:**
   - Выбрать **Distribution → App Store Connect**
   - Нажать "Continue"

3. **Выбрать App ID:**
   - В списке найти: **`XC family aladdin ios packetTunnel`** (или `family.aladdin.ios.packetTunnel`)
   - Выбрать его
   - Нажать "Continue"

4. **Выбрать сертификат:**
   - Выбрать сертификат **"Distribution"** (тот же)
   - Нажать "Continue"

5. **Ввести название:**
   - **Profile Name:** `ALADDIN PacketTunnel App Store Distribution`
   - Нажать "Generate"

6. **Скачать профиль:**
   - Нажать "Download"
   - Сохранить файл

---

## 📋 ПОСЛЕ СКАЧИВАНИЯ ПРОФИЛЕЙ

### Шаг 3: Запустить скрипт для кодирования

```bash
~/Desktop/ALADDIN_Profiles/encode_profiles.sh
```

Скрипт автоматически:
- ✅ Найдет скачанные профили
- ✅ Закодирует в base64
- ✅ Сохранит готовые файлы

---

### Шаг 4: Обновить GitHub Secrets

1. **Открыть:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Обновить PROVISIONING_PROFILE_APP:**
   - Найти `PROVISIONING_PROFILE_APP`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt`
   - Скопировать всё (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

3. **Обновить PROVISIONING_PROFILE_EXTENSION:**
   - Найти `PROVISIONING_PROFILE_EXTENSION`
   - Нажать "Update"
   - Открыть `~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt`
   - Скопировать всё (Cmd+A, Cmd+C)
   - Вставить в поле Secret (Cmd+V)
   - Нажать "Update secret"

---

## ✅ ГОТОВО!

После обновления секретов:
1. Запустить workflow "Build and Upload to App Store"
2. Билд должен собраться успешно!

---

**Дата:** 29 ноября 2025  
**App ID найдены, создаем профили!**

