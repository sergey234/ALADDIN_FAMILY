# ✅ ФАЙЛЫ ГОТОВЫ! ОБНОВИТЬ GITHUB SECRETS

**Дата:** 29 ноября 2025

---

## ✅ ЧТО СДЕЛАНО

✅ Оба профиля закодированы в base64:
- `~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt`
- `~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt`

---

## 🎯 СЛЕДУЮЩИЙ ШАГ: ОБНОВИТЬ GITHUB SECRETS

### Шаг 1: Открыть GitHub Secrets

1. **Открыть браузер:**
   - https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

---

### Шаг 2: Обновить PROVISIONING_PROFILE_APP

1. **Найти секрет:**
   - В списке найти `PROVISIONING_PROFILE_APP`
   - Нажать "Update" (или на сам секрет)

2. **Открыть файл:**
   - Открыть Finder
   - Перейти в `~/Desktop/ALADDIN_Profiles/`
   - Найти: `app_profile_appstore_base64.txt`
   - Двойной клик → откроется в TextEdit

3. **Скопировать:**
   - Cmd+A (выделить всё)
   - Cmd+C (скопировать)
   - Закрыть TextEdit

4. **Вставить в GitHub:**
   - Вернуться в браузер
   - В поле "Secret" нажать Cmd+V
   - Нажать "Update secret"

---

### Шаг 3: Обновить PROVISIONING_PROFILE_EXTENSION

1. **Найти секрет:**
   - В списке найти `PROVISIONING_PROFILE_EXTENSION`
   - Нажать "Update"

2. **Открыть файл:**
   - Открыть Finder
   - Перейти в `~/Desktop/ALADDIN_Profiles/`
   - Найти: `extension_profile_appstore_base64.txt`
   - Двойной клик → откроется в TextEdit

3. **Скопировать:**
   - Cmd+A (выделить всё)
   - Cmd+C (скопировать)
   - Закрыть TextEdit

4. **Вставить в GitHub:**
   - Вернуться в браузер
   - В поле "Secret" нажать Cmd+V
   - Нажать "Update secret"

---

## ✅ ПРОВЕРКА

После обновления обоих секретов:
- ✅ `PROVISIONING_PROFILE_APP` обновлен
- ✅ `PROVISIONING_PROFILE_EXTENSION` обновлен

---

## 🎯 ФИНАЛЬНЫЙ ШАГ

После обновления секретов:
1. Запустить workflow "Build and Upload to App Store"
2. Билд должен собраться успешно!

---

**Дата:** 29 ноября 2025  
**Файлы готовы, обновляйте GitHub Secrets!**

