# 🔧 КАК ОБНОВИТЬ ПРОФИЛИ В XCODE И ПРОВЕРИТЬ PORTAL

## 📋 ПРОБЛЕМА

- ❌ В Apple Developer Portal нет подменю для выбора "Packet Tunnel Provider"
- ❓ Где обновить профили в Xcode?
- ❓ Где проверить, правильно ли настроен Portal?

---

## 🔍 ШАГ 1: ПРОВЕРКА APPLE DEVELOPER PORTAL

### **Где смотреть:**

1. **Откройте Apple Developer Portal:**
   - Зайдите на: https://developer.apple.com/account/resources/identifiers/list
   - Войдите с вашим Apple ID

2. **Найдите Bundle ID для Extension:**
   - В списке найдите: `family.aladdin.ios.packetTunnel`
   - Нажмите на него

3. **Проверьте Capabilities:**
   - Должны быть включены:
     - ✅ **Personal VPN** (галочка стоит)
     - ✅ **Network Extensions** (галочка стоит)

4. **Проблема с подменю:**
   - ⚠️ Если подменю не появляется — это нормально!
   - Apple Developer Portal иногда не показывает подменю
   - **Решение:** Настройте через Xcode (см. ниже)

---

## 🔧 ШАГ 2: ОБНОВЛЕНИЕ ПРОФИЛЕЙ В XCODE

### **Где это находится:**

1. **Откройте Xcode**

2. **Откройте Preferences:**
   - **Xcode → Preferences...** (⌘ + ,)
   - Или: **Xcode → Settings...** (в новых версиях)

3. **Перейдите на вкладку "Accounts":**
   - В верхней панели выберите **"Accounts"**
   - Вы увидите список ваших Apple ID

4. **Выберите ваш Apple ID:**
   - Нажмите на ваш Apple ID в списке
   - Справа увидите список команд

5. **Нажмите "Download Manual Profiles":**
   - Кнопка находится под списком команд
   - Xcode загрузит все provisioning profiles с сервера Apple

6. **Или нажмите "Manage Certificates...":**
   - Если нужно управлять сертификатами
   - Обычно не требуется

---

## ✅ ШАГ 3: НАСТРОЙКА ЧЕРЕЗ XCODE (ЕСЛИ ПОДМЕНЮ НЕТ)

### **Если в Portal нет подменю:**

**Решение:** Настройте через Xcode — это правильный способ!

### **Как настроить:**

1. **Откройте проект в Xcode:**
   ```bash
   open ALADDIN.xcodeproj
   ```

2. **Выберите таргет ALADDINPacketTunnel:**
   - В левой панели выберите проект **ALADDIN**
   - Выберите таргет **ALADDINPacketTunnel**

3. **Перейдите на вкладку "Signing & Capabilities":**
   - В верхней панели выберите **"Signing & Capabilities"**

4. **Проверьте Capabilities:**
   - Должны быть включены:
     - ✅ **Personal VPN**
     - ✅ **Network Extensions**

5. **Настройте Network Extensions:**
   - Нажмите на **"Network Extensions"**
   - Если есть подменю — выберите **"Packet Tunnel Provider"**
   - Если подменю нет — Xcode автоматически настроит правильный тип

6. **Проверьте Automatic Signing:**
   - Убедитесь, что **"Automatically manage signing"** включено
   - Xcode автоматически создаст/обновит provisioning profiles

---

## 🔄 ШАГ 4: ОБНОВЛЕНИЕ ПРОФИЛЕЙ АВТОМАТИЧЕСКИ

### **Через Xcode (рекомендуется):**

1. **В Xcode:**
   - Выберите таргет **ALADDINPacketTunnel**
   - Перейдите на **"Signing & Capabilities"**
   - Если видите предупреждение — нажмите **"Try Again"** или **"Fix Issue"**
   - Xcode автоматически обновит профили

2. **Или через командную строку:**
   ```bash
   # Очистить старые профили
   rm -rf ~/Library/MobileDevice/Provisioning\ Profiles/*
   
   # Xcode загрузит новые при следующей сборке
   ```

---

## 🔍 ШАГ 5: ПРОВЕРКА, ЧТО ВСЁ ПРАВИЛЬНО

### **Проверка в Xcode:**

1. **Выберите таргет ALADDINPacketTunnel**

2. **Перейдите на "Signing & Capabilities"**

3. **Проверьте:**
   - ✅ **Team:** Ваш Team ID (`6CJVBBUGSN`)
   - ✅ **Bundle Identifier:** `family.aladdin.ios.packetTunnel`
   - ✅ **Capabilities:**
     - ✅ Personal VPN
     - ✅ Network Extensions

4. **Проверьте Provisioning Profile:**
   - Должен быть указан профиль (например: "iOS Team Provisioning Profile: family.aladdin.ios.packetTunnel")
   - Если видите предупреждение — нажмите **"Fix Issue"**

---

## 📝 ШАГ 6: ПРОВЕРКА ENTITLEMENTS

### **Проверьте, что entitlements правильные:**

1. **Откройте файл `ALADDINPacketTunnel.entitlements`**

2. **Проверьте содержимое:**
   ```xml
   <key>com.apple.developer.networking.networkextension</key>
   <array>
       <string>packet-tunnel</string>  ✅ Должно быть так
   </array>
   <key>com.apple.developer.networking.vpn.api</key>
   <array>
       <string>allow-vpn</string>  ✅ Должно быть так
   </array>
   ```

3. **Если правильно — всё хорошо!**

---

## ✅ ШАГ 7: ПЕРЕСБОРКА АРХИВА

### **После обновления профилей:**

1. **Очистите проект:**
   - **Product → Clean Build Folder** (⇧⌘K)

2. **Пересоберите архив:**
   - **Product → Archive**

3. **Проверьте, что сборка проходит без ошибок**

---

## 🎯 КРАТКАЯ ИНСТРУКЦИЯ

### **Обновить профили в Xcode:**

1. **Xcode → Preferences...** (⌘ + ,)
2. **Вкладка "Accounts"**
3. **Выберите ваш Apple ID**
4. **Нажмите "Download Manual Profiles"**

### **Проверить Portal:**

1. **https://developer.apple.com/account/resources/identifiers/list**
2. **Найдите `family.aladdin.ios.packetTunnel`**
3. **Проверьте Capabilities:**
   - ✅ Personal VPN
   - ✅ Network Extensions

### **Если подменю нет:**

1. **Настройте через Xcode:**
   - Таргет **ALADDINPacketTunnel**
   - **Signing & Capabilities**
   - Включите **Network Extensions**
   - Xcode автоматически настроит правильный тип

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### **О подменю:**

- ⚠️ **Если подменю не появляется в Portal — это нормально!**
- ✅ **Xcode автоматически настроит правильный тип**
- ✅ **Главное — включить Network Extensions в Portal и Xcode**

### **О профилях:**

- ✅ **Xcode автоматически создаст/обновит профили**
- ✅ **Если включен "Automatically manage signing"**
- ✅ **Профили обновятся при следующей сборке**

---

## ✅ ИТОГОВАЯ ПРОВЕРКА

### **Что должно быть:**

1. ✅ **В Portal:**
   - Personal VPN включена
   - Network Extensions включена

2. ✅ **В Xcode:**
   - Personal VPN включена
   - Network Extensions включена
   - Provisioning Profile обновлён

3. ✅ **В Entitlements:**
   - `packet-tunnel` (не `packet-tunnel-provider`)
   - `allow-vpn`

---

**ВСЁ ГОТОВО!** 🚀

