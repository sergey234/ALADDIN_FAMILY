# ⚡ БЫСТРАЯ ИНСТРУКЦИЯ: App Store Profiles

**Проблема:** У вас только Development профиль, нужен App Store профиль

---

## 🎯 ЧТО ДЕЛАТЬ (5 ШАГОВ)

### 1️⃣ Проверить сертификат

Откройте: https://developer.apple.com/account/resources/certificates/list

**Нужен:** Сертификат "Apple Distribution"  
**Если нет:** Создайте (нажмите "+" → выберите "Apple Distribution")

---

### 2️⃣ Создать профиль для основного приложения

1. Откройте: https://developer.apple.com/account/resources/profiles/list
2. Нажмите "+"
3. Выберите **"App Store"** (не Development!)
4. Выберите App ID: `family.aladdin.ios`
5. Выберите сертификат: "Apple Distribution"
6. Название: `ALADDIN App Store Distribution`
7. Скачайте профиль

---

### 3️⃣ Создать профиль для Extension

1. Нажмите "+"
2. Выберите **"App Store"**
3. Выберите App ID: `family.aladdin.ios.packetTunnel`
4. Выберите сертификат: "Apple Distribution"
5. Название: `ALADDIN PacketTunnel App Store Distribution`
6. Скачайте профиль

---

### 4️⃣ Закодировать в base64

```bash
# Создать папку
mkdir -p ~/Desktop/ALADDIN_Profiles

# Закодировать основной профиль
base64 -i ~/Downloads/ALADDIN_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt

# Закодировать профиль Extension
base64 -i ~/Downloads/ALADDIN_PacketTunnel_AppStore.mobileprovision | tr -d '\n' > ~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt
```

---

### 5️⃣ Обновить GitHub Secrets

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
2. Обновите `PROVISIONING_PROFILE_APP` (вставьте содержимое `app_profile_appstore_base64.txt`)
3. Обновите `PROVISIONING_PROFILE_EXTENSION` (вставьте содержимое `extension_profile_appstore_base64.txt`)

---

## ✅ ГОТОВО!

После обновления секретов запустите workflow снова.

---

**Подробная инструкция:** `docs/СОЗДАНИЕ_APP_STORE_PROFILES.md`

