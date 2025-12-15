# 📝 СОЗДАНИЕ ПОДПИСКИ INDIVIDUAL

**Дата:** 7 декабря 2025  
**Цель:** Создать подписку Individual с правильным Product ID

---

## ⚠️ ВАЖНО: ПРОВЕРКА НАЗВАНИЙ

### Текущая ситуация в App Store Connect:

1. **"ALADDIN Личный"** имеет ID: `family.aladdin.ios.subscription.basic`
   - ❌ Это НЕ Individual, это Basic!
   - В коде это соответствует `case basic`

2. **Нужно создать:** Individual с ID: `family.aladdin.ios.subscription.individual`

---

## 🎯 ПРАВИЛЬНОЕ СООТВЕТСТВИЕ

### В коде приложения:

```swift
case basic = "family.aladdin.ios.subscription.basic"        // Базовый
case individual = "family.aladdin.ios.subscription.individual" // Индивидуальный/Личный
case family = "family.aladdin.ios.subscription.family"      // Семейный
case premium = "family.aladdin.ios.subscription.premium"    // Премиум
```

### Правильные названия:

1. **Basic** = "Базовый" (бесплатная или самая дешевая)
   - Product ID: `family.aladdin.ios.subscription.basic`
   - Уровень: 4 (самый низкий)

2. **Individual** = "Личный" или "Индивидуальный"
   - Product ID: `family.aladdin.ios.subscription.individual`
   - Уровень: 3
   - ⚠️ ЭТУ ПОДПИСКУ НУЖНО СОЗДАТЬ!

3. **Family** = "Семейный"
   - Product ID: `family.aladdin.ios.subscription.family`
   - Уровень: 2

4. **Premium** = "Премиум"
   - Product ID: `family.aladdin.ios.subscription.premium`
   - Уровень: 1 (самый высокий)

---

## 📝 СОЗДАНИЕ ПОДПИСКИ INDIVIDUAL

### ШАГ 1: Заполнить форму создания

1. **Оригинальное название:**
   - Введите: `ALADDIN Индивидуальный`
   - Или: `Individual Subscription`
   - Это внутреннее название

2. **ID продукта:**
   - Введите: `family.aladdin.ios.subscription.individual`
   - ⚠️ **КРИТИЧЕСКИ ВАЖНО:** Должен быть именно таким!

3. Нажмите **"Создать"** (Create)

### ШАГ 2: Настроить подписку

1. **Subscription Group:**
   - Выберите: **"ALADDIN - Подписки"**

2. **Уровень:**
   - Выберите: **3**
   - (Между Basic (4) и Family (2))

3. **Duration (Продолжительность):**
   - Выберите: **"1 месяц"** (1 month)

4. **Price (Цена):**
   - Нажмите **"Установить цены"** (Set Prices)
   - Установите цену для вашей страны
   - Нажмите **"Сохранить"** (Save)

### ШАГ 3: Локализация

1. Нажмите **"Локализация"** (Localization)

2. **Русский язык:**
   - **Display Name (Отображаемое имя):** `Индивидуальный тариф`
   - Или: `Личный тариф`
   - **Description (Описание):** `1 устройство, полная защита, AI помощник`
   - Нажмите **"Сохранить"** (Save)

3. **English:**
   - **Display Name:** `Individual Plan`
   - **Description:** `1 device, full protection, AI assistant`
   - Нажмите **"Сохранить"** (Save)

### ШАГ 4: Сохранить подписку

1. Проверьте все настройки
2. Нажмите **"Сохранить"** (Save) в правом верхнем углу

---

## ⚠️ ВАЖНО: ПРОБЛЕМА С НАЗВАНИЯМИ

### Текущая проблема:

В App Store Connect у вас:
- **"ALADDIN Личный"** имеет ID `family.aladdin.ios.subscription.basic`
- Это означает, что "Личный" = Basic, а не Individual!

### Решение:

1. **Вариант 1 (рекомендуется):** Переименовать существующую подписку
   - "ALADDIN Личный" → переименовать в "ALADDIN Базовый"
   - Это будет Basic (бесплатная/самая дешевая)

2. **Вариант 2:** Оставить как есть, но понимать соответствие
   - "ALADDIN Личный" = Basic (в коде)
   - Создать новую "ALADDIN Индивидуальный" = Individual

---

## 📋 ИТОГОВАЯ СТРУКТУРА ПОДПИСОК

После создания всех подписок должно быть:

| Уровень | Название в App Store | Product ID | Название в коде |
|---------|---------------------|------------|-----------------|
| 1 | ALADDIN Премиум | `family.aladdin.ios.subscription.premium` | Premium |
| 2 | ALADDIN Семейный | `family.aladdin.ios.subscription.family` | Family |
| 3 | ALADDIN Индивидуальный | `family.aladdin.ios.subscription.individual` | Individual |
| 4 | ALADDIN Базовый | `family.aladdin.ios.subscription.basic` | Basic |

---

## 🎯 ОТВЕТ НА ВОПРОС

**Вопрос:** "Мне нужен ID бесплатной подписки Базовый"

**Ответ:**

ID для Basic (Базовый): `family.aladdin.ios.subscription.basic`

**НО:** У вас уже есть подписка с этим ID, но она называется "ALADDIN Личный"!

**Рекомендация:**
1. Переименовать "ALADDIN Личный" в "ALADDIN Базовый"
2. Создать новую подписку "ALADDIN Индивидуальный" с ID `family.aladdin.ios.subscription.individual`

---

## 📝 ЧЕКЛИСТ

- [ ] Создана подписка Individual с ID `family.aladdin.ios.subscription.individual`
- [ ] Уровень установлен: 3
- [ ] Период: 1 месяц
- [ ] Цены установлены
- [ ] Локализация заполнена (русский и английский)
- [ ] Проверено соответствие Product ID коду приложения

---

**Дата создания:** 07.12.2025  
**Статус:** Инструкция для создания подписки Individual

