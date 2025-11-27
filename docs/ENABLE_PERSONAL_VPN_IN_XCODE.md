# 🔧 КАК ВКЛЮЧИТЬ PERSONAL VPN В XCODE

## 📋 ПРОБЛЕМА

- ❌ Personal VPN видно в Xcode, но отключено
- ❌ Непонятно, как включить
- ✅ На сайте Apple Developer Portal всё включено

---

## ✅ РЕШЕНИЕ: ВКЛЮЧИТЬ PERSONAL VPN В XCODE

### **ШАГ 1: Откройте проект в Xcode**

```bash
open ALADDIN.xcodeproj
```

---

### **ШАГ 2: Выберите таргет ALADDIN (основное приложение)**

1. **В левой панели** выберите проект **ALADDIN** (синяя иконка)
2. **В центральной панели** выберите таргет **ALADDIN** (не ALADDINPacketTunnel)

---

### **ШАГ 3: Перейдите на вкладку "Signing & Capabilities"**

1. **В верхней панели** выберите вкладку **"Signing & Capabilities"**
2. Вы увидите список Capabilities

---

### **ШАГ 4: Добавьте Personal VPN**

1. **Нажмите кнопку "+ Capability"** (в левом верхнем углу списка Capabilities)
2. **В появившемся окне** найдите **"Personal VPN"**
3. **Нажмите на "Personal VPN"**
4. **Xcode автоматически добавит** Personal VPN capability

---

### **ШАГ 5: Проверьте, что Personal VPN включена**

После добавления вы должны увидеть:
- ✅ **Personal VPN** в списке Capabilities
- ✅ Рядом должна быть галочка или статус "Enabled"

---

## 🔍 ЕСЛИ PERSONAL VPN УЖЕ ЕСТЬ, НО ОТКЛЮЧЕНА

### **Вариант 1: Включить через настройки**

1. **Найдите "Personal VPN"** в списке Capabilities
2. **Кликните на "Personal VPN"** (на саму строку)
3. **Проверьте, есть ли переключатель** или **кнопка "Enable"**
4. **Включите** переключатель или нажмите "Enable"

### **Вариант 2: Удалить и добавить заново**

1. **Найдите "Personal VPN"** в списке Capabilities
2. **Нажмите на кнопку "—"** (минус) рядом с "Personal VPN"
3. **Подтвердите удаление**
4. **Добавьте заново** через "+ Capability"

---

## 🔧 ШАГ 6: ПРОВЕРЬТЕ ТАРГЕТ ALADDINPacketTunnel

### **Для Extension тоже нужно проверить:**

1. **Выберите таргет ALADDINPacketTunnel**
2. **Перейдите на "Signing & Capabilities"**
3. **Проверьте Capabilities:**
   - ✅ **Personal VPN** — должна быть включена
   - ✅ **Network Extensions** — должна быть включена

---

## ⚠️ ВАЖНО: ПРОВЕРЬТЕ TEAM

### **Если Personal VPN не включается:**

1. **Проверьте, что выбран правильный Team:**
   - В разделе **"Signing"** должен быть выбран ваш Team
   - Team ID: `6CJVBBUGSN`

2. **Если Team не выбран:**
   - Выберите Team из выпадающего списка
   - Xcode автоматически включит capabilities

---

## 🔄 ШАГ 7: ОБНОВИТЬ ПРОФИЛИ

### **После включения Personal VPN:**

1. **Xcode → Preferences...** (⌘ + ,)
2. **Вкладка "Accounts"**
3. **Выберите ваш Apple ID**
4. **Нажмите "Download Manual Profiles"**
5. **Или просто пересоберите проект** — Xcode обновит профили автоматически

---

## ✅ ПРОВЕРКА: ВСЁ ЛИ ВКЛЮЧЕНО

### **Чеклист для проверки:**

#### **Таргет ALADDIN (основное приложение):**
- ✅ **Team:** `6CJVBBUGSN` (выбран)
- ✅ **Bundle ID:** `family.aladdin.ios`
- ✅ **Personal VPN:** включена (если нужно для основного приложения)
- ⚠️ **Примечание:** Personal VPN обычно нужна только для Extension

#### **Таргет ALADDINPacketTunnel (Extension):**
- ✅ **Team:** `6CJVBBUGSN` (выбран)
- ✅ **Bundle ID:** `family.aladdin.ios.packetTunnel`
- ✅ **Personal VPN:** включена ✅ **ОБЯЗАТЕЛЬНО!**
- ✅ **Network Extensions:** включена ✅ **ОБЯЗАТЕЛЬНО!**

---

## 📝 КРАТКАЯ ИНСТРУКЦИЯ

1. **Xcode → Открыть проект**
2. **Выбрать таргет ALADDINPacketTunnel**
3. **Вкладка "Signing & Capabilities"**
4. **"+ Capability" → "Personal VPN"**
5. **Проверить, что включена**
6. **Обновить профили**

---

## 🎯 ЕСЛИ НЕ ПОЛУЧАЕТСЯ ВКЛЮЧИТЬ

### **Проблема: Personal VPN не включается**

**Решение 1: Проверьте Team**
- Убедитесь, что выбран правильный Team
- Team должен быть платным ($99/год)

**Решение 2: Проверьте Bundle ID в Portal**
- Зайдите на: https://developer.apple.com/account/resources/identifiers/list
- Найдите `family.aladdin.ios.packetTunnel`
- Убедитесь, что Personal VPN включена там

**Решение 3: Пересоздать профиль**
- В Xcode: Signing & Capabilities
- Снимите галочку "Automatically manage signing"
- Подождите 2 секунды
- Снова включите "Automatically manage signing"
- Выберите Team
- Xcode создаст новый профиль

---

**Попробуйте добавить Personal VPN через "+ Capability" — это самый простой способ!** 🚀

