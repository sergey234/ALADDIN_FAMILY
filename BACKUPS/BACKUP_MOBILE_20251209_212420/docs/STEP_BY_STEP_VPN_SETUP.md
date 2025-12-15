# 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ: Включить Personal VPN в Xcode

## 🎯 ЦЕЛЬ

Включить Personal VPN в Xcode для таргета ALADDINPacketTunnel

---

## 📝 ШАГ ЗА ШАГОМ

### **ШАГ 1: Откройте Xcode**

1. **Откройте проект:**
   ```bash
   open ALADDIN.xcodeproj
   ```

---

### **ШАГ 2: Найдите таргет ALADDINPacketTunnel**

1. **В левой панели** (Project Navigator):
   - Найдите проект **ALADDIN** (синяя иконка в самом верху)
   - Нажмите на него

2. **В центральной панели** (Editor):
   - Вы увидите список **TARGETS**
   - Найдите **ALADDINPacketTunnel** (не ALADDIN!)
   - Нажмите на него

---

### **ШАГ 3: Перейдите на "Signing & Capabilities"**

1. **В верхней панели** (вкладки):
   - Найдите вкладку **"Signing & Capabilities"**
   - Нажмите на неё

2. **Вы увидите:**
   - Раздел **"Signing"** (вверху)
   - Раздел **"Capabilities"** (ниже)

---

### **ШАГ 4: Добавьте Personal VPN**

#### **Вариант A: Если Personal VPN видно, но отключено**

1. **Найдите "Personal VPN"** в списке Capabilities
2. **Кликните на "Personal VPN"** (на саму строку, не на галочку)
3. **Проверьте, есть ли переключатель:**
   - Если есть — включите его
   - Если нет — попробуйте вариант B

#### **Вариант B: Если Personal VPN нет в списке**

1. **Найдите кнопку "+ Capability"** (в левом верхнем углу списка Capabilities)
2. **Нажмите на "+ Capability"**
3. **В появившемся окне:**
   - Найдите **"Personal VPN"** в списке
   - Нажмите на **"Personal VPN"**
4. **Xcode автоматически добавит** Personal VPN в список

---

### **ШАГ 5: Проверьте, что Personal VPN включена**

После добавления вы должны увидеть:
- ✅ **Personal VPN** в списке Capabilities
- ✅ Рядом должна быть галочка или статус "Enabled"
- ✅ Если есть предупреждение — нажмите "Fix Issue"

---

### **ШАГ 6: Проверьте Network Extensions**

1. **Убедитесь, что "Network Extensions" тоже включена**
2. **Если нет — добавьте через "+ Capability"**

---

## 🔄 ШАГ 7: ОБНОВИТЬ ПРОФИЛИ

### **После включения Personal VPN:**

1. **Xcode → Preferences...** (⌘ + ,)
2. **Вкладка "Accounts"**
3. **Выберите ваш Apple ID**
4. **Нажмите "Download Manual Profiles"**
5. **Подождите** (5-10 секунд)

---

## ✅ ПРОВЕРКА

### **Что должно быть:**

1. ✅ **Team:** `6CJVBBUGSN` (выбран)
2. ✅ **Bundle ID:** `family.aladdin.ios.packetTunnel`
3. ✅ **Personal VPN:** включена ✅
4. ✅ **Network Extensions:** включена ✅

---

## ⚠️ ЕСЛИ НЕ ПОЛУЧАЕТСЯ

### **Проблема 1: Personal VPN не включается**

**Решение:**
1. Проверьте, что выбран правильный Team (`6CJVBBUGSN`)
2. Проверьте, что Personal VPN включена в Apple Developer Portal
3. Попробуйте пересоздать профиль (см. ниже)

### **Проблема 2: Нет кнопки "+ Capability"**

**Решение:**
1. Убедитесь, что выбран таргет **ALADDINPacketTunnel** (не ALADDIN!)
2. Убедитесь, что вы на вкладке **"Signing & Capabilities"**

### **Проблема 3: Предупреждения о профиле**

**Решение:**
1. Снимите галочку "Automatically manage signing"
2. Подождите 2 секунды
3. Снова включите "Automatically manage signing"
4. Выберите Team
5. Xcode создаст новый профиль

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. Xcode → Таргет ALADDINPacketTunnel
2. Signing & Capabilities
3. "+ Capability" → "Personal VPN"
4. Проверить, что включена
5. Обновить профили
```

---

**Попробуйте сейчас — это займёт 2 минуты!** 🚀

