# 📋 ШАГ 2: ЭКСПОРТ И ДОБАВЛЕНИЕ В GITHUB SECRETS

**Дата:** 29 ноября 2025  
**Этап:** ЭТАП 2 из детального плана

---

## ✅ ЧТО УЖЕ СДЕЛАНО

- ✅ Provisioning profiles найдены
- ✅ Profiles скопированы на Desktop в папку `ALADDIN_Profiles`
- ✅ Profiles закодированы в base64:
  - `app_profile_base64.txt` (основное приложение)
  - `extension_profile_base64.txt` (Network Extension)

---

## 🎯 ЧТО ДЕЛАТЬ СЕЙЧАС

### Шаг 2.1: Открыть файлы с base64

1. **Открыть Finder:**
   - Перейти на Desktop
   - Открыть папку `ALADDIN_Profiles`

2. **Открыть файл `app_profile_base64.txt`:**
   - Двойной клик для открытия в TextEdit
   - Или правый клик → "Open With" → TextEdit

3. **Скопировать всё содержимое:**
   - Cmd+A (выделить всё)
   - Cmd+C (скопировать)
   - Сохранить в буфер обмена

---

### Шаг 2.2: Добавить в GitHub Secrets

1. **Открыть GitHub:**
   - Перейти на: https://github.com/sergey234/ALADDIN_FAMILY
   - Войти в аккаунт (если не вошли)

2. **Открыть Settings:**
   - Нажать на вкладку "Settings" вверху
   - В левом меню выбрать "Secrets and variables" → "Actions"

3. **Добавить первый секрет:**
   - Нажать "New repository secret" (зелёная кнопка справа)
   - **Name:** `PROVISIONING_PROFILE_APP`
   - **Secret:** Вставить содержимое `app_profile_base64.txt` (Cmd+V)
   - Нажать "Add secret"

4. **Добавить второй секрет:**
   - Нажать "New repository secret" снова
   - **Name:** `PROVISIONING_PROFILE_EXTENSION`
   - **Secret:** Открыть `extension_profile_base64.txt`, скопировать всё (Cmd+A, Cmd+C), вставить (Cmd+V)
   - Нажать "Add secret"

5. **Проверить секреты:**
   - Должны быть видны:
     - `PROVISIONING_PROFILE_APP` ✅
     - `PROVISIONING_PROFILE_EXTENSION` ✅
     - `APPLE_TEAM_ID` (если уже добавлен)

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

### Что должно быть в GitHub Secrets:

1. **PROVISIONING_PROFILE_APP:**
   - ✅ Добавлен
   - ✅ Содержит base64 строку (очень длинная)

2. **PROVISIONING_PROFILE_EXTENSION:**
   - ✅ Добавлен
   - ✅ Содержит base64 строку (очень длинная)

3. **APPLE_TEAM_ID:**
   - ✅ Должен быть: `6CJVBBUGSN`
   - ⚠️ Если нет, добавить:
     - Name: `APPLE_TEAM_ID`
     - Secret: `6CJVBBUGSN`

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После добавления секретов:
- **ЭТАП 3:** Обновить workflow для использования profiles
- Инструкция: `docs/ШАГ_3_ОБНОВИТЬ_WORKFLOW.md`

---

**Дата:** 29 ноября 2025  
**Инструкция:** Экспорт и добавление profiles в GitHub Secrets

