# ✅ ПОЛНЫЙ ЧЕКЛИСТ: Проверка всех настроек VPN

**Дата:** $(date)  
**Цель:** Убедиться, что все настройки VPN правильные

---

## 📋 ЧЕКЛИСТ ДЛЯ ПРОВЕРКИ

### **1. ✅ Apple Developer Portal**

#### **1.1. Bundle ID: `family.aladdin.ios.packetTunnel`**
- [ ] Зайдите на: https://developer.apple.com/account/resources/identifiers/list
- [ ] Найдите `family.aladdin.ios.packetTunnel`
- [ ] Проверьте Capabilities:
  - [ ] ✅ **Personal VPN** — включена (галочка стоит)
  - [ ] ✅ **Network Extensions** — включена (галочка стоит)
  - [ ] ⚠️ **Packet Tunnel Provider** — должен быть выбран (если есть подменю)

**Статус:** ⚠️ **ТРЕБУЕТ ПРОВЕРКИ**

---

### **2. ✅ Xcode — Таргет ALADDINPacketTunnel**

#### **2.1. Откройте Xcode:**
- [ ] Откройте проект `ALADDIN.xcodeproj`
- [ ] Выберите таргет **ALADDINPacketTunnel** (не ALADDIN!)

#### **2.2. Вкладка "Signing & Capabilities":**
- [ ] Перейдите на вкладку **"Signing & Capabilities"**
- [ ] Проверьте:
  - [ ] ✅ **Team:** `6CJVBBUGSN` (выбран)
  - [ ] ✅ **Bundle Identifier:** `family.aladdin.ios.packetTunnel`
  - [ ] ✅ **Automatically manage signing:** включено

#### **2.3. Capabilities:**
- [ ] ✅ **Personal VPN** — должна быть в списке и включена
  - [ ] Если НЕТ — нажмите **"+ Capability"** → **"Personal VPN"**
  - [ ] Если есть, но отключена — включите переключатель
- [ ] ✅ **Network Extensions** — должна быть в списке и включена
  - [ ] Если НЕТ — нажмите **"+ Capability"** → **"Network Extensions"**
  - [ ] Если есть, но отключена — включите переключатель

**Статус:** ⚠️ **ТРЕБУЕТ ПРОВЕРКИ**

---

### **3. ✅ Entitlements файлы**

#### **3.1. ALADDINPacketTunnel.entitlements (Release):**
- [ ] Откройте файл `ALADDINPacketTunnel.entitlements`
- [ ] Проверьте содержимое:
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

**Статус:** ✅ **ПРАВИЛЬНО** (уже исправлено)

#### **3.2. ALADDINPacketTunnelDebug.entitlements (Debug):**
- [ ] Откройте файл `ALADDINPacketTunnelDebug.entitlements`
- [ ] Проверьте содержимое (должно быть такое же, как выше)

**Статус:** ✅ **ПРАВИЛЬНО** (уже исправлено)

---

### **4. ✅ Bundle IDs**

#### **4.1. Основное приложение:**
- [ ] Bundle ID: `family.aladdin.ios`
- [ ] Настроено в project.pbxproj

**Статус:** ✅ **ПРАВИЛЬНО**

#### **4.2. Network Extension:**
- [ ] Bundle ID: `family.aladdin.ios.packetTunnel`
- [ ] Настроено в project.pbxproj

**Статус:** ✅ **ПРАВИЛЬНО**

---

### **5. ✅ Code Signing**

#### **5.1. Таргет ALADDINPacketTunnel:**
- [ ] `CODE_SIGN_STYLE = Automatic`
- [ ] `DEVELOPMENT_TEAM = 6CJVBBUGSN`
- [ ] `CODE_SIGN_ENTITLEMENTS = ALADDINPacketTunnel.entitlements` (Release)
- [ ] `CODE_SIGN_ENTITLEMENTS = ALADDINPacketTunnelDebug.entitlements` (Debug)

**Статус:** ✅ **ПРАВИЛЬНО**

---

### **6. ✅ Provisioning Profiles**

#### **6.1. Обновить профили:**
- [ ] Xcode → Preferences... (⌘ + ,)
- [ ] Вкладка "Accounts"
- [ ] Выберите ваш Apple ID
- [ ] Нажмите "Download Manual Profiles"

