# ПОЛНАЯ ИНСТРУКЦИЯ: APP STORE CONNECT

**Дата:** 11 декабря 2025  
**Проблемы от Apple:** Краш при Subscribe + IAP продукты не отправлены

---

## 🚨 ПРОБЛЕМЫ ОТ APPLE:

### 1. Краш при Subscribe
> "The app crashed during review. Apps that crash negatively impact users."

**Статус:** ✅ **ИСПРАВЛЕНО В КОДЕ** (нужно загрузить новый build)

### 2. IAP продукты не отправлены
> "The app includes references to subscription but the associated in-app purchase products have not been submitted for review."

**Статус:** ⏳ **ТРЕБУЕТ ДЕЙСТВИЙ**

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ:

### ✅ ЗАДАЧА 1: ДОБАВИТЬ PRIVACY POLICY И TERMS OF USE URL

**Где добавить:**

1. **Privacy Policy URL:**
   - Раздел: **"App Information"** → **"Privacy Policy URL"**
   - Значение: `https://aladdin-ai.ru/privacy.html`

2. **Terms of Use URL:**
   - Раздел: **"App Versions"** → **"Description"** (в конце описания)
   - Добавить: `Terms of Use: https://aladdin-ai.ru/terms.html`

**Инструкция:** `docs/AppStore/ГДЕ_ДОБАВИТЬ_PRIVACY_TERMS_В_APP_STORE_CONNECT_11_12_2025.md`

---

### ⏳ ЗАДАЧА 2: СОЗДАТЬ IAP ПРОДУКТЫ

**Нужно создать 4 продукта:**

1. **Basic:** `family.aladdin.ios.subscription.basic.v2`
2. **Individual:** `family.aladdin.ios.subscription.individual.v2`
3. **Family:** `family.aladdin.ios.subscription.family`
4. **Premium:** `family.aladdin.ios.subscription.premium`

**Для каждого продукта:**
- ✅ Создать в разделе "In-App Purchases"
- ✅ Добавить Display Name (RU + EN)
- ✅ Добавить Description (RU + EN)
- ✅ Установить цену
- ✅ **Добавить скриншот для App Review (ОБЯЗАТЕЛЬНО!)**
- ✅ Отправить на проверку

**Инструкция:** `docs/AppStore/СОЗДАНИЕ_IAP_ПРОДУКТОВ_11_12_2025.md`

---

### ⏳ ЗАДАЧА 3: ЗАГРУЗИТЬ НОВЫЙ BUILD

**После исправления краша:**
1. Увеличить версию (например, 1.0.1, Build 8)
2. Собрать архив в Xcode
3. Загрузить в App Store Connect
4. Дождаться обработки (10-30 минут)

---

### ⏳ ЗАДАЧА 4: ОТПРАВИТЬ НА ПРОВЕРКУ

**После создания продуктов:**
1. Добавить продукты в версию приложения
2. Убедиться что все готово:
   - ✅ Privacy Policy URL добавлен
   - ✅ Terms of Use URL добавлен
   - ✅ Продукты созданы и отправлены
   - ✅ Новый build загружен
3. Отправить на проверку

---

## 📊 ПРИОРИТЕТЫ:

### 🎯 ПРИОРИТЕТ 1: Создать IAP продукты (1-2 часа)
- Без продуктов приложение не пройдет проверку
- Нужны скриншоты для каждого продукта

### 🎯 ПРИОРИТЕТ 2: Добавить Privacy/Terms URLs (10 минут)
- Быстро и просто
- Обязательно для подписок

### 🎯 ПРИОРИТЕТ 3: Загрузить новый build (30 минут)
- После исправления краша
- Нужно собрать и загрузить

### 🎯 ПРИОРИТЕТ 4: Отправить на проверку (10 минут)
- После выполнения всех задач выше

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ:

- **IAP продукты:** 1-2 часа
- **Privacy/Terms URLs:** 10 минут
- **Новый build:** 30 минут
- **Отправка:** 10 минут

**ИТОГО:** 2-3 часа

---

## 📋 ЧЕКЛИСТ:

### Перед отправкой:

- [ ] Privacy Policy URL добавлен
- [ ] Terms of Use URL добавлен
- [ ] 4 IAP продукта созданы
- [ ] Скриншоты добавлены для всех продуктов
- [ ] Продукты отправлены на проверку
- [ ] Продукты добавлены в версию приложения
- [ ] Новый build загружен (с исправлением краша)
- [ ] Все готово к отправке

---

## 🎯 СЛЕДУЮЩИЙ ШАГ:

**Начать с создания IAP продуктов** - это самая долгая задача.

---

**Дата:** 11 декабря 2025
