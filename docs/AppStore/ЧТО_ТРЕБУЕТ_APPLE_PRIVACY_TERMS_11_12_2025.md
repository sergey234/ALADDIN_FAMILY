# ЧТО ТРЕБУЕТ APPLE - ПРОСТОЕ ОБЪЯСНЕНИЕ

**Дата:** 11 декабря 2025

---

## 📋 ЧТО APPLE ГОВОРИТ В ПИСЬМЕ:

### Guideline 3.1.2 - Business - Payments - Subscriptions

**Цитата из письма Apple:**

> "The app's metadata is missing the following required information:
> - A functional link to the Terms of Use (EULA)
> - A functional link to the privacy policy in the Privacy Policy field in App Store Connect"

**Перевод на русский:**

> "В метаданных приложения отсутствует следующая обязательная информация:
> - **Рабочая ссылка** на Условия использования (EULA)
> - **Рабочая ссылка** на политику конфиденциальности в поле Privacy Policy в App Store Connect"

---

## ✅ ЧТО ЗНАЧИТ "FUNCTIONAL LINK" (РАБОЧАЯ ССЫЛКА):

**Apple требует:**
- ✅ Ссылка должна **РАБОТАТЬ** (открываться)
- ✅ Ссылка должна показывать **ПРАВИЛЬНЫЙ КОНТЕНТ** (Privacy Policy или Terms of Use)
- ✅ Ссылка должна быть **ДОСТУПНА** (не 404, не редирект на главную)

**Apple НЕ требует:**
- ❌ Конкретный формат URL (с `.html` или без)
- ❌ Короткие URL (это просто хорошая практика)

---

## 🎯 ВАЖНОЕ УТОЧНЕНИЕ:

### Apple НЕ говорит что URL должны быть без .html!

**Apple говорит только:**
- "functional link" = **рабочая ссылка**
- Ссылка должна открываться и показывать правильный контент

**Вы можете использовать:**
- ✅ `https://aladdin-ai.ru/privacy.html` - **ПОДХОДИТ**, если работает
- ✅ `https://aladdin-ai.ru/terms.html` - **ПОДХОДИТ**, если работает
- ✅ `https://aladdin-ai.ru/privacy` - **ПОДХОДИТ**, если работает
- ✅ `https://aladdin-ai.ru/terms` - **ПОДХОДИТ**, если работает

---

## ❌ В ЧЕМ РЕАЛЬНАЯ ПРОБЛЕМА:

### Текущая ситуация:

1. ✅ `https://aladdin-ai.ru/privacy.html` - **РАБОТАЕТ** (показывает Privacy Policy)
2. ✅ `https://aladdin-ai.ru/terms.html` - **РАБОТАЕТ** (показывает Terms of Use)
3. ❌ `https://aladdin-ai.ru/privacy` - **НЕ РАБОТАЕТ** (показывает главную страницу)
4. ❌ `https://aladdin-ai.ru/terms` - **НЕ РАБОТАЕТ** (показывает главную страницу)

**Проблема:** `/privacy` и `/terms` редиректят на главную страницу вместо показа правильного контента.

---

## ✅ РЕШЕНИЕ:

### Вариант 1: Использовать .html URL (ПРОСТОЕ РЕШЕНИЕ)

**Если `/privacy.html` и `/terms.html` работают, используйте их!**

В App Store Connect укажите:
- Privacy Policy URL: `https://aladdin-ai.ru/privacy.html`
- Terms of Use URL: `https://aladdin-ai.ru/terms.html`

**Apple это примет!** Главное чтобы ссылки работали.

---

### Вариант 2: Настроить короткие URL (ЕСЛИ ХОТИТЕ)

Если хотите короткие URL без `.html`, нужно:
1. Настроить nginx чтобы `/privacy` показывал `privacy.html`
2. Настроить nginx чтобы `/terms` показывал `terms.html`

**Но это НЕ обязательно!** Apple принимает и `.html` версии.

---

## 📝 ЧТО НУЖНО СДЕЛАТЬ В APP STORE CONNECT:

### 1. Privacy Policy URL:

**Поле:** Privacy Policy URL (в настройках приложения)

**Можно указать:**
- ✅ `https://aladdin-ai.ru/privacy.html` (работает)
- ✅ `https://aladdin-ai.ru/privacy` (если настроить роутинг)

---

### 2. Terms of Use URL:

**Поле:** App Description (в описании приложения) или EULA field

**Можно указать:**
- ✅ `https://aladdin-ai.ru/terms.html` (работает)
- ✅ `https://aladdin-ai.ru/terms` (если настроить роутинг)

---

## 🎯 ИТОГ:

### Apple требует:
- ✅ **Рабочие ссылки** на Privacy Policy и Terms of Use
- ✅ Ссылки должны открываться и показывать правильный контент

### Apple НЕ требует:
- ❌ Конкретный формат URL
- ❌ Короткие URL без расширений

### Рекомендация:
**Используйте `/privacy.html` и `/terms.html`** - они работают, Apple их примет!

---

## ✅ ПРОСТОЕ РЕШЕНИЕ:

1. В App Store Connect укажите:
   - Privacy Policy URL: `https://aladdin-ai.ru/privacy.html`
   - Terms of Use URL: `https://aladdin-ai.ru/terms.html`

2. Проверьте что ссылки работают:
   - Откройте в браузере
   - Должны показать правильный контент

3. Готово! Apple примет эти ссылки.

---

**Дата создания:** 11 декабря 2025
