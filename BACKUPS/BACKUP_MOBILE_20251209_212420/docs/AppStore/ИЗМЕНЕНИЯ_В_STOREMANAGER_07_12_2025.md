# 📝 ИЗМЕНЕНИЯ В STOREMANAGER.SWIFT

**Дата:** 7 декабря 2025  
**Файл:** `Core/Store/StoreManager.swift`

---

## ✅ ВЫПОЛНЕННЫЕ ИЗМЕНЕНИЯ

### Изменение Product ID для Individual подписки

**Строка 24:**

**Было:**
```swift
case individual = "family.aladdin.ios.subscription.individual"
```

**Стало:**
```swift
case individual = "family.aladdin.ios.subscription.individual.v2"
```

---

## 📋 ПРИЧИНА ИЗМЕНЕНИЯ

1. Старый Product ID `family.aladdin.ios.subscription.individual` был занят
2. Подписка Individual была случайно удалена в App Store Connect
3. Apple резервирует Product ID даже после удаления подписки
4. Использован новый ID с суффиксом `.v2`

---

## 🎯 ЧТО НУЖНО В APP STORE CONNECT

При создании подписки Individual использовать:
- **Product ID:** `family.aladdin.ios.subscription.individual.v2`
- **Reference Name:** `ALADDIN Индивидуальный`
- **Уровень:** 3
- **Период:** 1 месяц

---

## ⚠️ ВАЖНО

- ✅ Файл обновлен локально
- ⏳ Изменения НЕ закоммичены в Git (будет сделано позже)
- ⏳ Изменения НЕ отправлены в GitHub (будет сделано позже)
- ✅ После создания подписки в App Store Connect с новым ID - все будет работать

---

**Дата создания:** 07.12.2025  
**Статус:** Изменения сохранены, коммит отложен

