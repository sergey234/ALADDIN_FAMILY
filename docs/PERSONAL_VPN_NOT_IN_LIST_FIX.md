# ❌ Personal VPN нет в списке Capabilities - РЕШЕНИЕ

## 🚨 ПРОБЛЕМА

- ❌ Personal VPN **НЕТ** в списке при нажатии "+ Capability"
- ❌ Нельзя выбрать Personal VPN
- ❌ Xcode не показывает Personal VPN как доступную capability

---

## ✅ РЕШЕНИЕ: Сначала включить в Apple Developer Portal

**Главная причина:** Personal VPN должна быть **сначала включена в Apple Developer Portal**, и только потом она появится в Xcode.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 1: Включите Personal VPN в Apple Developer Portal**

1. **Откройте:** https://developer.apple.com/account/resources/identifiers/list
2. **Войдите** в свой Apple Developer аккаунт
3. **Найдите Bundle ID:** `family.aladdin.ios.packetTunnel`
   - Используйте поиск или прокрутите список
4. **Кликните на Bundle ID** (откроется страница с деталями)

### **ШАГ 2: Включите Capabilities в Portal**

На странице Bundle ID найдите раздел **"Capabilities"**:

1. **Включите галочку "Personal VPN"**
2. **Включите галочку "Network Extensions"**
3. **Внутри Network Extensions:**
   - Раскройте список (если есть подменю)
   - Выберите **"Packet Tunnel Provider"**
4. **Нажмите "Save"** (Сохранить) в правом верхнем углу

### **ШАГ 3: Подождите 1-2 минуты**

Apple обновит настройки на серверах. Подождите 1-2 минуты.

### **ШАГ 4: Вернитесь в Xcode**

1. **Выберите таргет ALADDINPacketTunnel**
2. **Вкладка "Signing & Capabilities"**
3. **Проверьте Team:**
   - Team должен быть выбран (не "None")
   - Team ID должен совпадать с Portal

### **ШАГ 5: Обновите Provisioning Profiles**

1. **Xcode → Preferences...** (⌘ + ,)
2. **Вкладка "Accounts"**
3. **Выберите ваш Apple ID**
4. **Нажмите "Download Manual Profiles"**
5. **Подождите** пока загрузятся профили

**Или автоматически:**
- В Xcode: Signing & Capabilities
- Снимите галочку "Automatically manage signing"
- Подождите 2 секунды
- Снова включите "Automatically manage signing"
- Выберите Team
- Xcode обновит профили автоматически

### **ШАГ 6: Попробуйте добавить Personal VPN снова**

1. **Нажмите "+ Capability"**
2. **Проверьте список** - Personal VPN должна появиться
3. **Выберите Personal VPN**

---

## 🔍 ЕСЛИ Bundle ID НЕ НАЙДЕН В PORTAL

### **Создайте Bundle ID в Portal:**

1. **На странице Identifiers** нажмите кнопку **"+"** (плюс)
2. **Выберите "App IDs"** → **"Continue"**
3. **Выберите "App"** → **"Continue"**
4. **Заполните:**
   - **Description:** `ALADDIN Packet Tunnel Extension`
   - **Bundle ID:** `family.aladdin.ios.packetTunnel` (Explicit)
5. **В разделе "Capabilities":**
   - ✅ Включите **Personal VPN** (галочка)
   - ✅ Включите **Network Extensions** (галочка)
   - ✅ Внутри Network Extensions выберите **"Packet Tunnel Provider"**
6. **Нажмите "Continue"** → **"Register"**

---

## ⚠️ ВАЖНО: Проверьте Team

### **Проблема: Personal VPN требует платный аккаунт**

Personal VPN доступна **только для платного Apple Developer Program** ($99/год).

**Проверьте:**
1. Зайдите на: https://developer.apple.com/account
2. Проверьте раздел **"Membership"**
3. Должно быть: **"Active"** (не "Free")

**Если аккаунт бесплатный:**
- Personal VPN **не будет доступна**
- Нужно купить Apple Developer Program ($99/год)

---

## 🔧 АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ: Добавить вручную через Entitlements

Если Personal VPN всё ещё не появляется в списке, можно добавить вручную:

### **ШАГ 1: Проверьте Entitlements файл**

Откройте файл `ALADDINPacketTunnel.entitlements` и убедитесь, что там есть:

```xml
<key>com.apple.developer.networking.vpn.api</key>
<array>
    <string>allow-vpn</string>
</array>
```

### **ШАГ 2: Добавьте вручную (если нет)**

Если ключа нет, добавьте его в `ALADDINPacketTunnel.entitlements`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.developer.networking.networkextension</key>
    <array>
        <string>packet-tunnel</string>
    </array>
    <key>com.apple.developer.networking.vpn.api</key>
    <array>
        <string>allow-vpn</string>
    </array>
</dict>
</plist>
```

### **ШАГ 3: Пересоберите проект**

1. **Product → Clean Build Folder** (⇧⌘K)
2. **Product → Build** (⌘B)

---

## 📋 ЧЕКЛИСТ: Всё должно быть так

### ✅ В Apple Developer Portal:
- ✅ Bundle ID `family.aladdin.ios.packetTunnel` существует
- ✅ Personal VPN включена (галочка)
- ✅ Network Extensions включена (галочка)
- ✅ Packet Tunnel Provider выбран
- ✅ Сохранено (Save)

### ✅ В Xcode:
- ✅ Team выбран (платный аккаунт)
- ✅ Bundle Identifier: `family.aladdin.ios.packetTunnel`
- ✅ "Automatically manage signing" включена
- ✅ Provisioning Profiles обновлены

### ✅ В Entitlements:
- ✅ `ALADDINPacketTunnel.entitlements` содержит:
  - `com.apple.developer.networking.networkextension` → `packet-tunnel`
  - `com.apple.developer.networking.vpn.api` → `allow-vpn`

---

## 🎯 ИТОГОВАЯ ИНСТРУКЦИЯ

1. **СНАЧАЛА:** Включите Personal VPN в Apple Developer Portal
2. **ПОДОЖДИТЕ:** 1-2 минуты
3. **В Xcode:** Обновите provisioning profiles
4. **ПОПРОБУЙТЕ:** Нажать "+ Capability" - Personal VPN должна появиться

**Если Personal VPN всё ещё не появляется:**
- Проверьте, что аккаунт платный ($99/год)
- Добавьте вручную через entitlements файл

---

## ✅ ГЛАВНОЕ ПРАВИЛО

**Personal VPN должна быть сначала включена в Portal, потом она появится в Xcode!**

Проверьте Portal прямо сейчас - это самое важное! 🚀

