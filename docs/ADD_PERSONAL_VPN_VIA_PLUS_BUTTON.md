# ➕ Как добавить Personal VPN через кнопку "+ Capability"

## 📋 Что вы видите

В Xcode для Personal VPN написано:
> **"add capabilities by clicking the + button above"**

Это означает, что Personal VPN **видна в списке**, но **ещё не добавлена** в проект.

---

## ✅ РЕШЕНИЕ: Добавить через кнопку "+"

### **ШАГ 1: Найдите кнопку "+ Capability"**

1. **Выберите таргет ALADDINPacketTunnel** в Xcode
2. **Вкладка "Signing & Capabilities"**
3. **В верхней части списка Capabilities** найдите кнопку **"+ Capability"**
   - Обычно она находится **над списком** capabilities
   - Или в **правом верхнем углу** списка

### **ШАГ 2: Нажмите на кнопку "+ Capability"**

1. **Кликните на кнопку "+ Capability"**
2. **Откроется окно** со списком всех доступных capabilities

### **ШАГ 3: Найдите и выберите Personal VPN**

1. **В появившемся окне** найдите **"Personal VPN"**
   - Можете использовать поиск (если есть)
   - Или прокрутите список вниз
2. **Кликните на "Personal VPN"**
3. **Xcode автоматически добавит** Personal VPN в список capabilities

### **ШАГ 4: Проверьте, что Personal VPN добавлена**

После добавления вы должны увидеть:
- ✅ **Personal VPN** в списке Capabilities
- ✅ Рядом должна быть галочка или статус "Enabled"
- ✅ Больше не должно быть текста "add capabilities by clicking the + button above"

---

## 🔍 Если кнопка "+ Capability" не видна

### **Вариант 1: Проверьте, что выбран правильный таргет**

1. **В левой панели** выберите проект **ALADDIN** (синяя иконка)
2. **В центральной панели** выберите таргет **ALADDINPacketTunnel** (не ALADDIN)
3. **Вкладка "Signing & Capabilities"**
4. Кнопка "+ Capability" должна появиться

### **Вариант 2: Проверьте Team**

Если кнопка "+ Capability" неактивна (серая):
1. **В разделе "Signing"** проверьте, что **Team выбран**
2. Если Team не выбран:
   - Выберите Team из выпадающего списка
   - Кнопка "+ Capability" должна стать активной

### **Вариант 3: Обновите Xcode**

Если кнопка всё ещё не видна:
1. **Закройте Xcode**
2. **Откройте проект заново**
3. **Проверьте снова**

---

## 📋 Пошаговая инструкция с картинками (текстовое описание)

```
┌─────────────────────────────────────────┐
│  ALADDINPacketTunnel                    │
│  Signing & Capabilities                 │
├─────────────────────────────────────────┤
│                                         │
│  Signing:                               │
│  ☑ Automatically manage signing        │
│  Team: [6CJVBBUGSN ▼]                  │
│                                         │
│  Capabilities:                          │
│  ┌───────────────────────────────────┐ │
│  │  + Capability  ← НАЖМИТЕ СЮДА!    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ▼ Personal VPN                         │
│    add capabilities by clicking         │
│    the + button above                   │
│                                         │
└─────────────────────────────────────────┘
```

**Действия:**
1. Нажмите на **"+ Capability"** (кнопка над списком)
2. В окне выберите **"Personal VPN"**
3. Personal VPN добавится в список

---

## ✅ После добавления

После того, как вы добавите Personal VPN:

1. **Personal VPN появится в списке** с галочкой
2. **Xcode автоматически:**
   - Добавит необходимые entitlements
   - Обновит provisioning profiles
   - Настроит capability

3. **Проверьте, что всё правильно:**
   - Personal VPN в списке ✅
   - Рядом галочка или "Enabled" ✅
   - Нет ошибок в Xcode ✅

---

## 🔧 Если Personal VPN не добавляется

### **Проблема 1: Кнопка "+ Capability" неактивна**

**Решение:**
1. Проверьте, что **Team выбран**
2. Проверьте, что **Bundle ID правильный**: `family.aladdin.ios.packetTunnel`
3. Включите **"Automatically manage signing"**

### **Проблема 2: Personal VPN не появляется в окне выбора**

**Решение:**
1. Убедитесь, что Personal VPN включена в **Apple Developer Portal**
2. Обновите provisioning profiles:
   - Xcode → Preferences... (⌘ + ,) → Accounts
   - Выберите Apple ID → "Download Manual Profiles"

### **Проблема 3: Ошибка при добавлении**

**Решение:**
1. Проверьте, что у вас **платный Apple Developer Program** ($99/год)
2. Personal VPN требует платный аккаунт
3. Бесплатный аккаунт не поддерживает VPN capabilities

---

## 🎯 Краткая инструкция

1. **Выберите таргет ALADDINPacketTunnel**
2. **Вкладка "Signing & Capabilities"**
3. **Найдите кнопку "+ Capability"** (над списком)
4. **Нажмите на "+ Capability"**
5. **Выберите "Personal VPN"**
6. **Готово!** ✅

---

## ✅ Итог

Если видите текст **"add capabilities by clicking the + button above"**:
- Это означает, что Personal VPN **видна**, но **не добавлена**
- Нужно **нажать на кнопку "+ Capability"** и **выбрать Personal VPN**
- После этого Personal VPN добавится в проект автоматически

**Попробуйте нажать на кнопку "+ Capability" прямо сейчас!** 🚀

