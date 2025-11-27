# 🔍 ПРОВЕРКА: Выбран ли Packet Tunnel Provider

**Проблема:** Personal VPN и Network Extensions уже включены, но ошибка остаётся  
**Решение:** Проверить, что Packet Tunnel Provider выбран в подменю

---

## ✅ ЧТО ПРОВЕРИТЬ

### **ШАГ 1: Проверить подменю Network Extensions**

1. **Зайдите на:** https://developer.apple.com/account/resources/identifiers/list
2. **Кликните на `family.aladdin.ios.packetTunnel`**
3. **Прокрутите до раздела "Capabilities"**
4. **Найдите "Network Extensions"** (должна быть галочка ☑️)
5. **Кликните на "Network Extensions"** (на саму строку, не на галочку)
6. **Должно открыться подменю** или **детали**

**Проверьте, что в подменю отмечено:**
- ☑️ **Packet Tunnel Provider** ← ДОЛЖНО БЫТЬ ОТМЕЧЕНО!

**Если НЕ отмечено:**
- Отметьте галочку ☑️ рядом с "Packet Tunnel Provider"
- Нажмите "Save"

---

### **ШАГ 2: Проверить основной Bundle ID**

1. **Вернитесь на страницу Identifiers**
2. **Кликните на `family.aladdin.ios`** (основное приложение)
3. **Проверьте Capabilities:**
   - ☑️ **Personal VPN** (если нужно)
   - ☑️ **Network Extensions** (если нужно)
4. **Если что-то не включено — включите и нажмите "Save"**

---

### **ШАГ 3: Удалить старые Provisioning Profiles**

Старые профили могут не содержать обновлённые capabilities.

1. **Откройте Xcode**
2. **Xcode → Preferences** (`⌘ + ,`)
3. **Вкладка "Accounts"**
4. **Выберите ваш Apple ID**
5. **Нажмите "View Details..."**
6. **Найдите профили для:**
   - `family.aladdin.ios`
   - `family.aladdin.ios.packetTunnel`
7. **Удалите старые профили:**
   - Выделите профиль
   - Нажмите клавишу `Delete` или кнопку "—" (минус)
8. **Нажмите "Download Manual Profiles"** или кнопку обновления
9. **Xcode создаст новые профили** с правильными capabilities

---

### **ШАГ 4: Очистить проект и пересобрать**

1. **В Xcode выберите "Any iOS Device (arm64)"**

2. **Product → Clean Build Folder** (`Shift + ⌘ + K`)

3. **Подождите 10 секунд**

4. **Удалите DerivedData:**
   - Закройте Xcode
   - Откройте Finder
   - Нажмите `⌘ + Shift + G` (Go to Folder)
   - Введите: `~/Library/Developer/Xcode/DerivedData`
   - Найдите папку `ALADDIN-*`
   - Удалите её
   - Откройте Xcode снова

5. **Product → Build** (`⌘ + B`)

6. **Product → Archive**

---

## ⚠️ ВАЖНО: ПРОВЕРКА ПОДМЕНЮ

**Частая ошибка:** Network Extensions включён, но Packet Tunnel Provider НЕ выбран в подменю.

**Как проверить:**

1. **Кликните на строку "Network Extensions"** (не на галочку, а на саму строку)
2. **Должно открыться окно** или **подменю** с опциями:
   ```
   ☐ Content Filter Provider
   ☐ App Proxy Provider
   ☐ Packet Tunnel Provider  ← ДОЛЖНО БЫТЬ ☑️
   ☐ DNS Proxy Provider
   ```
3. **Если Packet Tunnel Provider НЕ отмечен:**
   - Отметьте галочку ☑️
   - Нажмите "Save" или "Continue"

---

## 📋 ЧТО ДОЛЖНО БЫТЬ ВКЛЮЧЕНО

### **Для `family.aladdin.ios.packetTunnel`:**

✅ **Personal VPN** (в основном списке)  
✅ **Network Extensions** (в основном списке)  
   └─ ✅ **Packet Tunnel Provider** (в подменю) ← **ВАЖНО!**

---

## 🔧 АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ: Пересоздать Provisioning Profile

Если после всех проверок ошибка остаётся:

1. **В Xcode:** Signing & Capabilities
2. **Снимите галочку** "Automatically manage signing"
3. **Подождите 2 секунды**
4. **Снова включите** "Automatically manage signing"
5. **Выберите Team** в выпадающем списке
6. **Xcode создаст новый профиль** с правильными capabilities

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. Проверить, что Packet Tunnel Provider отмечен в подменю Network Extensions
2. Удалить старые provisioning profiles в Xcode
3. Download Manual Profiles
4. Удалить DerivedData
5. Product → Clean Build Folder
6. Product → Archive
```

---

**Проверьте подменю Network Extensions — там должен быть отмечен Packet Tunnel Provider!** 🚀

