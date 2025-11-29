# 🔄 АЛЬТЕРНАТИВА: ДОБАВЛЕНИЕ СЕКРЕТОВ БЕЗ HOMEBREW

**Дата:** 29 ноября 2025  
**Если Homebrew не установится на macOS 11.7**

---

## ✅ ПРОСТОЙ СПОСОБ: ВРУЧНУЮ ЧЕРЕЗ БРАУЗЕР

**Это самый быстрый способ (2-3 минуты)!**

### Шаг 1: Открыть GitHub Secrets

Откройте в браузере:
https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

---

### Шаг 2: Добавить первый секрет

1. **В окне TextEdit с `app_profile_base64.txt`:**
   - Cmd+A (выделить всё)
   - Cmd+C (скопировать)

2. **В GitHub:**
   - Нажать "New repository secret"
   - **Name:** `PROVISIONING_PROFILE_APP`
   - **Secret:** вставить (Cmd+V)
   - Нажать "Add secret"

---

### Шаг 3: Добавить второй секрет

1. **В окне TextEdit с `extension_profile_base64.txt`:**
   - Cmd+A (выделить всё)
   - Cmd+C (скопировать)

2. **В GitHub:**
   - Нажать "New repository secret"
   - **Name:** `PROVISIONING_PROFILE_EXTENSION`
   - **Secret:** вставить (Cmd+V)
   - Нажать "Add secret"

---

### Шаг 4: Проверить/добавить APPLE_TEAM_ID

1. **Проверить список секретов:**
   - Должен быть секрет `APPLE_TEAM_ID` со значением `6CJVBBUGSN`

2. **Если нет:**
   - Нажать "New repository secret"
   - **Name:** `APPLE_TEAM_ID`
   - **Secret:** `6CJVBBUGSN`
   - Нажать "Add secret"

---

## ✅ ПРОВЕРКА

После добавления должны быть:
- ✅ `PROVISIONING_PROFILE_APP`
- ✅ `PROVISIONING_PROFILE_EXTENSION`
- ✅ `APPLE_TEAM_ID` = `6CJVBBUGSN`

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После добавления секретов:
- Я обновлю workflow для использования profiles
- Затем можно будет собрать билд с подписью

---

**Дата:** 29 ноября 2025  
**Инструкция:** Альтернативный способ добавления секретов

