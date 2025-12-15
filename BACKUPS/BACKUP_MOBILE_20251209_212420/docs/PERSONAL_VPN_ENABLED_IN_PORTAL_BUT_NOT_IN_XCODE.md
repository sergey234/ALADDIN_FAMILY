# ✅ Personal VPN включена в Portal, но не появляется в Xcode

## 📋 Что вы видите в Portal

- ✅ Platform Support: iOS, visionOS, macOS
- ✅ Provisioning Support: Development, Ad hoc, App Store Connect, Developer ID
- ✅ Entitlement Keys: `com.apple.developer.networking.vpn.api`

**Это означает, что Personal VPN уже включена в Portal!** ✅

---

## 🚨 ПРОБЛЕМА: Не появляется в Xcode

Если Personal VPN включена в Portal, но не появляется в Xcode при нажатии "+ Capability", нужно:

1. **Проверить Network Extensions** (тоже должна быть включена)
2. **Обновить provisioning profiles** в Xcode
3. **Перезапустить Xcode**

---

## ✅ РЕШЕНИЕ: Пошаговая инструкция

### **ШАГ 1: Проверьте Network Extensions в Portal**

В Apple Developer Portal на странице Bundle ID `family.aladdin.ios.packetTunnel` проверьте:

**Должны быть включены ОБЕ capability:**
- ✅ **Personal VPN** - включена (вы уже проверили)
- ✅ **Network Extensions** - должна быть включена
  - Внутри Network Extensions должен быть выбран **"Packet Tunnel Provider"**

**Если Network Extensions не включена:**
1. Включите галочку **Network Extensions**
2. Внутри выберите **"Packet Tunnel Provider"**
3. Нажмите **"Save"**

### **ШАГ 2: Обновите Provisioning Profiles в Xcode**

1. **Xcode → Preferences...** (⌘ + ,)
2. **Вкладка "Accounts"**
3. **Выберите ваш Apple ID**
4. **Нажмите "Download Manual Profiles"**
5. **Подождите** пока загрузятся профили (может занять 1-2 минуты)

**Или автоматически:**
1. В Xcode: **Signing & Capabilities**
2. **Снимите галочку** "Automatically manage signing"
3. **Подождите 2 секунды**
4. **Снова включите** "Automatically manage signing"
5. **Выберите Team**
6. Xcode создаст/обновит профили автоматически

### **ШАГ 3: Перезапустите Xcode**

1. **Закройте Xcode** полностью (⌘Q)
2. **Подождите 5 секунд**
3. **Откройте Xcode** заново
4. **Откройте проект** `ALADDIN.xcodeproj`

### **ШАГ 4: Очистите и пересоберите проект**

1. **Product → Clean Build Folder** (⇧⌘K)
2. **Подождите** пока очистится
3. **Product → Build** (⌘B)

### **ШАГ 5: Попробуйте добавить Personal VPN снова**

1. **Выберите таргет ALADDINPacketTunnel**
2. **Вкладка "Signing & Capabilities"**
3. **Нажмите "+ Capability"**
4. **Проверьте список** - Personal VPN должна появиться

---

## 🔍 ЕСЛИ Personal VPN ВСЁ ЕЩЁ НЕ ПОЯВЛЯЕТСЯ

### **Вариант 1: Проверьте, что Network Extensions включена**

**В Portal проверьте:**
- ✅ Personal VPN - включена ✅ (уже проверили)
- ✅ Network Extensions - должна быть включена ⚠️ **ПРОВЕРЬТЕ ЭТО!**
  - Внутри должен быть выбран "Packet Tunnel Provider"

**Если Network Extensions не включена:**
- Personal VPN может не работать без Network Extensions
- Включите Network Extensions в Portal
- Сохраните
- Подождите 1-2 минуты
- Обновите профили в Xcode

### **Вариант 2: Проверьте Team в Xcode**

1. **Выберите таргет ALADDINPacketTunnel**
2. **Вкладка "Signing & Capabilities"**
3. **В разделе "Signing"** проверьте:
   - ✅ **Team:** должен быть выбран (не "None")
   - ✅ **Team ID:** должен совпадать с Portal
   - ✅ **"Automatically manage signing"** - включена

**Если Team не выбран:**
- Выберите Team из списка
- Xcode обновит профили

### **Вариант 3: Добавьте вручную через Entitlements**

Если Personal VPN всё ещё не появляется, можно добавить вручную:

1. **Откройте файл** `ALADDINPacketTunnel.entitlements`
2. **Проверьте, что там есть:**
   ```xml
   <key>com.apple.developer.networking.vpn.api</key>
   <array>
       <string>allow-vpn</string>
   </array>
   ```
3. **Если нет** - добавьте вручную
4. **Пересоберите проект**

---

## 📋 ЧЕКЛИСТ: Всё должно быть так

### ✅ В Apple Developer Portal:
- ✅ Bundle ID `family.aladdin.ios.packetTunnel` существует
- ✅ **Personal VPN** - включена ✅ (вы проверили)
- ✅ **Network Extensions** - включена ⚠️ **ПРОВЕРЬТЕ!**
- ✅ **Packet Tunnel Provider** - выбран внутри Network Extensions
- ✅ Сохранено (Save)

### ✅ В Xcode:
- ✅ Team выбран (не "None")
- ✅ Bundle Identifier: `family.aladdin.ios.packetTunnel`
- ✅ "Automatically manage signing" включена
- ✅ Provisioning Profiles обновлены (Download Manual Profiles)
- ✅ Xcode перезапущен

### ✅ В Entitlements:
- ✅ `ALADDINPacketTunnel.entitlements` содержит:
  - `com.apple.developer.networking.networkextension` → `packet-tunnel`
  - `com.apple.developer.networking.vpn.api` → `allow-vpn`

---

## 🎯 ГЛАВНОЕ: Проверьте Network Extensions

**Самый частый случай:** Personal VPN включена, но **Network Extensions не включена**.

**Проверьте в Portal:**
1. Зайдите на страницу Bundle ID `family.aladdin.ios.packetTunnel`
2. Найдите раздел "Capabilities"
3. Проверьте, что **Network Extensions** тоже включена
4. Внутри Network Extensions должен быть выбран **"Packet Tunnel Provider"**

**Если Network Extensions не включена:**
- Включите её
- Сохраните
- Подождите 1-2 минуты
- Обновите профили в Xcode
- Personal VPN должна появиться

---

## ✅ ИТОГОВАЯ ИНСТРУКЦИЯ

1. **Проверьте Network Extensions в Portal** (должна быть включена)
2. **Обновите provisioning profiles в Xcode**
3. **Перезапустите Xcode**
4. **Попробуйте добавить Personal VPN через "+ Capability"**

**Главное:** Убедитесь, что **ОБЕ** capability включены в Portal:
- ✅ Personal VPN
- ✅ Network Extensions → Packet Tunnel Provider

Проверьте Network Extensions прямо сейчас! 🚀