**Статус:** ⚠️ **ТРЕБУЕТ ВЫПОЛНЕНИЯ**

---

### **7. ✅ Info.plist для Extension**

#### **7.1. ALADDIN/ALADDINPacketTunnel/Info.plist:**
- [ ] Откройте файл `ALADDIN/ALADDINPacketTunnel/Info.plist`
- [ ] Проверьте:
  ```xml
  <key>NSExtensionPointIdentifier</key>
  <string>com.apple.networkextension.packet-tunnel</string>  ✅ Должно быть так
  ```

**Статус:** ✅ **ПРАВИЛЬНО**

---

## 🔧 КАК ВКЛЮЧИТЬ PERSONAL VPN В XCODE

### **Если Personal VPN видно, но отключено:**

1. **Найдите "Personal VPN"** в списке Capabilities
2. **Кликните на "Personal VPN"** (на саму строку, не на галочку)
3. **Проверьте, есть ли переключатель** или **кнопка "Enable"**
4. **Включите** переключатель или нажмите "Enable"

### **Если Personal VPN нет в списке:**

1. **Нажмите "+ Capability"** (в левом верхнем углу)
2. **Найдите "Personal VPN"** в списке
3. **Нажмите на "Personal VPN"**
4. **Xcode автоматически добавит** Personal VPN

### **Если не получается включить:**

1. **Проверьте Team:**
   - Убедитесь, что выбран правильный Team (`6CJVBBUGSN`)
   - Team должен быть платным ($99/год)

2. **Проверьте Bundle ID в Portal:**
   - Убедитесь, что Personal VPN включена в Apple Developer Portal
   - Зайдите на: https://developer.apple.com/account/resources/identifiers/list
   - Найдите `family.aladdin.ios.packetTunnel`
   - Проверьте, что Personal VPN включена

3. **Пересоздать профиль:**
   - В Xcode: Signing & Capabilities
   - Снимите галочку "Automatically manage signing"
   - Подождите 2 секунды
   - Снова включите "Automatically manage signing"
   - Выберите Team
   - Xcode создаст новый профиль

---

## ⚠️ ПРЕДУПРЕЖДЕНИЯ ОБ ИКОНКАХ

### **Проблема:**
- Предупреждения об иконках AppIcon в Xcode

### **Решение:**
1. **Откройте Assets.xcassets**
2. **Откройте AppIcon.appiconset**
3. **Проверьте, что все размеры заполнены:**
   - 20x20 (@2x, @3x)
   - 29x29 (@2x, @3x)
   - 40x40 (@2x, @3x)
   - 60x60 (@2x, @3x)
   - 76x76 (@1x, @2x) — для iPad
   - 83.5x83.5 (@2x) — для iPad Pro
   - 1024x1024 (@1x) — для App Store

4. **Если есть файл `ALADDIN_icon_1024.png` без назначения:**
   - Удалите его или назначьте на 1024x1024 слот

**Статус:** ⚠️ **ТРЕБУЕТ ПРОВЕРКИ**

---

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА

### **После всех исправлений:**

1. **Очистите проект:**
   - Product → Clean Build Folder (⇧⌘K)

2. **Пересоберите архив:**
   - Product → Archive

3. **Проверьте, что сборка проходит без ошибок**

4. **Проверьте предупреждения:**
   - Если есть предупреждения об иконках — исправьте
   - Если есть предупреждения о VPN — проверьте настройки

---

## 📝 КРАТКАЯ ИНСТРУКЦИЯ

### **Включить Personal VPN:**
1. Xcode → Таргет ALADDINPacketTunnel
2. Signing & Capabilities
3. "+ Capability" → "Personal VPN"
4. Проверить, что включена

### **Исправить иконки:**
1. Assets.xcassets → AppIcon.appiconset
2. Проверить, что все размеры заполнены
3. Удалить неиспользуемые файлы

### **Проверить Portal:**
1. https://developer.apple.com/account/resources/identifiers/list
2. Найти `family.aladdin.ios.packetTunnel`
3. Проверить Capabilities

---

**Пройдитесь по чеклисту и отметьте все пункты!** ✅

