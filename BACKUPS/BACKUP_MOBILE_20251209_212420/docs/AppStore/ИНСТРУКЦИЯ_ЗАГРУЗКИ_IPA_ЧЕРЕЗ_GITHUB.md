# 📤 ИНСТРУКЦИЯ: ЗАГРУЗКА IPA ЧЕРЕЗ GITHUB ACTIONS

**Дата:** 3 декабря 2025  
**Workflow:** `upload-ipa-only.yml`

---

## 🎯 ЦЕЛЬ

Загрузить готовый IPA из артефактов GitHub Actions в App Store Connect автоматически.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Откройте GitHub Actions

1. **Откройте браузер**
2. **Перейдите по ссылке:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions
   ```
3. **Войдите в GitHub** (если не вошли)

---

### ШАГ 2: Найдите Workflow

1. **В левом меню** найдите раздел "Workflows"
2. **Найдите:** "Upload IPA to App Store Connect"
3. **Нажмите** на название workflow

---

### ШАГ 3: Запустите Workflow

1. **Нажмите кнопку** "Run workflow" (справа вверху)
2. **Выберите ветку:** `main` или `master`
3. **Заполните параметры:**
   - **Artifact name:** `ALADDIN-IPA` (по умолчанию)
   - **Run ID:** оставьте пустым (использует последний)
4. **Нажмите** зеленую кнопку "Run workflow"

---

### ШАГ 4: Дождитесь завершения

1. **Workflow начнет выполняться**
2. **Проверьте логи:**
   - Шаг 1: "Checkout code" ✅
   - Шаг 2: "Download IPA artifact" ✅
   - Шаг 3: "Find IPA file" ✅
   - Шаг 4: "Upload to App Store Connect" ✅

3. **Время выполнения:** 5-10 минут

---

### ШАГ 5: Проверьте загрузку

1. **Откройте App Store Connect:**
   ```
   https://appstoreconnect.apple.com
   ```

2. **Перейдите:**
   - My Apps → ALADDIN X AI
   - TestFlight → Builds

3. **Проверьте статус:**
   - **Processing** → билд обрабатывается (30-60 минут)
   - **Ready to Submit** → готов к отправке ✅
   - **Invalid** → есть ошибки ❌

---

## ✅ ПРОВЕРКА

### Что должно произойти:

- [ ] Workflow запустился успешно
- [ ] IPA скачан из артефактов
- [ ] IPA загружен в App Store Connect
- [ ] Билд появился в TestFlight → Builds
- [ ] Статус "Processing" или "Ready to Submit"

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: Workflow не найден
**Решение:** Проверьте, что файл `.github/workflows/upload-ipa-only.yml` существует

### Проблема 2: Артефакт не найден
**Решение:** Убедитесь, что последний workflow создал артефакт "ALADDIN-IPA"

### Проблема 3: API ключи не настроены
**Решение:** Проверьте GitHub Secrets:
- `APP_STORE_CONNECT_API_KEY`
- `APP_STORE_CONNECT_ISSUER_ID`
- `APP_STORE_CONNECT_API_KEY_ID`

---

## 🔗 ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **App Store Connect:** https://appstoreconnect.apple.com
- **Workflow файл:** `.github/workflows/upload-ipa-only.yml`

---

**Дата:** 3 декабря 2025  
**Статус:** ✅ Инструкция готова

