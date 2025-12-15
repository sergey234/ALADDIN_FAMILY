# 🔄 ОБНОВЛЕНИЕ PRODUCT ID ДЛЯ BASIC ТАРИФА

**Дата:** 7 декабря 2025

---

## ✅ ИЗМЕНЕНИЯ

### Обновлен Product ID для Basic тарифа

**Старый ID:**
```
family.aladdin.ios.subscription.basic
```

**Новый ID:**
```
family.aladdin.ios.subscription.basic.v2
```

---

## 📝 ИЗМЕНЕНИЯ В КОДЕ

### Файл: `Core/Store/StoreManager.swift`

**До:**
```swift
enum ProductID: String, CaseIterable {
    case basic = "family.aladdin.ios.subscription.basic"
    case individual = "family.aladdin.ios.subscription.individual.v2"
    case family = "family.aladdin.ios.subscription.family"
    case premium = "family.aladdin.ios.subscription.premium"
```

**После:**
```swift
enum ProductID: String, CaseIterable {
    case basic = "family.aladdin.ios.subscription.basic.v2"
    case individual = "family.aladdin.ios.subscription.individual.v2"
    case family = "family.aladdin.ios.subscription.family"
    case premium = "family.aladdin.ios.subscription.premium"
```

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ В APP STORE CONNECT

### При создании подписки Basic:

1. **Product ID:** `family.aladdin.ios.subscription.basic.v2`
2. **Название:** ALADDIN Базовый
3. **Цена:** 0 рублей (бесплатно)
4. **Уровень:** 0
5. **Период:** 1 месяц

---

## 📋 ТЕКУЩИЕ PRODUCT IDs

| Тариф | Product ID |
|-------|------------|
| Basic | `family.aladdin.ios.subscription.basic.v2` |
| Individual | `family.aladdin.ios.subscription.individual.v2` |
| Family | `family.aladdin.ios.subscription.family` |
| Premium | `family.aladdin.ios.subscription.premium` |

---

**Статус:** ✅ Обновлено в коде  
**Дата:** 07.12.2025

