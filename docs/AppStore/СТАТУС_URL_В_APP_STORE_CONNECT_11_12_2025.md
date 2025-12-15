# СТАТУС: URL В APP STORE CONNECT

**Дата:** 11 декабря 2025  
**Вопрос:** Добавлены ли Privacy Policy и Terms of Use URL в App Store Connect?

---

## ❌ ОТВЕТ: НЕТ, ЕЩЕ НЕ ДОБАВЛЕНО

**Статус:** ⏳ **ТРЕБУЕТ ДЕЙСТВИЙ**

---

## ✅ ЧТО УЖЕ СДЕЛАНО:

1. ✅ **В приложении (код):**
   - Ссылки на Privacy Policy и Terms of Use добавлены в `TariffsScreen.swift`
   - Текст согласия: "Нажимая 'Subscribe', вы соглашаетесь с [Terms of Use] и [Privacy Policy]"
   - Ссылки открывают экраны `PrivacyPolicyScreen` и `TermsOfServiceScreen`

2. ✅ **На сайте:**
   - `https://aladdin-ai.ru/privacy.html` - работает ✅
   - `https://aladdin-ai.ru/terms.html` - работает ✅
   - VPN удален из обоих файлов ✅

---

## ⏳ ЧТО НУЖНО СДЕЛАТЬ:

### В App Store Connect (веб-интерфейс):

1. **Privacy Policy URL:**
   - Раздел: **"App Information"** → **"Privacy Policy URL"**
   - Добавить: `https://aladdin-ai.ru/privacy.html`
   - **Статус:** ⏳ **НЕ ДОБАВЛЕНО**

2. **Terms of Use URL:**
   - Раздел: **"App Versions"** → **"Description"** (в конце)
   - Добавить: `Terms of Use: https://aladdin-ai.ru/terms.html`
   - **Статус:** ⏳ **НЕ ДОБАВЛЕНО**

---

## 📋 КАК ПРОВЕРИТЬ:

### Проверить в App Store Connect:

1. Войти в https://appstoreconnect.apple.com
2. Выбрать приложение **ALADDIN**
3. Перейти в **"App Information"**
4. Проверить поле **"Privacy Policy URL"**:
   - Если пустое → **НЕ ДОБАВЛЕНО** ❌
   - Если есть `https://aladdin-ai.ru/privacy.html` → **ДОБАВЛЕНО** ✅

5. Перейти в **"App Versions"** → открыть версию
6. Проверить **"Description"**:
   - Если нет "Terms of Use: https://aladdin-ai.ru/terms.html" → **НЕ ДОБАВЛЕНО** ❌
   - Если есть → **ДОБАВЛЕНО** ✅

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ:

### Шаг 1: Добавить Privacy Policy URL (5 минут)

1. App Store Connect → ALADDIN → **"App Information"**
2. Найти раздел **"Privacy"** или **"App Privacy"**
3. В поле **"Privacy Policy URL"** ввести:
   ```
   https://aladdin-ai.ru/privacy.html
   ```
4. Нажать **"Save"** (Сохранить)

### Шаг 2: Добавить Terms of Use URL (5 минут)

1. App Store Connect → ALADDIN → **"App Versions"**
2. Открыть версию приложения (например, 1.0)
3. Найти раздел **"Description"**
4. В конце описания добавить:
   ```
   Terms of Use: https://aladdin-ai.ru/terms.html
   ```
5. Нажать **"Save"** (Сохранить)

---

## ✅ ПОСЛЕ ДОБАВЛЕНИЯ:

**Проверить:**
- ✅ Privacy Policy URL сохранен
- ✅ Terms of Use URL добавлен в Description
- ✅ Обе ссылки работают (можно кликнуть и проверить)

---

## 📋 ИНСТРУКЦИЯ:

Подробная инструкция: `docs/AppStore/ГДЕ_ДОБАВИТЬ_PRIVACY_TERMS_В_APP_STORE_CONNECT_11_12_2025.md`

---

## ⚠️ ВАЖНО:

**Это нужно сделать ВРУЧНУЮ в веб-интерфейсе App Store Connect!**

Я не могу это сделать автоматически - это требует входа в ваш аккаунт Apple Developer.

---

**Дата:** 11 декабря 2025
