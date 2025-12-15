# 📱 ИНСТРУКЦИЯ: Как включить Packet Tunnel Provider в Apple Developer Portal

**Вопрос:** Где найти "Packet Tunnel Provider" внутри Network Extensions?

---

## ✅ ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 1: Открыть Bundle ID**

1. **Зайдите на:** https://developer.apple.com/account/resources/identifiers/list
2. **Найдите `family.aladdin.ios.packetTunnel`** в списке
3. **Кликните на него** (один раз)

---

### **ШАГ 2: Найти раздел Capabilities**

1. **В открывшемся окне** прокрутите вниз
2. **Найдите раздел "Capabilities"** (или "App Services")
3. **Это большой список с чекбоксами** (галочками)

---

### **ШАГ 3: Найти Network Extensions**

1. **В списке Capabilities** найдите строку:
   ```
   ☐ Network Extensions
   ```
   (или с галочкой, если уже включено)

2. **Отметьте галочку** ☑️ рядом с "Network Extensions"

3. **После отметки галочки** появится **подменю** или **дополнительные опции**

---

### **ШАГ 4: Выбрать Packet Tunnel Provider**

1. **После включения "Network Extensions"** появится список опций:
   ```
   ☐ Network Extensions
      ├─ ☐ Content Filter Provider
      ├─ ☐ App Proxy Provider
      ├─ ☐ Packet Tunnel Provider  ← ВЫБЕРИТЕ ЭТО
      └─ ☐ DNS Proxy Provider
   ```

2. **Отметьте галочку** ☑️ рядом с **"Packet Tunnel Provider"**

3. **Также отметьте** (если нужно):
   - ☑️ **Personal VPN** (в основном списке Capabilities)

---

## 📋 ВИЗУАЛЬНОЕ ОПИСАНИЕ

### **Как это выглядит в интерфейсе:**

```
┌─────────────────────────────────────────┐
│ App ID: family.aladdin.ios.packetTunnel │
├─────────────────────────────────────────┤
│                                         │
│ Capabilities:                           │
│                                         │
│ ☐ App Groups                            │
│ ☐ Associated Domains                    │
│ ☐ Background Modes                      │
│ ☐ Data Protection                       │
│ ☐ Game Center                           │
│ ☐ HealthKit                             │
│ ☐ HomeKit                               │
│ ☐ In-App Purchase                       │
│ ☐ Inter-App Audio                       │
│ ☐ Maps                                   │
│ ☐ Network Extensions                    │ ← НАЙДИТЕ ЭТО
│ ☐ Personal VPN                          │ ← И ЭТО
│ ☐ Push Notifications                    │
│ ☐ Siri                                  │
│ ☐ ...                                   │
│                                         │
└─────────────────────────────────────────┘
```

### **После клика на Network Extensions:**

```
┌─────────────────────────────────────────┐
│ Network Extensions                      │
├─────────────────────────────────────────┤
│                                         │
│ ☐ Content Filter Provider               │
│ ☐ App Proxy Provider                   │
│ ☐ Packet Tunnel Provider                │ ← ВЫБЕРИТЕ ЭТО
│ ☐ DNS Proxy Provider                   │
│                                         │
│ [Cancel]  [Save]                        │
└─────────────────────────────────────────┘
```

---

## ✅ ПОЛНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

1. **Открыть:** https://developer.apple.com/account/resources/identifiers/list
2. **Кликнуть на:** `family.aladdin.ios.packetTunnel`
3. **Прокрутить вниз** до раздела "Capabilities"
4. **Найти:** "Network Extensions" в списке
5. **Отметить галочку** ☑️ рядом с "Network Extensions"
6. **В появившемся подменю** найти "Packet Tunnel Provider"
7. **Отметить галочку** ☑️ рядом с "Packet Tunnel Provider"
8. **Также отметить:** ☑️ "Personal VPN" (в основном списке)
9. **Нажать "Save"** (внизу справа)
10. **Дождаться сохранения** (5-10 секунд)

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### **Проблема 1: "Network Extensions" неактивна (серая)**

**Причина:** Нужен платный Apple Developer Program ($99/год).

**Решение:**
- Убедитесь, что у вас есть платный аккаунт
- Если нет — купите Apple Developer Program

---

### **Проблема 2: После отметки "Network Extensions" не появляется подменю**

**Решение:**
1. **Обновите страницу** (F5 или Cmd+R)
2. **Попробуйте снова** отметить "Network Extensions"
3. **Подождите 2-3 секунды** — подменю может появиться с задержкой

---

### **Проблема 3: Не могу найти "Network Extensions" в списке**

**Решение:**
1. **Прокрутите список Capabilities вниз**
2. **Используйте поиск** (Cmd+F) и введите "Network"
3. **Или найдите "Personal VPN"** — "Network Extensions" обычно рядом

---

## 📝 КРАТКАЯ ПАМЯТКА

```
1. developer.apple.com/account/resources/identifiers/list
2. Кликнуть на family.aladdin.ios.packetTunnel
3. Прокрутить до Capabilities
4. Найти Network Extensions → отметить галочку
5. В подменю найти Packet Tunnel Provider → отметить галочку
6. Также отметить Personal VPN
7. Нажать Save
```

---

## ✅ ЧТО ДОЛЖНО БЫТЬ ВКЛЮЧЕНО

После выполнения должны быть отмечены:

✅ **Personal VPN** (в основном списке)  
✅ **Network Extensions** (в основном списке)  
   └─ ✅ **Packet Tunnel Provider** (в подменю Network Extensions)

---

**Готово!** После включения этих Capabilities provisioning profile будет соответствовать entitlements! 🚀

